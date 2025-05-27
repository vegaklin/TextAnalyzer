from abc import ABC, abstractmethod
from pathlib import Path
from ..model.enums import PlotType

class TextOperation(ABC):
    @abstractmethod
    def execute(self, folder_path: Path, analyzer, plot_type: PlotType):
        pass