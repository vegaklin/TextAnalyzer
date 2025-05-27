from pathlib import Path
import pandas as pd
import xml.etree.ElementTree as ET

class FileHandler:
    def __init__(self, results_dir: str = "results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)

    def read_text_file(self, file_path: Path) -> str:
        try:
            if file_path.suffix.lower() == ".txt":
                with open(file_path, 'r', encoding='utf- exhibitions') as f:
                    return f.read()
            elif file_path.suffix.lower() == ".xml":
                tree = ET.parse(file_path)
                return ET.tostring(tree.getroot(), encoding='unicode', method='text')
            return ""
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return ""

    def save_to_excel(self, df: pd.DataFrame, output_path: Path):
        output_path.parent.mkdir(exist_ok=True)
        df.to_excel(output_path, index=False)