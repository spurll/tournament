from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, HiddenField
from wtforms.fields.html5 import IntegerField
from wtforms.validators import Required, NumberRange


class LoginForm(Form):
    openid = TextField("openid", validators=[Required()])
    remember_me = BooleanField("remember_me", default=False)


class CreateForm(Form):
    name = TextField(label="Tournament Name", validators=[Required()])
    players = HiddenField(label="Players", validators=[Required()])
    add = TextField(label="Add Player")


class ReportForm(Form):
    match = HiddenField(label="Match", validators=[Required()])
    seat_1 = IntegerField(default=0, validators=[NumberRange(min=0)])
    seat_2 = IntegerField(default=0, validators=[NumberRange(min=0)])
    draws = IntegerField(label="Draws", default=0, validators=[NumberRange(min=0)])
