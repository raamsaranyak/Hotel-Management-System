from hotel import db,login_manager
from flask_login import UserMixin
from sqlalchemy.orm import validates
from datetime import datetime
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
class User(db.Model,UserMixin):
    user_id=db.Column(db.Integer,primary_key=True,)
    username=db.Column(db.String(50),unique=True,index=True,nullable=False)
    password=db.Column(db.String(70),nullable=False)
    email=db.Column(db.String(50),unique=True,index=True,nullable=False)
    role=db.Column(db.String(15),index=True,nullable=False,default="customer")
    account_status=db.Column(db.String(20),index=True,nullable=False,default="ACTIVE")
    created_date_time=db.Column(db.DateTime,index=True,nullable=False,default=datetime.utcnow)
    deleted_at=db.Column(db.DateTime,index=True,nullable=True,default=None)
    customer_details=db.relationship("Customer_Details",backref="user",uselist=False)
    booking_records=db.relationship("Booking",backref="user")
    guests=db.relationship("Guest",backref="user")
    reviews=db.relationship("Review",backref="user")
    complaints=db.relationship("Complaint",backref="user")
    audit_logs=db.relationship("AuditLog",backref="user")
    created_rooms=db.relationship("Room",foreign_keys="Room.created_by",backref="admin_creator")
    updated_rooms=db.relationship("Room",foreign_keys="Room.updated_by",backref="admin_updater")
    def get_id(self):
        return str(self.user_id)
class Customer_Details(db.Model):
    user_id=db.Column(db.Integer,db.ForeignKey("user.user_id"),primary_key=True)
    customer_name=db.Column(db.String(50),nullable=False)
    gender=db.Column(db.String(10),nullable=False)
    date_of_birth=db.Column(db.Date,nullable=False)
    contact_number=db.Column(db.String(20),index=True)
    address=db.Column(db.String(70))
class Hotel(db.Model):
    hotel_id=db.Column(db.Integer,primary_key=True)
    hotel_name=db.Column(db.String(50),index=True,nullable=False)
    branch_name=db.Column(db.String(50),index=True,nullable=False)
    location=db.Column(db.String(100),index=True,nullable=False)
    number_of_floors=db.Column(db.Integer,nullable=False)
    contact_number=db.Column(db.String(20),nullable=False)
    email=db.Column(db.String(50),nullable=False)
    rooms=db.relationship("Room",backref="hotel")
    booking_records=db.relationship("Booking",backref="hotel")
    created_at=db.Column(db.DateTime,default=datetime.utcnow,nullable=False)
    created_by=db.Column(db.Integer,db.ForeignKey("user.user_id"),nullable=False,index=True)
    updated_at=db.Column(db.DateTime,default=datetime.utcnow,nullable=False)
    updated_by=db.Column(db.Integer,db.ForeignKey("user.user_id"),nullable=False,index=True)
    @validates("number_of_floors")
    def validate_floors(self,key,value):
        if value<1 or value>100:
            raise ValueError("Number of floors must be between 1 and 100.")
        return value
class Room(db.Model):
    room_id=db.Column(db.Integer,primary_key=True)
    room_no=db.Column(db.Integer,nullable=False,index=True)
    hotel_id=db.Column(db.Integer,db.ForeignKey("hotel.hotel_id"),nullable=False,index=True)
    category=db.Column(db.String(20),index=True,nullable=False)
    capacity=db.Column(db.Integer,nullable=False)
    beds=db.Column(db.String(20),nullable=False)
    current_price=db.Column(db.Float,nullable=False,index=True)
    floor=db.Column(db.Integer,nullable=False)
    room_status=db.Column(db.String(30),nullable=False,index=True)
    booking_records=db.relationship("Booking",backref="room")
    created_at=db.Column(db.DateTime,default=datetime.utcnow,nullable=False)
    created_by=db.Column(db.Integer,db.ForeignKey("user.user_id"),nullable=False,index=True)
    updated_at=db.Column(db.DateTime,default=datetime.utcnow,nullable=False)
    updated_by=db.Column(db.Integer,db.ForeignKey("user.user_id"),nullable=False,index=True)
    @validates("current_price","capacity")
    def validate_price(self,key,value):
        if value<=0:
            raise ValueError(f"{key}  cannot be negative")
        return value 
    @validates("floor")
    def validate_floor(self,key,value):
        if value < 0:
            raise ValueError("Floor cannot be negative")
        return value
    __table_args__=(db.UniqueConstraint("hotel_id","room_no",name="uq_hotel_room"),)
class Amenities(db.Model):
    amenity_id=db.Column(db.Integer,primary_key=True)
    hotel_id=db.Column(db.Integer,db.ForeignKey("hotel.hotel_id"),nullable=False,index=True)
    room_category=db.Column(db.String(20),nullable=False,index=True)
    amenity_name=db.Column(db.String(50),nullable=False,index=True)
