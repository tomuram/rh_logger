# rh_logger
## A package for logging / process status / metrics reporting for rhoana

How to use:

* `rh_logger.start_process(args, msg)`: log the start of a process (args gives enough context to figure out the data inputs and outputs)
* `rh_logger.end_process(msg)`: log the end of a process
* `rh_logger.report_metric(name, metric, context=None)`: Report a metric such as accuracy or execution time. Context gives enough information to narrow the metric to an instance of the named step.
