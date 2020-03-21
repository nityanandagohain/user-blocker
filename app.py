#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import TextField, PasswordField, TextAreaField, StringField, validators
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import FileHandler
import os
import traceback
from functools import wraps
from dotenv import load_dotenv


#----------------------------------------------------------------------------#
# App Config
#----------------------------------------------------------------------------#
load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getrandom(4)
app.config['RECAPTCHA_USE_SSL']= False
app.config['RECAPTCHA_PUBLIC_KEY']=os.getenv('RECAPTCHA_PUBLIC_KEY')
app.config['RECAPTCHA_PRIVATE_KEY']=os.getenv('RECAPTCHA_PRIVATE_KEY')
app.config['RECAPTCHA_OPTIONS']= {'theme':'black'}


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'

db = SQLAlchemy(app)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)

# Ip checking decorator.
def check_ip(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        captcha_required = False
        ip_addr = request.remote_addr
        # query for the ip_addr
        ip_addr_obj = IpAddressCount.query.filter_by(ip=ip_addr).first()
        if ip_addr_obj:
            logging.info("Ip addr exisit: ip:{} , count: {}".format(ip_addr_obj.ip, ip_addr_obj.count))
            max_allowed_witout_captcha = 3
            
            if request.method == 'POST':
                max_allowed_witout_captcha = 4

            if ip_addr_obj.count >= max_allowed_witout_captcha:
                captcha_required = True

            ip_addr_obj.count += 1
            db.session.commit()
        else:
            logging.info("Creating a new entry in database")
            ip_add = IpAddressCount(ip=ip_addr, count = 1)
            db.session.add(ip_add)
            db.session.commit()
        return test(*args, captcha_required ,**kwargs)
    return wrap

#----------------------------------------------------------------------------#
# Database Model.
#----------------------------------------------------------------------------#
class IpAddressCount(db.Model):   
    ip = db.Column(db.String, primary_key=True)
    count = db.Column(db.Integer, nullable=False)
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

#----------------------------------------------------------------------------#
# Forms.
#----------------------------------------------------------------------------#
class RegisterForm(FlaskForm):
    name = StringField('name', [validators.DataRequired(), validators.Length(max=255)])
    password = PasswordField('new password', [validators.DataRequired(),validators.Length(min=8)])
    email = StringField('emailaddress', [validators.DataRequired(), validators.Length(min=6, max=35)])

class RegisterFormWithRecaptcha(RegisterForm):   
    recaptcha = RecaptchaField()


#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#
@app.route('/register', methods=['GET', 'POST']) 
@check_ip
def register(captcha_required):
    form = None
    if captcha_required:
        form = RegisterFormWithRecaptcha()
    else:
        form = RegisterForm()

    # form.recaptcha = RecaptchaField()
    if form.validate_on_submit():
        try:
            name = form.name.data
            email = form.email.data
            password = form.password.data
            user = User(username=name, email=email, password=password)
            db.session.add(user)
            db.session.commit()
            return "the form has been submitted. Success!"
        except:
            traceback.print_exc()
            logging.warning("failed to register")

    return render_template("register.html", form=form)

# Default port:
if __name__ == '__main__':
    db.create_all()
    app.run(port=5000, debug=True, host='0.0.0.0')