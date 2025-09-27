"""
Structured logging utilities.
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional


class StructuredLogger:
    """Structured logger for consistent logging across the application"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            self._setup_logger()
    
    def _setup_logger(self):
        """Setup logger with structured formatting"""
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)8s] %(name)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def info(self, message: str, metadata: Optional[Dict[str, Any]] = None):
        """Log info message with optional metadata"""
        if metadata:
            full_message = f"{message} | {json.dumps(metadata)}"
        else:
            full_message = message
        self.logger.info(full_message)
    
    def debug(self, message: str, metadata: Optional[Dict[str, Any]] = None):
        """Log debug message with optional metadata"""
        if metadata:
            full_message = f"{message} | {json.dumps(metadata)}"
        else:
            full_message = message
        self.logger.debug(full_message)
    
    def warning(self, message: str, metadata: Optional[Dict[str, Any]] = None):
        """Log warning message with optional metadata"""
        if metadata:
            full_message = f"{message} | {json.dumps(metadata)}"
        else:
            full_message = message
        self.logger.warning(full_message)
    
    def error(self, message: str, metadata: Optional[Dict[str, Any]] = None):
        """Log error message with optional metadata"""
        if metadata:
            full_message = f"{message} | {json.dumps(metadata)}"
        else:
            full_message = message
        self.logger.error(full_message)


def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance"""
    return StructuredLogger(name)