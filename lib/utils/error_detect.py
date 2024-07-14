from functools import wraps
import logging
import traceback
import os
from evals.api import CompletionResult

def call_without_throw(func):
    # If there is an error while calling, log the error and return the error message, rather than throwing an exception
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            logging.error(traceback.format_exc())
            result = ErrorCompletionResult(exception=traceback.format_exc())
        return result
    return wrapper

class ErrorCompletionResult(CompletionResult):
    def __init__(self, exception) -> None:
        self.exception = exception

    def get_completions(self) -> list[str]:
        return ["Error: " + str(self.exception).strip()] if self.exception else ["Unknown"]