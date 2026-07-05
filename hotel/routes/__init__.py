from flask import render_template, request, url_for, redirect, flash, session
from hotel import app, db, bcrypt, login_manager
from sqlalchemy import func
from hotel.models import User, Room, Customer_Details, Booking, Review, ContactMessage, Payment
from hotel.models import Hotel, Amenities, Complaint, Guest, AuditLog, Invoice
from hotel.forms import RegistrationForm, LoginForm, AccountForm, HotelSearchForm, GuestForm
from hotel.forms import ContactForm, ReviewForm, AddRoomForm,ComplaintForm, HotelForm, CreateAdminForm
from flask_login import login_user, logout_user, current_user, login_required
from datetime import date, timedelta, datetime
from .authentication_routes import *
from .booking_routes import *
from .customer_routes import *
from .admin_routes import *