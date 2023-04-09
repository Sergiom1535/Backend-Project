from flask import Flask, render_template, request, redirect, url_for, session, abort, make_response,jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import jwt
import pymysql
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
conn = pymysql.connect(
        host='localhost',
        user='root', 
        password = "Yeyo!535",
        db='Backend_proj',
		cursorclass=pymysql.cursors.DictCursor
        )

app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOAD_PATH'] = 'uploads'
app.config['SECRET_KEY']='my_keys'


cur = conn.cursor()

def token_required(func):
    @wraps(func)
    def decorated(*args,**kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'Alert':'Token is missing'})
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'Alert':'Invalid Token'})
    return decorated

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/')
def home():
    if not session.get('logged_in'):
        return 'user not logged in'
    else:
        return 'logged in'

@app.route('/auth')
@token_required
def auth():
    return 'JWT is Verified'

@app.route('/', methods=['POST'])
def upload_files():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
    if file_ext not in app.config['UPLOAD_EXTENSIONS']:
        return make_response('Not a valid file extension',415)
    uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
    return redirect(url_for('index'))




@app.route('/register', methods = [ 'GET','POST'])
def register():
    Username = request.args.get('username')
    email = request.args.get('email')
    password = request.args.get('password')
    cur.execute('SELECT * FROM users WHERE Username = % s', (Username,))
    account = cur.fetchone()
    conn.commit()
    if account is not None:
        return make_response('account exist!',406)
        
    else:
        cur.execute('INSERT INTO users VALUES (NULL, % s, % s, % s)',(Username,email,password,))
        conn.commit()
        return 'account created'
    return 'DONE'

@app.route('/login', methods = ['GET','POST'])
def login():
    Username = request.args.get('username')
    password = request.args.get('password')
    cur.execute('SELECT * FROM users WHERE Username = %s AND password = % s',(Username,password))
    account = cur.fetchone()
    conn.commit()
    if account is None:

        return make_response('invalid username/password!',404)
        
    else:
        session['logged_in'] = True
        token = jwt.encode({
            'Username': request.args.get('username'),
            'expiration': str(datetime.utcnow() + timedelta(seconds =120))
        },
            app.config['SECRET_KEY'])
        return (jsonify({'token': token.decode('utf-8')}),'loggin successful')

    return ' '

@app.route('/public', methods = [ 'GET','POST'])
def public():
    cur.execute('SELECT Username FROM users')
    usernames = cur.fetchall()
    conn.commit()
    return usernames






if __name__ == "__main__":
    	app.run(host ="localhost", port = int("5000"))