from fastapi.params import Depends
from jose import JWTError, jwt
from sqlalchemy import UUID
from sqlalchemy.orm import Session, sessionmaker
from starlette.exceptions import HTTPException
from app.core.database import db
from app.core.vars import ALGORITHM, SECRET_KEY
from app.models.user import User
from app.core.security import oauth2_schema

def get_session():
    try:
        Session = sessionmaker(bind=db)
        session = Session()
        yield session
    finally:
        session.close()

def verify_token(token: str = Depends(oauth2_schema), session: Session = Depends(get_session)):
    try:
        dic_info = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id = str(dic_info.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Acesso negado")
    
    user = session.query(User).filter(User.id==id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Acesso inválido")
    return user