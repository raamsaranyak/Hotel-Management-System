from . import *
class HotelSearchForm(FlaskForm):
    check_in_date=DateField("Check in",validators=[DataRequired()])
    check_out_date=DateField("Check Out",validators=[DataRequired()])
    number_of_people=IntegerField("People",validators=[DataRequired(),NumberRange(min=1,message="Number of people must be at least 1")])
    category=SelectField("Category",choices=[("","All Categories"),("STANDARD","Standard"),("DELUXE","Deluxe"),("SUITE","Suite")])
    submit=SubmitField("Search")
    def validate_check_out_date(self,check_out_date):
       if self.check_in_date.data and check_out_date.data <= self.check_in_date.data:
           raise ValidationError("Check Out Date must be after Check In Date.")
class GuestForm(FlaskForm):
    guest_name=StringField("Guest Name",validators=[DataRequired()])
    gender=RadioField("Gender",choices=[("MALE","Male"),("FEMALE","Female"),("Other","Other")], validators=[DataRequired()])
    age=IntegerField("Age",validators=[DataRequired()])
    contact_number=StringField("Contact Number",validators=[DataRequired()])
    number_of_people=IntegerField("Number of People",validators=[DataRequired()])
    submit=SubmitField("Confirm Booking")