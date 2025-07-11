from datetime import datetime
from enum import Enum
from sqlalchemy import (Column, Integer, String, DateTime, ForeignKey, Enum as SAEnum)
from sqlalchemy.orm import declarative_base, relationship
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

Base = declarative_base()

# SQLAlchemy Models

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    games = relationship("Game", secondary="user_games", back_populates="players")
    moves = relationship("Move", back_populates="user")

class GameStatus(str, Enum):
    waiting = "waiting"
    in_progress = "in_progress"
    finished = "finished"

class Game(Base):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(SAEnum(GameStatus), default=GameStatus.waiting)
    turn = Column(Integer, default=1)
    current_player_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    winner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    board_state = Column(String, default="_________") # 9 chars for tictactoe board

    players = relationship("User", secondary="user_games", back_populates="games")
    moves = relationship("Move", back_populates="game")

class UserGame(Base):
    __tablename__ = "user_games"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    game_id = Column(Integer, ForeignKey("games.id"), primary_key=True)

class Move(Base):
    __tablename__ = "moves"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    game_id = Column(Integer, ForeignKey("games.id"))
    position = Column(Integer) # 0-8
    symbol = Column(String) # "X" or "O"
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="moves")
    game = relationship("Game", back_populates="moves")

class Leaderboard(Base):
    __tablename__ = "leaderboard"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    draws = Column(Integer, default=0)

# Pydantic Schemas

class UserCreate(BaseModel):
    # PUBLIC_INTERFACE
    """Schema for creating a user account."""
    username: str = Field(..., description="Unique username for the user.")
    email: EmailStr = Field(..., description="Email address of the user.")
    password: str = Field(..., description="Password for the user account.")

class UserLogin(BaseModel):
    # PUBLIC_INTERFACE
    """Schema for user login."""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")

class UserRead(BaseModel):
    # PUBLIC_INTERFACE
    """Schema for reading user info (returned to client)."""
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True

class GameCreate(BaseModel):
    # PUBLIC_INTERFACE
    """Schema for creating a new game."""
    pass  # No input needed, just create

class GameJoin(BaseModel):
    # PUBLIC_INTERFACE
    """Schema for joining a game."""
    game_id: int

class GameLeave(BaseModel):
    # PUBLIC_INTERFACE
    """Schema for leaving a game."""
    game_id: int

class MoveCreate(BaseModel):
    # PUBLIC_INTERFACE
    """Schema for making a move."""
    game_id: int
    position: int # 0-8

class MoveRead(BaseModel):
    # PUBLIC_INTERFACE
    """Schema for displaying a move."""
    user_id: int
    position: int
    symbol: str
    created_at: datetime

    class Config:
        orm_mode = True

class GameStatusEnum(str, Enum):
    waiting = "waiting"
    in_progress = "in_progress"
    finished = "finished"

class GameRead(BaseModel):
    # PUBLIC_INTERFACE
    """Schema for displaying game info."""
    id: int
    created_at: datetime
    status: GameStatusEnum
    turn: int
    current_player_id: Optional[int]
    winner_id: Optional[int]
    board_state: str
    players: List[UserRead]
    moves: List[MoveRead] = []

    class Config:
        orm_mode = True

class LeaderboardEntry(BaseModel):
    # PUBLIC_INTERFACE
    """Schema for leaderboard entry."""
    username: str
    wins: int
    losses: int
    draws: int

class LeaderboardResponse(BaseModel):
    # PUBLIC_INTERFACE
    """Schema for leaderboard response."""
    leaderboard: List[LeaderboardEntry]

