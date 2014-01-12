import libtcodpy as libtcod
import game
import IO
import sheet
import util


# handles all the keyboard input commands
# stuff to do: add more commands
def keyboard_commands():
	ev = libtcod.sys_check_for_event(libtcod.EVENT_ANY, game.kb, game.mouse)
	(mx, my) = (game.mouse.cx, game.mouse.cy)
	if ev == libtcod.EVENT_MOUSE_RELEASE:
		if mx in range(game.MESSAGE_X, game.MESSAGE_X + game.MESSAGE_WIDTH) and my in range(game.MESSAGE_Y, game.MESSAGE_Y + game.MESSAGE_HEIGHT) and game.mouse.wheel_up:
			see_message_log(up=True)
		elif mx in range(game.MESSAGE_X, game.MESSAGE_X + game.MESSAGE_WIDTH) and my in range(game.MESSAGE_Y, game.MESSAGE_Y + game.MESSAGE_HEIGHT) and game.mouse.wheel_down:
			see_message_log(down=True)
		elif mx in range(game.MAP_X + 3, game.MAP_X + 9) and my == 0 and game.mouse.lbutton_pressed:
			state = options_menu()
			if state == 'save':
				if save_game():
					return state
			if state == 'quit':
				if quit_game():
					return state
			game.mouse.lbutton_pressed = False
		elif mx in range(game.PLAYER_STATS_X + 9, game.PLAYER_STATS_X + 12) and my == 0 and game.mouse.lbutton_pressed:
			sheet.character_sheet()
			game.mouse.lbutton_pressed = False
		elif mx in range(game.MAP_X + 13, game.MAP_X + 18) and my == 0 and game.mouse.lbutton_pressed:
			show_worldmap()
		elif mx in range(game.SCREEN_WIDTH - 18, game.SCREEN_WIDTH - 11) and my == 0 and game.mouse.lbutton_pressed:
			show_time()
		elif mx in range(game.SCREEN_WIDTH - 7, game.SCREEN_WIDTH - 4) and my == 0 and game.mouse.lbutton_pressed:
			help()
			game.mouse.lbutton_pressed = False

	if ev == libtcod.EVENT_KEY_PRESS:
		key_char = chr(game.kb.c)
		if game.kb.vk == libtcod.KEY_ENTER and game.kb.lalt:
			libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
		elif game.kb.vk == libtcod.KEY_TAB:
			show_worldmap()
		elif game.kb.vk == libtcod.KEY_ESCAPE:
			state = options_menu()
			if state == 'save':
				if save_game():
					return state
			if state == 'quit':
				if quit_game():
					return state

		elif game.kb.vk == libtcod.KEY_UP or game.kb.vk == libtcod.KEY_KP8:
			player_move(0, -1)
		elif game.kb.vk == libtcod.KEY_DOWN or game.kb.vk == libtcod.KEY_KP2:
			player_move(0, 1)
		elif game.kb.vk == libtcod.KEY_LEFT or game.kb.vk == libtcod.KEY_KP4:
			player_move(-1, 0)
		elif game.kb.vk == libtcod.KEY_RIGHT or game.kb.vk == libtcod.KEY_KP6:
			player_move(1, 0)
		elif game.kb.vk == libtcod.KEY_KP7:
			player_move(-1, -1)
		elif game.kb.vk == libtcod.KEY_KP9:
			player_move(1, -1)
		elif game.kb.vk == libtcod.KEY_KP1:
			player_move(-1, 1)
		elif game.kb.vk == libtcod.KEY_KP3:
			player_move(1, 1)
		elif game.kb.vk == libtcod.KEY_SPACE or game.kb.vk == libtcod.KEY_KP5:
			wait_turn()
		elif game.kb.vk == libtcod.KEY_PAGEUP:
			see_message_log(up=True)
		elif game.kb.vk == libtcod.KEY_PAGEDOWN:
			see_message_log(down=True)

		elif (game.kb.lctrl or game.kb.rctrl) and game.kb.c != 0:
			if key_char == 'd':
				game.debug.menu()
			elif key_char == 'e':
				show_time()
			elif key_char == 'm':
				see_message_history()
			elif key_char == 's':
				if save_game():
					return 'save'
			elif key_char == 'x':
				if quit_game():
					return 'quit'
			else:
				game.message.new('Invalid command', game.turns)
		elif (game.kb.lalt or game.kb.ralt) and game.kb.c != 0:
			game.message.new('Invalid command', game.turns)

		elif game.kb.c != 0:
			if key_char == 'a':
				attack()
			elif key_char == 'b':
				bash()
			elif key_char == 'c':
				close_door()
			elif key_char == 'd':
				drop_item()
			elif key_char == 'e':
				equip_item()
			elif key_char == 'g':
				pickup_item()
			elif key_char == 'i':
				inventory()
			elif key_char == 'k':
				use_skill()
			elif key_char == 'l':
				look()
			elif key_char == 'o':
				open_door()
			elif key_char == 'r':
				remove_item()
			elif key_char == 'u':
				use_item()
			elif key_char == '<':
				climb_up_stairs()
			elif key_char == '>':
				climb_down_stairs()
			elif key_char == 'z':
				sheet.character_sheet()
			elif key_char == '?':
				help()
			else:
				game.message.new('Invalid command', game.turns)
		game.mouse.lbutton_pressed = False


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
	target = [obj for obj in game.current_map.objects if obj.y == y and obj.x == x and obj.entity]

	#attack if target found, move otherwise
	if target:
		game.player.attack(target[0])
	elif not game.player.can_move():
		game.message.new("You can't move!", game.turns)
		game.player_took_turn = True
	else:
		if game.current_map.tile[x][y]['name'] == 'door':
			open_door(dx, dy)
		elif game.current_map.tile[x][y]['name'] == 'locked door':
			game.message.new('The door is locked!', game.turns)
		else:
			game.char.move(dx, dy, game.current_map)
			if game.current_map.tile[game.char.x][game.char.y]['type'] == 'trap' and not game.player.is_above_ground():
				if game.current_map.tile_is_invisible(game.char.x, game.char.y):
					util.trigger_trap(game.char.x, game.char.y)
				else:
					game.message.new('You sidestep the ' + game.current_map.tile[game.char.x][game.char.y]['name'] + '.', game.turns)
			if game.current_map.tile[game.char.x][game.char.y]['name'] in ['deep water', 'very deep water']:
				if 'swimming' not in game.player.flags:
					game.player.flags.append('swimming')
				stamina_loss = (100 - game.player.skills[game.player.find_skill('Swimming')].level) / 2
				if stamina_loss == 0:
					stamina_loss = 1
				game.player.lose_stamina(stamina_loss)
				if game.player.no_stamina():
					game.message.new('You drown!', game.turns, libtcod.light_orange)
					game.message.new('*** Press space ***', game.turns)
					game.cause_of_death = 'drowning'
					game.game_state = 'death'
				else:
					game.player.skills[game.player.find_skill('Swimming')].gain_xp(2)
			elif 'swimming' in game.player.flags:
				game.player.flags.remove('swimming')

			if game.current_map.location_id == 0:
				px = game.current_map.map_width / 3
				py = game.current_map.map_height / 3
				if (game.char.y / py) == 0 or (game.char.x / px) == 0 or (game.char.y / py) == 2 or (game.char.x / px) == 2:
					game.worldmap.player_positionx += dx
					game.worldmap.player_positiony += dy
					if game.worldmap.player_positionx not in range(game.WORLDMAP_WIDTH):
						game.worldmap.player_positionx = game.WORLDMAP_WIDTH - abs(game.worldmap.player_positionx)
					if game.worldmap.player_positiony not in range(game.WORLDMAP_HEIGHT):
						game.worldmap.player_positiony = game.WORLDMAP_HEIGHT - abs(game.worldmap.player_positiony)
					level = (game.worldmap.player_positiony * game.WORLDMAP_WIDTH) + game.worldmap.player_positionx
					util.change_maps(level)
			util.items_at_feet()
		game.fov_recompute = True


