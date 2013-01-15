import libtcodpy as libtcod
import os
import game
import util
import map


def handle_keys():
	key = libtcod.Key()
	ev = libtcod.sys_check_for_event(libtcod.EVENT_ANY, key, game.mouse)
	if ev == libtcod.EVENT_KEY_PRESS:
		if key.vk == libtcod.KEY_ENTER and key.lalt:
			libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

		if game.game_state == 'playing':
			if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
				player_move(0, -1)
			elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
				player_move(0, 1)
			elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
				player_move(-1, 0)
			elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
				player_move(1, 0)
			elif key.vk == libtcod.KEY_KP7:
				player_move(-1, -1)
			elif key.vk == libtcod.KEY_KP9:
				player_move(1, -1)
			elif key.vk == libtcod.KEY_KP1:
				player_move(-1, 1)
			elif key.vk == libtcod.KEY_KP3:
				player_move(1, 1)
			elif key.vk == libtcod.KEY_SPACE or key.vk == libtcod.KEY_KP5:
				wait_turn()
			elif key.vk == libtcod.KEY_TAB:
				show_worldmap()
			elif key.vk == libtcod.KEY_ESCAPE:
				state = options_menu()
				if state == 'save':
					if save_game():
						return state
				if state == 'quit':
					if quit_game():
						return state
			elif (key.lctrl or key.rctrl) and chr(key.c) == 'x':
				if quit_game():
					return 'quit'
			elif (key.lctrl or key.rctrl) and chr(key.c) == 's':
				if save_game():
					return 'save'
			else:
				key_char = chr(key.c)

				if key_char == 'a':
					attack()
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
				if key_char == 'z':
					ztats()
				if key_char == '<':
					climb_stairs('up')
				if key_char == '>':
					climb_stairs('down')
				if key_char == '?':
					help()

				return 'didnt-take-turn'


# function that returns some coordinates when player needs to input a direction
def key_check(key, dx, dy):
	if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
		dy -= 1
	elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
		dy += 1
	elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
		dx -= 1
	elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
		dx += 1
	elif key.vk == libtcod.KEY_KP7:
		dx -= 1
		dy -= 1
	elif key.vk == libtcod.KEY_KP9:
		dx += 1
		dy -= 1
	elif key.vk == libtcod.KEY_KP1:
		dx -= 1
		dy += 1
	elif key.vk == libtcod.KEY_KP3:
		dx += 1
		dy += 1
	return dx, dy


# moves the player to new coordinates or attacks an enemy
def player_move(dx, dy):
	#the coordinates the player is moving to/attacking
	x = game.char.x + dx
	y = game.char.y + dy

	#try to find an attackable object there
	target = None
	for object in game.current_map.objects:
		if object.entity and object.x == x and object.y == y:
			target = object
			break

	#attack if target found, move otherwise
	if target is not None:
		game.player.attack(target)
	else:
		if game.current_map.tiles[game.char.x + dx][game.char.y + dy].type == 'door':
			open_door(dx, dy)
		else:
			game.char.move(dx, dy, game.current_map)
			if game.current_map.location_id == 0:
				coordx = [-1, 0, 1]
				coordy = [-(game.WORLDMAP_WIDTH), 0, game.WORLDMAP_WIDTH]
				px = game.current_map.map_width / 3
				py = game.current_map.map_height / 3
				if (game.char.y / py) == 0 or (game.char.x / px) == 0 or (game.char.y / py) == 2 or (game.char.x / px) == 2:
					level = game.current_map.location_level + coordx[game.char.x / px] + coordy[game.char.y / py]
					game.worldmap.player_positionx += dx
					game.worldmap.player_positiony += dy
					util.change_maps(0, level)
		util.items_at_feet()
		game.fov_recompute = True


