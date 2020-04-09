from flask_wtf import FlaskForm
from wtforms import TextField, BooleanField, HiddenField, PasswordField
from wtforms.fields.html5 import IntegerField
from wtforms.validators import Required, NumberRange


class LoginForm(FlaskForm):
    username = TextField("Username:", validators=[Required()])
    password = PasswordField("Password:", validators=[Required()])
    remember = BooleanField("Remember Me", default=True)


class CreateForm(FlaskForm):
    name = TextField(label="Tournament Name", default="Tournament",
                     validators=[Required()])
    players = HiddenField(label="Players", validators=[Required()])
    add = TextField(label="Add Player")


class ReportForm(FlaskForm):
    match = HiddenField(label="Match", validators=[Required()])
    seat_1 = IntegerField(default=0, validators=[NumberRange(min=0)])
    seat_2 = IntegerField(default=0, validators=[NumberRange(min=0)])
    draws = IntegerField(label="Draws", default=0, validators=[NumberRange(min=0)])
