'''
2 Whites And A Gray: Gitae Parl (PM), Brianna Tieu, Nada Hameed
SOFTDEV
P00
'''

from flask import Flask, session, render_remplate, request, redirect, url_for
import sqlite3

# new database for logins and posts
DB_FILE="blog.db"

db = sqlite3.connect(DB_FILE)
c = db.cursor()

# user login table
command = "create table logins (user TEXT, password TEXT)"
c.execute(command)
db.commit()

# FLASK #
app = Flask(__name__)
app.secret.key = 'b_9#y2L"F4Q8z\n\xec]/'

@app.route("/")
def index():
    if 'user' in session:
        return redirect(url_for('home'))
    else:
        return render_template( 'login.html' )

#@app.route('/auth', methods=['GET', 'POST'])
#def authenticate():