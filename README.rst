Marteau - Continuous load testing
=================================

Marteau uses Funkload to run a load test against a project.

The entry point is a YAML configuration file.

Example::

    name: foo
    test: StupidTest.test_simple
    script: loadtest.py
    xml: simple-bench.xml


Run Marteau locally
-------------------

Use the **marteau** command line tool, followed by the repository
or a local directory.

Example::

    $ marteau https://github.com/mozilla-services/marteau


Run Marteau in the cloud
------------------------

XXX

::
    $ marteau https://github.com/mozilla-services/marteau --server http://marteau-server.example.org
