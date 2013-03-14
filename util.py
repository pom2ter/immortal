import libtcodpy as libtcod
import pickle
import os
import copy
import game
import commands
import effects


#######################################
# miscellanous functions
#######################################

# add a turn and do checks for statuses and stuffies
def add_turn():
	game.turns += 1
	game.gametime.update(1)
	game.player_move = True
	game.redraw_gui = True

	if game.turns % (50 - game.player.endurance) == 0:
		game.player.heal_health(1)
	if game.turns % (50 - game.player.intelligence) == 0:
		game.player.heal_mana(1)

	game.player.item_expiration()
	game.player.item_is_active()
	game.player.check_condition()
	game.fov_torch = any('torchlight' in x.flags and x.active for x in game.player.inventory)

	if 'detect_trap' in game.player.flags:
		game.gametime.update(1)
		dice = libtcod.random_get_int(game.rnd, 0, 200)
		if game.player.thieving_skills[0].level >= dice:
			if len(game.traps) > 0:
				dice = libtcod.random_get_int(game.rnd, 0, len(game.traps) - 1)
				for i, (x, y) in enumerate(game.traps):
					if i == dice:
						game.current_map.tiles[x][y] = game.tiles.get_tile(game.current_map.tiles[x][y].name)
						if 'invisible' in game.current_map.tiles[x][y].flags:
							game.current_map.tiles[x][y].flags.remove('invisible')
				game.message.new('You detect a trap!', game.turns)
				game.player.thieving_skills[0].gain_xp(3)
			else:
				game.player.thieving_skills[0].gain_xp(1)
		else:
			dice = libtcod.random_get_int(game.rnd, 0, 100)
			if game.player.thieving_skills[0].level >= dice:
				game.player.thieving_skills[0].gain_xp(1)


# change game settings
def change_settings(box, width, height, options, blitmap=False):
	fonts = ['  Small  ', '  Large  ']
	confirm, cancel = False, False
	if game.font == 'large':
		current = 1
	else:
		current = 0
	lerp = 1.0
	descending = True

	key = libtcod.Key()
	libtcod.console_print_rect(box, 2, 2, width - 4, 2, '(You may need to restart the game for the changes to take effect)')
	libtcod.console_print(box, 2, 5, 'Font: ')

	while not confirm and not cancel:
		for i in range(len(fonts)):
			libtcod.console_set_default_background(box, libtcod.black)
			if current == i:
				color, lerp, descending = color_lerp(lerp, descending)
				libtcod.console_set_default_background(box, color)
			libtcod.console_print_ex(box, 10 + (i * 10), 5, libtcod.BKGND_SET, libtcod.LEFT, fonts[i])

		if blitmap:
			libtcod.console_blit(box, 0, 0, width, height, 0, ((game.MAP_WIDTH - width) / 2) + game.MAP_X, (game.MAP_HEIGHT - height) / 2, 1.0, 1.0)
		else:
			libtcod.console_blit(box, 0, 0, width, height, 0, (game.SCREEN_WIDTH - width) / 2, (game.SCREEN_HEIGHT - height) / 2, 1.0, 1.0)
		libtcod.console_flush()
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, libtcod.Mouse())

		if key.vk == libtcod.KEY_LEFT:
			current -= 1
			if current < 0:
				current = 1
			lerp = 1.0
			descending = True
		elif key.vk == libtcod.KEY_RIGHT:
			current += 1
			if current > 1:
				current = 0
			lerp = 1.0
			descending = True
		elif key.vk == libtcod.KEY_ESCAPE:
			cancel = True
		elif key.vk == libtcod.KEY_ENTER:
			confirm = True

	if confirm:
		f = open('settings.ini', 'wb')
		f.write('[Font]\n')
		if current == 0:
			f.write('small\n')
		else:
			f.write('large\n')
		f.close()


# color fading in/out
def color_lerp(lerp, descending, base=libtcod.black, light=libtcod.light_blue):
	color = base
	if descending:
		lerp -= 0.001
		if lerp < 0.4:
			lerp = 0.4
			descending = False
	else:
		lerp += 0.001
		if lerp > 1.0:
			lerp = 1.0
			descending = True
	color = libtcod.color_lerp(color, light, lerp)
	return color, lerp, descending


