"""
Referendum's app: Referendum's views
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.forms import DateTimeInput
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, ListView, CreateView, UpdateView
from django.views.generic.edit import FormMixin
from tempus_dominus.widgets import DateTimePicker

from referendum.forms import VoteForm, CommentForm
from referendum.models import Referendum, Category, VoteToken, Choice


class ReferendumListView(ListView):
    model = Referendum
    template_name = 'referendum/referendum_list.html'
    queryset = Referendum.objects.filter(publication_date__isnull=False, publication_date__lte=timezone.now())

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['categories'] = Category.objects.all()
        context['title'] = "Liste des référendums"
        return context


class CategoryView(ListView):
    model = Category
    template_name = 'referendum/referendum_list.html'

    def get_object(self):
        return self.model.objects.get(slug=self.kwargs['slug'])

    def get_queryset(self):
        return self.get_object().referendum_set.filter(publication_date__isnull=False,
                                                       publication_date__lte=timezone.now())

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['categories'] = Category.objects.all()
        context['title'] = "Liste des référendums dans la catégorie {}".format(self.get_object().title.lower())
        return context


class MyReferendumsView(LoginRequiredMixin, ListView):
    model = Referendum
    template_name = 'referendum/referendum_list.html'

    def get_queryset(self):
        return Referendum.objects.filter(creator=self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['categories'] = Category.objects.all()
        context['title'] = "Mes référendums"
        return context


class ReferendumDetailView(DetailView):
    model = Referendum
    template_name = 'referendum/referendum_detail.html'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if self.object.is_in_progress and self.request.user.has_perm('referendum.is_citizen'):
            vote_token, created = VoteToken.objects.get_or_create(user=self.request.user, referendum=self.object)
            return redirect(reverse_lazy('vote', kwargs={'token': vote_token.token}))
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = self.get_comment_form()
        return context

    def get_comment_form(self):
        form = CommentForm(initial={'referendum': self.object.pk})
        return form


class ReferendumCreateView(CreateView):
    model = Referendum
    fields = ["title", "description", "question", "categories"]
    template_name = 'referendum/referendum_create.html'

    def get_form_class(self):
        form_class = super().get_form_class()
        for field_name, field in form_class.base_fields.items():
            field.widget.attrs['class'] = 'form-control'
        return form_class

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.creator = self.request.user
        self.object.save()
        return HttpResponseRedirect('/')


class ReferendumUpdateView(UpdateView):
    model = Referendum
    fields = []
    template_name = 'referendum/referendum_update.html'

    def get_fields(self):
        """
        Get form field according to referendum state.
        :return:
        """
        self.fields = self.object.get_updatable_fields()

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if not self.object.creator == request.user:
            raise PermissionDenied
        return response

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if not self.object.creator == request.user:
            raise PermissionDenied
        return response

    def get_form_class(self):
        self.get_fields()
        form_class = super().get_form_class()
        for field_name, field in form_class.base_fields.items():
            if isinstance(field.widget, DateTimeInput):
                field.widget = DateTimePicker(options={
                    'format': 'DD/MM/YYYY',
                    'locale': 'fr'
                })
            else:
                field.widget.attrs['class'] = 'form-control'
        return form_class


class ReferendumVoteView(FormMixin, DetailView):
    slug_field = 'token'
    slug_url_kwarg = 'token'
    model = VoteToken
    template_name = 'referendum/referendum_detail.html'
    form_class = VoteForm

    def check_user_is_citizen(self):
        return self.request.user.has_perm('referendum.is_citizen')

    def get_vote_token(self):
        return self.model.objects.get(token=self.kwargs['token'])

    def check_token_user_is_request_user(self):
        token_user = self.get_vote_token().user
        return token_user == self.request.user

    def get_success_url(self):
        return reverse_lazy('referendum', kwargs={'slug': self.object.slug})

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        context['token'] = self.kwargs['token']
        context['can_vote'] = self.check_user_is_citizen()
        context['valid_token'] = self.check_token_user_is_request_user()
        context['already_voted'] = self.get_vote_token().voted
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_object(self, queryset=None):
        return self.get_vote_token().referendum

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        choices = [(choice.id, choice.title) for choice in self.object.choice_set.all()]
        form.fields['choice'].choices = choices
        return form

    def form_valid(self, form):
        choice = Choice.objects.get(pk=form.cleaned_data['choice'])
        self.get_vote_token().vote(choice=choice)
        return super().form_valid(form)
