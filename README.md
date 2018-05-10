## Project Description

A multiple file field implementation in Django.

It works well with Django-1.8.18 Python 2.7. Welcome to test it in other version and PR.

[![PyPI version](https://badge.fury.io/py/django-multiplefilefield.svg)](https://badge.fury.io/py/django-multiplefilefield)

### Installation

- You can install ``django-multiplefilefield``  with a package manage tool which you prefered the most, for example, to me it's pip:

```bash
pip install django-multiplefilefield
```
- Add ``multiplefilefield``  to your ``INSTALLED_APPS``  tuple in your settings file settings*.py:

```python
INSTALLED_APPS = (
    # …
    "multiplefilefield",
)
```

### Usage

- Fortunately, ``multiplefilefield``  provides the compatibility to the common single file FileField in Django. You can easily change ``models.FileField`` to ``MultipleFileModelField`` , do something to update your old field like:

```bash
./manage.py makemigrations
./manage.py migrate
```

- Or create a new model to have a try with it, just like what I did in the ``multiplefilefield_example``  app:

```python
from django.db import models
from multiplefilefield.fields import MultipleFileModelField

class SimpleMultipleFileFieldModel(models.Model):
    hash = models.CharField(name="hash", max_length=128)
    files = MultipleFileModelField(name="files")
```

- Once you created a model with ``MultipleFileModelField``, you can use it just like the traditional model with ``FileField``.

### Template

In the template, please do like this (object can be a SimpleMultileFileFieldModel instance)

```html
{% if object.files  %}
    {% for file in object.files %}
    <li><a href="{{ file.url }}">{{file.name}}</a></li>
    {% endfor %}
{% endif %}
```

### Regular Forms / Admin

In the form, all will be okay. It will be rendered as a ``<input/>``  with attribute ``multiple`` . 

So just ``Command + Click`` to choose multiple files in Mac, ``Ctrl + Click`` in PC. In the smartphones, surely you can choose many files !

### License

<a href="http://philippbosch.mit-license.org/">MIT</a>