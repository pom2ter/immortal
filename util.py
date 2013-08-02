import libtcodpy as libtcod
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
	game.draw_gui = True
	game.draw_map = True
	libtcod.console_clear(game.con)

	if game.turns % (50 - game.player.endurance) == 0:
		game.player.heal_health(1)
	if game.turns % (50 - game.player.intelligence) == 0:
		game.player.heal_mana(1)
	if game.turns % (40 - game.player.strength) == 0:
		game.player.heal_stamina(1)
		if 'unconscious' in game.player.flags:
			game.message.new('You regain consciousness.', game.turns)
			game.player.flags.remove('unconscious')

	game.player.item_expiration()
	game.player.item_is_active()
	game.player.check_condition()
	game.fov_torch = any('torchlight' in x.flags and x.active for x in game.player.inventory)

	if 'detect_trap' in game.player.flags:
		game.gametime.update(1)
		skill = game.player.find_skill('Detect Traps')
		if game.player.skills[skill].level >= libtcod.random_get_int(game.rnd, 0, 200):
			if len(game.traps) > 0:
				dice = libtcod.random_get_int(game.rnd, 0, len(game.traps) - 1)
				for i, (x, y) in enumerate(game.traps):
					if i == dice:
						game.current_map.set_tile_values(game.current_map.tile[x][y]['name'], x, y)
						if game.current_map.is_invisible(x, y):
							game.current_map.tile[x][y].pop('invisible', None)
				game.message.new('You detect a trap!', game.turns)
				game.player.skills[skill].gain_xp(3)
			else:
				game.player.skills[skill].gain_xp(1)
		else:
			if game.player.skills[skill].level >= libtcod.random_get_int(game.rnd, 0, 100):
				game.player.skills[skill].gain_xp(1)


