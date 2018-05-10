import datetime
import os
import warnings

from django.core import checks
from django.db import models

from django.core.files.base import File
from django.utils import six
from django.utils.deprecation import RemovedInDjango110Warning
from django.utils.encoding import force_str, force_text
from django.utils.inspect import func_supports_parameter
from django.core.files.storage import default_storage

from multiplefilefield.forms import MultipleFileField


class FieldFile(File):
    def __init__(self, instance, field, name):
        super(FieldFile, self).__init__(None, name)
        self.instance = instance
        self.field = field
        self.storage = field.storage
        self._committed = True
        self._size = 0

    def __eq__(self, other):
        # Older code may be expecting MultipleFileModelField values to be simple strings.
        # By overriding the == operator, it can remain backwards compatibility.
        if hasattr(other, 'name'):
            return self.name == other.name
        return self.name == other

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.name)

    # The standard File contains most of the necessary properties, but
    # FieldFiles can be instantiated without a name, so that needs to
    # be checked for here.

    def _require_file(self):
        if not self:
            raise ValueError("The '%s' attribute has no file associated with it." % self.field.name)

    def _get_file(self):
        self._require_file()
        if not hasattr(self, '_file') or self._file is None:
            self._file = self.storage.open(self.name, 'rb')
        return self._file

    def _set_file(self, _file):
        self._file = _file

    def _del_file(self):
        del self._file

    file = property(_get_file, _set_file, _del_file)

    def _get_path(self):
        self._require_file()
        return self.storage.path(self.name)
    path = property(_get_path)

    def _get_url(self):
        self._require_file()
        return self.storage.url(self.name)
    url = property(_get_url)

    def _get_size(self):
        self._require_file()
        if not self._committed:
            return self.file.size
        return self.storage.size(self.name)
    size = property(_get_size)

    def open(self, mode='rb'):
        self._require_file()
        self.file.open(mode)
    # open() doesn't alter the file's contents, but it does reset the pointer
    open.alters_data = True

    # In addition to the standard File API, FieldFiles have extra methods
    # to further manipulate the underlying file, as well as update the
    # associated model instance.

    def save(self, name, content, save=True):
        # Check whether named
        if not getattr(self.file, "_named", False):
            name = self.field.generate_filename(self.instance, name)

        if func_supports_parameter(self.storage.save, 'max_length'):
            self.name = self.storage.save(name, content, max_length=self.field.max_length)
        else:
            warnings.warn(
                'Backwards compatibility for storage backends without '
                'support for the `max_length` argument in '
                'Storage.save() will be removed in Django 1.10.',
                RemovedInDjango110Warning, stacklevel=2
            )
            self.name = self.storage.save(name, content)

        self.field.file_save_cache_list.append(self)
        setattr(self.instance, self.field.name, self.field.file_save_cache_list)

        # Update the file size cache
        self._size = content.size
        self._committed = True

        # Save the object because it has changed, unless save is False
        if save:
            self.instance.save()
    save.alters_data = True

    def delete(self, save=True):
        if not self:
            return
        # Only close the file if it's already open, which we know by the
        # presence of self._file
        if hasattr(self, '_file'):
            self.close()
            del self.file

        self.storage.delete(self.name)

        self.name = None
        setattr(self.instance, self.field.name, self.name)

        # Delete the file size cache
        if hasattr(self, '_size'):
            del self._size
        self._committed = False

        if save:
            self.instance.save()
    delete.alters_data = True

    def _get_closed(self):
        _file = getattr(self, '_file', None)
        return _file is None or _file.closed
    closed = property(_get_closed)

    def close(self):
        _file = getattr(self, '_file', None)
        if _file is not None:
            _file.close()

    def __getstate__(self):
        # FieldFile needs access to its associated model field and an instance
        # it's attached to in order to work properly, but the only necessary
        # data to be pickled is the file's name itself. Everything else will
        # be restored later, by FileDescriptor below.
        return {'name': self.name, 'closed': False, '_committed': True, '_file': None}


