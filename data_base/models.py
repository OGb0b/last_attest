from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, VARCHAR
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Enum as SQLAEnum
from datetime import datetime as dt
import enum
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL= os.getenv("DATABASE_URL")
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)  # Telegram user ID
    username = Column(VARCHAR(64), nullable=True)
    created_at = Column(DateTime, default=dt.utcnow)

    businesses = relationship("Business", back_populates="user")

class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(VARCHAR(255), nullable=False)
    description = Column(Text, nullable=False)
    target_audience = Column(VARCHAR(255), nullable=False)
    created_at = Column(DateTime, default=dt.utcnow)

    user = relationship("User", back_populates="businesses")

async def async_main():
    engine = create_async_engine(
        DATABASE_URL,
        echo=True,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(async_main())