// script.js

var socket = io();

socket.on('connect', function() {
    console.log('Connected to server');
});

socket.on('process_status', function(data) {
    // Display process status in the status div
    $('#status').text('Status: ' + data);
    
    // Optionally, alert the user with the status message
    alert(data);
});

function startProcess() {
    socket.emit('start_process');

    // Example countdown logic (optional)
    var count = 10;
    var countdownInterval = setInterval(function() {
        $('#status').text('Starting VID_BOT in ' + count + ' seconds...');
        count--;
        if (count < 0) {
            clearInterval(countdownInterval);
            $('#status').text('VID_BOT is running');
        }
    }, 1000);

    // After countdown, request current process status
    setTimeout(function() {
        socket.emit('get_process_status');
    }, 10000); // Wait 10 seconds (same as countdown) before checking status
}

function stopProcess() {
    socket.emit('stop_process');
}

function restartProcess() {
    socket.emit('restart_process');

    // Example countdown logic for restart (optional)
    var count = 10;
    var countdownInterval = setInterval(function() {
        $('#status').text('Restarting VID_BOT in ' + count + ' seconds...');
        count--;
        if (count < 0) {
            clearInterval(countdownInterval);
            $('#status').text('VID_BOT is running');
        }
    }, 1000);

    // After countdown, request current process status
    setTimeout(function() {
        socket.emit('get_process_status');
    }, 10000); // Wait 10 seconds (same as countdown) before checking status
}
