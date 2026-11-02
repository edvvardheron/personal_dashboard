from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings

#sqlite needs this flag because fastapi uses multiple threads to handle requests,
# and sqlite is not thread-safe by default.
# This flag allows the database connection to be shared across threads.
connect_args = {'check_same_thread': False} if settings.database_url.startswith('sqlite') else {}

# engine is the core interface to the database,
# and it manages connections and executes SQL statements.
engine = create_engine(settings.database_url, connect_args=connect_args)

# sessionmaker is a factory for creating new Session objects,
# which are used to interact with the database in a transactional manner.
SessionLocal = sessionmaker(bind=engine)


# DeclarativeBase is a base class for all ORM models,
# and it provides the necessary metadata and functionality for mapping Python classes to database tables.
class Base(DeclarativeBase):
    pass

# get_db is a dependency function that provides a database session to the route handlers.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()