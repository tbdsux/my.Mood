from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, Length, ValidationError, Email, EqualTo
from flask_login import current_user
from myMood import bcrypt
from myMood.models import User


class UpdateBgImage(FlaskForm):
    image_background = FileField(validators=[FileAllowed(["jpg", "png"])])
    update = SubmitField("Save Changes")


class UpdateProfilePic(FlaskForm):
    profile_pic = FileField(validators=[FileAllowed(["jpg", "png"])])
    update = SubmitField("Save Changes")


class UpdateProfile(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=3, max=15)]
    )
    random_say = TextAreaField("Say Something")
    update = SubmitField("Save Changes")


class UpdateWHOAMI(FlaskForm):
    whoami = TextAreaField("Who Am I?")
    update = SubmitField("Save Changes")


class UpdateSocialLinks(FlaskForm):
    fb = StringField("Facebook")
    tw = StringField("Twitter")
    ig = StringField("Instagram")
    yt = StringField("Youtube")
    update = SubmitField("Save Changes")

    # def validate_fb(self, fb):
    #     if fb.data != None or fb.data != "":
    #         fb_links = [
    #             "http://fb.me/",
    #             "https://fb.me/",
    #             "https://facebook.com/",
    #             "https://www.facebook.com/",
    #         ]
    #         if not fb.data.startswith(tuple(fb_links)):
    #             raise ValidationError("Invalid Facebook URL!")
    #
    # def validate_tw(self, tw):
    #     if tw.data != None or tw.data != "":
    #         tw_links = [
    #             "http://t.co/",
    #             "https://t.co/",
    #             "https://twitter.com/",
    #             "https://www.twitter.com/",
    #         ]
    #         if not tw.data.startswith(tuple(tw_links)):
    #             raise ValidationError("Invalid Twitter URL!")
    #
    # def validate_ig(self, ig):
    #     if ig.data != None or ig.data != "":
    #         ig_links = ["https://instagram.com/", "https://www.instagram.com/"]
    #         if not ig.data.startswith(tuple(ig_links)):
    #             raise ValidationError("Invalid Instagram URL!")
    #
    # def validate_yt(self, yt):
    #     if yt.data != None or yt.data != "":
    #         yt_links = [
    #             "http://youtu.be/",
    #             "http://yt.be/",
    #             "https://youtu.be/",
    #             "https://yt.be/",
    #             "https://youtube.com/",
    #             "https://www.youtube.com/",
    #         ]
    #         if not yt.data.startswith(tuple(yt_links)):
    #             raise ValidationError("Invalid Youtube URL!")


class UpdateEmail(FlaskForm):
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    updateEmail = SubmitField("Update")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("An account with that email address already exists!")


class UpdatePassword(FlaskForm):
    current_password = PasswordField("Current Password", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    updatePass = SubmitField("Change Password")

    def validate_current_password(self, current_password):
        if not bcrypt.check_password_hash(current_user.password, current_password.data):
            raise ValidationError("Please input your current password to validate!")

    def validate_password(self, password):
        if bcrypt.check_password_hash(current_user.password, password.data):
            raise ValidationError("Same password! Please input a different password.")
