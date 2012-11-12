import json

from cornice import Service
from pyramid.exceptions import NotFound
from pyramid.httpexceptions import HTTPBadRequest, HTTPConflict

shared_memory = Service(name="Shared Memory", path="/data/{key}")


@shared_memory.get()
def get_data(request):
    """Set the given data in the underlying database."""
    key = request.matchdict.get('key')
    value = request.redis.get(key)
    if not value:
        raise NotFound("Unknown key %s" % key)

    # the value should be json encoded, let's try to decode and return it.
    try:
        return json.dumps(value)
    except ValueError:
        # if we fail, just retun what's stored there.
        return value


@shared_memory.put()
def set_data(request):
    if not request.body:
        raise HTTPBadRequest()

    key = request.matchdict.get('key')
    # check that the data doesn't exist already. If so, return an error code
    if request.redis.get(key) is not None:
        # We don't competely match the HTTP specification here since we are
        # not returning information explaining why this failed; Basically,
        # this is because we don't want to overwrite a resource that's already
        # existing, we want this to behave as a lock.
        return HTTPConflict()

    # we should have the data to store in the body
    request.redis.set(key, request.body)
    request.response.status = "201 Created"
    return "ok"


@shared_memory.delete()
def delete_data(request):
    key = request.matchdict.get('key')
    request.redis.delete(key)
    return "ok"
