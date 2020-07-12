from flask import (
    render_template,
    url_for,
    flash,
    redirect,
    request,
    Blueprint,
    current_app,
    session,
)
from sqlalchemy.sql.expression import func
from flask_login import login_user, current_user, logout_user, login_required
from myMood import db, bcrypt, cache
from myMood.models import User, Post
from myMood.stories.query import (
    query_all_stories,
    query_all_public_stories,
    query_public_stories,
    query_def_stories,
    query_all_stories,
)
from myMood.users.query import (
    query_user_profile,
    query_search_user,
    query_search_stories,
)
from myMood.users.forms import (
    RegisterForm,
    LoginForm,
    FollowForm,
    ResetPassForm,
    NewPassForm,
)
from myMood.stories.forms import NewStoryForm
from myMood.main.forms import SearchForm
from myMood.users.forms_profile import (
    UpdateProfile,
    UpdateProfilePic,
    UpdateWHOAMI,
    UpdateBgImage,
    UpdateSocialLinks,
    UpdateEmail,
    UpdatePassword,
)
from myMood.users.utils import save_bg_image, save_profile_pic, send_reset_email
import os

users = Blueprint("users", __name__)


def is_post():
    return request.method == "POST"


@users.route("/user/login", methods=["GET", "POST"])
def user_login():
    # bypass if user is authenticated
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()

    if request.method == "POST":
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                session["user"] = request.form["email"]
                login_user(user, remember=form.remember.data)
                next_page = request.args.get("next")
                return (
                    redirect(next_page)
                    if next_page
                    else redirect(url_for("users.dashboard"))
                )
            else:
                flash("Incorrect Email / Password!!", "danger")

    return render_template(
        "main/login.html", form=form, form_title="Login", screen_height="h-screen"
    )


@users.route("/user/register", methods=["GET", "POST"])
def user_register():
    # bypass if user is authenticated
    if current_user.is_authenticated:
        return redirect(url_for("users.dashboard"))

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
            return redirect(url_for("users.user_register"))

    return render_template(
        "main/register.html", form=form, form_title="Register", screen_height="h-full"
    )


@users.route("/logout")
def user_logout():
    session.pop("user", None)
    logout_user()
    return redirect(url_for("users.user_login"))


# Dashboard Routes
@users.route("/", methods=["GET", "POST"])
def dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for("main.home"))
    # s = current_user
    # page = request.args.get("stories", 1, type=int)
    s = current_user
    stories = s.followed_posts().limit(10).all()
    # stories = Post.query.filter_by(author=current_user).order_by(
    #     Post.date_posted.desc()
    # )
    # stories = Post.query.order_by(Post.date_posted.desc()).paginate(
    #     page=page, per_page=5
    # )
    form = NewStoryForm()

    if request.method == "POST":
        if form.validate_on_submit():
            story = Post(
                content=form.content.data,
                emotion=form.emotion.data,
                state=form.state.data,
                author=current_user,
            )
            db.session.add(story)
            db.session.commit()
            if request.form["state"] == "public":
                cache.delete_memoized(query_public_stories, query_all_public_stories)
            cache.delete_memoized(query_def_stories)
            return redirect(url_for("users.dashboard"))
    return render_template(
        "dashboard/index.html", form=form, dashboard_title="Home", stories=stories,
    )


# Follow User
@users.route("/follow/<user_to_follow>", methods=["POST"])
def follow_user(user_to_follow):
    formFollow = FollowForm()
    if request.method == "POST":
        if formFollow.validate_on_submit():
            target_user = User.query.filter_by(username=user_to_follow).first()
            current_user.follow(target_user)
            db.session.commit()
            cache.delete_memoized(query_user_profile, user_to_follow)
            cache.delete("user_stories")
            cache.delete_memoized(dash_profile, user_to_follow)
            return redirect(url_for("users.dash_profile", user=user_to_follow))


# Unfollow User
@users.route("/unfollow/<user_to_unfollow>", methods=["POST"])
def unfollow_user(user_to_unfollow):
    formFollow = FollowForm()
    if request.method == "POST":
        if formFollow.validate_on_submit():
            target_user = User.query.filter_by(username=user_to_unfollow).first()
            current_user.unfollow(target_user)
            db.session.commit()
            cache.delete_memoized(query_user_profile, user_to_unfollow)
            cache.delete("user_stories")
            cache.delete_memoized(dash_profile, user_to_unfollow)
            return redirect(url_for("users.dash_profile", user=user_to_unfollow))


