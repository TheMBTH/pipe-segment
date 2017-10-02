import pytest
import posixpath as pp
import newlinejson as nlj

from apache_beam.testing.test_pipeline import TestPipeline as _TestPipeline
# rename the class to prevent py.test from trying to collect TestPipeline as a unit test class

import apache_beam as beam
from apache_beam.testing.util import assert_that
from apache_beam.testing.util import equal_to
from apache_beam.testing.util import open_shards
from apache_beam import Map
from apache_beam import GroupByKey
from apache_beam import FlatMap

import pipeline
from pipeline.transforms.segment import Segment
from pipeline.coders import JSONCoder
from pipeline.coders import Timestamp2DatetimeDoFn
from pipeline.coders import Datetime2TimestampDoFn


@pytest.mark.filterwarnings('ignore:Using fallback coder:UserWarning')
@pytest.mark.filterwarnings('ignore:The compiler package is deprecated and removed in Python 3.x.:DeprecationWarning')
@pytest.mark.filterwarnings('ignore:open_shards is experimental.:FutureWarning')
class TestPipeline():

    def _run_pipeline (self, source, sink, expected, args=[]):
        args += [
            'local',
            '--sourcefile=%s' % source,
            '--sink=%s' % sink
        ]

        pipeline.__main__.run(args, force_wait=True)

        with nlj.open(expected) as expected:
            with open_shards('%s*' % sink) as output:
                assert sorted(expected) == sorted(nlj.load(output))

    def test_Pipeline_basic_args(self, test_data_dir, temp_dir):
        source = pp.join(test_data_dir, 'input.json')
        sink = pp.join(temp_dir, 'output')
        expected = pp.join(test_data_dir, 'expected.json')

        self._run_pipeline(source, sink, expected)

    def test_Pipeline_window(self, test_data_dir, temp_dir):
        source = pp.join(test_data_dir, 'input.json')
        sink = pp.join(temp_dir, 'output')
        expected = pp.join(test_data_dir, 'expected-window-1.json')
        args = [ '--window_size=1' ]
        self._run_pipeline(source, sink, expected, args)

    def test_Pipeline_parts(self, test_data_dir, temp_dir):
        source = pp.join(test_data_dir, 'input.json')
        sink = pp.join(temp_dir, 'output')
        expected = pp.join(test_data_dir, 'expected.json')

        with _TestPipeline() as p:
            result = (
                p
                | beam.io.ReadFromText(file_pattern=source, coder=JSONCoder())
                | "timestamp2datetime" >> beam.ParDo(Timestamp2DatetimeDoFn())
                | "ExtractMMSI" >> Map(lambda row: (row['mmsi'], row))
                | "GroupByMMSI" >> GroupByKey('mmsi')
                | Segment()
                | "Flatten" >> FlatMap(lambda(k,v): v)
                | "datetime2timestamp" >> beam.ParDo(Datetime2TimestampDoFn())
                | "WriteToSink" >> beam.io.WriteToText(
                    file_path_prefix=sink,
                    num_shards=1,
                    coder=JSONCoder()
                )
            )

            p.run()
            with nlj.open(expected) as expected:
                with open_shards('%s*' % sink) as output:
                    assert sorted(expected) == sorted(nlj.load(output))

