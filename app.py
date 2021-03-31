from flask import (
    Flask,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
    flash
)
import psycopg2
from models import *
from dbDetails import *
from functools import wraps

con = psycopg2.connect(dbname=DBNAME, user=DBUSER, host=DBHOST, password=DBPASSWORD)
cur = con.cursor()

app = Flask(__name__)
app.secret_key = 'somesecretkeythatonlyishouldknow'

@app.before_request
def before_request():
    g.user = None
    if session and session['user_id']:
        cur.execute("SELECT * from users where id = '{}'".format(session['user_id']))
        items = cur.fetchone()
        print("Before request executed")
        g.user = User(id=items[0], username=items[1], gender = items[2], password=items[3])
        
        

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form['username']
        password = request.form['password']
        
        cur.execute("SELECT * from users where username = '{}' and password = '{}'".format(username,password))
        items = cur.fetchone()
        if(not items):
            return render_template('login.html', error="Invalid credentials")
        else:
            user = User(id=items[0], username=items[1], gender = items[2], password=items[3])
            session['user_id'] = user.id
            return redirect(url_for('profile'))

    return render_template('login.html')

@app.route('/profile')
def profile():
    if not g.user:
        return redirect(url_for('login'))
    return render_template('profile.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/companies')
def companies():
    if not g.user:
        return redirect(url_for('login'))
    cur.execute("SELECT name from tickers")
    items = cur.fetchall()
    items = items[1:5]
    return render_template('companies.html',items= items)
    

@app.route('/')
def home():
    return "Home"

if __name__ == "__main__":
    app.run(debug = True)