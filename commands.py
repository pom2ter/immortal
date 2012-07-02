import libtcodpy as libtcod
import os
import util
import map
import game


def handle_keys():
	key = libtcod.Key()
	ev = libtcod.sys_check_for_event(libtcod.EVENT_ANY, key, game.mouse)
	if ev == libtcod.EVENT_KEY_PRESS:
		if key.vk == libtcod.KEY_ENTER and key.lalt:
			libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

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
				wait_turn()
			elif key.vk == libtcod.KEY_ESCAPE:
				state = options_menu()
				if state == 'help':
					help()
				if state == 'save':
					if save_game():
						return 'save'
				if state == 'exit':
					if quit_game():
						return 'exit'
			elif (key.lctrl or key.rctrl) and chr(key.c) == 'x':
				if quit_game():
					return 'exit'
			elif (key.lctrl or key.rctrl) and chr(key.c) == 's':
				if save_game():
					return 'save'
			else:
				key_char = chr(key.c)

				if key_char == 'c':
					close_door()
				if key_char == 'd':
					drop_item()
				if key_char == 'e':
					equip_item()
				if key_char == 'g':
					pickup_item()
				if key_char == 'i':
					inventory()
				if key_char == 'l':
					look()
				if key_char == 'o':
					open_door()
				if key_char == 'r':
					remove_item()
				if key_char == 'u':
					use_item()
				if key_char == '<':
					climb_stairs('up')
				if key_char == '>':
					climb_stairs('down')
				if key_char == '?':
					help()

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


#climb up/down stairs
def climb_stairs(direction):
	if (direction == 'up' and game.current_map.tiles[game.char.x][game.char.y].icon != "<") or (direction == 'down' and game.current_map.tiles[game.char.x][game.char.y].icon != ">"):
		game.message.new('You see no stairs going in that direction!', game.player.turns, libtcod.white)
	else:
		if direction == 'down':
			level = game.current_map.location_level + 1
			game.message.new('You climb down the stairs.', game.player.turns, libtcod.white)
		else:
			level = game.current_map.location_level - 1
			game.message.new('You climb up the stairs.', game.player.turns, libtcod.white)
		game.old_maps.append(game.current_map)
		generate = True
		for i in range(len(game.old_maps) - 1):
			if game.old_maps[i].location_id == game.current_map.location_id and game.old_maps[i].location_level == level:
				game.current_map = game.old_maps[i]
				if direction == 'down':
					(game.char.x, game.char.y) = game.current_map.up_staircase
				else:
					(game.char.x, game.char.y) = game.current_map.down_staircase
				game.old_maps.pop(i)
				generate = False
				break
		if generate:
			game.current_map = map.Map(game.current_map.location_name, game.current_map.location_id, level)
		game.player.add_turn()
		game.fov_recompute = True
		util.initialize_fov()
		util.render_all()


# close door
def close_door():
	game.message.new('Close door in which direction?', game.player.turns)
	util.render_all()
	libtcod.console_flush()
	dx = 0
	dy = 0
	key = libtcod.Key()

	libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS, key, libtcod.Mouse(), True)
	if key.vk == libtcod.KEY_UP:
		dy = -1
	elif key.vk == libtcod.KEY_DOWN:
		dy = 1
	elif key.vk == libtcod.KEY_LEFT:
		dx = -1
	elif key.vk == libtcod.KEY_RIGHT:
		dx = 1

	if game.current_map.tiles[game.char.x + dx][game.char.y + dy].name == 'opened door':
		game.current_map.tiles[game.char.x + dx][game.char.y + dy] = game.tiles.gettile('door')
		game.player.add_turn()
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
		choice = util.msg_box('drop', 'Drop an item', 'Up/down to select, ENTER to drop, ESC to exit', game.player.inventory, box_height=max(16, len(game.player.inventory) + 4))
		if choice != -1:
			obj = map.Object(game.char.x, game.char.y, game.player.inventory[choice].icon, game.player.inventory[choice].name, game.player.inventory[choice].color, True, item=game.player.inventory[choice])
			game.current_map.objects.append(obj)
			obj.send_to_back()
			game.player.inventory.pop(choice)
			game.player.add_turn()


# equip an item
def equip_item():
	equippable = False
	for item in game.player.inventory:
		if item.is_equippable():
			equippable = True
	if not equippable:
		game.message.new("You don't have any equippable items.", game.player.turns, libtcod.white)
	else:
		filter = []
		itempos = []
		for i in range(0, len(game.player.inventory)):
			if game.player.inventory[i].is_equippable():
				filter.append(game.player.inventory[i])
				itempos.append(i)
		choice = util.msg_box('equip', 'Wear/Equip an item', 'Up/down to select, ENTER to equip, ESC to exit', filter, box_height=max(16, len(filter) + 4))
		if choice != -1:
			game.player.equip(itempos[choice])


# help screen
def help():
	contents = open('data/commands.txt', 'r').read()
	util.msg_box('text', 'Help', contents=contents, box_width=40, box_height=22)


# see inventory
def inventory():
	if len(game.player.inventory) == 0:
		game.message.new('Your inventory is empty.', game.player.turns, libtcod.white)
	else:
		choice = util.msg_box('inv', 'Inventory', 'Up/down to select, ENTER to use, ESC to exit', game.player.inventory, box_height=max(16, len(game.player.inventory) + 4))
		if choice != -1:
			game.player.inventory[choice].use(choice)