class MultipleFileDescriptor(object):
    def __init__(self, field):
        self.field = field

    def __wrap__(self, _file, instance=None):
        # Other types of files may be assigned as well, but they need to have
        # the FieldFile interface added to them. Thus, we wrap any other type of
        # File inside a FieldFile (well, the field's attr_class, which is
        # usually FieldFile).
        if isinstance(_file, File) and not isinstance(_file, FieldFile):
            file_copy = self.field.attr_class(instance, self.field, _file.name)
            file_copy.file = _file
            file_copy._committed = False
            return file_copy

        # Finally, because of the (some would say boneheaded) way pickle works,
        # the underlying FieldFile might not actually itself have an associated
        # file. So we need to reset the details of the FieldFile in those cases.
        elif isinstance(_file, FieldFile) and not hasattr(_file, 'field'):
            _file.instance = instance
            _file.field = self.field
            _file.storage = self.field.storage
            return instance
        elif _file is None:
            return ""

        # if file is FieldFile and 'field' not set, return it
        return _file

    def __get__(self, instance=None, owner=None):
        if instance is None:
            raise AttributeError(
                "The '%s' attribute can only be accessed from %s instances."
                % (self.field.name, owner.__name__))
        # This is slightly complicated, so worth an explanation.
        # instance.file`needs to ultimately return some instance of `File`,
        # probably a subclass. Additionally, this returned object needs to have
        # the FieldFile API so that users can easily do things like
        # instance.file.path and have that delegated to the file storage engine.
        # Easy enough if we're strict about assignment in __set__, but if you
        # peek below you can see that we're not. So depending on the current
        # value of the field we have to dynamically construct some sort of
        # "thing" to return.

        # The instance dict contains whatever was originally assigned
        # in __set__.
        files = instance.__dict__[self.field.name]
        temp_list = []

        if isinstance(files, list):
            for _file in files:
                temp_list.append(self.__wrap__(_file, instance))
        elif isinstance(files, str) or isinstance(files, unicode):
            # If this value is a string (instance.file = "path/to/file") or None
            # then we simply wrap it with the appropriate attribute class according
            # to the file field. [This is FieldFile for MultipleFileModelFields and
            # ImageFieldFile for ImageFields; it's also conceivable that user
            # subclasses might also want to subclass the attribute class]. This
            # object understands how to convert a path to a file, and also how to
            # handle None.
            if isinstance(files, six.string_types) or files is None:
                if files:
                    if files[0] == '[':
                        files = files[1:]
                    if files[-1] == ']':
                        files = files[:len(files) - 1]
                    file_name_list = list(files.split(", "))
                    file_list = []
                    for _file in file_name_list:
                        if _file:
                            _file = _file.strip()
                            if _file[0] == 'u' and _file[1] == "\'":
                                _file = _file[2:]
                            if _file[0] == '\'':
                                _file = _file[1:]
                            if _file[-1] == "\'":
                                _file = _file[:len(_file) - 1]
                            attr = self.field.attr_class(instance, self.field, _file)
                            file_list.append(attr)
                    instance.__dict__[self.field.name] = file_list
                else:
                    instance.__dict__[self.field.name] = ""
                return instance.__dict__[self.field.name]
        else:
            temp_list.append(self.__wrap__(files, instance))

        instance.__dict__[self.field.name] = temp_list

        # That was fun, wasn't it?
        return instance.__dict__[self.field.name]

    def __set__(self, instance, value):
        instance.__dict__[self.field.name] = value


