from . import *
class AccountForm(FlaskForm):
    username = StringField("Username",validators=[DataRequired()]) 
    email=StringField("Email",validators=[Email(),DataRequired()])
    customer_name = StringField("Name",validators=[DataRequired()])
    gender=RadioField("Gender",choices=[("MALE","Male"),("FEMALE","Female"),("Other","Other")], validators=[DataRequired()])
    date_of_birth=DateField("Date-of-Birth",validators=[DataRequired()])
    contact_number=StringField("Mobile Number",validators=[DataRequired()])
    address=TextAreaField("Address")
    submit = SubmitField("Update")
class ReviewForm(FlaskForm):
    rating = SelectField("Rating", choices=[("5", "5 Stars"), 
                                        ("4", "4 Stars"), 
                                        ("3", "3 Stars"), 
                                        ("2", "2 Stars"), 
                                        ("1", "1 Star")], 
                                        validators=[DataRequired()]
                                        )
    review_text=TextAreaField("Review",validators=[DataRequired()])
    submit=SubmitField("Submit Review")
class ContactForm(FlaskForm):
    name=StringField("Name",validators=[DataRequired()])
    contact_number=StringField("Contact Number",validators=[DataRequired()])
    email=StringField("Email",validators=[DataRequired(),Email()])
    message=TextAreaField("Message",validators=[DataRequired()])
    submit=SubmitField("Send Message")
class ComplaintForm(FlaskForm):
    complaint_text=TextAreaField("Complaint",validators=[DataRequired()])
    submit=SubmitField("Submit Complaint")