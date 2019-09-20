# -*- coding: utf-8 -*-

from django.db import connection
from django.db.models.fields import Field
from django.utils.translation import ugettext_lazy as _


class SingleLineTextField(Field):
    description = _('Text')

    def get_internal_type(self):
        return 'TextField'

    def to_python(self, value):
        if isinstance(value, str) or value is None:
            return value
        return str(value)

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        return self.to_python(value)

    def formfield(self, **kwargs):
        defaults = {'max_length': self.max_length}
        if self.null and \
                not connection.features.interprets_empty_strings_as_nulls:
            defaults['empty_value'] = None
        defaults.update(kwargs)
        field = super().formfield(**defaults)
        field.widget.attrs.update({'style': 'width: 80%;'})
        return field
