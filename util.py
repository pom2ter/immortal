import libtcodpy as libtcod
import math
import game
import IO
import commands
import mapgen
import effects


#########################################
# miscellanous functions
#########################################

# add a turn and do checks for statuses and stuffies
def add_turn():
	game.turns += 1
	game.gametime.update(1)
	game.draw_gui = True
	game.draw_map = True
	libtcod.console_clear(game.con)

	game.player.item_expiration()
	game.player.item_is_active()
	game.player.check_condition()
	game.player.check_burdened_status()
	game.fov_torch = any('torchlight' in x.flags and x.active for x in game.player.inventory)

	nb = 50
	if 'hungry' in game.player.flags:
		nb = 75
	if 'famished' in game.player.flags:
		nb = 100
	if 'starving' in game.player.flags:
		if game.turns % 9 == 0 and not game.player.is_disabled():
			game.player.take_damage(1, 'starvation')
	if game.turns % (nb - game.player.endurance) == 0:
		game.player.heal_health(1)
	if game.turns % (50 - game.player.intelligence) == 0:
		game.player.heal_mana(1)

	if 'detect_trap' in game.player.flags:
		game.gametime.update(1)
		skill = game.player.find_skill('Detect Traps')
		if game.player.skills[skill].level >= libtcod.random_get_int(game.rnd, 0, 200):
			if game.traps:
				dice = libtcod.random_get_int(game.rnd, 0, len(game.traps) - 1)
				for i, (x, y) in enumerate(game.traps):
					if i == dice:
						game.current_map.set_tile_values(game.current_map.tile[x][y]['name'], x, y)
						if game.current_map.tile_is_invisible(x, y):
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
	lerp = 1.0
	descending = True
	current = 0

	fonts = sorted(game.fonts, reverse=True)
	font = 0
	if game.setting_font == 'large':
		font = 2
	elif game.setting_font == 'medium':
		font = 1
	history = game.setting_history
	fullscreen = ['on', 'off']
	fs = 0
	if game.setting_fullscreen == 'off':
		fs = 1

	key = libtcod.Key()
	libtcod.console_print_rect(box, 2, 2, width - 4, 2, '(You may need to restart the game for the changes to take effect)')
	libtcod.console_print(box, 2, 5, 'Font size: ')
	libtcod.console_print(box, 2, 6, 'Message history size: ')
	libtcod.console_print(box, 2, 7, 'Fullscreen: ')
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

		# message history size setting
		if current == 1:
			libtcod.console_set_default_foreground(box, libtcod.white)
			libtcod.console_set_default_background(box, color)
		else:
			libtcod.console_set_default_foreground(box, libtcod.grey)
			libtcod.console_set_default_background(box, libtcod.black)
		libtcod.console_rect(box, 26, 6, 13, 1, True, libtcod.BKGND_SET)
		libtcod.console_print_ex(box, 32, 6, libtcod.BKGND_SET, libtcod.CENTER, str(history))

		# full screen mode
		if current == 2:
			libtcod.console_set_default_foreground(box, libtcod.white)
			libtcod.console_set_default_background(box, color)
		else:
			libtcod.console_set_default_foreground(box, libtcod.grey)
			libtcod.console_set_default_background(box, libtcod.black)
		libtcod.console_rect(box, 26, 7, 13, 1, True, libtcod.BKGND_SET)
		libtcod.console_print_ex(box, 32, 7, libtcod.BKGND_SET, libtcod.CENTER, fullscreen[fs].capitalize())

		for i in range(5, 8):
			libtcod.console_set_default_foreground(box, libtcod.white)
			libtcod.console_print_ex(box, 25, i, libtcod.BKGND_NONE, libtcod.LEFT, chr(27))
			libtcod.console_print_ex(box, 39, i, libtcod.BKGND_NONE, libtcod.LEFT, chr(26))

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
				font -= 1
				if font == -1:
					font = len(fonts) - 1
			if current == 1:
				history -= 50
				if history == 0:
					history = 1000
			if current == 2:
				if fs == 0:
					fs = 1
				else:
					fs = 0
		elif key.vk == libtcod.KEY_RIGHT:
			if current == 0:
				font += 1
				if font == len(fonts):
					font = 0
			if current == 1:
				history += 50
				if history > 1000:
					history = 50
			if current == 2:
				if fs == 0:
					fs = 1
				else:
					fs = 0
		elif key.vk == libtcod.KEY_UP:
			current -= 1
			if current == -1:
				current = 2
		elif key.vk == libtcod.KEY_DOWN:
			current += 1
			if current == 3:
				current = 0
		elif key.vk == libtcod.KEY_ESCAPE:
			cancel = True
		elif key.vk == libtcod.KEY_ENTER:
			confirm = True

	if confirm:
		game.setting_history = history
		game.setting_fullscreen = fullscreen[fs]
		if game.setting_fullscreen == 'on':
			libtcod.console_set_fullscreen(True)
		else:
			libtcod.console_set_fullscreen(False)
		if blitmap:
			game.message.trim_history()
		IO.save_settings(fonts[font], str(history), fullscreen[fs])


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


