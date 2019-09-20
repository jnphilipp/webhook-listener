# -*- coding: utf-8 -*-
# Copyright (C) 2019 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>

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

    def post(self, request, *args, **kwargs):
        try:
            payload = json.loads(request.POST['payload'])
            webhook = Webhook.objects.get(hook_id=payload['hook_id'])
            self.logger.info(f'Running webhook {webhook.name} ' +
                             f'[{webhook.hook_id}].')
            self.logger.debug(f'Payload: {request}')
            webhook.run(payload)
            return JsonResponse({'timestamp': datetime.utcnow().isoformat()})
        except Webhook.DoesNotExist:
            return HttpResponseNotFound(f'No webhook with id {hook_id} found.')
