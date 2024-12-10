from app.model import PostSchema
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.database.database import SessionLocal, Post



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()

# Routes
@app.get("/", tags=["root"])
async def read_root() -> dict:
    return {"message": "Welcome to your blog!"}


@app.get("/posts", tags=["posts"])
async def get_posts(db: Session = Depends(get_db())) -> dict:
    posts = db.query(Post).all()
    return {"data": [post.__dict__ for post in posts]}


@app.get("/posts/{id}", tags=["posts"])
async def get_single_post(id: int, db: Session = Depends(get_db())) -> dict:
    post = db.query(Post).filter(Post.id == id).first()
    if not post:
        raise HTTPException(status_code=404, detail="No such post with the supplied ID.")
    return {"data": post.__dict__}



@app.post("/posts", tags=["posts"])
async def create_post(post: PostSchema, db: Session = Depends(get_db())) -> dict:
    new_post = Post(title=post.title, content=post.content)
    db.add(new_post)  
    db.commit()  
    db.refresh(new_post)  
    return {"data": new_post.__dict__}  
