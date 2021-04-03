from flask import (
    Flask,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
    flash,
    Response
)
import psycopg2
import random
from models import *
from dbDetails import *
from functools import wraps
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.backends.backend_svg import FigureCanvasSVG
from matplotlib.figure import Figure
import io

con = psycopg2.connect(dbname=DBNAME, user=DBUSER, host=DBHOST, password=DBPASSWORD)
cur = con.cursor()

app = Flask(__name__)
app.secret_key = 'somesecretkeythatonlyishouldknow'
ticker_list = [] 

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

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password2 = request.form['password2']
        gender = request.form['gender']

        cur.execute("SELECT * from users where username = '{}'".format(username))
        items = cur.fetchone()
        if(items):
            return render_template('signup.html', error="Username already taken")
        elif(password != password2):
            return render_template('signup.html', error="Passwords don't match")
        else:
            cur.execute("SELECT * from users")
            items = cur.fetchall()
            cur.execute("INSERT INTO users (id,username,gender,password) VALUES(%s,%s,%s,%s)", ((len(items))+1,username,gender,password))
            con.commit()
            return redirect(url_for('login'))

    return render_template('signup.html')

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
    cur.execute("SELECT * from tickers")
    companies = cur.fetchall()
    # print(companies)
    cur.execute("SELECT tickers.ticker,tickers.name from favourites,tickers where favourites.id = '{}' and favourites.ticker = tickers.ticker".format(g.user.id))
    fav = cur.fetchall()
    return render_template('companies.html',companies= companies,fav= fav)

@app.route('/analyze', methods = ['GET', 'POST'])
def analyze():
    if not g.user:
        return redirect(url_for('login'))
    if request.method == 'POST':
        global ticker_list
        ticker_list = request.form.getlist('mycheckbox')
        print('ticker list = ',ticker_list)
        return render_template('graph.html')

    cur.execute("SELECT tickers.ticker,tickers.name from favourites,tickers where favourites.id = '{}' and favourites.ticker = tickers.ticker".format(g.user.id))
    fav = cur.fetchall()
    return render_template('analyze.html', fav = fav)
    
@app.route('/toggleFavourites/<string:ticker>')
def toggleFavourites(ticker):
    if not g.user:
        return redirect(url_for('login'))
    cur.execute("SELECT * from favourites where id = '{}' and ticker = '{}'".format(g.user.id,ticker))
    items = cur.fetchone()
    if(not items):
        cur.execute("INSERT INTO favourites (id,ticker) VALUES(%s,%s)", (g.user.id,ticker))
        con.commit()
    else:
        cur.execute("DELETE FROM favourites WHERE id = %s and ticker = %s", (g.user.id,ticker))
        con.commit()
    return redirect(url_for('companies'))

@app.route('/plot.svg')
def plot_png():
    fig = create_figure()
    output = io.BytesIO()
    FigureCanvasSVG(fig).print_svg(output)
    return Response(output.getvalue(), mimetype='image/svg+xml')

def create_figure():
    min_x = 1000000000
    Y_arr = []
    global ticker_list
    for ticker in ticker_list:
        cur.execute("select close from stocks where ticker = '{}'".format(ticker))
        close_arr = cur.fetchall()
        print('close arr = ',close_arr)
        min_x = min(min_x, len(close_arr))
        Y_arr.append(close_arr)
        X_arr = range(min_x)

    fig = Figure()
    axis = fig.add_subplot(1,1,1)
    for y in Y_arr:
        axis.plot(X_arr, y[0:min_x])
    return fig

# @app.route('/plot.png')
# def plot_png():
#     fig = create_figure()
#     output = io.BytesIO()
#     FigureCanvas(fig).print_png(output)
#     return Response(output.getvalue(), mimetype='image/png')

# def create_figure():
#     fig = Figure()
#     axis = fig.add_subplot(1, 1, 1)
    # xs = range(100)
    # ys = [random.randint(1, 50) for x in xs]
    # axis.plot(xs, ys)
    # return fig

@app.route('/')
def home():
    return "Home"

if __name__ == "__main__":
    app.run(debug = True)