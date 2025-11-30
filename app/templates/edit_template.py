def render_edit_page(item):
    return f"""
    <h2>Редактирование СТЕ #{item['id_сте']}</h2>

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