# death screens and final score
def death(quit=False):
	libtcod.console_set_default_foreground(0, libtcod.white)
	libtcod.console_set_default_background(0, libtcod.black)
	libtcod.console_clear(0)
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 1, libtcod.BKGND_SET, libtcod.CENTER, 'Summary for ' + game.player.name)
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 3, libtcod.BKGND_SET, libtcod.CENTER, '_________________')
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 4, libtcod.BKGND_SET, libtcod.CENTER, '  /                 \ ')
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 5, libtcod.BKGND_SET, libtcod.CENTER, '  /                   \ ')
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 6, libtcod.BKGND_SET, libtcod.CENTER, '  /                     \ ')
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 7, libtcod.BKGND_SET, libtcod.CENTER, '|                     |')
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 8, libtcod.BKGND_SET, libtcod.CENTER, '|                     |')
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 9, libtcod.BKGND_SET, libtcod.CENTER, '|                     |')
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 10, libtcod.BKGND_SET, libtcod.CENTER, '|                     |')
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 11, libtcod.BKGND_SET, libtcod.CENTER, '|                     |')
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 12, libtcod.BKGND_SET, libtcod.CENTER, '|                     |')
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 13, libtcod.BKGND_SET, libtcod.CENTER, '|                     |')
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 14, libtcod.BKGND_SET, libtcod.CENTER, '|                     |')
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 15, libtcod.BKGND_SET, libtcod.CENTER, '|                     |')
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 16, libtcod.BKGND_SET, libtcod.CENTER, '* |   *     *     *     |*')
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 17, libtcod.BKGND_SET, libtcod.CENTER, '____\(/___\-/___/|\___\/\____/)\_____')

	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 6, libtcod.BKGND_SET, libtcod.CENTER, 'R I P')
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 8, libtcod.BKGND_SET, libtcod.CENTER, game.player.name)
	if quit:
		libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 10, libtcod.BKGND_SET, libtcod.CENTER, 'quitted the game')
		line2 = 'quitted the game'
	else:
		libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 10, libtcod.BKGND_SET, libtcod.CENTER, 'Killed by')
		libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 11, libtcod.BKGND_SET, libtcod.CENTER, game.killer)
		line2 = 'was killed by ' + game.killer
	if game.current_map.location_id == 0:
		libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 12, libtcod.BKGND_SET, libtcod.CENTER, 'in the')
	else:
		libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 12, libtcod.BKGND_SET, libtcod.CENTER, 'on level ' + str(game.current_map.location_level) + ' in the')
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 13, libtcod.BKGND_SET, libtcod.CENTER, game.current_map.location_name)

	score = game.player.score()
	line1 = game.player.name + ', the level ' + str(game.player.level) + ' ' + game.player.gender + ' ' + game.player.race + ' ' + game.player.profession + ','
	if game.current_map.location_id == 0:
		line2 += ' in the ' + game.current_map.location_name + ' (' + str(game.turns) + ' turns)'
	else:
		line2 += ' on level ' + str(game.current_map.location_level) + ' in the ' + game.current_map.location_name + ' (' + str(game.turns) + ' turns)'
	libtcod.console_print(0, 2, 20, 'Final score')
	libtcod.console_print(0, 2, 22, str(score))
	libtcod.console_print(0, 8, 22, line1)
	libtcod.console_print(0, 8, 23,	line2)
	libtcod.console_flush()
	libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS, libtcod.Key(), libtcod.Mouse(), True)

	game.highscore.append((score, line1, line2))
	game.highscore = sorted(game.highscore, reverse=True)
	if len(game.highscore) > 10:
		game.highscore.pop()
	save_high_scores()
	if game.player.name.lower() in game.savefiles:
		os.remove('saves/' + game.player.name.lower())


# returns a particular point on the map
def find_map_position(mapposx, mapposy):
	if int(mapposx) == int(round(mapposx)):
		if int(mapposy) == int(round(mapposy)):
			char = chr(226)
		else:
			char = chr(232)
	else:
		if int(mapposy) == int(round(mapposy)):
			char = chr(227)
		else:
			char = chr(229)
	return char


