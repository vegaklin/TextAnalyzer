from ..interface.text_operation import TextOperation
from ..util.file_handler import FileHandler
from ..util.plotter import Plotter
from ..model.enums import PlotType
from .lemmatization import LemmatizationOperation
from pathlib import Path
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from typing import List, Tuple

class POSCountOperation(TextOperation):
    def __init__(self, file_handler: FileHandler, plotter: Plotter):
        self.file_handler = file_handler
        self.plotter = plotter
        self.max_workers = 8
        self.lock = Lock()

    def execute(self, periods: List[Tuple[str, str]], folder_path: Path, analyzer, plot_type: PlotType):
        pos_counts_by_year = self.process_files(periods, folder_path, analyzer)
        word_counts = LemmatizationOperation(self.file_handler, self.plotter).process_files(periods, folder_path, analyzer)
        self.save_results(pos_counts_by_year, word_counts, plot_type)

    def process_file(self, file_path: Path, analyzer) -> dict:
        text = self.file_handler.read_text_file(file_path)
        grammems = analyzer.count_grammems(text)
        return grammems

    def process_files(self, periods: List[Tuple[str, str]], folder_path: Path, analyzer):
        pos_counts_by_year = {}
        for start, end in periods:
            period_key = (start, end)
            pos_counts_by_year[period_key] = {}
            files = []
            for year in range(int(start), int(end) + 1):
                year_folder = folder_path / str(year)
                if year_folder.is_dir():
                    files.extend(list(year_folder.glob("*.txt")) + list(year_folder.glob("*.xml")))

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = [
                    executor.submit(self.process_file, file_path, analyzer)
                    for file_path in files
                ]
                for future in futures:
                    grammems = future.result()
                    with self.lock:
                        for grammem, count in grammems.items():
                            pos_counts_by_year[period_key][grammem] = pos_counts_by_year[period_key].get(grammem, 0) + count
        return pos_counts_by_year

    def save_results(self, pos_counts_by_year, word_counts, plot_type: PlotType):
        all_grammems = set()
        for period in pos_counts_by_year:
            all_grammems.update(pos_counts_by_year[period].keys())
        for grammem in all_grammems:
            periods = sorted(pos_counts_by_year.keys(), key=lambda x: x[0])
            period_labels = [f"{start}-{end}" if start != end else start for start, end in periods]
            counts = [pos_counts_by_year[period].get(grammem, 0) for period in periods]
            frequencies = [
                round((count / word_counts.get(period, 1)) * 100, 5) if word_counts.get(period, 1) > 0 else 0.0
                for period, count in zip(periods, counts)
            ]
            df = pd.DataFrame({
                "Период": period_labels,
                f"Количество {grammem}": counts,
                f"Процент {grammem}": frequencies
            })
            self.file_handler.save_to_excel(df, self.file_handler.results_dir / f"{grammem}_counts.xlsx")
            self.plotter.create_plot(
                period_labels, frequencies, plot_type,
                f"Процент слов для {grammem}", "Период", "Процент",
                self.file_handler.results_dir / f"{grammem}_plot.png"
            )