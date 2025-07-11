from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.api.models import LeaderboardEntry, LeaderboardResponse, Leaderboard, User
from src.api.database import get_db

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])

# PUBLIC_INTERFACE
@router.get("/", response_model=LeaderboardResponse, summary="Get leaderboard", description="Get leaderboard top players by wins")
def get_leaderboard(db: Session = Depends(get_db)):
    entries = (
        db.query(Leaderboard, User)
        .join(User, Leaderboard.user_id == User.id)
        .order_by(Leaderboard.wins.desc())
        .limit(20)
        .all()
    )
    leaderboard = [
        LeaderboardEntry(
            username=u.username,
            wins=l.wins,
            losses=l.losses,
            draws=l.draws,
        ) for (l,u) in entries
    ]
    return LeaderboardResponse(leaderboard=leaderboard)
