from fastapi import FastAPI

from app.api.routes.nodes import router as nodes_router
from app.api.routes.edges import router as edges_router
from app.api.routes.routes import router as routes_router
app = FastAPI(
    title="Network Route Optimization API",
    version="1.0.0",
)


app.include_router(nodes_router)
app.include_router(edges_router)
app.include_router(routes_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}