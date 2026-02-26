import os
import pytest

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


@pytest.fixture
def data_dir():
    return DATA_DIR


@pytest.fixture
def sample_peaks1(data_dir):
    return os.path.join(data_dir, 'sample_peaks1.bed')


@pytest.fixture
def sample_peaks2(data_dir):
    return os.path.join(data_dir, 'sample_peaks2.bed')


@pytest.fixture
def sample_reads1(data_dir):
    return os.path.join(data_dir, 'sample_reads1.bed')


@pytest.fixture
def sample_reads2(data_dir):
    return os.path.join(data_dir, 'sample_reads2.bed')
