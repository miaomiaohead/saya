# -*- coding:utf-8 -*-

import os

from flask import session, jsonify, Blueprint, Response, current_app as app


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
