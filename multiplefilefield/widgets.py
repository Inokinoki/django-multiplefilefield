from django.forms import Widget
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.utils.html import format_html
from django.forms.utils import flatatt

import multiplefilefield.fields


class MultipleFileInput(Widget):
    input_type = 'file'
    needs_multipart_form = True

    template_title = _(
        '%(input)s %(multiple_tip)s<br/> Count : %(count)i'
    )

    template_item = _(
        '<li> <a href="%(initial_url)s">'
        '%(initial)s</a> </li>'
    )

    # Translate!
    multiple_tip = _(
        'Multiple files possible'
    )

    def render(self, name, value, attrs=None):
        # Add file input multiple attribute before render
        if attrs:
            attrs.update({'multiple': True,
                          'type': 'file',
                          'name': name})
        else:
            attrs = {'multiple': True,
                     'type': 'file',
                     'name': name}

        substitutions = {}
        counter = 0         # Item counter
        template_temp = ""  # Item template, avoid the formatter format % in url string
        if value:
            template_temp += '<ol>'
            for _file in value:
                if isinstance(_file, multiplefilefield.fields.FieldFile):
                    # If not FieldFile, it is not from database
                    counter += 1
                    file_info = {"initial_url": _file.url, "initial": _file}
                    template_temp += (self.template_item % file_info)
                else:
                    return format_html('<input{} />' + str(self.multiple_tip), flatatt(attrs))
            template_temp += '</ol>'
        else:
            return format_html('<input{} />' + str(self.multiple_tip), flatatt(attrs))

        substitutions["multiple_tip"] = self.multiple_tip
        substitutions["count"] = counter
        substitutions['input'] = format_html('<input{} />', flatatt(attrs))

        # Return all the template
        return mark_safe(self.template_title % substitutions + template_temp)

    def value_from_datadict(self, data, files, name):
        # For an object of MultiValueDict, get() means getting one of the multi values
        # while getlist() means getting all available files
        if files:
            return files.getlist(name, None)
        else:
            return None
