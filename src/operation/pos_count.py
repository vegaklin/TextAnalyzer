from ..interface.text_operation import TextOperation
from ..util.file_handler import FileHandler
from ..util.plotter import Plotter
from ..model.enums import PlotType
from .lemmatization import LemmatizationOperation
from pathlib import Path
import pandas as pd

class POSCountOperation(TextOperation):
    def __init__(self, file_handler: FileHandler, plotter: Plotter):
        self.file_handler = file_handler
        self.plotter = plotter

    def execute(self, folder_path: Path, analyzer, plot_type: PlotType):
        pos_counts_by_year = self.process_files(folder_path, analyzer)
        word_counts = LemmatizationOperation(self.file_handler, self.plotter).process_files(folder_path, analyzer)
        self.save_results(pos_counts_by_year, word_counts, plot_type)
        return pos_counts_by_year

    def process_files(self, folder_path: Path, analyzer):
        pos_counts_by_year = {}
        for year_folder in folder_path.iterdir():
            if year_folder.is_dir():
                year = year_folder.name
                pos_counts_by_year[year] = {}
                for file_path in list(year_folder.glob("*.txt")) + list(year_folder.glob("*.xml")):
                    text = self.file_handler.read_text_file(file_path)
                    grammems = analyzer.count_grammems(text)
                    for grammem, count in grammems.items():
                        pos_counts_by_year[year][grammem] = pos_counts_by_year[year].get(grammem, 0) + count
        return pos_counts_by_year

    def save_results(self, pos_counts_by_year, word_counts, plot_type: PlotType):
        all_grammems = set()
        for year in pos_counts_by_year:
            all_grammems.update(pos_counts_by_year[year].keys())
        for grammem in all_grammems:
            years = sorted(pos_counts_by_year.keys())
            counts = [pos_counts_by_year[year].get(grammem, 0) for year in years]
            frequencies = [
                round((count / word_counts.get(year, 1)) * 100, 5) if word_counts.get(year, 1) > 0 else 0.0
                for year, count in zip(years, counts)
            ]
            df = pd.DataFrame({
                "Год": years,
                f"Количество {grammem}": counts,
                f"Процент {grammem}": frequencies
            })
            self.file_handler.save_to_excel(df, self.file_handler.results_dir / f"{grammem}_counts.xlsx")
            self.plotter.create_plot(
                years, frequencies, plot_type,
                f"Процент слов для {grammem}", "Год", "Процент",
                self.file_handler.results_dir / f"{grammem}_plot.png"
            )