def render_search_page(query, results):
    items_html = ""
    for item in results:
        items_html += f"""
        <div style='border:1px solid #aaa; padding:10px; margin:10px 0;'>
            <strong>ID:</strong> {item['id_сте']}<br>
            <strong>Название:</strong> {item['название_сте']}<br>
            <strong>Модель:</strong> {item['модель']}<br>
            <strong>Производитель:</strong> {item['производитель']}<br>
            <a href="/edit/{item['id_сте']}">Редактировать</a>
        </div>
        """

    return f"""
    <h2>Поиск СТЕ</h2>
    <form method="get" action="/search">
        <input type="text" name="q" value="{query}">
        <button type="submit">Поиск</button>
    </form>

    {items_html if items_html else "<p>Ничего не найдено.</p>"}
    <a href="/add">Добавить новую СТЕ</a>
    """
