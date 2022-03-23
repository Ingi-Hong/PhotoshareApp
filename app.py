######################################
# author ben lawson <balawson@bu.edu>
# Edited by: Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

from getpass import getuser
import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask_login
import time 

#for image uploading
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'pro097'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from users")
users = cursor.fetchall()

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from users")
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	
	
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd
	return user

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT password FROM users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('hello.html', message='Logged out')

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html')

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
	return render_template('register.html', supress='True')

@app.route("/register", methods=['POST'])
def register_user():
	try:
		first_name = request.form.get('first_name')
		last_name = request.form.get ('last_name')
		
		email=request.form.get('email')
		password=request.form.get('password')
		
	except:
		print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	if test:
		print(cursor.execute("INSERT INTO users (email, password, is_registered,first_name, last_name) VALUES ('{0}', '{1}', 1, '{2}','{3}')".format(email, password, first_name, last_name)))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		
		flask_login.login_user(user)
		return render_template('hello.html', name=email, message='Account Created!')
	else:
		print("couldn't find all tokens")
		return flask.redirect(flask.url_for('register'))

def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT data, p_id, caption FROM photos WHERE owner_id= '{0}'".format(uid))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT email FROM users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM users WHERE email = '{0}'".format(email)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True

def isTagUnique (tag):
	cursor= conn.cursor()
	if cursor.execute("Select tag FROM tags WHERE tag = '{0}'".format(tag)):
		return False
	else:
		return True

def getComments(p_id):
	cursor = conn.cursor()
	cursor.execute("SELECT text, uid, date FROM comments WHERE pid = '{0}'".format(p_id))
	return cursor.fetchall()\

