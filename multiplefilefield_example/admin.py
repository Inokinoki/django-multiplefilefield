from django.contrib import admin

from multiplefilefield_example.models import SimpleMultipleFileFieldModel,\
    MultipleMultipleFileFieldModel


# Register your models here.
admin.site.register(SimpleMultipleFileFieldModel)
admin.site.register(MultipleMultipleFileFieldModel)
