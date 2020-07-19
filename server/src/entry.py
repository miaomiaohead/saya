# -*- coding:utf-8 -*-

import webapp


def main():
    app = webapp.create_app()
    app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
