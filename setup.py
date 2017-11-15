from setuptools import setup

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
