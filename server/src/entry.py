# -*- coding:utf-8 -*-

from optparse import OptionParser

import webapp

from config import prod, test


CONFIG_MAP = {
    "test": test.TestConfig(),
    "prod": prod.ProdConfig(),
}


def parse_args():
    parser = OptionParser()

    parser.add_option("--env", dest="env", default="test")
    parser.add_option("--host", dest="host", default="0.0.0.0")
    parser.add_option("--port", dest="port", default=5000, type="int")
    parser.add_option("--workers", dest="workers", default=1, type="int")

    return parser.parse_args()


def main():
    options, _ = parse_args()
    config = CONFIG_MAP[options.env]
    app = webapp.create_app(config)
    app.run(host=options.host, port=options.port, workers=options.workers, access_log=False)


if __name__ == "__main__":
    main()
