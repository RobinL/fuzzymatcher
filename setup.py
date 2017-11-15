from setuptools import setup

# see https://stackoverflow.com/questions/14399534/reference-requirements-txt-for-the-install-requires-kwarg-in-setuptools-setup-py
setup(name='addme',
      version='0.1',
      description='Add two numbers using the pandas Series sum method',
      url='https://github.com/RobinL/python_package_template',
      author='Robin Linacre',
      author_email='robinlinacre@hotmail.com',
      license='MIT',
      packages=['addme'],
      setup_requires=['pandas'],
      test_requires=["pylint", "coverage", "codecov"],
      zip_safe=False)
