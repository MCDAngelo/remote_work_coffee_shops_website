from functools import wraps
import os

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_bootstrap import Bootstrap5
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from werkzeug.security import check_password_hash, generate_password_hash

from forms import CoffeeShopFilters, CoffeeShopForm, LoginForm, RegisterForm

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("APP_SECRET")

bootstrap = Bootstrap5(app)

login_manager = LoginManager()
login_manager.init_app(app)


# Set up class for database:
class Base(DeclarativeBase):
    pass


# Set up database connection to app
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_URI", "sqlite:///cafes.db")
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Define table schemas
class Cafe(db.Model):
    __tablename__ = "cafe"
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
    potentially_closed: Mapped[bool] = mapped_column(Boolean, nullable=True)
    deleted: Mapped[bool] = mapped_column(Boolean, nullable=True)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    admin: Mapped[bool] = mapped_column(Boolean, nullable=True)


# Create the db:
with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


def admin_only(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return login_manager.unauthorized()
        if not current_user.admin:
            return login_manager.unauthorized()
        return func(*args, **kwargs)

    return decorated_view


def create_filter_form(filter_form):
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
    filter_form.location.choices = locations_list
    filter_form.seats.choices = cafe_seats_list
    return filter_form


@app.route("/", methods=["POST", "GET"])
def home():
    cafes_list = (
        db.session.execute(db.select(Cafe).where(Cafe.deleted.isnot(True)))
        .scalars()
        .all()
    )
    filter_form = CoffeeShopFilters()
    filter_form = create_filter_form(filter_form)
    if filter_form.validate_on_submit() & filter_form.submit.data:
        q = db.select(Cafe).where(Cafe.deleted.isnot(True))
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


@app.route("/cafe/<int:cafe_id>")
def show_cafe(cafe_id):
    cafe = db.get_or_404(Cafe, cafe_id)
    return render_template("cafe_info.html", cafe=cafe)


@app.route("/add_new", methods=["GET", "POST"])
def add_new_cafe():
    cafe_form = CoffeeShopForm()
    cafe_form = create_filter_form(cafe_form)
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
    return render_template("add_cafe.html", form=cafe_form, is_edit=False)


@app.route("/report_closure/<int:cafe_id>", methods=["GET", "POST"])
def report_closure(cafe_id):
    submitted = False
    cafe = db.get_or_404(Cafe, cafe_id)
    if request.method == "POST":
        if current_user.is_authenticated:
            submitted = True
            cafe.potentially_closed = True
            db.session.commit()
        else:
            flash("Please log in to report a closure.")
            return redirect(url_for("login"))
    return render_template("report_closure.html", cafe=cafe, submitted_req=submitted)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        pswd = form.password.data
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if not user:
            flash("Hmm, this email doesn't exist in our records, try again.")
            return redirect(url_for("login"))
        elif not check_password_hash(user.password, pswd):
            flash("Incorrect password, try again.")
            return redirect(url_for("login"))
        else:
            login_user(user)
            return redirect(url_for("home"))
    return render_template("login.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        existing_user = db.session.execute(
            db.select(User).where(User.email == email)
        ).scalar()
        if existing_user:
            flash(
                "You already have an account registered with this email, login instead!"
            )
            return redirect(url_for("login"))
        else:
            hashed_pswd = generate_password_hash(
                password=form.password.data,
                method="pbkdf2:sha256",
                salt_length=8,
            )
            new_user = User(  # type: ignore[call-arg]
                email=email,
                username=form.username.data,
                password=hashed_pswd,
                admin=True if email == os.getenv("SUPER_ADMIN_EMAIL") else False,
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("home"))
    return render_template("register.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/admin")
@admin_only
def admin_view():
    return render_template("admin.html", user=current_user)


@app.route("/admin/edit_cafes")
@admin_only
def edit_cafes():
    cafes = (
        db.session.execute(db.select(Cafe).order_by(Cafe.potentially_closed.desc()))
        .scalars()
        .all()
    )
    return render_template("admin_cafes.html", user=current_user, cafes=cafes)


@app.route("/admin/delete_cafe/<int:cafe_id>", methods=["GET", "POST"])
@admin_only
def delete_cafe(cafe_id):
    submitted = False
    cafe = db.get_or_404(Cafe, cafe_id)
    if request.method == "POST":
        submitted = True
        cafe.deleted = True
        db.session.commit()
        redirect(url_for("edit_cafes"))
    return render_template(
        "admin_delete_cafe.html", cafe=cafe, submitted=submitted, form_type="delete"
    )


@app.route("/admin/restore_cafe/<int:cafe_id>", methods=["GET", "POST"])
@admin_only
def restore_cafe(cafe_id):
    submitted = False
    cafe = db.get_or_404(Cafe, cafe_id)
    if request.method == "POST":
        submitted = True
        cafe.deleted = False
        cafe.potentially_closed = False
        db.session.commit()
        redirect(url_for("edit_cafes"))
    return render_template(
        "admin_delete_cafe.html", cafe=cafe, submitted=submitted, form_type="restore"
    )


@app.route("/admin/edit_cafe/<int:cafe_id>", methods=["GET", "POST"])
@admin_only
def admin_edit_cafe(cafe_id):
    cafe = db.get_or_404(Cafe, cafe_id)
    cafe_form = CoffeeShopForm(
        name=cafe.name,
        map_url=cafe.map_url,
        img_url=cafe.img_url,
        location=cafe.location,
        seats=cafe.seats,
        has_toilet=cafe.has_toilet,
        has_sockets=cafe.has_sockets,
        can_take_calls=cafe.can_take_calls,
        coffee_price=float(cafe.coffee_price.replace("£", "")),
    )
    cafe_form = create_filter_form(cafe_form)
    if cafe_form.validate_on_submit():
        cafe.name = cafe_form.name.data
        cafe.map_url = cafe_form.map_url.data
        cafe.img_url = cafe_form.img_url.data
        cafe.location = cafe_form.location.data
        cafe.seats = cafe_form.seats.data
        cafe.has_toilet = cafe_form.has_toilet.data
        cafe.has_wifi = cafe_form.has_wifi.data
        cafe.has_sockets = cafe_form.has_sockets.data
        cafe.can_take_calls = cafe_form.can_take_calls.data
        cafe.coffee_price = f"£{cafe_form.coffee_price.data}"
        db.session.commit()
        return redirect(url_for("show_cafe", cafe_id=cafe.id))
    return render_template("add_cafe.html", form=cafe_form, is_edit=True)


@app.route("/admin/edit_users", methods=["GET", "POST"])
@admin_only
def edit_users():
    users = db.session.execute(db.select(User)).scalars().all()
    if request.method == "POST":
        admin_user_ids = request.form.getlist("make_admin")
        print(admin_user_ids)
        for user in users:
            if str(user.id) in admin_user_ids:
                user.admin = True
            else:
                user.admin = False
            db.session.commit()
        flash("Database has been successfully updated")
        return redirect(url_for("edit_users"))
    return render_template("admin_users.html", user=current_user, users=users)


if __name__ == "__main__":
    app.run(
        debug=True,
        host="localhost",
        port=8000,
    )