# change game settings
def change_settings(box, width, height, blitmap=False):
	confirm, cancel = False, False
	fonts = sorted(game.fonts, reverse=True)
	font = 0
	if game.setting_font == 'large':
		font = 2
	elif game.setting_font == 'medium':
		font = 1
	lerp = 1.0
	descending = True
	history = game.setting_history
	current = 0

	key = libtcod.Key()
	libtcod.console_print_rect(box, 2, 2, width - 4, 2, '(You may need to restart the game for the changes to take effect)')
	libtcod.console_print(box, 2, 5, 'Font size: ')
	libtcod.console_print(box, 2, 6, 'Message history size: ')
	while not confirm and not cancel:
		color, lerp, descending = color_lerp(lerp, descending)

		# font size setting
		if current == 0:
			libtcod.console_set_default_foreground(box, libtcod.white)
			libtcod.console_set_default_background(box, color)
		else:
			libtcod.console_set_default_foreground(box, libtcod.grey)
			libtcod.console_set_default_background(box, libtcod.black)
		libtcod.console_rect(box, 26, 5, 13, 1, True, libtcod.BKGND_SET)
		libtcod.console_print_ex(box, 32, 5, libtcod.BKGND_SET, libtcod.CENTER, fonts[font].capitalize())
		libtcod.console_set_default_foreground(box, libtcod.white)
		if current != 0:
			libtcod.console_set_default_foreground(box, libtcod.black)
		elif font == 0:
			libtcod.console_set_default_foreground(box, libtcod.darkest_grey)
		libtcod.console_print_ex(box, 25, 5, libtcod.BKGND_NONE, libtcod.LEFT, chr(27))
		libtcod.console_set_default_foreground(box, libtcod.white)
		if current != 0:
			libtcod.console_set_default_foreground(box, libtcod.black)
		elif font == len(fonts) - 1:
			libtcod.console_set_default_foreground(box, libtcod.darkest_grey)
		libtcod.console_print_ex(box, 39, 5, libtcod.BKGND_NONE, libtcod.LEFT, chr(26))

		# message history size setting
		if current == 1:
			libtcod.console_set_default_foreground(box, libtcod.white)
			libtcod.console_set_default_background(box, color)
		else:
			libtcod.console_set_default_foreground(box, libtcod.grey)
			libtcod.console_set_default_background(box, libtcod.black)
		libtcod.console_rect(box, 26, 6, 13, 1, True, libtcod.BKGND_SET)
		libtcod.console_print_ex(box, 32, 6, libtcod.BKGND_SET, libtcod.CENTER, str(history))
		libtcod.console_set_default_foreground(box, libtcod.white)
		if current != 1:
			libtcod.console_set_default_foreground(box, libtcod.black)
		elif history == 50:
			libtcod.console_set_default_foreground(box, libtcod.darkest_grey)
		libtcod.console_print_ex(box, 25, 6, libtcod.BKGND_NONE, libtcod.LEFT, chr(27))
		libtcod.console_set_default_foreground(box, libtcod.white)
		if current != 1:
			libtcod.console_set_default_foreground(box, libtcod.black)
		elif history == 1000:
			libtcod.console_set_default_foreground(box, libtcod.darkest_grey)
		libtcod.console_print_ex(box, 39, 6, libtcod.BKGND_NONE, libtcod.LEFT, chr(26))

		if blitmap:
			libtcod.console_blit(box, 0, 0, width, height, 0, ((game.MAP_WIDTH - width) / 2) + game.MAP_X, (game.MAP_HEIGHT - height) / 2, 1.0, 1.0)
		else:
			libtcod.console_blit(box, 0, 0, width, height, 0, (game.SCREEN_WIDTH - width) / 2, (game.SCREEN_HEIGHT - height) / 2, 1.0, 1.0)
		libtcod.console_flush()
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, libtcod.Mouse())

		if key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_DOWN:
			lerp = 1.0
			descending = True
		if key.vk == libtcod.KEY_LEFT:
			if current == 0:
				if font > 0:
					font -= 1
			if current == 1:
				if history > 50:
					history -= 50
		elif key.vk == libtcod.KEY_RIGHT:
			if current == 0:
				if font < len(fonts) - 1:
					font += 1
			if current == 1:
				if history < 1000:
					history += 50
		elif key.vk == libtcod.KEY_UP:
			if current > 0:
				current -= 1
		elif key.vk == libtcod.KEY_DOWN:
			if current < 1:
				current += 1
		elif key.vk == libtcod.KEY_ESCAPE:
			cancel = True
		elif key.vk == libtcod.KEY_ENTER:
			confirm = True

	if confirm:
		game.setting_history = history
		if blitmap:
			game.message.trim_history()
		f = open('settings.ini', 'wb')
		f.write('[Font]\n')
		f.write(fonts[font] + '\n')
		f.write('[History]\n')
		f.write(str(history) + '\n')
		f.close()


# color fading in/out
def color_lerp(lerp, descending, base=libtcod.black, light=libtcod.light_blue):
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
	color = libtcod.color_lerp(base, light, lerp)
	return color, lerp, descending


# returns a particular point on the map (when you see the worldmap)
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


# return a string with the names of all objects under the mouse
def get_names_under_mouse():
	(x, y) = (game.mouse.cx - game.MAP_X, game.mouse.cy - 1)
	px = x + game.curx
	py = y + game.cury
	if x in range(game.MAP_WIDTH) and y in range(game.MAP_HEIGHT) and game.current_map.is_explored(px, py):
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
			if game.current_map.is_invisible(px, py):
				return prefix + 'a floor'
			return prefix + game.current_map.tile[px][py]['article'] + game.current_map.tile[px][py]['name']

		if len(names) > 1:
			string = prefix
			for i in range(len(names)):
				if i == len(names) - 1:
					string += ' and '
				elif i > 0:
					string += ', '
				if names[i].item is not None:
					string += names[i].item.get_name(True)
				if names[i].entity is not None:
					string += names[i].entity.get_name(True)
			return string
		else:
			if names[0].item is not None:
				return prefix + names[0].item.get_name(True)
			if names[0].entity is not None:
				return prefix + names[0].entity.get_name(True)
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
	text_left = inv.get_name()
	if inv.duration > 0:
		text_left += ' (' + str(inv.duration) + ' turns left)'
	if inv.active:
		text_left += ' *in use*'
	text_right = str(round(inv.weight * inv.quantity, 1)) + ' lbs'
	return text_left, text_right


