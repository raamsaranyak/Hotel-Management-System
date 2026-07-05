from . import *
@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if current_user.role!="admin":
        flash("Access Denied","danger")
        return redirect(url_for("home"))
    user_count=User.query.count()
    hotel_count=Hotel.query.count()
    room_count=Room.query.count()
    booking_count=Booking.query.count()
    review_count=Review.query.count()
    message_count=ContactMessage.query.count()
    available_rooms=Room.query.filter_by(room_status="AVAILABLE").count()
    occupied_rooms=Room.query.filter_by(room_status="OCCUPIED").count()
    maintainence_rooms=Room.query.filter_by(room_status="MAINTAINENCE").count()
    booked_rooms=Room.query.filter_by(room_status="BOOKED").count()
    booked_count=Booking.query.filter_by(booking_status="BOOKED").count()
    checked_in_count=Booking.query.filter_by(booking_status="CHECKED_IN").count()
    active_users=User.query.filter_by(account_status="ACTIVE").count()
    blocked_users=User.query.filter_by(account_status="BLOCKED").count()
    inactive_users=User.query.filter_by(account_status="INACTIVE").count()
    checked_out_count=Booking.query.filter_by(booking_status="CHECKED_OUT").count()
    cancelled_count=Booking.query.filter_by(booking_status="CANCELLED").count()
    pending_complaints=Complaint.query.filter_by(complaint_status="PENDING").count()
    resolved_complaints=Complaint.query.filter_by(complaint_status="RESOLVED").count()
    visible_reviews=Review.query.filter_by(review_visibility="VISIBLE").count()
    hidden_reviews=Review.query.filter_by(review_visibility="HIDDEN").count()
    return render_template("admin/admin_dashboard.html",
                            user_count=user_count,
                            hotel_count=hotel_count,
                            room_count=room_count,
                            booking_count=booking_count,
                            review_count=review_count,
                            message_count=message_count,
                            available_rooms=available_rooms,
                            occupied_rooms=occupied_rooms,
                            maintainence_rooms=maintainence_rooms,
                            booked_rooms=booked_rooms,
                            booked_count=booked_count,
                            checked_in_count=checked_in_count,
                            active_users=active_users,
                            blocked_users=blocked_users,
                            inactive_users=inactive_users,
                            checked_out_count=checked_out_count,
                            cancelled_count=cancelled_count,
                            pending_complaints=pending_complaints,
                            resolved_complaints=resolved_complaints,
                            visible_reviews=visible_reviews,
                            hidden_reviews=hidden_reviews,
                            )
@app.route("/admin/hotels")
@login_required
def manage_hotels():
    if current_user.role!="admin":
        flash("Access Denied","danger")
        return redirect(url_for("home"))
    search=request.args.get("search","").strip()
    sort=request.args.get("sort","hotel_name")
    order=request.args.get("order","asc")
    page=request.args.get("page",1,type=int)
    hotel_id=request.args.get("hotel_id",type=int)
    query=Hotel.query
    if search:
        query=query.filter(
            Hotel.hotel_name.ilike(f"%{search}%")|
            Hotel.branch_name.ilike(f"%{search}%")|
            Hotel.location.ilike(f"%{search}%")
        )
    field=Hotel.hotel_id
    if sort=="hotel_id":
        field=Hotel.hotel_id
    elif sort=="hotel_name":
        field=Hotel.hotel_name
    elif sort=="branch_name":
        field=Hotel.branch_name
    elif sort=="location":
        field=Hotel.location
    if order == "asc":
        query = query.order_by(field.asc())
    else:
        query = query.order_by(field.desc())
    hotels=query.paginate(page=page,per_page=10)
    selected_hotel=None
    rooms=[]
    drawer_open=False
    if hotel_id:
        selected_hotel=Hotel.query.get_or_404(hotel_id)
        rooms=Room.query.filter_by(hotel_id=hotel_id).order_by(Room.room_no.asc()).all()
        drawer_open=True
    return render_template(
        "admin/manage_hotels.html",
        hotels=hotels,
        search=search,
        selected_sort=sort,
        selected_order=order,
        selected_hotel=selected_hotel,
        rooms=rooms,
        drawer_open=drawer_open
    )
@app.route("/admin/hotels/<int:hotel_id>")
@login_required
def hotel_profile(hotel_id):
    if current_user.role!="admin":
        flash("Access Denied","danger")
        return redirect(url_for("home"))
    hotel=Hotel.query.get_or_404(hotel_id)
    total_rooms=Room.query.filter_by(hotel_id=hotel.hotel_id).count()
    available_rooms=Room.query.filter_by(hotel_id=hotel.hotel_id,room_status="AVAILABLE").count()
    occupied_rooms=Room.query.filter_by(hotel_id=hotel.hotel_id,room_status="OCCUPIED").count()
    booked_rooms=Room.query.filter_by(hotel_id=hotel.hotel_id,room_status="BOOKED").count()
    status=request.args.get("booking_status","ALL")
    search=request.args.get("search","").strip()
    sort=request.args.get("sort_by","booking_date_time")
    direction=request.args.get("direction","desc")
    page=request.args.get("page",1,type=int)
    query=Booking.query.filter_by(hotel_id=hotel.hotel_id)
    if status!="ALL":
        query=query.filter(Booking.booking_status==status)
    if search:
        if search.isdigit():
            query=query.filter(Booking.booking_id==int(search))
        else:
            query=query.join(Booking.user).join(User.customer_details).filter(Customer_Details.customer_name.ilike(f"%{search}%"))
    field=Booking.booking_date_time
    if sort=="booking_date_time":
        field=Booking.booking_date_time
    elif sort=="check_in_date":
        field=Booking.check_in_date
    elif sort=="price_at_booking":
        field=Booking.price_at_booking
    if direction=="asc":
        query=query.order_by(field.asc())
    else:
        query=query.order_by(field.desc())
    bookings=query.paginate(page=page,per_page=10)
    rooms=Room.query.filter_by(hotel_id=hotel.hotel_id).order_by(Room.room_no.asc()).all()
    return render_template(
        "admin/hotel_profile.html",
        hotel=hotel,
        rooms=rooms,
        total_rooms=total_rooms,
        available_rooms=available_rooms,
        occupied_rooms=occupied_rooms,
        booked_rooms=booked_rooms,
        bookings=bookings,
        search=search,
        selected_status=status,
        selected_sort=sort,
        selected_direction=direction
    )
