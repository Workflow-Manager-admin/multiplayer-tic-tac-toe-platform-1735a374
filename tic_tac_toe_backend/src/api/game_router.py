from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from src.api.models import (
    Game, GameCreate, GameJoin, GameLeave, Move, MoveCreate, MoveRead,
    GameRead, User, UserRead, GameStatus, UserGame
)
from src.api.database import get_db

router = APIRouter(prefix="/games", tags=["Games"])

def get_current_user(request: Request, db: Session):
    user_id = request.cookies.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    return user

# PUBLIC_INTERFACE
@router.post("/create", response_model=GameRead, summary="Create new game", description="Create a new Tic Tac Toe game.")
def create_game(_: GameCreate, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    game = Game(status=GameStatus.waiting)
    db.add(game)
    db.commit()
    db.refresh(game)
    # Add creator as first player
    db.add(UserGame(user_id=user.id, game_id=game.id))
    db.commit()
    db.refresh(game)
    players = [user]
    return _to_game_read(game, db, players=players)

# PUBLIC_INTERFACE
@router.post("/join", response_model=GameRead, summary="Join a game", description="Join a waiting game as player 2.")
def join_game(body: GameJoin, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    game = db.query(Game).filter(Game.id == body.game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    # Only allow one more player
    player_ids = [ug.user_id for ug in db.query(UserGame).filter(UserGame.game_id == game.id)]
    if len(player_ids) >= 2:
        raise HTTPException(status_code=400, detail="Game already full")
    # Add to UserGame
    if user.id in player_ids:
        raise HTTPException(status_code=400, detail="You are already in this game")
    db.add(UserGame(user_id=user.id, game_id=game.id))
    game.status = GameStatus.in_progress
    if game.current_player_id is None:
        game.current_player_id = player_ids[0]  # first joined starts
    db.commit()
    db.refresh(game)
    players = db.query(User).filter(User.id.in_(player_ids + [user.id])).all()
    return _to_game_read(game, db, players=players)

# PUBLIC_INTERFACE
@router.post("/leave", summary="Leave a game", description="Leave a game you're in.")
def leave_game(body: GameLeave, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    ug = db.query(UserGame).filter(UserGame.game_id == body.game_id, UserGame.user_id == user.id).first()
    if not ug:
        raise HTTPException(status_code=404, detail="User not in game")
    db.delete(ug)
    db.commit()
    return {"left": True}

# PUBLIC_INTERFACE
@router.post("/play", response_model=GameRead, summary="Make a move", description="Play a move in a game.")
def play_move(body: MoveCreate, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    game = db.query(Game).filter(Game.id == body.game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    # Ensure user is a player in the game
    player_ids = [ug.user_id for ug in db.query(UserGame).filter(UserGame.game_id == game.id)]
    if user.id not in player_ids:
        raise HTTPException(status_code=403, detail="Not a player of this game")
    moves = db.query(Move).filter(Move.game_id == game.id).order_by(Move.created_at).all()
    # Whose turn is it?
    symbol = "X" if player_ids[0] == user.id else "O"
    # Ensure turn
    x_count = sum(m.symbol == "X" for m in moves)
    o_count = sum(m.symbol == "O" for m in moves)
    if (symbol == "X" and x_count > o_count) or (symbol == "O" and o_count >= x_count):
        raise HTTPException(status_code=400, detail="Not your turn")
    if body.position < 0 or body.position > 8:
        raise HTTPException(status_code=400, detail="Position out of bounds")
    board = list(game.board_state)
    if board[body.position] != "_":
        raise HTTPException(status_code=400, detail="Position already taken")
    board[body.position] = symbol
    mv = Move(user_id=user.id, game_id=game.id, position=body.position, symbol=symbol)
    db.add(mv)
    game.board_state = "".join(board)
    # Check for win or draw (basic logic):
    winner = _find_winner(board)
    if winner:
        game.status = GameStatus.finished
        game.winner_id = user.id
    elif "_" not in board:
        game.status = GameStatus.finished
        game.winner_id = None
    else:
        game.turn += 1
        # Switch current_player_id
        other_player_id = next(pid for pid in player_ids if pid != user.id)
        game.current_player_id = other_player_id
    db.commit()
    db.refresh(game)
    return _to_game_read(game, db)

# PUBLIC_INTERFACE
@router.get("/{game_id}", response_model=GameRead, summary="Get game state", description="Retrieve the current state of a game.")
def get_game(game_id: int, db: Session = Depends(get_db)):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return _to_game_read(game, db)

def _find_winner(board):
    """Return symbol ("X" or "O") if someone wins, else None."""
    wins = [
        [0,1,2],[3,4,5],[6,7,8], # Rows
        [0,3,6],[1,4,7],[2,5,8], # Cols
        [0,4,8],[2,4,6]
    ]
    for a,b,c in wins:
        if board[a] == board[b] == board[c] and board[a] in ("X","O"):
            return board[a]
    return None

def _to_game_read(game, db, players=None):
    # Compose game info as per GameRead schema
    if not players:
        player_ids = [ug.user_id for ug in db.query(UserGame).filter(UserGame.game_id == game.id)]
        players = db.query(User).filter(User.id.in_(player_ids)).all()
    moves = db.query(Move).filter(Move.game_id == game.id).order_by(Move.created_at).all()
    return GameRead(
        id=game.id,
        created_at=game.created_at,
        status=game.status,
        turn=game.turn,
        current_player_id=game.current_player_id,
        winner_id=game.winner_id,
        board_state=game.board_state,
        players=[UserRead.from_orm(u) for u in players],
        moves=[MoveRead.from_orm(m) for m in moves],
    )
