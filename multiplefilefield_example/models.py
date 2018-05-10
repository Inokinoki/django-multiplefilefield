from django.db import models
from multiplefilefield.fields import MultipleFileModelField


# Create your models here.
class SimpleMultipleFileFieldModel(models.Model):
    hash = models.CharField(name="hash", max_length=128)
    files = MultipleFileModelField(name="files")


class MultipleMultipleFileFieldModel(models.Model):
    hash = models.CharField(name="hash", max_length=128)
    files_1 = MultipleFileModelField(upload_to="file1")
    files_2 = MultipleFileModelField(upload_to="file2")
    files_3 = MultipleFileModelField(upload_to="file3")
    files_4 = MultipleFileModelField()
    files_5 = MultipleFileModelField()


class TestMultipleFile(models.Model):
    name = models.CharField(null=False, blank=False, max_length=128)
    files = MultipleFileModelField()
