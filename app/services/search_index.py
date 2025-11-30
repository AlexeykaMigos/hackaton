# app/services/search_index.py
from typing import Dict, List, Set
import re

from app.utils.file_ops import load_data
from app.utils.parser import parse_characteristics

WORD_RE = re.compile(r"[a-zA-Zа-яА-Я0-9]+")


def tokenize(text: str) -> List[str]:
    """Нормализованная токенизация текста: только буквы/цифры, lower."""
    if not text:
        return []
    return [t.lower() for t in WORD_RE.findall(text)]


class SearchIndex:
    def __init__(self):
        self.index: Dict[str, Set[int]] = {}
        self.data = load_data()
        self._prepare_items()
        self._build_index()

    def _prepare_items(self):
        for it in self.data:
            if "_parsed_chars" not in it:
                it["_parsed_chars"] = parse_characteristics(it.get("характеристики", ""))

    def _build_index(self):
        """
        Строит токен → множество id_сте по всем текстовым полям.
        """
        for it in self.data:
            item_id = it["id_сте"]

            fields = []
            fields.append(it.get("название_сте", ""))
            fields.append(it.get("производитель", ""))
            fields.append(it.get("модель", ""))
            fields.append(it.get("название_категории", ""))
            fields.append(it.get("характеристики", ""))

            # include parsed_chars (ключи и значения)
            for k, v in it["_parsed_chars"].items():
                fields.append(k)
                fields.append(v)

            # Join text and tokenize
            tokens = []
            for f in fields:
                tokens.extend(tokenize(str(f)))

            # Update index
            for tok in tokens:
                if tok not in self.index:
                    self.index[tok] = set()
                self.index[tok].add(item_id)

    def search(self, query: str) -> List[dict]:
        """
        Выполняет быстрый поиск по токенам:
        1) токены запроса → пересечение id (логика AND)
        2) возвращает список объектов
        """
        q_tokens = tokenize(query)
        if not q_tokens:
            return []

        # Если один токен → просто вернуть множество
        if len(q_tokens) == 1:
            tok = q_tokens[0]
            ids = self.index.get(tok, set())
        else:
            # Логика AND: пересечение результатов для всех токенов
            sets = []
            for tok in q_tokens:
                sets.append(self.index.get(tok, set()))
            ids = set.intersection(*sets) if sets else set()

        # Выбрать объекты по id
        id_map = {it["id_сте"]: it for it in self.data}
        return [id_map[i] for i in ids]


# Singleton index
search_index = SearchIndex()