# change fov radius base on time of day
def fov_radius():
	game.FOV_RADIUS = 9
	if game.gametime.hour == 20:
		game.FOV_RADIUS = 9 - (game.gametime.minute / 10)
	if game.gametime.hour == 6:
		game.FOV_RADIUS = 3 + (game.gametime.minute / 10)
	if game.gametime.hour >= 21 or game.gametime.hour < 6 or game.current_map.location_id != 0:
		game.FOV_RADIUS = 3
	if game.fov_torch:
		if game.FOV_RADIUS < game.TORCH_RADIUS:
			game.FOV_RADIUS = game.TORCH_RADIUS


# return a string with the names of all objects under the mouse
def get_names_under_mouse():
	(x, y) = (game.mouse.cx - game.MAP_X, game.mouse.cy - 1)
	px = x + game.curx
	py = y + game.cury
	if x in range(game.MAP_WIDTH - 1) and y in range(game.MAP_HEIGHT - 1) and game.current_map.explored[px][py]:
		names = [obj for obj in game.current_map.objects if obj.x == px and obj.y == py]
		prefix = 'you see '
		if not libtcod.map_is_in_fov(game.fov_map, px, py):
			prefix = 'you remember seeing '
			for i in range(len(names) - 1, -1, -1):
				if names[i].entity is not None:
					names.pop(i)
		if (px, py) == (game.char.x, game.char.y):
			return 'you see yourself'
		if names == []:
			if game.current_map.tiles[px][py].is_invisible():
				return prefix + 'a floor'
			return prefix + game.current_map.tiles[px][py].article + game.current_map.tiles[px][py].name

		if len(names) > 1:
			string = prefix
			for i in range(len(names)):
				if i == len(names) - 1:
					string += ' and '
				elif i > 0:
					string += ', '
				if names[i].item is not None:
					string += names[i].item.article + names[i].item.name
				if names[i].entity is not None:
					string += names[i].entity.article + names[i].entity.name
			return string
		else:
			if names[0].item is not None:
				return prefix + names[0].item.article + names[0].item.name
			if names[0].entity is not None:
				return prefix + names[0].entity.article + names[0].entity.name
	else:
		return ''


# stack items if possible
def item_stacking(inv, equip=False):
	output = []
	for x in inv:
		if x not in output:
			output.append(x)
		else:
			for y in output:
				if x == y:
					y.quantity += 1
	if equip:
		output = [x for x in output if x.is_equippable()]
	return output


# return formatted string for inventory listing
def inventory_output(inv):
	if inv.is_identified():
		if inv.quantity > 1:
			text_left = str(inv.quantity) + ' ' + inv.plural
		else:
			text_left = inv.name
	else:
		text_left = inv.unidentified_name
	if inv.duration > 0:
		text_left += ' (' + str(inv.duration) + ' turns left)'
	if inv.active:
		text_left += ' *in use*'
	text_right = str(round(inv.weight * inv.quantity, 1)) + ' lbs'
	return text_left, text_right


# output names of items you pass by
def items_at_feet():
	objects = [obj for obj in game.current_map.objects if obj.item and obj.x == game.char.x and obj.y == game.char.y]
	if len(objects) > 1:
		game.message.new('You see several items at your feet.', game.turns)
	elif len(objects) == 1:
		if objects[0].item.name == 'gold':
			commands.pickup_item()
			game.turns -= 1
		else:
			game.message.new('You see ' + objects[0].item.article + objects[0].item.name, game.turns)


# print loading maps message
def loadgen_message():
	libtcod.console_print(game.con, 0, 0, 'Loading/Generating map chunks...')
	libtcod.console_blit(game.con, 0, 0, game.MAP_WIDTH, game.MAP_HEIGHT, 0, game.MAP_X, game.MAP_Y)
	libtcod.console_flush()


# check to see if you can auto-move with mouse
def mouse_auto_move():
	for obj in game.current_map.objects:
		if libtcod.map_is_in_fov(game.fov_map, obj.x, obj.y) and (obj.entity is not None):
			game.message.new('Auto-move aborted: Monster is near', game.turns)
			game.mouse_move = False
			return False
	return True


