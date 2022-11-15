'''
2 Whites And A Gray: Gitae Park (PM), Brianna Tieu, Nada Hameed
SOFTDEV
P00
'''

'''
existing account used for testing:
    - user: octo
    - pass: dad
'''

import sqlite3

from flask import Flask, redirect, render_template, request, session, url_for

#================================== SQL ==================================#

# new database for logins and posts
DB_FILE="blog.db"

db = sqlite3.connect(DB_FILE, check_same_thread=False) #credit to the piazza post made by Team Scuba-Doo Dog Erasers
c = db.cursor()

# user login table
command = "create table IF NOT EXISTS logins (user TEXT, password TEXT)"
c.execute(command)
db.commit()

# blogs table
command = "create table IF NOT EXISTS blogs (blogName TEXT, username TEXT)"
#autoincrement automatically counts up for us as new entries are put into the database
c.execute(command)
db.commit()

# entries table
command="create table IF NOT EXISTS entries (blogName TEXT, user TEXT, entryTitle TEXT, postContent TEXT)"
c.execute(command)
db.commit()

#================================= FLASK =================================#
app = Flask(__name__)
app.secret_key = 'b_9#y2L"F4Q8z\n\xec]/'
#=========================================================================#

# displays all of the user's created blogs, double for loop to access the tuple data
def displayBlogs():
    blogList = c.execute("SELECT blogName FROM blogs where username = ?", (session['username'],)).fetchall() #fetches all the names of all the created blogs
    blogs_String = ""
    for blogs in blogList:
        for blog in blogs:
            blogs_String = blogs_String + blog + ', '
    return blogs_String [:-2]

'''
root of the page:
    - checks if the user is logged in or has an ongoing session
        - if so, they go to the home page
    - otherwise, login page
'''
@app.route("/")
def index():
    if 'username' in session:
        return render_template( 'home.html', status="Successfully logged in!", blogs=displayBlogs() )
    else:
        return render_template( 'login.html' )

'''
auth route:
    - checks for the user's inputted data in the login page to see if it matches with
    existing accounts in the database
'''
@app.route('/auth', methods=['GET', 'POST'])
def authenticate():

    username = request.form['username']
    password = request.form['password']

    c.execute("SELECT * FROM logins;")
    user_logins = c.fetchall()

    for user in user_logins:
        if username == user[0] and password == user[1]:
            session['username'] = username
            return render_template( 'home.html', status="Successfully logged in!", blogs=displayBlogs() )
        if username == user[0] and password != user[1]:
            return render_template( 'login.html', login="Invalid password!" )

    return render_template( 'login.html', login="Submitted username is not registered!" )

'''
register route:
    - changes the html template
'''
@app.route("/register")
def register():
    return render_template( 'register.html' )

'''
signup route:
    - checks if user's inputted username already exists in the database
        - if so, user must resubmit form
    - otherwise, user's login is inputted into the database and redirected back to log in
'''
@app.route("/signup", methods=['GET', 'POST'])
def signUp():

    newUser = request.form['username']
    newPass = request.form['password']

    c.execute("SELECT * FROM logins;")
    user_logins = c.fetchall()

    for user in user_logins:
        if newUser == user[0]:
            return render_template( 'register.html' , status="Submitted username is already in use.")

    c.execute("INSERT INTO logins VALUES (?,?);", (newUser, newPass))
    db.commit()
    return render_template( 'login.html', login="New user has been created successfully! Log in with your new credentials!" )

'''
logout route:
    - removes the user from the session
    - redirects them back to index function ( login page )
'''
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

'''
newblog route:
    - renders a new template for the user to create a new blog
'''
@app.route('/newblog')
def newBlog():
    return render_template( 'new_blog.html' )

