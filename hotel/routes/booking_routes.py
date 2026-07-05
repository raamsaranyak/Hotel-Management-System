from . import *
@app.route("/book",methods=["GET","POST"])
@login_required
def book():
    form=HotelSearchForm()
    hotels=None
    min_date=date.today().isoformat()
    max_date=(date.today()+timedelta(days=90)).isoformat()
    if form.validate_on_submit():
        session["check_in_date"]=form.check_in_date.data.isoformat()
        session["check_out_date"]=form.check_out_date.data.isoformat()
        session["number_of_people"]=form.number_of_people.data
        return redirect(url_for("book",category=form.category.data))
    category=request.args.get("category")
    if "check_in_date" in session:
        form.check_in_date.data=date.fromisoformat(session["check_in_date"])
    if "check_out_date" in session:
        form.check_out_date.data=date.fromisoformat(session["check_out_date"])
    if "number_of_people" in session:
        form.number_of_people.data=session["number_of_people"]
    # Read filter/sort params from GET
    min_price=request.args.get("min_price",type=float)
    max_price=request.args.get("max_price",type=float)
    beds=request.args.get("beds","")
    sort_by=request.args.get("sort_by","name")
    direction=request.args.get("direction","asc")
    
    if category is not None:
        form.category.data=category
        
        # Build query with filters
        needs_room=(category!="" or min_price is not None or max_price is not None or beds!="" or sort_by=="price")
        
        query=Hotel.query
        if needs_room:
            query=query.join(Room,Hotel.hotel_id==Room.hotel_id)
        
        if category!="":
            query=query.filter(Room.category==category)
        if min_price is not None:
            query=query.filter(Room.current_price>=min_price)
        if max_price is not None:
            query=query.filter(Room.current_price<=max_price)
        if beds!="":
            query=query.filter(Room.beds==beds)
        
        if sort_by=="name":
            query=query.order_by(Hotel.hotel_name.asc() if direction=="asc" else Hotel.hotel_name.desc())
        elif sort_by=="price":
            query=query.order_by(Room.current_price.asc() if direction=="asc" else Room.current_price.desc())
        
        hotels=query.distinct().all()
    
    # Store filter values for template
    selected_beds=beds if beds else "Any"
    
    return render_template(
        "booking/book.html",
        form=form,
        hotels=hotels,
        min_date=min_date,
        max_date=max_date,
        min_price=min_price or "",
        max_price=max_price or "",
        selected_beds=selected_beds,
        selected_category=category if category else "ALL",
        selected_sort=sort_by,
        selected_direction=direction
    )
@app.route("/rooms/<int:hotel_id>",methods=["GET"])
@login_required
def hotel_rooms(hotel_id):
    hotel=Hotel.query.get_or_404(hotel_id)
    
    # Read filter/sort params from GET (also handles modify search since it's a GET form)
    check_in=request.args.get("check_in_date")
    check_out=request.args.get("check_out_date")
    num_people=request.args.get("number_of_people")
    if check_in:
        session["check_in_date"]=check_in
    if check_out:
        session["check_out_date"]=check_out
    if num_people:
        session["number_of_people"]=int(num_people)
    
    category=request.args.get("category","")
    min_price=request.args.get("min_price",type=float)
    max_price=request.args.get("max_price",type=float)
    beds=request.args.get("beds","Any")
    sort_by=request.args.get("sort_by","random")
    direction=request.args.get("direction","asc")
    people=request.args.get("people","Any")
    
    # Build rooms query with filters
    query=Room.query.filter_by(hotel_id=hotel_id)
    
    if category and category!="":
        query=query.filter(Room.category==category)
    if min_price is not None:
        query=query.filter(Room.current_price>=min_price)
    if max_price is not None:
        query=query.filter(Room.current_price<=max_price)
    if beds!="Any" and beds!="":
        query=query.filter(Room.beds==beds)
    if people!="Any" and people!="":
        query=query.filter(Room.capacity>=int(people))
    
    # Apply sorting
    if sort_by=="price":
        order_field=Room.current_price
    elif sort_by=="capacity":
        order_field=Room.capacity
    elif sort_by=="room_no":
        order_field=Room.room_no
    else:
        order_field=func.random()
    
    if sort_by!="random":
        if direction=="desc":
            query=query.order_by(order_field.desc())
        else:
            query=query.order_by(order_field.asc())
    else:
        query=query.order_by(order_field)
    
    rooms=query.all()
    
    # Store selected filer values for template
    selected_beds=beds if beds!="Any" else ""
    if selected_beds=="":
        selected_beds="Any"
    
    return render_template(
        "booking/book_room.html",
        hotel=hotel,
        rooms=rooms,
        min_price=min_price or 1000,
        max_price=max_price or 12400,
        selected_category=category if category else "ALL",
        selected_beds=selected_beds,
        selected_people=people if people!="Any" else "Any",
        selected_sort=sort_by,
        selected_direction=direction
    )
@app.route("/book_room/<int:room_id>",methods=["GET","POST"])
@login_required
def book_room(room_id):
    room=Room.query.get_or_404(room_id)
    if room.room_status!="AVAILABLE":
        flash("Room is not available","danger")
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
    subtotal=room.current_price*total_nights
    tax=subtotal*0.18
    discount=0
    coupon_message=None
    if request.method=="POST":
        if "apply_coupon" in request.form:
            coupon_code=request.form.get("coupon_code").strip()
            if coupon_code:
                coupon_message="Coupon feature will be implemented soon."
            else:
                coupon_message="Please enter a coupon code."
        elif "pay_now" in request.form:
            if request.form.get("agree_terms")==None:
                flash("Please accept the booking policies.","warning")
            else:
                return redirect(url_for("confirm_booking",room_id=room.room_id))
    grand_total=subtotal+tax-discount
    amenities=Amenities.query.filter_by(hotel_id=room.hotel_id,room_category=room.category).all()
    return render_template(
        "booking/booking_summary.html",
        room=room,
        amenities=amenities,
        check_in_date=check_in_date,
        check_out_date=check_out_date,
        total_nights=total_nights,
        number_of_people=number_of_people,
        subtotal=subtotal,
        tax=tax,
        discount=discount,
        grand_total=grand_total,
        coupon_message=coupon_message,
        current_datetime=datetime.utcnow()
    )
