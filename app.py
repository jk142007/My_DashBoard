from flask import Flask, render_template, request, redirect, session, url_for
import random
import requests
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Database setup
DB_NAME = os.path.join(os.path.dirname(__file__), 'database.db')

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Dashboard
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

# Registration (Sign Up)
@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ""
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                           (name, email, password))
            conn.commit()
            message = "Registration successful! You can now log in."
        except sqlite3.IntegrityError:
            message = "Email already exists. Please try a different one."
        finally:
            conn.close()
    return render_template('register.html', message=message)

# Login (Sign In)
@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['user'] = user[1]  # user's name
            return redirect(url_for('dashboard'))
        else:
            message = "Invalid credentials."
    return render_template('login.html', message=message)

# View Users
@app.route('/view-users')
def view_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email FROM users")
    users = cursor.fetchall()
    conn.close()
    return render_template('view_users.html', users=users)

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('dashboard'))

# Calculator
@app.route('/calculator', methods=['GET', 'POST'])
def calculator():
    result = ""
    if request.method == 'POST':
        num1 = float(request.form['num1'])
        num2 = float(request.form['num2'])
        operation = request.form['operation']
        if operation == 'add':
            result = num1 + num2
        elif operation == 'subtract':
            result = num1 - num2
        elif operation == 'multiply':
            result = num1 * num2
        elif operation == 'divide':
            result = num1 / num2 if num2 != 0 else "Error: Division by zero"
    return render_template('calc.html', result=result)

# Currency Converter
@app.route('/converter', methods=['GET', 'POST'])
def converter():
    result = ""
    if request.method == 'POST':
        amount = float(request.form['amount'])
        rate = float(request.form['rate'])
        from_currency = request.form['from_currency']
        to_currency = request.form['to_currency']
        converted_amount = amount * rate
        result = f"{amount} {from_currency} = {converted_amount} {to_currency}"
    return render_template('currcon.html', result=result)

# Guessing Game
secret_number = random.randint(1, 100)

@app.route('/guess', methods=['GET', 'POST'])
def guess():
    global secret_number
    message = ""
    if request.method == 'POST':
        guess = int(request.form['guess'])
        if guess < secret_number:
            message = "Too low!"
        elif guess > secret_number:
            message = "Too high!"
        else:
            message = "Correct! Generating new number..."
            secret_number = random.randint(1, 100)
    return render_template('guess.html', message=message)

# Rock Paper Scissors
@app.route('/rps', methods=['GET', 'POST'])
def rps():
    result = ""
    if request.method == 'POST':
        user_choice = request.form['choice']
        computer_choice = random.choice(['rock', 'paper', 'scissors'])
        if user_choice == computer_choice:
            result = "It's a tie!"
        elif (
            (user_choice == 'rock' and computer_choice == 'scissors')
            or (user_choice == 'paper' and computer_choice == 'rock')
            or (user_choice == 'scissors' and computer_choice == 'paper')
        ):
            result = "You win!"
        else:
            result = "Computer wins!"
        result += f" Computer chose {computer_choice}."
    return render_template('rps.html', result=result)

# Quote
@app.route('/quote')
def quote():
    quotes = [
        ("The only limit to our realization of tomorrow is our doubts of today.", "Franklin D. Roosevelt"),
        ("Do not wait to strike till the iron is hot; but make it hot by striking.", "William Butler Yeats"),
        ("Success is not final, failure is not fatal: it is the courage to continue that counts.", "Winston Churchill"),
        ("Believe you can and you're halfway there.", "Theodore Roosevelt"),
        ("It always seems impossible until it’s done.", "Nelson Mandela")
    ]
    selected_quote = random.choice(quotes)
    quote_text, author = selected_quote
    return render_template('quote.html', quote=quote_text, author=author)

# Weather
API_KEY = '80347c83aec8713c87281bed836cc250'

@app.route('/weather', methods=['GET', 'POST'])
def weather():
    weather_data = None
    if request.method == 'POST':
        city = request.form['city']
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            weather_data = {
                'city': data['name'],
                'temperature': data['main']['temp'],
                'description': data['weather'][0]['description'].title(),
            }
        else:
            weather_data = {'error': 'City not found'}
    return render_template('weather.html', weather=weather_data)

# Feedback Page
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form['name']
        message = request.form['message']
        with open("feedback.txt", "a") as f:
            f.write(f"Name: {name}\nMessage: {message}\n---\n")
        return render_template('feedback.html', thank_you=True, name=name)
    return render_template('feedback.html', thank_you=False)

if __name__ == '__main__':
    app.run(debug=True)
