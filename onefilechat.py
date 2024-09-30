from flask import Flask, request, jsonify, render_template_string, session
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this to a secure key in production
socketio = SocketIO(app)

# In-memory storage for chat messages
chat_messages = []

# HTML template for the chat page
chat_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            margin-top: 50px;
        }
        #chat-container {
            background-color: #f1f1f1;
            padding: 10px;
            border: 1px solid #ccc;
            overflow-y: scroll;
            height: 300px;
            margin-bottom: 20px;
        }
        #username-input {
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div id="username-input">
        <label for="username">Username:</label>
        <input type="text" id="username" name="username" required>
        <button onclick="setUsername()">Set Username</button>
    </div>
    <div id="chat-container">
        <h2>Chat</h2>
        <ul id="chat-list"></ul>
    </div>
    <div id="chat-input">
        <form id="chat-form">
            <input type="text" id="chat-message" name="message" required>
            <button type="submit">Send</button>
        </form>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.0/socket.io.js"></script>
    <script>
        const socket = io();
        let username = '';

        function setUsername() {
            username = document.getElementById('username').value;
            document.getElementById('username-input').style.display = 'none';
            loadMessages();
        }

        document.getElementById('chat-form').addEventListener('submit', function(event) {
            event.preventDefault();
            if (username) {
                const message = document.getElementById('chat-message').value;
                socket.emit('send_message', { message: message, username: username });
                document.getElementById('chat-message').value = '';
            } else {
                alert('Please set a username first.');
            }
        });

        socket.on('receive_message', function(data) {
            const chatList = document.getElementById('chat-list');
            const li = document.createElement('li');
            li.textContent = `${data.username}: ${data.message}`;
            chatList.appendChild(li);
            chatList.scrollTop = chatList.scrollHeight;
        });

        function loadMessages() {
            fetch('/get_messages')
            .then(response => response.json())
            .then(data => {
                const chatList = document.getElementById('chat-list');
                chatList.innerHTML = '';
                if (data.status === 'success') {
                    data.messages.forEach(message => {
                        const li = document.createElement('li');
                        li.textContent = message;
                        chatList.appendChild(li);
                    });
                } else {
                    const li = document.createElement('li');
                    li.textContent = 'No messages yet.';
                    chatList.appendChild(li);
                }
            });
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(chat_html)

@socketio.on('send_message')
def handle_send_message(data):
    message = data['message']
    username = data['username']
    chat_messages.append(f"{username}: {message}")
    emit('receive_message', {'username': username, 'message': message}, broadcast=True)

@app.route('/get_messages', methods=['GET'])
def get_messages():
    return jsonify({"status": "success", "messages": chat_messages})

if __name__ == '__main__':
    socketio.run(app, debug=True, port=8000, host="0.0.0.0")
