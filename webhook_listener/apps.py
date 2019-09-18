# -*- coding: utf-8 -*-
# Copyright (C) 2019 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class WebhookListenerConfig(AppConfig):
    name = 'webhook_listener'
    verbose_name = _('Webhook listener')
    verbose_name_plural = _('Webhooks listeners')
