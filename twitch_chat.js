const tmi = require('tmi.js');
const fs = require('fs');
const readline = require('readline');

function runChat(identity) {
	var opts = {
		connection: {
			secure: true,
			reconnect: true
		},
		channels: [ 'EggSquishIt' ]
	};
	if(identity !== null) {
		opts.identity = identity;
	}

	const client = new tmi.Client(opts);

	client.connect().catch(function(e) {
		if(e === "Login authentication failed") {
			identity = null;
		}
		console.log("Failed to connect: " + JSON.stringify(e));
		setTimeout(function() {
			runChat(identity);
		}, 5000);
	}).then(function() {
		client.on('message', function(channel, tags, message, self) {
			console.log("<" + tags['display-name'] + "> " + message);
		});

		var con = readline.createInterface({
			input: process.stdin,
			output: process.stdout,
			terminal: false
		});

		con.on("line", function(line) {
			var re = /^([^ ]*) ([^ ]*) (.*)$/
			var match = line.match(re);
			try {
				var cmd = match[1];
				var target = match[2];
				var msg = match[3];

				switch(cmd) {
					case "say":
						client.say(target, msg).catch(function(e) {
							console.log("Failed to send twitch message to " + target + ": " + msg);
							console.log("Error was " + e);
						});
						break;
					case "whisper":
						client.whisper(target, msg).catch(function(e) {});
							console.log("Failed to send twitch whisper to " + target + ": " + msg);
							console.log("Error was " + e);
						break;
				}
			} catch(e) {
			}
		});
	});
}

fs.readFile("twitch_identity.json", "utf8", function(err, data) {
	var identity = null;
	if(err === null) {
		try {
			identity = JSON.parse(data);
		} catch(e) {
			identity = null;
		}
	}
	runChat(identity);
});
