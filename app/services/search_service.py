from app.utils.parser import parse_characteristics
from app.utils.file_ops import load_data

data = load_data()

# Предобработка
for item in data:
    item["_parsed_chars"] = parse_characteristics(item.get("характеристики", ""))


def search_stes(query: str):
    if not query.strip():
        return []

    query = query.lower()
    results = []

    for item in data:
        # По основным полям
        for field in ["название_сте", "модель", "производитель", "название_категории"]:
            if query in str(item.get(field, "")).lower():
                results.append(item)
                break
        else:
            # По характеристикам
            for key, val in item["_parsed_chars"].items():
                if query in key.lower() or query in val.lower():
                    results.append(item)
                    break

    return results


def get_all_data():
    return data