# reset item quantities to 1
def reset_quantity(inv):
	for x in inv:
		x.quantity = 1


# returns the roll of a die
def roll_dice(nb_dices, nb_faces, multiplier=1, bonus=0):
	return libtcod.random_get_int(game.rnd, nb_dices, nb_dices * nb_faces * multiplier) + bonus


# save changes to the highscores
def save_high_scores():
	f = open('data/highscores.dat', 'wb')
	pickle.dump(game.highscore, f)
	f.close()


# set a map properties based on a fully explore map
def set_full_explore_map():
	set_map = libtcod.map_new(game.current_map.map_width, game.current_map.map_height)
	for py in range(game.current_map.map_height):
		for px in range(game.current_map.map_width):
			libtcod.map_set_properties(set_map, px, py, not game.current_map.tiles[px][py].block_sight, not game.current_map.is_blocked(px, py, False))
	path = libtcod.dijkstra_new(set_map)
	return path


# show the worldmap
def showmap(box, box_width, box_height):
	lerp, choice = 1.0, -1
	descending, keypress = True, False
	libtcod.image_blit_2x(game.worldmap.map_image_small, box, 1, 1)
	mapposx = game.worldmap.player_positionx * (float(game.SCREEN_WIDTH - 2) / float(game.WORLDMAP_WIDTH))
	mapposy = game.worldmap.player_positiony * (float(game.SCREEN_HEIGHT - 2) / float(game.WORLDMAP_HEIGHT))
	char = find_map_position(mapposx, mapposy)
	libtcod.console_set_default_foreground(box, libtcod.black)
	for (id, name, abbr, x, y) in game.worldmap.dungeons:
		dmapposx = x * (float(game.SCREEN_WIDTH - 2) / float(game.WORLDMAP_WIDTH))
		dmapposy = y * (float(game.SCREEN_HEIGHT - 2) / float(game.WORLDMAP_HEIGHT))
		dchar = find_map_position(dmapposx, dmapposy)
		libtcod.console_print_ex(box, int(dmapposx) + 1, int(dmapposy) + 1, libtcod.BKGND_NONE, libtcod.LEFT, dchar)
	while not keypress:
		color, lerp, descending = color_lerp(lerp, descending, light=libtcod.red)
		libtcod.console_set_default_foreground(box, color)
		libtcod.console_print_ex(box, int(mapposx) + 1, int(mapposy) + 1, libtcod.BKGND_NONE, libtcod.LEFT, char)
		libtcod.console_blit(box, 0, 0, box_width, box_height, 0, (game.SCREEN_WIDTH - box_width) / 2, (game.SCREEN_HEIGHT - box_height) / 2, 1.0, 1.0)
		libtcod.console_flush()
		key = libtcod.Key()
		ev = libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, libtcod.Mouse())
		if ev == libtcod.EVENT_KEY_PRESS:
			if chr(key.c) == 's':
				libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, game.SCREEN_HEIGHT / 2, libtcod.BKGND_DARKEN, libtcod.CENTER, ' Saving map... ')
				libtcod.console_flush()
				game.worldmap.create_map_images(2)
			else:
				break


# someone set off a trap :O
def spring_trap(x, y, victim='You'):
	game.current_map.tiles[x][y] = copy.deepcopy(game.tiles.get_tile(game.current_map.tiles[x][y].name))
	if 'invisible' in game.current_map.tiles[x][y].flags:
		game.current_map.tiles[x][y].flags.remove('invisible')
	if libtcod.map_is_in_fov(game.fov_map, x, y):
		game.message.new(victim + ' sprung a trap!', game.turns)
	if 'fx_teleport' in game.current_map.tiles[x][y].flags:
		effects.teleportation(x, y, victim)
	if 'fx_stuck' in game.current_map.tiles[x][y].flags:
		effects.stuck(x, y, victim)
	if 'fx_poison_gas' in game.current_map.tiles[x][y].flags:
		effects.poison_gas(x, y, 3, 20)
	if 'fx_sleep_gas' in game.current_map.tiles[x][y].flags:
		effects.sleeping_gas(x, y, 3, 20)
	if 'fx_fireball' in game.current_map.tiles[x][y].flags:
		effects.fireball(x, y, 3)


