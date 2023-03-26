var socketio = io();

const messages = document.getElementById('messages');

const createMessage = (name, msg) => {
    const content = `
    <div class='text'>
        <span>
            <strong>${name}</strong>: ${msg}
        </span>
        <span class='muted'
            ${new Date().toLocaleString()}
        </span>
    </div>
    `;
    messages.innerHTML += content;
};

socketio.on('message', (data) => {
    createMessage(data.name, data.message);
})

const sendMessage = () => {
    console.log('send')
}