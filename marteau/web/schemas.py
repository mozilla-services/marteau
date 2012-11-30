from formencode import Schema, validators, FancyValidator, Invalid


class Cycles(FancyValidator):

    def _to_python(self, value, state):
        value = value.strip().lower()
        numbers = value.split(':')
        error = 'Cycles are column separated integers'

        for number in numbers:
            if not number.isdigit():
                raise Invalid(error, value, state)

        return value


class JobSchema(Schema):

    filter_extra_fields = True
    allow_extra_fields = True
    ignore_key_missing = True

    repo = validators.String(not_empty=True)
    redirect_url = validators.String()
    cycles = Cycles()
    duration = validators.Int(optional=True)
    nodes = validators.Int()
    fixture_plugin = validators.String()   # should look at list instead
    fixture_options = validators.String()
    #email = validators.Email()


class NodeSchema(Schema):

    filter_extra_fields = True
    allow_extra_fields = True

    name = validators.String(not_empty=True)
