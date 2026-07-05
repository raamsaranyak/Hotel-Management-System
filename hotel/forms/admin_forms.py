from . import *
class CreateAdminForm(FlaskForm):
    username=StringField("Username",validators=[DataRequired(),Length(min=2,max=20)])
    password=PasswordField("Password",validators=[DataRequired(),Length(min=8,max=20)])
    confirm_password=PasswordField("Confirm Password",validators=[DataRequired(),EqualTo("password")])
    email=StringField("Email",validators=[DataRequired(),Email()])
    name=StringField("Name",validators=[DataRequired()])
    contact_number=StringField("Contact Number",validators=[DataRequired()])
    submit=SubmitField("Create Admin")
    def validate_username(self,username):
        user=User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Username already taken!")
    def validate_email(self,email):
        user=User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Email already registered!")
class AddRoomForm(FlaskForm):
    hotel=SelectField("Hotel",validators=[DataRequired()])
    room_no=IntegerField("Room No",validators=[DataRequired()])
    category=SelectField("Category",choices=[("STANDARD","Standard"),("DELUXE","Deluxe"),("SUITE","Suite")],validators=[DataRequired()])
    capacity=IntegerField("Capacity",validators=[DataRequired()])
    beds=SelectField("Bed Configuration",choices=[
    ("1 Single","1 Single"),
    ("1 Double","1 Double"),
    ("1 Queen","1 Queen"),
    ("2 Queen","2 Queen"),
    ("1 King","1 King"),
    ("2 King","2 King")
    ],validators=[DataRequired()]
    )
    current_price=FloatField("Price",validators=[DataRequired()])
    floor=IntegerField("Floor",validators=[DataRequired()])
    submit = SubmitField("Add Room")
class HotelForm(FlaskForm):
    hotel_name=StringField("Hotel Name",validators=[DataRequired()])
    branch_name=StringField("Branch Name",validators=[DataRequired()])
    location=StringField("Location",validators=[DataRequired()])
    number_of_floors=IntegerField("Number of Floors",validators=[DataRequired()])
    contact_number=StringField("Contact Number",validators=[DataRequired()])
    email=StringField("Email",validators=[DataRequired(),Email()])
    submit=SubmitField("Save")