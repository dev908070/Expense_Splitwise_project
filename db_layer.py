from sqlalchemy import create_engine, Column, Integer, String, DateTime,ForeignKey,Boolean
from sqlalchemy.ext.declarative import declarative_base
import datetime
import pandas as pd
import sqlite3

# Step 2: Create declarative base
Base = declarative_base()

# Step 3: Create the database engine
# The database file will be created in the current directory with the name "AttendanceManagementSystem.db"
engine = create_engine('sqlite:///ExpenseSplitwise.db', echo=True)  # Set echo to True to see SQL commands in the console
conn_string = 'ExpenseSplitwise.db'

# Step 4: Define your models
class User(Base):
    __tablename__ = 'users'

    userId = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    mobileNumber = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    is_authenticated=Column(Boolean,default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
   
    
class Expense_group(Base):
    __tablename__ = 'expense_group'

    expGroupId = Column(Integer, primary_key=True, autoincrement=True)
    expGroupName = Column(String(50), nullable=False)
    userId = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class Expense_group_user_mapping(Base):
    __tablename__ = 'expense_group_user_mapping'

    expense_group_user_mapping_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    mobileNumber = Column(String(100), nullable=False)
    expGroupId = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    
class Expense_data(Base):
    __tablename__ = 'expense_data'

    exp_id = Column(Integer, primary_key=True, autoincrement=True)
    total_expense_amount=Column(Integer, nullable=False)
    splited_exp_amount = Column(Integer, nullable=False)
    user_mapping_id = Column(Integer, nullable=False)
    expGroupId = Column(Integer, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
        

# Step 5: Create the tables in the database
Base.metadata.create_all(engine)

