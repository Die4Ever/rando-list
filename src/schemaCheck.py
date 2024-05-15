from jsonschema import validate, exceptions
from pathlib import Path
import yaml

# https://json-schema.org/learn/getting-started-step-by-step#going-deeper-with-properties
# https://cswr.github.io/JsonSchema/spec/introduction/

ValidString = { "type": "string", "minLength": 1, }

MaybeString = {
    "anyOf": [
        {
            "type": "string",
            "minLength": 1
        },
        {"type": "null"}, 
]}

randomizer_schema = {
    "type": "object",
    "properties": {
        "game": ValidString,
        "identifier": ValidString,
        "url": ValidString,
        "comment": MaybeString,
        "multiworld": {"type": "boolean"},
        "obsolete": {"type": "boolean"},
        "discord": ValidString,
        "community": ValidString,
        "contact": ValidString,
    },
    "required": ["game", "identifier", "url" ],
    "additionalProperties": False,
}

series_schema = {
    "type": "object",
    "properties": {
        "name": ValidString,
        "comment": MaybeString,
        "sub-series": MaybeString,
        "randomizers": {
            "type": "array",
            "minItems": 1,
            #"items": randomizer_schema,
        },
    },

    "required": ["name", "randomizers"],
    "additionalProperties": False,
}


def validateSeriesConfig(path: Path):
    failures = 0
    text = path.read_text()
    data = yaml.load(text, Loader=yaml.CLoader)
    try:
        validate(data, series_schema)
        for rando in data['randomizers']:
            try:
                validate(rando, randomizer_schema)
            except exceptions.ValidationError as e:
                failures += 1
                print('ERROR:', rando)
                id = rando.get('game', '')  + ' ' + rando.get('identifier', '')
                print('ERROR in', path, ': randomizer definition', id, '-', e.message)
    except exceptions.ValidationError as e:
        failures += 1
        print('ERROR in', path, ': series definition -', e.message)
    return failures


def validateYamlFiles():
    failures = 0
    success = 0
    for file in Path('series').glob('*'):
        try:
            new_failures = validateSeriesConfig(file)
            if new_failures == 0:
                success += 1
            failures += new_failures
        except Exception as e:
            failures += 1
            print('ERROR in', file, e)

    assert success > 0
    return failures


if __name__ == "__main__":
    exit(validateYamlFiles())
