from ...interface.adjective_analyzer import AdjectiveAnalyzer
import pymorphy2

class OpenCorporaAdjectiveAnalyzer(AdjectiveAnalyzer):
    def __init__(self):
        self.morph = pymorphy2.MorphAnalyzer()

    def get_qualitative_or_relative(self, lemma: str) -> str:
        parses = self.morph.parse(lemma)
        for parsed in parses:
            if 'Qual' in parsed.tag:
                return "качественное"
        return "относительное"