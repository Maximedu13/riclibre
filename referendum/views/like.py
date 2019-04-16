
from django.http import HttpResponseForbidden
from django.views.generic import DetailView

from referendum.models import Referendum, Like


class LikeView(DetailView):
    model = Referendum

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if request.user.is_authenticated:
            like, created = Like.objects.get_or_create(referendum=self.object, user=request.user)
            if not created:
                like.delete()
        else:
            return HttpResponseForbidden()
        return response
