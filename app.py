from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from urllib.parse import urlparse
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'  # Use environment variable for secret key

# Configure the SQLAlchemy part of the app instance
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://udjh022agk9u8s:p79faf817b42bc76733b02696eba79c0b923d362c858e671066e6d00ed9e001b9@c5hilnj7pn10vb.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d5qjhdfn08fv98'
db = SQLAlchemy(app)  # Initialize SQLAlchemy instance

# Define SQLAlchemy models for users and applications
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_title = db.Column(db.String(), nullable=False)
    company = db.Column(db.String(), nullable=False)
    status = db.Column(db.String(), nullable=False)
    applied_on = db.Column(db.Date, nullable=False)
    link = db.Column(db.Text)
    description = db.Column(db.Text)
    notes = db.Column(db.Text)

# Routes

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash('Username already exists.')
        else:
            hashed_pwd = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(username=username, password=hashed_pwd, email=email)
            db.session.add(new_user)
            db.session.commit()
            flash('Signup successful! Please login')
            return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials. Please try again.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        position = request.form['position']
        company = request.form['company']
        status = request.form['status']
        link = request.form['link']
        
        # Ensure user is logged in
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        # Create a new application record
        new_application = Application(
            user_id=session['user_id'],
            job_title=position,
            company=company,
            status=status,
            applied_on=datetime.now().date(),
            link=link
        )
        
        db.session.add(new_application)
        db.session.commit()
        
        apps = Application.query.filter_by(user_id=session['user_id']).all()
        return render_template('home.html', username=session['username'], apps=apps)
    
    if 'user_id' in session:
        apps = Application.query.filter_by(user_id=session['user_id']).all()
        return render_template('home.html', username=session['username'], apps=apps)
    else:
        return redirect(url_for('login'))
    
@app.route('/application/<int:application_id>')
def application(application_id):
    application = Application.query.filter_by(id=application_id, user_id=session['user_id']).first()
    if application:
        return render_template('application.html', application=application)
    else:
        flash('Application not found or unauthorized access.')
        return redirect(url_for('home'))
    
@app.route('/delete/<int:application_id>')
def delete(application_id):
    application = Application.query.filter_by(id=application_id, user_id=session['user_id']).first()
    if application:
        db.session.delete(application)
        db.session.commit()
        flash('Application deleted successfully')
    else:
        flash('Application not found or unauthorized access.')
    return redirect(url_for('home'))
    
@app.route('/update/<int:application_id>', methods=['POST'])
def update_status(application_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized access'}), 403

    new_val = request.form['value']
    field = request.form['field']
    
    application = Application.query.filter_by(id=application_id, user_id=session['user_id']).first()
    if not application:
        return jsonify({'error': 'Application not found or unauthorized access'}), 404
    
    setattr(application, field, new_val)
    db.session.commit()
    
    return jsonify({'message': 'Status updated successfully'})


@app.route('/scrape', methods=['POST'])
def scrape():
    linkedinurl = request.form['url']
    url = "https://api.scrapingdog.com/linkedinjobs"
    api_key = "6686860957b0cb18a4596e24"
    job_id = linkedinurl[35:45]

    params = {
        "api_key": api_key,
        "job_id": job_id
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()[0]
    
    position = data['job_position']
    company = data['company_name']
    description = data['job_description']
    location = data['job_location']
    pay = data['base_pay']

    status = request.form['status']
    link = linkedinurl
    
    new_application = Application(
        user_id=session['user_id'],
        job_title=position,
        company=company,
        status=status,
        applied_on=datetime.now().date(),
        link=link,
        description=description
    )
    
    db.session.add(new_application)
    db.session.commit()
    
    apps = Application.query.filter_by(user_id=session['user_id']).all()
    return render_template('home.html', username=session['username'], apps=apps)


if __name__ == '__main__':
    app.run(debug=True)