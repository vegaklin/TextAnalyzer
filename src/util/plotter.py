import matplotlib.pyplot as plt
from pathlib import Path
from ..model.enums import PlotType

class Plotter:
    def create_plot(self, years, values, plot_type: PlotType, title: str, xlabel: str, ylabel: str, output_path: Path):
        plt.figure(figsize=(10, 6))
        if plot_type == PlotType.BAR:
            plt.bar(years, values)
        elif plot_type == PlotType.LINE:
            plt.plot(years, values, marker='o')
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.grid(True)
        output_path.parent.mkdir(exist_ok=True)
        plt.savefig(output_path)
        plt.close()