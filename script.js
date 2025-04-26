document.addEventListener('DOMContentLoaded', function() {
    const usernameInput = document.getElementById('username');
    const joinChannelNameInput = document.getElementById('join-channel-name');
    const joinPasswordInput = document.getElementById('join-password');
    const createChannelNameInput = document.getElementById('create-channel-name');
    const createPasswordField = document.getElementById('create-password');
    const enablePasswordCheckbox = document.getElementById('enable-password');
    const joinButton = document.getElementById('join-button');
    const createButton = document.getElementById('create-button');
    const createPasswordLabel = document.querySelector('#create-channel-section label[for="create-password"]');

    // WebSocket connection
    const ws = new WebSocket('ws://localhost:8765');

    ws.onopen = function() {
        console.log('WebSocket connection established.');
    };

    ws.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);
            console.log('Received message:', data);

            if (data.type === 'joined') {
                const username = usernameInput.value;
                const channel = data.channel;
                console.log('About to redirect to chat.html'); // Added log
                window.location.href = `chat.html?username=${encodeURIComponent(username)}&channel=${encodeURIComponent(channel)}`;
                console.log('Redirected to chat.html'); // Added log (this might not execute if redirect is immediate)
            } else if (data.type === 'error') {
                alert('Error: ' + data.message);
            }
        } catch (error) {
            console.error('Error processing message from server:', error);
        }
    };

    ws.onclose = function() {
        console.log('WebSocket connection closed.');
    };

    ws.onerror = function(error) {
        console.error('WebSocket error:', error);
        console.trace(); // Added stack trace
    };

    // Toggle visibility of create password field
    if (enablePasswordCheckbox && createPasswordField && createPasswordLabel) {
        enablePasswordCheckbox.addEventListener('change', function() {
            createPasswordField.style.display = this.checked ? 'block' : 'none';
            createPasswordLabel.style.display = this.checked ? 'block' : 'none';
        });
    }

    // Handle Join button click
    if (joinButton) {
        joinButton.addEventListener('click', function() {
            console.log('Join button clicked.'); // Added log
            const username = usernameInput.value.trim();
            const channel = joinChannelNameInput.value.trim();
            const password = joinPasswordInput.value;

            if (username && channel) {
                console.log('Sending join message.'); // Added log
                ws.send(JSON.stringify({
                    action: 'join',
                    username: username,
                    channel: channel,
                    password: password
                }));
                console.log('Join message sent.'); // Added log
            } else {
                alert('Please enter a username and channel name to join.');
            }
        });
    }

    // Handle Create button click
    if (createButton) {
        createButton.addEventListener('click', function() {
            console.log('Create button clicked.'); // Added log
            const username = usernameInput.value.trim();
            const channel = createChannelNameInput.value.trim();
            const password = enablePasswordCheckbox.checked ? createPasswordField.value : null;

            if (username && channel) {
                console.log('Sending create message.'); // Added log
                ws.send(JSON.stringify({
                    action: 'create',
                    username: username,
                    channel: channel,
                    password: password
                }));
                console.log('Create message sent.'); // Added log
            } else {
                alert('Please enter a username and channel name to create.');
            }
        });
    }
});