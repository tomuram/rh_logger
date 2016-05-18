'''logger.py - the Datadog logger'''

import collections
import datadog
import datetime
import os
import rh_logger.api
import sys
import traceback

DATADOG_APP_KEY = os.environ.get(
    "DATADOG_APP_KEY",
    "6e43ea6fc7bbfb27f6a693e5364e19f640c85bff")


class DatadogLogger(rh_logger.api.Logger):
    '''Logger for datadog'''

    def __init__(self, name, context):
        self.name = name
        if isinstance(context, collections.Sequence):
            self.context = context
        else:
            self.context = [context]
        datadog.initialize(api_key=os.environ["RH_DATADOG_API_KEY"],
                           app_key=DATADOG_APP_KEY)

    def start_process(self, msg):
        '''Report the start of a process

        :param msg: an introductory message for the process
        '''
        datadog.api.Event.create(title="%s starting" % self.name,
                                 text=msg,
                                 alert_type="info",
                                 tags=[self.name, "startup"] + self.context)

    def end_process(self, msg, exit_code):
        '''Report the end of a process

        :param msg: an informative message about why the process ended
        :param exit_code: one of the :py:class: `ExitCode` enumerations
        '''
        if exit_code == rh_logger.ExitCode.success:
            datadog.api.Event.create(title="%s exiting" % self.name,
                                     text=msg,
                                     alert_type="success",
                                     tags=[self.name, "success"])
        else:
            datadog.api.Event.create(title="%s exiting with error" % self.name,
                                     text=msg,
                                     alert_type="error",
                                     tags=[self.name, "error", exit_code.name])

    def report_metric(self, name, metric, subcontext=None):
        '''Report a metric such as accuracy or execution time

        :param name: name of the metric, e.g. "Rand score"
        :param metric: the value
        :param subcontext: an optional sequence of objects identifying a
        subcontext for the metric such as a tile of the MFOV being processed.
        '''
        if isinstance(subcontext, collections.Sequence):
            tags = [self.name] + subcontext
        elif subcontext is not None:
            tags = [self.name, subcontext]
        else:
            tags = [self.name]
        datadog.api.Metric.send(metric=name,
                                points=[metric],
                                host=self.name,
                                tags=tags)

    def report_event(self, event, context=None):
        '''Report an event

        :param event: the name of the event, for instance, "Frobbing complete"
        :param context: a subcontext such as "MFOV: 5, Tile: 3"
        '''
        if isinstance(context, collections.Sequence):
            tags = [self.name] + context
        else:
            tags = [self.name, context]
        datadog.api.Event.create(title=event,
                                 text=event,
                                 alert_type="info",
                                 tags=tags)

    def report_exception(self, exception=None, msg=None):
        '''Report an exception

        :param exception: the :py:class: `Exception` that was thrown. Default
        is the one reported by sys.exc_info()
        :param msg: an informative message
        '''
        if exception is None:
            exc_type, exception, traceback = sys.exc_info()
        else:
            exc_type = type(exception)
            traceback = None
        if msg is None:
            msg = str(exception)
        tags = [self.name, "exception", exc_type.__name__]
        if traceback is not None:
            # TODO: add stack breadcrumbs to the tags
            #       Consider using Sentry for logging exceptions
            msg += "\n" + traceback.format_exception(
                exc_type, exception, traceback)
        datadog.api.Event.create(title="Exception report",
                                 text=msg,
                                 alert_type="error",
                                 tags=tags)
        datadog.api.Metric.send(metrics="exception",
                                points=[(datetime.datetime.now(),
                                         1)],
                                type="counter",
                                tags=tags)


def get_logger(name, context=None):
    if context is None:
        context = []
    return DatadogLogger(name, context)
