from ..interface.text_operation import TextOperation
from ..util.file_handler import FileHandler
from ..util.plotter import Plotter
from ..model.enums import PlotType
from pathlib import Path
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from typing import List, Tuple

class LemmatizationOperation(TextOperation):
    def __init__(self, file_handler: FileHandler, plotter: Plotter):
        self.file_handler = file_handler
        self.plotter = plotter
        self.max_workers = 8
        self.lock = Lock()

    def execute(self, periods: List[Tuple[str, str]], folder_path: Path, analyzer, plot_type: PlotType):
        word_counts = self.process_files(periods, folder_path, analyzer)
        self.save_results(periods, word_counts, plot_type)

    def process_file(self, file_path: Path, analyzer, year_dir: Path) -> int:
        text = self.file_handler.read_text_file(file_path)
        lemmas = analyzer.lemmatize(text)
        self.file_handler.save_to_excel(
            pd.DataFrame(lemmas, columns=["Токен", "Лемма"]),
            year_dir / f"{file_path.stem}_lemmatization_results.xlsx"
        )
        return len(lemmas)

    def process_files(self, periods: List[Tuple[str, str]], folder_path: Path, analyzer):
        word_counts_by_year = {}
        for start, end in periods:
            period_key = (start, end)
            word_counts_by_year[period_key] = 0
            for year in range(int(start), int(end) + 1):
                year_folder = folder_path / str(year)
                if year_folder.is_dir():
                    year_dir = self.file_handler.results_dir / str(year)
                    year_dir.mkdir(exist_ok=True)
                    files = list(year_folder.glob("*.txt")) + list(year_folder.glob("*.xml"))
                    with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                        futures = [
                            executor.submit(self.process_file, file_path, analyzer, year_dir)
                            for file_path in files
                        ]
                        for future in futures:
                            word_count = future.result()
                            with self.lock:
                                word_counts_by_year[period_key] += word_count
        return word_counts_by_year
    
    def save_results(self, periods: List[Tuple[str, str]], word_counts, plot_type: PlotType):
        period_labels = [f"{start}-{end}" if start != end else start for start, end in periods]
        self.plotter.create_plot(
            period_labels,
            [word_counts[(start, end)] for start, end in periods],
            plot_type,
            "Количество слов за каждый период",
            "Период",
            "Количество слов",
            self.file_handler.results_dir / "word_count_plot.png"
        )
        self.file_handler.save_to_excel(
            pd.DataFrame(
                [{"Период": f"{start}-{end}" if start != end else start, "Количество слов": count} for (start, end), count in word_counts.items()]
            ),
            self.file_handler.results_dir / "period_word_counts.xlsx"
        )
        return word_counts