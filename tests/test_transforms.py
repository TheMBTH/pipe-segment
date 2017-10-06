import pytest
import unittest
from copy import deepcopy
from datetime import datetime

import apache_beam as beam

from apache_beam.testing.test_pipeline import TestPipeline as _TestPipeline
# rename the class to prevent py.test from trying to collect TestPipeline as a unit test class

from apache_beam.testing.util import assert_that
from apache_beam.testing.util import equal_to

from pipeline.transforms.identity import Identity
from pipeline.transforms.segment import Segment
from pipeline.coders import timestamp2datetime
from pipeline.coders import Timestamp2DatetimeDoFn

from gpsdio.schema import datetime2str



@pytest.mark.filterwarnings('ignore:Using fallback coder:UserWarning')
@pytest.mark.filterwarnings('ignore:The compiler package is deprecated and removed in Python 3.x.:DeprecationWarning')
class TestTransforms(unittest.TestCase):
    SAMPLE_DATA = [
        (1, [{'mmsi': 1, 'timestamp': datetime(2017,1,1,0,0,0)}]),
        (1, [{'mmsi': 1, 'timestamp': datetime(2017,1,1,0,0,1)}]),
        (1, [{'mmsi': 1, 'timestamp': datetime(2017,1,1,0,0,2)}]),
        (2, [{'mmsi': 2, 'timestamp': datetime(2017,1,1,0,0,0)}]),
        (2, [{'mmsi': 2, 'timestamp': datetime(2017,1,1,0,0,1)}]),
        (3, [{'mmsi': 3, 'timestamp': datetime(2017,1,1,0,0,0)}]),
    ]

    def test_Identity(self):
        with _TestPipeline() as p:
            result = (
                p
                | beam.Create(self.SAMPLE_DATA)
                | Identity())

            assert_that(result, equal_to(self.SAMPLE_DATA))

    def test_Segment(self):
        def _seg_id_from_message(msg):
            return '{}-{}'.format(msg['mmsi'], datetime2str(msg['timestamp']))

        def _add_seg_id (row):
            row[1][0]['seg_id'] = _seg_id_from_message(row[1][0])
            return row

        expected = map(_add_seg_id, deepcopy(self.SAMPLE_DATA))

        with _TestPipeline() as p:
            result = (
                p
                | beam.Create(self.SAMPLE_DATA)
                | Segment())

            assert_that(result, equal_to(expected))