from . import *
@app.route('/',methods=["GET","POST"])
def home():
    form=ContactForm()
    if form.validate_on_submit():
        messages=ContactMessage(name=form.name.data,
                                contact_number=form.contact_number.data,
                                email=form.email.data,
                                message=form.message.data
                                )
        try:
            db.session.add(messages)
            db.session.commit()
            flash("Message has been sent successfully.","success")
            return redirect(url_for("home"))
        except Exception as e:
            db.session.rollback()
            flash("Failed to send message, please try again after some time","danger")
    return render_template("home.html",form=form)
@app.route("/register",methods=["GET","POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form=RegistrationForm()
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user=User(username=form.username.data,password=hashed_password,email=form.email.data)
        try:
            db.session.add(user)
            db.session.flush()
            customer=Customer_Details(user_id=user.user_id,
                                    customer_name=form.customer_name.data,
                                    gender=form.gender.data,
                                    date_of_birth=form.date_of_birth.data,
                                    contact_number=form.contact_number.data,
                                    address=form.address.data)
            db.session.add(customer)
            db.session.commit()
            flash("Registration Successful","success")
        except Exception:
            db.session.rollback()
            flash("Registration failed. Please try again.","danger")
            return redirect(url_for("register"))
        return redirect(url_for("login"))
    return render_template("authentication/registration.html",form=form)
@app.route("/login",methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.username.data).first()
        if user is None:
            flash("User Doesn't exist Please register First","danger")
            return redirect(url_for("register"))
        elif bcrypt.check_password_hash(user.password,form.password.data):
            flash("Login Successful","success")
            login_user(user, remember=form.remember.data)
            return redirect(url_for("home"))
        else:
            flash("Invalid Password","danger")
    return render_template("authentication/login.html",form=form)
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout Successful","info")
    return redirect(url_for("home"))