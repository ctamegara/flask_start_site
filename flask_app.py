from flask import Flask, render_template, redirect, url_for,request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy.sql import select


################################################################################
#####              PARAMÉTRAGE DE LA BASE DE DONNÉES                      ######
################################################################################



### Remplissez les deux champs ci-dessous
MY_USERNAME=""             #écrivez ici votre username
MY_DB_PASSWORD=""          #écrivez ici le mot de passe de votre base de données


### Ne touchez pas à ça
app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'Une_phrase_secrète'
SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username=MY_USERNAME,
    password=MY_DB_PASSWORD,
    hostname=MY_USERNAME+".mysql.pythonanywhere-services.com",
    databasename=MY_USERNAME+"$mydb",
)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


### Ne touchez pas à ça
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'



################################################################################
#####                          LA CLASSE USER                             ######
################################################################################


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), unique=True)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(80))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('Identifiant', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Mot de passe', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('enregistrer')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('Identifiant', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Mot de passe', validators=[InputRequired(), Length(min=8, max=80)])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_active :
        return render_template('logged_in_warning.html', message = "Vous devez être déconnecté avant de vous connecter")

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('profil'))
            else :
                return "<h1> Mauvais nom d'utilisateur ou mauvais mot de passe </h1>"

        return "<h1> Mauvais nom d'utilisateur ou mauvais mot de passe </h1>"

    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if current_user.is_active :
        return render_template('logged_in_warning.html', message = "Vous devez être déconnecté avant de vous inscrire")

    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('profil'))
    return render_template('signup.html', form=form)




@app.route('/logout' )
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/profil')
@login_required
def profil():
    return " profil de "+current_user.username+ "(exemple de page nécessitant d'être logué)"

@app.route('/')
def welcome():
    return " ma page (exemple de page ne nécessitant pas d'être logué)"

