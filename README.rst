Marteau - Continuous load testing
=================================

Marteau uses Funkload to run a load test against a project and
build a report.

The entry point is a YAML configuration file.

Example::

    name: TokenServer
    test: NodeAssignmentTest.test_realistic
    script: loadtest.py
    xml: simple-bench.xml
    wdir: loadtest
    deps:
        - PyBrowserID


Run Marteau locally
-------------------

Use the **marteau** command line tool, followed by the repository
or a local directory.

Example::

    $ marteau https://github.com/mozilla-services/tokenserver


Run Marteau in the cloud
------------------------

You can push the run in the cloud by using the **--server** option.


::

    $ marteau https://github.com/mozilla-services/tokenserver --server http://marteau-server.example.org
    Running on marteau-server.example.org
    Job Id: {322423-jgkjg8k-jbkj}

This push the load test into a queue and is launched asynchonously on the server.

The call returns a job ID you can use to get a status::

    $ marteau --server http://marteau-server.example.org status {322423-jgkjg8k-jbkj}
    Running