# look (with keyboard)
def look():
	game.message.new('Looking... (Arrow keys to move cursor, ESC to exit)', game.player.turns)
	util.render_all()
	dx = game.char.x
	dy = game.char.y
	key = libtcod.Key()

	while not libtcod.console_is_window_closed():
		libtcod.console_set_default_background(0, libtcod.white)
		libtcod.console_rect(0, game.MAP_X + dx, dy + 1, 1, 1, False, libtcod.BKGND_SET)
		libtcod.console_flush()
		text = ""

		libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS, key, libtcod.Mouse(), True)
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

		#create a list with the names of all objects at the cursor coordinates
		if dx in range(0, game.MAP_WIDTH - 1) and dy in range(0, game.MAP_HEIGHT - 1) and game.current_map.explored[dx][dy]:
			names = [obj for obj in game.current_map.objects
				if obj.x == dx and obj.y == dy]

			prefix = 'you see '
			if not libtcod.map_is_in_fov(game.fov_map, dx, dy):
				prefix = 'you remember seeing '
				for i in range(len(names) - 1, -1, -1):
					if names[i].entity != None:
						names.pop(i)
			if (dx, dy) == (game.char.x, game.char.y):
				text = 'you see yourself'
			elif names == []:
				text = prefix + game.current_map.tiles[dx][dy].article + game.current_map.tiles[dx][dy].name
			elif len(names) > 1:
				text = prefix
				for i in range(0, len(names)):
					if i == len(names) - 1:
						text += ' and '
					elif i > 0:
						text += ', '
					if names[i].item != None:
						text += names[i].item.article + names[i].item.name
					if names[i].entity != None:
						text += names[i].entity.article + names[i].entity.name
			else:
				if names[0].item != None:
					text = prefix + names[0].item.article + names[0].item.name
				if names[0].entity != None:
					text = prefix + names[0].entity.article + names[0].entity.name

		libtcod.console_set_default_foreground(game.con, libtcod.white)
		libtcod.console_set_default_background(game.con, libtcod.black)
		libtcod.console_rect(game.con, 0, 0, game.MAP_WIDTH, 1, True, libtcod.BKGND_SET)
		libtcod.console_print(game.con, 0, 0, text)
		libtcod.console_blit(game.con, 0, 0, game.MAP_WIDTH, game.MAP_HEIGHT, 0, game.MAP_X, game.MAP_Y)


# open door
def open_door():
	game.message.new('Open door in which direction?', game.player.turns)
	util.render_all()
	libtcod.console_flush()
	dx = 0
	dy = 0
	key = libtcod.Key()

	libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS, key, libtcod.Mouse(), True)
	if key.vk == libtcod.KEY_UP:
		dy = -1
	elif key.vk == libtcod.KEY_DOWN:
		dy = 1
	elif key.vk == libtcod.KEY_LEFT:
		dx = -1
	elif key.vk == libtcod.KEY_RIGHT:
		dx = 1

	if game.current_map.tiles[game.char.x + dx][game.char.y + dy].name == 'door':
		game.current_map.tiles[game.char.x + dx][game.char.y + dy] = game.tiles.gettile('opened door')
		game.player.add_turn()
		game.message.new('You open the door.', game.player.turns)
		game.fov_recompute = True
		util.initialize_fov()
		util.render_all()
	elif game.current_map.tiles[game.char.x + dx][game.char.y + dy].name == 'opened door':
		game.message.new('That door is already opened!', game.player.turns, libtcod.red)
	elif dx != 0 or dy != 0:
		game.message.new('There is no door in that direction!', game.player.turns, libtcod.red)


# ingame options menu
def options_menu():
	choice = util.msg_box('options', 'Main Menu', contents=['Help', 'Options', 'Save and quit game', 'Quit without saving'], box_width=23, box_height=6)
	if choice == 0:
		return 'help'
	if choice == 2:
		return 'save'
	if choice == 3:
		return 'exit'
	return


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


# dialog to confirm quitting the game
def quit_game():
	util.render_all()
	libtcod.console_print(game.con, 0, 0, 'Are you sure you want to quit the game? (y/n)')
	libtcod.console_blit(game.con, 0, 0, game.MAP_WIDTH, game.MAP_HEIGHT, 0, game.MAP_X, game.MAP_Y)
	libtcod.console_flush()
	key = libtcod.Key()

	libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS, key, libtcod.Mouse(), True)
	if chr(key.c) == 'y' or chr(key.c) == 'Y':
		if game.player.name.lower() in game.savefiles:
			os.remove('saves/' + game.player.name.lower())
		return True
	return False


# remove/unequip an item
def remove_item():
	if len(game.player.equipment) == 0:
		game.message.new("You don't have any equipped items.", game.player.turns, libtcod.white)
	else:
		choice = util.msg_box('remove', 'Remove/Unequip an item', 'Up/down to select, ENTER to remove, ESC to exit', game.player.equipment, box_height=max(16, len(game.player.equipment) + 4))
		if choice != -1:
			game.player.unequip(choice)


# dialog to confirm saving the game
def save_game():
	util.render_all()
	libtcod.console_print(game.con, 0, 0, 'Do you want to save (and quit) the game? (y/n)')
	libtcod.console_blit(game.con, 0, 0, game.MAP_WIDTH, game.MAP_HEIGHT, 0, game.MAP_X, game.MAP_Y)
	libtcod.console_flush()
	key = libtcod.Key()

	libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS, key, libtcod.Mouse(), True)
	if chr(key.c) == 'y' or chr(key.c) == 'Y':
		return True
	return False


# use an item
def use_item():
	if len(game.player.inventory) == 0:
		game.message.new('Your inventory is empty.', game.player.turns, libtcod.white)
	else:
		choice = util.msg_box('use', 'Use an item', 'Up/down to select, ENTER to use, ESC to exit', game.player.inventory, box_height=max(16, len(game.player.inventory) + 4))
		if choice != -1:
			game.player.inventory[choice].use(choice)


# passing one turn
def wait_turn():
	game.message.new("Time passes...", game.player.turns, libtcod.white)
	game.player.add_turn()
