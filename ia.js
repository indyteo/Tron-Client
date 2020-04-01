var net = require("net");
var methods = require("methods");
var move;

const ia = {
	id: null,
	name: "IA",
	pos: new Array(2),
	board: null,
	size: new Array(2),
	moves: ["LEFT", "UP", "RIGHT", "DOWN"],
	direction: null
};

var connexion = net.createConnection({port: 8000, host: "localhost"}, () => {
	connexion.write(ia.name);
});

function setup_callback(data) {
	var msg = data.toString();
	console.log(msg);
	if (! isNaN(Number(msg))) {
		ia.id = Number(msg);
	}
	else {
		var size, pos;
		msg = msg.split(";");
		size = methods.toIntArray(msg[0].split(":"));
		pos = methods.toIntArray(msg[1].split(":"));
		ia.board = methods.createArrayZero(size[0], size[1]);
		ia.pos = pos;
		ia.size = size;
		
		ia.board[0][Math.trunc(ia.size[1] / 2)] = 1;
		ia.board[Math.trunc(ia.size[0] / 2)][0] = 1;
		ia.board[ia.size[0] - 1][Math.trunc(ia.size[1] / 2)] = 1;
		ia.board[Math.trunc(ia.size[0] / 2)][ia.size[1] - 1] = 1;
		
		connexion.removeListener("data", setup_callback);
		connexion.on("data", update_board);
		start();
	}
}

connexion.on("data", setup_callback);

function start() {
	if (ia.pos[0] == 0)
		ia.direction = 2;
	else if (ia.pos[0] == ia.size[0] - 1)
		ia.direction = 0;
	else if (ia.pos[1] == 0)
		ia.direction = 2;
	else
		ia.direction = 0;
	
	move();
}

function canMove(move) {
	if ((ia.pos[0] == 0 && move == "LEFT")
			|| (ia.pos[0] == ia.size[0] - 1 && move == "RIGHT")
			|| (ia.pos[1] == 0 && move == "UP")
			|| (ia.pos[1] == ia.size[1] - 1 && move == "DOWN"))
		return false;

	let pos_provisoire = [ia.pos[0], ia.pos[1]];
	
	if (move == "UP")
		pos_provisoire[1] -= 1;
	else if (move == "DOWN")
		pos_provisoire[1] += 1;
	else if (move == "LEFT")
		pos_provisoire[0] -= 1;
	else
		pos_provisoire[0] += 1;
	
	return pos_provisoire[0] >= 0 && pos_provisoire[0] < ia.size[0] && pos_provisoire[1] >= 0 && pos_provisoire[1] < ia.size[1] && ia.board[pos_provisoire[0]][pos_provisoire[1]] == 0;
}

function update_board(data) {
	var msg = data.toString();
	console.log("Données reçues : " + msg);
	
	var positions = msg.split(";");
	for (var i = 0; i < positions.length; i++) {
		positions[i] = methods.parsePos(positions[i], ia.size);
		if (positions[i])
			ia.board[positions[i][0]][positions[i][1]] = 1;
	}
	ia.pos = positions[ia.id];
	
	console.log("On est en : " + ia.pos[0] + ", " + ia.pos[1]);
	
	move();
}

function move() {
	let index = ia.direction, move = ia.moves[index];
	while (! canMove(move)) {
		index = (index + 1) % 4;
		move = ia.moves[index];
	}
	connexion.write(move);
}

connexion.on("error", (err) => {
	console.error(err);
});

connexion.on("close", () => {
	console.log("Fermeture de la connexion");
});