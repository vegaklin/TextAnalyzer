from ..interface.text_operation import TextOperation
from ..util.file_handler import FileHandler
from ..util.plotter import Plotter
from ..model.enums import PlotType
from ..analyzer.pymorphy2_analyzer import Pymorphy2Analyzer
from ..analyzer.pymystem3_analyzer import Pymystem3Analyzer
from pathlib import Path
import pandas as pd
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

class AdjectiveAnalysisOperation(TextOperation):
    def __init__(self, file_handler: FileHandler, plotter: Plotter, adjective_analyzer):
        self.file_handler = file_handler
        self.plotter = plotter
        self.adjective_analyzer = adjective_analyzer
        self.lock = Lock()

    def execute(self, folder_path: Path, analyzer, plot_type: PlotType):
        adjective_types_by_year, all_adjective_types = self.process_files(folder_path, analyzer)
        self.save_results(adjective_types_by_year, all_adjective_types)
        return adjective_types_by_year

    def process_file(self, file_path: Path, analyzer) -> tuple[dict, set]:
        text = self.file_handler.read_text_file(file_path)
        grammems = analyzer.count_grammems_lemmas(text)
        local_adjective_types = {}
        local_adjective_lemmas = defaultdict(set)
        for grammem, lemma_counts in grammems.items():
            if (
                (isinstance(analyzer, Pymorphy2Analyzer) and grammem in ["ADJF", "ADJS"]) or
                (isinstance(analyzer, Pymystem3Analyzer) and grammem == "A")
            ):
                for lemma, count in lemma_counts.items():
                    adj_type = self.adjective_analyzer.get_qualitative_or_relative(lemma)
                    local_adjective_types[adj_type] = local_adjective_types.get(adj_type, 0) + count
                    local_adjective_lemmas[adj_type].add(lemma)

        return local_adjective_types, local_adjective_lemmas

    def process_files(self, folder_path: Path, analyzer):
        adjective_types_by_year = {}
        all_adjective_types = defaultdict(set)
        max_workers = 8 

        for year_folder in folder_path.iterdir():
            if year_folder.is_dir():
                year = year_folder.name
                adjective_types_by_year[year] = {}
                files = list(year_folder.glob("*.txt")) + list(year_folder.glob("*.xml"))
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = [
                        executor.submit(self.process_file, file_path, analyzer)
                        for file_path in files
                    ]
                    for future in futures:
                        local_adjective_types, local_adjective_lemmas = future.result()
                        with self.lock:
                            for adj_type, count in local_adjective_types.items():
                                adjective_types_by_year[year][adj_type] = adjective_types_by_year[year].get(adj_type, 0) + count
                            for adj_type, lemmas in local_adjective_lemmas.items():
                                all_adjective_types[adj_type].update(lemmas)
        return adjective_types_by_year, all_adjective_types

    def save_results(self, adjective_types_by_year, all_adjective_types):
        data = [{"Лемма": lemma, "Тип": adj_type} for adj_type, lemmas in all_adjective_types.items() for lemma in sorted(lemmas)]
        self.file_handler.save_to_excel(
            pd.DataFrame(data),
            self.file_handler.results_dir / "all_adjectives.xlsx"
        )
        years = sorted(adjective_types_by_year.keys())
        types = ["качественное", "относительное", "качественное и относительное"]
        data = [
            {"Тип": adj_type, **{year: round(adjective_types_by_year[year].get(adj_type, 0) / sum(adjective_types_by_year[year].values()) * 100, 2) if sum(adjective_types_by_year[year].values()) > 0 else 0.0 for year in years}}
            for adj_type in types
        ]
        self.file_handler.save_to_excel(
            pd.DataFrame(data),
            self.file_handler.results_dir / "adjective_type_percentages.xlsx"
        )