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


def post_request(url, data=None, files=None):
    req = None
    if files:
        req = requests.post(url, files=files)
    elif data:
        req = requests.post(url, json=data)
    else:
        req = requests.post(url)
    if req.status_code == 401:
        abort(401)
    return req


def put_request(url, data=None):
    req = None
    if data:
        req = requests.put(url, json=data, headers=headers)
    else:
        req = requests.put(url, headers=headers)
    return req


def delete_request(url, data=None):
    req = None
    if data:
        req = requests.delete(url, json=data, headers=headers)
    else:
        req = requests.delete(url, headers=headers)
    return req
