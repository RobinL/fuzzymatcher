.. image:: https://travis-ci.org/RobinL/python_package_template.svg?branch=dev
    :target: https://travis-ci.org/RobinL/python_package_template

.. image:: https://codecov.io/gh/RobinL/python_package_test_rl/branch/dev/graph/badge.svg
  :target: https://codecov.io/gh/RobinL/python_package_test_rl

.. image:: https://readthedocs.org/projects/python-package-test-rl/badge/?version=latest
:target: http://python-package-test-rl.readthedocs.io/en/latest/
:alt: Documentation Status

A template Python package 
=========================

This repo contains a tiny Python package with a number of features:

- The API is autodocumented using Sphinx, and can be viewed on `ReadTheDocs <http://python-package-test-rl.readthedocs.io/en/latest/>`_.
- Demonstrates how to properly use logging.
- Demonstrates how to generate code coverage report 
- Demonstrates how to set up CI with Travis, which runs unit tests and a linter
- Demonstrates how to use ```setup.py``` to enable the package to be installed using ```pip```.

References
----------

Autodocumented API
~~~~~~~~~~~~~~~~~~

This relies on the use of Python docstrings combined with Sphinx.

Google docstring style can be found here:
http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html

More information on setting up Sphinx can be found here:
https://samnicholls.net/2016/06/15/how-to-sphinx-readthedocs/


Pip install
~~~~~~~~~~~
To pip install, we need a valid ```setup.py``` file, and then the package can be installed from Github using:

::

    pip install git+https://github.com/RobinL/python_package_template.git

Unit testing
~~~~~~~~~~~~

Having reviewed the options, I chose to use the standard unittest library for unit testing

It seems simplest to use the default Python module.  The main advantage of ```pytest``` in a simple project seems to be less boilerplate, but the differences are not enormous.  

To run the tests locally, we can just run:

::

    python -m unittest discover

In the travis file we run them, whilst also producing a coverage report and syncing with codecov.io


Things to remember:
-------------------

ReadTheDocs will fail by default if your project has dependencies (e.g. pandas)
To correct, go to Advanced Settings in the ReadTheDocs web interface, and point it at your requirements.txt file.

