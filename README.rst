.. image:: https://badge.fury.io/py/fuzzymatcher.svg
    :target: https://badge.fury.io/py/fuzzymatcher

.. image:: https://codecov.io/gh/RobinL/fuzzymatcher/branch/dev/graph/badge.svg
  :target: https://codecov.io/gh/RobinL/fuzzymatcher



fuzzymatcher
======================================

A Python package that allows the user to fuzzy match two pandas dataframes based on one or more common fields.

Fuzzymatches uses ``sqlite3``'s Full Text Search to find potential matches.

It then uses `probabilistic record linkage <https://en.wikipedia.org/wiki/Record_linkage#Probabilistic_record_linkage>`_ to score matches.

Finally it outputs a list of the matches it has found and associated score. 


Installation
------------

``pip install fuzzymatcher``

Note that you will need a build of sqlite which includes FTS4.  This seems to be widely included by default, but otherwise `see here <https://www.sqlite.org/fts3.html#compiling_and_enabling_fts3_and_fts4>`_.

Usage
-----

See `examples.ipynb <https://github.com/RobinL/fuzzymatcher/blob/master/examples.ipynb>`_ for examples of usage and the output.

You can run these examples interactively `here <https://mybinder.org/v2/gh/RobinL/fuzzymatcher/master?filepath=examples.ipynb>`_.

Simple example
--------------

Suppose you have a table called ``df_left`` which looks like this:

====  =============
  id  ons_name
====  =============
   0  Darlington
   1  Monmouthshire
   2  Havering
   3  Knowsley
   4  Charnwood
 ...  etc.
====  =============

And you want to link it to a table ``df_right`` that looks like this:

====  =========================
  id  os_name
====  =========================
   0  Darlington (B)
   1  Havering London Boro
   2  Sir Fynwy - Monmouthshire
   3  Knowsley District (B)
   4  Charnwood District (B)
 ...  etc.
====  =========================

You can write:

.. code:: python

  import fuzzymatcher
  fuzzymatcher.fuzzy_left_join(df_left, df_right, left_on = "ons_name", right_on = "os_name")

And you'll get:

==================  =============  =========================
  best_match_score  ons_name       os_name
==================  =============  =========================
          0.178449  Darlington     Darlington (B)
          0.133371  Monmouthshire  Sir Fynwy - Monmouthshire
          0.102473  Havering       Havering London Boro
          0.155775  Knowsley       Knowsley District (B)
          0.155775  Charnwood      Charnwood District (B)
               ...  etc.           etc.
==================  =============  =========================