# returns currency in gold, silver and copper
def convert_coins(coins):
	return coins / 10000, (coins / 100) % 100, coins % 100


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


# find terrain type base on elevation
def find_terrain_type(coord):
	terrain = 'Forest'
	heightmap = game.worldmap.hm_list[coord]
	for key, value in game.terrain.items():
		if value['elevation'] <= heightmap <= value['maxelev']:
			terrain = key
			break
	return terrain


# return a string with the names of all objects under the mouse
def get_names_under_mouse():
	(x, y) = (game.mouse.cx - game.MAP_X, game.mouse.cy - 1)
	px = x + game.curx
	py = y + game.cury
	if y in range(game.MAP_HEIGHT) and x in range(game.MAP_WIDTH) and game.current_map.tile_is_explored(px, py):
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
			if game.current_map.tile_is_invisible(px, py):
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
		else:
			game.message.new('You see ' + objects[0].item.get_name(True) + '.', game.turns)


# print loading maps message
def loadgen_message():
	libtcod.console_print(0, game.MAP_X, game.MAP_Y, 'Loading/Generating map chunks...')
	libtcod.console_flush()


# auto attack with mouse
def mouse_auto_attack(x, y, target):
	if abs(x - game.char.x) > 1 or abs(y - game.char.y) > 1:
		if (abs(x - game.char.x) == 2 and abs(y - game.char.y) <= 2) or (abs(y - game.char.y) == 2 and abs(x - game.char.x) <= 2) and game.player.skills[game.player.find_weapon_type()].name == 'Polearm':
			game.player.attack(target)
		elif game.player.skills[game.player.find_weapon_type()].name in ['Bow', 'Missile']:
			game.player.attack(target, True)
		else:
			game.message.new('Target is out of range.', game.turns)
	else:
		game.player.attack(target)


# check to see if you can auto-move with mouse
def mouse_auto_move():
	for obj in game.current_map.objects:
		if libtcod.map_is_in_fov(game.fov_map, obj.x, obj.y) and obj.entity is not None:
			game.message.new('Auto-move aborted: Monster is near.', game.turns)
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
def set_full_explore_map(map, dijkstra=True):
	set_map = libtcod.map_new(map.map_width, map.map_height)
	for py in range(map.map_height):
		for px in range(map.map_width):
			libtcod.map_set_properties(set_map, px, py, not map.tile_is_sight_blocked(px, py), not map.tile_is_blocked(px, py))
	if dijkstra:
		path = libtcod.dijkstra_new(set_map)
	else:
		path = libtcod.path_new_using_map(set_map)
	return path


