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

import json
import logging

from datetime import datetime
from django.conf import settings
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from webhook_listener.decorators import verify_signature
from webhook_listener.models import Webhook


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(verify_signature, name='dispatch')
class WebhookListenerView(generic.View):
    def __init__(self, *args, **kwargs):
        super(generic.View, self).__init__(*args, **kwargs)
        self.logger = logging.getLogger('webhook_listener.WebhookListenerView')

    def post(self, request, webhook, *args, **kwargs):
        self.logger.info(f'Running webhook {webhook.name}.')
        self.logger.debug(f'Payload: {request.body}')
        webhook.run(payload)
        return JsonResponse({'timestamp': datetime.utcnow().isoformat()})
