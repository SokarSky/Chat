from flask import render_template, request, redirect, url_for, session, g
from flask_login import login_user, logout_user, current_user, login_required
from flask_socketio import SocketIO, emit, join_room, leave_room,close_room, rooms, disconnect
from app import app, db, lm, socketio, thread
from app.forms import LoginForm, PasswordForm, RegistryFrom
from app.db_select import checkNickname, addUser, initUser, loadUser, createRoom, addUserInRoom
from time import gmtime, strftime
from random import random
from re import split




@lm.user_loader
def load_user(nickname):
	return loadUser(nickname)


@app.before_request
def before_request():
	g.user = current_user


@app.route('/', methods=["GET", "POST"])
@app.route('/index/', methods=["GET", "POST"])
@login_required
def index():
	return render_template('user_page.html', user=g.user)


@app.route('/registry/', methods=["GET", "POST"])
@app.route('/login/', methods=["GET", "POST"])
def login():
	LogForm = LoginForm()
	
	if LogForm.validate_on_submit():
		nickname = LogForm.nickname.data
		session['remember_me'] = LogForm.remember_me.data
		
		if checkNickname(nickname):
			return redirect(url_for('password', nickname=nickname))
		else:
			return redirect(url_for('registry', nickname=nickname))
	else:
		return render_template('login.html', form=LogForm)


@app.route('/login/<nickname>', methods=["GET", "POST"])
def password(nickname):
	PasForm = PasswordForm()
	
	if PasForm.validate_on_submit():
		password = PasForm.password.data
		remember_me = False
		if 'remember_me' in session:
			remember_me = session['remember_me']
			session.pop('remember_me', None)
		user = initUser(nickname, password)
		if user == False:
			return render_template('password.html', form=PasForm, nickname=nickname, errorPass = 'Wrong password')
		login_user(user, remember = remember_me)
		return redirect(url_for('index'))

	if checkNickname(nickname):
		return render_template('password.html', form=PasForm, nickname=nickname)
	else:
		return redirect(url_for('registry', nickname=nickname))


@app.route('/registry/<nickname>', methods=["GET", "POST"])
def registry(nickname):
	RegForm = RegistryFrom()

	if RegForm.validate_on_submit():
		password = RegForm.password.data
		addUser(nickname, password)
		remember_me = False
		if 'remember_me' in session:
			remember_me = session['remember_me']
			session.pop('remember_me', None)
		user = initUser(nickname, password)
		login_user(user, remember = remember_me)
		return redirect(url_for('index'))

	if checkNickname(nickname):
		return redirect(url_for('password', nickname=nickname))
	else:
		return render_template('registry.html', form=RegForm, nickname=nickname)

	
@app.route('/logout/')
@login_required
def logout():
	logout_user()
	return redirect(url_for('login'))



def background_thread():
	pass
	"""Example of how to send server generated events to clients."""
"""	count = 0
	while True:
		socketio.sleep(10)
		count += 1
		socketio.emit('my_response', {'data': 'Server generated event', 'count': count}, namespace='/test')"""



@socketio.on('leave', namespace='/test')
def leave(message):
	leave_room(message['room'])
	for c in current_user.chats:
		if str(c.chat.id) == message['room']:
			db.session.delete(c)
			db.session.commit()
			datetime = strftime("%H:%M:%S  %d.%m.%Y", gmtime())
			emit('my_response', {'data': current_user.nickname+' left the chat ', 'user': '', 'room': message['room'], 'date':datetime}, room=message['room'])



@socketio.on('my_room_event', namespace='/test')
def send_room_message(message):
	if message['data']!= "":
		datetime = strftime("%H:%M:%S  %d.%m.%Y", gmtime())
		emit('my_response', {'data': message['data'], 'user': current_user.nickname, 'room': message['room'], 'date':datetime, 'color':colorUser()}, room=message['room'])
		writeLog(current_user.nickname, datetime, message['data'], message['room'])



@socketio.on('connect', namespace='/test')
def test_connect():
	global thread
	if thread is None:
		thread = socketio.start_background_task(target=background_thread)
	
	for c in current_user.chats:
		join_room(str(c.chat.id))
		string=readLog(str(c.chat.id))
		for s in string[1:-1]:
			mess = split("\t", s)
			#if mess[2] is not None:
			emit('my_response', {'data': mess[2], 'user': mess[0], 'room': str(c.chat.id), 'date':mess[1]})
		


@socketio.on('create_room', namespace='/test')
def create_room(message):
	room = createRoom(message['room'], current_user)
	datetime = strftime("%H:%M:%S  %d.%m.%Y", gmtime())
	writeLog(current_user.nickname, datetime, "", str(room.id))
	emit('service', {'data': 'reload page'})
	


@socketio.on('add_user', namespace='/test')
def add_user(message):
	room = int(message['room'])
	
	for c in current_user.chats:
		if c.chat.id == room:
			if addUserInRoom(room, message['user']):
				datetime = strftime("%H:%M:%S  %d.%m.%Y", gmtime())
				emit('my_response', {'data': current_user.nickname+' invited the user ' + message['user'], 'user': '', 'room': str(room), 'date':datetime}, room=str(room))
				emit('service', {'data': 'add user', 'nickname':message['user'], 'room':str(room)}, room=str(room))
			
	
def colorUser():
	if 'color' in session:
		color = session['color']
	else:
		r = int(random() * 256)
		g = int(random() * 256)
		b = int(random() * 256)
		color = "#%02x%02x%02x" % (r,g,b)
		session['color'] = color
	return color


def writeLog(nickname, date, data, room):
	logFile = open("log/"+room+".log", "ab")
	string=(nickname + "\t" + date + "\t" + data + "\t\n").encode('utf-8')
	logFile.write(string)
	logFile.close()


def readLog(room):
	logFile = open("log/"+room+".log", "rb")
	string=logFile.read().decode('utf-8')
	string=split("\t\n", string)
	logFile.close()
	return string

