# -*- coding: utf-8 -*-
"""
Logger Configuration Module

Provides centralized logging configuration for the Sec Interp plugin.
"""

import logging
import sys


def get_logger(name):
    """Get a configured logger for the plugin.
    
    Args:
        name: Name of the logger (typically __name__ from calling module)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(f"SecInterp.{name}")
    
    # Only configure if not already configured
    if not logger.handlers:
        # Set level - change to INFO for production, DEBUG for development
        logger.setLevel(logging.DEBUG)
        
        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        
        # Create formatter
        formatter = logging.Formatter(
            '[%(asctime)s] %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(handler)
        
        # Prevent propagation to avoid duplicate messages
        logger.propagate = False
    
    return logger
