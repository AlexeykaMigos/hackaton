from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from app.utils.file_ops import load_data, save_data
from app.utils.parser import parse_characteristics
from app.templates.add_template import render_add_page

router = APIRouter()

@router.get("/add", response_class=HTMLResponse)
def add_page():
    return render_add_page()


@router.post("/add")
def add_item(
        название_сте: str = Form(...),
        модель: str = Form(...),
        производитель: str = Form(...),
        название_категории: str = Form(...),
        характеристики: str = Form(...),
        ссылка_на_картинку_сте: str = Form(...)
):
    data = load_data()

    new_id = max([x["id_сте"] for x in data]) + 1 if data else 1

    new_item = {
        "id_сте": new_id,
        "название_сте": название_сте,
        "модель": модель,
        "производитель": производитель,
        "название_категории": название_категории,
        "характеристики": характеристики,
        "ссылка_на_картинку_сте": ссылка_на_картинку_сте,
        "_parsed_chars": parse_characteristics(характеристики),
    }

    data.append(new_item)
    save_data(data)

    return RedirectResponse(url=f"/edit/{new_id}", status_code=302)
