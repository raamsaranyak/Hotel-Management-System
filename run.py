from hotel import app, db
from hotel.models import *

with app.app_context():
    print("Creating database tables...")
    db.create_all()
    print("Database tables created.")

if __name__ == "__main__":
    app.run()