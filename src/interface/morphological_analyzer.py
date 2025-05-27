from abc import ABC, abstractmethod

class MorphologicalAnalyzer(ABC):
    @abstractmethod
    def lemmatize(self, text: str):
        pass

    @abstractmethod
    def count_grammems(self, text: str):
        pass

    @abstractmethod
    def count_grammems_lemmas(self, text: str):
        pass