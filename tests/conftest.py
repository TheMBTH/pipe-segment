import posixpath
import os
import tempfile
import shutil

import pytest

TESTS_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_DATA_DIR = posixpath.join(TESTS_DIR, 'data')


@pytest.fixture(scope='session')
def test_data_dir():
    return TEST_DATA_DIR


@pytest.fixture(scope='function')
def temp_dir(request):
    d = tempfile.mkdtemp()

    def fin():
        shutil.rmtree(d, ignore_errors=True)

    request.addfinalizer(fin)
    return d