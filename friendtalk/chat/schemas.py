# -*- coding: utf-8 -*-
from pydantic import BaseModel, Field
from pydantic.typing import List
from .forms import RegisterUserForm

class RegisterUserFormSchema(BaseModel):
    username: str = Field(description="Имя пользователя")
    email: str = Field(description="Электронная почта")
    password1: str = Field(description="Пароль")
    password2: str = Field(description="Подтверждение пароля")

class RegisterUserResponseSchema(BaseModel):
    msg: str = Field(description="Сообщение об успешной регистрации")

class FriendRequestSchema(BaseModel):
    friend_id: int = Field(description="ID друга")

class AddFriendResponseSchema(BaseModel):
    msg: str = Field(description="Сообщение о результате операции")


class DeleteFriendResponseSchema(BaseModel):
    msg: str = Field(description="Сообщение об успешном удалении друга")

class PathParameterSchema(BaseModel):
    friend_id: int = Field(description="ID друга")

class FriendRequestStatusResponseSchema(BaseModel):
    current_user: str = Field(description="Имя текущего пользователя")
    friend_user: str = Field(description="Имя друга")
    status: str = Field(description="Статус заявки на дружбу")

class AcceptFriendRequestResponseSchema(BaseModel):
    msg: str = Field(description="Сообщение об успешном принятии заявки")

class LoginFormSchema(BaseModel):
    username: str = Field(description="Имя пользователя")
    password: str = Field(description="Пароль")

class LoginResponseSchema(BaseModel):
    msg: str = Field(description="Сообщение об успешном входе")

class UserSchema(BaseModel):
    # Определите поля и описания для вашей модели User
    id: int = Field(description="ID пользователя")
    username: str = Field(description="Имя пользователя")
    email: str = Field(description="Электронная почта пользователя")

class ProfileViewSchema(BaseModel):
    # Определите поля и описания для вашего ответа
    friends: list[UserSchema] = Field(description="Список друзей")

class FriendRequestSchemaFull(BaseModel):
    # Определите поля и описания для вашей модели FriendRequest
    id: int = Field(description="ID запроса")
    from_user: int = Field(description="ID отправителя")
    to_user: int = Field(description="ID получателя")
    status: bool = Field(description="Статус запроса")

class FriendRequestListViewSchema(BaseModel):
    # Определите поля и описания для вашего ответа
    friend_requests: list[FriendRequestSchemaFull] = Field(description="Список запросов в друзья")


class OutRequestsListSchema(BaseModel):
    # A schema for the list of outgoing requests
    data: List[FriendRequestSchema] = Field(description="The list of outgoing requests")

class PostParameterSchema(BaseModel):
    # A schema for the POST parameter
    request_id: int = Field(description="The ID of the friend request to delete")