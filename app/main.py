from fastapi import FastAPI
from app.routes.search import router as search_router
from app.routes.edit import router as edit_router
from app.routes.add import router as add_router

app = FastAPI(title="СТЕ Поиск")

# Роуты
app.include_router(search_router)
app.include_router(edit_router)
app.include_router(add_router)


