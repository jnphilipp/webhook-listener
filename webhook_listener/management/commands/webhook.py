# -*- coding: utf-8 -*-
# Copyright (C) 2019 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>

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
        add_parser.add_argument('hook-id', help=_('Hub Webhook ID'))
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
                self.add(options['name'], options['hook-id'], options['token'],
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

    def add(self, name, hook_id, token, command):
        if token is None:
            token = ''.join('%02x' % i for i in os.urandom(32))
        webhook = Webhook.objects.create(name=name, hook_id=hook_id,
                                         token=token, command=command.read())
        self.stdout.write(self.style.SUCCESS('Webhook created.'))
        self.stdout.write(f'Name: {webhook.name}')
        self.stdout.write(f'Hook ID: {webhook.hook_id}')
        self.stdout.write(f'Token: {webhook.token}')
        self.stdout.write(f'Command:\n{webhook.command}')

    def list(self):
        for webhook in Webhook.objects.all():
            self.stdout.write(f'* {webhook.name} [{webhook.hook_id}]')