# attack someone (primarily use for ranged weapons)
def attack():
	game.message.new('Attack... (Arrow keys to move cursor, ENTER to attack, ESC to exit)', game.player.turns)
	util.render_map()
	target = None
	dx = game.char.x - game.curx
	dy = game.char.y - game.cury
	key = libtcod.Key()

	while not libtcod.console_is_window_closed():
		libtcod.console_set_default_background(0, libtcod.white)
		libtcod.console_rect(0, game.MAP_X + dx, dy + 1, 1, 1, False, libtcod.BKGND_SET)
		libtcod.console_flush()

		libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS, key, libtcod.Mouse(), True)
		dx, dy = key_check(key, dx, dy)
		if key.vk == libtcod.KEY_ESCAPE:
			del game.message.log[len(game.message.log) - 1]
			util.render_message_panel()
			break

		if dx < 0:
			dx = 0
		if dy < 0:
			dy = 0
		if dx == game.MAP_WIDTH:
			dx -= 1
		if dy == game.MAP_HEIGHT:
			dy -= 1
		px = dx + game.curx
		py = dy + game.cury

		if key.vk == libtcod.KEY_ENTER:
			for obj in game.current_map.objects:
				if obj.entity and obj.x == px and obj.y == py:
					target = obj
			if not game.current_map.explored[px][py]:
				game.message.new("You can't fight darkness.", game.player.turns)
			elif target is None:
				game.message.new('There is no one here.', game.player.turns)
			else:
				if abs(px - game.char.x) > 1 or abs(py - game.char.y) > 1:
					game.message.new('Target is out of range.', game.player.turns)
					target = None
			break

		libtcod.console_set_default_foreground(game.con, libtcod.white)
		libtcod.console_set_default_background(game.con, libtcod.black)
		libtcod.console_rect(game.con, 0, 0, game.MAP_WIDTH, 1, True, libtcod.BKGND_SET)
		libtcod.console_blit(game.con, 0, 0, game.MAP_WIDTH, game.MAP_HEIGHT, 0, game.MAP_X, game.MAP_Y)

	if target is not None:
		game.player.attack(target)


# climb up/down stairs
def climb_stairs(direction):
	decombine, combine = False, False
	location_id = game.current_map.location_id
	location_name = game.current_map.location_name
	location_abbr = game.current_map.location_abbr

	if (direction == 'up' and game.current_map.tiles[game.char.x][game.char.y].icon != "<") or (direction == 'down' and game.current_map.tiles[game.char.x][game.char.y].icon != ">"):
		game.message.new('You see no stairs going in that direction!', game.player.turns)
	else:
		if direction == 'down':
			if game.current_map.location_id > 0:
				level = game.current_map.location_level + 1
				game.message.new('You climb down the stairs.', game.player.turns)
			else:
				decombine = True
				level = 1
				for (id, name, abbr, x, y) in game.worldmap.dungeons:
					if y * game.WORLDMAP_WIDTH + x == game.current_map.location_level:
						location_id = id
						location_name = name
						location_abbr = abbr
				game.message.new('You enter the ' + location_name + '.', game.player.turns)
		else:
			if game.current_map.location_level > 1:
				level = game.current_map.location_level - 1
				game.message.new('You climb up the stairs.', game.player.turns)
			else:
				combine = True
				(level, game.char.x, game.char.y) = game.current_map.overworld_position
				location_id = 0
				location_name = 'Wilderness'
				location_abbr = 'WD'
				game.message.new('You return to the ' + location_name + '.', game.player.turns)

		if decombine:
			util.decombine_maps()
			game.old_maps.append(game.current_map)
			op = (game.current_map.location_level, game.char.x, game.char.y)
			for i in range(len(game.border_maps)):
				game.old_maps.append(game.border_maps[i])
		else:
			game.old_maps.append(game.current_map)

		if not combine:
			generate = True
			for i in xrange(len(game.old_maps)):
				if game.old_maps[i].location_id == location_id and game.old_maps[i].location_level == level:
					game.current_map = game.old_maps[i]
					if direction == 'down':
						(game.char.x, game.char.y) = game.current_map.up_staircase
					else:
						(game.char.x, game.char.y) = game.current_map.down_staircase
					game.old_maps.pop(i)
					generate = False
					break
			if generate:
				game.current_map = map.Map(location_name, location_abbr, location_id, level)
		else:
			util.load_old_maps(location_id, level)
			util.combine_maps()

		if decombine:
			game.current_map.overworld_position = op
		game.player.add_turn()
		game.fov_recompute = True