# output names of items you pass by
def items_at_feet():
	objects = [obj for obj in game.current_map.objects if obj.x == game.char.x and obj.y == game.char.y and obj.item]
	if len(objects) > 1:
		game.message.new('You see several items at your feet.', game.turns)
	elif len(objects) == 1:
		if objects[0].item.type == 'money':
			commands.pickup_item()
			game.turns -= 1
		else:
			game.message.new('You see ' + objects[0].item.get_name(True), game.turns)


# print loading maps message
def loadgen_message():
	libtcod.console_print(0, game.MAP_X, game.MAP_Y, 'Loading/Generating map chunks...')
	libtcod.console_flush()


# check to see if you can auto-move with mouse
def mouse_auto_move():
	for obj in game.current_map.objects:
		if libtcod.map_is_in_fov(game.fov_map, obj.x, obj.y) and obj.entity is not None:
			game.message.new('Auto-move aborted: Monster is near', game.turns)
			game.mouse_move = False
			return False
	return True


# reset item quantities to 1
def reset_quantity(inv):
	for x in inv:
		x.quantity = 1


# returns the roll of a die
def roll_dice(nb_dices, nb_faces, multiplier=1, bonus=0, extra_roll=False):
	roll = libtcod.random_get_int(game.rnd, nb_dices * multiplier, nb_dices * nb_faces * multiplier) + bonus
	if extra_roll and 100 * roll / ((nb_dices * nb_faces * multiplier) + bonus) >= 80:
		roll = libtcod.random_get_int(game.rnd, nb_dices * multiplier, nb_dices * nb_faces * multiplier) + bonus
	return roll


# set map properties based on a fully explore map
def set_full_explore_map():
	set_map = libtcod.map_new(game.current_map.map_width, game.current_map.map_height)
	for py in range(game.current_map.map_height):
		for px in range(game.current_map.map_width):
			libtcod.map_set_properties(set_map, px, py, not game.current_map.is_sight_blocked(px, py), not game.current_map.is_blocked(px, py, False))
	path = libtcod.dijkstra_new(set_map)
	return path


