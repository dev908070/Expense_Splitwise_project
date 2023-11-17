import bcrypt
from db_layer import User, Base, engine
from sqlalchemy.orm import sessionmaker
import pandas as pd

Session = sessionmaker(bind=engine)
session = Session()

def checkPhoneNumberExist(mobileNumber):
    result = session.query(User).filter_by(mobileNumber=mobileNumber).first() is not None
    return result

def checkEmailAddressExist(email):
    result = session.query(User).filter_by(email=email).first() is not None
    return result

def hash_password(password):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password

def check_password(input_password, hashed_password):
    return bcrypt.checkpw(input_password.encode('utf-8'), hashed_password)

def registerUser(name,email,mobileNumber,password):
    password= hash_password(password)
    if checkPhoneNumberExist(mobileNumber):
        return "mobile number already exists"
    if checkEmailAddressExist(email):
        return "email already exists"
    new_user = User(name=name, email=email, mobileNumber=mobileNumber, password=password)
    session.add(new_user)
    session.commit()
    session.close()
    return "User registered successfully"


def loginUser(email,input_password):
    if checkEmailAddressExist(email):
        user = session.query(User).filter_by(email=email).first()
        if user:
            hashed_password=user.password
            check_pwd=check_password(input_password, hashed_password)
        if check_pwd:
            user_data = session.query(User).filter_by(email=email).all()
            if user_data:
                columns = ['userId', 'name', 'email', 'mobileNumber', 'created_at']
                data = [(user.userId, user.name, user.email, user.mobileNumber, user.created_at) for user in user_data]
                login_result = pd.DataFrame(data, columns=columns)  
                user.is_authenticated = True
                session.commit() 
                session.close()         
                return login_result.to_json(orient="records",date_format='iso')
        else:
            return "Wrong password entered"
    else:
        return "email is not exists please register first"


def logout_user(email):
    try:
        user = session.query(User).filter_by(email=email).first()
        if user:
            user.is_authenticated = False
            session.commit()
            return  "Logout"
        else:
            return "Logout failed"

    except Exception as e:
        session.rollback()
        return "Logout failed"

    finally:
        session.close()
