var socketio = io();

const messages = document.getElementById('messages');

const createMessage = (name, msg) => {
    const content =  `
    <div class='text'>
        <span class='msg-full'>
            <strong id='msg-name'>${name}</strong>
            <br>${msg}
        </span>
        <!-- <span class='muted'>${new Date().toLocaleString()}</span> (add date to message)-->
    </div>
    `;
    messages.innerHTML += content;
};

socketio.on('message', (data) => {
    createMessage(data.name, data.message);
  
})

const sendMessage = () => {
    const message = document.getElementById('message');
    if (message.value == "") return;
    socketio.emit('message', {data: message.value});
    message.value = '';
}