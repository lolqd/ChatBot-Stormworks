port = 600
sf = string.format

function onCreate(is_world_create)
	server.announce("Server","Chat addon reload...")
end

function onPlayerJoin(steam_id, name, peer_id, admin, auth)
	data = sf("/Join/steam_id = %s: name = %s", steam_id, name)
	server.httpGet(port, data)
end

function onPlayerLeave(steam_id, name, peer_id, is_admin, is_auth)
	data = sf("/Leave/steam_id = %s: name = %s", steam_id, name)
	server.httpGet(port, data)
end

function onChatMessage(user_peer_id, sender_name, message, steam_id)
	data = sf("/Message/sender_n = %s: user_peer_id = %d: message = %s: steam_id = %s:", sender_name, user_peer_id, message, steam_id)
	server.httpGet(port, data)
end