# attack someone (primarily use for ranged weapons)
def attack():
	game.message.new('Attack... (Arrow keys to move cursor, TAB to cycle targets, ENTER to attack, ESC to exit)', game.turns)
	util.render_map()
	dx = game.char.x - game.curx
	dy = game.char.y - game.cury
	possible_targets = [obj for obj in game.current_map.objects if libtcod.map_is_in_fov(game.fov_map, obj.x, obj.y) and obj.entity]
	target = None
	ranged = False
	pt = 0

	while True:
		libtcod.console_set_default_background(0, libtcod.white)
		libtcod.console_rect(0, game.MAP_X + dx, dy + 1, 1, 1, False, libtcod.BKGND_SET)
		libtcod.console_flush()
		libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS, game.kb, game.mouse, True)
		dx, dy = key_check(game.kb, dx, dy)
		if game.kb.vk == libtcod.KEY_ESCAPE:
			del game.message.log[len(game.message.log) - 1]
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

		if game.kb.vk == libtcod.KEY_ENTER:
			if not game.current_map.tile_is_explored(px, py):
				game.message.new("You can't fight darkness.", game.turns)
			else:
				target = [obj for obj in game.current_map.objects if obj.y == py and obj.x == px and obj.entity]
				if not target:
					game.message.new('There is no one here.', game.turns)
				elif abs(px - game.char.x) > 1 or abs(py - game.char.y) > 1:
					if (abs(px - game.char.x) == 2 and abs(py - game.char.y) <= 2) or (abs(py - game.char.y) == 2 and abs(px - game.char.x) <= 2) and game.player.skills[game.player.find_weapon_type()].name == 'Polearm':
						break
					elif game.player.skills[game.player.find_weapon_type()].name not in ['Bow', 'Missile']:
						game.message.new('Target is out of range.', game.turns)
						target = []
					else:
						ranged = True
			break

		if game.kb.vk == libtcod.KEY_TAB:
			if possible_targets:
				pt += 1
				if pt == len(possible_targets):
					pt = 0
				dx = possible_targets[pt].x - game.curx
				dy = possible_targets[pt].y - game.cury

		libtcod.console_set_default_foreground(game.con, libtcod.white)
		libtcod.console_set_default_background(game.con, libtcod.black)
		libtcod.console_rect(game.con, 0, 0, game.MAP_WIDTH, 1, True, libtcod.BKGND_SET)
		libtcod.console_blit(game.con, 0, 0, game.MAP_WIDTH, game.MAP_HEIGHT, 0, game.MAP_X, game.MAP_Y)
	if target:
		game.player.attack(target[0], ranged)


