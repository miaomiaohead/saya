# -*- coding:utf-8 -*-

import os
import logging
import time


class StatisticHelper(object):
    """统计工具 输出用于统计的日志
    """
    def __init__(self, logger_file):
        # init logger
        self._logger = logging.getLogger("pyserver-statistic")
        self._logger.setLevel(logging.INFO)

        # create log dir
        if not os.path.exists(os.path.dirname(logger_file)):
            os.mkdir(os.path.dirname(logger_file))

        # init handler
        log_handler_init = logging.handlers.TimedRotatingFileHandler
        log_handler = log_handler_init(logger_file,
                                       when='D',
                                       interval=1,
                                       encoding='UTF-8',
                                       backupCount=7)
        log_handler.setLevel(logging.INFO)
        log_handler.setFormatter(logging.Formatter("%(message)s"))
        self._logger.addHandler(log_handler)

    def append_record(self, subject, key, value, description=""):
        now = int(time.time())
        self._logger.info(f"{now}|{subject}|{key}|{value}|{description}")
