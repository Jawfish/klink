from argon2 import PasswordHasher
from fastapi import APIRouter, Depends

from service.api import messages as msg
from service.api.schema import UserIn
from service.database.data_handler import DataHandler, get_data_handler

ph = PasswordHasher()
router = APIRouter()


@router.post("/user/", status_code=201)
def create_user(
    user_in: UserIn,
    data_handler: DataHandler = Depends(get_data_handler),
) -> dict:
    hashed_password = ph.hash(user_in.password)
    data_handler.create_user(user_in.username, hashed_password)

    return {"message": msg.USER_CREATED_MSG}


# import datetime
# import os

# import jwt
# from common.database_middleware import get_db
# from dotenv import load_dotenv

# load_dotenv()

# SECRET_KEY = os.getenv("SECRET_KEY")

# @router.get("/user/{username}")
# def get_user(username: str, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.username == username).first()
#     if user is not None:
#         return {"username": user.username}
#     # auth errors are kept intentionally vague so attackers can't enumerate users
#     return {"message": "Invalid credentials"}


# @router.post("/token/")
# def login(login_data: UserIn, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.username == login_data.username).first()
#     if user is None:
#         # return 400 instead of 404 for obscurity purposes
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#     try:
#         ph.verify(user.password, login_data.password)
#     except exceptions.VerifyMismatchError:
#         raise HTTPException(status_code=401, detail="Invalid credentials")

#     token_data = {
#         "sub": user.username,
#         "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
#     }
#     token = jwt.encode(token_data, SECRET_KEY, algorithm="HS256")
#     return {"access_token": token}
