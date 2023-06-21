from fastapi import FastAPI
from src.api import carts, pkg_util, catalog, b2b

description = """
Central Coast Cauldrons is the premier ecommerce site for all your alchemical desires.
"""

app = FastAPI(
    title="Central Coast Cauldrons",
    description=description,
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Lucas Pierce",
        "email": "lupierce@calpoly.edu",
    },
)

app.include_router(carts.router)
app.include_router(catalog.router)
app.include_router(pkg_util.router)
app.include_router(b2b.router)


@app.get("/")
async def root():
    return {"message": "Welcome to the Central Coast Cauldrons."}
