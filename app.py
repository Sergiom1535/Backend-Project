from flask import Flask
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



if __name__ == "__main__":
    	app.run(host ="localhost", port = int("5000"))