# -*- coding: utf-8 -*-
# Copyright (C) 2019 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>

import hashlib

from django.conf import settings
from django.http import HttpResponseForbidden
from functools import wraps
from hmac import compare_digest, digest


def verify_signature(func):
    @wraps(func)
    def func_wrapper(request, *args, **kwargs):
        if not compare_digest(digest(b'test', request.body, hashlib.sha1),
                              request.META.get('HTTP_X-Hub-Signature')):
            return HttpResponseForbidden('Signature verification failed.')

        return func(request, *args, **kwargs)
    return func_wrapper
