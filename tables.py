import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    password = Column(String(50), nullable=False)


class Account(Base):
    __tablename__ = 'account'
    id = Column(Integer, primary_key=True)
    account_name = Column(String(50))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)


class AccountDetails(Base):
    __tablename__ = 'account_details'
    id = Column(Integer, primary_key=True)
    question = Column(String(100), nullable=True)
    password = Column(String(50), nullable=False)
    account_id = Column(Integer, ForeignKey('account.id'))
    account = relationship(Account)


def create_db(db_name):
    engine = create_engine(db_name)
    Base.metadata.create_all(engine)


# TODO: organize into a connector class?  > different storage method can use the same format
def login(user):
    return True


def load_record(user):
    return {}
