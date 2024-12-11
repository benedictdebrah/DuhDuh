from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from jose import JWTError, jwt

from app.database.database import SessionLocal, Post, User
from app.core.config import settings
from app.core.security import create_access_token
from app.core.hashing import Hasher
from app.model import PostSchema, UserSchema, Token

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    docs_url="/",
)

# Utility function to get the current user
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    return user

# Routes
@app.get("/", tags=["Homepage"])
async def read_root() -> dict:
    return {"message": "Welcome to your blog!"}

@app.post("/posts", tags=["Posts"])
async def create_post(post: PostSchema, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    new_post = Post(title=post.title, content=post.content, user_id=current_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"data": new_post.__dict__}

@app.get("/posts", tags=["Posts"])
async def get_posts(db: Session = Depends(get_db)) -> dict:
    posts = db.query(Post).all()
    return {"data": [post.__dict__ for post in posts]}

@app.get("/posts/{id}", tags=["Posts"])
async def get_single_post(id: int, db: Session = Depends(get_db)) -> dict:
    post = db.query(Post).filter(Post.id == id).first()
    if not post:
        raise HTTPException(status_code=404, detail="No such post with the supplied ID.")
    return {"data": post.__dict__}

@app.put("/posts/{id}", tags=["Posts"])
async def update_post(id: int, post: PostSchema, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    post_to_update = db.query(Post).filter(Post.id == id, Post.user_id == current_user.id).first()
    if not post_to_update:
        raise HTTPException(status_code=404, detail="No such post with the supplied ID.")
    for key, value in post.dict().items():
        setattr(post_to_update, key, value)
    db.commit()
    updated_post = {column.name: getattr(post_to_update, column.name) for column in Post.__table__.columns}
    return {"data": updated_post}

@app.delete("/posts/{id}", tags=["Posts"])
async def delete_post(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    post_to_delete = db.query(Post).filter(Post.id == id, Post.user_id == current_user.id).first()
    if not post_to_delete:
        raise HTTPException(status_code=404, detail="No such post with the supplied ID.")
    db.delete(post_to_delete)
    db.commit()
    return {"data": "Post deleted successfully."}

# User Registration Endpoint
@app.post("/user/signup", tags=["User"])
async def signup(user: UserSchema, db: Session = Depends(get_db)) -> dict:
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already registered.")
    hashed_password = Hasher.get_password_hash(user.password)
    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password=hashed_password,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully."}

# User Login Endpoint
@app.post("/user/login", tags=["User"], response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Token:
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not Hasher.verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}
