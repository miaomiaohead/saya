# -*- coding:utf-8 -*-

import os
import sys

import webapp
import config

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 输入参数没有指定环境 或者 参数无效，才从环境变量中获取环境
env = sys.argv[1] if len(sys.argv) >= 2 else None
cfg = config.env_config.get(env)

if not env or not cfg:
    env = os.environ.get("SERVER_ENV", "formal")
    cfg = config.env_config.get(env)

if not cfg:
    raise Exception("env '%s' invalid" % env)

# 创建app
app = webapp.create_app(cfg)
app.server_env = env

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=cfg.PORT)
