from .util.file_handler import FileHandler
from .util.plotter import Plotter
from .model.enums import PlotType
from .operation.lemmatization import LemmatizationOperation
from .operation.pos_count import POSCountOperation
from .operation.pos_word_count import POSWordCountOperation
from .operation.adjective_analysis import AdjectiveAnalysisOperation
from .analyzer.pymorphy2_analyzer import Pymorphy2Analyzer
from .analyzer.pymystem3_analyzer import Pymystem3Analyzer
from .analyzer.adjective_analyzer.open_corpora_analyzer import OpenCorporaAdjectiveAnalyzer
from .analyzer.adjective_analyzer.wiktionary_analyzer import WiktionaryAdjectiveAnalyzer
from pathlib import Path
from typing import List, Tuple
import os

class TextAnalyzerApp:
    def __init__(self):
        self.file_handler = FileHandler()
        self.plotter = Plotter()

    def select_operation(self):
        print("Доступные функции:")
        print("1. Лемматизация и подсчет слов")
        print("2. Доля частей речи")
        print("3. Частота слов по частям речи")
        print("4. Доля качественных и относительных прилагательных")
        choice = input("Выберите номер функции: ").strip()
        if choice == "1":
            return LemmatizationOperation(self.file_handler, self.plotter)
        elif choice == "2":
            return POSCountOperation(self.file_handler, self.plotter)
        elif choice == "3":
            return POSWordCountOperation(self.file_handler, self.plotter)
        elif choice == "4":
            adjective_analyzer = self.select_adjective_analyzer()
            return AdjectiveAnalysisOperation(self.file_handler, self.plotter, adjective_analyzer)
        else:
            raise ValueError("Invalid operation choice")

    def select_analyzer(self):
        print("\nДоступные морфологические анализаторы:")
        print("1. pymorphy2")
        print("2. pymystem3")
        choice = input("Выберите номер анализатора: ").strip()
        if choice == "1":
            return Pymorphy2Analyzer()
        elif choice == "2":
            return Pymystem3Analyzer()
        else:
            raise ValueError("Invalid analyzer choice")

    def select_adjective_analyzer(self):
        print("\nДоступные словари для анализа:")
        print("1. OpenCorpora")
        print("2. ВикиСловарь")
        choice = input("Выберите номер словаря: ").strip()
        if choice == "1":
            return OpenCorporaAdjectiveAnalyzer()
        elif choice == "2":
            return WiktionaryAdjectiveAnalyzer()
        else:
            raise ValueError("Invalid adjective analyzer choice")

    def get_folder_path(self):
        folder_path = input("\nВведите полный путь к папке: ").strip()
        if not os.path.isdir(folder_path):
            raise ValueError("Invalid folder path")
        return Path(folder_path)
    
    def get_available_years(self, folder_path: Path) -> List[str]:
        years = []
        for year_folder in folder_path.iterdir():
            if year_folder.is_dir() and year_folder.name.isdigit():
                years.append(year_folder.name)
        return sorted(years)

    def select_periods(self, years: List[str]) -> List[Tuple[str, str]]:
        print("\nВыберите режим обработки:")
        print("1. По отдельным годам")
        print("2. По периодам")
        choice = input("Выберите номер режима: ").strip()
        if choice == "1":
            return [(year, year) for year in years]
        elif choice == "2":
            max_periods = len(years)
            while True:
                try:
                    num_periods = int(input(f"Введите количество периодов (1–{max_periods}): ").strip())
                    if 1 <= num_periods <= max_periods:
                        break
                    print(f"Ошибка: количество периодов должно быть от 1 до {max_periods}.")
                except ValueError:
                    print("Ошибка: введите целое число.")
            periods = []
            used_years = set()
            print(f"Доступные годы: {', '.join(years)}")
            for i in range(num_periods):
                while True:
                    try:
                        start = input(f"Введите начальный год для периода {i+1}: ").strip()
                        if start not in years or start in used_years:
                            print("Ошибка: год недоступен или уже использован.")
                            continue
                        end = input(f"Введите конечный год для периода {i+1}: ").strip()
                        if end not in years or end in used_years:
                            print("Ошибка: год недоступен или уже использован.")
                            continue
                        if int(end) < int(start):
                            print("Ошибка: конечный год не может быть раньше начального.")
                            continue
                        period_years = [y for y in years if int(start) <= int(y) <= int(end)]
                        if not all(y not in used_years for y in period_years):
                            print("Ошибка: некоторые годы в диапазоне уже использованы.")
                            continue
                        periods.append((start, end))
                        used_years.update(period_years)
                        break
                    except Exception as e:
                        print(f"Ошибка: {e}")
            return periods
        else:
            raise ValueError("Invalid period choice")


    def select_plot_type(self):
        print("\nДоступные типы графиков:")
        print("1. Бар-график")
        print("2. Линейный график")
        choice = input("Выберите номер типа графика: ").strip()
        if choice == "1":
            return PlotType.BAR
        elif choice == "2":
            return PlotType.LINE
        else:
            raise ValueError("Invalid plot type")

    def run(self):
        try:
            operation = self.select_operation()
            analyzer = self.select_analyzer()
            plot_type = self.select_plot_type()
            folder_path = self.get_folder_path()
            years = self.get_available_years(folder_path)
            if not years:
                raise ValueError("No valid year folders found in the provided directory.")
            periods = self.select_periods(years)
            operation.execute(periods, folder_path, analyzer, plot_type)
            print("Обработка завершена.")
        except Exception as e:
            print(f"Ошибка: {e}")