# bash open something (only good against locked doors and chests)
def bash():
	attempt = False
	for x in range(-1, 2):
		for y in range(-1, 2):
			if 'locked' in game.current_map.tile[game.char.x + x][game.char.y + y]:
				name = game.current_map.tile[game.char.x + x][game.char.y + y]['name']
				if game.player.strength >= util.roll_dice(1, 40):
					game.message.new('You bash open the ' + name + '.', game.turns)
					if name == 'locked door':
						game.current_map.set_tile_values('opened door', game.char.x + x, game.char.y + y)
					if name == 'locked chest':
						if 'trapped' in game.current_map.tile[game.char.x + x][game.char.y + y]:
							game.current_map.tile[game.char.x + x][game.char.y + y].update({game.chest_trap[libtcod.random_get_int(game.rnd, 0, len(game.chest_trap) - 1)]: True})
							game.current_map.tile[game.char.x + x][game.char.y + y].pop('trapped', None)
							util.trigger_trap(game.char.x + x, game.char.y + y, chest=True)
						game.current_map.set_tile_values('empty chest', game.char.x + x, game.char.y + y)
						nb_items = libtcod.random_get_int(game.rnd, 2, 4)
						for i in range(nb_items):
							game.current_map.objects.append(game.baseitems.loot_generation(game.char.x + x, game.char.y + y, game.current_map.threat_level))
				else:
					game.message.new('You failed to bash open the ' + name + '.', game.turns)
				game.player.take_damage(1, 'bashing a ' + name)
				game.player.lose_stamina(1)
				game.player_took_turn = True
				attempt = True
	if not attempt:
		game.message.new('You bash air. You find it strangely exhilarating.', game.turns)


# climb down some stairs
def climb_down_stairs():
	location_name = game.current_map.location_name
	location_abbr = game.current_map.location_abbr
	location_id = game.current_map.location_id
	threat_level = game.current_map.threat_level
	dungeon_type = game.current_map.type
	map_width = game.DUNGEON_MAP_WIDTH
	map_height = game.DUNGEON_MAP_HEIGHT
	op = (0, 0, 0)

	if game.current_map.tile[game.char.x][game.char.y]['icon'] != '>':
		game.message.new('You see no stairs going in that direction!', game.turns)
	else:
		if game.current_map.location_id > 0:
			level = game.current_map.location_level + 1
			game.message.new('You climb down the stairs.', game.turns)
			util.store_map(game.current_map)
			IO.autosave(False)
			map_width = game.current_map.map_width
			map_height = game.current_map.map_height
			if util.roll_dice(1, 10) == 10:
				threat_level += 1
		else:
			level = 1
			for (id, name, abbr, x, y, tlevel, dtype) in game.worldmap.dungeons:
				if y * game.WORLDMAP_WIDTH + x == game.current_map.location_level:
					location_id = id
					location_name = name
					location_abbr = abbr
					threat_level = tlevel
					dungeon_type = dtype
					if dtype == 'Maze':
						map_width = game.MAP_WIDTH
						map_height = game.MAP_HEIGHT
			game.message.new('You enter the ' + location_name + '.', game.turns)
			util.decombine_maps()
			op = (game.current_map.location_level, game.char.x, game.char.y)
			util.store_map(game.current_map)
			for i in range(len(game.border_maps)):
				util.store_map(game.border_maps[i])
			IO.autosave()

		util.loadgen_message()
		game.current_map = util.fetch_map({'name': location_name, 'id': location_id, 'abbr': location_abbr, 'level': level, 'threat': threat_level, 'map_width': map_width, 'map_height': map_height, 'type': dungeon_type}, dir='up')
		game.current_map.overworld_position = op
		IO.autosave_current_map()
		game.current_map.check_player_position()
		util.initialize_fov()
		game.fov_recompute = True
		game.player_took_turn = True


