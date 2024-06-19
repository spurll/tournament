from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, HiddenField, PasswordField, \
    IntegerField
from wtforms.validators import DataRequired, NumberRange


class LoginForm(FlaskForm):
    username = StringField("Username:", validators=[DataRequired()])
    password = PasswordField("Password:", validators=[DataRequired()])
    remember = BooleanField("Remember Me", default=True)


class CreateForm(FlaskForm):
    name = StringField(label="Tournament Name", default="Tournament",
                     validators=[DataRequired()])
    players = HiddenField(label="Players", validators=[DataRequired()])
    add = StringField(label="Add Player")


class ReportForm(FlaskForm):
    match = HiddenField(label="Match", validators=[DataRequired()])
    seat_1 = IntegerField(default=0, validators=[NumberRange(min=0)])
    seat_2 = IntegerField(default=0, validators=[NumberRange(min=0)])
    draws = IntegerField(label="Draws", default=0, validators=[NumberRange(min=0)])
