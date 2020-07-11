from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    EqualTo,
    ValidationError,
    Regexp,
)
from myMood.models import User

# Register
class RegisterForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired(), Length(min=3, max=15), Regexp(r"^[\w.@+-]+$")],
    )
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )

    agree = BooleanField("I agree to the ")

    register = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                "Username already taken. Please choose a different one."
            )

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("An account with that email address already exists!")


# Login
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])

    remember = BooleanField("Remember Me")

    login = SubmitField("Sign In")


# User follow, unfollow
class FollowForm(FlaskForm):
    submit = SubmitField("Submit")


# Reset Password Form
class ResetPassForm(FlaskForm):
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    request = SubmitField("Request Password Reset")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError(
                "There is no user registered with that email address."
            )


# New Password Form
class NewPassForm(FlaskForm):
    password = PasswordField("New Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm New Password", validators=[DataRequired(), EqualTo("password")]
    )
    reset = SubmitField("Reset Password")
