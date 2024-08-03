from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from db import add_user, get_user_by_name, add_application, get_applications_by_user, get_application_by_id, delete_application_by_id, update_application_by_id
from werkzeug.security import check_password_hash
import requests
import os
from openai import OpenAI

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get('OPENAI_KEY')
)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'secret')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        existing_user = get_user_by_name(username)

        if existing_user:
            flash('Username already exists.')
        else:
            add_user(username, password, email)
            flash('Signup successful! Please login')
            return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user_by_name(username)

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
        add_application(session['user_id'], position, company, status, link)
        apps = get_applications_by_user(session['user_id'])
        return render_template('home.html', username=session['username'], apps=apps)
    if 'user_id' in session:
        apps = get_applications_by_user(session['user_id'])
        return render_template('home.html', username=session['username'], apps=apps)
    else:
        return render_template('landing.html')
    
@app.route('/application/<int:application_id>', methods=['GET', 'POST'])
def application(application_id):
    application = get_application_by_id(application_id)

    if request.method == 'POST':
        instructions = request.form['instructions']
        description = get_application_by_id(application_id).description
        letter = gen_cover_letter(description, instructions)
        if application and application.user_id == session['user_id']:
            return render_template('application.html', application=application, letter=letter)
    if application and application.user_id == session['user_id']:
        return render_template('application.html', application=application)
    
@app.route('/delete/<int:application_id>')
def delete(application_id):
    delete_application_by_id(application_id, session['user_id'])
    flash('Application deleted successfully')
    return redirect(url_for('home'))
    
@app.route('/update/<int:application_id>', methods=['POST'])
def update_status(application_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized access'}), 403

    new_val = request.form['value']
    field = request.form['field']
    update_application_by_id(application_id, session['user_id'], field, new_val)
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
    add_application(session['user_id'], position, company, status, link, description)
    apps = get_applications_by_user(session['user_id'])
    return redirect(url_for('home'))


def gen_cover_letter(desc, data):
    prompt = f"Write a cover letter for the following job description: {desc} and follow these instructions: {data}"
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-3.5-turbo",
    )
    
    return chat_completion.choices[0].message.content

if __name__ == '__main__':
    app.run(debug=True)

  