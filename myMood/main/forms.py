from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    search_field = StringField(validators=[DataRequired()])

    search = SubmitField()
