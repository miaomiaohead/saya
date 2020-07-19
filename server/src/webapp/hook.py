# -*- coding:utf-8 -*-


def register(app):

    @app.middleware('request')
    async def before_request(request):
        print("request")

    @app.middleware('response')
    async def after_request(request, response):
        print("response")
