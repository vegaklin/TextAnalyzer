from ...interface.adjective_analyzer import AdjectiveAnalyzer
import pymorphy2
import requests
from bs4 import BeautifulSoup

class WiktionaryAdjectiveAnalyzer(AdjectiveAnalyzer):
    def __init__(self):
        self.morph = pymorphy2.MorphAnalyzer()

    def get_qualitative_or_relative(self, lemma: str) -> str:
        try:
            url = f"https://ru.wiktionary.org/wiki/{lemma}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            content = soup.find('div', class_='mw-parser-output')
            if not content:
                return "неизвестно"
            text = content.get_text().lower()
            if 'качественное' in text:
                return "качественное"
            elif 'относительное' in text:
                return "относительное"
            else:
                parsed = self.morph.parse(lemma)[0]
                return "качественное" if 'Qual' in parsed.tag else "относительное"
        except Exception as e:
            print(f"Error fetching Wiktionary for {lemma}: {e}")
            return "неизвестно"