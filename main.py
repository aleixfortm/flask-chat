from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase

app = Flask(__name__)
app.config["SECRET_KEY"] = 'secret2'
socketio = SocketIO(app)


rooms = {}

def generate_code(length):
    #Generates random non-existent 4-digit code
    while True:
        code = ''
        for _ in range(length):
            code += random.choice(ascii_uppercase)

        if code not in rooms:
            return code

def generate_color():
    # Generates random RGB values
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    colors = [r, g, b]
    # Makes one of the colors imperatively bright
    """
    n = random.randint(0, 2)
    colors[n] = random.randint(170, 255)
    colors = tuple(colors)
    """
    return colors
   

@app.route("/", methods=["POST", "GET"])
def home():

    session.clear()

    if request.method == 'POST':
        name = request.form.get('name')
        code = request.form.get('code')
        join = request.form.get('join', False)
        create = request.form.get('create', False)

        if not name:
            return render_template("home.html", error='Provide a valid name', code=code, name=name)
        
        if join != False and not code:
            return render_template('home.html', error='Please enter a valid room code', code=code, name=name)

        room = code
        if create != False:
            room = generate_code(4)
            rooms[room] = {'n_users': 0, 'users': []}
            print(rooms)
        elif code not in rooms:
            return render_template('home.html', error='Specified room does not exist', code=code, name=name)

        session['room'] = room
        session['name'] = name
        
        return redirect(url_for('room'))
    
    # render html block for home page, passing no variables
    return render_template("home.html")

@app.route("/room")
def room():
    
    # Avoid joining room directly from navbar
    room = session.get('room')
    if room is None or session.get('name') is None or room not in rooms:
        return redirect(url_for('home'))

    # render html block for lobby page, passing code variable to display
    return render_template('room.html', code=room)


@socketio.on('message')
def message(data):
    room = session.get("room")
    if room not in rooms:
        return
    
    # Check if user already in dict so no need to generate color again
    # Maybe check if possible to pass it to session and retrieve it from there (?)
    
    user_name = session.get("name")
    existent_user = False
    color = generate_color()

    for i, user in enumerate(rooms[room]['users']):
        if user['name'] == user_name:
            existent_user = True
            pos = i
            color = user['color']
            break 

    content = {
            "name": user_name,
            "color": color,
            "message": data["data"],
            }


    if existent_user:
        rooms[room]["users"][pos] = content
    else:
        rooms[room]["users"].append(content)

    send(content, to=room)
    
    print(rooms)
    print(f" {session.get('name')} said: {data['data']}")

# Socket connection (e.g. connecting players to certain lobbies or sending messages to several clients)
@socketio.on('connect')
def connect(auth):
    room = session.get('room')
    name = session.get('name')
    # Make sure they have provided room and name
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    send({"name": name, "message": "has joined the lobby"}, to=room)
    
    rooms[room]["n_users"] += 1 
    print(f'{name} joined room {room}')

@socketio.on('disconnect')
def disconnect():
    room = session.get('room')
    name = session.get('name')
    
    leave_room(room)
    
    if room in rooms:
        rooms[room]['n_users'] -= 1
        if rooms[room]['n_users'] <= 0:
            del rooms[room]
        
    send({"name": name, "message": "has left the lobby"}, to=room)
    
    print(f"{name} has left the room {room}")


if __name__ == '__main__':
    socketio.run(app)