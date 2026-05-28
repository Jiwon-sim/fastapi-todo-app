from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import models
from database import engine, get_db

app = FastAPI()

# 앱 시작 시 DB 테이블 자동 생성
models.Base.metadata.create_all(bind=engine)

# HTML 템플릿 폴더 지정
templates = Jinja2Templates(directory="templates")

# 1. 할 일 목록 조회 (HTML 페이지 출력)
@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    todos = db.query(models.Todo).all()
    return templates.TemplateResponse(
        name="index.html",
        request=request,
        context={"todo_list": todos}
    )

# 2. 할 일 추가 (HTML Form 요청 처리)
@app.post("/add")
def add_todo(title: str = Form(...), db: Session = Depends(get_db)):
    new_todo = models.Todo(title=title)
    db.add(new_todo)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

# 3. 할 일 상태 변경 (완료/미완료 토글)
@app.get("/update/{todo_id}")
def update_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if todo:
        todo.completed = not todo.completed
        db.commit()
    return RedirectResponse(url="/", status_code=303)

# 4. 할 일 삭제
@app.get("/delete/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if todo:
        db.delete(todo)
        db.commit()
    return RedirectResponse(url="/", status_code=303)
