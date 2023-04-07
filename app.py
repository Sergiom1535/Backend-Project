from flask import Flask, render_template, request, redirect, url_for, session, abort
import pymysql
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
conn = pymysql.connect(
        host='localhost',
        user='root', 
        password = "Yeyo!535",
        db='Backend_proj',
		cursorclass=pymysql.cursors.DictCursor
        )
cur = conn.cursor()
@app.route('/')
@app.route('/register', methods = [ 'GET','POST'])
def register():
    Username = request.args.get('username')
    email = request.args.get('email')
    password = request.args.get('password')
    cur.execute('SELECT * FROM users WHERE Username = % s', (Username,))
    account = cur.fetchone()
    conn.commit()
    if account is not None:
        return 'account exist!'
        
    else:
        cur.execute('INSERT INTO users VALUES (NULL, % s, % s, % s)',(Username,email,password,))
        conn.commit()
        return 'account created'
    return 'DONE'






if __name__ == "__main__":
    	app.run(host ="localhost", port = int("5000"))