class MultipleFileModelField(models.Field):
    # The class to wrap instance attributes in. Accessing the file object off
    # the instance will always return an instance of attr_class.
    attr_class = FieldFile

    # The descriptor to use for accessing the attribute off of the class.
    descriptor_class = MultipleFileDescriptor

    description = "File"

    def __init__(self, verbose_name=None, name=None, upload_to='', storage=None, **kwargs):
        self._primary_key_set_explicitly = 'primary_key' in kwargs
        self._unique_set_explicitly = 'unique' in kwargs

        self.file_save_cache_list = []
        self.storage = storage or default_storage
        self.upload_to = upload_to
        if callable(upload_to):
            self.generate_filename = upload_to

        kwargs['max_length'] = kwargs.get('max_length', 100)
        super(MultipleFileModelField, self).__init__(verbose_name, name, **kwargs)

    def pre_save(self, model_instance, add):
        """Returns field's value just before saving."""
        files = super(MultipleFileModelField, self).pre_save(model_instance, add)
        self.file_save_cache_list = []
        files_string = []
        if files:
            # Commit the file to storage prior to saving the model
            # Can raise not null here in future
            for _file in files:
                if isinstance(_file, FieldFile):
                    if not _file._committed:
                        _file.save(_file.name, _file, save=False)
                    files_string.append(_file.name)
        return files_string

    def get_internal_type(self):
        return "CharField"

    def save_form_data(self, instance, data):
        # Important: None means "no change", other false value means "clear"
        # This subtle distinction (rather than a more explicit marker) is
        # needed because we need to consume values that are also sane for a
        # regular (non Model-) Form to find in its cleaned_data dictionary.
        if data is not None:
            if isinstance(data, list):
                # Pickup to save
                data_temp = []
                for d in data:
                    if isinstance(d, FieldFile):
                        # Set _named, when data picked from database, do not rename it
                        setattr(d.file, "_named", True)
                        data_temp.append(d.file)
                    else:
                        data_temp.append(d)
                data = data_temp
            # This value will be converted to unicode and stored in the
            # database, so leaving False as-is is not acceptable.
            if not data:
                data = ''
            setattr(instance, self.name, data)

    def get_prep_value(self, value):
        """Returns field's value prepared for saving into a database."""
        # Need to convert File objects provided via a form to unicode for database insertion
        if value is None:
            value = super(MultipleFileModelField, self).get_prep_value(value)
            return six.text_type(value) if value is not None else None
        return six.text_type(value)

    """
    The following codes are copied from source codes django-1.8.18 FileField,
    for implementing the basic functions those Field doesn't have.
    """
    def check(self, **kwargs):
        errors = super(MultipleFileModelField, self).check(**kwargs)
        errors.extend(self._check_unique())
        errors.extend(self._check_primary_key())
        return errors

    def _check_unique(self):
        if self._unique_set_explicitly:
            return [
                checks.Error(
                    "'unique' is not a valid argument for a %s." % self.__class__.__name__,
                    hint=None,
                    obj=self,
                    id='fields.E200',
                )
            ]
        else:
            return []

    def _check_primary_key(self):
        if self._primary_key_set_explicitly:
            return [
                checks.Error(
                    "'primary_key' is not a valid argument for a %s." % self.__class__.__name__,
                    hint=None,
                    obj=self,
                    id='fields.E201',
                )
            ]
        else:
            return []

    def deconstruct(self):
        name, path, args, kwargs = super(MultipleFileModelField, self).deconstruct()
        if kwargs.get("max_length", None) == 100:
            del kwargs["max_length"]
        kwargs['upload_to'] = self.upload_to
        if self.storage is not default_storage:
            kwargs['storage'] = self.storage
        return name, path, args, kwargs

    def get_prep_lookup(self, lookup_type, value):
        if hasattr(value, 'name'):
            value = value.name
        return super(MultipleFileModelField, self).get_prep_lookup(lookup_type, value)

    def contribute_to_class(self, cls, name, **kwargs):
        super(MultipleFileModelField, self).contribute_to_class(cls, name, **kwargs)
        setattr(cls, self.name, self.descriptor_class(self))

    def get_directory_name(self):
        return os.path.normpath(force_text(datetime.datetime.now().strftime(force_str(self.upload_to))))

    def get_filename(self, filename):
        return os.path.normpath(self.storage.get_valid_name(os.path.basename(filename)))

    def generate_filename(self, instance, filename):
        return os.path.join(self.get_directory_name(), self.get_filename(filename))

    def formfield(self, **kwargs):
        defaults = {'form_class': MultipleFileField,
                    'max_length': self.max_length}
        # If a file has been provided previously, then the form doesn't require
        # that a new file is provided this time.
        # The code to mark the form field as not required is used by
        # form_for_instance, but can probably be removed once form_for_instance
        # is gone. ModelForm uses a different method to check for an existing file.
        if 'initial' in kwargs:
            defaults['required'] = False
        defaults.update(kwargs)
        return super(MultipleFileModelField, self).formfield(**defaults)


