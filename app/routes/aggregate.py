from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from app.services.aggregation_service import aggregate_category

router = APIRouter()


@router.get("/aggregate", response_class=JSONResponse)
def aggregate_route(category_id: int = Query(..., description="id_категории"),
                    top_k: int = Query(10, ge=1, le=200),
                    n_clusters: int = Query(5, ge=1, le=50)):
    result = aggregate_category(category_id=int(category_id), top_k=int(top_k), n_clusters=int(n_clusters))
    return JSONResponse(content=result)