# climb up some stairs
def climb_up_stairs():
	combine = False
	location_name = game.current_map.location_name
	location_abbr = game.current_map.location_abbr
	location_id = game.current_map.location_id
	threat_level = game.current_map.threat_level
	dungeon_type = game.current_map.type
	map_width = game.DUNGEON_MAP_WIDTH
	map_height = game.DUNGEON_MAP_HEIGHT

	if game.current_map.tile[game.char.x][game.char.y]['icon'] != '<':
		game.message.new('You see no stairs going in that direction!', game.turns)
	else:
		if game.current_map.location_level > 1:
			level = game.current_map.location_level - 1
			game.message.new('You climb up the stairs.', game.turns)
		else:
			combine = True
			(level, game.char.x, game.char.y) = game.current_map.overworld_position
			location_id = 0
			location_name = 'Wilderness'
			location_abbr = 'WD'
			game.message.new('You return to the ' + location_name + '.', game.turns)

		util.store_map(game.current_map)
		util.loadgen_message()
		IO.autosave(False)
		if not combine:
			game.current_map = util.fetch_map({'name': location_name, 'id': location_id, 'abbr': location_abbr, 'level': level, 'threat': threat_level, 'map_width': map_width, 'map_height': map_height, 'type': dungeon_type}, dir='down')
			IO.autosave_current_map()
		else:
			game.current_map = util.fetch_map({'name': location_name, 'id': location_id, 'abbr': location_abbr, 'level': level, 'map_width': game.current_map.map_width, 'map_height': game.current_map.map_height})
			util.fetch_border_maps()
			IO.autosave_current_map()
			util.combine_maps()
		game.current_map.check_player_position()
		util.initialize_fov()
		game.fov_recompute = True
		game.player_took_turn = True


# close door
def close_door():
	dx, dy = 0, 0
	game.message.new('Close door in which direction?', game.turns)
	libtcod.console_flush()
	libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS, game.kb, game.mouse, True)
	dx, dy = key_check(game.kb, dx, dy)

	if game.current_map.tile[game.char.x + dx][game.char.y + dy]['name'] == 'opened door':
		game.current_map.set_tile_values('door', game.char.x + dx, game.char.y + dy)
		game.message.new('You close the door.', game.turns)
		game.fov_recompute = True
		game.player_took_turn = True
	elif game.current_map.tile[game.char.x + dx][game.char.y + dy]['name'] in ['door', 'locked door']:
		game.message.new('That door is already closed!', game.turns)
	elif dx != 0 or dy != 0:
		game.message.new('There is no door in that direction!', game.turns)


# drop an item
# stuff to do: drop lit torch
def drop_item():
	qty = 1
	if not game.player.inventory:
		game.message.new('Your inventory is empty.', game.turns)
	else:
		output = util.item_stacking(game.player.inventory)
		choice = game.messages.box('Drop item', 'Up/down to select, ENTER to drop, ESC to exit', 'center_mapx', 'center_mapy', 65, max(19, len(output) + 4), output, inv=True, step=2, mouse_exit=True)
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
	game.draw_gui = True


# equip an item
def equip_item():
	if not any(item.is_equippable() for item in game.player.inventory):
		game.message.new("You don't have any equippable items.", game.turns)
	else:
		output = util.item_stacking(game.player.inventory, True)
		choice = game.messages.box('Wear/Equip an item', 'Up/down to select, ENTER to equip, ESC to exit', 'center_mapx', 'center_mapy', 65, max(19, len(output) + 4), output, inv=True, step=2, mouse_exit=True)
		util.reset_quantity(game.player.inventory)
		if choice != -1:
			game.player.equip_item(output[choice])
	game.draw_gui = True


# help screen
# stuff to do: change manual screen
def help():
	contents = IO.load_manual()
	game.messages.box('Help', None, 'center_mapx', 'center_screeny', len(max(contents, key=len)) + 20, len(contents) + 4, contents, input=False)
	game.draw_gui = True


# highscore screen
def highscores():
	if game.highscore:
		contents = []
		for (score, line1, line2) in game.highscore:
			contents.append(str(score).ljust(6) + line1)
			contents.append('      ' + line2)
			contents.append(' ')
		game.messages.box('High scores', None, 0, 0, game.SCREEN_WIDTH, game.SCREEN_HEIGHT, contents, input=False)
	else:
		contents = ['The high scores file is empty.']
		game.messages.box('High scores', None, 'center_screenx', 'center_screeny', len(max(contents, key=len)) + 16, len(contents) + 4, contents, input=False, align=libtcod.CENTER)
	game.draw_gui = True


