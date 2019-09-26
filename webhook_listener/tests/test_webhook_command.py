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

import contextlib
import io

from django.test import TestCase
from webhook_listener.management.commands.webhook import Command
from webhook_listener.models import Webhook


class TokenCommandTestCase(TestCase):
    def test_add(self):
        with io.StringIO() as buf:
            with contextlib.redirect_stdout(buf):
                command = Command()
                command.handle(subcommand='add', name='test', re_path='.*',
                               event_type='push', repo_name='.*',
                               command=io.StringIO('#!/bin/bash\n' +
                                                   'echo "test"\n'))
                self.assertEquals(1, Webhook.objects.count())

                command.handle(subcommand='add', name='python-test',
                               re_path='test/', event_type='.*',
                               repo_name='.*',
                               command=io.StringIO('#!/usr/bin/env python\n' +
                                                   'print("test")\n'))
                self.assertEquals(2, Webhook.objects.count())
                self.assertEquals('Webhook created.\nName: test\nRe-path: .*' +
                                  '\nEvent-type: push\nRepo-name: .*\n' +
                                  'Command:\n#!/bin/bash\necho "test"\n' +
                                  'Webhook created.\nName: python-test\n' +
                                  'Re-path: test/\nEvent-type: .*\n' +
                                  'Repo-name: .*\nCommand:\n#!/usr/bin/env' +
                                  ' python\nprint("test")\n', buf.getvalue())

    def test_delete(self):
        with io.StringIO() as buf:
            with contextlib.redirect_stdout(buf):
                command = Command()
                command.handle(subcommand='add', name='test', re_path='.*',
                               event_type='push', repo_name='.*',
                               command=io.StringIO('#!/bin/bash\n' +
                                                   'echo "test"\n'))
                self.assertEquals(1, Webhook.objects.count())

                command.handle(subcommand='delete', name='test')
                self.assertEquals(0, Webhook.objects.count())
                self.assertEquals('Webhook created.\nName: test\nRe-path: .*' +
                                  '\nEvent-type: push\nRepo-name: .*\n' +
                                  'Command:\n#!/bin/bash\necho "test"\n' +
                                  'Webhook deleted.\nName: test\nRe-path: .*' +
                                  '\nEvent-type: push\nRepo-name: .*\n' +
                                  'Command:\n#!/bin/bash\necho "test"\n',
                                  buf.getvalue())

    def test_info(self):
        with io.StringIO() as buf:
            with contextlib.redirect_stdout(buf):
                command = Command()
                command.handle(subcommand='add', name='test', re_path='.*',
                               event_type='push', repo_name='.*',
                               command=io.StringIO('#!/bin/bash\n' +
                                                   'echo "test"\n'))
                self.assertEquals(1, Webhook.objects.count())

                command.handle(subcommand='info', name='test')
                self.assertEquals('Webhook created.\nName: test\nRe-path: .*' +
                                  '\nEvent-type: push\nRepo-name: .*\n' +
                                  'Command:\n#!/bin/bash\necho "test"\n' +
                                  'Name: test\nRe-path: .*\nEvent-type: push' +
                                  '\nRepo-name: .*\nCommand:\n#!/bin/bash\n' +
                                  'echo "test"\n', buf.getvalue())

    def test_list(self):
        with io.StringIO() as buf:
            with contextlib.redirect_stdout(buf):
                command = Command()
                command.handle(subcommand='add', name='test', re_path='.*',
                               event_type='push', repo_name='.*',
                               command=io.StringIO('#!/bin/bash\n' +
                                                   'echo "test"\n'))
                self.assertEquals(1, Webhook.objects.count())

                command.handle(subcommand='add', name='python-test',
                               re_path='test/', event_type='.*',
                               repo_name='.*',
                               command=io.StringIO('#!/usr/bin/env python\n' +
                                                   'print("test")\n'))
                self.assertEquals(2, Webhook.objects.count())

                command.handle(subcommand='list')
                self.assertEquals('Webhook created.\nName: test\nRe-path: .*' +
                                  '\nEvent-type: push\nRepo-name: .*\n' +
                                  'Command:\n#!/bin/bash\necho "test"\n' +
                                  'Webhook created.\nName: python-test\n' +
                                  'Re-path: test/\nEvent-type: .*\n' +
                                  'Repo-name: .*\nCommand:\n#!/usr/bin/env' +
                                  ' python\nprint("test")\n* python-test\n* ' +
                                  'test\n', buf.getvalue())

    def test_webhook_not_found(self):
        with io.StringIO() as err, io.StringIO() as out:
            with contextlib.redirect_stderr(err), \
                    contextlib.redirect_stdout(out):
                command = Command()
                command.handle(subcommand='add', name='test', re_path='.*',
                               event_type='push', repo_name='.*',
                               command=io.StringIO('#!/bin/bash\n' +
                                                   'echo "test"\n'))
                self.assertEquals(1, Webhook.objects.count())

                command.handle(subcommand='info', name='python-test')
                self.assertEquals('Webhook created.\nName: test\nRe-path: .*' +
                                  '\nEvent-type: push\nRepo-name: .*\n' +
                                  'Command:\n#!/bin/bash\necho "test"\n',
                                  out.getvalue())
                self.assertEquals('Webhook not found.\n', err.getvalue())
