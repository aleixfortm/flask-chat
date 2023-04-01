var socketio = io();

const createJoinMessage = (name, msg, color='white', n_users) => {
    lobby_members.innerHTML = n_users;

    const content =  `
    <div class='text'>
        <span class='msg-full'>
            <strong id='msg-name' style='color: rgb(${color})'>${name} </strong> <strong style='color: #b7ffb0'>${msg}</strong>
        </span>
        <!-- <span class='muted'>${new Date().toLocaleString()}</span> (add date to message)-->
    </div>
    `;

    messages.innerHTML += content;
};


const createMessage = (name, msg, color='red') => {
    const content =  `
    <div class='text'>
        <span class='msg-full'>
            <strong id='msg-name' style='color: rgb(${color})'>${name} </strong>${msg}
        </span>
        <!-- <span class='muted'>${new Date().toLocaleString()}</span> (add date to message)-->
    </div>
    `;
    
    messages.innerHTML = content;
};

const createLeaveMessage = (name, msg, color='white', n_users=1) => {
    lobby_members.innerHTML = n_users;

    const content =  `
    <div class='text'>
        <span class='msg-full'>
            <strong id='msg-name' style='color: rgb(${color})'>${name} </strong><strong style='color: #ff7676'>${msg}</strong>
        </span>
        <!-- <span class='muted'>${new Date().toLocaleString()}</span> (add date to message)-->
    </div>
    `;
    
    messages.innerHTML += content;
};


socketio.on('message', (data) => {
    if (data.message === 'has joined the lobby') {
        createJoinMessage(data.name, data.message, data.color, data.n_users);


    }else if (data.message === 'has left the lobby') {

        createLeaveMessage(data.name, data.message, data.color, data.n_users);

    }else{

        createMessage(data.name, data.message, data.color);

    }
})

// Fetches data from message input box and emits it to socketio
const sendMessage = () => {
    const message = document.getElementById('message');
    if (message.value == "") return;
    socketio.emit('message', {data: message.value});
    message.value = '';
}

// Sends message upon hitting Enter
const msgForm = document.getElementById('content');
msgForm.addEventListener('keydown', (event) => {
    if (event.key === 'Enter'){
        sendMessage();
    }
})