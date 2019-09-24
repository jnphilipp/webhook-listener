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

import logging
import os
import stat
import subprocess

from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from threading import Thread
from webhook_listener.decorators import postpone
from webhook_listener.fields import SingleLineTextField


class Token(models.Model):
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name=_('Updated at'))

    secret = SingleLineTextField(unique=True, verbose_name=_('Secret'))

    class Meta:
        verbose_name = _('Token')
        verbose_name_plural = _('Tokens')


class Webhook(models.Model):
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name=_('Updated at'))

    name = SingleLineTextField(unique=True, verbose_name=_('Name'))
    re_path = SingleLineTextField(default='.*',
                                  verbose_name=_('Regex for matching URI.'))
    event_type = SingleLineTextField(default='.*',
                                     verbose_name=_('Regex for matching ' +
                                                    'X-GitHub-Delivery ' +
                                                    'header.'))
    repo_name = SingleLineTextField(default='.*',
                                    verbose_name=_('Regex for matching ' +
                                                   'repository/full_name ' +
                                                   'from payload.'))
    command = models.TextField(verbose_name=_('Command'))

    @postpone
    def run(self, payload=""):
        def log(stream, loggercb):
            while True:
                out = stream.readline()
                if out:
                    loggercb(out.decode('utf-8').rstrip())
                else:
                    break

        logger = logging.getLogger('django')
        logger.info(f'Runnng webhook {self.name} command.')

        slug = slugify(self.name)
        with open(f'/tmp/{slug}_webhook', 'w', encoding='utf8') as f:
            f.write(self.command)

        os.chmod(f'/tmp/{slug}_webhook',
                 os.stat(f'/tmp/{slug}_webhook').st_mode | stat.S_IXUSR |
                 stat.S_IXGRP | stat.S_IXOTH)

        pobj = subprocess.Popen([f'/tmp/{slug}_webhook', payload],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout_thread = Thread(target=log,
                               args=(pobj.stdout,
                                     lambda s: logger.log(logging.INFO, s)))

        stderr_thread = Thread(target=log,
                               args=(pobj.stderr,
                                     lambda s: logger.log(logging.ERROR, s)))

        stdout_thread.start()
        stderr_thread.start()

        while stdout_thread.isAlive() and stderr_thread.isAlive():
            pass

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = _('Webhook')
        verbose_name_plural = _('Webhooks')
