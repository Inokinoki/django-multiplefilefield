from django.forms import Widget, FileField
from django.core.exceptions import ValidationError

from multiplefilefield.widgets import MultipleFileInput


class MultipleFileField(FileField):
    widget = MultipleFileInput

    def valid_error(self, file_name, file_size, file_count):
        # Validate max length in average
        # but we can have a better way to validate file total size
        if self.max_length is not None and len(file_name) > self.max_length / file_count:
            params = {'max': self.max_length / file_count, 'length': len(file_name)}
            raise ValidationError(self.error_messages['max_length'], code='max_length', params=params)
        # Validate file name
        if not file_name:
            raise ValidationError(self.error_messages['invalid'], code='invalid')
        # Validate empty file
        if not self.allow_empty_file and not file_size:
            raise ValidationError(self.error_messages['empty'], code='empty')

    def to_python(self, data):
        if data in self.empty_values:
            return None

        # For file list and file, handle in different situations
        if isinstance(data, list):
            for _file in data:
                # UploadedFile objects should have name and size attributes.
                try:
                    self.valid_error(_file.name, _file.size, len(data) if len(data) > 0 else 1)
                except AttributeError:
                    raise ValidationError(self.error_messages['invalid'], code='invalid')
        else:
            # UploadedFile objects should have name and size attributes.
            try:
                self.valid_error(data.name, data.size)
            except AttributeError:
                raise ValidationError(self.error_messages['invalid'], code='invalid')
        return data