# close door
def close_door():
	game.message.new('Close door in which direction?', game.player.turns)
	libtcod.console_flush()
	dx, dy = 0, 0
	key = libtcod.Key()

	libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS, key, libtcod.Mouse(), True)
	dx, dy = key_check(key, dx, dy)

	if game.current_map.tiles[game.char.x + dx][game.char.y + dy].name == 'opened door':
		game.current_map.tiles[game.char.x + dx][game.char.y + dy] = game.tiles.get_tile('door')
		game.player.add_turn()
		game.message.new('You close the door.', game.player.turns)
		game.fov_recompute = True
	elif game.current_map.tiles[game.char.x + dx][game.char.y + dy].name == 'door':
		game.message.new('That door is already closed!', game.player.turns)
	elif dx != 0 or dy != 0:
		game.message.new('There is no door in that direction!', game.player.turns)


# drop an item
def drop_item():
	qty = 1
	if len(game.player.inventory) == 0:
		game.message.new('Your inventory is empty.', game.player.turns)
	else:
		output = util.item_stacking(game.player.inventory)
		choice = util.msg_box('drop', 'Drop an item', 'Up/down to select, ENTER to drop, ESC to exit', output, box_height=max(16, len(output) + 4), blitmap=True)
		if choice != -1:
			if output[choice].quantity > 1:
				libtcod.console_print(0, game.PLAYER_STATS_WIDTH + 2, 1, 'Drop how many: _')
				libtcod.console_flush()
				qty = game.messages.input('', 0, game.PLAYER_STATS_WIDTH + 17, 1)
				if qty == '' or not qty.isdigit():
					choice = -1
				elif int(qty) < 1 or int(qty) > output[choice].quantity:
					choice = -1
		util.reset_quantity(game.player.inventory)
		if choice != -1:
			game.player.drop_item(output[choice], int(qty))
	game.redraw_gui = True


# equip an item
def equip_item():
	equippable = any(item.is_equippable() for item in game.player.inventory)
	if not equippable:
		game.message.new("You don't have any equippable items.", game.player.turns)
	else:
		output = util.item_stacking(game.player.inventory, True)
		choice = util.msg_box('equip', 'Wear/Equip an item', 'Up/down to select, ENTER to equip, ESC to exit', output, box_height=max(16, len(output) + 4), blitmap=True)
		util.reset_quantity(game.player.inventory)
		if choice != -1:
			game.player.equip_item(output[choice])
	game.redraw_gui = True


# help screen
def help():
	contents = open('data/help.txt', 'r').read()
	util.msg_box('text', 'Help', contents=contents, box_width=40, box_height=26, blitmap=True)
	game.redraw_gui = True


# highscore screen
def highscores():
	if os.path.exists('data/highscores.dat'):
#		util.msg_box('highscore', 'High scores', contents=game.highscore, box_width=game.SCREEN_WIDTH, box_height=game.SCREEN_HEIGHT)
		contents = []
		for (score, line1, line2) in game.highscore:
			contents.append(str(score).ljust(6) + line1)
			contents.append("      " + line2)
			contents.append(" ")
		game.messages.box('High scores', None, 0, 0, game.SCREEN_WIDTH, game.SCREEN_HEIGHT, contents, input=False)
	else:
#		util.msg_box('text', 'High scores', contents="The high scores file is empty.", box_width=41, box_height=5, center=True)
		contents = ["The high scores file is empty."]
		game.messages.box('High scores', None, (game.SCREEN_WIDTH - (len(max(contents, key=len)) + 18)) / 2, (game.SCREEN_HEIGHT - (len(contents) + 4)) / 2, len(max(contents, key=len)) + 18, len(contents) + 4, contents, input=False, align=libtcod.CENTER)
	game.redraw_gui = True


# see inventory
def inventory():
	if len(game.player.inventory) == 0:
		game.message.new('Your inventory is empty.', game.player.turns)
	else:
		output = util.item_stacking(game.player.inventory)
#		choice = util.msg_box('inv', 'Inventory', 'Up/down to select, ENTER to use, ESC to exit', output, box_height=max(16, len(output) + 4), blitmap=True)
		choice = game.messages.box('Inventory', 'Up/down to select, ENTER to use, ESC to exit', game.PLAYER_STATS_WIDTH + ((game.MAP_WIDTH - 56) / 2), ((game.MAP_HEIGHT + 1) - max(16, len(output) + 4)) / 2, 60, max(16, len(output) + 4), output, inv=True, step=2, mouse_exit=True)
		util.reset_quantity(game.player.inventory)
		if choice != -1:
			output[choice].use()
	game.redraw_gui = True


# look (with keyboard)
def look():
	game.message.new('Looking... (Arrow keys to move cursor, ESC to exit)', game.player.turns)
	util.render_map()
	dx = game.char.x - game.curx
	dy = game.char.y - game.cury
	key = libtcod.Key()

	while not libtcod.console_is_window_closed():
		libtcod.console_set_default_background(0, libtcod.white)
		libtcod.console_rect(0, game.MAP_X + dx, dy + 1, 1, 1, False, libtcod.BKGND_SET)
		libtcod.console_flush()
		text = ""

		libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS, key, libtcod.Mouse(), True)
		dx, dy = key_check(key, dx, dy)
		if key.vk == libtcod.KEY_ESCAPE:
			del game.message.log[len(game.message.log) - 1]
			util.render_message_panel()
			break

		if dx < 0:
			dx = 0
		if dy < 0:
			dy = 0
		if dx == game.MAP_WIDTH:
			dx -= 1
		if dy == game.MAP_HEIGHT:
			dy -= 1
		px = dx + game.curx
		py = dy + game.cury

		#create a list with the names of all objects at the cursor coordinates
		if dx in range(game.MAP_WIDTH - 1) and dy in range(game.MAP_HEIGHT - 1) and game.current_map.explored[px][py]:
			names = [obj for obj in game.current_map.objects if obj.x == px and obj.y == py]
			prefix = 'you see '
			if not libtcod.map_is_in_fov(game.fov_map, px, py):
				prefix = 'you remember seeing '
				for i in range(len(names) - 1, -1, -1):
					if names[i].entity != None:
						names.pop(i)
			if (px, py) == (game.char.x, game.char.y):
				text = 'you see yourself'
			elif names == []:
				text = prefix + game.current_map.tiles[px][py].article + game.current_map.tiles[px][py].name
			elif len(names) > 1:
				text = prefix
				for i in range(len(names)):
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
def open_door(x=None, y=None):
	dx, dy = 0, 0
	if x == None:
		game.message.new('Open door in which direction?', game.player.turns)
		libtcod.console_flush()
		key = libtcod.Key()
		libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS, key, libtcod.Mouse(), True)
		dx, dy = key_check(key, dx, dy)
	else:
		dx, dy = x, y

	if game.current_map.tiles[game.char.x + dx][game.char.y + dy].name == 'door':
		game.current_map.tiles[game.char.x + dx][game.char.y + dy] = game.tiles.get_tile('opened door')
		game.player.add_turn()
		game.message.new('You open the door.', game.player.turns)
		game.fov_recompute = True
	elif game.current_map.tiles[game.char.x + dx][game.char.y + dy].name == 'opened door':
		game.message.new('That door is already opened!', game.player.turns)
	elif dx != 0 or dy != 0:
		game.message.new('There is no door in that direction!', game.player.turns)