#######################################
# main screen functions
#######################################

# initialize the field of vision
def initialize_fov(update=False):
	game.traps = []
	if not update:
		game.fov_map = libtcod.map_new(game.current_map.map_width, game.current_map.map_height)
		for y in range(game.current_map.map_height):
			for x in range(game.current_map.map_width):
				libtcod.map_set_properties(game.fov_map, x, y, not game.current_map.tiles[x][y].block_sight, game.current_map.explored[x][y] and (not game.current_map.is_blocked(x, y)))
	else:
		for y in range(game.char.y - game.FOV_RADIUS, game.char.y + game.FOV_RADIUS):
			for x in range(game.char.x - game.FOV_RADIUS, game.char.x + game.FOV_RADIUS):
				if x < game.current_map.map_width and y < game.current_map.map_height:
					libtcod.map_set_properties(game.fov_map, x, y, not game.current_map.tiles[x][y].block_sight, game.current_map.explored[x][y] and (not game.current_map.is_blocked(x, y)))
					if libtcod.map_is_in_fov(game.fov_map, x, y):
						if game.current_map.tiles[x][y].type == 'trap' and game.current_map.tiles[x][y].is_invisible():
							game.traps.append((x, y))
	# compute paths using dijkstra algorithm
	game.path_dijk = libtcod.dijkstra_new(game.fov_map)
	libtcod.dijkstra_compute(game.path_dijk, game.char.x, game.char.y)
	libtcod.dijkstra_path_set(game.path_dijk, game.path_dx, game.path_dy)


# render the hp and mana bar
def render_bar(con, x, y, total_width, name, value, maximum, bar_color, back_color):
	#render a bar (HP, experience, etc). first calculate the width of the bar
	bar_width = int(float(value) / maximum * total_width)

	#render the background first
	libtcod.console_set_default_background(con, back_color)
	libtcod.console_rect(con, x, y, total_width, 1, False, libtcod.BKGND_SET)

	#now render the bar on top
	libtcod.console_set_default_background(con, bar_color)
	if bar_width > 0:
		libtcod.console_rect(con, x, y, bar_width, 1, False, libtcod.BKGND_SET)

	#finally, some centered text with the values
	libtcod.console_set_default_foreground(con, libtcod.white)
	libtcod.console_print_ex(con, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER, ' ' + name + ': ' + str(value) + '/' + str(maximum) + ' ')


# render the gui of the main screen
def render_gui(color):
	buffer = libtcod.ConsoleBuffer(game.SCREEN_WIDTH, game.SCREEN_HEIGHT)
	for i in range(game.SCREEN_WIDTH):
		buffer.set_fore(i, 0, color.r, color.g, color.b, chr(205))
		buffer.set_fore(i, game.SCREEN_HEIGHT - 1, color.r, color.g, color.b, chr(205))
	for i in range(game.MAP_X, game.SCREEN_WIDTH):
		buffer.set_fore(i, game.MESSAGE_Y - 1, color.r, color.g, color.b, chr(205))
	for i in range(game.SCREEN_HEIGHT):
		buffer.set_fore(0, i, color.r, color.g, color.b, chr(186))
		buffer.set_fore(game.MAP_X - 1, i, color.r, color.g, color.b, chr(186))
		buffer.set_fore(game.SCREEN_WIDTH - 1, i, color.r, color.g, color.b, chr(186))
	buffer.set_back(0, 0, color.r, color.g, color.b)
	buffer.set_back(0, game.SCREEN_HEIGHT - 1, color.r, color.g, color.b)
	buffer.set_back(game.MAP_X - 1, 0, color.r, color.g, color.b)
	buffer.set_back(game.MAP_X - 1, game.MESSAGE_Y - 1, color.r, color.g, color.b)
	buffer.set_back(game.MAP_X - 1, game.SCREEN_HEIGHT - 1, color.r, color.g, color.b)
	buffer.set_back(game.SCREEN_WIDTH - 1, 0, color.r, color.g, color.b)
	buffer.set_back(game.SCREEN_WIDTH - 1, game.MESSAGE_Y - 1, color.r, color.g, color.b)
	buffer.set_back(game.SCREEN_WIDTH - 1, game.SCREEN_HEIGHT - 1, color.r, color.g, color.b)
	buffer.blit(0, fill_fore=True, fill_back=True)