class Guest(db.Model):
    guest_id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey("user.user_id"))
    booking_id=db.Column(db.Integer,db.ForeignKey("booking.booking_id"))
    guest_name=db.Column(db.String(30),nullable=False,index=True)
    gender=db.Column(db.String(10),nullable=False)
    age=db.Column(db.Integer,nullable=False)
    contact_number=db.Column(db.String(20),nullable=False)
    number_of_people=db.Column(db.Integer,nullable=False)
    @validates("age","number_of_people")
    def validate_positive(self,key,value):
        if value<=0:
            raise ValueError(f"{key} must be geater than 0")
        return value
class Booking(db.Model):
    booking_id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey("user.user_id"),nullable=False)
    hotel_id=db.Column(db.Integer,db.ForeignKey("hotel.hotel_id"),nullable=False)
    check_in_date=db.Column(db.Date,nullable=False,index=True)
    check_out_date=db.Column(db.Date,nullable=False,index=True)
    number_of_people=db.Column(db.Integer,nullable=False)
    booking_status=db.Column(db.String(20),nullable=False,index=True)
    booking_date_time=db.Column(db.DateTime,nullable=False,index=True)
    price_at_booking = db.Column(db.Float,nullable=False)
    actual_check_in_datetime=db.Column(db.DateTime)
    actual_check_out_datetime=db.Column(db.DateTime)
    guests=db.relationship("Guest",backref="booking")
    room_id=db.Column(db.Integer,db.ForeignKey("room.room_id"),nullable=False)
    payments=db.relationship("Payment",backref="booking")
    reviews=db.relationship("Review",backref="booking")
    complaints=db.relationship("Complaint",backref="booking")
    @validates("number_of_people")
    def validate_positive(self,key,value):
        if value<=0:
            raise ValueError(f"{key} must be greater than 0")
        return value
class Payment(db.Model):
    transaction_id=db.Column(db.String(100),primary_key=True)
    booking_id=db.Column(db.Integer,db.ForeignKey("booking.booking_id"),nullable=False)
    transaction_date_time=db.Column(db.DateTime,index=True,nullable=False)
    amount=db.Column(db.Float,nullable=False)
    payment_method=db.Column(db.String(30),nullable=False)
    payment_status=db.Column(db.String(20),nullable=False,index=True)
    receipt_number=db.Column(db.String(50),nullable=False,unique=True,index=True)
    invoice=db.relationship("Invoice",backref="payment",uselist=False)
    @validates("amount")
    def validate_amount(self,key,value):
        if value <= 0:
            raise ValueError("Amount cannot be negative")
        return value
class Invoice(db.Model):
    invoice_id=db.Column(db.Integer,primary_key=True)
    transaction_id=db.Column(db.String(100),db.ForeignKey("payment.transaction_id"),nullable=False)
    tax_amount=db.Column(db.Float,default=0)
    discount_amount=db.Column(db.Float,default=0)
    final_amount=db.Column(db.Float)
    invoice_date=db.Column(db.Date,index=True,nullable=False)
    @validates("tax_amount","discount_amount","final_amount")
    def validate_amounts(self,key,value):
        if value < 0:
            raise ValueError(f"{key} cannot be negative")
        return value
class Review(db.Model):
    review_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), index=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("booking.booking_id"), unique=True)
    rating = db.Column(db.Integer,index=True,nullable=False)
    review_text = db.Column(db.Text)
    review_datetime = db.Column(db.DateTime, index=True)
    review_visibility=db.Column(db.String(20),nullable=False,default="VISIBLE",index=True)
    @validates("rating")
    def validate_rating(self,key,value):
        if value < 1 or value > 5:
            raise ValueError("Rating must be between 1 and 5")
        return value
class Complaint(db.Model):
    complaint_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), index=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("booking.booking_id"), index=True)
    complaint_text = db.Column(db.Text)
    complaint_datetime = db.Column(db.DateTime, index=True)
    complaint_status = db.Column(db.String(30), index=True)
    resolution_details = db.Column(db.Text,default=None)
class ContactMessage(db.Model):
    message_id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50),nullable=False,index=True)
    contact_number=db.Column(db.String(20),nullable=False,index=True)
    email=db.Column(db.String(50),nullable=False,index=True)
    message=db.Column(db.Text,nullable=False)
    date_time=db.Column(db.DateTime,nullable=False,index=True,default=datetime.utcnow)
class AuditLog(db.Model):
    log_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), index=True)
    action_performed = db.Column(db.String(200), index=True)
    table_name = db.Column(db.String(100), index=True)
    record_id = db.Column(db.Integer, index=True)
    action_datetime = db.Column(db.DateTime, index=True)