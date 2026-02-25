from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Optional

Base = declarative_base()


class DatabaseConfig:
    """Database configuration"""

    def __init__(
        self,
        user: str,
        password: str,
        host: str,
        port: int,
        database: str,
        echo: bool = False,
    ):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database
        self.echo = echo

    @property
    def connection_string(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    def get_engine(self):
        """Get SQLAlchemy engine"""
        return create_engine(
            self.connection_string,
            echo=self.echo,
            pool_size=10,
            max_overflow=20,
            pool_recycle=3600,
        )

    def get_session_factory(self):
        """Get session factory"""
        engine = self.get_engine()
        return sessionmaker(bind=engine, expire_on_commit=False)

    def create_all_tables(self):
        """Create all tables"""
        engine = self.get_engine()
        Base.metadata.create_all(bind=engine)