# see your inventory
def inventory():
	if not game.player.inventory:
		game.message.new('Your inventory is empty.', game.turns)
	else:
		output = util.item_stacking(game.player.inventory)
		choice = game.messages.box('Inventory', 'Up/down to select, ENTER to use, ESC to exit', 'center_mapx', 'center_mapy', 65, max(19, len(output) + 4), output, inv=True, step=2, mouse_exit=True)
		util.reset_quantity(game.player.inventory)
		if choice != -1:
			output[choice].use()
	game.draw_gui = True


# look (with keyboard)
def look():
	game.message.new('Looking... (Arrow keys to move cursor, ESC to exit)', game.turns)
	util.render_map()
	dx = game.char.x - game.curx
	dy = game.char.y - game.cury

	while True:
		libtcod.console_set_default_background(0, libtcod.white)
		libtcod.console_rect(0, game.MAP_X + dx, dy + 1, 1, 1, False, libtcod.BKGND_SET)
		libtcod.console_flush()
		text = ""

		libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS, game.kb, game.mouse, True)
		dx, dy = key_check(game.kb, dx, dy)
		if game.kb.vk == libtcod.KEY_ESCAPE:
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

		# create a list with the names of all objects at the cursor coordinates
		if dx in range(game.MAP_WIDTH - 1) and dy in range(game.MAP_HEIGHT - 1) and game.current_map.tile_is_explored(px, py):
			names = [obj for obj in game.current_map.objects if obj.x == px and obj.y == py]
			prefix = 'you see '
			if not libtcod.map_is_in_fov(game.fov_map, px, py):
				prefix = 'you remember seeing '
				for i in range(len(names) - 1, -1, -1):
					if names[i].entity is not None:
						names.pop(i)
			if (px, py) == (game.char.x, game.char.y):
				text = 'you see yourself'
			elif names == []:
				if game.current_map.tile_is_invisible(px, py):
					text = prefix + 'a floor'
				else:
					text = prefix + game.current_map.tile[px][py]['article'] + game.current_map.tile[px][py]['name']
			elif len(names) > 1:
				text = prefix
				for i in range(len(names)):
					if i == len(names) - 1:
						text += ' and '
					elif i > 0:
						text += ', '
					if names[i].item is not None:
						text += names[i].item.get_name(True)
					if names[i].entity is not None:
						text += names[i].entity.get_name(True)
			else:
				if names[0].item is not None:
					text = prefix + names[0].item.get_name(True)
				if names[0].entity is not None:
					text = prefix + names[0].entity.get_name(True)

		libtcod.console_set_default_foreground(game.con, libtcod.light_yellow)
		libtcod.console_rect(game.con, 0, 0, game.MAP_WIDTH, 2, True, libtcod.BKGND_NONE)
		libtcod.console_print_rect(game.con, 0, 0, game.MAP_WIDTH - 18, game.MAP_HEIGHT, text)
		libtcod.console_blit(game.con, 0, 0, game.MAP_WIDTH, game.MAP_HEIGHT, 0, game.MAP_X, game.MAP_Y)
	game.draw_map = True


# open door
def open_door(x=None, y=None):
	dx, dy = 0, 0
	if x is None:
		game.message.new('Open door in which direction?', game.turns)
		libtcod.console_flush()
		libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS, game.kb, game.mouse, True)
		dx, dy = key_check(game.kb, dx, dy)
	else:
		dx, dy = x, y

	if game.current_map.tile[game.char.x + dx][game.char.y + dy]['name'] == 'door':
		game.current_map.set_tile_values('opened door', game.char.x + dx, game.char.y + dy)
		game.message.new('You open the door.', game.turns)
		game.fov_recompute = True
		game.player_took_turn = True
	elif game.current_map.tile[game.char.x + dx][game.char.y + dy]['name'] == 'opened door':
		game.message.new('That door is already opened!', game.turns)
	elif game.current_map.tile[game.char.x + dx][game.char.y + dy]['name'] == 'locked door':
		game.message.new('The door is locked!', game.turns)
	elif dx != 0 or dy != 0:
		game.message.new('There is no door in that direction!', game.turns)


