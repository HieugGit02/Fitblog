"""
Custom logging handler to write logs to database.
This handler writes log records to SystemLog model so they can be viewed in admin.
"""
import logging
from django.db import connection
from django.utils import timezone


class DatabaseLogHandler(logging.Handler):
    """
    A logging handler that writes log records to SystemLog model.
    """
    
    def emit(self, record):
        """
        Emit a log record to the database.
        """
        try:
            # Avoid circular imports by importing here
            from blog.models import SystemLog
            
            # Check if database connection is available
            try:
                connection.ensure_connection()
            except Exception:
                # Database not available, skip logging to DB
                return
            
            # Format the log message
            message = self.format(record)
            
            # Create log entry
            log = SystemLog.objects.create(
                level=record.levelname,
                logger_name=record.name,
                message=message,
                timestamp=timezone.now()
            )
        except Exception:
            # If logging to DB fails, fail silently
            # (to avoid infinite recursion or broken logging)
            self.handleError(record)
