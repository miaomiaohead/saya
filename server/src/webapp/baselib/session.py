# -*- coding:utf-8 -*-

from tools import encrypt_tools


DEFAULT_MAX_AGE = 30 * 24 * 3600


class SessionConfig(object):
    def __init__(self, session_secret, session_name=".session", session_path="/",
                 session_domain=None, max_age=None, httponly=False, secure=False):
        assert isinstance(session_secret, str)

        self.session_name = session_name
        self.session_domain = session_domain
        self.session_path = session_path
        self.session_secret = session_secret
        self.max_age = max_age or DEFAULT_MAX_AGE
        self.httponly = httponly
        self.secure = secure


class Session(object):
    def __init__(self, session_config):
        self._session_config = session_config
        self._changed = False
        self._local = {}

    def set(self, k, v):
        self._changed = True
        self._local[k] = v

    def get(self, k, default=None):
        return self._local.get(k, default)

    def keys(self):
        return self._local.keys()

    def items(self):
        return self._local.items()

    def values(self):
        return self._local.values()

    def exists(self, k):
        return k in self._local

    def __getitem__(self, key):
        return self._local[key]

    def __setitem__(self, key, value):
        self._local[key] = value

    def __contains__(self, key):
        return key in self._local

    def __len__(self):
        return len(self._local)

    def load_request_cookie(self, request):
        session_config = self._session_config
        session_name = session_config.session_name
        session_secret = session_config.session_secret

        encrypt_session = request.cookies.get(session_name)
        if encrypt_session:
            self._local = encrypt_tools.des_decrypt_dict(session_secret, encrypt_session)

    def inject_response_cookie(self, response):
        if not self._changed:
            return

        session_config = self._session_config
        session_secret = session_config.session_secret
        session_name = session_config.session_name
        session_path = session_config.session_path
        session_domain = session_config.session_domain
        max_age = session_config.max_age
        httponly = session_config.httponly
        secure = session_config.secure

        encrypt_session = encrypt_tools.des_encrypt_dict(session_secret, self._local)

        response.cookies[session_name] = encrypt_session
        response.cookies[session_name]["path"] = session_path
        response.cookies[session_name]["max-age"] = max_age
        response.cookies[session_name]["httponly"] = httponly
        response.cookies[session_name]["secure"] = secure
        if session_domain:
            response.cookies[session_name]["domain"] = session_domain

        self._changed = False