# ingame options menu
def options_menu():
	choice = util.msg_box('options', 'Menu', contents=['Read the manual', 'Change settings', 'View high scores', 'Save and quit game', 'Quit without saving'], box_width=23, box_height=7, blitmap=True)
	if choice == 0:
		help()
	if choice == 1:
		settings()
	if choice == 2:
		highscores()
	if choice == 3:
		return 'save'
	if choice == 4:
		return 'quit'
	return


# pick up an item
def pickup_item():
	nb_items, itempos = [], []
	for i in range(len(game.current_map.objects)):
		if game.current_map.objects[i].x == game.char.x and game.current_map.objects[i].y == game.char.y and game.current_map.objects[i].can_be_pickup:
			game.current_map.objects[i].item.turn_created = game.current_map.objects[i].first_appearance
			nb_items.append(game.current_map.objects[i].item)
			itempos.append(i)

	if len(nb_items) == 0:
		game.message.new('There is nothing to pick up.', game.player.turns)
	elif len(nb_items) == 1:
		nb_items[0].pick_up(nb_items[0].turn_created)
		game.current_map.objects.pop(itempos[0])
	else:
		qty = 1
		output = util.item_stacking(nb_items)
		choice = util.msg_box('pickup', 'Get an item', 'Up/down to select, ENTER to get, ESC to exit', output, box_height=max(16, len(output) + 4), blitmap=True)
		if choice != -1:
			if output[choice].quantity > 1:
				libtcod.console_print(0, game.PLAYER_STATS_WIDTH + 2, 1, 'Pickup how many: _')
				libtcod.console_flush()
				qty = game.messages.input('', 0, game.PLAYER_STATS_WIDTH + 19, 1)
				if qty == '' or not qty.isdigit():
					choice = -1
				elif int(qty) < 1 or int(qty) > output[choice].quantity:
					choice = -1
		if choice != -1:
			x = 0
			for i in range(len(nb_items) - 1, -1, -1):
				if nb_items[i] == output[choice] and x < int(qty):
					nb_items[i].pick_up(nb_items[i].turn_created)
					game.current_map.objects.pop(itempos[i])
					x += 1
		util.reset_quantity(nb_items)
		game.redraw_gui = True


# dialog to confirm quitting the game
def quit_game():
	util.render_map()
	libtcod.console_print(game.con, 0, 0, 'Are you sure you want to quit the game? (y/n)')
	libtcod.console_blit(game.con, 0, 0, game.MAP_WIDTH, game.MAP_HEIGHT, 0, game.MAP_X, game.MAP_Y)
	libtcod.console_flush()
	key = libtcod.Key()

	libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS, key, libtcod.Mouse(), True)
	if chr(key.c) == 'y' or chr(key.c) == 'Y':
		return True
	return False


# remove/unequip an item
def remove_item():
	if len(game.player.equipment) == 0:
		game.message.new("You don't have any equipped items.", game.player.turns)
	else:
		choice = util.msg_box('remove', 'Remove/Unequip an item', 'Up/down to select, ENTER to remove, ESC to exit', game.player.equipment, box_height=max(16, len(game.player.equipment) + 4), blitmap=True)
		if choice != -1:
			game.player.unequip(choice)
	game.redraw_gui = True


# dialog to confirm saving the game
def save_game():
	util.render_map()
	libtcod.console_print(game.con, 0, 0, 'Do you want to save (and quit) the game? (y/n)')
	libtcod.console_blit(game.con, 0, 0, game.MAP_WIDTH, game.MAP_HEIGHT, 0, game.MAP_X, game.MAP_Y)
	libtcod.console_flush()
	key = libtcod.Key()

	libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS, key, libtcod.Mouse(), True)
	if chr(key.c) == 'y' or chr(key.c) == 'Y':
		return True
	return False


