from database import engine, Base
from models import User, TaskLog  # make sure TaskLog is included!

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Done.")