# print the game messages, one line at a time
def render_message_panel():
	libtcod.console_clear(game.panel)
	game.message.delete()
	for y, (line, color, turn) in enumerate(game.message.log):
		new_color = libtcod.color_lerp(libtcod.darkest_grey, color, 1 - ((game.turns - turn) * 0.1))
		libtcod.console_set_default_foreground(game.panel, new_color)
		libtcod.console_print(game.panel, 0, y, line)
	libtcod.console_blit(game.panel, 0, 0, game.MESSAGE_WIDTH, game.MESSAGE_HEIGHT, 0, game.MESSAGE_X, game.MESSAGE_Y)


# print the player stats in the panel
def render_player_stats_panel():
	libtcod.console_set_default_background(game.ps, libtcod.black)
	libtcod.console_clear(game.ps)
	render_bar(game.ps, 0, 5, game.PLAYER_STATS_WIDTH, 'HP', game.player.health, game.player.max_health, libtcod.red, libtcod.darker_red)
	render_bar(game.ps, 0, 6, game.PLAYER_STATS_WIDTH, 'MP', game.player.mana, game.player.max_mana, libtcod.blue, libtcod.darker_blue)
	libtcod.console_print(game.ps, 0, 0, game.player.name)
	libtcod.console_print(game.ps, 0, 1, game.player.race + ' ' + game.player.profession)
	libtcod.console_print(game.ps, 0, 3, game.current_map.location_abbr + '-' + str(game.current_map.location_level) + '     ')
	libtcod.console_print(game.ps, 0, 8, 'LV: ' + str(game.player.level))
	libtcod.console_print(game.ps, 0, 9, 'XP: ' + str(game.player.xp))
	libtcod.console_print(game.ps, 0, 10, 'Str: ' + str(game.player.strength) + ' ')
	libtcod.console_print(game.ps, 0, 11, 'Dex: ' + str(game.player.dexterity) + ' ')
	libtcod.console_print(game.ps, 0, 12, 'Int: ' + str(game.player.intelligence) + ' ')
	libtcod.console_print(game.ps, 0, 13, 'Wis: ' + str(game.player.wisdom) + ' ')
	libtcod.console_print(game.ps, 0, 14, 'End: ' + str(game.player.endurance) + ' ')
	libtcod.console_print(game.ps, 0, 15, 'Karma: ' + str(game.player.karma) + ' ')
	libtcod.console_print(game.ps, 0, game.PLAYER_STATS_HEIGHT - 2, 'Turns: ' + str(game.turns) + ' ')
	libtcod.console_print(game.ps, 0, 17, 'Active skills: ')
	libtcod.console_print(game.ps, 0, 20, 'Condition: ')
	libtcod.console_set_default_foreground(game.ps, libtcod.light_sepia)
	if 'detect_trap' in game.player.flags:
		libtcod.console_print(game.ps, 0, 18, 'DetTrap')

	cond = ''
	if 'stuck' in game.player.flags:
		cond += 'Stuck '
	if 'poison' in game.player.flags:
		cond += 'Psnd '
	if 'sleep' in game.player.flags:
		cond += 'Sleep '
	libtcod.console_print(game.ps, 0, 21, cond)
	libtcod.console_blit(game.ps, 0, 0, game.PLAYER_STATS_WIDTH, game.PLAYER_STATS_HEIGHT, 0, game.PLAYER_STATS_X, game.PLAYER_STATS_Y)


# floating text animations for damage and healing
def render_floating_text_animations():
	for i, (x, y, line, color, turn) in enumerate(reversed(game.hp_anim)):
		new_color = libtcod.color_lerp(libtcod.black, color, 1 - ((turn / 15) * 0.2))
		libtcod.console_set_default_foreground(game.con, new_color)
		libtcod.console_print_ex(game.con, x - game.curx, y - game.cury - (turn / 15), libtcod.BKGND_NONE, libtcod.CENTER, line)
		game.hp_anim[len(game.hp_anim) - i - 1] = (x, y, line, color, turn + 1)
		if turn > 60:
			game.hp_anim.pop(len(game.hp_anim) - i - 1)


