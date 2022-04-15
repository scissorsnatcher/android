from sqlalchemy import (BigInteger, Boolean, Column, DateTime,
                        ForeignKeyConstraint, Integer, PrimaryKeyConstraint,
                        SmallInteger, String, UniqueConstraint, create_engine,
                        func)
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()


class Settings(Base):
    __tablename__ = 'settings'

    param = Column(String, primary_key=True)
    value = Column(JSON, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('param', name='settings_pkey'),
    )


class Account(Base):
    __tablename__ = 'account'

    id = Column(SmallInteger, autoincrement=True)
    zoom_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    premium = Column(Boolean, nullable=False)
    description = Column(String)

    meetings = relationship('AccountMeeting')

    __table_args__ = (
        PrimaryKeyConstraint('id', name='account_pkey'),
        UniqueConstraint('zoom_id', 'name', name='account_uniqueness'),
    )


class AccountMeeting(Base):
    __tablename__ = 'account_meeting'

    id = Column(Integer, autoincrement=True)
    account_id = Column(SmallInteger)
    meeting_id = Column(Integer)
    is_creator = Column(Boolean, default=False)

    meetings = relationship('Meeting', backref='account_meeting')

    __table_args__ = (
        PrimaryKeyConstraint('id', name='account_meeting_pkey'),
        UniqueConstraint('account_id', 'meeting_id', name='account_meeting_uniqueness'),
        ForeignKeyConstraint(('account_id',), ('account.id',), name='account_meeting_account_id_fkey'),
        ForeignKeyConstraint(('meeting_id',), ('meeting.id',), name='account_meeting_meeting_id_fkey'),
    )


class Meeting(Base):
    __tablename__ = 'meeting'

    id = Column(Integer, primary_key=True, autoincrement=True)
    zoom_id = Column(Integer, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('id', name='meeting_pkey'),
    )


class MeetingConfig(Base):
    __tablename__ = 'meeting_config'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    meeting_id = Column(BigInteger)
    config = Column(JSON, nullable=False)
    action = Column(String, nullable=False)
    ts = Column(DateTime, nullable=False)

    meeting = relationship('Meeting', lazy='joined')

    __table_args__ = (
        PrimaryKeyConstraint('id', name='meeting_config_pkey'),
        ForeignKeyConstraint(('meeting_id',), ('meeting.id',), name='meeting_config_meeting_id_fkey'),
    )


class Log(Base):
    __tablename__ = 'log'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    meeting_config_id = Column(BigInteger)
    message = Column(JSON, nullable=False)
    ts = Column(DateTime, server_default=func.now())
    type = Column(String, nullable=False)

    meeting = relationship('Meeting', lazy='joined')

    __table_args__ = (
        PrimaryKeyConstraint('id', name='log_pkey'),
        ForeignKeyConstraint(('meeting_config_id',), ('meeting_config.id',), name='log_meeting_config_id_fkey'),
    )


class Repository:
    instances = {}

    @classmethod
    async def create(cls, db_url: str, **kwargs):
        if db_url in Repository.instances:
            return Repository.instances[db_url]

        instance = cls()
        engine = create_engine(db_url, **kwargs)

        Base.metadata.create_all(engine)
        session = sessionmaker(engine, expire_on_commit=False)

        setattr(instance, 'session', session)
        setattr(instance, 'engine', engine)

        cls.instances[db_url] = instance
        return instance