# scrollbar management
def scrollbar(con, x, y, start, size, length, reverse=False):
	fore1 = libtcod.darkest_grey
	fore2 = libtcod.darkest_grey
	if reverse:
		if start > 0:
			fore2 = libtcod.white
		if start + size < length:
			fore1 = libtcod.white
	else:
		if start > 0:
			fore1 = libtcod.white
		if start + size < length:
			fore2 = libtcod.white
	libtcod.console_put_char_ex(con, x, y, chr(24), fore1, libtcod.black)
	libtcod.console_put_char_ex(con, x, y + size - 1, chr(25), fore2, libtcod.black)
	for i in range(size - 2):
		libtcod.console_put_char_ex(con, x, y + i + 1, chr(179), libtcod.darkest_grey, libtcod.black)
	if length - size > 0:
		step = float(size - 2) / float(length - size)
		bar = int(math.ceil(start * step))
		if bar < 1 and start == 0:
			bar = 1
		if bar > size - 2 and start + size == length:
			bar = size - 2
		if reverse:
			libtcod.console_put_char_ex(con, x, y + (size - 1) - bar, chr(179), libtcod.white, libtcod.black)
		else:
			libtcod.console_put_char_ex(con, x, y + bar, chr(179), libtcod.white, libtcod.black)


# show the worldmap
# stuff to do: add towns
def showmap(box):
	lerp, choice = 1.0, -1
	descending, keypress = True, False
	choice, zoom = False, False
	key = libtcod.Key()
	startx = game.worldmap.player_positionx - (game.SCREEN_WIDTH / 2)
	starty = game.worldmap.player_positiony - (game.SCREEN_HEIGHT / 2)
	if startx < 0:
		startx = 0
	if startx > game.WORLDMAP_WIDTH - game.SCREEN_WIDTH + 2:
		startx = game.WORLDMAP_WIDTH - game.SCREEN_WIDTH + 2
	if starty < 0:
		starty = 0
	if starty > game.WORLDMAP_HEIGHT - game.SCREEN_HEIGHT + 2:
		starty = game.WORLDMAP_HEIGHT - game.SCREEN_HEIGHT + 2

	while not choice:
		ev = libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, libtcod.Mouse())
		if not zoom:
			libtcod.image_blit_2x(game.worldmap.map_image_small, box, 1, 1)
			mapposx = game.worldmap.player_positionx * (float(game.SCREEN_WIDTH - 2) / float(game.WORLDMAP_WIDTH))
			mapposy = game.worldmap.player_positiony * (float(game.SCREEN_HEIGHT - 2) / float(game.WORLDMAP_HEIGHT))
			char = find_map_position(mapposx, mapposy)
			libtcod.console_set_default_foreground(box, libtcod.black)
			for (id, name, abbr, x, y, tlevel, dtype) in game.worldmap.dungeons:
				dmapposx = x * (float(game.SCREEN_WIDTH - 2) / float(game.WORLDMAP_WIDTH))
				dmapposy = y * (float(game.SCREEN_HEIGHT - 2) / float(game.WORLDMAP_HEIGHT))
				dchar = find_map_position(dmapposx, dmapposy)
				libtcod.console_print_ex(box, int(dmapposx) + 1, int(dmapposy) + 1, libtcod.BKGND_NONE, libtcod.LEFT, dchar)

		if zoom:
			libtcod.console_blit(game.wm, startx, starty, game.SCREEN_WIDTH - 2, game.SCREEN_HEIGHT - 2, box, 1, 1, 1.0, 1.0)
			libtcod.console_set_default_foreground(box, libtcod.black)
			for (id, name, abbr, x, y, tlevel, dtype) in game.worldmap.dungeons:
				if y in range(starty, starty + game.SCREEN_HEIGHT - 2) and x in range(startx, startx + game.SCREEN_WIDTH - 2):
					libtcod.console_print_ex(box, x - startx + 1, y - starty + 1, libtcod.BKGND_NONE, libtcod.LEFT, chr(23))

		color, lerp, descending = color_lerp(lerp, descending, light=libtcod.red)
		libtcod.console_set_default_foreground(box, color)
		if not zoom:
			libtcod.console_print_ex(box, int(mapposx) + 1, int(mapposy) + 1, libtcod.BKGND_NONE, libtcod.LEFT, char)
		if zoom and game.worldmap.player_positiony in range(starty, starty + game.SCREEN_HEIGHT - 2) and game.worldmap.player_positionx in range(startx, startx + game.SCREEN_WIDTH - 2):
			libtcod.console_print_ex(box, game.worldmap.player_positionx - startx + 1, game.worldmap.player_positiony - starty + 1, libtcod.BKGND_NONE, libtcod.LEFT, '@')
		libtcod.console_blit(box, 0, 0, game.SCREEN_WIDTH, game.SCREEN_HEIGHT, 0, 0, 0, 1.0, 1.0)
		libtcod.console_flush()

		if ev == libtcod.EVENT_KEY_PRESS:
			key_char = chr(key.c)
			if key_char == 's':
				libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, game.SCREEN_HEIGHT / 2, libtcod.BKGND_DARKEN, libtcod.CENTER, ' Saving map... ')
				libtcod.console_flush()
				game.worldmap.create_map_images(2)
			elif key_char == 'z':
				zoom = not zoom
			elif key.vk == libtcod.KEY_UP and zoom:
				if starty > 0:
					starty -= 1
			elif key.vk == libtcod.KEY_DOWN and zoom:
				if starty < game.WORLDMAP_HEIGHT - game.SCREEN_HEIGHT + 2:
					starty += 1
			elif key.vk == libtcod.KEY_LEFT and zoom:
				if startx > 0:
					startx -= 1
			elif key.vk == libtcod.KEY_RIGHT and zoom:
				if startx < game.WORLDMAP_WIDTH - game.SCREEN_WIDTH + 2:
					startx += 1
			elif (key.vk == libtcod.KEY_TAB or key.vk == libtcod.KEY_ESCAPE) and ev == libtcod.EVENT_KEY_PRESS:
				choice = True


