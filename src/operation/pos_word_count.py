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

class POSWordCountOperation(TextOperation):
    def __init__(self, file_handler: FileHandler, plotter: Plotter):
        self.file_handler = file_handler
        self.plotter = plotter
        self.max_workers = 8
        self.lock = Lock()

    def execute(self,periods: List[Tuple[str, str]], folder_path: Path, analyzer, plot_type: PlotType):
        word_counts_by_year = self.process_files(periods, folder_path, analyzer)
        word_counts = LemmatizationOperation(self.file_handler, self.plotter).process_files(periods, folder_path, analyzer)
        self.save_results(word_counts_by_year, word_counts)
        self.interactive_for_words(word_counts_by_year, word_counts, plot_type)

    def process_file(self, file_path: Path, analyzer) -> dict:
        text = self.file_handler.read_text_file(file_path)
        grammems = analyzer.count_grammems_lemmas(text)
        return grammems

    def process_files(self, periods: List[Tuple[str, str]],  folder_path: Path, analyzer):
        word_counts_by_year = {}
        for start, end in periods:
            period_key = (start, end)
            word_counts_by_year[period_key] = {}
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
                        for grammem, lemma_counts in grammems.items():
                            if grammem not in word_counts_by_year[period_key]:
                                word_counts_by_year[period_key][grammem] = {}
                            for lemma, count in lemma_counts.items():
                                word_counts_by_year[period_key][grammem][lemma] = word_counts_by_year[period_key][grammem].get(lemma, 0) + count
        return word_counts_by_year


    def save_results(self, word_counts_by_year, word_counts):
        all_grammems = set()
        for year in word_counts_by_year:
            all_grammems.update(word_counts_by_year[year].keys())
        for grammem in all_grammems:
            grammem_dir = self.file_handler.results_dir / grammem
            grammem_dir.mkdir(exist_ok=True)
            periods = sorted(word_counts_by_year.keys(), key=lambda x: x[0])
            period_labels = [f"{start}-{end}" if start != end else start for start, end in periods]
            all_lemmas = set()
            for period in periods:
                all_lemmas.update(word_counts_by_year[period].get(grammem, {}).keys())
            data = [
                {
                    "Лемма": lemma,
                    **{
                        period_labels[i]: round(
                            word_counts_by_year[period].get(grammem, {}).get(lemma, 0) / word_counts.get(period, 1) * 1_000_000, 5
                        ) if word_counts.get(period, 1) > 0 else 0.0
                        for i, period in enumerate(periods)
                    }
                }
                for lemma in all_lemmas
            ]
            self.file_handler.save_to_excel(
                pd.DataFrame(data),
                grammem_dir / f"{grammem}_frequencies.xlsx"
            )
            
    def interactive_for_words(self, word_counts_by_year, word_counts, plot_type: PlotType):
        print("Результаты сохранены. Доступен разбор для каждого слова:")
        all_grammems = set()
        for year in word_counts_by_year:
            all_grammems.update(word_counts_by_year[year].keys())
        while True:
            print("\nДоступные части речи:", ", ".join(sorted(all_grammems)))
            grammem = input("Введите часть речи (или 'q' для выхода): ").strip()
            if grammem.lower() == 'q':
                break
            if grammem not in all_grammems:
                print("Ошибка: указанная часть речи не найдена.")
                continue

            available_lemmas = set()
            for period in word_counts_by_year:
                available_lemmas.update(word_counts_by_year[period].get(grammem, {}).keys())
            print(f"Доступные леммы для {grammem} (первые 10):", ", ".join(sorted(available_lemmas)[:10]), "...")
            lemma = input("Введите слово (лемму): ").strip().lower()
            if lemma not in available_lemmas:
                print("Ошибка: указанная лемма не найдена для данной части речи.")
                continue

            periods = sorted(word_counts_by_year.keys(), key=lambda x: x[0])
            period_labels = [f"{start}-{end}" if start != end else start for start, end in periods]
            frequencies = [
                round(word_counts_by_year[period].get(grammem, {}).get(lemma, 0) / word_counts.get(period, 1) * 1_000_000, 5)
                if word_counts.get(period, 1) > 0 else 0.0
                for period in periods
            ]

            output_path = self.file_handler.results_dir / f"{grammem}_{lemma}_frequency_plot.png"
            self.plotter.create_plot(
                period_labels, frequencies, PlotType.LINE,
                f"Частота леммы '{lemma}' ({grammem}) по периодам",
                "Период", "Частота (IPM)",
                output_path
            )
            print(f"График сохранён: {output_path}")