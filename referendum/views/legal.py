"""
Referendum's app: Legal view module
"""
import logging

from django.views.generic import TemplateView

LOGGER = logging.getLogger(__name__)


class LegalView(TemplateView):
    """
    Referendum's app legal view.
    """
    template_name = 'referendum/legal.html'
