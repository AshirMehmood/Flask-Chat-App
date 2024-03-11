'''
real time chat room project using SocketIO
'''
from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


# unnamed method(can only do one task like handling json)
@socketio.on('json')
def handle_json(json):
    print('received json: ' + str(json))



# Custom named event can support multiple arguements
@socketio.on("my_event")
def handle_my_custom_event(json, arg1, arg2, arg3):
    print(f"recieved json: " + str(json)
          + "recieved args {arg1} {arg2} {arg3} ")



if __name__ == '__main__':
    socketio.run(app)

