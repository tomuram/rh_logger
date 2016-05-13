'''api.py - API for the Rhoana logger'''

import enum
import os
import pkg_resources

__logging_backend = os.environ.get("RH_LOGGING_BACKEND", "default")

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
    for entry_point in pkg_resources.WorkingSet().iter_entry_points(
        'rh_logger.backend', get_logging_backend()):
        fn = entry_point.resolve()
        result = fn(name, args)
        if result is not None:
            return result

class ExitCode(enum.Enum):
    '''Process completed successfully'''
    success = 0
    '''Process exiting because of bad input data'''
    precondition_error = 1
    '''Process exiting because of I/O or network error'''
    io_error = 2
    '''Process exiting because of internal error'''
    internal_error = 3
    
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
    
    def report_event(self, event, context=None):
        '''Report an event

        :param event: the name of the event, for instance, "Frobbing complete"
        :param context: a subcontext such as "MFOV: 5, Tile: 3"
        '''
        raise NotImplementedError()
    
    def report_exception(self, exception=None, msg=None):
        '''Report an exception
        
        :param exception: the :py:class: `Exception` that was thrown. Default
        is the one reported by sys.exc_info()
        :param msg: an informative message
        '''
        raise NotImplementedError()
