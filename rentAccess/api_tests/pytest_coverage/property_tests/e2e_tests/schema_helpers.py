import json
from os.path import join, dirname, abspath
from jsonschema import validate
import logging


def assert_valid_schema(data, schema_file):
    """ Checks whether the given data matches the schema """

    schema = _load_json_schema(schema_file)
    logging.info("Loading Schema")
    return validate(data, schema)


def _load_json_schema(filename):
    """ Loads the given schema file """

    absolute_path = join(dirname(abspath(__file__)), 'schemas' + filename)
    logging.info(absolute_path)
    with open(absolute_path) as schema_file:
        logging.info("Loading Schema")
        return json.loads(schema_file.read())