# ingame options menu
def options_menu():
	contents = ['Read the manual', 'Change settings', 'View high scores', 'View message log', 'Save and quit game', 'Quit without saving']
	choice = game.messages.box('Menu', None, 'center_mapx', 'center_mapy', len(max(contents, key=len)) + 6, len(contents) + 4, contents, mouse_exit=True, step=2, scrollbar=False)
	if choice == 0:
		help()
	if choice == 1:
		settings()
	if choice == 2:
		highscores()
	if choice == 3:
		see_message_history()
	if choice == 4:
		return 'save'
	if choice == 5:
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

	if not nb_items and not game.current_map.tile[game.char.x][game.char.y]['type'] == 'rock':
		game.message.new('There is nothing to pick up.', game.turns)
	elif not nb_items and game.current_map.tile[game.char.x][game.char.y]['type'] == 'rock':
		item = game.baseitems.create_item('uncursed ', '', 'stone', '', 'identified')
		item.turns_created = game.turns
		game.player.inventory.append(item)
		game.message.new('You pick up a stone.', game.turns, libtcod.green)
	elif len(nb_items) == 1:
		nb_items[0].pick_up(nb_items[0].turn_created)
		game.current_map.objects.pop(itempos[0])
	else:
		qty = 1
		output = util.item_stacking(nb_items)
		choice = game.messages.box('Get an item', 'Up/down to select, ENTER to get, ESC to exit', 'center_mapx', 'center_mapy', 65, max(19, len(output) + 4), output, inv=True, step=2, mouse_exit=True)
		if choice != -1:
			if output[choice].quantity > 1 and output[choice].type != 'money':
				libtcod.console_print(0, game.PLAYER_STATS_WIDTH + 2, 1, 'Pickup how many: _')
				libtcod.console_flush()
				qty = game.messages.input('', 0, game.PLAYER_STATS_WIDTH + 19, 1)
				if qty == '' or not qty.isdigit():
					choice = -1
				elif int(qty) < 1 or int(qty) > output[choice].quantity:
					choice = -1
			if output[choice].quantity > 1 and output[choice].type == 'money':
				qty = output[choice].quantity
		if choice != -1:
			x = 0
			for i in range(len(nb_items) - 1, -1, -1):
				if nb_items[i] == output[choice] and x < int(qty):
					nb_items[i].pick_up(nb_items[i].turn_created)
					game.current_map.objects.pop(itempos[i])
					x += 1
		util.reset_quantity(nb_items)
		game.draw_gui = True


# dialog to confirm quitting the game
def quit_game():
	util.render_map()
	libtcod.console_print(0, game.MAP_X, game.MAP_Y, 'Are you sure you want to quit the game? (y/n)')
	libtcod.console_flush()
	libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS, game.kb, game.mouse, True)
	if chr(game.kb.c) == 'y' or chr(game.kb.c) == 'Y':
		return True
	return False


# remove/unequip an item
def remove_item():
	if not game.player.equipment:
		game.message.new("You don't have any equipped items.", game.turns)
	else:
		choice = game.messages.box('Remove/Unequip an item', 'Up/down to select, ENTER to remove, ESC to exit', 'center_mapx', 'center_mapy', 65, max(19, len(game.player.equipment) + 4), game.player.equipment, inv=True, step=2, mouse_exit=True)
		if choice != -1:
			game.player.unequip(choice)
	game.draw_gui = True


# dialog to confirm saving the game
def save_game():
	util.render_map()
	libtcod.console_print(0, game.MAP_X, game.MAP_Y, 'Do you want to save (and quit) the game? (y/n)')
	libtcod.console_flush()
	libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS, game.kb, game.mouse, True)
	if chr(game.kb.c) == 'y' or chr(game.kb.c) == 'Y':
		return True
	return False