@app.route("/confirm_booking/<int:room_id>",methods=["GET","POST"])
@login_required
def confirm_booking(room_id):
    room=Room.query.get_or_404(room_id)
    if room.room_status!="AVAILABLE":
        flash("Room is not available","danger")
        return redirect(url_for("book"))
    if session.get("check_in_date")==None or session.get("check_out_date")==None or session.get("number_of_people")==None:
        flash("Please search for a room before booking.","warning")
        return redirect(url_for("book"))
    existing_booking=Booking.query.filter_by(
        room_id=room.room_id,
        booking_status="BOOKED"
    ).first()
    if existing_booking:
        flash("This room has already been booked.","warning")
        return redirect(url_for("book"))
    check_in_date=datetime.strptime(session.get("check_in_date"),"%Y-%m-%d").date()
    check_out_date=datetime.strptime(session.get("check_out_date"),"%Y-%m-%d").date()
    total_nights=(check_out_date-check_in_date).days
    if total_nights<=0:
        flash("Check Out Date must be after Check In Date.","danger")
        return redirect(url_for("book"))
    subtotal=room.current_price*total_nights
    tax=subtotal*0.18
    discount=0
    grand_total=subtotal+tax-discount
    current_datetime=datetime.utcnow()
    try:
        booking=Booking(
            user_id=current_user.user_id,
            hotel_id=room.hotel_id,
            room_id=room.room_id,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            number_of_people=session.get("number_of_people"),
            booking_status="BOOKED",
            booking_date_time=current_datetime,
            price_at_booking=grand_total
        )
        db.session.add(booking)
        db.session.flush()
        payment=Payment(
            transaction_id=f"TXN{current_datetime.strftime('%Y%m%d%H%M%S')}",
            booking_id=booking.booking_id,
            transaction_date_time=current_datetime,
            amount=grand_total,
            payment_method="ONLINE",
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
        room.room_status="BOOKED"
        db.session.add(invoice)
        db.session.commit()
        booking_id=booking.booking_id
        session.pop("check_in_date",None)
        session.pop("check_out_date",None)
        session.pop("number_of_people",None)
        flash("Room Booked Successfully","success")
        return redirect(url_for("booking_success",booking_id=booking.booking_id))
    except Exception as e:
        print(e)
        db.session.rollback()
        flash("An Error Occured While booking. Please try again after some time","danger")
        return redirect(url_for("book_room",room_id=room.room_id))
@app.route("/booking_success/<int:booking_id>")
@login_required
def booking_success(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != current_user.user_id:
        flash("Unauthorized Access", "danger")
        return redirect(url_for("booking_history"))
    payment = Payment.query.filter_by(booking_id=booking.booking_id).first()
    invoice = None
    if payment:
        invoice = Invoice.query.filter_by(transaction_id=payment.transaction_id).first()
    return render_template(
        "booking/booking_success.html",
        booking=booking,
        payment=payment,
        invoice=invoice
    )
@app.route("/cancel_booking/<int:booking_id>")
@login_required
def cancel_booking(booking_id):
    booking=Booking.query.get_or_404(booking_id)
    if booking.user_id!=current_user.user_id:
        flash("Unauthorized Access","danger")
        return redirect(url_for("booking_history"))
    if booking.booking_status!="BOOKED":
        flash("This booking cannot be cancelled","warning")
        return redirect(url_for("booking_history"))
    if booking.check_in_date<=date.today():
        flash("Booking cannot be cancelled on or after Check In Date","warning")
        return redirect(url_for("booking_history"))
    try:
        booking.booking_status="CANCELLED"
        booking.room.room_status="AVAILABLE"
        payment=Payment.query.filter_by(booking_id=booking.booking_id).first()
        if payment:
            payment.payment_status="REFUNDED"
        db.session.commit()
        flash("Booking Cancelled Successfully","success")
    except Exception as e:
        print(e)
        db.session.rollback()
        flash("An Error Occured While cancelling the booking. Please try again after some time","danger")
    return redirect(url_for("booking_history"))
@app.route("/booking_history")
@login_required
def booking_history():
    query=Booking.query.filter_by(user_id=current_user.user_id)
    search=request.args.get("search","").strip()
    selected_status=request.args.get("booking_status","ALL")
    selected_sort=request.args.get("sort_by","booking_date_time")
    selected_direction=request.args.get("direction","desc")
    page=request.args.get("page",1,type=int)
    if selected_status!="ALL":
        query=query.filter(Booking.booking_status==selected_status)
    if search:
        if search.isdigit():
            query=query.filter(Booking.booking_id==int(search))
        else:
            query=query.join(Booking.room).filter(Room.room_no==search)
    if selected_sort=="check_in_date":
        field=Booking.check_in_date
    elif selected_sort=="price_at_booking":
        field=Booking.price_at_booking
    else:
        field=Booking.booking_date_time
    if selected_direction=="asc":
        query=query.order_by(field.asc())
    else:
        query=query.order_by(field.desc())
    bookings=query.paginate(page=page,per_page=10)
    return render_template(
        "booking/booking_history.html",
        bookings=bookings,
        search=search,
        selected_status=selected_status,
        selected_sort=selected_sort,
        selected_direction=selected_direction
    )