@app.route("/admin/hotels/add",methods=["GET","POST"])
@login_required
def add_hotel():
    if current_user.role!="admin":
        flash("Access Denied","danger")
        return redirect(url_for("home"))
    form=HotelForm()
    if form.validate_on_submit():
        existing_hotel=Hotel.query.filter_by(
            hotel_name=form.hotel_name.data,
            branch_name=form.branch_name.data
        ).first()
        if existing_hotel:
            flash("Hotel already exists!","warning")
            return redirect(url_for("add_hotel"))
        hotel=Hotel(
            hotel_name=form.hotel_name.data,
            branch_name=form.branch_name.data,
            location=form.location.data,
            number_of_floors=form.number_of_floors.data,
            contact_number=form.contact_number.data,
            email=form.email.data,
            created_by=current_user.user_id,
            updated_by=current_user.user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        try:
            db.session.add(hotel)
            db.session.flush()
            create_audit_log("Added Hotel","Hotel",hotel.hotel_id)
            db.session.commit()
            flash("Hotel added successfully","success")
            return redirect(url_for("manage_hotels"))
        except Exception:
            db.session.rollback()
            flash("Failed to add hotel. Please try again.","danger")
    return render_template("admin/add_hotel.html",form=form)
@app.route("/admin/hotels/<int:hotel_id>/edit",methods=["GET","POST"])
@login_required
def edit_hotel(hotel_id):
    if current_user.role!="admin":
        flash("Access Denied","danger")
        return redirect(url_for("home"))
    hotel=Hotel.query.get_or_404(hotel_id)
    form=HotelForm()
    if form.validate_on_submit():
        existing_hotel=Hotel.query.filter_by(
            hotel_name=form.hotel_name.data,
            branch_name=form.branch_name.data
        ).first()
        if existing_hotel and existing_hotel.hotel_id!=hotel.hotel_id:
            flash("Hotel already exists.","warning")
            return redirect(url_for("edit_hotel",hotel_id=hotel.hotel_id))
        hotel.hotel_name=form.hotel_name.data
        hotel.branch_name=form.branch_name.data
        hotel.location=form.location.data
        hotel.number_of_floors=form.number_of_floors.data
        hotel.contact_number=form.contact_number.data
        hotel.email=form.email.data
        hotel.updated_by=current_user.user_id
        hotel.updated_at=datetime.utcnow()
        try:
            create_audit_log("Updated Hotel","Hotel",hotel.hotel_id)
            db.session.commit()
            flash("Hotel updated successfully.","success")
            return redirect(url_for("manage_hotels"))
        except Exception:
            db.session.rollback()
            flash("Failed to update hotel. Please try again.","danger")
    elif request.method=="GET":
        form.hotel_name.data=hotel.hotel_name
        form.branch_name.data=hotel.branch_name
        form.location.data=hotel.location
        form.number_of_floors.data=hotel.number_of_floors
        form.contact_number.data=hotel.contact_number
        form.email.data=hotel.email
    return render_template("admin/edit_hotel.html",form=form,hotel=hotel)
@app.route("/admin/rooms")
@login_required
def manage_rooms():
    if current_user.role!="admin":
        flash("Access Denied","danger")
        return redirect(url_for("home"))
    status=request.args.get("room_status","ALL")
    search=request.args.get("search","").strip()
    category=request.args.get("category","ALL")
    sort=request.args.get("sort","room_no")
    order=request.args.get("order","asc")
    page=request.args.get("page",1,type=int)
    room_id=request.args.get("room_id",type=int)
    query=Room.query
    if status!="ALL":
        query=query.filter(Room.room_status==status)
    if search:
        if search.isdigit():
            query=query.filter(Room.room_no==int(search))
        else:
            query=query.join(Room.hotel).filter(Hotel.hotel_name.ilike(f"%{search}%"))
    if category!="ALL":
        query=query.filter(Room.category==category)
    field=Room.room_no
    if sort=="room_no":
        field=Room.room_no
    elif sort=="current_price":
        field=Room.current_price
    elif sort=="capacity":
        field=Room.capacity
    elif sort=="floor":
        field=Room.floor
    if order=="asc":
        query=query.order_by(field.asc())
    else:
        query=query.order_by(field.desc())   
    rooms=query.paginate(page=page,per_page=10)
    selected_room = None
    amenities = []
    drawer_open = False
    if room_id:
        selected_room = Room.query.get_or_404(room_id)
        amenities = Amenities.query.filter_by(hotel_id=selected_room.hotel_id,room_category=selected_room.category).all()
        drawer_open = True
    return render_template("admin/manage_rooms.html",
                            rooms=rooms,
                            search=search,
                            selected_status=status,
                            selected_category=category,
                            selected_sort=sort,
                            selected_order=order,
                            selected_room=selected_room,
                            amenities=amenities,
                            drawer_open=drawer_open
                            )
@app.route("/admin/rooms/add",methods=["GET","POST"])
@login_required
def add_room():
    if current_user.role!="admin":
        flash("Access Denied","danger")
        return redirect(url_for("home"))
    form=AddRoomForm()
    hotels=Hotel.query.all()
    form.hotel.choices=[(str(hotel.hotel_id), hotel.hotel_name)for hotel in hotels]
    if form.validate_on_submit():
        existing_room=Room.query.filter_by(room_no=form.room_no.data,hotel_id=int(form.hotel.data)).first()
        if existing_room:
            flash("Room No already exists!","warning")
            return redirect(url_for("add_room"))
        room=Room(
            room_no=form.room_no.data,
            hotel_id=int(form.hotel.data),
            category=form.category.data,
            capacity=form.capacity.data,
            beds=form.beds.data,
            current_price=form.current_price.data,
            floor=form.floor.data,
            room_status="AVAILABLE",
            created_by=current_user.user_id,
            updated_by=current_user.user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
            )
        try:
            db.session.add(room)
            db.session.flush()
            create_audit_log("Added Room","Room",room.room_id)
            db.session.commit()
            flash("Room added successfully","success")
            return redirect(url_for("manage_rooms"))
        except Exception as e:
            db.session.rollback()
            flash("Failed to add room. Please try again.","danger")
    return render_template("admin/add_room.html",form=form)
@app.route("/admin/rooms/<int:room_id>/edit",methods=["GET","POST"])
@login_required
def edit_room(room_id):
    if current_user.role!="admin":
        flash("Access Denied","danger")
        return redirect(url_for("home"))
    room=Room.query.get_or_404(room_id)
    form=AddRoomForm()
    hotels=Hotel.query.all()
    form.hotel.choices=[(str(hotel.hotel_id), hotel.hotel_name) for hotel in hotels]
    if form.validate_on_submit():
        existing_room=Room.query.filter_by(
            room_no=form.room_no.data,
            hotel_id=int(form.hotel.data)
        ).first()
        if existing_room and existing_room.room_id != room.room_id:
            flash("Room number already exists for the selected hotel.", "warning")
            return redirect(url_for("edit_room", room_id=room.room_id))
        room.hotel_id=int(form.hotel.data)
        room.room_no=form.room_no.data
        room.category=form.category.data
        room.capacity=form.capacity.data
        room.beds=form.beds.data
        room.current_price=form.current_price.data
        room.floor=form.floor.data
        room.updated_by=current_user.user_id
        room.updated_at=datetime.utcnow()
        try:
            create_audit_log("Updated Room","Room",room.room_id)
            db.session.commit()
            flash("Room updated successfully.", "success")
            return redirect(url_for("manage_rooms"))
        except Exception as e:
            db.session.rollback()
            flash("Failed to update room. Please try again.", "danger")
    elif request.method == "GET":
        form.hotel.data=str(room.hotel_id)
        form.room_no.data=room.room_no
        form.category.data=room.category
        form.capacity.data=room.capacity
        form.beds.data=room.beds
        form.current_price.data=room.current_price
        form.floor.data=room.floor
    return render_template("admin/edit_room.html",form=form,room=room)
@app.route("/admin/rooms/<int:room_id>")
@login_required
def room_profile(room_id):
    if current_user.role!="admin":
        flash("Access Denied","danger")
        return redirect(url_for("home"))
    room=Room.query.get_or_404(room_id)
    amenities=Amenities.query.filter_by(hotel_id=room.hotel_id,room_category=room.category).all()
    current_booking=Booking.query.filter_by(room_id=room.room_id,booking_status="CHECKED_IN").first()
    status=request.args.get("booking_status","ALL")
    search=request.args.get("search","").strip()
    sort=request.args.get("sort_by","booking_date_time")
    direction=request.args.get("direction","desc")
    page=request.args.get("page",1,type=int)
    query=Booking.query.filter_by(room_id=room.room_id)
    if status!="ALL":
        query=query.filter(Booking.booking_status==status)
    if search:
        if search.isdigit():
            query=query.filter(Booking.booking_id==int(search))
        else:
            query=query.join(Booking.user).join(User.customer_details).filter(Customer_Details.customer_name.ilike(f"%{search}%"))
    field=Booking.booking_date_time
    if sort=="booking_date_time":
        field=Booking.booking_date_time
    elif sort=="check_in_date":
        field=Booking.check_in_date
    elif sort=="price_at_booking":
        field=Booking.price_at_booking
    if direction=="asc":
        query=query.order_by(field.asc())
    else:
        query=query.order_by(field.desc())
    bookings=query.paginate(page=page,per_page=10)
    return render_template("admin/room_profile.html",
                            room=room,
                            amenities=amenities,
                            current_booking=current_booking,
                            bookings=bookings,
                            search=search,
                            selected_status=status,
                            selected_sort=sort,
                            selected_direction=direction)
@app.route("/admin/bookings")
@login_required
def manage_bookings():
    if current_user.role != "admin":
        flash("Access Denied", "danger")
        return redirect(url_for("home"))

    search = request.args.get("search", "").strip()
    status = request.args.get("booking_status", "ALL")
    page = request.args.get("page", 1, type=int)
    sort_by = request.args.get("sort_by", "booking_date_time")
    direction = request.args.get("direction", "desc")
    query = Booking.query
    if status != "ALL":
        query = query.filter(Booking.booking_status == status)
    if search:
        if search.isdigit():
            query = query.filter(Booking.booking_id == int(search))
        else:
            query = (
                query.outerjoin(Booking.user)
                .outerjoin(User.customer_details)
                .outerjoin(Guest)
                .filter(
                    Customer_Details.customer_name.ilike(f"%{search}%") |
                    Guest.guest_name.ilike(f"%{search}%")
                )
            )
    if sort_by == "booking_date_time":
        field = Booking.booking_date_time
    elif sort_by == "check_in_date":
        field = Booking.check_in_date
    elif sort_by == "price_at_booking":
        field = Booking.price_at_booking
    else:
        field = Booking.booking_date_time
    if direction == "asc":
        query = query.order_by(field.asc())
    else:
        query = query.order_by(field.desc())
    bookings = query.paginate(page=page, per_page=10)
    return render_template(
        "admin/manage_bookings.html",
        bookings=bookings,
        selected_status=status,
        search=search,
        selected_sort=sort_by,
        selected_direction=direction
    )
@app.route("/admin/manage_booking/<int:booking_id>")
@login_required
def manage_booking(booking_id):
    if current_user.role!="admin":
        flash("Access Denied","danger")
        return redirect(url_for("home"))
    booking=Booking.query.get_or_404(booking_id)
    payment=Payment.query.filter_by(
        booking_id=booking.booking_id
    ).first()
    invoice=None
    if payment:
        invoice=Invoice.query.filter_by(
            transaction_id=payment.transaction_id
        ).first()
    guest=None
    if booking.user_id is None:
        guest=Guest.query.filter_by(
            booking_id=booking.booking_id
        ).first()
    rooms=Room.query.filter_by(
        hotel_id=booking.hotel_id
    ).order_by(Room.room_no.asc()).all()
    return render_template(
        "admin/manage_booking.html",
        booking=booking,
        payment=payment,
        invoice=invoice,
        guest=guest,
        rooms=rooms
    )
@app.route("/admin/booking/<int:booking_id>/edit",methods=["GET","POST"])
@login_required
def edit_booking(booking_id):
    if current_user.role!="admin":
        flash("Access Denied","danger")
        return redirect(url_for("home"))
    booking=Booking.query.get_or_404(booking_id)
    edit_mode=True
    payment=Payment.query.filter_by(booking_id=booking.booking_id).first()
    invoice=None
    if payment:
        invoice=Invoice.query.filter_by(transaction_id=payment.transaction_id).first()
    guest=None
    if booking.user_id is None:
        guest=Guest.query.filter_by(booking_id=booking.booking_id).first()
    rooms=Room.query.filter_by(hotel_id=booking.hotel_id).order_by(Room.room_no.asc()).all()
    if booking.booking_status!="BOOKED":
        flash("Booking can only be edited before check-in.","warning")
        return redirect(url_for("manage_booking",booking_id=booking.booking_id))
    if request.method=="POST":
        check_in_date_str=request.form.get("check_in_date")
        check_out_date_str=request.form.get("check_out_date")
        number_of_people=request.form.get("number_of_people",type=int)
        room_id=request.form.get("room_id",type=int)
        try:
            check_in_date=datetime.strptime(check_in_date_str,"%Y-%m-%d").date()
            check_out_date=datetime.strptime(check_out_date_str,"%Y-%m-%d").date()
        except (ValueError, TypeError):
            flash("Invalid date format.","danger")
            return render_template("admin/manage_booking.html",booking=booking,payment=payment,invoice=invoice,guest=guest,rooms=rooms,edit_mode=True)
        if check_out_date<=check_in_date:
            flash("Check Out Date must be after Check In Date.","danger")
            return render_template("admin/manage_booking.html",booking=booking,payment=payment,invoice=invoice,guest=guest,rooms=rooms,edit_mode=True)
        if not number_of_people or number_of_people<1:
            flash("Number of people must be at least 1.","danger")
            return render_template("admin/manage_booking.html",booking=booking,payment=payment,invoice=invoice,guest=guest,rooms=rooms,edit_mode=True)
        new_room=Room.query.get(room_id) if room_id else None
        if not new_room:
            flash("Invalid room selection.","danger")
            return render_template("admin/manage_booking.html",booking=booking,payment=payment,invoice=invoice,guest=guest,rooms=rooms,edit_mode=True)
        if new_room.hotel_id!=booking.hotel_id:
            flash("Selected room does not belong to this hotel.","danger")
            return render_template("admin/manage_booking.html",booking=booking,payment=payment,invoice=invoice,guest=guest,rooms=rooms,edit_mode=True)
        if number_of_people>new_room.capacity:
            flash(f"Number of people exceeds room capacity ({new_room.capacity}).","danger")
            return render_template("admin/manage_booking.html",booking=booking,payment=payment,invoice=invoice,guest=guest,rooms=rooms,edit_mode=True)
        if new_room.room_id!=booking.room_id and new_room.room_status!="AVAILABLE":
            flash("Selected room is not available.","danger")
            return render_template("admin/manage_booking.html",booking=booking,payment=payment,invoice=invoice,guest=guest,rooms=rooms,edit_mode=True)
        try:
            if new_room.room_id!=booking.room_id:
                old_room=booking.room
                old_room.room_status="AVAILABLE"
                new_room.room_status="BOOKED"
            total_nights=(check_out_date-check_in_date).days
            subtotal=new_room.current_price*total_nights
            tax=subtotal*0.18
            discount=0
            grand_total=subtotal+tax-discount
            booking.check_in_date=check_in_date
            booking.check_out_date=check_out_date
            booking.number_of_people=number_of_people
            booking.price_at_booking=grand_total
            booking.room_id=new_room.room_id
            pay=Payment.query.filter_by(booking_id=booking.booking_id).first()
            if pay:
                pay.amount=grand_total
                inv=Invoice.query.filter_by(transaction_id=pay.transaction_id).first()
                if inv:
                    inv.tax_amount=tax
                    inv.discount_amount=discount
                    inv.final_amount=grand_total
            create_audit_log("Updated Booking","Booking",booking.booking_id)
            db.session.commit()
            flash("Booking updated successfully.","success")
            return redirect(url_for("manage_booking",booking_id=booking.booking_id))
        except Exception as e:
            print(e)
            db.session.rollback()
            flash("An error occurred while updating the booking.","danger")
    return render_template("admin/manage_booking.html",booking=booking,payment=payment,invoice=invoice,guest=guest,rooms=rooms,edit_mode=True)
@app.route("/admin/cancel_booking/<int:booking_id>")
@login_required
def admin_cancel_booking(booking_id):
    if current_user.role!="admin":
        flash("Access Denied","danger")
        return redirect(url_for("home"))
    booking=Booking.query.get_or_404(booking_id)
    if booking.booking_status!="BOOKED":
        flash("This booking cannot be cancelled as it is not in BOOKED status.","warning")
        return redirect(url_for("manage_booking",booking_id=booking.booking_id))
    try:
        booking.booking_status="CANCELLED"
        booking.room.room_status="AVAILABLE"
        payment=Payment.query.filter_by(booking_id=booking.booking_id).first()
        if payment:
            payment.payment_status="REFUNDED"
        create_audit_log("Admin Cancelled Booking","Booking",booking.booking_id)
        db.session.commit()
        flash("Booking cancelled successfully by admin.","success")
    except Exception as e:
        print(e)
        db.session.rollback()
        flash("An error occurred while cancelling the booking.","danger")
    return redirect(url_for("manage_booking",booking_id=booking.booking_id))
@app.route("/admin/book_guest/<int:room_id>",methods=["GET","POST"])
@login_required
def book_guest(room_id):
    if current_user.role!="admin":
        flash("Access Denied","danger")
        return redirect(url_for("home"))
    room=Room.query.get_or_404(room_id)
    if room.room_status!="AVAILABLE":
        flash("Room is not available.","danger")
        return redirect(url_for("book"))
    check_in_date=session.get("check_in_date")
    check_out_date=session.get("check_out_date")
    number_of_people=session.get("number_of_people")
    if check_in_date is None or check_out_date is None or number_of_people is None:
        flash("Please search for a room first.","warning")
        return redirect(url_for("book"))
    check_in_date=datetime.strptime(check_in_date,"%Y-%m-%d").date()
    check_out_date=datetime.strptime(check_out_date,"%Y-%m-%d").date()
    total_nights=(check_out_date-check_in_date).days
    if total_nights<=0:
        flash("Check Out Date must be after Check In Date.","danger")
        return redirect(url_for("book"))
    subtotal=room.current_price*total_nights
    tax=subtotal*0.18
    discount=0
    grand_total=subtotal+tax-discount
    form=GuestForm()
    if form.validate_on_submit():
        current_datetime=datetime.utcnow()
        try:
            booking=Booking(
                user_id=None,
                hotel_id=room.hotel_id,
                room_id=room.room_id,
                check_in_date=check_in_date,
                check_out_date=check_out_date,
                number_of_people=number_of_people,
                booking_status="BOOKED",
                booking_date_time=current_datetime,
                price_at_booking=grand_total
            )
            db.session.add(booking)
            db.session.flush()
            guest=Guest(
                user_id=None,
                booking_id=booking.booking_id,
                guest_name=form.guest_name.data.strip().title(),
                gender=form.gender.data,
                age=form.age.data,
                contact_number=form.contact_number.data,
                number_of_people=number_of_people
            )
            db.session.add(guest)
            payment=Payment(
                transaction_id=f"TXN{current_datetime.strftime('%Y%m%d%H%M%S')}",
                booking_id=booking.booking_id,
                transaction_date_time=current_datetime,
                amount=grand_total,
                payment_method="OFFLINE",
                payment_status="SUCCESS",
                receipt_number=f"RCPT{booking.booking_id}{current_datetime.strftime('%Y%m%d%H%M%S')}"
            )
            db.session.add(payment)
            db.session.flush()
            invoice=Invoice(
                transaction_id=payment.transaction_id,
                tax_amount=tax,
                discount_amount=discount,
                final_amount=grand_total,
                invoice_date=date.today()
            )
            db.session.add(invoice)
            room.room_status="BOOKED"
            create_audit_log("Created Guest Booking","Booking",booking.booking_id)
            db.session.commit()
            session.pop("check_in_date",None)
            session.pop("check_out_date",None)
            session.pop("number_of_people",None)
            flash("Guest booking created successfully.","success")
            return redirect(url_for("manage_booking",booking_id=booking.booking_id))
        except Exception:
            db.session.rollback()
            flash("An error occurred while creating the guest booking.","danger")
    return render_template(
        "admin/book_guest.html",
        form=form,
        room=room,
        check_in_date=check_in_date,
        check_out_date=check_out_date,
        total_nights=total_nights,
        number_of_people=number_of_people,
        subtotal=subtotal,
        tax=tax,
        discount=discount,
        grand_total=grand_total
    )
@app.route("/admin/update_guest/<int:guest_id>",methods=["GET","POST"])
@login_required
def update_guest(guest_id):
    if current_user.role!="admin":
        flash("Access Denied","danger")
        return redirect(url_for("home"))
    guest=Guest.query.get_or_404(guest_id)
    if guest.booking.booking_status!="BOOKED":
        flash("Guest details can only be updated before check in.","warning")
        return redirect(url_for("manage_booking",booking_id=guest.booking_id))
    form=GuestForm()
    if request.method=="GET":
        form.guest_name.data=guest.guest_name
        form.gender.data=guest.gender
        form.age.data=guest.age
        form.contact_number.data=guest.contact_number
        form.number_of_people.data=guest.number_of_people
    if form.validate_on_submit():
        guest.guest_name=form.guest_name.data.strip().title()
        guest.gender=form.gender.data
        guest.age=form.age.data
        guest.contact_number=form.contact_number.data
        guest.number_of_people=form.number_of_people.data
        try:
            create_audit_log("Updated Guest","Guest",guest.guest_id)
            db.session.commit()
            flash("Guest updated successfully.","success")
            return redirect(url_for("manage_booking",booking_id=guest.booking_id))
        except Exception:
            db.session.rollback()
            flash("An error occurred while updating the guest.","danger")
    return render_template(
        "admin/edit_guest.html",
        form=form,
        guest=guest
    )
@app.route("/admin/check_in/<int:booking_id>")
@login_required
def check_in_customer(booking_id):
    if current_user.role!="admin":
        flash("Access Denied","danger")
        return redirect(url_for("home"))
    booking=Booking.query.get_or_404(booking_id)
    if booking.booking_status!="BOOKED":
        flash("Customer has already checked in or booking is invalid","warning")
        return redirect(url_for("manage_bookings"))
    if booking.check_in_date>date.today():
        flash("Customer cannot be checked in before the Check In Date","warning")
        return redirect(url_for("manage_bookings"))
    try:
        booking.booking_status="CHECKED_IN"
        booking.actual_check_in_datetime=datetime.utcnow()
        booking.room.room_status="OCCUPIED"
        create_audit_log("Checked In Booking","Booking",booking.booking_id)
        db.session.commit()
        flash("Customer Checked In Successfully","success")
    except Exception as e:
        print(e)
        db.session.rollback()
        flash("An Error Occured While checking in the customer. Please try again after some time","danger")
    return redirect(url_for("manage_bookings"))
@app.route("/admin/check_out/<int:booking_id>")
@login_required
def check_out_customer(booking_id):
    if current_user.role!="admin":
        flash("Access Denied","danger")
        return redirect(url_for("home"))
    booking=Booking.query.get_or_404(booking_id)
    if booking.booking_status!="CHECKED_IN":
        flash("Customer is not currently checked in","warning")
        return redirect(url_for("manage_bookings"))
    try:
        booking.booking_status="CHECKED_OUT"
        booking.actual_check_out_datetime=datetime.utcnow()
        booking.room.room_status="AVAILABLE"
        create_audit_log("Checked Out Booking","Booking",booking.booking_id)
        db.session.commit()
        flash("Customer Checked Out Successfully","success")
    except Exception as e:
        print(e)
        db.session.rollback()
        flash("An Error Occured While checking out the customer. Please try again after some time","danger")
    return redirect(url_for("manage_bookings"))
@app.route("/admin/manage_admins")
@login_required
def manage_admins():
    if current_user.role!="admin":
        flash("Access Denied","danger")
        return redirect(url_for("home"))
    query=User.query.filter(User.role=="admin")
    search=request.args.get("search","").strip()
    selected_sort=request.args.get("sort_by","username")
    selected_direction=request.args.get("direction","asc")
    page=request.args.get("page",1,type=int)
    if search:
        if search.isdigit():
            query=query.filter(User.user_id==int(search))
        else:
            query=query.filter(
                User.username.ilike(f"%{search}%")|
                User.email.ilike(f"%{search}%")
            )
    field=User.username
    if selected_sort=="created_date_time":
        field=User.created_date_time
    elif selected_sort=="user_id":
        field=User.user_id
    if selected_direction=="asc":
        query=query.order_by(field.asc())
    else:
        query=query.order_by(field.desc())
    admins=query.paginate(page=page,per_page=10)
    return render_template(
        "admin/manage_users.html",
        users=admins,
        search=search,
        selected_sort=selected_sort,
        selected_direction=selected_direction
    )
@app.route("/admin/manage_admin/<int:user_id>")
@login_required
def manage_admin(user_id):
    if current_user.role!="admin":
        flash("Access Denied","danger")
        return redirect(url_for("home"))
    admin_user=User.query.get_or_404(user_id)
    if admin_user.role!="admin":
        flash("User is not an admin.","warning")
        return redirect(url_for("manage_admins"))
    return render_template(
        "admin/manage_user.html",
        user=admin_user
    )
@app.route("/admin/add_admin",methods=["GET","POST"])
@login_required
def add_admin():
    if current_user.role!="admin":
        flash("Access Denied","danger")
        return redirect(url_for("home"))
    form=CreateAdminForm()
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        admin_user=User(
            username=form.username.data,
            password=hashed_password,
            email=form.email.data,
            role="admin"
        )
        try:
            db.session.add(admin_user)
            db.session.flush()
            customer=Customer_Details(
                user_id=admin_user.user_id,
                customer_name=form.name.data,
                gender="Other",
                date_of_birth=date.today(),
                contact_number=form.contact_number.data,
                address="Admin User"
            )
            db.session.add(customer)
            db.session.flush()
            create_audit_log("Created Admin","User",admin_user.user_id)
            db.session.commit()
            flash(f"Admin '{form.username.data}' created successfully.","success")
            return redirect(url_for("manage_admins"))
        except Exception as e:
            print(e)
            db.session.rollback()
            flash("Failed to create admin. Please try again.","danger")
    admin_query=User.query.filter(User.role=="admin").order_by(User.username.asc())
    admins=admin_query.paginate(page=1,per_page=10)
    return render_template("admin/manage_users.html",form=form,show_add_form=True,users=admins,search="",selected_sort="username",selected_direction="asc",selected_status="ALL")
@app.route("/admin/make_admin/<int:user_id>",methods=["POST"])
@login_required
def make_admin(user_id):
    if current_user.role!="admin":
        flash("Access Denied","danger")
        return redirect(url_for("home"))
    user=User.query.get_or_404(user_id)
    if user.role=="admin":
        flash("User is already an admin.","warning")
        return redirect(url_for("manage_user",user_id=user.user_id))
    try:
        user.role="admin"
        create_audit_log("Promoted to Admin","User",user.user_id)
        db.session.commit()
        flash(f"User '{user.username}' has been promoted to admin.","success")
    except Exception:
        db.session.rollback()
        flash("An error occurred while promoting the user.","danger")
    return redirect(url_for("manage_user",user_id=user.user_id))
@app.route("/admin/demote_admin/<int:user_id>",methods=["POST"])
@login_required
def demote_admin(user_id):
    if current_user.role!="admin":
        flash("Access Denied","danger")
        return redirect(url_for("home"))
    admin_user=User.query.get_or_404(user_id)
    if admin_user.role!="admin":
        flash("User is not an admin.","warning")
        return redirect(url_for("manage_admins"))
    if admin_user.user_id==current_user.user_id:
        flash("You cannot demote your own account.","danger")
        return redirect(url_for("manage_admin",user_id=admin_user.user_id))
    try:
        admin_user.role="customer"
        create_audit_log("Demoted from Admin","User",admin_user.user_id)
        db.session.commit()
        flash(f"Admin '{admin_user.username}' has been demoted to customer.","success")
    except Exception:
        db.session.rollback()
        flash("An error occurred while demoting the admin.","danger")
    return redirect(url_for("manage_admins"))
@app.route("/admin/manage_users")
@login_required
def manage_users():
    if current_user.role!="admin":
        flash("Access Denied","danger")
        return redirect(url_for("home"))
    query=User.query.join(User.customer_details)
    query=query.filter(User.role=="customer")
    search=request.args.get("search","").strip()
    selected_status=request.args.get("account_status","ALL")
    selected_sort=request.args.get("sort_by","username")
    selected_direction=request.args.get("direction","asc")
    page=request.args.get("page",1,type=int)
    if search:
        if search.isdigit():
            query=query.filter(User.user_id==int(search))
        else:
            query=query.filter(
                User.username.ilike(f"%{search}%")|
                User.email.ilike(f"%{search}%")|
                Customer_Details.customer_name.ilike(f"%{search}%")
            )
    if selected_status!="ALL":
        query=query.filter(User.account_status==selected_status)
    if selected_sort=="customer_name":
        field=Customer_Details.customer_name
    elif selected_sort=="created_date_time":
        field=User.created_date_time
    else:
        field=User.username
    if selected_direction=="asc":
        query=query.order_by(field.asc())
    else:
        query=query.order_by(field.desc())
    users=query.paginate(page=page,per_page=10)
    return render_template(
        "admin/manage_users.html",
        users=users,
        search=search,
        selected_status=selected_status,
        selected_sort=selected_sort,
        selected_direction=selected_direction
    )
@app.route("/admin/manage_user/<int:user_id>")
@login_required
def manage_user(user_id):
    if current_user.role!="admin":
        flash("Access Denied","danger")
        return redirect(url_for("home"))
    user=User.query.get_or_404(user_id)
    total_bookings=Booking.query.filter_by(user_id=user.user_id).count()
    active_bookings=Booking.query.filter(
        Booking.user_id==user.user_id,
        Booking.booking_status.in_(["BOOKED","CHECKED_IN"])
    ).count()
    completed_bookings=Booking.query.filter_by(
        user_id=user.user_id,
        booking_status="CHECKED_OUT"
    ).count()
    cancelled_bookings=Booking.query.filter_by(
        user_id=user.user_id,
        booking_status="CANCELLED"
    ).count()
    total_reviews=Review.query.filter_by(user_id=user.user_id).count()
    total_complaints=Complaint.query.filter_by(user_id=user.user_id).count()
    total_payments=Payment.query.join(Booking).filter(
        Booking.user_id==user.user_id
    ).count()
    return render_template(
        "admin/manage_user.html",
        user=user,
        total_bookings=total_bookings,
        active_bookings=active_bookings,
        completed_bookings=completed_bookings,
        cancelled_bookings=cancelled_bookings,
        total_reviews=total_reviews,
        total_complaints=total_complaints,
        total_payments=total_payments
    )
@app.route("/admin/block_user/<int:user_id>",methods=["POST"])
@login_required
def block_user(user_id):
    if current_user.role!="admin":
        flash("Access Denied","danger")
        return redirect(url_for("home"))
    user=User.query.get_or_404(user_id)
    if user.role=="admin":
        flash("Admin accounts cannot be blocked.","danger")
        return redirect(url_for("manage_user",user_id=user.user_id))
    if user.user_id==current_user.user_id:
        flash("You cannot block your own account.","danger")
        return redirect(url_for("manage_user",user_id=user.user_id))
    active_booking=Booking.query.filter(
        Booking.user_id==user.user_id,
        Booking.booking_status.in_(["BOOKED","CHECKED_IN"])
    ).first()
    if active_booking:
        flash("User has an active booking. Cannot block the account.","warning")
        return redirect(url_for("manage_user",user_id=user.user_id))
    try:
        user.account_status="BLOCKED"
        create_audit_log("Blocked User","User",user.user_id)
        db.session.commit()
        flash("User blocked successfully.","success")
    except Exception:
        db.session.rollback()
        flash("An error occurred while blocking the user.","danger")
    return redirect(url_for("manage_user",user_id=user.user_id))
@app.route("/admin/unblock_user/<int:user_id>",methods=["POST"])
@login_required
def unblock_user(user_id):
    if current_user.role!="admin":
        flash("Access Denied","danger")
        return redirect(url_for("home"))
    user=User.query.get_or_404(user_id)
    if user.role=="admin":
        flash("Admin accounts cannot be modified.","danger")
        return redirect(url_for("manage_user",user_id=user.user_id))
    if user.user_id==current_user.user_id:
        flash("You cannot modify your own account.","danger")
        return redirect(url_for("manage_user",user_id=user.user_id))
    try:
        user.account_status="ACTIVE"
        create_audit_log("Unblocked User","User",user.user_id)
        db.session.commit()
        flash("User unblocked successfully.","success")
    except Exception:
        db.session.rollback()
        flash("An error occurred while unblocking the user.","danger")
    return redirect(url_for("manage_user",user_id=user.user_id))
@app.route("/admin/manage_reviews")
@login_required
def manage_reviews():
    if current_user.role!="admin":
        flash("Access Denied","danger")
        return redirect(url_for("home"))
    query=Review.query.join(Review.user).join(User.customer_details).join(Review.booking)
    search=request.args.get("search","").strip()
    selected_rating=request.args.get("rating","ALL")
    selected_visibility=request.args.get("visibility","ALL")
    selected_sort=request.args.get("sort_by","review_datetime")
    selected_direction=request.args.get("direction","desc")
    page=request.args.get("page",1,type=int)
    if search:
        if search.isdigit():
            query=query.filter(
                (Review.review_id==int(search))|
                (Review.booking_id==int(search))
            )
        else:
            query=query.filter(
                Customer_Details.customer_name.ilike(f"%{search}%")
            )
    if selected_rating!="ALL":
        query=query.filter(Review.rating==int(selected_rating))
    if selected_visibility!="ALL":
        query=query.filter(Review.review_visibility==selected_visibility)
    if selected_sort=="rating":
        field=Review.rating
    else:
        field=Review.review_datetime
    if selected_direction=="asc":
        query=query.order_by(field.asc())
    else:
        query=query.order_by(field.desc())
    reviews=query.paginate(page=page,per_page=10)
    return render_template(
        "admin/manage_reviews.html",
        reviews=reviews,
        search=search,
        selected_rating=selected_rating,
        selected_visibility=selected_visibility,
        selected_sort=selected_sort,
        selected_direction=selected_direction
    )
@app.route("/admin/hide_review/<int:review_id>",methods=["POST"])
@login_required
def hide_review(review_id):
    if current_user.role!="admin":
        flash("Access Denied","danger")
        return redirect(url_for("home"))
    review=Review.query.get_or_404(review_id)
    if review.review_visibility=="HIDDEN":
        flash("Review is already hidden.","warning")
        return redirect(url_for("manage_reviews"))
    try:
        review.review_visibility="HIDDEN"
        create_audit_log("Hidden Review","Review",review.review_id)
        db.session.commit()
        flash("Review hidden successfully.","success")
    except Exception:
        db.session.rollback()
        flash("An error occurred while hiding the review.","danger")
    return redirect(url_for("manage_reviews"))
@app.route("/admin/show_review/<int:review_id>",methods=["POST"])
@login_required
def show_review(review_id):
    if current_user.role!="admin":
        flash("Access Denied","danger")
        return redirect(url_for("home"))
    review=Review.query.get_or_404(review_id)
    if review.review_visibility=="VISIBLE":
        flash("Review is already visible.","warning")
        return redirect(url_for("manage_reviews"))
    try:
        review.review_visibility="VISIBLE"
        create_audit_log("Visible Review","Review",review.review_id)
        db.session.commit()
        flash("Review is now visible to customers.","success")
    except Exception:
        db.session.rollback()
        flash("An error occurred while showing the review.","danger")
    return redirect(url_for("manage_reviews"))
@app.route("/admin/manage_complaints")
@login_required
def manage_complaints():
    if current_user.role!="admin":
        flash("Access Denied","danger")
        return redirect(url_for("home"))
    query=Complaint.query.join(Complaint.user).join(User.customer_details).join(Complaint.booking)
    selected_status=request.args.get("complaint_status","ALL")
    search=request.args.get("search","").strip()
    selected_sort=request.args.get("sort_by","complaint_datetime")
    selected_direction=request.args.get("direction","desc")
    page=request.args.get("page",1,type=int)
    field=Complaint.complaint_datetime
    if selected_status!="ALL":
        query=query.filter(Complaint.complaint_status==selected_status)
    if search:
        if search.isdigit():
            query=query.filter(
                (Complaint.complaint_id==int(search))|
                (Complaint.booking_id==int(search))
            )
        else:
            query=query.filter(
                Customer_Details.customer_name.ilike(f"%{search}%")
            )
    if selected_sort=="complaint_datetime":
        field=Complaint.complaint_datetime
    if selected_direction=="asc":
        query=query.order_by(field.asc())
    else:
        query=query.order_by(field.desc())
    complaints=query.paginate(page=page,per_page=10)
    return render_template(
        "admin/manage_complaints.html",
        complaints=complaints,
        selected_status=selected_status,
        search=search,
        selected_sort=selected_sort,
        selected_direction=selected_direction
    )
@app.route("/admin/manage_complaint/<int:complaint_id>")
@login_required
def manage_complaint(complaint_id):
    if current_user.role!="admin":
        flash("Access Denied","danger")
        return redirect(url_for("home"))
    complaint=Complaint.query.get_or_404(complaint_id)
    return render_template(
        "admin/manage_complaint.html",
        complaint=complaint
    )
@app.route("/admin/resolve_complaint/<int:complaint_id>",methods=["GET","POST"])
@login_required
def resolve_complaint(complaint_id):
    if current_user.role!="admin":
        flash("Access Denied","danger")
        return redirect(url_for("home"))
    complaint=Complaint.query.get_or_404(complaint_id)
    if complaint.complaint_status=="RESOLVED":
        flash("Complaint has already been resolved.","warning")
        return redirect(url_for("manage_complaint",complaint_id=complaint.complaint_id))
    if request.method=="POST":
        resolution_details=request.form.get("resolution_details","").strip()
        if not resolution_details:
            flash("Resolution details are required.","danger")
            return render_template(
                "admin/resolve_complaint.html",
                complaint=complaint
            )
        try:
            complaint.resolution_details=resolution_details
            complaint.complaint_status="RESOLVED"
            create_audit_log("Resolved Complaint","Complaint",complaint.complaint_id)
            db.session.commit()
            flash("Complaint resolved successfully.","success")
            return redirect(url_for("manage_complaint",complaint_id=complaint.complaint_id))
        except Exception:
            db.session.rollback()
            flash("An error occurred while resolving the complaint.","danger")
    return render_template(
        "admin/resolve_complaint.html",
        complaint=complaint
    )
@app.route("/admin/manage_contact_messages")
@login_required
def manage_contact_messages():
    if current_user.role!="admin":
        flash("Access Denied","danger")
        return redirect(url_for("home"))
    query=ContactMessage.query
    search=request.args.get("search","").strip()
    selected_sort=request.args.get("sort_by","date_time")
    selected_direction=request.args.get("direction","desc")
    page=request.args.get("page",1,type=int)
    if search:
        if search.isdigit():
            query=query.filter(
                ContactMessage.message_id==int(search)
            )
        else:
            query=query.filter(
                ContactMessage.name.ilike(f"%{search}%")|
                ContactMessage.email.ilike(f"%{search}%")|
                ContactMessage.contact_number.ilike(f"%{search}%")
            )
    if selected_sort=="name":
        field=ContactMessage.name
    else:
        field=ContactMessage.date_time
    if selected_direction=="asc":
        query=query.order_by(field.asc())
    else:
        query=query.order_by(field.desc())
    messages=query.paginate(page=page,per_page=10)
    return render_template(
        "admin/manage_contact_messages.html",
        messages=messages,
        search=search,
        selected_sort=selected_sort,
        selected_direction=selected_direction
    )
@app.route("/admin/manage_contact_message/<int:message_id>")
@login_required
def manage_contact_message(message_id):
    if current_user.role!="admin":
        flash("Access Denied","danger")
        return redirect(url_for("home"))
    message=ContactMessage.query.get_or_404(message_id)
    return render_template(
        "admin/manage_contact_message.html",
        message=message
    )
@app.route("/admin/manage_audit_logs")
@login_required
def manage_audit_logs():
    if current_user.role!="admin":
        flash("Access Denied","danger")
        return redirect(url_for("home"))
    query=AuditLog.query.join(AuditLog.user)
    search=request.args.get("search","").strip()
    selected_sort=request.args.get("sort_by","action_datetime")
    selected_direction=request.args.get("direction","desc")
    page=request.args.get("page",1,type=int)
    if search:
        if search.isdigit():
            query=query.filter(AuditLog.log_id==int(search))
        else:
            query=query.filter(
                User.username.ilike(f"%{search}%")|
                AuditLog.action_performed.ilike(f"%{search}%")|
                AuditLog.table_name.ilike(f"%{search}%")
            )
    if selected_sort=="username":
        field=User.username
    elif selected_sort=="table_name":
        field=AuditLog.table_name
    else:
        field=AuditLog.action_datetime
    if selected_direction=="asc":
        query=query.order_by(field.asc())
    else:
        query=query.order_by(field.desc())
    logs=query.paginate(page=page,per_page=10)
    return render_template(
        "admin/manage_audit_logs.html",
        logs=logs,
        search=search,
        selected_sort=selected_sort,
        selected_direction=selected_direction
    )
@app.route("/admin/audit_log/<int:log_id>")
@login_required
def audit_log_profile(log_id):
    if current_user.role!="admin":
        flash("Access Denied","danger")
        return redirect(url_for("home"))
    log=AuditLog.query.get_or_404(log_id)
    return render_template(
        "admin/audit_log_profile.html",
        log=log
    )
def create_audit_log(action,table,record_id):
    log=AuditLog(
        user_id=current_user.user_id,
        action_performed=action,
        table_name=table,
        record_id=record_id,
        action_datetime=datetime.utcnow()
    )
    db.session.add(log)