CRITICAL = 50
ERROR    = 40
WARNING  = 30
INFO     = 20
DEBUG    = 10
NOTSET   = 0

_level_dict = {
    CRITICAL: "CRITICAL",
    ERROR: "ERROR",
    WARNING: "WARNING",
    INFO: "INFO",
    DEBUG: "DEBUG",
}

class Logger:

    level = NOTSET

    def __init__(self, name):
        self.name = name

    def setLevel(self, level):
        self.level = level

    def isEnabledFor(self, level):
        return level >= self.level

    def log(self, level, msg, *args):
        if level >= self.level:
            print(self.name, _level_dict[level], msg)

    def debug(self, msg, *args):
        self.log(DEBUG, msg, *args)

    def info(self, msg, *args):
        self.log(INFO, msg, *args)

    def warning(self, msg, *args):
        self.log(WARNING, msg, *args)

    warn = warning

    def error(self, msg, *args):
        self.log(ERROR, msg, *args)

    def critical(self, msg, *args):
        self.log(CRITICAL, msg, *args)

def getLogger(name=None):
    if name is None:
        name = "root"
    if name in _loggers:
        return _loggers[name]
    l = Logger(name)
    _loggers[name] = l
    return l

_loggers = {}