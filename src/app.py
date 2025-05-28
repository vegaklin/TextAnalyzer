from .util.file_handler import FileHandler
from .util.plotter import Plotter
from .model.enums import AnalyzerChoice, AdjectiveAnalyzerChoice, PlotType
from .operation.lemmatization import LemmatizationOperation
from .operation.pos_count import POSCountOperation
from .operation.pos_word_count import POSWordCountOperation
from .operation.adjective_analysis import AdjectiveAnalysisOperation
from .analyzer.pymorphy2_analyzer import Pymorphy2Analyzer
from .analyzer.pymystem3_analyzer import Pymystem3Analyzer
from .analyzer.adjective_analyzer.open_corpora_analyzer import OpenCorporaAdjectiveAnalyzer
from .analyzer.adjective_analyzer.wiktionary_analyzer import WiktionaryAdjectiveAnalyzer
from pathlib import Path
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
        print("Доступные морфологические анализаторы:")
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
        print("Доступные словари для анализа:")
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
        folder_path = input("Введите полный путь к папке: ").strip()
        if not os.path.isdir(folder_path):
            raise ValueError("Invalid folder path")
        return Path(folder_path)

    def select_plot_type(self):
        print("Доступные типы графиков:")
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
            operation.execute(folder_path, analyzer, plot_type)
            print("Обработка завершена.")
        except Exception as e:
            print(f"Ошибка: {e}")