# show the worldmap
# stuff to do: add towns, zoom
def showmap(box, box_width, box_height):
	lerp, choice = 1.0, -1
	descending, keypress = True, False
	libtcod.image_blit_2x(game.worldmap.map_image_small, box, 1, 1)
	mapposx = game.worldmap.player_positionx * (float(game.SCREEN_WIDTH - 2) / float(game.WORLDMAP_WIDTH))
	mapposy = game.worldmap.player_positiony * (float(game.SCREEN_HEIGHT - 2) / float(game.WORLDMAP_HEIGHT))
	char = find_map_position(mapposx, mapposy)
	libtcod.console_set_default_foreground(box, libtcod.black)
	for (id, name, abbr, x, y, tlevel) in game.worldmap.dungeons:
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
	explored = game.current_map.is_explored(x, y)
	game.current_map.set_tile_values(game.current_map.tile[x][y]['name'], x, y)
	if game.current_map.is_invisible(x, y):
		game.current_map.tile[x][y].pop('invisible', None)
	if explored:
		game.current_map.tile[x][y].update({'explored': True})
	if libtcod.map_is_in_fov(game.fov_map, x, y):
		game.message.new(victim + ' sprung a trap!', game.turns)
	if 'fx_teleport' in game.current_map.tile[x][y]:
		effects.teleportation(x, y, victim)
	if 'fx_stuck' in game.current_map.tile[x][y]:
		effects.stuck(x, y, victim)
	if 'fx_poison_gas' in game.current_map.tile[x][y]:
		effects.poison_gas(x, y, 3, 20)
	if 'fx_sleep_gas' in game.current_map.tile[x][y]:
		effects.sleeping_gas(x, y, 3, 20)
	if 'fx_fireball' in game.current_map.tile[x][y]:
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
				libtcod.map_set_properties(game.fov_map, x, y, not game.current_map.is_sight_blocked(x, y), game.current_map.is_explored(x, y) and (not game.current_map.is_blocked(x, y)))
	else:
		for y in range(game.char.y - game.FOV_RADIUS, game.char.y + game.FOV_RADIUS):
			for x in range(game.char.x - game.FOV_RADIUS, game.char.x + game.FOV_RADIUS):
				if x < game.current_map.map_width and y < game.current_map.map_height:
					libtcod.map_set_properties(game.fov_map, x, y, not game.current_map.is_sight_blocked(x, y), game.current_map.is_explored(x, y) and (not game.current_map.is_blocked(x, y)))
					if libtcod.map_is_in_fov(game.fov_map, x, y):
						if game.current_map.tile[x][y]['type'] == 'trap' and game.current_map.is_invisible(x, y):
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
	if name == 'ST':
		libtcod.console_set_default_foreground(con, libtcod.black)
	else:
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
	y = 0
	libtcod.console_clear(game.panel)
	for i in range(max(0, len(game.message.log) - 5 - game.old_msg), len(game.message.log) - game.old_msg):
		libtcod.console_set_default_foreground(game.panel, game.message.log[i][1])
		libtcod.console_print(game.panel, 0, y, game.message.log[i][0])
		y += 1
	if game.old_msg + 5 < len(game.message.log):
		libtcod.console_put_char_ex(game.panel, game.MESSAGE_WIDTH - 1, 0, chr(24), libtcod.white, libtcod.black)
	if game.old_msg > 0:
		libtcod.console_put_char_ex(game.panel, game.MESSAGE_WIDTH - 1, game.MESSAGE_HEIGHT - 1, chr(25), libtcod.white, libtcod.black)
	libtcod.console_blit(game.panel, 0, 0, game.MESSAGE_WIDTH, game.MESSAGE_HEIGHT, 0, game.MESSAGE_X, game.MESSAGE_Y)


