import libtcodpy as libtcod
import util
import map
import game


def handle_keys():
	key = libtcod.console_check_for_keypress(libtcod.KEY_PRESSED)
	if key.vk == libtcod.KEY_ENTER and key.lalt:
		libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
	elif key.vk == libtcod.KEY_ESCAPE:
		return 'exit'

	if game.game_state == 'playing':
		if key.vk == libtcod.KEY_UP:
			player_move_or_attack(0, -1)
		elif key.vk == libtcod.KEY_DOWN:
			player_move_or_attack(0, 1)
		elif key.vk == libtcod.KEY_LEFT:
			player_move_or_attack(-1, 0)
		elif key.vk == libtcod.KEY_RIGHT:
			player_move_or_attack(1, 0)
		elif key.vk == libtcod.KEY_SPACE:
			player_move_or_attack(0, 0)
		else:
			key_char = chr(key.c)

			if key_char == 'c':
				close_door()
			if key_char == 'd':
				drop_item()
			if key_char == 'g':
				pickup_item()
			if key_char == 'i':
				inventory()
			if key_char == 'l':
				look()
			if key_char == 'o':
				open_door()

			return 'didnt-take-turn'


def player_move_or_attack(dx, dy):
	#the coordinates the player is moving to/attacking
	x = game.char.x + dx
	y = game.char.y + dy

	#try to find an attackable object there
	target = None
#	for object in maps.objects:
#		if object.fighter and object.x == x and object.y == y:
#			target = object
#			break

	#attack if target found, move otherwise
	if target is not None:
		game.char.fighter.attack(target)
	else:
		game.char.move(dx, dy, game.current_map)
		game.fov_recompute = True


# close door
def close_door():
	game.message.new('Close door in which direction?', game.player.turns)
	util.render_all()
	libtcod.console_flush()
	dx = 0
	dy = 0

	key = libtcod.console_wait_for_keypress(True)
	if key.vk == libtcod.KEY_UP:
		dy = -1
	elif key.vk == libtcod.KEY_DOWN:
		dy = 1
	elif key.vk == libtcod.KEY_LEFT:
		dx = -1
	elif key.vk == libtcod.KEY_RIGHT:
		dx = 1

	if game.current_map.tiles[game.char.x + dx][game.char.y + dy].name == 'opened door':
		game.current_map.tiles[game.char.x + dx][game.char.y + dy].icon = '+'
		game.current_map.tiles[game.char.x + dx][game.char.y + dy].name = 'door'
		game.current_map.tiles[game.char.x + dx][game.char.y + dy].color = libtcod.dark_orange
		game.current_map.tiles[game.char.x + dx][game.char.y + dy].dark_color = libtcod.darkest_orange
		game.current_map.tiles[game.char.x + dx][game.char.y + dy].blocked = True
		game.current_map.tiles[game.char.x + dx][game.char.y + dy].block_sight = True
		game.player.turns += 1
		game.message.new('You close the door.', game.player.turns)
		game.fov_recompute = True
		util.initialize_fov()
		util.render_all()
	elif game.current_map.tiles[game.char.x + dx][game.char.y + dy].name == 'door':
		game.message.new('That door is already closed!', game.player.turns, libtcod.red)
	elif dx != 0 or dy != 0:
		game.message.new('There is no door in that direction!', game.player.turns, libtcod.red)


# drop an item
def drop_item():
	if len(game.player.inventory) == 0:
		game.message.new('Your inventory is empty.', game.player.turns, libtcod.white)
	else:
		choice = util.msg_box('drop', 'Drop an item', 'Up/down to select, ENTER to drop, ESC to exit')
		if choice != -1:
			print choice
			obj = map.Object(game.char.x, game.char.y, game.player.inventory[choice].icon, game.player.inventory[choice].name, game.player.inventory[choice].color, True, item=game.player.inventory[choice])
			game.current_map.objects.append(obj)
			obj.send_to_back()
			game.player.inventory.pop(choice)


# see inventory
def inventory():
	if len(game.player.inventory) == 0:
		game.message.new('Your inventory is empty.', game.player.turns, libtcod.white)
	else:
		util.msg_box('inv', 'Inventory', 'Up/down to select, ENTER-Use, BSPACE-Drop, ESC-Exit')


