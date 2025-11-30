def render_add_page():
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
