# -*- coding:utf-8 -*-

import os

from flask import session, jsonify, Blueprint, request, current_app as app


blue_print = Blueprint("debug", __name__)


@blue_print.route("/", methods=["get", "post"])
@blue_print.route("/list_api", methods=["get", "post"])
def list_api():
    url_iter = app.url_map.iter_rules()
    scopes = [rule.rule for rule in url_iter]
    scopes.append("/webapi/search/es_index_status")
    scopes.append("/webapi/search/es_index_page")
    scopes.sort()
    return "<br>".join(scopes)


@blue_print.route("/status", methods=["get", "post"])
def health():
    sessions = {}
    for k, v in session.items():
        sessions[k] = v
    resp = {
        "env": app.server_env,
        "sessions": sessions,
        "cwd": os.getcwd(),
    }
    return jsonify(resp)


@blue_print.route("/echo", methods=["get", "post"])
def echo():
    sessions = {}
    for k, v in session.items():
        sessions[k] = v

    headers = {}
    for k, v in request.headers:
        headers[k] = v

    body_bytes = request.get_data()
    body = str(body_bytes)

    url = request.url

    resp = {
        "sessions": sessions,
        "headers": headers,
        "body": body,
        "url": url,
    }
    return jsonify(resp)