# User Profile
@users.route("/u/<user>", methods=["GET"])
@cache.memoize()
def dash_profile(user):
    formUpProfile = UpdateProfile()
    formUpProfilePic = UpdateProfilePic()
    formUpBgImage = UpdateBgImage()
    formUpWhoami = UpdateWHOAMI()
    formUpSocialLinks = UpdateSocialLinks()
    formFollow = FollowForm()

    if request.method == "GET":
        formUpProfile.username.data = current_user.username
        formUpProfile.random_say.data = current_user.random_say
        formUpWhoami.whoami.data = current_user.whoami
        formUpSocialLinks.fb.data = current_user.social_fb
        formUpSocialLinks.tw.data = current_user.social_tw
        formUpSocialLinks.ig.data = current_user.social_ig
        formUpSocialLinks.yt.data = current_user.social_yt

    username = query_user_profile(user)
    if username != current_user:
        cache.delete_memoized(dash_profile, user)
    # stories = Post.query.filter_by(author=username).order_by(Post.date_posted.desc())
    if current_user == username:
        stories = (
            Post.query.filter_by(author=username)
            .order_by(Post.date_posted.desc())
            .limit(7)
            .all()
        )
    else:
        if current_user.is_following(username):
            stories = (
                Post.query.filter_by(author=username)
                .order_by(Post.date_posted.desc())
                .limit(7)
                .all()
            )
        else:
            stories = (
                Post.query.filter_by(author=username, state="public")
                .order_by(Post.date_posted.desc())
                .limit(7)
                .all()
            )

    return render_template(
        "dashboard/user_profile.html",
        dashboard_title=user + " - Profile",
        my_stories=stories,
        user=username,
        formUpProfile=formUpProfile,
        formUpProfilePic=formUpProfilePic,
        formUpBgImage=formUpBgImage,
        formUpWhoami=formUpWhoami,
        formUpSocialLinks=formUpSocialLinks,
        formFollow=formFollow,
    )


#:> Update User_Info Routes

# Background Profile
@users.route("/u/<user>/update?=bg_image", methods=["POST"])
def update_BgImage(user):
    formUpBgImage = UpdateBgImage()
    if request.method == "POST":
        if formUpBgImage.validate_on_submit():
            if formUpBgImage.image_background.data:
                # delete the existing background pic is it is not the default one
                if current_user.acc_image_bg != "default.jpg":
                    pp_path = os.path.join(
                        current_app.root_path,
                        "static\\profile_pics\\bg_profile",
                        current_user.acc_image_bg,
                    )
                    try:
                        os.remove(pp_path)
                    except FileNotFoundError:
                        pass

                # change the background pic
                pic_file = save_bg_image(formUpBgImage.image_background.data)
                current_user.acc_image_bg = pic_file
                db.session.commit()
                cache.delete_memoized(query_user_profile, user)
                cache.delete_memoized(dash_profile, user)
                return redirect(
                    url_for("users.dash_profile", user=current_user.username)
                )


# Profile Picture
@users.route("/u/<user>/update?=profile_pic", methods=["POST"])
def update_ProfilePic(user):
    formUpProfilePic = UpdateProfilePic()
    if request.method == "POST":
        if formUpProfilePic.validate_on_submit():
            if formUpProfilePic.profile_pic.data:
                # delete the existing profile pic is it is not the default one
                if current_user.acc_image != "default.jpg":
                    pp_path = os.path.join(
                        current_app.root_path,
                        "static\\profile_pics",
                        current_user.acc_image,
                    )
                    try:
                        os.remove(pp_path)
                    except FileNotFoundError:
                        pass

                # change the profile pic
                pic_file = save_profile_pic(formUpProfilePic.profile_pic.data)
                current_user.acc_image = pic_file
                db.session.commit()
                cache.delete_memoized(query_user_profile, user)
                cache.delete_memoized(dash_profile, user)
                return redirect(
                    url_for("users.dash_profile", user=current_user.username)
                )


# Profile Info
@users.route("/u/<user>/update?=profile", methods=["POST"])
def update_Profile(user):
    formUpProfile = UpdateProfile()
    if request.method == "POST":
        if formUpProfile.validate_on_submit():
            current_user.username = formUpProfile.username.data
            current_user.random_say = formUpProfile.random_say.data
            db.session.commit()
            cache.delete_memoized(query_user_profile, user)
            cache.delete_memoized(dash_profile, user)
            return redirect(url_for("users.dash_profile", user=current_user.username))
    return redirect(url_for("users.dash_profile", user=current_user.username))


# WHOAMI
@users.route("/u/<user>/update?=whoami", methods=["POST"])
def update_Whoami(user):
    formUpWhoami = UpdateWHOAMI()
    if request.method == "POST":
        if formUpWhoami.validate_on_submit():
            current_user.whoami = formUpWhoami.whoami.data
            db.session.commit()
            cache.delete_memoized(query_user_profile, user)
            cache.delete_memoized(dash_profile, user)
            return redirect(url_for("users.dash_profile", user=current_user.username))


