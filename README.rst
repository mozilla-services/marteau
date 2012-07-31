Continuous load testing project
===============================

Not triggered by commits, but manually

Configuration file: .marteau.yaml

Example::

    config: NodeAssignmentTest
    script: loadtest.py
    nodes: 1
    notifications:
        email:
            - tarek@mozilla.com
        irc:
            channels:
                - "irc.freenode.org#mozilla-circus"
            on_success: change

Why it's cool:

- KISS load testing (one py script) -- like readthedocs and travis-ci
- easy to trigger a massive amount of load

How it's used:

- provides a local script to try out the config. "marteau .marteau.yaml"
- you register a github repo on marteau-cld.org, it looks for .marteau.yaml
- you ping the server to run it (via the command line script or via a button on the
  site)

Marteau does the following:

- spreads the load accross multiple nodes
- runs the loadtest as defined in the config+script
- builds the merged report
- publish the report on marteau-cld.org ala travis
- sends a notification (email, irc, etc)

Limitations

- you have to prove you own the domain, by adding a key file at the root
  containing a secret text marteau-cld.org gives you
- no js tests
- the user is responsible for cleanups

Business plan:

- free for 1 node
- pay per use for > 1 node.
- use Heroku or EC2

open question:

- security ? cgroups ?
- how do scale the testings ? queues ?
- how to track usage
