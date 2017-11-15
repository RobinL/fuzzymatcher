# -*- coding: utf-8 -*-

"""
Testing travis
"""

import logging
log = logging.getLogger(__name__)

import pandas as pd 

def addme(num1, num2):
    """
    Add two numbers together

    """

    log.debug("hello")
    log.warning("omg")

    total = pd.Series([num1, num2]).sum()

    return total