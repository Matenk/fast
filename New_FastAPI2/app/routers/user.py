from fastapi import APIRouter, Depends, status, HTTPException
# Сессия БД
from sqlalchemy.orm import Session
from starlette.status import HTTP_404_NOT_FOUND

# Функция подключения к БД
from app.backend.db_depends import get_db
# Аннотации, Модели БД и Pydantic.
from typing import Annotated
from app.models.user import User
from app.routers.task import create_task
from app.schemas import CreateUser, UpdateUser
# Функции работы с записями.
from sqlalchemy import insert, select, update, delete
# Функция создания slug-строки
from slugify import slugify

router = APIRouter(prefix='/user', tags=['user'])

@router.get('/')
async def all_users(db:Annotated[Session, Depends(get_db)]):
    users = db.scalars(select(User)).all()
    return users

@router.get('/user_id')
async def user_by_id(db:Annotated[Session, Depends(get_db)], user_id: int):
    user = db.scalars(select(User).where(User.id == user_id)).first()
    if user is None:
        raise HTTPException(status_code=404, detail='User was not found')
    return user


@router.post('/create')
async def create_user(db:Annotated[Session, Depends(get_db)], create_user: CreateUser):
    user = db.scalars(select(User).where(User.username == create_user.username)).first()
    if user is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User already exists')
    new_user = User(username=create_user.username,
                    firstname = create_user.firstname,
                    lastname = create_user.lastname,
                    age = create_user.age)
    db.add(new_user)
    db.commit()

@router.put('/update')
async def update_user(db:Annotated[Session, Depends(get_db)], user_id: int, update_user: UpdateUser):
    user = db.scalars(select(User).where(User.id == user_id)).first()
    if user is not None:
        db.execute(update(User).where(User.id == user_id).values(firstname=update_user.firstname,
                                                                 lastname=update_user.lastname,
                                                                 age=update_user.age))
        db.commit()
        return {'status_code': status.HTTP_200_OK, 'transaction': 'User update is successful!'}
    raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                        detail='User was not found')

@router.delete('/delete')
async def delete_user(db:Annotated[Session, Depends(get_db)], user_id: int):
    user = db.scalars(select(User).where(User.id == user_id)).first()
    if user is not None:
        db.execute(delete(User).where(User.id == user_id))
        db.commit()
        return {'status_code': status.HTTP_200_OK, 'transaction': 'User was deleted!'}
    raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                        detail='User was not found')

