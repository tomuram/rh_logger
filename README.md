# rh_logger
## A package for logging / process status / metrics reporting for rhoana

How to use:

* `logger = rh_logger.get_logger(name, args)`: get a logger with the process's name and enough context in `args` to figure out the data inputs and outputs used to run it. 
* `logger.start_process(msg)`: log the start of a process
* `logger.end_process(msg)`: log the end of a process
* `logger.report_metric(name, metric, subcontext=None)`: Report a metric such as accuracy or execution time. Subcontext gives enough information to narrow the metric to an instance of the named step.
* `logger.report_event(name, event, context=None)`: Report an event.  Context gives enough information to narrow the metric to an instance of the named step.
* `logger.report_exception(exception, msg=None)`: Report an exception. Message is `str(exception)` by default.
