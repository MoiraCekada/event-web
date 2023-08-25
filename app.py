from flask import Flask, render_template, request, session, redirect, url_for, flash
import json
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app) # for password encryption

app.config["SECRET_KEY"] = "hfgdjoeeiuryt635tsjs"

with open('config.json') as server: # reading server adress
    server_details = json.load(server)['server_details']

local_server = True # we are working at local_server

if local_server:
    app.config['SQLALCHEMY_DATABASE_URI'] = server_details['local_server']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = server_details['production_server']

db = SQLAlchemy(app) # intitializing object for database interaction

class RegisterUser(db.Model):
    sr_number = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, unique = True, nullable = False)
    phone = db.Column(db.String, unique = True, nullable = False)
    email = db.Column(db.String, unique = True, nullable = False)
    password = db.Column(db.String, nullable = False)

class Events(db.Model):
    sr_number = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, unique = False, nullable = False)
    location = db.Column(db.String, unique = False, nullable = False)
    date = db.Column(db.Date, unique = False, nullable = False)
    time = db.Column(db.Time, unique = False, nullable = False)
    budget  = db.Column(db.String, unique = False, nullable = False)
    description = db.Column(db.String, unique = False, nullable = False)
    username = db.Column(db.String, unique = False, nullable = False)


class Members(db.Model):
    sr_number = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, unique = False, nullable = False)
    contact = db.Column(db.String, unique = False, nullable = False)
    age = db.Column(db.String, unique = False, nullable = False)
    location = db.Column(db.String, unique = False, nullable = False)
    event_number = db.Column(db.Integer, unique = True)
    event_name = db.Column(db.String, unique = False, nullable = False)


@app.route("/")
def home():
    if ("user" in session):
        return render_template('index.html', user = str(session["user"]))
    
    return render_template('index.html', user = None)


@app.route("/about")
def about():
    if ("user" in session):
        return render_template('about.html', user = str(session["user"]))
    
    return render_template('about.html', user = None)


@app.route("/events", methods=['GET', 'POST'])
def events():
    if ("user" in session):
        if request.method == 'POST': # creating a new event
            name = request.form.get('name')
            location = request.form.get('location')
            date = request.form.get('date')
            time = request.form.get('time')
            budget = request.form.get('budget')
            messageText = request.form.get('messageText')
            
            try:
                add_event = Events(name = name, location = location,
                                        date = date, time = time, budget = budget,
                                        description = messageText, username = str(session["user"]))
                db.session.add(add_event)
                db.session.commit()
            
            except Exception as e:
                flash("event isn\'t created please try again...".title())
                return render_template('events.html', user=str(session["user"]), events = events)

        events = db.session.query(Events).filter(Events.username == f'{str(session["user"])}').all()
        return render_template('events.html', user=str(session["user"]), events = events)
    
    return render_template('events.html', user = None)


@app.route("/edit/<sr_number>", methods = ['GET', 'POST'])
def edit_event(sr_number):
    """functionality can only be accessed by admin"""
    if ("user" in session):
        if request.method == 'POST': # getting data of targeted event
            name = request.form.get('name')
            location = request.form.get('location')
            date = request.form.get('date')
            time = request.form.get('date')
            budget = request.form.get('budget')
            description = request.form.get('description')
            
            try:
                # making uodates in database
                event = Events.query.filter_by(sr_number = sr_number).first()
                event.name = name
                event.location = location
                event.date = date
                event.time = time
                event.budget = budget
                event.description = description
                db.session.commit()

                flash("event updated successfully...".title(), category = "error")
                return redirect(url_for('events')) # back to events page
            
            except Exception as e:
                flash("event isn\'t updated, please check your internet connection".title(), category = "error")
                return redirect(url_for('events'))

        event = Events.query.filter_by(sr_number = sr_number).first()
        return render_template('edit_event.html', event = event, user = str(session["user"]))


