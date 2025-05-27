from ..interface.morphological_analyzer import MorphologicalAnalyzer
from pymystem3 import Mystem
import re
from collections import defaultdict

class Pymystem3Analyzer(MorphologicalAnalyzer):
    def __init__(self):
        self.morph = Mystem(disambiguation=True)
        self.pos_regex = re.compile(r'^([A-Z]+)')

    def lemmatize(self, text: str):
        analysis = self.morph.analyze(text)
        return [
            (entry["text"], entry["analysis"][0]["lex"] if entry["analysis"] else entry["text"])
            for entry in analysis if "analysis" in entry
        ]

    def count_grammems(self, text: str):
        analysis = self.morph.analyze(text)
        grammems_count = {}
        for entry in analysis:
            if "analysis" in entry:
                if entry["analysis"]:
                    gr_info = entry["analysis"][0]["gr"]
                    match = self.pos_regex.match(gr_info)
                    pos = match.group(1) if match else "UNKNOWN"
                    grammems_count[pos] = grammems_count.get(pos, 0) + 1
                else:
                    grammems_count["UNKNOWN"] = grammems_count.get("UNKNOWN", 0) + 1
        return grammems_count

    def count_grammems_lemmas(self, text: str):
        analysis = self.morph.analyze(text)
        grammems_count = defaultdict(dict)
        for entry in analysis:
            if "analysis" in entry:
                if entry["analysis"]:
                    gr_info = entry["analysis"][0]["gr"]
                    lemma = entry["analysis"][0].get("lex", "UNKNOWN")
                    match = self.pos_regex.match(gr_info)
                    pos = match.group(1) if match else "UNKNOWN"
                    grammems_count[pos][lemma] = grammems_count[pos].get(lemma, 0) + 1
                else:
                    lemma = entry.get("text", "UNKNOWN").lower()
                    grammems_count["UNKNOWN"][lemma] = grammems_count["UNKNOWN"].get(lemma, 0) + 1
        return grammems_count