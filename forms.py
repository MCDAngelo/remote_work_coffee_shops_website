from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DecimalField,
    SelectField,
    SelectMultipleField,
    SubmitField,
    StringField,
)
from wtforms.validators import DataRequired, Length, NumberRange, URL


class CoffeeShopFilters(FlaskForm):
    has_wifi = BooleanField("Must have Wifi Available")
    has_sockets = BooleanField("Must have Power Sockets Available")
    can_take_calls = BooleanField("Must be Phone-call Friendly")
    has_toilet = BooleanField("Must have Washroom Available")
    location = SelectMultipleField("Location")
    seats = SelectMultipleField("Number of Seats")
    submit = SubmitField("Filter")
    clear = SubmitField("Clear Filters")


class CoffeeShopForm(FlaskForm):
    name = StringField(
        "Name of Coffee Shop", validators=[DataRequired(), Length(min=1, max=250)]
    )
    map_url = StringField(
        "Link to the coffee shop on google maps",
        validators=[DataRequired(), URL()],
    )
    img_url = StringField(
        "Link to an image of the coffee shop",
        validators=[DataRequired(), URL()],
    )
    has_wifi = BooleanField("Wifi available")
    has_sockets = BooleanField("Power sockets available")
    can_take_calls = BooleanField("Can take calls")
    has_toilet = BooleanField("Washrooms available")
    location = SelectField("Location", validators=[DataRequired()])
    seats = SelectField("Approx. number of seats", validators=[DataRequired()])
    coffee_price = DecimalField(
        "Cost of a cup of coffee (£)",
        validators=[DataRequired(), NumberRange(min=0.5, max=20)],
    )
    submit = SubmitField("Submit")