# someone set off a trap :O
def trigger_trap(x, y, victim='You', chest=False):
	flags = game.current_map.tile[x][y]
	if not chest:
		explored = game.current_map.tile_is_explored(x, y)
		game.current_map.set_tile_values(game.current_map.tile[x][y]['name'], x, y)
		if game.current_map.tile_is_invisible(x, y):
			game.current_map.tile[x][y].pop('invisible', None)
		if explored:
			game.current_map.tile[x][y].update({'explored': True})
	else:
		x = game.char.x
		y = game.char.y

	if libtcod.map_is_in_fov(game.fov_map, x, y):
		game.message.new(victim + ' triggered a trap!', game.turns)
	if 'fx_teleport' in flags:
		effects.teleportation(x, y, victim)
	if 'fx_stuck' in flags:
		effects.stuck(x, y, victim)
	if 'fx_poison_gas' in flags:
		effects.poison_gas(x, y, 3, 20)
	if 'fx_sleep_gas' in flags:
		effects.sleeping_gas(x, y, 3, 20)
	if 'fx_fireball' in flags:
		effects.fireball(x, y, 3)
	if 'fx_arrow' in flags:
		direction = libtcod.random_get_int(game.rnd, 0, 3)
		sx, sy = x - 2, y
		if direction == 1:
			sx, sy = x, y - 2
		if direction == 2:
			sx, sy = x + 2, y
		if direction == 3:
			sx, sy = x, y + 2
		effects.missile_attack(sx, sy, x, y, True)
	if 'fx_needle' in flags:
		effects.poison_needle(x, y)


#########################################
# map utils functions
#########################################

# main functions for building the overworld maps
def change_maps(level):
	loadgen_message()
	decombine_maps()
	store_map(game.current_map)
	for i in range(len(game.border_maps)):
		store_map(game.border_maps[i])
	IO.autosave()
	game.current_map = fetch_map({'name': game.current_map.location_name, 'id': game.current_map.location_id, 'abbr': game.current_map.location_abbr, 'level': level, 'map_width': game.current_map.map_width, 'map_height': game.current_map.map_height})
	fetch_border_maps()
	IO.autosave_current_map()
	combine_maps()
	initialize_fov()
	game.fov_recompute = True


