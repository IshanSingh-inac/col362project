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
from bigQuery import *
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
        if (items):
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

@app.route('/deleteAccount')
def deleteAccount():
    cur.execute("DELETE FROM users WHERE id = '{}'".format(g.user.id))
    con.commit()
    session.pop('user_id', None)
    return redirect(url_for('login'))

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
    cur.execute("with trending_companies(ticker, name) as \
        (\
            select tickers.ticker, tickers.name\
            from favourites, tickers\
            where favourites.ticker = tickers.ticker \
            group by tickers.ticker, tickers.name \
            order by count(favourites.id) desc, tickers.name asc\
        )\
        select * from trending_companies limit 10")
    trend = cur.fetchall()
    return render_template('companies.html',companies= companies,fav= fav, trend = trend)

@app.route('/analyze', methods = ['GET', 'POST'])
def analyze():
    if not g.user:
        return redirect(url_for('login'))
    if request.method == 'POST':
        global ticker_list
        ticker_list = request.form.getlist('mycheckbox')
        # print('ticker list = ',ticker_list)
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

@app.route('/toggleFollowing/<int:id>')
def toggleFollowing(id):
    if not g.user:
        return redirect(url_for('login'))
    cur.execute("SELECT * from following where id1 = '{}' and id2 = '{}'".format(g.user.id,id))
    items = cur.fetchone()
    if(not items):
        cur.execute("INSERT INTO following (id1,id2) VALUES(%s,%s)",(g.user.id,id))
        con.commit()
    else:
        cur.execute("DELETE FROM following WHERE id1 = %s and id2 = %s", (g.user.id,id))
        con.commit()
    return redirect(url_for('following'))

@app.route('/trending')
def trending():
    if not g.user:
        return redirect(url_for('login'))
    cur.execute("with trending_companies(ticker, name) as \
        (\
            select tickers.ticker, tickers.name\
            from favourites, tickers\
            where favourites.ticker = tickers.ticker \
            group by tickers.ticker, tickers.name \
            order by count(favourites.id) desc, tickers.name asc\
        )\
        select * from trending_companies limit 10")
    items = cur.fetchall()
    cur.execute("SELECT tickers.ticker,tickers.name from favourites,tickers where favourites.id = '{}' and favourites.ticker = tickers.ticker".format(g.user.id))
    fav = cur.fetchall()
    return render_template('trending.html', trend = items, fav = fav)

@app.route('/plot.svg')
def plot_png():
    fig = create_figure()
    output = io.BytesIO()
    FigureCanvasSVG(fig).print_svg(output)
    return Response(output.getvalue(), mimetype='image/svg+xml')

def create_figure():
    Y_arr = []
    X_arr = []
    legends_arr = []
    global ticker_list
    cur.execute("select date from stocks where ticker = '{}'".format(ticker_list[0]))
    X_arr = cur.fetchall()
    for ticker in ticker_list:
        cur.execute("select close from stocks where ticker = '{}'".format(ticker))
        close_arr = cur.fetchall()
        # print('close arr = ',close_arr)
        Y_arr.append(close_arr)
        cur.execute("select * from tickers where ticker = '{}'".format(ticker))
        ticker, comp_name = cur.fetchone()
        legends_arr.append(comp_name)

    fig = Figure()
    axis = fig.add_subplot(1,1,1)
    fig.suptitle('Stocks Analysis')
    axis.set_xlabel('Date (in year)')
    axis.set_ylabel('Closing value')
    for i in range(len(Y_arr)):
        axis.plot(X_arr, Y_arr[i], label = legends_arr[i])
    axis.legend(loc = "upper left")
    return fig

@app.route('/notes', methods = ['GET', 'POST'])
def notes():
    if not g.user:
        return redirect(url_for('login'))
    if request.method == 'POST':
        new_notes = request.form['Notes']
        cur.execute("insert into notes (id,note) VALUES(%s,%s)", (g.user.id,new_notes))
        con.commit()
        return redirect(url_for('notes'))

    cur.execute("select * from notes where id = {}".format(g.user.id))
    user_notes = cur.fetchall()
    # print('user notes = ',user_notes)
    return render_template('notes.html', user_notes = user_notes)

@app.route('/remove_notes/<string:note>')
def remove_notes(note):
    if not g.user:
        return redirect(url_for('login'))
    cur.execute("DELETE FROM notes WHERE id = %s and note = %s", (g.user.id,note))
    con.commit()
    return redirect(url_for('notes'))

@app.route('/edit_notes/<string:note>', methods = ['POST', 'GET'])
def edit_notes(note):
    if not g.user:
        return redirect(url_for('login'))
    if request.method == 'POST':
        new_note = request.form['updated_note']
        cur.execute("update notes set note = %s where notes.id = %s and notes.note = %s", (new_note,g.user.id,note))
        con.commit()
        return redirect(url_for('notes'))
    else:
        return render_template('edit_notes.html', note = note)

@app.route('/following')
def following():
    if not g.user:
        return redirect(url_for('login'))
    cur.execute("SELECT users.id,users.username from users")
    users = cur.fetchall()
    cur.execute("SELECT users.id,users.username from users, following where following.id1 = '{}' and following.id2 = users.id".format(g.user.id))
    following = cur.fetchall()
    cur.execute(followingFavQuery.format(g.user.id))
    followingFav = cur.fetchall()
    return render_template('following.html',users= users,following= following,followingFav=followingFav)

@app.route('/')
def home():
    return redirect(url_for('profile'))

if __name__ == "__main__":
    app.run(debug = True)