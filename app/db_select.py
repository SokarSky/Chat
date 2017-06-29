from app import models, db, app
import base64
import uuid
import hashlib

def checkNickname(nickname):
	user = models.User.query.get(nickname)
	if user is not None:
		return True
	else:
		return False


def addUser(nickname, password):
	if not checkNickname(nickname):
		password = get_hash_password(password, app.config['SECRET_KEY'])
		u = models.User(nickname=nickname, password=password)
		db.session.add(u)
		db.session.commit()


def initUser(nickname, password):
	user = models.User.query.get(nickname)
	password = get_hash_password(password, app.config['SECRET_KEY'])
	if user.nickname == nickname and user.password == password:
		return user
	else:
		return False 


def loadUser(nickname):
	return models.User.query.get(nickname)


def createRoom(name, user):
	c=models.Chat(name=name)
	db.session.add(c)
	cu=models.ChatUser(userNickname=user.nickname, chatId=c.id)
	db.session.add(cu)
	db.session.commit()
	return c


def addUserInRoom(room, nickname):
	if checkNickname(nickname):
		cu=models.ChatUser(userNickname=nickname,chatId=int(room))
		db.session.add(cu)
		db.session.commit()
		return True



def get_hash_password(password, salt = None):
	if salt == None:
		salt = uuid.uuid4().hex
	text = password.encode('utf-8') + salt.encode('utf-8')
	h = hashlib.sha512()
	h.update(text)
	return str(h.hexdigest())