# combine some overworld maps into a super map
def combine_maps():
	mapid = [[0, 1, 2], [3, 0, 4], [5, 6, 7]]
	super_map = mapgen.Map(game.current_map.location_name, game.current_map.location_abbr, game.current_map.location_id, game.current_map.location_level, game.current_map.threat_level, game.current_map.map_width * 3, game.current_map.map_height * 3, game.current_map.type, True)
	game.char.x += game.current_map.map_width
	game.char.y += game.current_map.map_height
	super_map.objects.append(game.char)
	for i in range(3):
		for j in range(3):
			if i == 1 and j == 1:
				current = game.current_map
			else:
				current = game.border_maps[mapid[i][j]]
			for x in range(game.current_map.map_width):
				for y in range(game.current_map.map_height):
					super_map.tile[x + (j * game.current_map.map_width)][y + (i * game.current_map.map_height)] = current.tile[x][y]
			for obj in current.objects:
				if obj.name != 'player':
					obj.x = obj.x + (j * game.current_map.map_width)
					obj.y = obj.y + (i * game.current_map.map_height)
					super_map.objects.append(obj)
	game.current_backup = game.current_map
	game.current_map = super_map


# decombine the super map into their respective smaller chunks
def decombine_maps():
	mapid = [[0, 1, 2], [3, 0, 4], [5, 6, 7]]
	super_map = game.current_map
	for i in range(3):
		for j in range(3):
			if i == 1 and j == 1:
				current = game.current_backup
			else:
				current = game.border_maps[mapid[i][j]]
			for x in range(current.map_width):
				for y in range(current.map_height):
					current.tile[x][y] = super_map.tile[x + (j * current.map_width)][y + (i * current.map_height)]
			current.objects = []
			current.objects.append(game.char)
			for obj in super_map.objects:
				if obj.x / (super_map.map_width / 3) == j and obj.y / (super_map.map_height / 3) == i and obj.name != 'player':
					obj.x = obj.x - (j * (super_map.map_width / 3))
					obj.y = obj.y - (i * (super_map.map_height / 3))
					current.objects.append(obj)
			if i == 1 and j == 1:
				game.current_map = current
			else:
				game.border_maps[mapid[i][j]] = current
	if game.char.x >= game.current_map.map_width * 2:
		game.char.x -= game.current_map.map_width * 2
	elif game.char.x >= game.current_map.map_width:
		game.char.x -= game.current_map.map_width
	if game.char.y >= game.current_map.map_height * 2:
		game.char.y -= game.current_map.map_height * 2
	elif game.char.y >= game.current_map.map_height:
		game.char.y -= game.current_map.map_height


# fetch border maps when in the overworld
def fetch_border_maps():
	level = game.current_map.location_level
	coord = [level - game.WORLDMAP_WIDTH - 1, level - game.WORLDMAP_WIDTH, level - game.WORLDMAP_WIDTH + 1, level - 1, level + 1, level + game.WORLDMAP_WIDTH - 1, level + game.WORLDMAP_WIDTH, level + game.WORLDMAP_WIDTH + 1]
	for i in range(len(coord)):
		if i in [0, 3, 5]:
			if coord[i] % game.WORLDMAP_WIDTH == game.WORLDMAP_WIDTH - 1:
				coord[i] = coord[i] + game.WORLDMAP_WIDTH
		if i in [2, 4, 7]:
			if coord[i] % game.WORLDMAP_WIDTH == 0:
				coord[i] = coord[i] - game.WORLDMAP_WIDTH
		if coord[i] not in range(game.WORLDMAP_WIDTH * game.WORLDMAP_HEIGHT):
			coord[i] = abs((game.WORLDMAP_WIDTH * game.WORLDMAP_HEIGHT) - abs(coord[i]))
		game.border_maps[i] = fetch_map({'name': game.current_map.location_name, 'id': game.current_map.location_id, 'abbr': game.current_map.location_abbr, 'level': coord[i], 'map_width': game.current_map.map_width, 'map_height': game.current_map.map_height})


