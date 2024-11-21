from sqlalchemy import Column, Integer, String, ForeignKey, Index, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class MessageModel(Base):
    __tablename__ = 'message'
    id = Column(String, primary_key=True, default=None)
    email = Column(String, default=None)
    username = Column(String, default=None)
    ip_address = Column(String, default=None)
    created_at = Column(String, default=None)
    location = relationship("LocationModel",back_populates="message")
    device_info = relationship("DeviceInfoModel",back_populates="message")
    explosive_sentences = relationship("ExplosiveSentenceModel",back_populates="message")
    hostage_sentences = relationship("HostageSentenceModel",back_populates="message")

class LocationModel(Base):
    __tablename__ = 'location'
    id = Column(Integer, primary_key=True, autoincrement=True)
    latitude = Column(Float, default=None)
    longitude = Column(Float, default=None)
    city = Column(String, default=None)
    country = Column(String, default=None)
    message_id = Column(String, ForeignKey('message.id'), default=None)
    message = relationship("MessageModel", back_populates="location")

class DeviceInfoModel(Base):
    __tablename__ = 'device_info'
    id = Column(Integer, primary_key=True, autoincrement=True)
    browser = Column(String, default=None)
    os = Column(String, default=None)
    device_id = Column(String, default=None)
    message_id = Column(String, ForeignKey('message.id'))

    message = relationship("MessageModel", back_populates="device_info")

class ExplosiveSentenceModel(Base):
    __tablename__ = 'explosive_sentence'
    id = Column(Integer, primary_key=True, autoincrement=True)
    sentence = Column(String, default=None)
    message_id = Column(String, ForeignKey('message.id'), default=None)
    message = relationship("MessageModel", back_populates="explosive_sentences")

class HostageSentenceModel(Base):
    __tablename__ = 'hostage_sentence'
    id = Column(Integer, primary_key=True, autoincrement=True)
    sentence = Column(String, default=None)
    message_id = Column(String, ForeignKey('message.id'), default=None)
    message = relationship("MessageModel", back_populates="hostage_sentences")