# Social Links
@users.route("/u/<user>/update?=social_links", methods=["POST"])
def update_SocialLinks(user):
    formUpSocialLinks = UpdateSocialLinks()
    if request.method == "POST":
        if formUpSocialLinks.validate_on_submit():
            current_user.social_fb = formUpSocialLinks.fb.data
            current_user.social_tw = formUpSocialLinks.tw.data
            current_user.social_ig = formUpSocialLinks.ig.data
            current_user.social_yt = formUpSocialLinks.yt.data
            db.session.commit()
            cache.delete_memoized(query_user_profile, user)
            cache.delete_memoized(dash_profile, user)
            return redirect(url_for("users.dash_profile", user=current_user.username))


# Account Settings
@users.route("/account/settings", methods=["GET", "POST"])
def dash_acc_settings(emailErr=None, passErr=None):
    formCEmail = UpdateEmail()
    formCPass = UpdatePassword()

    if request.method == "POST":
        if "updateEmail" in request.form and formCEmail.validate_on_submit():
            current_user.email = formCEmail.email.data
            db.session.commit()
            flash("You have successfully updated your email address.", "success")
            return redirect(url_for("users.dash_acc_settings"))
        if "updatePass" in request.form and formCPass.validate_on_submit():
            hashed_pass = bcrypt.generate_password_hash(formCPass.password.data).decode(
                "utf-8"
            )
            current_user.password = hashed_pass
            db.session.commit()
            flash("You have successfully changed your password.", "success")
            return redirect(url_for("users.dash_acc_settings"))
    if request.method == "GET":
        formCEmail.email.data = current_user.email
    return render_template(
        "dashboard/acc_settings.html",
        dashboard_title="Account Settings",
        formCEmail=formCEmail,
        formCPass=formCPass,
        emailErr=emailErr,
        passErr=passErr,
    )


# Discover
@users.route("/discover", methods=["GET", "POST"])
def dash_discover():
    formFollow = FollowForm()
    formSearch = SearchForm()

    if formSearch.validate_on_submit():
        return redirect(url_for("users.search", query=formSearch.search_field.data))

    users = (
        User.query.filter(User.username != current_user.username)
        .order_by(func.random())
        .limit(5)
        .all()
    )

    stories = query_public_stories()

    return render_template(
        "dashboard/discover.html",
        users=users,
        dashboard_title="Discover",
        stories=stories,
        formFollow=formFollow,
        formSearch=formSearch,
    )


# Search
@users.route("/search", methods=["GET", "POST"])
@login_required
def search():
    formFollow = FollowForm()
    formSearch = SearchForm()

    q = request.args.get("query")

    if formSearch.validate_on_submit():
        return redirect(url_for("users.search", query=formSearch.search_field.data))

    # get users
    users = query_search_user(q)
    # get stories
    # s = current_user
    # stories = s.search_posts(q).all()
    stories = query_search_stories(q)

    # pass the search query to the inut value
    formSearch.search_field.data = q

    return render_template(
        "dashboard/search.html",
        formFollow=formFollow,
        formSearch=formSearch,
        users=users,
        stories=stories,
        query=q,
        dashboard_title="Search: '" + q + "'",
    )


# get posts of a user
@users.route("/u/<user>/stories")
@cache.cached(key_prefix="user_stories")
def user_stories(user):
    # page = request.args.get("p", 1, type=int)
    u = User.query.filter_by(username=user).first_or_404()
    stories = (
        Post.query.filter_by(author=u).order_by(Post.date_posted.desc()).limit(7).all()
    )

    if u == current_user:
        title = "My Stories"
    else:
        title = u.username + "'s Stories"

    return render_template(
        "dashboard/post_user.html", dashboard_title=title, stories=stories, u=u
    )


# Reset Password > Send a Request Token
@users.route("/reset/password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = ResetPassForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash(
            "An email has been sent with instructions to reset your password.", "info"
        )
    return render_template(
        "main/forgot_password.html",
        form_title="Forgot Password",
        form=form,
        screen_height="h-screen",
    )


# Reset Password > Enter a new password
@users.route("/reset/password/new", methods=["GET", "POST"])
def new_password():
    token = request.args.get("token")
    if current_user.is_authenticated:
        return redirect(url_for("users.home"))
    user = User.verify_reset_token(token)
    if user is None:
        flash("That is an invalid or expired token!", "warning")
        return redirect(url_for("users.reset_request"))
    form = NewPassForm()
    if form.validate_on_submit():
        hashed_pass = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user.password = hashed_pass
        db.session.commit()
        flash("Your password has been updated! You can now log in!", "success")
        return redirect(url_for("users.user_login"))
    return render_template(
        "main/new_password.html", form_title="Reset Password", form=form
    )
