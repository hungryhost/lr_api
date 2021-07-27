import json
import pytest
import logging

from django.test import TestCase
from django.urls import reverse
from common.models import SupportedCity
from ..factories import PropertyFactory, PropertyAddressFactory
import properties.models as p_models
from api_tests.pytest_coverage.property_tests.e2e_tests.json_factories import PropertyJsonFactory
from api_tests.pytest_coverage.schema_helpers import assert_valid_schema


