from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, VARCHAR
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Enum as SQLAEnum
from datetime import datetime
import enum
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import asyncio


DATABASE_URL= "postgresql+asyncpg://postgress:0000@localhost:5432/attest"
Base = declarative_base()

class GenerationType(str, enum.Enum):
    product_card = "product_card"
    product_description = "product_description"
    ad_headline = "ad_headline"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)  # Telegram user ID
    username = Column(VARCHAR(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    businesses = relationship("Business", back_populates="user")

class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(VARCHAR(255), nullable=False)
    description = Column(Text, nullable=False)
    target_audience = Column(VARCHAR(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="businesses")
    generations = relationship("Generation", back_populates="business")

class Generation(Base):
    __tablename__ = "generations"

    id = Column(Integer, primary_key=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    type = Column(SQLAEnum(GenerationType), nullable=False)
    object_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    business = relationship("Business", back_populates="generations")

class ProductCard(Base):
    __tablename__ = "product_cards"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    features = Column(Text, nullable=True)
    price = Column(String(50), nullable=True)
    image_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ProductDescription(Base):
    __tablename__ = "product_descriptions"

    id = Column(Integer, primary_key=True)
    input_data = Column(Text, nullable=False)  # JSON как строка
    output_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class AdHeadline(Base):
    __tablename__ = "ad_headlines"

    id = Column(Integer, primary_key=True)
    input_data = Column(Text, nullable=False)
    headline = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Асинхронное создание таблиц
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