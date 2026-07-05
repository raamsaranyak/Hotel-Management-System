from . import *
class RegistrationForm(FlaskForm):
    username=StringField("Username",validators=[DataRequired(),Length(min=2,max=20)])
    password=PasswordField("Password",validators=[DataRequired(),Length(min=8,max=20)])
    confirm_password=PasswordField("Confirm Password",validators=[DataRequired(),Length(min=8,max=20),EqualTo("password")])
    email=StringField("Email",validators=[DataRequired(),Email()])
    customer_name=StringField("Name",validators=[DataRequired()])
    gender=RadioField("Gender",choices=[("MALE","Male"),("FEMALE","Female"),("Other","Other")], validators=[DataRequired()])
    date_of_birth=DateField("Date-of-Birth",validators=[DataRequired()])
    contact_number=StringField("Mobile Number",validators=[DataRequired()])
    address=TextAreaField("Address")
    submit=SubmitField("Submit")
    def validate_username(self,username):
        user=User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Username ALready Taken! Please Try another one")
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Email already registered. Please use another one.")
class LoginForm(FlaskForm):
    username=StringField("Username",validators=[DataRequired()])
    password=PasswordField("Password",validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit=SubmitField("Login")