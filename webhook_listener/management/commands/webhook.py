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

from argparse import FileType
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext_lazy as _
from sys import stdin, stdout
from webhook_listener.models import Webhook


class Command(BaseCommand):
    help = 'Manage webhooks.'

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='subcommand')

        add_parser = subparsers.add_parser('add', help=_('Add new Webhook'))
        add_parser.add_argument('name', help=_('Webhook name'))
        add_parser.add_argument('command', nargs='?', type=FileType('r'),
                                default=stdin, help=_('Command'))
        add_parser.add_argument('-t', '--token', default=None,
                                help=_('Secret token, if none is given a ' +
                                       'random token will be generated.'))

        delete_parser = subparsers.add_parser('delete',
                                              help='Delete a Webhook')
        delete_parser.add_argument('name', help='Webhook name')

        list_parser = subparsers.add_parser('list', help=_('List Webhooks'))

        run_parser = subparsers.add_parser('run', help=_('Run a Webhook'))
        run_parser.add_argument('name', help=_('Webhook name'))
        run_parser.add_argument('payload', nargs='?', type=FileType('r'),
                                default=stdin, help=_('JSON payload'))

    def handle(self, *args, **options):
        try:
            if options['subcommand'] == 'add':
                self.add(options['name'], options['token'],
                         options['command'])
            elif options['subcommand'] == 'delete':
                Webhook.objects.get(name=options['name']).delete()
            elif options['subcommand'] == 'list':
                self.list()
            elif options['subcommand'] == 'run':
                webhook = Webhook.objects.get(name=options['name'])
                self.stdout.write(f'Running {webhook.name}.')
                webhook.run(options['payload'].read())
        except Webhook.DoesNotExist:
            self.stdout.write(self.style.ERROR('Webhook not found.'))

    def add(self, name, token, command):
        if token is None:
            token = ''.join('%02x' % i for i in os.urandom(32))
        webhook = Webhook.objects.create(name=name, token=token,
                                         command=command.read())
        self.stdout.write(self.style.SUCCESS('Webhook created.'))
        self.stdout.write(f'Name: {webhook.name}')
        self.stdout.write(f'Token: {webhook.token}')
        self.stdout.write(f'Command:\n{webhook.command}')

    def list(self):
        for webhook in Webhook.objects.all():
            self.stdout.write(f'* {webhook.name}')