# show all the old messages
def see_message_history():
	box_width = game.MESSAGE_WIDTH + 2
	box_height = (game.SCREEN_HEIGHT / 2) + 4
	box = libtcod.console_new(box_width, box_height)
	game.messages.box_gui(box, 0, 0, box_width, box_height, libtcod.green)
	libtcod.console_set_default_foreground(box, libtcod.black)
	libtcod.console_set_default_background(box, libtcod.green)
	libtcod.console_print_ex(box, box_width / 2, 0, libtcod.BKGND_SET, libtcod.CENTER, ' Message History ')
	libtcod.console_set_default_foreground(box, libtcod.green)
	libtcod.console_set_default_background(box, libtcod.black)
	libtcod.console_print_ex(box, box_width / 2, box_height - 1, libtcod.BKGND_SET, libtcod.CENTER, ' Arrow keys - Scroll up/down, ESC - exit ')
	libtcod.console_print_ex(box, box_width - 5, 0, libtcod.BKGND_SET, libtcod.LEFT, '[x]')
	libtcod.console_set_default_foreground(box, libtcod.white)

	scroll = 0
	while True:
		libtcod.console_rect(box, 1, 1, box_width - 2, box_height - 2, True, libtcod.BKGND_SET)
		for i in range(min(box_height - 4, len(game.message.history))):
			libtcod.console_set_default_foreground(box, game.message.history[i + scroll][1])
			libtcod.console_print(box, 2, i + 2, game.message.history[i + scroll][0])
		util.scrollbar(box, box_width - 2, 2, scroll, box_height - 4, len(game.message.history))
		libtcod.console_blit(box, 0, 0, box_width, box_height, 0, (game.SCREEN_WIDTH - box_width) / 2, (game.MAP_HEIGHT - box_height + 2) / 2, 1.0, 1.0)
		libtcod.console_flush()
		ev = libtcod.sys_check_for_event(libtcod.EVENT_ANY, game.kb, game.mouse)
		(mx, my) = (game.mouse.cx, game.mouse.cy)
		if ((game.kb.vk == libtcod.KEY_UP or game.kb.vk == libtcod.KEY_KP8) and ev == libtcod.EVENT_KEY_PRESS) or (ev == libtcod.EVENT_MOUSE_RELEASE and game.mouse.wheel_up):
			if scroll > 0:
				scroll -= 1
		elif ((game.kb.vk == libtcod.KEY_DOWN or game.kb.vk == libtcod.KEY_KP2) and ev == libtcod.EVENT_KEY_PRESS) or (ev == libtcod.EVENT_MOUSE_RELEASE and game.mouse.wheel_down):
			if box_height - 4 + scroll < len(game.message.history):
				scroll += 1
		elif game.kb.vk == libtcod.KEY_ESCAPE and ev == libtcod.EVENT_KEY_PRESS:
			break
		elif (mx == ((game.SCREEN_WIDTH - box_width) / 2) + box_width - 4 and my == (game.MAP_HEIGHT - box_height + 2) / 2) and (ev == libtcod.EVENT_MOUSE_RELEASE) and game.mouse.lbutton_pressed:
			break
	libtcod.console_delete(box)
	game.draw_gui = True


# show some of the old messages
def see_message_log(up=False, down=False):
	if up:
		if game.old_msg < len(game.message.log) - game.MESSAGE_HEIGHT:
			game.old_msg += 1
	if down:
		if game.old_msg > 0:
			game.old_msg -= 1
	util.render_message_panel()
	libtcod.console_flush()


# settings screen
def settings():
	width, height = 44, 10
	box = libtcod.console_new(width, height)
	game.messages.box_gui(box, 0, 0, width, height, libtcod.green)
	libtcod.console_set_default_foreground(box, libtcod.black)
	libtcod.console_set_default_background(box, libtcod.green)
	libtcod.console_print_ex(box, width / 2, 0, libtcod.BKGND_SET, libtcod.CENTER, ' Settings ')
	libtcod.console_set_default_foreground(box, libtcod.green)
	libtcod.console_set_default_background(box, libtcod.black)
	libtcod.console_print_ex(box, width - 5, 0, libtcod.BKGND_SET, libtcod.LEFT, '[x]')
	libtcod.console_set_default_foreground(box, libtcod.white)
	util.change_settings(box, width, height, blitmap=True)
	libtcod.console_delete(box)
	game.draw_gui = True


# print current time/date
def show_time():
	game.message.new(game.time.time_to_text(), game.turns)


# show a miniature world map
# stuff to do: add towns, zoom
def show_worldmap():
	box = libtcod.console_new(game.SCREEN_WIDTH, game.SCREEN_HEIGHT)
	game.messages.box_gui(box, 0, 0, game.SCREEN_WIDTH, game.SCREEN_HEIGHT, libtcod.green)
	libtcod.console_set_default_foreground(box, libtcod.black)
	libtcod.console_set_default_background(box, libtcod.green)
	libtcod.console_print_ex(box, game.SCREEN_WIDTH / 2, 0, libtcod.BKGND_SET, libtcod.CENTER, ' World Map ')
	libtcod.console_set_default_foreground(box, libtcod.green)
	libtcod.console_set_default_background(box, libtcod.black)
	libtcod.console_print_ex(box, game.SCREEN_WIDTH / 2, game.SCREEN_HEIGHT - 1, libtcod.BKGND_SET, libtcod.CENTER, '[ Red dot - You, Black dots - Dungeons, S - Save map, Z - Zoom, TAB - Exit ]')
	libtcod.console_set_default_foreground(box, libtcod.white)
	util.showmap(box)
	libtcod.console_delete(box)
	game.draw_gui = True


# use an item
def use_item():
	if not game.player.inventory:
		game.message.new('Your inventory is empty.', game.turns)
	else:
		output = util.item_stacking(game.player.inventory)
		choice = game.messages.box('Use an item', 'Up/down to select, ENTER to use, ESC to exit', 'center_mapx', 'center_mapy', 65, max(19, len(output) + 4), output, inv=True, step=2, mouse_exit=True)
		util.reset_quantity(game.player.inventory)
		if choice != -1:
			output[choice].use()
	game.draw_gui = True


