//var socket = io.connect("http://localhost:5000");
var socket = io.connect("https://");
socket.on('connect', function () {
    socket.emit('echo', {data: 'Im connected!'});
})

var gameState = {};
socket.on('game', function (data) {
    // update DOM according to new message
    console.log("Received game data");
    console.log(data);
    gameState = data;
});

socket.on('requpdate', function (data) {
    console.log("update requested")
    socket.emit('game', game_id);
});

socket.on('error', function (data) {
    alert("invalid move");
});

socket.on('gameover', function (winner) {
    if (winner === "you") {
        alert("You win!");
    }
    else {
        alert("You lose!");
    }
});

socket.emit('game', game_id); // game_id is hard-coded with the template engine