# check to see if destination map already exist, if so fetch it, if not generate it
def fetch_map(data, dir='up'):
	generate = True
	for i in xrange(len(game.old_maps)):
		if game.old_maps[i].location_id == data['id'] and game.old_maps[i].location_level == data['level']:
			temp_map = game.old_maps[i]
			if temp_map.location_id > 0:
				if dir == 'up':
					(game.char.x, game.char.y) = temp_map.up_staircase
				else:
					(game.char.x, game.char.y) = temp_map.down_staircase
			generate = False
			break
	if generate:
		if data['id'] == 0:
			temp_map = mapgen.Map(data['name'], data['abbr'], data['id'], data['level'], game.worldmap.set_threat_level(data['level'] % game.WORLDMAP_WIDTH, data['level'] / game.WORLDMAP_WIDTH), data['map_width'], data['map_height'], find_terrain_type(data['level']))
		else:
			temp_map = mapgen.Map(data['name'], data['abbr'], data['id'], data['level'], data['threat'], data['map_width'], data['map_height'], data['type'])
	return temp_map


# store old map on map change
def store_map(data):
	add = True
	for i in xrange(len(game.old_maps)):
		if game.old_maps[i].location_id == data.location_id and game.old_maps[i].location_level == data.location_level:
			game.old_maps[i] = data
			add = False
			break
	if add:
		game.old_maps.append(data)


#########################################
# main screen functions
#########################################

def path_func(xFrom, yFrom, xTo, yTo, user_data):
	if 'explored' in game.current_map.tile[xTo][yTo] and not 'blocked' in game.current_map.tile[xTo][yTo]:
		return 1.0
	return 0.0


# initialize the field of vision
def initialize_fov(update=False):
#	print 'Loading/Generating map chunks...'
#	t0 = libtcod.sys_elapsed_seconds()
	game.traps = []
	if not update:
		game.fov_map = libtcod.map_new(game.current_map.map_width, game.current_map.map_height)
		for y in range(game.current_map.map_height):
			for x in range(game.current_map.map_width):
				libtcod.map_set_properties(game.fov_map, x, y, not 'block_sight' in game.current_map.tile[x][y], 'explored' in game.current_map.tile[x][y] and not 'blocked' in game.current_map.tile[x][y])
	else:
		for y in range(game.char.y - game.FOV_RADIUS, game.char.y + game.FOV_RADIUS):
			for x in range(game.char.x - game.FOV_RADIUS, game.char.x + game.FOV_RADIUS):
				if y < game.current_map.map_height and x < game.current_map.map_width:
					libtcod.map_set_properties(game.fov_map, x, y, not 'block_sight' in game.current_map.tile[x][y], 'explored' in game.current_map.tile[x][y] and not 'blocked' in game.current_map.tile[x][y])
					if 'invisible' in game.current_map.tile[x][y] and game.current_map.tile[x][y]['type'] == 'trap' and libtcod.map_is_in_fov(game.fov_map, x, y):
						game.traps.append((x, y))
	# compute paths using a*star algorithm
	game.path = libtcod.path_new_using_function(game.current_map.map_width, game.current_map.map_height, path_func)
	libtcod.path_compute(game.path, game.char.x, game.char.y, game.path_dx, game.path_dy)
