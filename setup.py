from setuptools import setup

# see https://stackoverflow.com/questions/14399534/reference-requirements-txt-for-the-install-requires-kwarg-in-setuptools-setup-py
setup(name='fuzzymatcher',
      version='0.0.5',
      description='Fuzzy match two pandas dataframes based on one or more common fields',
      url='https://github.com/RobinL/fuzzymatcher',
      author='Robin Linacre',
      author_email='robinlinacre@hotmail.com',
      license='MIT',
      packages=['fuzzymatcher'],  # The directory to look in for the source code
      install_requires=['pandas', 'metaphone', 'python-Levenshtein', 'fuzzywuzzy', 'python-dateutil'],
      test_requires=["pylint", "coverage", "codecov"],
      keywords=["matching", "fuzzy", "probabalistic", "recordlinking", "fuzzymatching"],
      download_url = 'https://github.com/RobinL/fuzzymatcher/archive/v0.0.4.tar.gz',
      zip_safe=False)
