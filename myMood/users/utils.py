import os, secrets
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from myMood import mail


def save_profile_pic(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    pic_fn = random_hex + f_ext
    pic_path = os.path.join(current_app.root_path, "static/profile_pics", pic_fn)

    output_size = (300, 300)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    # save picture
    i.save(pic_path)
    return pic_fn


def save_bg_image(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    pic_fn = random_hex + f_ext
    pic_path = os.path.join(
        current_app.root_path, "static/profile_pics/bg_profile", pic_fn
    )

    output_size = (1300, 730)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    # save picture
    i.save(pic_path)
    return pic_fn


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message(
        subject="Request Password Reset (my.Mood)",
        sender="noreply@myMood.com",
        recipients=[user.email],
    )
    msg.body = f"""my.Mood - Reset Password Request

    To reset your password, visit the following link:
    {url_for('users.new_password', token=token, _external=True)}

If you did not make this equest then simply ignore this email
    """
    mail.send(msg)
