from enum import Enum

class AnalyzerChoice(Enum):
    PYMORPHY2 = "pymorphy2"
    PYMYSTEM3 = "pymystem3"

class AdjectiveAnalyzerChoice(Enum):
    OPEN_CORPORA = "OpenCorpora"
    WIKI = "ВикиСловарь"

class PlotType(Enum):
    BAR = "bar"
    LINE = "line"