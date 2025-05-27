from ..interface.morphological_analyzer import MorphologicalAnalyzer
from nltk.tokenize import RegexpTokenizer
import pymorphy2
from collections import defaultdict

class Pymorphy2Analyzer(MorphologicalAnalyzer):
    def __init__(self):
        self.morph = pymorphy2.MorphAnalyzer()
        self.tokenizer = RegexpTokenizer(r'[\w-]+')

    def lemmatize(self, text: str):
        tokens = self.tokenizer.tokenize(text)
        tokens = [token for token in tokens if not token.isdigit()]
        return [(token, self.morph.parse(token)[0].normal_form) for token in tokens]

    def count_grammems(self, text: str):
        tokens = self.tokenizer.tokenize(text)
        tokens = [token for token in tokens if not token.isdigit()]
        grammems_count = {}
        for token in tokens:
            parsed = self.morph.parse(token)[0]
            pos = parsed.tag.POS or "UNKNOWN"
            grammems_count[pos] = grammems_count.get(pos, 0) + 1
        return grammems_count

    def count_grammems_lemmas(self, text: str):
        tokens = self.tokenizer.tokenize(text)
        tokens = [token for token in tokens if not token.isdigit()]
        grammems_count = defaultdict(dict)
        for token in tokens:
            parsed = self.morph.parse(token)[0]
            pos = parsed.tag.POS or "UNKNOWN"
            lemma = parsed.normal_form
            grammems_count[pos][lemma] = grammems_count[pos].get(lemma, 0) + 1
        return grammems_count