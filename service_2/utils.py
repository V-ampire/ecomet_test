import traceback


def str_exception(exc: Exception, with_traceback=False) -> str:
    try:
        message = f"{type(exc)}: {str(exc)}."
    except Exception as e:
        message = (f"{type(exc)}: "
                   f"<Error when converting an exception to the line: {e}>")
    if with_traceback:
        traceback_str = ''.join(traceback.format_tb(exc.__traceback__))
        message = f"{message}\n{traceback_str}"
    return message
