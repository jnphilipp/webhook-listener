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

import atexit
import hashlib
import json
import threading

from django.conf import settings
from django.core.mail import mail_admins
from django.http import HttpResponseForbidden, HttpResponseNotAllowed
from functools import wraps
from hmac import compare_digest, new
from queue import Queue
from webhook_listener.models import Webhook


def verify_signature(func):
    @wraps(func)
    def func_wrapper(request, *args, **kwargs):
        if request.method != 'Post':
            return HttpResponseNotAllowed(['POST'])

        hook_id = json.loads(request.POST['payload'])['hook_id']
        webhook = Webhook.objects.get(hook_id=hook_id)
        x_hub_signature = request.META.get('HTTP_X_HUB_SIGNATURE')
        signature = new(webhook.token, request.body, hashlib.sha1).hexdigest()
        signature = f'sha1={signature}'
        if not compare_digest(x_hub_signature, signature):
            return HttpResponseForbidden('Signature verification failed.')

        return func(request, *args, **kwargs)
    return func_wrapper


def postpone(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        _queue.put((func, args, kwargs))
    return func_wrapper


def _worker():
    while True:
        func, args, kwargs = _queue.get()
        try:
            func(*args, **kwargs)
        except Exception:
            import traceback
            details = traceback.format_exc()
            mail_admins('Background process exception', details)
        finally:
            _queue.task_done()


def _cleanup():
    _queue.join()


_queue = Queue()
_thread = threading.Thread(target=_worker)
_thread.daemon = True
_thread.start()
atexit.register(_cleanup)
