from app import db


class ChatUser(db.Model):
	__tablename__ = 'ChatUser'
	userNickname = db.Column(db.Text, db.ForeignKey('User.nickname'), primary_key=True)
	chatId = db.Column(db.Integer, db.ForeignKey('Chat.id'), primary_key=True)

	chat = db.relationship("Chat", back_populates="users")
	user = db.relationship("User", back_populates="chats")

	def __repr__(self):
		return '<User: %r, Chat: %r>' % (self.userNickname, self.chatId)


class User(db.Model):
	__tablename__ = 'User'
	nickname = db.Column(db.Text, primary_key=True)
	password = db.Column(db.Text)
	chats = db.relationship("ChatUser", back_populates="user")

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return self.nickname

	def __repr__(self):
		return '<User %r>' % (self.nickname)


class Chat(db.Model):
	__tablename__ = 'Chat'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.Text)
	users = db.relationship("ChatUser", back_populates="chat")


	def __repr__(self):
		return '<Chat %r>' % (self.id)

