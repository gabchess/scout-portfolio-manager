import json
from pathlib import Path
from typing import Union

from .contracts import PortfolioSnapshot


class FixturePortfolioReader:
    """Observe-only reader for deterministic, Zerion-shaped fixture data."""

    def __init__(self, fixture_path: Union[str, Path]):
        self.fixture_path = Path(fixture_path)

    def snapshot(self) -> PortfolioSnapshot:
        return PortfolioSnapshot.model_validate(json.loads(self.fixture_path.read_text()))
