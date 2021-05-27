from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, RadioField 
from wtforms.validators import DataRequired, Length, Email
from wtforms import widgets

# OPTIONAL Fields and Validators
# from wtforms import PasswordField
# from wtforms.validators import DataRequired, Length, Email, EqualTo

 # writes python classes that automatically transformed to html forms

class boatsearchform(FlaskForm):
    sitename = RadioField('Site', choices=[('YW','Yachtworld'), ('SBL', 'SailboatListings'),('both','Both')], widget=widgets.TableWidget(with_table_tag=True))
    inputcurr = StringField('inputcurr')
    minprice = StringField('minprice')
    maxprice = StringField('maxprice')
    minlength = StringField('minlength', validators=[DataRequired(), Length(min=2, max=3)])
    maxlength = StringField('maxlength')
    sortparam = StringField('inputsearch')
    submit = SubmitField('Begin Search')
    # password = PasswordField('Password', validators=[DataRequired()])
    # confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), Equalto('password')])


class loginform(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')
