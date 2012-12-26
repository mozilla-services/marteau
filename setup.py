import os
from setuptools import setup, find_packages
from marteau import __version__

install_requires = ['funkload', 'pyramid',
                    'gevent',
                    'circus', 'PyYAML', 'paramiko',
                    'Mako', 'retools',
                    'virtualenv', 'Sphinx',
                    'pyramid_simpleform',
                    'formencode',
                    'pyramid_whoauth',
                    'repoze.who.plugins.browserid',
                    'pyramid_beaker',
                    'pyramid_macauth',
                    'pyramid_multiauth',
                    'wsgiproxy',
                    'vaurienclient',
                    'requests',
                    'fabric'
                    ]


try:
    import importlib
except ImportError:
    install_requires.append('importlib')

DOCS = os.path.join(os.path.dirname(__file__), 'marteau', 'docs', 'source')
BUILD = os.path.join(os.path.dirname(__file__), 'marteau', 'docs', 'build')


try:
    import argparse     # NOQA
except ImportError:
    install_requires.append('argparse')

try:
    from sphinx.setup_command import BuildDoc

    kwargs = {'cmdclass': {'build_sphinx': BuildDoc},
            'command_options': {'build_sphinx':
                        {'project': ('setup.py', 'marteau'),
                        'version': ('setup.py', __version__),
                        'release': ('setup.py', __version__),
                        'source_dir': ('setup.py', DOCS),
                        'build_dir': ('setup.py', BUILD)}}}

except ImportError:
    kwargs = {}


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
      test_requires=['nose', 'WebTest'],
      test_suite='nose.collector',
      entry_points="""
      [console_scripts]
      marteau-serve = marteau.runserver:main
      marteau = marteau.job:main
      """, **kwargs)