def getUsersAlbums(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT name,date,owner_id,a_id FROM albums WHERE owner_id = '{0}' ".format(uid))
	return cursor.fetchall()\

def getAllPhotos():
	cursor = conn.cursor()
	cursor.execute("SELECT data, p_id, caption FROM photos")
	return cursor.fetchall()\

def getUsersFriends(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT first_name, last_name, email FROM users WHERE email IN (SELECT user2 FROM friends WHERE user1 = '{0}') ".format(uid))
	return cursor.fetchall()\

def getTaggedPhotos(tags):
	cursor = conn.cursor()
	cursor.execute("SELECT data, p_id, caption FROM photos WHERE p_id IN (SELECT p_id FROM tagged_photos WHERE tags = '{0}') ".format(tags))
	return cursor.fetchall()\

#end login code

@app.route('/profile')
@flask_login.login_required
def protected():
	return render_template('hello.html', name=flask_login.current_user.id, message="Here's your profile")

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		photo_data = imgfile.read()
		album = request.form.get('album')
		tags = request.form.get('tags')
		albums = getUsersAlbums(uid)
		print(album)
		print(albums)
		check = [item for item in albums if item[0] == album]

		try:
			a_id = check[0][3]
			print(a_id)
		except:
			return render_template('hello.html', name=flask_login.current_user.id, message='Create Album First!', photos=getUsersPhotos(uid),base64=base64)



		cursor = conn.cursor()
		cursor.execute("INSERT INTO photos (data, caption, a_id, owner_id) VALUES (%s, %s, %s, %s)", (photo_data, caption, a_id, uid))

		conn.commit()
		if tags != None:
			if isTagUnique(tags):
				cursor.execute("INSERT INTO tags (tag) VALUES (%s)", (tags))
				conn.commit()
			cursor.execute("INSERT INTO tagged_photos (tags) VALUES (%s)", (tags))
			conn.commit()

		return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPhotos(uid),base64=base64)
	#The method is GET so we return a HTML form to upload the a photo.
	else:
		return render_template('upload.html')
#end photo uploading code

#album
@app.route ('/create', methods = ['GET', 'POST'])
@flask_login.login_required
def create_album():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		a_name = request.form.get ('album name')
		date = request.form.get ('date')
		cursor = conn.cursor()
		cursor.execute("INSERT INTO albums (Name, date, owner_id) VALUES (%s, %s,%s)",(a_name, date, uid))
		
		conn.commit()
		return render_template('hello.html', name = flask_login.current_user.id, message = 'Album Created', albums = getUsersAlbums(uid), base64=base64 )
	
	else: 
		return render_template('create.html')

 #photos library
@app.route ('/photos',methods=['GET'])
@flask_login.login_required 
def photo_library():
	if request.method == 'GET':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		return render_template('photos.html', name= flask_login.current_user.id,message = ' Photo Library', photos=getAllPhotos(),base64=base64)
	else:
		return render_template('hello.html')


@app.route('/comments/<pid>', methods = ['GET','POST'])
@flask_login.login_required
def comment_section(pid):
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		p_id = pid
		text = request.form.get('text')
		cursor = conn.cursor()
		cursor.execute("INSERT INTO comments (text,date,uid, pid) VALUES (%s,%s,%s, %s)",(text, time.strftime('%Y-%m-%d'), uid, p_id))
		conn.commit()
		return render_template('comments.html', name = flask_login.current_user.id, message= 'Comment Posted', comments = getComments(p_id),base64=base64, p_id = p_id, uid = uid )
	else: 
		uid = getUserIdFromEmail(flask_login.current_user.id)
		p_id = pid 
		return render_template('comments.html', name = flask_login.current_user.id, message= 'Comments', comments = getComments(p_id),base64=base64, p_id = p_id, uid = uid)
    	
@app.route('/social', methods = ['GET', 'POST'])
@flask_login.login_required
def social():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	friends = getUsersFriends(uid)

	if request.method == 'GET':
		return render_template('social.html', name = flask_login.current_user.id, friends = friends)
	else:
		if 'search' in request.form:
			search = request.form.get("search")
			cursor = conn.cursor()
			cursor.execute("SELECT first_name, last_name, email FROM users WHERE first_name LIKE '%{0}%' OR last_name LIKE '%{1}%'".format(search, search))
			searched = cursor.fetchall()
			return render_template('social.html', name = flask_login.current_user.id, searched = searched, friends = friends)

		else:
			email = request.form.get("friendrequest")
			cursor = conn.cursor()

			# Check to see if friendship exists 
			if cursor.execute("SELECT user1, user2 FROM friends WHERE user1 = '{0}' and user2 = '{1}'".format(email, uid)):
				#this means there are greater than zero entries with that email
				return render_template('social.html', name = flask_login.current_user.id, message="Friend Already Added!")

			cursor.execute("INSERT INTO friends (user1, user2) VALUES (%s, %s)", (uid, email))
			cursor.execute("INSERT INTO friends (user1, user2) VALUES (%s, %s)", (email, uid))
			conn.commit()
			return render_template('social.html', name = flask_login.current_user.id, message="Friend added!", friends = friends)


@app.route ('/tags', methods = ['GET', 'POST'])
@flask_login.login_required
def tags():
	if request.method == 'POST':
		tags = request.form.get("tags")
		
		tagged = getTaggedPhotos(tags)

		return render_template('tags.html', name= flask_login.current_user.id, message = "Found",tagged = tagged , base64 = base64)

	else: 
		tags = request.form.get("tags")
		cursor = conn.cursor()
		cursor.execute("SELECT tags, COUNT(*) AS magnitude FROM tagged_photos GROUP BY tags ORDER BY magnitude DESC LIMIT 5")
		famous = cursor.fetchall()
		print(" ")
		print(" ")
		print(" ")
		print(famous)
		print(" ")
		print(" ")
		print(" ")
		return render_template('tags.html', name= flask_login.current_user.id, message = "Found", famous = famous, base64=base64)



#default page
@app.route("/", methods=['GET'])
def hello():
	return render_template('hello.html', message='Welecome to Photoshare')

if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)


