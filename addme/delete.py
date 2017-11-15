# -*- coding: utf-8 -*-

"""
Testing travis
"""

import logging
import pandas as pd

log = logging.getLogger(__name__)

def addme(num1, num2):
    """Add two numberss together using pandas Series.sum()

    Args:
        num1: A number
        num2: The number to add to num1

    Returns:
        numeric: The two numbers added together
    """

    log.debug("hello")
    log.warning("omg")

    total = pd.Series([num1, num2]).sum()

    a = 1 # Pylint will warn here

    return total