# return new colors for tiles animations
def render_tiles_animations(x, y, icon, light, dark, lerp):
	z = libtcod.random_get_int(game.rnd, 1, 70)
	if z == 70:
		l = libtcod.random_get_int(game.rnd, 0, 1)
		if l == 0:
			if lerp >= 0.1:
				lerp -= 0.1
			else:
				lerp += 0.1
		else:
			if lerp < 1.0:
				lerp += 0.1
			else:
				lerp -= 0.1
	front = libtcod.color_lerp(light, icon, lerp)
	back = libtcod.color_lerp(dark, light, lerp)
	return front, back, lerp


# determine the current viewport for the map panel
def find_map_viewport():
	game.curx, game.cury = 0, 0
	if game.current_map.map_width > game.MAP_WIDTH:
		if game.char.x >= game.MAP_WIDTH / 2 and game.char.x <= (game.current_map.map_width - game.MAP_WIDTH) + (game.MAP_WIDTH / 2):
			game.curx = game.char.x - (game.MAP_WIDTH / 2)
		if game.char.x > (game.current_map.map_width - game.MAP_WIDTH) + (game.MAP_WIDTH / 2):
			game.curx = game.current_map.map_width - game.MAP_WIDTH
	if game.current_map.map_height > game.MAP_HEIGHT:
		if game.char.y >= game.MAP_HEIGHT / 2 and game.char.y <= (game.current_map.map_height - game.MAP_HEIGHT) + (game.MAP_HEIGHT / 2):
			game.cury = game.char.y - (game.MAP_HEIGHT / 2)
		if game.char.y > (game.current_map.map_height - game.MAP_HEIGHT) + (game.MAP_HEIGHT / 2):
			game.cury = game.current_map.map_height - game.MAP_HEIGHT