#	t1 = libtcod.sys_elapsed_seconds()
#	print '    done (%.3f seconds)' % (t1 - t0)


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
	for i in range(max(0, len(game.message.log) - game.MESSAGE_HEIGHT - game.old_msg), len(game.message.log) - game.old_msg):
		libtcod.console_set_default_foreground(game.panel, game.message.log[i][1])
		libtcod.console_print(game.panel, 0, y, game.message.log[i][0])
		y += 1
	scrollbar(game.panel, game.MESSAGE_WIDTH - 1, 0, game.old_msg, game.MESSAGE_HEIGHT, len(game.message.log), True)
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
	libtcod.console_print(game.ps, 0, 1, game.player.race + ' ' + game.player.profession)
	libtcod.console_print(game.ps, 0, 2, 'Level ' + str(game.player.level))
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
	libtcod.console_print(game.ps, 0, 18, 'Hunger level: ')
	libtcod.console_print(game.ps, 0, 21, 'Active skills: ')
	libtcod.console_print(game.ps, 0, 24, 'Condition: ')
	libtcod.console_set_default_foreground(game.ps, libtcod.light_sepia)

	for flags in game.player.flags:
		if flags in ['hungry', 'famished', 'starving', 'bloated', 'full', 'normal']:
			libtcod.console_print(game.ps, 0, 19, '%c%c%c%c%s%c' % (libtcod.COLCTRL_FORE_RGB, 115, 255, 115, flags.capitalize(), libtcod.COLCTRL_STOP))

	act_skill = ''
	if 'detect_trap' in game.player.flags:
		act_skill += 'DetectTrap '
	if 'swimming' in game.player.flags:
		act_skill += 'Swimming '
	libtcod.console_print(game.ps, 0, 22, act_skill)

	cond = ''
	for flags in game.player.flags:
		if flags in ['stuck', 'poison', 'sleep', 'unconscious', 'burdened', 'strained', 'overburdened']:
			cond += flags.capitalize() + ' '
	libtcod.console_print(game.ps, 0, 25, cond)
	libtcod.console_blit(game.ps, 0, 0, game.PLAYER_STATS_WIDTH, game.PLAYER_STATS_HEIGHT, 0, game.PLAYER_STATS_X, game.PLAYER_STATS_Y)


