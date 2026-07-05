from . import *
@app.route("/profile",methods=["GET","POST"])
@login_required
def profile():
    form=AccountForm()
    if request.method=="GET":
        form.username.data=current_user.username
        form.email.data=current_user.email
        form.customer_name.data=current_user.customer_details.customer_name
        form.gender.data=current_user.customer_details.gender
        form.date_of_birth.data=current_user.customer_details.date_of_birth
        form.contact_number.data=current_user.customer_details.contact_number
        form.address.data=current_user.customer_details.address
    elif request.method=="POST":
        form.username.data=current_user.username
        form.gender.data=current_user.customer_details.gender
        form.date_of_birth.data=current_user.customer_details.date_of_birth
    if form.validate_on_submit():
        current_user.email=form.email.data
        current_user.customer_details.customer_name=form.customer_name.data
        current_user.customer_details.contact_number=form.contact_number.data
        current_user.customer_details.address=form.address.data
        db.session.commit()
        flash("Update successful","success")
        return redirect(url_for("profile"))
    return render_template("customer/profile.html",form=form)
@app.route("/rooms", methods=["GET"])
def rooms():
    query = Room.query
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    category = request.args.get("category", "ALL")
    beds = request.args.get("beds", "Any")
    people = request.args.get("people", "Any")
    sort_by = request.args.get("sort_by", "random")
    direction = request.args.get("direction", "asc")
    print(f"sort_by = {sort_by}")
    print(f"direction = {direction}")
    page = request.args.get("page", 1, type=int)
    if min_price is not None:
        query = query.filter(Room.current_price >= min_price)
    if max_price is not None:
        query = query.filter(Room.current_price <= max_price)
    if category != "ALL":
        query = query.filter(Room.category == category)
    if beds != "Any":
        query = query.filter(Room.beds == beds)
    if people != "Any":
        query = query.filter(Room.capacity >= int(people))
    if sort_by == "price":
        order_field = Room.current_price
    elif sort_by == "capacity":
        order_field = Room.capacity
    else:
        order_field = func.random()
    if sort_by != "random":
        if direction == "desc":
            query = query.order_by(order_field.desc())
        else:
            query = query.order_by(order_field.asc())
    else:
        query = query.order_by(order_field)
    rooms_pagination = query.paginate(page=page, per_page=15, error_out=False)
    return render_template(
        "customer/rooms_catalog.html",
        rooms=rooms_pagination,
        min_price=min_price or 1000,
        max_price=max_price or 12400,
        selected_category=category,
        selected_beds=beds,
        selected_people=people,
        selected_sort=sort_by,
        selected_direction=direction
    )
@app.route("/about")
def about():
    return render_template("customer/about.html")
@app.route("/services")
def services():
    return render_template("customer/services.html")
@app.route("/review",methods=["GET","POST"])
@login_required
def review():
    form=ReviewForm()
    reviews=Review.query.filter_by(review_visibility="VISIBLE").order_by(Review.review_datetime.desc()).all()
    my_reviews=Review.query.filter_by(user_id=current_user.user_id).order_by(Review.review_datetime.desc()).all()
    average_rating=(db.session.query(db.func.avg(Review.rating)).filter_by(review_visibility="VISIBLE").scalar() or 0)
    five_star_count=Review.query.filter_by(rating=5, review_visibility="VISIBLE").count()
    four_star_count=Review.query.filter_by(rating=4, review_visibility="VISIBLE").count()
    three_star_count=Review.query.filter_by(rating=3, review_visibility="VISIBLE").count()
    two_star_count=Review.query.filter_by(rating=2, review_visibility="VISIBLE").count()
    one_star_count=Review.query.filter_by(rating=1, review_visibility="VISIBLE").count()
    completed_booking=Booking.query.filter_by(
        user_id=current_user.user_id,
        booking_status="CHECKED_OUT"
    ).first()
    if form.validate_on_submit():
        if completed_booking is None:
            flash("You can review only after completing a stay","danger")
            return redirect(url_for("review"))
        if my_reviews:
            flash("You have already submitted a review for your account. Only one review per user is allowed.", "danger")
            return redirect(url_for("review"))
        review_obj=Review(
            user_id=current_user.user_id,
            booking_id=completed_booking.booking_id,
            rating=int(form.rating.data),
            review_text=form.review_text.data,
            review_datetime=datetime.utcnow()
        )
        try:
            db.session.add(review_obj)
            db.session.commit()
            flash("Review submitted successfully","success")
        except Exception:
            db.session.rollback()
            flash("Review submission failed","danger")
        return redirect(url_for("review"))
    return render_template(
        "customer/reviews.html",
        form=form,
        reviews=reviews,
        my_reviews=my_reviews,
        average_rating=round(average_rating,1),
        five_star_count=five_star_count,
        four_star_count=four_star_count,
        three_star_count=three_star_count,
        two_star_count=two_star_count,
        one_star_count=one_star_count
    )
@app.route("/submit_complaint/<int:booking_id>",methods=["GET","POST"])
@login_required
def submit_complaint(booking_id):
    booking=Booking.query.get_or_404(booking_id)
    if booking.user_id!=current_user.user_id:
        flash("Access Denied","danger")
        return redirect(url_for("home"))
    if booking.booking_status=="CANCELLED":
        flash("Complaints cannot be submitted for cancelled bookings.","warning")
        return redirect(url_for("booking_history"))
    existing_complaint=Complaint.query.filter_by(booking_id=booking.booking_id).first()
    if existing_complaint:
        flash("Complaint has already been submitted for this booking.","warning")
        return redirect(url_for("my_complaints"))
    form=ComplaintForm()
    if form.validate_on_submit():
        complaint=Complaint(
            user_id=current_user.user_id,
            booking_id=booking.booking_id,
            complaint_text=form.complaint_text.data.strip().capitalize(),
            complaint_datetime=datetime.utcnow(),
            complaint_status="OPEN"
        )
        try:
            db.session.add(complaint)
            db.session.commit()
            flash("Complaint submitted successfully.","success")
            return redirect(url_for("my_complaints"))
        except Exception:
            db.session.rollback()
            flash("An error occurred while submitting the complaint.","danger")
    return render_template(
        "customer/submit_complaint.html",
        form=form,
        booking=booking
    )
@app.route("/my_complaints")
@login_required
def my_complaints():
    query=Complaint.query.filter_by(user_id=current_user.user_id)
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
    if selected_sort=="complaint_datetime":
        field=Complaint.complaint_datetime
    if selected_direction=="asc":
        query=query.order_by(field.asc())
    else:
        query=query.order_by(field.desc())
    complaints=query.paginate(page=page,per_page=10)
    return render_template(
        "customer/my_complaints.html",
        complaints=complaints,
        selected_status=selected_status,
        search=search,
        selected_sort=selected_sort,
        selected_direction=selected_direction
    )
@app.route("/complaint/<int:complaint_id>")
@login_required
def complaint_profile(complaint_id):
    complaint=Complaint.query.get_or_404(complaint_id)
    if complaint.user_id!=current_user.user_id:
        flash("Access Denied","danger")
        return redirect(url_for("home"))
    return render_template(
        "customer/complaint_profile.html",
        complaint=complaint
    )