# look (with keyboard)
def look():
	game.message.new('Looking... (Arrow keys to move cursor, ESC to exit)', game.player.turns)
	util.render_all()
	dx = game.char.x
	dy = game.char.y

	while not libtcod.console_is_window_closed():
		libtcod.console_set_default_background(0, libtcod.white)
		libtcod.console_rect(0, game.PLAYER_STATS_WIDTH + dx, dy, 1, 1, False, libtcod.BKGND_SET)
		libtcod.console_flush()
		text = ""

		key = libtcod.console_wait_for_keypress(True)
		if key.vk == libtcod.KEY_UP:
			dy -= 1
		elif key.vk == libtcod.KEY_DOWN:
			dy += 1
		elif key.vk == libtcod.KEY_LEFT:
			dx -= 1
		elif key.vk == libtcod.KEY_RIGHT:
			dx += 1
		if key.vk == libtcod.KEY_ESCAPE:
			del game.message.log[len(game.message.log) - 1]
			break

		if dx < 0:
			dx = 0
		if dy < 0:
			dy = 0
		if dx == game.MAP_WIDTH:
			dx -= 1
		if dy == game.MAP_HEIGHT:
			dy -= 1

		#create a list with the names of all objects at the mouse's coordinates and in FOV
		if dx in range(0, game.MAP_WIDTH - 1) and dy in range(0, game.MAP_HEIGHT - 1) and game.current_map.tiles[dx][dy].explored:
			names = [obj.name for obj in game.current_map.objects
				if obj.x == dx and obj.y == dy and libtcod.map_is_in_fov(game.fov_map, obj.x, obj.y)]
			if names == []:
				text = 'you see a ' + game.current_map.tiles[dx][dy].name
			else:
				names = ', a '.join(names)  # join the names, separated by commas
				text = 'you see a ' + names.capitalize()

		libtcod.console_set_default_foreground(game.con, libtcod.white)
		libtcod.console_set_default_background(game.con, libtcod.black)
		libtcod.console_rect(game.con, 1, 0, game.MAP_WIDTH, 1, True, libtcod.BKGND_SET)
		libtcod.console_print(game.con, 1, 0, text)
		libtcod.console_blit(game.con, 0, 0, game.MAP_WIDTH, game.MAP_HEIGHT, 0, 20, 0)


# open door
def open_door():
	game.message.new('Open door in which direction?', game.player.turns)
	util.render_all()
	libtcod.console_flush()
	dx = 0
	dy = 0

	key = libtcod.console_wait_for_keypress(True)
	if key.vk == libtcod.KEY_UP:
		dy = -1
	elif key.vk == libtcod.KEY_DOWN:
		dy = 1
	elif key.vk == libtcod.KEY_LEFT:
		dx = -1
	elif key.vk == libtcod.KEY_RIGHT:
		dx = 1

	if game.current_map.tiles[game.char.x + dx][game.char.y + dy].name == 'door':
		game.current_map.tiles[game.char.x + dx][game.char.y + dy].icon = '/'
		game.current_map.tiles[game.char.x + dx][game.char.y + dy].name = 'opened door'
		game.current_map.tiles[game.char.x + dx][game.char.y + dy].color = libtcod.dark_orange
		game.current_map.tiles[game.char.x + dx][game.char.y + dy].dark_color = libtcod.darkest_orange
		game.current_map.tiles[game.char.x + dx][game.char.y + dy].blocked = False
		game.current_map.tiles[game.char.x + dx][game.char.y + dy].block_sight = False
		game.player.turns += 1
		game.message.new('You open the door.', game.player.turns)
		game.fov_recompute = True
		util.initialize_fov()
		util.render_all()
	elif game.current_map.tiles[game.char.x + dx][game.char.y + dy].name == 'opened door':
		game.message.new('That door is already opened!', game.player.turns, libtcod.red)
	elif dx != 0 or dy != 0:
		game.message.new('There is no door in that direction!', game.player.turns, libtcod.red)


# pick up an item
def pickup_item():
	pickup = False
	for object in game.current_map.objects:  # look for an item in the player's tile
		if object.x == game.char.x and object.y == game.char.y and object.can_be_pickup:
			object.item.pick_up()
			game.current_map.objects.remove(object)
			pickup = True
			break
	if not pickup:
		game.message.new('There is nothing to pick up.', game.player.turns, libtcod.white)
