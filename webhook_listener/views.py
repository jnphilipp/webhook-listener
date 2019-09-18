# -*- coding: utf-8 -*-
# Copyright (C) 2019 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>

import logging

from datetime import datetime
from django.conf import settings
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from webhook_listener.decorators import verify_signature


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(verify_signature, name='dispatch')
class WebhookListenerView(generic.View):
    def __init__(self, *args, **kwargs):
        super(generic.View, self).__init__(*args, **kwargs)
        self.logger = logging.getLogger('webhook_listener.WebhookListenerView')

    def get(self, request, *args, **kwargs):
        self.logger.info(f'{request}')
        return JsonResponse({'timestamp': datetime.utcnow().isoformat()},
                            json_dumps_params={'indent': 4})