# print the player stats in the panel
def render_player_stats_panel():
	libtcod.console_set_default_background(game.ps, libtcod.black)
	libtcod.console_clear(game.ps)
	libtcod.console_set_color_control(libtcod.COLCTRL_1, libtcod.green, libtcod.black)
	libtcod.console_set_color_control(libtcod.COLCTRL_2, libtcod.red, libtcod.black)
	render_bar(game.ps, 0, 6, game.PLAYER_STATS_WIDTH, 'HP', game.player.health, game.player.max_health, libtcod.red, libtcod.darker_red)
	render_bar(game.ps, 0, 7, game.PLAYER_STATS_WIDTH, 'ST', game.player.stamina, game.player.max_stamina, libtcod.yellow, libtcod.darker_yellow)
	render_bar(game.ps, 0, 8, game.PLAYER_STATS_WIDTH, 'MP', game.player.mana, game.player.max_mana, libtcod.blue, libtcod.darker_blue)
	libtcod.console_print(game.ps, 0, 0, game.player.name)
	libtcod.console_print(game.ps, 0, 1, 'Level ' + str(game.player.level))
	libtcod.console_print(game.ps, 0, 2, game.player.race + ' ' + game.player.profession)
	libtcod.console_print(game.ps, 0, 4, game.current_map.location_abbr + '-' + str(game.current_map.location_level) + '     ')
	libtcod.console_print(game.ps, 0, 10, 'XP: ' + str(game.player.xp))

	if game.player.strength > game.player.base_strength:
		libtcod.console_print(game.ps, 0, 11, 'Str: %c%i%c ' % (libtcod.COLCTRL_1, game.player.strength, libtcod.COLCTRL_STOP))
	elif game.player.strength < game.player.base_strength:
		libtcod.console_print(game.ps, 0, 11, 'Str: %c%i%c ' % (libtcod.COLCTRL_2, game.player.strength, libtcod.COLCTRL_STOP))
	else:
		libtcod.console_print(game.ps, 0, 11, 'Str: ' + str(game.player.strength) + ' ')

	if game.player.dexterity > game.player.base_dexterity:
		libtcod.console_print(game.ps, 0, 12, 'Dex: %c%i%c ' % (libtcod.COLCTRL_1, game.player.dexterity, libtcod.COLCTRL_STOP))
	elif game.player.dexterity < game.player.base_dexterity:
		libtcod.console_print(game.ps, 0, 12, 'Dex: %c%i%c ' % (libtcod.COLCTRL_2, game.player.dexterity, libtcod.COLCTRL_STOP))
	else:
		libtcod.console_print(game.ps, 0, 12, 'Dex: ' + str(game.player.dexterity) + ' ')

	if game.player.intelligence > game.player.base_intelligence:
		libtcod.console_print(game.ps, 0, 13, 'Int: %c%i%c ' % (libtcod.COLCTRL_1, game.player.intelligence, libtcod.COLCTRL_STOP))
	elif game.player.intelligence < game.player.base_intelligence:
		libtcod.console_print(game.ps, 0, 13, 'Int: %c%i%c ' % (libtcod.COLCTRL_2, game.player.intelligence, libtcod.COLCTRL_STOP))
	else:
		libtcod.console_print(game.ps, 0, 13, 'Int: ' + str(game.player.intelligence) + ' ')

	if game.player.wisdom > game.player.base_wisdom:
		libtcod.console_print(game.ps, 0, 14, 'Wis: %c%i%c ' % (libtcod.COLCTRL_1, game.player.wisdom, libtcod.COLCTRL_STOP))
	elif game.player.wisdom < game.player.base_wisdom:
		libtcod.console_print(game.ps, 0, 14, 'Wis: %c%i%c ' % (libtcod.COLCTRL_2, game.player.wisdom, libtcod.COLCTRL_STOP))
	else:
		libtcod.console_print(game.ps, 0, 14, 'Wis: ' + str(game.player.wisdom) + ' ')

	if game.player.endurance > game.player.base_endurance:
		libtcod.console_print(game.ps, 0, 15, 'End: %c%i%c ' % (libtcod.COLCTRL_1, game.player.endurance, libtcod.COLCTRL_STOP))
	elif game.player.endurance < game.player.base_endurance:
		libtcod.console_print(game.ps, 0, 15, 'End: %c%i%c ' % (libtcod.COLCTRL_2, game.player.endurance, libtcod.COLCTRL_STOP))
	else:
		libtcod.console_print(game.ps, 0, 15, 'End: ' + str(game.player.endurance) + ' ')

	libtcod.console_print(game.ps, 0, 16, 'Karma: ' + str(game.player.karma) + ' ')
	libtcod.console_print(game.ps, 0, game.PLAYER_STATS_HEIGHT - 2, 'Turns: ' + str(game.turns) + ' ')
	libtcod.console_print(game.ps, 0, 18, 'Active skills: ')
	libtcod.console_print(game.ps, 0, 21, 'Condition: ')
	libtcod.console_set_default_foreground(game.ps, libtcod.light_sepia)
	act_skill = ''
	if 'detect_trap' in game.player.flags:
		act_skill += 'DetTrap '
	if 'swimming' in game.player.flags:
		act_skill += 'Swimming '
	libtcod.console_print(game.ps, 0, 19, act_skill)

	cond = ''
	if 'stuck' in game.player.flags:
		cond += 'Stuck '
	if 'poison' in game.player.flags:
		cond += 'Poisoned '
	if 'sleep' in game.player.flags:
		cond += 'Sleep '
	if 'unconscious' in game.player.flags:
		cond += 'Unconscious '
	libtcod.console_print(game.ps, 0, 22, cond)
	libtcod.console_blit(game.ps, 0, 0, game.PLAYER_STATS_WIDTH, game.PLAYER_STATS_HEIGHT, 0, game.PLAYER_STATS_X, game.PLAYER_STATS_Y)


