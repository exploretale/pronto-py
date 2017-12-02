# -*- coding: utf-8 -*-

import requests
from flask import session, abort


def get_request(url, data=None):
    req = None
    try:
        if data:
            req = requests.get(url, params=data)
        else:
            req = requests.get(url)
    except requests.exceptions.ConnectionError:
        abort(503)
    if req.status_code == 401:
        abort(401)
    return req
