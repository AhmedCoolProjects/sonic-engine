from sonic_engine.util.dataclass import nested_dataclass
from typing import Literal
import logging
logging.basicConfig(format='%(name)s [%(levelname)s] %(message)s')


@nested_dataclass
class LogOptions:
    "Extension log options"

    level: Literal['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'] = 'DEBUG'
    "Log level"

    dir: str = './logs'
    "Path to the logs folder"


class Logger:
    def __init__(self, config: LogOptions, ctx: str):
        self.ctx = ctx
        self.config = config
        self.level = getattr(logging, config.level)
        self.l = logging.getLogger(name=ctx)
        self.l.setLevel(self.level)

    def log(self, level: int, msg: str, *args):
        msg = ' '.join((str(arg) for arg in (msg, ) + args))
        self.l.log(level, msg)

    def debug(self, msg: str, *args):
        self.log(logging.DEBUG, str(msg), *args)

    def info(self, msg: str, *args):
        self.log(logging.INFO, str(msg), *args)

    def warning(self, msg: str, *args):
        self.log(logging.WARNING, str(msg), *args)

    def error(self, msg: str, *args):
        self.log(logging.ERROR, str(msg), *args)

    def critical(self, msg: str, *args):
        self.log(logging.CRITICAL, str(msg), *args)