'''
blog route:
    - checks if the desired blog name already exists
         - if so, user must resubmit the form
    - otherwise, blog is created and user is taken to the view page, where they can view all the website's existing blogs
'''
@app.route('/blog', methods=['GET', 'POST'])
def createBlog():
    c.execute("SELECT * FROM blogs")
    allBlogs = c.fetchall()

    for name in allBlogs:
        if request.form['blogName'] == name[0]:
            return render_template( 'new_blog.html', status="There is already an existing blog with this name! Try again." )

    c.execute("INSERT INTO blogs (blogName, username) VALUES (?,?);", (request.values['blogName'], session['username'],))
    db.commit()

    return render_template( 'home.html', blogs=displayBlogs() )

'''
newpost route:
    - renders a new template for the user to create a new post
'''
@app.route('/newpost')
def newPost():
    return render_template( 'new_post.html' )

'''
createpost route:
    - takes user input for blog name, entry name and content
    - creates an entry for the user's new post in the database
    - brings user back to the viewing page, where they can see all existing blogs with a message
    notifying that their post has been succesffuly created
'''
@app.route('/createpost', methods=['GET', 'POST'])
def createPost():
    c.execute("INSERT INTO entries VALUES (?,?,?,?);", (request.values['blog_name'], session['username'], request.values['entry_title'], request.values['postContent']))
    db.commit()
    allBlogs = c.execute("SELECT * FROM blogs").fetchall()
    return render_template( 'view.html', status = "Post has been successfully published!", blogList=allBlogs )

'''
view route:
    - shows user all existing blogs
'''
@app.route('/view', methods=['GET', 'POST'])
def view():
    allBlogs = c.execute("SELECT * FROM blogs").fetchall()
    return render_template( 'view.html', blogList=allBlogs )

'''
view/<blog> route:
    - dynamic route that shows the user all the entries that belong to a blog
'''
@app.route('/view/<blog>', methods=['GET', 'POST'])
def viewBlog(blog):
    allPosts = c.execute("SELECT * FROM entries WHERE blogName = ?", (blog,)).fetchall()
    return render_template( 'view_blog.html', blogName = blog, postList = allPosts )

'''
edit route:
    - shows the user all the blogs that they own so they can edit
'''
@app.route('/edit')
def edit():
    yourBlogs = c.execute("SELECT * FROM blogs WHERE username = ?", (session['username'],)).fetchall()
    return render_template( 'edit.html', blogList = yourBlogs )

'''
edit/<blog> route:
    - dynamic route that shows the user all the entries in a blog
'''
@app.route('/edit/<blog>', methods=['GET', 'POST'])
def editBlog(blog):
    allEntries = c.execute("SELECT * from entries WHERE blogName = ?", (blog,)).fetchall()
    return render_template( 'edit_blog.html', postList = allEntries, blogName = blog)

'''
edit/<blog>/<entry> route:
    - dynamic route that shows the user the entry that they are choosing to edit
'''
@app.route('/edit/<blog>/<entry>', methods=['GET', 'POST'])
def editEntry(blog, entry):
    entryList = c.execute("SELECT * from entries WHERE blogName = ? AND entryTitle = ?", (blog, entry)).fetchall()
    firstEntry = entryList[0]
    return render_template ( 'edit_entry.html', entryElements = firstEntry, blogName=blog, author=firstEntry[1], entryName=entry, content=firstEntry[3])

'''

!! ES BROKEN, the request.form.get('content') returns nothing / no updated text, request.values['content'] returns a BadRequestKeyError!!

update/<blog>/<entry> route:
    - dynamic route that updates the database with the new content
    - redirects the user back to the first editing page where they can see all their own blogs
'''
@app.route('/update/<blog>/<entry>', methods=['GET', 'POST'])
def updateEntry(blog, entry):
    c.execute("UPDATE entries SET postContent = ? WHERE blogName = ? AND entryTitle = ?", (request.form.get('content', False), blog, entry))
    return redirect(url_for('edit'))

if __name__ == "__main__":
    app.debug = True
    app.run()
