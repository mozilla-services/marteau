from setuptools import setup, find_packages
from marteau import __version__


install_requires = ['funkload', 'bottle', 'rq', 'rq-dashboard',
                    'circus', 'PyYAML', 'paramiko']


try:
    import argparse     # NOQA
except ImportError:
    install_requires.append('argparse')


with open('README.rst') as f:
    README = f.read()


setup(name='marteau',
      version=__version__,
      packages=find_packages(),
      description=("Hammer it."),
      long_description=README,
      author="Tarek Ziade",
      author_email="tarek@ziade.org",
      include_package_data=True,
      zip_safe=False,
      classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: Apache Software License",
        "Development Status :: 1 - Planning"],
      install_requires=install_requires,
      test_requires=['nose'],
      test_suite='nose.collector',
      entry_points="""
      [console_scripts]
      marteau-serve = marteau.runserver:main
      marteau = marteau.job:main
      """)
