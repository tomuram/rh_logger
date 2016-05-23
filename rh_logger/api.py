'''api.py - API for the Rhoana logger'''

import enum
import os
import pkg_resources
import rh_config
import time


def set_logging_backend(name):
    '''Set the name of the logging backend

    :param name: name of the logger (see below)

    The logger will use a backend with the registered entry point from the
    group, "rh_logger.backend", and the given name.
    '''
    global __logging_backend
    __logging_backend = name


def get_logging_backend():
    '''Return the name of the current logging backend'''
    return __logging_backend


def get_logger(name, args):
    '''Get a logger

    :param name: the name to use for reporting
    :param args: a list of string arguments giving the parameterization
         of the process, for instance the input arguments
    :returns: a Logger instance
    '''
    global logger, logging_config
    if logger.has_logger():
        return logger

    backend = get_logging_backend()
    for entry_point in pkg_resources.WorkingSet().iter_entry_points(
            'rh_logger.backend', backend):
        fn = entry_point.load()
        logging_config = logging_config_root.get(backend, {})
        logger_ = fn(name, args)
        if logger_ is not None:
            logger.set_logger(logger_)
            return logger


def get_logging_config():
    '''Get the section of the rh_config for the loaded logger'''
    return logging_config


class ExitCode(enum.Enum):
    '''Process completed successfully'''
    success = 0
    '''Process exiting because of bad input data'''
    precondition_error = 1
    '''Process exiting because of I/O or network error'''
    io_error = 2
    '''Process exiting because of internal error'''
    internal_error = 3


class TimeSeries(object):
    '''A time series is a set of metrics generated over time

    The use case is a rapid process which is being done repeatedly - this
    aggregates the metrics on that process into one API round-trip.
    '''

    def __init__(self):
        self.timestamps_and_metrics = []

    def report_metric(self, metric):
        self.timestamps_and_metrics.append((time.time(), metric))


class Logger(object):
    '''Interface for all loggers'''

    def start_process(self, msg):
        '''Report the start of a process

        :param msg: an introductory message for the process
        '''
        raise NotImplementedError()

    def end_process(self, msg, exit_code):
        '''Report the end of a process

        :param msg: an informative message about why the process ended
        :param exit_code: one of the :py:class: `ExitCode` enumerations
        '''
        raise NotImplementedError()

    def report_metric(self, name, metric, subcontext=None):
        '''Report a metric such as accuracy or execution time

        :param name: name of the metric, e.g. "Rand score"
        :param metric: the value
        :param subcontext: an optional sequence of objects identifying a
        subcontext for the metric such as a tile of the MFOV being processed.
        '''
        raise NotImplementedError()

    def report_metrics(self, name, time_series, context=None):
        '''Report a number of metrics simultaneously'''
        raise NotImplementedError()

    def report_event(self, event, context=None, log_level=None):
        '''Report an event

        :param event: the name of the event, for instance, "Frobbing complete"
        :param context: a subcontext such as "MFOV: 5, Tile: 3"
        :param log_level: an optional log level. One of logging.DEBUG,
        logging.INFO, logging.WARNING, logging.ERROR or logging.CRITICAL
        '''
        raise NotImplementedError()

    def report_exception(self, exception=None, msg=None):
        '''Report an exception

        :param exception: the :py:class: `Exception` that was thrown. Default
        is the one reported by sys.exc_info()
        :param msg: an informative message
        '''
        raise NotImplementedError()


class LoggerProxy(Logger):
    '''This is a proxy for whatever logger is chosen

    The sole purpose of this logger is to let you do things like

    from rh_logger import logger

    because what you will get is the logger proxy.
    '''

    def has_logger(self):
        return hasattr(self, "logger")

    def set_logger(self, logger):
        '''Point at the real logger'''
        assert isinstance(logger, Logger)
        self.logger = logger

    def start_process(self, msg):
        '''Report the start of a process

        :param msg: an introductory message for the process
        '''
        self.logger.start_process(msg)

    def end_process(self, msg, exit_code):
        '''Report the end of a process

        :param msg: an informative message about why the process ended
        :param exit_code: one of the :py:class: `ExitCode` enumerations
        '''
        self.logger.end_process(msg, exit_code)

    def report_metric(self, name, metric, subcontext=None):
        '''Report a metric such as accuracy or execution time

        :param name: name of the metric, e.g. "Rand score"
        :param metric: the value
        :param subcontext: an optional sequence of objects identifying a
        subcontext for the metric such as a tile of the MFOV being processed.
        '''
        self.logger.report_metric(name, metric, subcontext)

    def report_metrics(self, name, time_series, context=None):
        '''Report a number of metrics simultaneously'''
        self.logger.report_metrics(name, time_series, context)

    def report_event(self, event, context=None, log_level=None):
        '''Report an event

        :param event: the name of the event, for instance, "Frobbing complete"
        :param context: a subcontext such as "MFOV: 5, Tile: 3"
        :param log_level: an optional log level. One of logging.DEBUG,
        logging.INFO, logging.WARNING, logging.ERROR or logging.CRITICAL
        '''
        self.logger.report_event(event, context, log_level)

    def report_exception(self, exception=None, msg=None):
        '''Report an exception

        :param exception: the :py:class: `Exception` that was thrown. Default
        is the one reported by sys.exc_info()
        :param msg: an informative message
        '''
        self.logger.report_exception(exception, msg)

logging_config_root = rh_config.config.get(
    "rh-logger",
    {"logging-backend": "default"})

__logging_backend = logging_config_root.get(
    "logging-backend", "default"
)

logging_config = None
logger = LoggerProxy()
