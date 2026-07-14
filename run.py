from hotel import app, db
from hotel.models import *

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run()