# floating text animations for damage and healing
def render_floating_text_animations():
	fps = 8
	try:
		for i, value in enumerate(reversed(game.hp_anim)):
			if game.MAP_Y + value['y'] - game.cury - (value['turns'] / fps) > 0:
				libtcod.console_set_default_foreground(0, libtcod.color_lerp(libtcod.black, value['color'], 1 - ((value['turns'] / fps) * 0.2)))
				if 'player' in value:
					libtcod.console_print_ex(0, game.MAP_X + game.char.x - game.curx, game.MAP_Y + game.char.y - game.cury - (value['turns'] / fps), libtcod.BKGND_NONE, libtcod.CENTER, value['damage'])
				else:
					libtcod.console_print_ex(0, game.MAP_X + value['x'] - game.curx, game.MAP_Y + value['y'] - game.cury - (value['turns'] / fps), libtcod.BKGND_NONE, libtcod.CENTER, value['damage'])
				if value['turns'] <= fps * 1.5:
					libtcod.console_set_default_foreground(0, value['icon_color'])
					if 'player' in value:
						libtcod.console_print_ex(0, game.MAP_X + game.char.x - game.curx, game.MAP_Y + game.char.y - game.cury, libtcod.BKGND_NONE, libtcod.CENTER, value['icon'])
					else:
						libtcod.console_print_ex(0, game.MAP_X + value['x'] - game.curx, game.MAP_Y + value['y'] - game.cury, libtcod.BKGND_NONE, libtcod.CENTER, value['icon'])
			value.update({'turns': value['turns'] + 1})
			if value['turns'] > fps * 4:
				game.hp_anim.pop(len(game.hp_anim) - i - 1)
	except IndexError:
		print "Error in render floating text animations function"
		print game.hp_anim


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
	if game.gametime.hour < 6 or game.gametime.hour >= 21 or game.current_map.location_id != 0:
		game.FOV_RADIUS = 3
	if game.fov_torch and game.FOV_RADIUS < game.TORCH_RADIUS:
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
				if game.draw_map and game.current_map.tile_is_explored(px, py):
					if game.current_map.tile_is_animated(px, py):
						libtcod.console_put_char_ex(game.con, x, y, game.current_map.tile[px][py]['icon'], game.current_map.tile[px][py]['dark_color'], game.current_map.tile[px][py]['dark_back_color'])
					else:
						libtcod.console_put_char_ex(game.con, x, y, game.current_map.tile[px][py]['icon'], game.current_map.tile[px][py]['dark_color'], game.current_map.tile[px][py]['back_dark_color'])
			else:
				if not game.fov_torch:
					if 'animate' in game.current_map.tile[px][py] or 'duration' in game.current_map.tile[px][py]:
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
				if not game.current_map.tile_is_explored(px, py):
					game.current_map.tile[px][py].update({'explored': True})

	# draw all objects in the map (if in the map viewport), except the player who his drawn last
	for obj in reversed(game.current_map.objects):
		if obj.y in range(game.cury, game.cury + game.MAP_HEIGHT) and obj.x in range(game.curx, game.curx + game.MAP_WIDTH) and game.current_map.tile_is_explored(obj.x, obj.y) and obj.name != 'player':
			if game.draw_map and obj.entity is not None:
				if libtcod.map_is_in_fov(game.fov_map, obj.x, obj.y) and not obj.entity.is_identified():
					skill = game.player.find_skill('Mythology')
					if (game.player.skills[skill].level * 0.8) + 20 >= roll_dice(1, 100):
						obj.entity.flags.append('identified')
						game.message.new('You properly identify the ' + obj.entity.unidentified_name + ' as ' + obj.entity.get_name(True) + '.', game.turns)
						game.player.skills[skill].gain_xp(3)
			if obj.entity is not None and not obj.entity.is_identified():
				obj.draw(game.con, libtcod.white)
			else:
				obj.draw(game.con)
	game.char.draw(game.con)
	libtcod.console_blit(game.con, 0, 0, game.MAP_WIDTH, game.MAP_HEIGHT, 0, game.MAP_X, game.MAP_Y)
	game.draw_map = False

	# move the player if using mouse
	if game.mouse_move:
		if mouse_auto_move() and not libtcod.path_is_empty(game.path):
			game.char.x, game.char.y = libtcod.path_walk(game.path, True)
			game.fov_recompute = True
			game.player_move = True
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
		if my in range(game.MAP_HEIGHT) and mx in range(game.MAP_WIDTH):
			libtcod.console_set_char_background(0, mx + game.MAP_X, my + 1, libtcod.white, libtcod.BKGND_SET)
			if game.current_map.tile_is_explored(px, py) and not game.current_map.tile_is_blocked(px, py):
				game.path_dx = px
				game.path_dy = py
				if game.mouse.lbutton_pressed:
					target = [obj for obj in game.current_map.objects if obj.y == py and obj.x == px and obj.entity]
					if target:
						mouse_auto_attack(px, py, target[0])
					else:
						game.mouse_move = mouse_auto_move()
				# draw a line between the player and the mouse cursor
				if not game.current_map.tile_is_blocked(game.path_dx, game.path_dy):
					libtcod.path_compute(game.path, game.char.x, game.char.y, game.path_dx, game.path_dy)
					for i in range(libtcod.path_size(game.path)):
						x, y = libtcod.path_get(game.path, i)
						if (y - game.cury) in range(game.MAP_HEIGHT) and (x - game.curx) in range(game.MAP_WIDTH):
							libtcod.console_set_char_background(0, game.MAP_X + x - game.curx, game.MAP_Y + y - game.cury, libtcod.desaturated_yellow, libtcod.BKGND_SET)

	libtcod.console_set_default_foreground(0, libtcod.light_yellow)
	libtcod.console_print_rect(0, game.MAP_X, game.MAP_Y, game.MAP_WIDTH - 18, game.MAP_HEIGHT, get_names_under_mouse())
	if game.debug.enable:
		libtcod.console_print_ex(0, game.MAP_X + game.MAP_WIDTH - 1, game.MAP_Y, libtcod.BKGND_NONE, libtcod.RIGHT, str(game.gametime.hour) + ':' + str(game.gametime.minute).rjust(2, '0') + ' (%3d fps)' % libtcod.sys_get_fps())
	if game.hp_anim:
		render_floating_text_animations()
