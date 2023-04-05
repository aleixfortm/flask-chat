from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase

# Declare server app and required config
app = Flask(__name__)
socketio = SocketIO(app)

# Set to local or public. Local server will run by default on port 5000. Public will run on port 8080.
server_config = 'local'

# Declare variables
rooms = {}
used_colors = []

def generate_code(length):

    #Generates random non-existent 4-digit code
    while True:
        code = ''
        for _ in range(length):
            code += random.choice(ascii_uppercase)

        if code not in rooms:
            return code


def generate_color():
    global used_colors

    # Randomise r, g, b values. By setting one of them to 255, the resulting color will be bright
    r = 255
    g = random.randint(0, 255)
    b = random.randint(0, 255)

    # Shuffle values
    colors = [r, g, b]
    random.shuffle(colors)
    
    return tuple(colors)
   

# Main server route
@app.route("/", methods=["POST", "GET"])
def home():

    # Clear session data for a new client
    session.clear()

    # If client is sending data to the server via POST request, save that data
    if request.method == 'POST':
        name = request.form.get('name')
        code = request.form.get('code')
        join = request.form.get('join', False)
        create = request.form.get('create', False)

        # Display errors on home screen if received data is not valid
        if not name:
            return render_template("home.html", error='Provide a valid name', code=code, name=name)
        if join != False and not code:
            return render_template('home.html', error='Please enter a valid room code', code=code, name=name)


        room = code
        # Creates new lobby if received a True 'create' argument
        if create != False:
            room = generate_code(4)
            rooms[room] = {'n_users': 0, 'users': []}
            print(rooms)
        # If 'create' argument is false and specified room is non-existent, return client to home and display error
        elif code not in rooms:
            return render_template('home.html', error='Specified room does not exist', code=code, name=name)

        # Save room code and username on client's session
        session['room'] = room
        session['name'] = name
        
        # Redirect client to room route if passed all previous tests
        return redirect(url_for('room'))
    
    # Redirect client to home page if request sent was not POST
    return render_template("home.html")


# Room route will check if client is elegible to load room template -- Send back home otherwise
@app.route("/room")
def room():

    # Redirect to home page if requirements not met (e.g. trying to access lobby without specifying name or lobby code)
    room = session.get('room')
    name = session.get('name')

    # Check whether username and room already exist
    existent_user = False
    existent_lobby = False
    if name != None and room in rooms:
        existent_lobby = True
        for user in rooms[room]['users']:
            if user['name'] == name:
                existent_user = True

    # Redirect client back to home page if one of the following conditions is met (not passed test)
    if room is None or name is None or room not in rooms or existent_user or not existent_lobby:
        return redirect(url_for('home'))
    
    # Load client-side room template if passed all tests
    return render_template('room.html', code=room)


@socketio.on('message')
def message(data):
    room = session.get("room")
    if room not in rooms:
        return

    user_name = session.get("name")
    existent_user = False

    for i, user in enumerate(rooms[room]['users']):
        if user['name'] == user_name:
            existent_user = True
            pos = i
            color = user['color']
            break 
    
    if not existent_user:
        color = generate_color()
    
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
    print(f"{session.get('name')} said: {data['data']}")


# Socket connection (e.g. connecting players to certain lobbies or sending messages to several clients)
@socketio.on('connect')
def connect(auth):
    room = session.get('room')
    name = session.get('name')
    
    # WIP -----------------------------
    existent_user = False
    if room in rooms:
        for user in rooms[room]['users']:
            if user['name'] == name:
                existent_user = True
                break 
    # ---------------------------------

    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return

    join_room(room)

    color = generate_color()
    message = "has joined the lobby"
    content = {
            "name": name,
            "color": color,
            "message": message,
            "n_users": rooms[room]['n_users'] + 1,
            }

    send(content, to=room)
    
    rooms[room]['users'].append(content)
    rooms[room]["n_users"] += 1
    print(f'{name} joined room {room}')


@socketio.on('disconnect')
def disconnect():
    room = session.get('room')
    name = session.get('name')

    leave_room(room)
    
    user_list = rooms[room]['users']
    for user in user_list:
        if user['name'] == name:
            color = user['color']
            user_list.remove(user)
            break 

    if room in rooms:
        rooms[room]['n_users'] -= 1
        if rooms[room]['n_users'] <= 0:
            del rooms[room]
    
    message = 'has left the lobby'
    content = {
            "name": name,
            "color": color,
            "message": message,
            "n_users": rooms[room]['n_users'],
            }

    send(content, to=room)
    print(f"{name} has left room {room}")


if __name__ == '__main__':
    if server_config == 'local':
        socketio.run(app, debug=True)
    
    elif server_config == 'public':
        socketio.run(app, port=8080, host='0.0.0.0')
