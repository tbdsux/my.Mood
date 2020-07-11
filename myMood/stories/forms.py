from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired


class NewStoryForm(FlaskForm):
    content = TextAreaField(validators=[DataRequired()])
    emotion = SelectField(
        choices=[
            ("default", "😃 Feeling..."),
            ("happy", "😀 Happy"),
            ("blessed", "😇 Blessed"),
            ("loved", "😍 Loved"),
            ("lovely", "😊 Lovely"),
            ("sad", "🙁 Sad"),
            ("surprised", "😱 Surprised"),
            ("angry", "😡 Angry"),
            ("excited", "😁 Excited"),
            ("embarassed", "😳 Embarrased"),
            ("thankful", "🤗 Thankful"),
            ("in_love", "🥰 In Love"),
            ("crazy", "😆 Crazy"),
            ("sick", "🤒 Sick"),
            ("tired", "😓 Tired"),
            ("sleepy", "🥱 Sleepy"),
        ]
    )
    state = SelectField(choices=[("private", "Private"), ("public", "Public")])

    post = SubmitField("Post")
