from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from src.api.models import User, UserCreate, UserLogin, UserRead
from src.api.database import get_db, hash_password, verify_password


router = APIRouter(prefix="/auth", tags=["Authentication"])

# PUBLIC_INTERFACE
@router.post("/signup", response_model=UserRead, summary="Register new user", description="Creates a new user account.")
def signup(data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter((User.username == data.username) | (User.email == data.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    u = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password)
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u

# PUBLIC_INTERFACE
@router.post("/login", response_model=UserRead, summary="Login user", description="Login with username and password, sets basic session.")
def login(data: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    response.set_cookie(key="user_id", value=str(user.id), httponly=True)
    return user

# PUBLIC_INTERFACE
@router.post("/logout", summary="Logout", description="Logs out the current session.")
def logout(response: Response):
    response.delete_cookie(key="user_id")
    return {"message": "Logged out."}

# PUBLIC_INTERFACE
@router.get("/session", response_model=UserRead, summary="Session check", description="Get current logged-in user info, if session exists")
def session_check(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not logged in")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Session invalid")
    return user
