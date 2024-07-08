from flask import Flask, redirect, render_template, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from forms import CoffeeShopFilters, CoffeeShopForm

app = Flask(__name__)
app.config["SECRET_KEY"] = "8BYkEfBA6O6donzWlSihBXox7C0sKR6b"

bootstrap = Bootstrap5(app)


# Set up class for database:
class Base(DeclarativeBase):
    pass


# Set up database connection to app
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cafes.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Define table schema
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)


# Create the db:
with app.app_context():
    db.create_all()


def create_filter_form(form_class):
    locations_list = (
        db.session.execute(db.select(Cafe.location).distinct().order_by(Cafe.location))
        .scalars()
        .all()
    )
    cafe_seats_list = (
        db.session.execute(db.select(Cafe.seats).distinct().order_by(Cafe.seats))
        .scalars()
        .all()
    )
    filter_form = form_class()
    filter_form.location.choices = locations_list
    filter_form.seats.choices = cafe_seats_list
    return filter_form


@app.route("/", methods=["POST", "GET"])
def home():
    cafes_list = db.session.execute(db.select(Cafe)).scalars().all()
    filter_form = create_filter_form(CoffeeShopFilters)
    if filter_form.validate_on_submit() & filter_form.submit.data:
        q = db.select(Cafe)
        if filter_form.has_wifi.data:
            q = q.where(Cafe.has_wifi)
        if filter_form.has_sockets.data:
            q = q.where(Cafe.has_sockets)
        if filter_form.can_take_calls.data:
            q = q.where(Cafe.can_take_calls)
        if filter_form.has_toilet.data:
            q = q.where(Cafe.has_toilet)
        if len(filter_form.location.data) > 0:
            q = q.where(Cafe.location.in_(filter_form.location.data))
        if len(filter_form.seats.data) > 0:
            q = q.where(Cafe.seats.in_(filter_form.seats.data))

        filtered_cafes_list = db.session.execute(q).scalars().all()
        return render_template(
            "index.html", cafes=filtered_cafes_list, form=filter_form
        )

    if filter_form.validate_on_submit() & filter_form.clear.data:
        return redirect(url_for("home"))

    # Add order by having all desirable properties
    return render_template("index.html", cafes=cafes_list, form=filter_form)


@app.route("/cafe-<int:cafe_id>")
def show_cafe(cafe_id):
    cafe = db.get_or_404(Cafe, cafe_id)
    return render_template("cafe_info.html", cafe=cafe)


@app.route("/add_new", methods=["GET", "POST"])
def add_new_cafe():
    cafe_form = create_filter_form(CoffeeShopForm)
    if cafe_form.validate_on_submit():
        new_shop = Cafe(  # type: ignore[call-arg]
            name=cafe_form.name.data,
            map_url=cafe_form.map_url.data,
            img_url=cafe_form.img_url.data,
            location=cafe_form.location.data,
            seats=cafe_form.seats.data,
            has_toilet=cafe_form.has_toilet.data,
            has_wifi=cafe_form.has_wifi.data,
            has_sockets=cafe_form.has_sockets.data,
            can_take_calls=cafe_form.can_take_calls.data,
            coffee_price=f"£{cafe_form.coffee_price.data}",
        )
        db.session.add(new_shop)
        db.session.commit()
        return redirect(url_for("show_cafe", cafe_id=new_shop.id))
    return render_template("add_cafe.html", form=cafe_form)


@app.route("/contact")
def contact():
    # Update template
    return render_template("index.html")


@app.route("/login")
def login():
    # Update template
    return render_template("index.html")


@app.route("/register")
def register():
    # Update template
    return render_template("index.html")


@app.route("/logout")
def logout():
    # Update template
    return render_template("index.html")


if __name__ == "__main__":
    app.run(
        debug=True,
        host="localhost",
        port=8000,
    )
