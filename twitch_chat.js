const tmi = require('tmi.js');
const fs = require('fs');

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
});
