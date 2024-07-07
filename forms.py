from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectMultipleField, SubmitField

seat_options = []
location_options = []


class CoffeeShopFilters(FlaskForm):
    has_wifi = BooleanField("Must have Wifi Available")
    has_sockets = BooleanField("Must have Power Sockets Available")
    can_take_calls = BooleanField("Must be Phone-call Friendly")
    has_toilet = BooleanField("Must have Washroom Available")
    location = SelectMultipleField("Location")
    seats = SelectMultipleField("Number of Seats")
    submit = SubmitField("Filter")
    clear = SubmitField("Clear Filters")