# use a skill
def use_skill():
	skills = [x for x in game.player.skills if x.can_use]
	output = [x.name for x in skills]
	choice = game.messages.box('Use a skill', 'Up/down to select, ENTER to use, ESC to exit', 'center_mapx', 'center_mapy', 65, max(19, len(output) + 4), output, step=2, mouse_exit=True)
	if choice != -1:
		if output[choice] == 'Detect Traps':
			skills[choice].active()

		if output[choice] == 'Artifacts':
			output2 = game.player.inventory + game.player.equipment
			choice2 = game.messages.box('Use skill on which item', 'Up/down to select, ENTER to use, ESC to exit', 'center_mapx', 'center_mapy', 65, max(19, len(output) + 4), output2, inv=True, step=2, mouse_exit=True)
			if choice2 != -1:
				if output2[choice2].is_identified():
					game.message.new('That item is already identified.', game.turns)
				elif output2[choice2].assay == game.player.level:
					game.message.new('You already tried to identify that item. You can do it once per item per level.', game.turns)
				else:
					if output2[choice2].level * 5 > skills[choice].level:
						game.message.new('Your skill is not high enough to identity that item.', game.turns)
						output2[choice2].assay = game.player.level
						skills[choice].gain_xp(1)
					else:
						game.message.new('You identify the item!', game.turns)
						output2[choice2].flags.append('identified')
						skills[choice].gain_xp(5)
					game.player_took_turn = True

		if output[choice] == 'Disarm Traps':
			attempt = False
			for x in range(-1, 2):
				for y in range(-1, 2):
					if 'trapped' in game.current_map.tile[game.char.x + x][game.char.y + y]:
						if skills[choice].level >= libtcod.random_get_int(game.rnd, 0, 150):
							if game.current_map.tile[game.char.x + x][game.char.y + y]['type'] == 'trap':
								game.current_map.set_tile_values('floor', game.char.x + x, game.char.y + y)
								game.message.new('You disarm the trap.', game.turns)
							else:
								game.message.new('You disarm the trap chest.', game.turns)
								game.current_map.tile[game.char.x + x][game.char.y + y].pop('trapped', None)
							skills[choice].gain_xp(5)
						else:
							game.message.new('You failed to disarm the trap.', game.turns)
							if util.roll_dice(1, 50) > game.player.karma:
								if game.current_map.tile[game.char.x + x][game.char.y + y]['type'] == 'trap':
									util.trigger_trap(game.char.x + x, game.char.y + y)
								else:
									game.current_map.tile[game.char.x + x][game.char.y + y].update({game.chest_trap[libtcod.random_get_int(game.rnd, 0, len(game.chest_trap) - 1)]: True})
									game.current_map.tile[game.char.x + x][game.char.y + y].pop('trapped', None)
									util.trigger_trap(game.char.x + x, game.char.y + y, chest=True)
							skills[choice].gain_xp(1)
						game.player_took_turn = True
						attempt = True
			if not attempt:
				game.message.new('There are no traps in your surroundings.', game.turns)

		if output[choice] == 'Lockpicking':
			attempt = False
			for x in range(-1, 2):
				for y in range(-1, 2):
					if 'locked' in game.current_map.tile[game.char.x + x][game.char.y + y]:
						name = game.current_map.tile[game.char.x + x][game.char.y + y]['name']
						if skills[choice].level >= libtcod.random_get_int(game.rnd, 0, 150):
							game.message.new('You unlock the ' + name + '.', game.turns)
							if name == 'locked door':
								game.current_map.set_tile_values('opened door', game.char.x + x, game.char.y + y)
							if name == 'locked chest':
								game.current_map.set_tile_values('empty chest', game.char.x + x, game.char.y + y)
								nb_items = util.roll_dice(2, 4)
								for i in range(nb_items):
									game.current_map.objects.append(game.baseitems.loot_generation(game.char.x + x, game.char.y + y, game.current_map.threat_level))
							skills[choice].gain_xp(5)
						else:
							game.message.new('You failed to unlock the ' + name + '.', game.turns)
							if 'trapped' in game.current_map.tile[game.char.x + x][game.char.y + y]:
								if game.player.karma < util.roll_dice(1, 30):
									game.current_map.tile[game.char.x + x][game.char.y + y].update({game.chest_trap[libtcod.random_get_int(game.rnd, 0, len(game.chest_trap) - 1)]: True})
									game.current_map.tile[game.char.x + x][game.char.y + y].pop('trapped', None)
									util.trigger_trap(game.char.x + x, game.char.y + y, chest=True)
							skills[choice].gain_xp(1)
						game.player_took_turn = True
						attempt = True
			if not attempt:
				game.message.new('There is nothing to unlock in your surroundings.', game.turns)
	game.draw_gui = True


# passing one turn
def wait_turn():
	game.message.new('Time passes...', game.turns)
	game.fov_recompute = True
	game.player_took_turn = True
