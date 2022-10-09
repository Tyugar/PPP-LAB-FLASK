from multiprocessing.reduction import duplicate
from flask import Flask, session, request, render_template, redirect,url_for
from flask_session import Session
import sqlite3


app = Flask("Flask - lab")

sess = Session()

DATABASE = 'database.db'

@app.before_first_request
def appInit():
    app.logger.info("before_first_request")
    conn = sqlite3.connect(DATABASE)
    conn.execute('CREATE TABLE IF NOT EXISTS  users (username TEXT, password TEXT, admin INTEGER)')
    conn.execute('CREATE TABLE IF NOT EXISTS cars (make TEXT, model TEXT, year INTEGER)')
    #TODO sprawic zeby nie wpisywalo dwa razy tego samego usera ;]
    conn.execute('INSERT INTO USERS (username,password,admin) VALUES ("admin","admin",1)')
    conn.commit()
    conn.close()


@app.route("/", methods=['GET', 'POST'])
def index():
    if 'user' in session:
        return render_template('index.html', isAdmin = isUserAdmin(session['user']), cars = getAllCars())
    else:
        return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    if (isUserExist(request.form['login'],request.form['password'])):
        session['user']=request.form['login']
        return index()
    else:
        return "Wrong login or password" + render_template('login.html')



@app.route('/logout', methods=['GET'])
def logout():
    if 'user' in session:
        session.pop('user')
    else:
        redirect(url_for('index'))
    return "Loged out <br>  <a href='/'> Come back </a>"


def isUserExist(name,password):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ? AND password = ?", (name,password))
    data=cur.fetchall()
    if len(data)==0:
        return False
    else:
        return True

@app.route('/addCar', methods=['POST'])
def addCar():
        make = request.form['make']
        model = request.form['model']
        year = request.form['year']

        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        cur.execute('INSERT INTO CARS (make,model,year) VALUES (?,?,?)',(make,model,year))
        con.commit()
        con.close()

        return redirect(url_for('index'))

@app.route('/addUser', methods=['POST'])
def addUser():
    login = request.form['login']
    password = request.form['password']
    if request.form.get('admin'):
        admin = 1
    else:
        admin = 0 
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute("INSERT INTO USERS (username,password,admin) VALUES (?,?,?)",(login,password,admin))
    con.commit()
    con.close()

    return redirect(url_for('users'))

@app.route("/users", methods=['GET'])
def users():
    if 'user' in session and isUserAdmin(session['user']):
        return render_template('users.html',users=getAllUsers())
    elif 'user' in session and not isUserAdmin(session['user']):
        return render_template('index.html')
    else:
        return render_template('login.html')

def getAllCars():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM cars")
    return cur.fetchall()

#TODO DODAC JAKIES ID DO TEGO 
def getAllUsers():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    return cur.fetchall()


#TODO dokonczyc to
def isUserAdmin(name):
    return True

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
sess.init_app(app)
app.config.from_object(__name__)
app.debug = True
app.run()

