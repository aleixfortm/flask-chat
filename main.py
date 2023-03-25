from flask import Flask, render_template, request, session, redirect
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase

app = Flask(__name__)
app.config["SECRET_KEY"] = 'secret2'
socketio = SocketIO(app)

rooms = {}

def generate_code(length):
    while True:
        code = ''
        for _ in range(length):
            code += random.choice(ascii_uppercase)

        if code not in rooms:
            return code
    
@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == 'POST':
        name = request.form.get('name')
        code = request.form.get('code')
        join = request.form.get('join', False)
        create = request.form.get('create', False)

        if not name:
            return render_template("home.html", error='Please enter a valid name')
        
        if join != False and not code:
            return render_template('home.html', error='Please enter a valid room code')

        room = code
        if create != False:
            room = generate_code(4)
            rooms[room] = {'members': 0, 'messages': []}
            print(rooms)
        elif room not in rooms:
            return render_template('home.html', error='Specified room does not exist')

    return render_template("home.html")

if __name__ == '__main__':
    socketio.run(app, debug=True)