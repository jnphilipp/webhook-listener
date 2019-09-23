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
    help = _('Manage webhooks.')

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='subcommand')

        add = subparsers.add_parser('add', help=_('Add a new webhook.'))
        add.add_argument('name', type=str, help=_('Name'))
        add.add_argument('command', nargs='?', type=FileType('r'),
                         default=stdin, help=_('Command, default stdin.'))
        add.add_argument('--re-path', type=str, default='*',
                         help=_('Regex for matching URI, default "*".'))
        add.add_argument('--event-type', type=str, default='*',
                         help=_('Regex for matching X-GitHub-Delivery header' +
                                ', default "*".'))
        add.add_argument('--repo-name', type=str, default='*',
                         help=_('Regex for matching repository/full_name from' +
                                ' payload, default "*".'))

        delete = subparsers.add_parser('delete', help=_('Delete a webhook.'))
        delete.add_argument('name', type=str, help=_('Name'))

        info = subparsers.add_parser('info', help=_('Info'))
        info.add_argument('name', type=str, help=_('Name'))

        subparsers.add_parser('list', help=_('List webhooks.'))

        run = subparsers.add_parser('run', help=_('Run a webhook.'))
        run.add_argument('name', type=str, help=_('Name'))
        run.add_argument('payload', nargs='?', type=FileType('r'),
                         default=stdin, help=_('JSON payload'))

        update = subparsers.add_parser('update', help=_('Update a webhook.'))
        update.add_argument('name', type=str, help=_('Name'))
        update.add_argument('command', nargs='?', type=FileType('r'),
                            default=stdin, help=_('Command, default stdin'))
        update.add_argument('--re-path', type=str, default=None,
                            help=_('Regex for matching URI.'))
        update.add_argument('--event-type', type=str, default=None,
                            help=_('Regex for matching X-GitHub-Delivery' +
                                   ' header.'))
        update.add_argument('--repo-name', type=str, default=None,
                            help=_('Regex for matching repository/' +
                                   'full_name from payload.'))

    def handle(self, *args, **options):
        try:
            if options['subcommand'] == 'add':
                self.add(options['name'], options['command'],
                         options['re_path'], options['event_type'],
                         options['repo_name'])
            elif options['subcommand'] == 'delete':
                Webhook.objects.get(name=options['name']).delete()
            elif options['subcommand'] == 'info':
                self.info(Webhook.objects.get(name=options['name']))
            elif options['subcommand'] == 'list':
                self.list()
            elif options['subcommand'] == 'run':
                webhook = Webhook.objects.get(name=options['name'])
                self.stdout.write(f'Running {webhook.name}.')
                webhook.run(options['payload'].read())
            elif options['subcommand'] == 'update':
                self.update(Webhook.objects.get(name=options['name']),
                            options['command'], options['re_path'],
                            options['event_type'], options['repo_name'])
        except Webhook.DoesNotExist:
            self.stdout.write(self.style.ERROR('Webhook not found.'))

    def add(self, name, command, re_path, event_type, repo_name):
        if token is None:
            token = ''.join('%02x' % i for i in os.urandom(32))
        webhook = Webhook.objects.create(name=name, re_path=re_path,
                                         event_type=event_type,
                                         repo_name=repo_name,
                                         command=command.read())
        self.stdout.write(self.style.SUCCESS('Webhook created.'))
        self.info(webhook)

    def info(self, webhook):
        self.stdout.write(f'Name: {webhook.name}')
        self.stdout.write(f'Re-path: {webhook.re_path}')
        self.stdout.write(f'Event-type: {webhook.event_type}')
        self.stdout.write(f'Repo-name: {webhook.repo_name}')
        self.stdout.write(f'Command:\n{webhook.command}')

    def list(self):
        for webhook in Webhook.objects.all():
            self.stdout.write(f'* {webhook.name}')

    def update(self, webhook, command, re_path, event_type, repo_name):
        if command is not None:
            command = command.read()
            if command:
                webhook.command = command
        if re_path is not None:
            webhook.re_path = re_path
        if event_type is not None:
            webhook.event_type = event_type
        if repo_name is not None:
            webhook.repo_name = repo_name
        webhook.save()

        self.stdout.write(self.style.SUCCESS('Webhook updated.'))
        self.info(webhook)
