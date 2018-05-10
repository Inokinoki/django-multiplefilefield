from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from .models import MultipleMultipleFileFieldModel


def index(request):
    temp = MultipleMultipleFileFieldModel.objects.first()
    if not temp:
        return render(request, 'index.html',
                      {
                          "title": _("Show object ") + str(temp.hash),
                          "object": temp
                       })
    else:
        return render(request, 'tutorial.html',
                      {"title": _("How to use it")})


