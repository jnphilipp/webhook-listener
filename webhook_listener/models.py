# -*- coding: utf-8 -*-
# Copyright (C) 2019 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>
#
# This file is part of webhook_listener.
#
# webhook_listener is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# webhook_listener is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with webhook_listener. If not, see <http://www.gnu.org/licenses/>.

import os
import stat
import subprocess

from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from webhook_listener.decorators import postpone
from webhook_listener.fields import SingleLineTextField


class Webhook(models.Model):
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name=_('Updated at'))

    name = SingleLineTextField(unique=True, verbose_name=_('Name'))
    token = SingleLineTextField(verbose_name=_('Token'))
    command = models.TextField(verbose_name=_('Command'))

    @postpone
    def run(self, payload=""):
        slug = slugify(self.name)
        with open(f'/tmp/{slug}_webhook', 'w', encoding='utf8') as f:
            f.write(self.command)

        os.chmod(f'/tmp/{slug}_webhook',
                 os.stat(f'/tmp/{slug}_webhook').st_mode | stat.S_IXUSR |
                 stat.S_IXGRP | stat.S_IXOTH)

        subprocess.call([f'/tmp/{slug}_webhook', payload])

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = _('Webhook')
        verbose_name_plural = _('Webhooks')