# show a miniature world map
def show_worldmap():
	util.msg_box('map', 'World Map', 'Red dot - You, Black dots - Dungeons, S - Save map', box_width=game.SCREEN_WIDTH, box_height=game.SCREEN_HEIGHT)
	game.redraw_gui = True


# settings screen
def settings():
	util.msg_box('settings', 'Settings', contents=game.font, box_width=40, box_height=8, center=True, blitmap=True)
	game.redraw_gui = True


# use an item
def use_item():
	if len(game.player.inventory) == 0:
		game.message.new('Your inventory is empty.', game.player.turns)
	else:
		output = util.item_stacking(game.player.inventory)
		choice = util.msg_box('use', 'Use an item', 'Up/down to select, ENTER to use, ESC to exit', output, box_height=max(16, len(output) + 4), blitmap=True)
		util.reset_quantity(game.player.inventory)
		if choice != -1:
			output[choice].use()
	game.redraw_gui = True


# passing one turn
def wait_turn():
	game.message.new("Time passes...", game.player.turns)
	game.player.add_turn()


# character sheet for stats
def ztats_attributes(con, width, height):
	util.text_box(con, 0, 0, width, height, 'Player stats')
	libtcod.console_set_default_foreground(con, libtcod.white)
	libtcod.console_set_default_background(con, libtcod.black)
	libtcod.console_print(con, 2, 2, game.player.name + ', a level ' + str(game.player.level) + ' ' + game.player.gender + ' ' + game.player.race + ' ' + game.player.profession)
	libtcod.console_print(con, 2, 4, 'Strength     : ' + str(game.player.strength))
	libtcod.console_print(con, 2, 5, 'Dexterity    : ' + str(game.player.dexterity))
	libtcod.console_print(con, 2, 6, 'Intelligence : ' + str(game.player.intelligence))
	libtcod.console_print(con, 2, 7, 'Wisdom       : ' + str(game.player.wisdom))
	libtcod.console_print(con, 2, 8, 'Endurance    : ' + str(game.player.endurance))
	libtcod.console_print(con, 2, 9, 'Karma        : ' + str(game.player.karma))

	libtcod.console_print(con, 30, 4, 'Health : ' + str(game.player.health) + '/' + str(game.player.max_health))
	libtcod.console_print(con, 30, 5, 'Mana   : ' + str(game.player.mana) + '/' + str(game.player.max_mana))
	libtcod.console_print(con, 30, 6, 'Experience: ' + str(game.player.xp))
	libtcod.console_print(con, 30, 7, 'Gold: ' + str(game.player.gold))

	libtcod.console_print(con, 2, 11, 'Attack Rating     : ' + str(game.player.attack_rating()))
	libtcod.console_print(con, 2, 12, 'Defense Rating    : ' + str(game.player.defense_rating()))
	libtcod.console_print(con, 2, 13, 'Carrying Capacity : ' + str(game.player.weight_carried()) + ' / ' + str(game.player.max_carrying_capacity()) + ' lbs')


# character sheet for skills
def ztats_skills(con, width, height):
	util.text_box(con, 0, 0, width, height, 'Skills')
	libtcod.console_set_default_foreground(con, libtcod.white)
	libtcod.console_set_default_background(con, libtcod.black)
	libtcod.console_print(con, 2, 2, 'Combat Skills')
	for i in range(len(game.player.combat_skills)):
		libtcod.console_print(con, 2, i + 4, game.player.combat_skills[i].name)
		libtcod.console_print(con, 15, i + 4, str(game.player.combat_skills[i].level))


