from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.models import *
from app.schemas import CreateTask, UpdateTask
from sqlalchemy import insert, select, update, delete
from slugify import slugify

router = APIRouter(prefix='/task', tags=['task'])


@router.get("/")
async def all_task(db: Annotated[Session, Depends(get_db)]):
        tasks = db.scalars(select(Task).where(Task.completed == False)).all()
        return tasks


@router.get("/task_id")
async def task_by_id(db: Annotated[Session, Depends(get_db)],
                     task_id: int):
    task_ = db.scalar(select(Task).where(Task.id == task_id))
    if task_ is not None:
        return task_
    raise HTTPException(status_code=404, detail="Task was not found")


@router.post("/create")
async def create_task(db: Annotated[Session, Depends(get_db)],
                      user_id: int,
                      task_create: CreateTask):
    user_ = db.scalar(select(User).where(User.id == user_id))
    if user_ is not None:
        db.execute(insert(Task).values(title=task_create.title,
                                   content=task_create.content,
                                   priority=task_create.priority,
                                   user_id=user_id,
                                   slug=slugify(task_create.title)))
        db.commit()
        return {
            'status_code': status.HTTP_201_CREATED,
            'transaction': 'Successful'
        }
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User was not found')

@router.put("/update")
async def update_task(db: Annotated[Session, Depends(get_db)],
                      task_id: int,
                      task_update: UpdateTask):
    task_ = db.scalars(select(Task).where(Task.id == task_id))
    for t in task_:
        if t is not None:
            db.execute(update(Task).where(Task.id == task_id).values(
                title=task_update.title,
                content=task_update.content,
                priority=task_update.priority))
            db.commit()
            return {
                'status_code': status.HTTP_200_OK,
                'transaction': 'Task update is successful'
            }
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Task was not found')


@router.delete("/delete")
async def delete_task(db: Annotated[Session, Depends(get_db)],
                      task_id: int):
    task_ = db.scalars(select(Task).where(Task.id == task_id))
    for t in task_:
        if t is not None:
# Для практического применения лучше менять статус задачи, а не удалять:
#            db.execute(update(Task).where(Task.id == task_id).values(completed=True))
# Однако пока делаем удаление по условию задачи:
            db.execute(delete(Task).where(Task.id == task_id))
            db.commit()
            return {
                'status_code': status.HTTP_200_OK,
                'transaction': 'Task delete is successful'}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Task was not found')