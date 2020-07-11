from flask import render_template, request, Blueprint, flash, url_for, redirect
from myMood import db, bcrypt, cache
from myMood.models import User, Post
from myMood.users.forms import RegisterForm
from sqlalchemy.sql.expression import func

main = Blueprint("main", __name__)


@main.route("/home", methods=["GET", "POST"])
@cache.cached(key_prefix="home_page")
def home():
    form = RegisterForm()

    if request.method == "POST":
        if "agree" in request.form:
            if form.validate_on_submit():
                hashed_pass = bcrypt.generate_password_hash(form.password.data).decode(
                    "utf-8"
                )
                user = User(
                    username=form.username.data,
                    email=form.email.data,
                    password=hashed_pass,
                )
                db.session.add(user)
                db.session.commit()
                flash(
                    "Your account has been successfully created. You can now login!",
                    "success",
                )
                return redirect(url_for("users.user_login"))
        else:
            flash("Please accept the Terms and Agreement", "danger")
            return redirect(url_for("main.home"))

    return render_template("main/index.html", title="my.Mood", form=form)


@main.route("/about")
@cache.cached(key_prefix="about_page")
def about():
    return render_template("main/about.html", title="About")


@main.route("/discover/g")
@cache.cached(key_prefix="discover_page")
def discover():
    users = User.query.order_by(func.random()).limit(6).all()
    stories = (
        Post.query.filter_by(state="public")
        .order_by(Post.date_posted.desc())
        .limit(7)
        .all()
    )
    return render_template(
        "main/discover.html", title="Discover", users=users, stories=stories
    )