# character sheet for equipment
def ztats_equipment(con, width, height):
	util.text_box(con, 0, 0, width, height, 'Equipment')
	libtcod.console_set_default_foreground(con, libtcod.white)
	libtcod.console_set_default_background(con, libtcod.black)
	libtcod.console_print(con, 2, 2, 'Head       :')
	libtcod.console_print(con, 2, 3, 'Cloak      :')
	libtcod.console_print(con, 2, 4, 'Neck       :')
	libtcod.console_print(con, 2, 5, 'Body       :')
	libtcod.console_print(con, 2, 6, 'Right Hand :')
	libtcod.console_print(con, 2, 7, 'Left Hand  :')
	libtcod.console_print(con, 2, 8, 'Ring       :')
	libtcod.console_print(con, 2, 9, 'Ring       :')
	libtcod.console_print(con, 2, 10, 'Gauntlets  :')
	libtcod.console_print(con, 2, 11, 'Boots      :')
	ring = 0
	for i in range(len(game.player.equipment)):
		if "armor_head" in game.player.equipment[i].flags:
			y = 2
		if "armor_cloak" in game.player.equipment[i].flags:
			y = 3
		if "armor_neck" in game.player.equipment[i].flags:
			y = 4
		if "armor_body" in game.player.equipment[i].flags:
			y = 5
		if "armor_ring" in game.player.equipment[i].flags:
			ring += 1
			y = 7 + ring
		if "armor_hands" in game.player.equipment[i].flags:
			y = 10
		if "armor_feet" in game.player.equipment[i].flags:
			y = 11
		if game.player.equipment[i].type == "weapon":
			y = 6
		if game.player.equipment[i].type == "shield":
			y = 7
		libtcod.console_print(con, 13, y, ': ' + game.player.equipment[i].name)
		libtcod.console_print_ex(con, width - 3, y, libtcod.BKGND_SET, libtcod.RIGHT, str(game.player.equipment[i].weight) + ' lbs')


# character sheet for inventory
def ztats_inventory(con, width, height):
	util.text_box(con, 0, 0, width, height, 'Inventory')
	libtcod.console_set_default_foreground(con, libtcod.white)
	libtcod.console_set_default_background(con, libtcod.black)
	output = util.item_stacking(game.player.inventory)
	for i in range(len(output)):
		if output[i].is_identified():
			if output[i].quantity > 1:
				text_left = str(output[i].quantity) + ' ' + output[i].plural
			else:
				text_left = output[i].name
		else:
			text_left = output[i].unidentified_name
		if output[i].duration > 0:
			text_left += ' (' + str(output[i].duration) + ' turns left)'
		text_right = str(round(output[i].weight * output[i].quantity, 1)) + ' lbs'
		libtcod.console_print(con, 2, i + 2, text_left)
		libtcod.console_print_ex(con, width - 3, i + 2, libtcod.BKGND_SET, libtcod.RIGHT, text_right)
	util.reset_quantity(game.player.inventory)


# character sheet
def ztats():
	width = 60
	height = 20
	screen = 0
	exit = False
	key = libtcod.Key()
	stats = libtcod.console_new(width, height)

	while exit == False:
		if screen == 0:
			ztats_attributes(stats, width, height)
		elif screen == 1:
			ztats_skills(stats, width, height)
		elif screen == 2:
			ztats_equipment(stats, width, height)
		elif screen == 3:
			ztats_inventory(stats, width, height)

		libtcod.console_print_ex(stats, width / 2, height - 1, libtcod.BKGND_SET, libtcod.CENTER, '[ Arrow Left/Right = Change Pages ]')
		libtcod.console_blit(stats, 0, 0, width, height, 0, ((game.MAP_WIDTH - width) / 2) + game.MAP_X, (game.MAP_HEIGHT - height) / 2, 1.0, 1.0)
		libtcod.console_flush()
		libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS, key, game.mouse, True)
		if key.vk == libtcod.KEY_LEFT:
			screen -= 1
			if screen < 0:
				screen = 3
		elif key.vk == libtcod.KEY_RIGHT:
			screen += 1
			if screen > 3:
				screen = 0
		elif key.vk == libtcod.KEY_ESCAPE:
			exit = True
	game.redraw_gui = True
