from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from typing import List, Dict, Any
import json
import os

app = FastAPI(title="СТЕ Поиск")

DATA_FILE = "output.json"

def load_data(file_path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл данных не найден: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def parse_characteristics(chars_str: str) -> Dict[str, str]:
    if not chars_str or not isinstance(chars_str, str):
        return {}
    pairs = [pair.strip() for pair in chars_str.split(";") if pair.strip()]
    result = {}
    for pair in pairs:
        if ":" in pair:
            key, value = pair.split(":", 1)
            result[key.strip()] = value.strip()
    return result

try:
    raw_data = load_data(DATA_FILE)
    for item in raw_data:
        item["_parsed_chars"] = parse_characteristics(item.get("характеристики", ""))
except Exception as e:
    raw_data = []
    print(f"Ошибка загрузки данных: {e}")

def search_stes(query: str) -> List[Dict[str, Any]]:
    if not query.strip():
        return []
    query_lower = query.lower()
    results = []
    for item in raw_data:
        for field in ["название_сте", "модель", "производитель", "название_категории"]:
            if item.get(field) and query_lower in str(item[field]).lower():
                results.append(item)
                break
        else:
            for key, value in item.get("_parsed_chars", {}).items():
                if query_lower in key.lower() or query_lower in value.lower():
                    results.append(item)
                    break
    return results

def render_results_html(query: str, results: List[Dict]) -> str:
    items_html = ""
    for item in results:
        clean_item = {k: v for k, v in item.items() if k != "_parsed_chars"}
        items_html += f"""
        <div style="border:1px solid #ccc; padding:10px; margin:10px 0;">
            <strong>ID:</strong> {clean_item.get('id_сте', '')}<br>
            <strong>Название:</strong> {clean_item.get('название_сте', '')}<br>
            <strong>Модель:</strong> {clean_item.get('модель', '')}<br>
            <strong>Производитель:</strong> {clean_item.get('производитель', '')}<br>
            <strong>Категория:</strong> {clean_item.get('название_категории', '')}<br>
            <strong>Характеристики:</strong><br>
            <pre style="background:#f9f9f9; padding:5px; overflow:auto;">{clean_item.get('характеристики', '')}</pre>
            <img src="{clean_item.get('ссылка_на_картинку_сте', '')}" alt="Изображение" style="max-width:100px; max-height:100px; margin-top:5px;">
        </div>
        """
    count = len(results)
    return f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Поиск СТЕ</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; }}
            input[type="text"] {{ width: 300px; padding: 8px; }}
            button {{ padding: 8px 16px; }}
        </style>
    </head>
    <body>
        <h2>Поиск СТЕ</h2>
        <form method="get" action="/search">
            <input type="text" name="q" value="{query}" placeholder="Введите запрос..." required>
            <button type="submit">Найти</button>
        </form>
        <hr>
        <h3>Найдено: {count} результатов</h3>
        {items_html if items_html else "<p>Ничего не найдено.</p>"}
        <br>
    </body>
    </html>
    """

@app.get("/search", response_class=HTMLResponse)
def search_page(request: Request, q: str = ""):
    if q:
        results = search_stes(q)
    else:
        results = []
    return HTMLResponse(content=render_results_html(q, results))

from fastapi import Form
from fastapi.responses import RedirectResponse

def save_data():
    """Сохранение данных в output.json"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(raw_data, f, ensure_ascii=False, indent=4)



@app.get("/edit/{item_id}", response_class=HTMLResponse)
def edit_page(item_id: int):
    item = next((x for x in raw_data if x["id_сте"] == item_id), None)
    if not item:
        return HTMLResponse("<h3>СТЕ не найден</h3>")

    return f"""
    <h2>Редактирование СТЕ #{item_id}</h2>
    <form method="post">
        Название: <input name="название_сте" value="{item['название_сте']}"><br><br>
        Модель: <input name="модель" value="{item['модель']}"><br><br>
        Производитель: <input name="производитель" value="{item['производитель']}"><br><br>
        Категория: <input name="название_категории" value="{item['название_категории']}"><br><br>

        Характеристики:<br>
        <textarea name="характеристики" rows="6" cols="60">{item['характеристики']}</textarea><br><br>

        Ссылка на картинку:<br>
        <input name="ссылка_на_картинку_сте" value="{item['ссылка_на_картинку_сте']}"><br><br>

        <button type="submit">Сохранить</button>
    </form>
    """


@app.post("/edit/{item_id}")
def save_edit(
        item_id: int,
        название_сте: str = Form(...),
        модель: str = Form(...),
        производитель: str = Form(...),
        название_категории: str = Form(...),
        характеристики: str = Form(...),
        ссылка_на_картинку_сте: str = Form(...)
):
    item = next((x for x in raw_data if x["id_сте"] == item_id), None)
    if not item:
        return HTMLResponse("<h3>СТЕ не найден</h3>")

    item.update({
        "название_сте": название_сте,
        "модель": модель,
        "производитель": производитель,
        "название_категории": название_категории,
        "характеристики": характеристики,
        "ссылка_на_картинку_сте": ссылка_на_картинку_сте,
        "_parsed_chars": parse_characteristics(характеристики)
    })

    save_data()
    return RedirectResponse(url=f"/edit/{item_id}", status_code=302)
                  

@app.get("/delete/{item_id}")
def delete_item(item_id: int):
    global raw_data
    raw_data = [x for x in raw_data if x["id_сте"] != item_id]
    save_data()
    return RedirectResponse(url="/search?q=", status_code=302)


@app.get("/add", response_class=HTMLResponse)
def add_page():
    return """
    <h2>Добавление новой СТЕ</h2>
    <form method="post">
        Название: <input name="название_сте"><br><br>
        Модель: <input name="модель"><br><br>
        Производитель: <input name="производитель"><br><br>
        Категория: <input name="название_категории"><br><br>

        Характеристики:<br>
        <textarea name="характеристики" rows="6" cols="60"></textarea><br><br>

        Ссылка на картинку:<br>
        <input name="ссылка_на_картинку_сте"><br><br>

        <button type="submit">Добавить</button>
    </form>
    """


@app.post("/add")
def add_item(
        название_сте: str = Form(...),
        модель: str = Form(...),
        производитель: str = Form(...),
        название_категории: str = Form(...),
        характеристики: str = Form(...),
        ссылка_на_картинку_сте: str = Form(...)
):
    new_id = max([x["id_сте"] for x in raw_data]) + 1 if raw_data else 1

    new_item = {
        "id_сте": new_id,
        "название_сте": название_сте,
        "модель": модель,
        "производитель": производитель,
        "название_категории": название_категории,
        "характеристики": характеристики,
        "ссылка_на_картинку_сте": ссылка_на_картинку_сте,
        "_parsed_chars": parse_characteristics(характеристики)
    }

    raw_data.append(new_item)
    save_data()

    return RedirectResponse(url=f"/edit/{new_id}", status_code=302)
