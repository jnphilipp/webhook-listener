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

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext_lazy as _
from webhook_listener.models import Token


class Command(BaseCommand):
    help = _('Manage tokens.')

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='subcommand')

        add = subparsers.add_parser('add', help=_('Add a new token.'))
        add.add_argument('secret', nargs='?', type=str, default=None,
                         help=_('Secret token, if none is given a random ' +
                                'token will be generated.'))

        delete = subparsers.add_parser('delete', help=_('Delete a token.'))
        delete.add_argument('id', type=int, help=_('Token ID'))

        info = subparsers.add_parser('info', help=_('Info'))
        info.add_argument('id', type=int, help=_('Token ID'))

        subparsers.add_parser('list', help=_('List tokens.'))

    def handle(self, *args, **options):
        try:
            if options['subcommand'] == 'add':
                self.add(options['token'])
            elif options['subcommand'] == 'delete':
                Token.objects.get(id=options['id']).delete()
            elif options['subcommand'] == 'info':
                self.info(Token.objects.get(id=options['id']))
            elif options['subcommand'] == 'list':
                self.list()
        except Webhook.DoesNotExist:
            self.stdout.write(self.style.ERROR('Token not found.'))

    def add(self, secret):
        if secret is None:
            secret = ''.join('%02x' % i for i in os.urandom(32))
        token = Token.objects.create(secret=secret)
        self.stdout.write(self.style.SUCCESS('Token created.'))
        self.info(token)

    def info(self, token):
        self.stdout.write(f'{token.id}: {token.secret}')

    def list(self):
        for token in Token.objects.all():
            self.info(token)
