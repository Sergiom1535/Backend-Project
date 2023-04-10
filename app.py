from flask import Flask, render_template, request, redirect, url_for, session, abort, make_response,jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import jwt
import pymysql
from datetime import datetime, timedelta
from functools import wraps

# our mysql db connection
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
conn = pymysql.connect(
        host='localhost',
        user='root', 
        password = "Yeyo!535",
        db='Backend_proj',
		cursorclass=pymysql.cursors.DictCursor
        )
# our app.configs for our file upload and our secrete keys for jwt
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOAD_PATH'] = 'uploads'
app.config['SECRET_KEY']='my_keys'


cur = conn.cursor()

#Jwt token creation
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
#api route for our file upload
@app.route('/')
def index():
    #send user to our index page  that has our form for file uploads
    return render_template("index.html")

@app.route('/home')
def home():
    #route is used to check if the user is logged in and authenticated
    if not session.get('logged_in'):
        #sends a 401 unathenticated error and message
        return make_response('not authenticate',401)
        return 'user not logged in'
    else:
        return 'logged in'

@app.route('/auth')
@token_required
def auth():
    return 'JWT is Verified'
#file upload route
@app.route('/', methods=['POST'])
def upload_files():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        #checks to see if file extension is valid extension
    if file_ext not in app.config['UPLOAD_EXTENSIONS']:
        #sends error and message if not a valid extension
        return make_response('Not a valid file extension',415)
        #send our file to our folder to save it
    uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
    #redirects our user back to index page
    return redirect(url_for('index'))



#route to register user
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
#login route 
@app.route('/login', methods = ['GET','POST'])
def login():
    #url takes ursname and password
    Username = request.args.get('username')
    password = request.args.get('password')
    cur.execute('SELECT * FROM users WHERE Username = %s AND password = % s',(Username,password))
    account = cur.fetchone()
    conn.commit()
    if account is None:
        #checks db if user enter valid credentials and sends message and 404 error
        return make_response('invalid username/password!',404)
        
    else:
        #if user loggin is succesful it return jwt token
        session['logged_in'] = True
        token = jwt.encode({
            'Username': request.args.get('username'),
            'expiration': str(datetime.utcnow() + timedelta(seconds =120))
        },
            app.config['SECRET_KEY'])
        return (jsonify({'token': token.decode('utf-8')}),'loggin successful')

    return ' '
#public route that does not need authentication or loggin to retrieve usernames that are taken
@app.route('/public', methods = [ 'GET','POST'])
def public():
    cur.execute('SELECT Username FROM users')
    usernames = cur.fetchall()
    conn.commit()
    return usernames






if __name__ == "__main__":
    	app.run(host ="localhost", port = int("5000"))