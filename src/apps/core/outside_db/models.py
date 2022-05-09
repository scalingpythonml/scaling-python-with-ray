# coding: utf-8
from sqlalchemy import Column, Date, Integer, String, text
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class SmsItem(Base):
    __tablename__ = "sms_item"

    id = Column(Integer, primary_key=True)
    sms_text = Column(String(50), nullable=False)
    sms_id = Column(Integer, nullable=False, unique=True)
    user_email = Column(String(50), nullable=False)
    recipient_phone_number = Column(String(50), nullable=False)
    sender_phone_number = Column(String(50), nullable=False)
    sms_date = Column(Date, nullable=False, server_default=text("(curdate())"))
