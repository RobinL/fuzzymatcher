.. image:: https://badge.fury.io/py/fuzzymatcher.svg
    :target: https://badge.fury.io/py/fuzzymatcher

.. image:: https://travis-ci.org/RobinL/fuzzymatcher.svg?branch=dev
    :target: https://travis-ci.org/RobinL/fuzzymatcher

.. image:: https://codecov.io/gh/RobinL/fuzzymatcher/branch/dev/graph/badge.svg
  :target: https://codecov.io/gh/RobinL/fuzzymatcher

.. image:: https://readthedocs.org/projects/fuzzymatcher/badge/?version=latest
    :target: http://fuzzymatcher.readthedocs.io/en/latest/
    :alt: Documentation Status


fuzzymatcher
======================================

A Python package that allows the user to fuzzy match two pandas dataframes based on one or more common fields.

Fuzzymatches uses ``sqlite3``'s Full Text Search to find potential matches.

It then uses `probabilistic record linkage <https://en.wikipedia.org/wiki/Record_linkage#Probabilistic_record_linkage>`_ to score matches.

Finally it outputs a list of the matches it has found and associated score.

Usage
-----

See `examples.ipynb <https://github.com/RobinL/fuzzymatcher/blob/dev/examples.ipynb>`_ for examples of usage and the output.

You can run these examples interactively `here <https://mybinder.org/v2/gh/RobinL/fuzzymatcher/dev?filepath=examples.ipynb>`_.


