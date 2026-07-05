from hotel import app, db
from hotel.models import *

with app.app_context():
    print("=" * 50)
    print("Creating database...")
    db.create_all()
    print("Database created successfully!")
    print("=" * 50)

if __name__ == "__main__":
    app.run()