from fastapi import FastAPI, exceptions
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from src.api import carts, catalog, bottler, barrels, admin, info, inventory
import json
import logging
import sys
from starlette.middleware.cors import CORSMiddleware

description = """
Central Coast Cauldrons is the premier ecommerce site for all your alchemical desires.
"""
tags_metadata = [
    {
        "name": "cart",
        "description": "Endpoints related to retrieving and updating time-related information.",
    },
    # You can add more tags here
]

app = FastAPI(
    title="Central Coast Cauldrons",
    description=description,
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Lucas Pierce",
        "email": "lupierce@calpoly.edu",
    },
    openapi_tags=tags_metadata
)

origins = ["https://potion-exchange.vercel.app"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(inventory.router)
app.include_router(carts.router)
app.include_router(catalog.router)
app.include_router(bottler.router)
app.include_router(barrels.router)
app.include_router(admin.router)
app.include_router(info.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Central Coast Cauldrons."}