# master function of the game, everything pass through here on every turn
def render_map():
	# recompute FOV if needed (the player moved or something)
	libtcod.console_clear(game.con)
	if game.fov_recompute:
		find_map_viewport()
		fov_radius()
		initialize_fov(True)
		libtcod.map_compute_fov(game.fov_map, game.char.x, game.char.y, game.FOV_RADIUS, game.FOV_LIGHT_WALLS, game.FOV_ALGO)
		game.fov_recompute = False

	# 'torch' animation
	if game.fov_torch:
		game.fov_torchx += 0.2
		tdx = [game.fov_torchx + 20.0]
		dx = libtcod.noise_get(game.fov_noise, tdx, libtcod.NOISE_SIMPLEX) * 1.5
		tdx[0] += 30.0
		dy = libtcod.noise_get(game.fov_noise, tdx, libtcod.NOISE_SIMPLEX) * 1.5
		di = 0.4 * libtcod.noise_get(game.fov_noise, [game.fov_torchx], libtcod.NOISE_SIMPLEX)

	# go through all tiles, and set their background color according to the FOV
	for y in range(game.MAP_HEIGHT):
		for x in range(game.MAP_WIDTH):
			px = x + game.curx
			py = y + game.cury
			visible = libtcod.map_is_in_fov(game.fov_map, px, py)
			if not visible:
				if game.current_map.explored[px][py]:
					libtcod.console_put_char_ex(game.con, x, y, game.current_map.tiles[px][py].icon, game.current_map.tiles[px][py].dark_color, game.current_map.tiles[px][py].dark_back_color)
			else:
				if not game.fov_torch:
					if game.current_map.animation[px][py] is not None:
						(front, back, game.current_map.animation[px][py]['lerp']) = render_tiles_animations(px, py, game.current_map.tiles[px][py].color, game.current_map.animation[px][py]['light_color'], game.current_map.animation[px][py]['dark_color'], game.current_map.animation[px][py]['lerp'])
						libtcod.console_put_char_ex(game.con, x, y, game.current_map.animation[px][py]['icon'], game.current_map.tiles[px][py].color, back)
					elif game.current_map.tiles[px][py].is_animate():
						(front, back, game.current_map.tiles[px][py].lerp) = render_tiles_animations(px, py, game.current_map.tiles[px][py].color, game.current_map.tiles[px][py].back_color, game.current_map.tiles[px][py].anim_color, game.current_map.tiles[px][py].lerp)
						libtcod.console_put_char_ex(game.con, x, y, game.current_map.tiles[px][py].icon, front, back)
					else:
						libtcod.console_put_char_ex(game.con, x, y, game.current_map.tiles[px][py].icon, game.current_map.tiles[px][py].color, game.current_map.tiles[px][py].back_color)
				else:
					base = game.current_map.tiles[px][py].back_color
					if game.current_map.animation[px][py] is not None:
						base = game.current_map.animation[px][py]['light_color']
					light = libtcod.gold
					r = float(px - game.char.x + dx) * (px - game.char.x + dx) + (py - game.char.y + dy) * (py - game.char.y + dy)
					if r < game.SQUARED_TORCH_RADIUS:
						l = (game.SQUARED_TORCH_RADIUS - r) / game.SQUARED_TORCH_RADIUS + di
						if l < 0.0:
							l = 0.0
						elif l > 1.0:
							l = 1.0
						base = libtcod.color_lerp(base, light, l)
					libtcod.console_put_char_ex(game.con, x, y, game.current_map.tiles[px][py].icon, game.current_map.tiles[px][py].color, base)
				game.current_map.explored[px][py] = True

	# draw a line between the player and the mouse cursor
	if game.path_dx in range(game.current_map.map_width) and game.path_dy in range(game.current_map.map_height):
		if game.current_map.explored[game.path_dx][game.path_dy] and not game.current_map.tiles[game.path_dx][game.path_dy].blocked:
			for i in range(libtcod.dijkstra_size(game.path_dijk)):
				x, y = libtcod.dijkstra_get(game.path_dijk, i)
				libtcod.console_set_char_background(game.con, x - game.curx, y - game.cury, libtcod.desaturated_yellow, libtcod.BKGND_SET)

	# move the player if using mouse
	if game.mouse_move:
		if not libtcod.dijkstra_is_empty(game.path_dijk) and mouse_auto_move():
			game.char.x, game.char.y = libtcod.dijkstra_path_walk(game.path_dijk)
			game.fov_recompute = True
			add_turn()
		else:
			items_at_feet()
			game.mouse_move = False

	if not game.mouse_move:
		(mx, my) = (game.mouse.cx - game.MAP_X, game.mouse.cy - 1)
		px = mx + game.curx
		py = my + game.cury
		if mx in range(game.MAP_WIDTH) and my in range(game.MAP_HEIGHT):
			game.path_dx = px
			game.path_dy = py
			libtcod.console_set_char_background(game.con, mx, my, libtcod.white, libtcod.BKGND_SET)
			if game.current_map.explored[px][py] and not game.current_map.tiles[px][py].blocked:
				if game.mouse.lbutton_pressed:
					if mouse_auto_move():
						game.mouse_move = True
			else:
				game.path_dx = 0
				game.path_dy = 0
			if not game.current_map.tiles[game.path_dx][game.path_dy].blocked:
				libtcod.dijkstra_path_set(game.path_dijk, game.path_dx, game.path_dy)
		else:
			game.path_dx = -1
			game.path_dy = -1

	# draw all objects in the map, except the player who his drawn last
	for obj in reversed(game.current_map.objects):
		if obj.name != 'player':
			obj.draw(game.con)
	game.char.draw(game.con)

	libtcod.console_print(game.con, 0, 0, get_names_under_mouse())
	if game.debug.enable:
		libtcod.console_print_ex(game.con, game.SCREEN_WIDTH - 20, 0, libtcod.BKGND_SET, libtcod.RIGHT, str(game.gametime.hour) + ':' + str(game.gametime.minute).rjust(2, '0') + ' (%3d fps)' % libtcod.sys_get_fps())
	render_floating_text_animations()
	libtcod.console_blit(game.con, 0, 0, game.MAP_WIDTH, game.MAP_HEIGHT, 0, game.MAP_X, game.MAP_Y)
