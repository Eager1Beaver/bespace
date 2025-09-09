# logger.py
import logging
import os
import sys

class logger(logging.Logger):
    def _stringify(self, obj):
        try:
            return str(obj)
        except Exception:
            try:
                return repr(obj)
            except Exception:
                return "<unprintable>"

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=1):
        # If user passed extra args but msg has no %-placeholders, join them
        if args and isinstance(msg, str) and ('%' not in msg):
            try:
                parts = [msg] + [self._stringify(a) for a in args]
                msg = " ".join(parts)
                args = ()  # prevent stdlib from doing %-formatting
            except Exception:
                msg = f"{msg} {args}"
                args = ()

        super()._log(level, msg, args, exc_info=exc_info, extra=extra,
                     stack_info=stack_info, stacklevel=stacklevel)

# Make logger the default logger class
logging.setLoggerClass(logger)

def _build_formatter():
    # Example: 2025-09-06 04:23:01,238 - static_cca.py - INFO - message
    return logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S,%f"
    )

def _ensure_handler(logger_obj):
    if logger_obj.handlers:
        return logger_obj

    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger_obj.setLevel(level)

    stream = logging.StreamHandler(stream=sys.stdout)
    stream.setLevel(level)
    stream.setFormatter(_build_formatter())
    logger_obj.addHandler(stream)

    log_file = os.getenv("LOG_FILE")
    if log_file:
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setLevel(level)
        fh.setFormatter(_build_formatter())
        logger_obj.addHandler(fh)

    # Avoid duplicate logs if root has handlers
    logger_obj.propagate = False
    return logger_obj

# Module-level logger used across the project
logger = _ensure_handler(logging.getLogger("bespace"))
