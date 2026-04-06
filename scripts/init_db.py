from app.db.database import Base, engine
from app.models.faq import FAQ  # noqa: F401

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully.")
