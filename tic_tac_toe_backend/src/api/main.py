from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.auth_router import router as auth_router
from src.api.game_router import router as game_router
from src.api.leaderboard_router import router as leaderboard_router
from src.api.models import Base as ModelsBase
from src.api.database import engine

app = FastAPI(
    title="Tic Tac Toe API",
    description="Multiplayer Tic Tac Toe backend. Features: user & session mgmt, game actions, leaderboard.",
    version="1.0.0",
    openapi_tags=[
        {"name":"Authentication","description":"User signup, login, logout, session."},
        {"name":"Games","description":"Game creation, join, play, state."},
        {"name":"Leaderboard","description":"Leaderboard for top players."}
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(game_router)
app.include_router(leaderboard_router)

@app.on_event("startup")
def startup():
    # Ensure DB tables exist at startup (all persistent models mapped to SQLite)
    ModelsBase.metadata.create_all(bind=engine)

@app.get("/", summary="Health Check")
def health_check():
    """Check API status."""
    return {"message": "Healthy"}
