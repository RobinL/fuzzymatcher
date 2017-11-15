A template Python package 
=========================

Notes
-----

A template Python package, including documentation, testing, code coverage etc.

Can be installed from Github using:

::

    pip install git+https://github.com/RobinL/python_package_template.git


Use Google docstring style:
http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html

More information about setting up Sphinx, especially with ReadTheDocs:
https://samnicholls.net/2016/06/15/how-to-sphinx-readthedocs/

Things to remember:
-------------------

ReadTheDocs will fail by default if your project has dependencies (e.g. pandas)
To correct, go to Advanced Settings in the ReadTheDocs web interface, and point it at your requirements.txt file.