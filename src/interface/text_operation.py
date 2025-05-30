from abc import ABC, abstractmethod
from pathlib import Path
from ..model.enums import PlotType
from typing import List, Tuple

class TextOperation(ABC):
    @abstractmethod
    def execute(self, periods: List[Tuple[str, str]], folder_path: Path, analyzer, plot_type: PlotType):
        pass