from flask_wtf import FlaskForm
from wtforms import TextField, BooleanField, PasswordField
from wtforms.validators import Required, EqualTo

class LoginForm(FlaskForm):
	nickname = TextField('nickname', validators = [Required()])
	remember_me = BooleanField('remember_me', default = False)

class PasswordForm(FlaskForm):
	password = PasswordField('password', validators = [Required()])

class RegistryFrom(FlaskForm):
	password = PasswordField('password', validators = [Required()])
	repeatPassword = PasswordField('repeatPassword', validators = [Required(), EqualTo('password', message='Passwords must match')])

