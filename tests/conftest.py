import tempfile
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def examples_dir() -> Path:
    """Path to the examples directory."""
    return Path(__file__).parent.parent / "examples"


@pytest.fixture
def tmp_output_dir():
    """Create a temporary directory for test outputs, cleaned up after the test."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def output_dir_factory(examples_dir):
    """Factory fixture to get paths to example files for different renderers."""

    def _get_output_path(domain: str, renderer_name: str) -> Path:
        path = Path(__file__).parent / "output" / domain / renderer_name
        return path

    return _get_output_path


@pytest.fixture
def sample_file_factory(examples_dir):
    """Factory fixture to get paths to example files for different renderers."""

    def _get_sample_path(domain: str, renderer_name: str, filename: str) -> Path:
        path = examples_dir / domain / renderer_name / filename
        if not path.exists():
            raise FileNotFoundError(f"Sample file not found: {path}")
        return path

    return _get_sample_path


@pytest.fixture(scope="session")
def root_dir() -> Path:
    """Project root directory (useful for general path resolution)."""
    return Path(__file__).parent.parent