@app.route("/delete/<sr_number>", methods = ['GET', 'POST'])
def delete_event(sr_number):
    if ("user" in session):
        try:
            event = Events.query.filter_by(sr_number = sr_number).first()
            db.session.delete(event)
            db.session.commit()
            flash("event deleted successfully...".title(), category = "error")
            return redirect(url_for('events'))
        
        except Exception as e:
            flash("error while deleting event please check your internet connection...".title(), category = "error")
            return redirect(url_for('events'))



@app.route("/dashboard")
def user_dashboard():
    if ("user" in session):
        events = db.session.query(Events).filter(Events.username == f'{str(session["user"])}').all()
        member = []
        for items in events:
            members = db.session.query(Members).filter(Members.event_number == items.sr_number).all()
            member.append(members)
        member1 = []
        for item in member:
            for items in item:
                member1.append(items)

        return render_template('dashboard.html', user = str(session["user"]), member = member1)
    

@app.route("/join")
def join_event():
    if ("user" in session):
        events = Events.query.filter_by().all()
        members = Members.query.filter_by().all()
        return render_template('join.html', events = events, user = str(session["user"]), member = members)

    events = Events.query.filter_by().all()
    return render_template('join.html', events = events, user = None)


@app.route("/join-event/<sr_number>", methods = ['GET', 'POST'])
def joining_event(sr_number):
    events = Events.query.filter_by(sr_number = sr_number).first()
    if "user" in session:
        if request.method == 'POST':
            name = request.form.get('name')
            location = request.form.get('location')
            age = request.form.get('age')
            contact = request.form.get('contact')
        
            client = Members(name = name, location = location, age = age, contact = contact, event_number = sr_number, event_name = events.name)
            db.session.add(client)
            db.session.commit()

            flash("event joind successfully...".title(), category = "success")
            return redirect(url_for('join_event'))

        return render_template('ejoin.html', user = str(session["user"]), event = events)

    return render_template('ejoin.html', user = None)






@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = db.session.query(RegisterUser).filter(RegisterUser.email == f'{email}').first()
        if user:
            if len(email) < 10:
                flash("Please enter a valid email.", category="error")
                return redirect(url_for('login'))
            
            elif ".com" not in email:
                flash("Please enter a valid email.", category="error")
                return redirect(url_for('login'))

            if bcrypt.check_password_hash(user.password, password):
                session["user"] = user.name
                flash("Logged in successfully!", category="success")
                return redirect(url_for('home', user = str(session["user"])))
            
            else:
                flash("Incorrect password! Try again.", category="error")
        
        else:
            flash("Email doesn't exist.", category="error")

    return render_template('login.html')


@app.route("/logout")
def logout():
    if "user" in session:
        session.pop('user')
        return render_template('index.html', user = None)


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user_email = db.session.query(RegisterUser).filter(RegisterUser.email == f'{email}').first()
        if user_email:
            flash("A user with this email already exists. Try again with another email.".title(), category="error")
            return render_template('signup.html')
        
        if len(name) < 3:
            flash("Name must be at least 3 characters.".title(), category="error")
            return render_template('signup.html')
        
        if len(email) < 10:
            flash("Email must be at least 10 characters.".title(), category="error")
            return render_template('signup.html')
        
        elif ".com" not in email:
            flash("Email must contain .com at the end.".title(), category="error")
            return render_template('signup.html')
        
        if password1 != password2:
            flash("Your password doesn\'t match.".title(), category="error")
            return render_template('signup.html')
        
        elif len(password1) < 6:
            flash("Password must be at least 6 characters".title(), category="error")
            return render_template('signup.html')
        
        else:
            try:
                hash_password = bcrypt.generate_password_hash(password1)
                register = RegisterUser(name = name, phone = phone, email = email, password = hash_password)
                db.session.add(register)
                db.session.commit()
                flash("Account created successfully. Please, Log in to access.".title(),
                    category="success")
                return redirect("/login")
            
            except Exception as e:
                flash("There is an error while creating account, please check your internet connection".title(), category = "error")
                return render_template('signup.html')

    return render_template('signup.html')


if __name__ == "__main__":
    app.run(debug=True)
