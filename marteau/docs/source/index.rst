Introduction
============

**Marteau** is based on `Funkload <http://funkload.nuxeo.org/>`_, which is a
functional and load web tester based on Python.

The main features of Funkload are:

- load tests are plain Python unit tests class
- everything can be run from the command-line
- you can run the load test locally or distributed across many nodes
- nice HTML reports are generated

**Marteau** is just a Redis-based queue that let you run distributed Funkload
load tests through the web.

**Marteau** features are:

- management of a list of nodes
- management of a list of workers
- enqueues load tests and drives Funkload to run them
- display successes, failures and Funkload reports


How to create a Marteau Load Test
=================================

Creating a load test for marteau is done in three steps:

- create a Funkload load test - composed of a module and a configuration file
- create a **.marteau.yml** file, that will be used by Marteau as the
  entry point.
- push everything in a Github repository.


Create a Funkload test
----------------------

Just follow Funkload `tutorial <http://funkload.nuxeo.org/tutorial.html>`_


Create a Marteau configuration file
-----------------------------------

The Marteau configuration file must be named **.marteau.yml** and must be
located in the root of your repository.

**.marteau.yml** is a YAML file with the following options. Every option is
optional except **script**, **test** and **name**.

- **name** -- a name describing the load test.
- **script** -- the Python module that contains the Funkload test
- **test** -- The test to run, which is a class name followed by a method name.
  e.g. *Class.method*
- **wdir** -- the directory relative to the repository root that contains the
  Funkload test -- *defaults to root*
- **nodes** -- the number of nodes to use to run the test -- *defaults to 1*
- **deps** -- a list of PyPI dependencies required by the test. Will be installed
  on every node prior to starting the load.
- **cycles** -- the Funkload cycles. See `definition <http://funkload.nuxeo.org/benching.html#cycle>`_.
  If not provided, will use the one in the Funkload configurarion file.
- **duration** -- the duration in seconds of each test.
  If not provided, will use the one in the Funkload configurarion file.
- **email** -- if provided, a recipient that will receive an e-mail when a load
  test run is finished, with a link to the HTML report.

Example of a configuration file  ::

    name: MarketPlace
    test: MarketplaceTest.test_marketplace
    script: loadtest.py
    nodes: 9
    email: tarek@ziade.org
    cycles: 10:20:30:100
    duration:120
    deps:
        - PyBrowserID


Try it locally
--------------

Once you have a Funkload test and a Marteau configuration file, you can try to run
it locally by using the **marteau** script against the github repo URL or against
a directory containing a clone of the repo::

    $ marteau /Users/tarek/Dev/github.com/tokenserver
    2012-08-16 13:27:25 [31624] [INFO] Hammer ready. Where are the nails ?
    virtualenv --no-site-packages .
    ...
    2012-08-16 13:46:20 [37308] [INFO] Report generated at '/tmp/report'
    2012-08-16 13:46:20 [37308] [INFO] Bye!


In this mode, Marteau will ignore the **node** option and just execute the load
test locally. Once it's over you get the report generated, and you can view
it in your browser.


Run it on a Marteau server
--------------------------

Once you are happy with your test, you can send it to a Marteau server via
the command line, using the **--server** option.

The first thing to do is to get an API key on the target Marteau server.

Let's say Marteau is running on **http://marteau.example.com**.

Visit **http://marteau.example.com/profile** with your Browser-ID login,
then hit the *Generate key* button.

You will geta a user and secret key - you will need to set in your environment
prior to running the script::

    $ export MACAUTH_USER=tarek@mozilla.com
    $ export MACAUTH_SECRET=eab6e5f09faec33...933d0a0e4c082fa74bc1e7a

Then you can run the script to add jobs in Marteau::

    $ bin/marteau https://github.com/mozilla-services/tokenserver --server http://marteau.example.com
    2012-08-16 14:21:22 [48118] [INFO] Sending the job to the Marteau server
    2012-08-16 14:21:22 [48118] [INFO] Test added at 'http://marteau.example.com/test/a3296777b6eb4d74a879d05bbd40c204'
    2012-08-16 14:21:22 [48118] [INFO] Bye!

You can then visit the URL and watch the console live.

Alternatively, you can visit the Marteau server and just fill the form.
