from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from app.utils.file_ops import load_data, save_data
from app.utils.parser import parse_characteristics
from app.templates.edit_template import render_edit_page

router = APIRouter()

@router.get("/edit/{item_id}", response_class=HTMLResponse)
def edit_page(item_id: int):
    data = load_data()
    item = next((x for x in data if x["id_сте"] == item_id), None)

    if not item:
        return HTMLResponse("<h3>СТЕ не найдено</h3>")

    return render_edit_page(item)


@router.post("/edit/{item_id}")
def save_edit(
        item_id: int,
        название_сте: str = Form(...),
        модель: str = Form(...),
        производитель: str = Form(...),
        название_категории: str = Form(...),
        характеристики: str = Form(...),
        ссылка_на_картинку_сте: str = Form(...)
):
    data = load_data()
    item = next((x for x in data if x["id_сте"] == item_id), None)

    if not item:
        return HTMLResponse("<h3>СТЕ не найдено</h3>")

    item.update({
        "название_сте": название_сте,
        "модель": модель,
        "производитель": производитель,
        "название_категории": название_категории,
        "характеристики": характеристики,
        "ссылка_на_картинку_сте": ссылка_на_картинку_сте,
        "_parsed_chars": parse_characteristics(характеристики),
    })

    save_data(data)

    return RedirectResponse(url=f"/edit/{item_id}", status_code=302)
