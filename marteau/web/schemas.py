from formencode import Schema, validators


class JobSchema(Schema):

    filter_extra_fields = True
    allow_extra_fields = True

    repo = validators.String(not_empty=True)
    redirect_url = validators.String()
    duration = validators.Int()
    nodes = validators.Int()
    email = validators.Email()
