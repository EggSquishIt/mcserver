const tmi = require('tmi.js');
const fs = require('fs');
const readline = require('readline');

fs.readFile("twitch_identity.json", "utf8", function(err, data) {
	var identity = JSON.parse(data);

	var opts = {
		identity: identity,
		connection: {
			secure: true,
			reconnect: true
		},
		channels: [ 'EggSquishIt' ]
	};
	const client = new tmi.Client(opts);

	client.connect();

	client.on('message', function(channel, tags, message, self) {
		console.log(`${tags['display-name']}: ${message}`);
	});

	var con = readline.createInterface({
		input: process.stdin,
		output: process.stdout,
		terminal: false
	});

	con.on("line", function(line) {
		var re = /^([^ ]*) ([^ ]*) (.*)$/
		var match = line.match(re);
		var cmd = match[1];
		var target = match[2];
		var msg = match[3];

		switch(cmd) {
			case "say":
				client.say(target, msg);
				break;
			case "whisper":
				client.whisper(target, msg);
				break;
		}
	});

});
