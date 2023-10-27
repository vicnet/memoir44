#!/usr/bin/env python3

import sys
import logging


class LoggingColor(logging.Formatter):

    """Logging Formatter to add colors and count warning / errors"""
    grey   = "\x1b[90m"
    green  = "\x1b[92m"
    yellow = "\x1b[93m"
    red    = "\x1b[91m"
    reset  = "\x1b[0m"

    format = "| %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: red + format + reset
    }

    def format(self, record):
        record.levelname = 'WARN' if record.levelname == 'WARNING' else record.levelname
        record.levelname = 'ERROR' if record.levelname == 'CRITICAL' else record.levelname
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

    @staticmethod
    def configure(level=logging.INFO):
        logger = logging.getLogger()
        logger.setLevel(level)
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(LoggingColor())
        logger.addHandler(ch)

def progress(count, total, suffix=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix))
    sys.stdout.flush()  # As suggested by Rom Ruben


if __name__ =='__main__':
    import logging
    LoggingColor.configure(logging.DEBUG)
    logging.debug('end')
