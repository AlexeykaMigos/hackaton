# app/services/aggregation_service.py
from typing import List, Dict, Any, Tuple
import re
import math

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import StandardScaler

from app.utils.file_ops import load_data
from app.utils.parser import parse_characteristics

# полезные regex
NUM_RE = re.compile(r"[-+]?\d+[.,]?\d*")

def load_all_data() -> List[Dict[str, Any]]:
    return load_data()

def characteristics_to_text(item: Dict[str, Any]) -> str:
    """
    Собирает текстовую строку характеристик для TF-IDF:
    включает поле 'характеристики', ключи и значения _parsed_chars, название/производитель.
    """
    parts = []
    if item.get("название_сте"):
        parts.append(str(item["название_сте"]))
    if item.get("производитель"):
        parts.append(str(item["производитель"]))
    if item.get("модель"):
        parts.append(str(item["модель"]))
    chars = item.get("характеристики", "")
    parts.append(str(chars))
    parsed = item.get("_parsed_chars", {})
    for k, v in parsed.items():
        parts.append(f"{k} {v}")
    return " ; ".join([p for p in parts if p])

def extract_numeric_features(parsed_chars: Dict[str, str]) -> Dict[str, float]:
    """
    Попытка извлечь числовые значения из parsed_chars.
    Возвращает словарь {key: float_value} только для успешно распарсенных чисел.
    """
    nums = {}
    for k, v in parsed_chars.items():
        if not v:
            continue
        m = NUM_RE.search(str(v).replace(",", "."))
        if m:
            try:
                value = float(m.group(0))
                nums[k] = value
            except Exception:
                continue
    return nums

def determine_significant_text_features(texts: List[str], top_k: int = 10) -> List[str]:
    """
    Строит TF-IDF и возвращает top_k наиболее важный токен (feature names).
    """
    vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b", max_df=0.9, min_df=1, ngram_range=(1,2))
    X = vectorizer.fit_transform(texts)
    # суммарная важность каждого терма
    sums = np.asarray(X.sum(axis=0)).ravel()
    terms = np.array(vectorizer.get_feature_names_out())
    top_idx = np.argsort(sums)[::-1][:top_k]
    return terms[top_idx].tolist()

def build_feature_matrix(items: List[Dict[str, Any]], text_features: List[str]) -> Tuple[np.ndarray, List[int], List[str]]:
    """
    Для каждого item строит вектор:
    - бинарные индикаторы наличия текстовых признаков (text_features)
    - нормированные числовые признаки (в колонках numeric_keys)
    Возвращает (matrix, item_ids, feature_names_list)
    """
    item_ids = []
    text_feats = text_features
    numeric_maps = []
    numeric_keys_set = set()
    texts = []

    for it in items:
        item_ids.append(it["id_сте"])
        texts.append(characteristics_to_text(it))
        nums = extract_numeric_features(it.get("_parsed_chars", {}))
        numeric_maps.append(nums)
        numeric_keys_set.update(nums.keys())

    numeric_keys = sorted(list(numeric_keys_set))
    rows = []
    for i, it in enumerate(items):
        row = []
        txt = texts[i].lower()
        # binary text features
        for feat in text_feats:
            row.append(1.0 if feat.lower() in txt else 0.0)
        # numeric features (fill 0 if missing)
        nums = numeric_maps[i]
        for nk in numeric_keys:
            row.append(float(nums.get(nk, 0.0)))
        rows.append(row)

    matrix = np.array(rows, dtype=float) if rows else np.zeros((0, len(text_feats)+len(numeric_keys)))
    feature_names = [f"text__{t}" for t in text_feats] + [f"num__{n}" for n in numeric_keys]
    # Normalize numeric columns (last len(numeric_keys) columns)
    if matrix.size:
        if numeric_keys:
            n_text = len(text_feats)
            scaler = StandardScaler()
            matrix[:, n_text:] = scaler.fit_transform(matrix[:, n_text:])
    return matrix, item_ids, feature_names

def cluster_items(matrix: np.ndarray, n_clusters: int = 5) -> List[int]:
    if matrix.size == 0:
        return []
    # если число объектов меньше кластеров — уменьшаем
    n_objects = matrix.shape[0]
    n_clusters = min(n_clusters, max(1, n_objects))
    model = AgglomerativeClustering(n_clusters=n_clusters)
    labels = model.fit_predict(matrix)
    return labels.tolist()

def aggregate_category(category_id: int, top_k: int = 10, n_clusters: int = 5) -> Dict[str, Any]:
    """
    Основная функция — возвращает агрегаты для указанной категории.
    """
    data = load_all_data()
    # фильтруем по категории
    items = [it for it in data if it.get("id_категории") == category_id]
    if not items:
        return {"category_id": category_id, "n_items": 0, "groups": []}

    # ensure parsed chars
    for it in items:
        if "_parsed_chars" not in it:
            it["_parsed_chars"] = parse_characteristics(it.get("характеристики", ""))

    texts = [characteristics_to_text(it) for it in items]
    text_features = determine_significant_text_features(texts, top_k=top_k)
    matrix, item_ids, feat_names = build_feature_matrix(items, text_features)
    labels = cluster_items(matrix, n_clusters=n_clusters)

    # build groups
    groups = {}
    for idx, lab in enumerate(labels):
        groups.setdefault(int(lab), []).append(items[idx])

    # summarize groups: common text features & numeric ranges
    summary_groups = []
    for lab, group_items in groups.items():
        # compute shared text features
        texts_in_group = [characteristics_to_text(it).lower() for it in group_items]
        common_texts = [f for f in text_features if all(f.lower() in t for t in texts_in_group)]
        # numeric summaries
        numeric_summary = {}
        # collect numeric keys and values
        numeric_vals = {}
        for it in group_items:
            nums = extract_numeric_features(it.get("_parsed_chars", {}))
            for k, v in nums.items():
                numeric_vals.setdefault(k, []).append(v)
        for k, vals in numeric_vals.items():
            numeric_summary[k] = {"min": float(min(vals)), "max": float(max(vals)), "mean": float(sum(vals)/len(vals))}

        summary_groups.append({
            "group_id": lab,
            "n_items": len(group_items),
            "common_text_features": common_texts,
            "numeric_summary": numeric_summary,
            "items": [ {"id_сте": it["id_сте"], "название_сте": it.get("название_сте"), "модель": it.get("модель"), "производитель": it.get("производитель")} for it in group_items ]
        })

    return {
        "category_id": category_id,
        "n_items": len(items),
        "n_requested_clusters": n_clusters,
        "text_features_used": text_features,
        "groups": summary_groups
    }
