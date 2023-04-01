from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase


app = Flask(__name__)
app.config["SECRET_KEY"] = 'secret2'
socketio = SocketIO(app)


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

    # Generates random RGB values
    r = 255
    g = random.randint(0, 255)
    b = random.randint(0, 255)

    colors = [r, g, b]
    random.shuffle(colors)

    return tuple(colors)
   

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
    # Redirect to home page if requirements not met (e.g. trying to access lobby without specifying name or lobby code)
    room = session.get('room')
    name = session.get('name')

    existent_user = False
    existent_lobby = False
    if name != None and room in rooms:
        existent_lobby = True
        for user in rooms[room]['users']:
            if user['name'] == name:
                existent_user = True

    if room is None or name is None or room not in rooms or existent_user or not existent_lobby:
        return redirect(url_for('home'))
    
    # render html block for lobby page, passing code variable to display
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


# Set server_cobfig as local or public. Local server will run by default on port 5000
server_config = 'local'

if __name__ == '__main__':
    if server_config == 'local':
        socketio.run(app, debug=True)
    
    elif server_config == 'public':
        socketio.run(app, port=8080, host='0.0.0.0')