import os
import tempfile

from fabric.operations import put
from fabric.decorators import parallel, hosts

from marteau.queue import Queue


nodes = [node.name for node in Queue().get_nodes()]


@parallel    # can be used if the key agent is loaded
@hosts(*nodes)
def deploy_key():
    """Deploy the auth key to all nodes"""
    fd, path = tempfile.mkstemp()
    os.close(fd)

    with open(path, 'w') as f:
        try:
            f.write(os.environ['AUTH_KEY'])
        except KeyError:
            msg = 'Make sure you define an AUTH_KEY in the env.'
            raise KeyError(msg)

    try:
        put(local_path=path, remote_path='/home/marteau/loadtest.auth',
            mode=0770)
    finally:
        os.remove(path)