# floating text animations for damage and healing
# stuff to do: anim should start and end before next anim
def render_floating_text_animations():
	for i, (x, y, line, color, turn) in enumerate(reversed(game.hp_anim)):
		libtcod.console_set_default_foreground(0, libtcod.color_lerp(libtcod.black, color, 1 - ((turn / 15) * 0.2)))
		if game.MAP_Y + y - game.cury - (turn / 15) > 0:
			libtcod.console_print_ex(0, game.MAP_X + x - game.curx, game.MAP_Y + y - game.cury - (turn / 15), libtcod.BKGND_NONE, libtcod.CENTER, line)
		game.hp_anim[len(game.hp_anim) - i - 1] = (x, y, line, color, turn + 1)
		if turn > 60:
			game.hp_anim.pop(len(game.hp_anim) - i - 1)


# return new colors for tiles animations
def render_tiles_animations(x, y, icon, light, dark, lerp):
	if libtcod.random_get_int(game.rnd, 1, 70) == 70:
		if libtcod.random_get_int(game.rnd, 0, 1) == 0:
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


# master function of the game, everything pass through here on every turn
def render_map():
	# recompute FOV if needed (the player moved or something)
	libtcod.console_rect(0, game.MAP_X, game.MAP_Y, game.MAP_WIDTH, game.MAP_HEIGHT, True)
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
			if not libtcod.map_is_in_fov(game.fov_map, px, py):
				if game.draw_map and game.current_map.is_explored(px, py):
					if game.current_map.is_animate(px, py):
						libtcod.console_put_char_ex(game.con, x, y, game.current_map.tile[px][py]['icon'], game.current_map.tile[px][py]['dark_color'], game.current_map.tile[px][py]['dark_back_color'])
					else:
						libtcod.console_put_char_ex(game.con, x, y, game.current_map.tile[px][py]['icon'], game.current_map.tile[px][py]['dark_color'], game.current_map.tile[px][py]['back_dark_color'])
			else:
				if not game.fov_torch:
					if game.current_map.is_animate(px, py) or 'duration' in game.current_map.tile[px][py]:
						(front, back, game.current_map.tile[px][py]['lerp']) = render_tiles_animations(px, py, game.current_map.tile[px][py]['color'], game.current_map.tile[px][py]['back_light_color'], game.current_map.tile[px][py]['back_dark_color'], game.current_map.tile[px][py]['lerp'])
						libtcod.console_put_char_ex(game.con, x, y, game.current_map.tile[px][py]['icon'], front, back)
					elif game.draw_map:
						libtcod.console_put_char_ex(game.con, x, y, game.current_map.tile[px][py]['icon'], game.current_map.tile[px][py]['color'], game.current_map.tile[px][py]['back_light_color'])
				else:
					base = game.current_map.tile[px][py]['back_light_color']
					r = float(px - game.char.x + dx) * (px - game.char.x + dx) + (py - game.char.y + dy) * (py - game.char.y + dy)
					if r < game.SQUARED_TORCH_RADIUS:
						l = (game.SQUARED_TORCH_RADIUS - r) / game.SQUARED_TORCH_RADIUS + di
						if l < 0.0:
							l = 0.0
						elif l > 1.0:
							l = 1.0
						base = libtcod.color_lerp(base, libtcod.gold, l)
					libtcod.console_put_char_ex(game.con, x, y, game.current_map.tile[px][py]['icon'], game.current_map.tile[px][py]['color'], base)
				if not game.current_map.is_explored(px, py):
					game.current_map.tile[px][py].update({'explored': True})

	# draw all objects in the map (if in the map viewport), except the player who his drawn last
	for obj in reversed(game.current_map.objects):
		if obj.x in range(game.curx, game.curx + game.MAP_WIDTH) and obj.y in range(game.cury, game.cury + game.MAP_HEIGHT) and game.current_map.is_explored(obj.x, obj.y) and obj.name != 'player':
			if game.draw_map and obj.entity is not None:
				if libtcod.map_is_in_fov(game.fov_map, obj.x, obj.y) and not obj.entity.is_identified():
					skill = game.player.find_skill('Mythology')
					if (game.player.skills[skill].level * 0.8) + 20 >= roll_dice(1, 100):
						obj.entity.flags.append('identified')
						game.message.new('You properly identify the ' + obj.entity.unidentified_name + ' as ' + obj.entity.get_name(True), game.turns)
						game.player.skills[skill].gain_xp(3)
			if obj.entity is not None and not obj.entity.is_identified():
				obj.draw(game.con, libtcod.white)
			else:
				obj.draw(game.con)
	game.char.draw(game.con)
	libtcod.console_blit(game.con, 0, 0, game.MAP_WIDTH, game.MAP_HEIGHT, 0, game.MAP_X, game.MAP_Y)
	game.draw_map = False

	# draw a line between the player and the mouse cursor
	if game.path_dx in range(game.current_map.map_width) and game.path_dy in range(game.current_map.map_height):
		if game.current_map.is_explored(game.path_dx, game.path_dy) and not game.current_map.is_blocked(game.path_dx, game.path_dy):
			for i in range(libtcod.dijkstra_size(game.path_dijk)):
				x, y = libtcod.dijkstra_get(game.path_dijk, i)
				if (x - game.curx) in range(game.MAP_WIDTH) and (y - game.cury) in range(game.MAP_HEIGHT):
					libtcod.console_set_char_background(0, game.MAP_X + x - game.curx, game.MAP_Y + y - game.cury, libtcod.desaturated_yellow, libtcod.BKGND_SET)

	# move the player if using mouse
	if game.mouse_move:
		if mouse_auto_move() and not libtcod.dijkstra_is_empty(game.path_dijk):
			game.char.x, game.char.y = libtcod.dijkstra_path_walk(game.path_dijk)
			game.fov_recompute = True
			add_turn()
		else:
			items_at_feet()
			game.mouse_move = False

	# check where is the mouse cursor if not in the act of moving while using the mouse
	if not game.mouse_move:
		(mx, my) = (game.mouse.cx - game.MAP_X, game.mouse.cy - 1)
		px = mx + game.curx
		py = my + game.cury
		game.path_dx = -1
		game.path_dy = -1
		if mx in range(game.MAP_WIDTH) and my in range(game.MAP_HEIGHT):
			libtcod.console_set_char_background(0, mx + game.MAP_X, my + 1, libtcod.white, libtcod.BKGND_SET)
			if game.current_map.is_explored(px, py) and not game.current_map.is_blocked(px, py):
				game.path_dx = px
				game.path_dy = py
				if game.mouse.lbutton_pressed:
					game.mouse_move = mouse_auto_move()
				if not game.current_map.is_blocked(game.path_dx, game.path_dy):
					libtcod.dijkstra_path_set(game.path_dijk, game.path_dx, game.path_dy)

	libtcod.console_set_default_foreground(0, libtcod.light_yellow)
	libtcod.console_print_rect(0, game.MAP_X, game.MAP_Y, game.MAP_WIDTH - 18, game.MAP_HEIGHT, get_names_under_mouse())
	if game.debug.enable:
		libtcod.console_print_ex(0, game.MAP_X + game.MAP_WIDTH - 1, game.MAP_Y, libtcod.BKGND_NONE, libtcod.RIGHT, str(game.gametime.hour) + ':' + str(game.gametime.minute).rjust(2, '0') + ' (%3d fps)' % libtcod.sys_get_fps())
	render_floating_text_animations()
