from abc import ABC, abstractmethod

class AdjectiveAnalyzer(ABC):
    @abstractmethod
    def get_qualitative_or_relative(self, lemma: str) -> str:
        pass