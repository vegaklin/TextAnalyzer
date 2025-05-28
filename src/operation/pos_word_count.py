from ..interface.text_operation import TextOperation
from ..util.file_handler import FileHandler
from ..util.plotter import Plotter
from ..model.enums import PlotType
from .lemmatization import LemmatizationOperation
from pathlib import Path
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

class POSWordCountOperation(TextOperation):
    def __init__(self, file_handler: FileHandler, plotter: Plotter):
        self.file_handler = file_handler
        self.plotter = plotter
        self.max_workers = 8
        self.lock = Lock()

    def execute(self, folder_path: Path, analyzer, plot_type: PlotType):
        word_counts_by_year = self.process_files(folder_path, analyzer)
        word_counts = LemmatizationOperation(self.file_handler, self.plotter).process_files(folder_path, analyzer)
        self.save_results(word_counts_by_year, word_counts)

    def process_file(self, file_path: Path, analyzer) -> dict:
        text = self.file_handler.read_text_file(file_path)
        grammems = analyzer.count_grammems_lemmas(text)
        return grammems

    def process_files(self, folder_path: Path, analyzer):
        word_counts_by_year = {}
        for year_folder in folder_path.iterdir():
            if year_folder.is_dir():
                year = year_folder.name
                word_counts_by_year[year] = {}
                files = list(year_folder.glob("*.txt")) + list(year_folder.glob("*.xml"))
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    futures = [
                        executor.submit(self.process_file, file_path, analyzer)
                        for file_path in files
                    ]
                    for future in futures:
                        grammems = future.result()
                        with self.lock:
                            for grammem, lemma_counts in grammems.items():
                                if grammem not in word_counts_by_year[year]:
                                    word_counts_by_year[year][grammem] = {}
                                for lemma, count in lemma_counts.items():
                                    word_counts_by_year[year][grammem][lemma] = word_counts_by_year[year][grammem].get(lemma, 0) + count
        return word_counts_by_year


    def save_results(self, word_counts_by_year, word_counts):
        all_grammems = set()
        for year in word_counts_by_year:
            all_grammems.update(word_counts_by_year[year].keys())
        for grammem in all_grammems:
            grammem_dir = self.file_handler.results_dir / grammem
            grammem_dir.mkdir(exist_ok=True)
            years = sorted(word_counts_by_year.keys())
            all_lemmas = set()
            for year in years:
                all_lemmas.update(word_counts_by_year[year].get(grammem, {}).keys())
            data = [
                {"Лемма": lemma, **{year: round(word_counts_by_year[year].get(grammem, {}).get(lemma, 0) / word_counts.get(year, 1) * 1_000_000, 5) if word_counts.get(year, 1) > 0 else 0.0 for year in years}}
                for lemma in all_lemmas
            ]
            self.file_handler.save_to_excel(
                pd.DataFrame(data),
                grammem_dir / f"{grammem}_frequencies.xlsx"
            )