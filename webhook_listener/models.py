# -*- coding: utf-8 -*-
# Copyright (C) 2019 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>

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
    hook_id = SingleLineTextField(unique=True, verbose_name=_('Hook ID'))
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
