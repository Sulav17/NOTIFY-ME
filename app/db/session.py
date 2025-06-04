from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

DATABASE_URL = (
    f"mysql+pymysql://{settings.mysql_user}:{settings.mysql_password}@"
    f"{settings.mysql_host}:{settings.mysql_port}/{settings.mysql_db}"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
