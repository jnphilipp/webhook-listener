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
import re

from django.test import TestCase
from webhook_listener.management.commands.token import Command
from webhook_listener.models import Token


class TokenCommandTestCase(TestCase):
    def test_add(self):
        regex = r'Token created\.\n1: [a-z0-9]+\nToken created.\n2: ' + \
            r'supersecret\n'

        with io.StringIO() as buf:
            with contextlib.redirect_stdout(buf):
                command = Command()
                command.handle(subcommand='add', secret=None)
                self.assertEquals(1, Token.objects.count())

                command.handle(subcommand='add', secret='supersecret')
                self.assertEquals(2, Token.objects.count())
                self.assertTrue(Token.objects.filter(secret='supersecret').
                                exists())

                self.assertIsNotNone(re.fullmatch(regex, buf.getvalue()))

    def test_delete(self):
        with io.StringIO() as buf:
            with contextlib.redirect_stdout(buf):
                command = Command()
                command.handle(subcommand='add', secret='supersecret')
                self.assertEquals(1, Token.objects.count())

                command.handle(subcommand='delete', id=1)
                self.assertEquals(0, Token.objects.count())

                self.assertEquals('Token created.\n1: supersecret\n' +
                                  'Token deleted.\nNone: supersecret\n',
                                  buf.getvalue())

    def test_info(self):
        with io.StringIO() as buf:
            with contextlib.redirect_stdout(buf):
                command = Command()
                command.handle(subcommand='add', secret='supersecret')
                self.assertEquals(1, Token.objects.count())

                command.handle(subcommand='info', id=1)
                self.assertEquals('Token created.\n1: supersecret\n' +
                                  '1: supersecret\n',
                                  buf.getvalue())

    def test_list(self):
        with io.StringIO() as buf:
            with contextlib.redirect_stdout(buf):
                command = Command()
                command.handle(subcommand='add', secret='supersecret')
                self.assertEquals(1, Token.objects.count())

                command.handle(subcommand='add', secret='supersupersecret')
                self.assertEquals(2, Token.objects.count())

                command.handle(subcommand='list')
                self.assertEquals('Token created.\n1: supersecret\n' +
                                  'Token created.\n2: supersupersecret\n' +
                                  '1: supersecret\n2: supersupersecret\n',
                                  buf.getvalue())

    def test_token_not_found(self):
        with io.StringIO() as err, io.StringIO() as out:
            with contextlib.redirect_stderr(err), \
                    contextlib.redirect_stdout(out):
                command = Command()
                command.handle(subcommand='add', secret='supersecret')
                self.assertEquals(1, Token.objects.count())

                command.handle(subcommand='info', id=2)
                self.assertEquals('Token created.\n1: supersecret\n',
                                  out.getvalue())
                self.assertEquals('Token not found.\n', err.getvalue())
