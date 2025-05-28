from ..interface.text_operation import TextOperation
from ..util.file_handler import FileHandler
from ..util.plotter import Plotter
from ..model.enums import PlotType
from pathlib import Path
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

class LemmatizationOperation(TextOperation):
    def __init__(self, file_handler: FileHandler, plotter: Plotter):
        self.file_handler = file_handler
        self.plotter = plotter
        self.lock = Lock()

    def execute(self, folder_path: Path, analyzer, plot_type: PlotType):
        word_counts = self.process_files(folder_path, analyzer)
        self.plotter.create_plot(
            sorted(word_counts.keys()),
            [word_counts[year] for year in sorted(word_counts.keys())],
            plot_type,
            "Количество слов за каждый год",
            "Год",
            "Количество слов",
            self.file_handler.results_dir / "word_count_plot.png"
        )
        self.file_handler.save_to_excel(
            pd.DataFrame(list(word_counts.items()), columns=["Год", "Количество слов"]),
            self.file_handler.results_dir / "year_word_counts.xlsx"
        )

    def process_file(self, file_path: Path, analyzer, year_dir: Path) -> int:
        text = self.file_handler.read_text_file(file_path)
        lemmas = analyzer.lemmatize(text)
        self.file_handler.save_to_excel(
            pd.DataFrame(lemmas, columns=["Токен", "Лемма"]),
            year_dir / f"{file_path.stem}_lemmatization_results.xlsx"
        )
        return len(lemmas)

    def process_files(self, folder_path: Path, analyzer):
        word_counts_by_year = {}
        max_workers = 8

        for year_folder in folder_path.iterdir():
            if year_folder.is_dir():
                year = year_folder.name
                word_counts_by_year[year] = 0
                year_dir = self.file_handler.results_dir / year
                year_dir.mkdir(exist_ok=True)
                files = list(year_folder.glob("*.txt")) + list(year_folder.glob("*.xml"))
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = [
                        executor.submit(self.process_file, file_path, analyzer, year_dir)
                        for file_path in files
                    ]
                    for future in futures:
                        word_count = future.result()
                        with self.lock:
                            word_counts_by_year[year] += word_count

        return word_counts_by_year