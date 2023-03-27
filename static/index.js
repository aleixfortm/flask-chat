var socketio = io();

const createJoinMessage = (name, msg, color='black') => {
    const content =  `
    <div class='text'>
        <span class='msg-full'>
            <strong id='msg-name' style='color:${color}'>${name} </strong> <a style='color: darkgreen'>${msg}</a>
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
            <strong id='msg-name' style='color: ${color}'>${name}: </strong>${msg}
        </span>
        <!-- <span class='muted'>${new Date().toLocaleString()}</span> (add date to message)-->
    </div>
    `;
    
    messages.innerHTML += content;
};

const createLeaveMessage = (name, msg, color='black') => {
    const content =  `
    <div class='text'>
        <span class='msg-full'>
            <strong id='msg-name' style='color: ${color}'>${name} </strong><a style='color: firebrick'>${msg}</a>
        </span>
        <!-- <span class='muted'>${new Date().toLocaleString()}</span> (add date to message)-->
    </div>
    `;
    
    messages.innerHTML += content;
};


socketio.on('message', (data) => {
    if (data.message === 'has joined the lobby') {

        createJoinMessage(data.name, data.message, data.color);

    }else if (data.message === 'has left the lobby') {

        createLeaveMessage(data.name, data.message, data.color)   

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
// Sends message upon clicking 'send' button
const sendButton = document.getElementById('send-btn');
sendButton.addEventListener('click', () => {
    sendMessage();
    /*
    const nameColor = document.getElementById('msg-name');
    nameColor.style.color = "red";
    */
})


