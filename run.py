#!venv/bin/python
#-*- coding:cp1251 -*-
from app import socketio, app
socketio.run(app, debug=True, host='0.0.0.0')

