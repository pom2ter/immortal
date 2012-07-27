import libtcodpy as libtcod
import game


def choices(con, width, height, options, typ, posx=0, posy=0, default=0):
	choice = False
	current, up, down = default, 0, height
	max_width = posx + width + posx
	max_height = posy + height + posy
	key = libtcod.Key()
	mouse = libtcod.Mouse()

	while not choice and choice != -1:
		ev = libtcod.sys_check_for_event(libtcod.EVENT_ANY, key, mouse)
		libtcod.console_set_default_foreground(con, libtcod.grey)
		libtcod.console_set_default_background(con, libtcod.black)
		libtcod.console_rect(con, 1, 1, max_width - 2, max_height - 2, True, libtcod.BKGND_SET)
		if up != 0:
			libtcod.console_print_ex(con, max_width - 2, 1, libtcod.BKGND_SET, libtcod.LEFT, chr(136))
			libtcod.console_print_ex(con, 1, 1, libtcod.BKGND_SET, libtcod.LEFT, chr(136))
		if down < len(options):
			libtcod.console_print_ex(con, max_width - 2, max_height - 2, libtcod.BKGND_SET, libtcod.LEFT, chr(142))
			libtcod.console_print_ex(con, 1, max_height - 2, libtcod.BKGND_SET, libtcod.LEFT, chr(142))
		for y in range(up, down):
			if y < len(options):
				if y == current:
					libtcod.console_set_default_foreground(con, libtcod.white)
					libtcod.console_set_default_background(con, libtcod.light_blue)
				else:
					libtcod.console_set_default_foreground(con, libtcod.grey)
					libtcod.console_set_default_background(con, libtcod.black)
				if typ == 'inventory':
					textl = options[y].unidentified_name
					textr = str(options[y].weight) + ' lbs'
				else:
					textl = options[y]
					textr = ''
				libtcod.console_rect(con, posx, (y - up) + posy, width, 1, True, libtcod.BKGND_SET)
				libtcod.console_print_ex(con, posx + 1, (y - up) + posy, libtcod.BKGND_SET, libtcod.LEFT, textl)
				libtcod.console_print_ex(con, width, (y - up) + posy, libtcod.BKGND_SET, libtcod.RIGHT, textr)

		x = (game.SCREEN_WIDTH - max_width) / 2
		y = (game.SCREEN_HEIGHT - max_height) / 2
		libtcod.console_blit(con, 0, 0, max_width, max_height, 0, x, y, 1.0, 0.8)
		libtcod.console_flush()

		(mx, my) = (mouse.cx, mouse.cy)
		if my in range(y + posy, y + height + posy) and mx in range(x + posx, x + width + posx):
			current = my - (y + posy) + up
			if current > len(options) - 1:
				current = len(options) - 1

		if key.vk == libtcod.KEY_DOWN and ev == libtcod.EVENT_KEY_PRESS:
			current = (current + 1) % len(options)
			if current == down:
				down += 1
				up += 1
			if current == 0:
				down = height
				up = 0
		elif key.vk == libtcod.KEY_UP and ev == libtcod.EVENT_KEY_PRESS:
			current = (current - 1) % len(options)
			if current < up:
				up -= 1
				down -= 1
			if current == len(options) - 1:
				if current > height - 1:
					up = len(options) - height
					down = len(options)
		elif key.vk == libtcod.KEY_ESCAPE and ev == libtcod.EVENT_KEY_PRESS:
			current = -1
			choice = -1
		elif (key.vk == libtcod.KEY_ENTER and ev == libtcod.EVENT_KEY_PRESS) or (mouse.lbutton_pressed and my in range(y + posy, y + height + posy) and mx in range(x + posx, x + width + posx) and (my - (y + posy) + up) <= len(options) - 1):
			choice = True
	return current


def msg_box(typ, header=None, footer=None, contents=None, box_width=60, box_height=5, center=False, default=0):
	width = box_width
	height = box_height
	box = libtcod.console_new(width, height)
	libtcod.console_set_default_foreground(box, libtcod.white)
	libtcod.console_set_default_background(box, libtcod.black)
	libtcod.console_print_frame(box, 0, 0, width, height, True, libtcod.BKGND_NONE, header)
	if footer != None:
		libtcod.console_print_ex(box, width / 2, height - 1, libtcod.BKGND_SET, libtcod.CENTER, '[ ' + footer + ' ]')

	if typ in ['inv', 'drop', 'use', 'remove', 'equip']:
		choice = choices(box, width - 4, height - 4, contents, 'inventory', 2, 2)
	if typ == 'save':
		choice = choices(box, width - 4, height - 4, contents, 'savegames', 2, 2)
	if typ in ['options', 'main_menu']:
		choice = choices(box, width - 2, height - 2, contents, 'options_menu', 1, 1, default)
	if typ == 'text':
		for i, line in enumerate(contents.split('\n')):
			if center:
				libtcod.console_print_ex(box, width / 2, 2 + i, libtcod.BKGND_SET, libtcod.CENTER, line)
			else:
				libtcod.console_print_ex(box, 2, 2 + i, libtcod.BKGND_SET, libtcod.LEFT, line)
		libtcod.console_blit(box, 0, 0, width, height, 0, (game.SCREEN_WIDTH - width) / 2, (game.SCREEN_HEIGHT - height) / 2, 1.0, 0.8)
		libtcod.console_flush()
		libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS, libtcod.Key(), libtcod.Mouse(), True)
		choice = -1
	return choice


def items_at_feet():
	objects = [obj for obj in game.current_map.objects if obj.item and obj.x == game.char.x and obj.y == game.char.y]
	if len(objects) > 1:
		game.message.new('You see several items at your feet.', game.player.turns, libtcod.white)
	elif len(objects) == 1:
		game.message.new('You see ' + objects[0].item.article + objects[0].item.name, game.player.turns, libtcod.white)


def roll_dice(nb_dices, nb_faces, multiplier, bonus):
	return libtcod.random_get_int(game.rnd, nb_dices, nb_dices * nb_faces * multiplier) + bonus


def get_names_under_mouse():
	#return a string with the names of all objects under the mouse
	(x, y) = (game.mouse.cx - game.MAP_X, game.mouse.cy - 1)

	#create a list with the names of all objects at the mouse's coordinates and in FOV
	if x in range(0, game.MAP_WIDTH - 1) and y in range(0, game.MAP_HEIGHT - 1) and game.current_map.explored[x][y]:
		names = [obj for obj in game.current_map.objects
			if obj.x == x and obj.y == y]

		prefix = 'you see '
		if not libtcod.map_is_in_fov(game.fov_map, x, y):
			prefix = 'you remember seeing '
			for i in range(len(names) - 1, -1, -1):
				if names[i].entity != None:
					names.pop(i)
		if (x, y) == (game.char.x, game.char.y):
			return 'you see yourself'
		if names == []:
			return prefix + game.current_map.tiles[x][y].article + game.current_map.tiles[x][y].name

		if len(names) > 1:
			string = prefix
			for i in range(0, len(names)):
				if i == len(names) - 1:
					string += ' and '
				elif i > 0:
					string += ', '
				if names[i].item != None:
					string += names[i].item.article + names[i].item.name
				if names[i].entity != None:
					string += names[i].entity.article + names[i].entity.name
			return string
		else:
			if names[0].item != None:
				return prefix + names[0].item.article + names[0].item.name
			if names[0].entity != None:
				return prefix + names[0].entity.article + names[0].entity.name
	else:
		return ''


def initialize_fov():
	game.fov_map = libtcod.map_new(game.MAP_WIDTH, game.MAP_HEIGHT)
	for y in range(game.MAP_HEIGHT):
		for x in range(game.MAP_WIDTH):
			libtcod.map_set_properties(game.fov_map, x, y, not game.current_map.tiles[x][y].block_sight, game.current_map.explored[x][y] and (not game.current_map.is_blocked(x, y)))
	game.path_dijk = libtcod.dijkstra_new(game.fov_map)
	game.path_recalculate = True


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


def render_message_panel():
	#prepare to render the message panel
	libtcod.console_set_default_foreground(0, libtcod.grey)
	libtcod.console_set_default_background(0, libtcod.black)
	libtcod.console_print_frame(0, game.MESSAGE_X - 1, game.MESSAGE_Y - 1, game.MESSAGE_WIDTH + 2, game.MESSAGE_HEIGHT + 2, True, libtcod.BKGND_NONE, None)
	libtcod.console_print(0, game.SCREEN_WIDTH - 1, game.MESSAGE_Y - 1, chr(180))
	libtcod.console_set_default_background(game.panel, libtcod.black)  # libtcod.Color(60, 45, 33))
	libtcod.console_clear(game.panel)
	game.message.delete()

	#print the game messages, one line at a time
	y = 0
	for (line, color, turn) in game.message.log:
		new_color = libtcod.color_lerp(libtcod.darkest_grey, color, 1 - ((game.player.turns - turn) * 0.1))
		libtcod.console_set_default_foreground(game.panel, new_color)
		libtcod.console_print(game.panel, 0, y, line)
		y += 1

	libtcod.console_blit(game.panel, 0, 0, game.MESSAGE_WIDTH, game.MESSAGE_HEIGHT, 0, game.MESSAGE_X, game.MESSAGE_Y)


def render_player_stats_panel():
	libtcod.console_set_default_foreground(0, libtcod.grey)
	libtcod.console_set_default_background(0, libtcod.black)
	libtcod.console_print_frame(0, 0, 0, game.MAP_X, game.SCREEN_HEIGHT, True, libtcod.BKGND_SET, None)
	libtcod.console_print(0, game.MESSAGE_X - 1, game.MESSAGE_Y - 1, chr(195))
	libtcod.console_print(0, game.MESSAGE_X - 1, game.SCREEN_HEIGHT - 1, chr(193))
	libtcod.console_print(0, game.MESSAGE_X - 1, 0, chr(194))
	render_bar(game.ps, 0, 6, game.PLAYER_STATS_WIDTH, 'HP', game.player.health, game.player.max_health, libtcod.red, libtcod.darker_red)
	render_bar(game.ps, 0, 7, game.PLAYER_STATS_WIDTH, 'MP', game.player.mana, game.player.max_mana, libtcod.blue, libtcod.darker_blue)
	libtcod.console_print(game.ps, 0, 0, game.player.name)
	libtcod.console_print(game.ps, 0, 1, game.player.race + " " + game.player.profession)
	libtcod.console_set_default_foreground(game.ps, libtcod.dark_green)
	libtcod.console_print(game.ps, 0, 3, game.current_map.location_name)
	libtcod.console_print(game.ps, 0, 4, "Level " + str(game.current_map.location_level))
	libtcod.console_set_default_foreground(game.ps, libtcod.white)
	libtcod.console_print(game.ps, 0, 9, "LV: " + str(game.player.level))
	libtcod.console_print(game.ps, 0, 10, "XP: " + str(game.player.xp))
	libtcod.console_print(game.ps, 0, 11, "Str:  " + str(game.player.strength))
	libtcod.console_print(game.ps, 0, 12, "Dex:  " + str(game.player.dexterity))
	libtcod.console_print(game.ps, 0, 13, "Int:  " + str(game.player.intelligence))
	libtcod.console_print(game.ps, 0, 14, "End:  " + str(game.player.endurance))
	libtcod.console_print(game.ps, 0, 15, "Luck: " + str(game.player.luck))
	libtcod.console_print(game.ps, 0, 17, "Turns: " + str(game.player.turns))
	libtcod.console_blit(game.ps, 0, 0, game.PLAYER_STATS_WIDTH, game.PLAYER_STATS_HEIGHT, 0, game.PLAYER_STATS_X, game.PLAYER_STATS_Y)


def render_all():
	libtcod.console_set_default_foreground(0, libtcod.grey)
	libtcod.console_set_default_background(0, libtcod.black)
	libtcod.console_print_frame(0, game.MAP_X - 1, game.MAP_Y - 1, game.MAP_WIDTH + 2, game.MAP_HEIGHT + 2, True, libtcod.BKGND_NONE, None)
	libtcod.console_clear(game.con)
	# recompute FOV if needed (the player moved or something)
	if game.fov_recompute:
		initialize_fov()
		game.fov_recompute = False
		if game.TORCH_RADIUS > 0:
			libtcod.map_compute_fov(game.fov_map, game.char.x, game.char.y, game.TORCH_RADIUS, game.FOV_LIGHT_WALLS, game.FOV_ALGO)
		else:
			libtcod.map_compute_fov(game.fov_map, game.char.x, game.char.y, game.FOV_RADIUS, game.FOV_LIGHT_WALLS, game.FOV_ALGO)

	# 'torch' animation
	if game.fov_torch:
		game.fov_torchx += 0.2
		tdx = [game.fov_torchx + 20.0]
		dx = libtcod.noise_get(game.fov_noise, tdx, libtcod.NOISE_SIMPLEX) * 1.5
		tdx[0] += 30.0
		dy = libtcod.noise_get(game.fov_noise, tdx, libtcod.NOISE_SIMPLEX) * 1.5
		di = 0.4 * libtcod.noise_get(game.fov_noise, [game.fov_torchx], libtcod.NOISE_SIMPLEX)

	# compute path using dijkstra algorithm
	if game.path_recalculate:
		libtcod.dijkstra_compute(game.path_dijk, game.char.x, game.char.y)
		libtcod.dijkstra_path_set(game.path_dijk, game.path_dx, game.path_dy)
		game.path_recalculate = False

	# go through all tiles, and set their background color according to the FOV
	for y in range(game.MAP_HEIGHT):
		for x in range(game.MAP_WIDTH):
			visible = libtcod.map_is_in_fov(game.fov_map, x, y)
			if not visible:
				if game.current_map.explored[x][y]:
					libtcod.console_put_char_ex(game.con, x, y, game.current_map.tiles[x][y].icon, game.current_map.tiles[x][y].dark_color, libtcod.black)
			else:
				if not game.fov_torch:
					libtcod.console_put_char_ex(game.con, x, y, game.current_map.tiles[x][y].icon, game.current_map.tiles[x][y].color, libtcod.black)
				else:
					base = libtcod.black
					light = libtcod.gold
					r = float(x - game.char.x + dx) * (x - game.char.x + dx) + (y - game.char.y + dy) * (y - game.char.y + dy)
					if r < game.SQUARED_TORCH_RADIUS:
						l = (game.SQUARED_TORCH_RADIUS - r) / game.SQUARED_TORCH_RADIUS + di
						if l < 0.0:
							l = 0.0
						elif l > 1.0:
							l = 1.0
						base = libtcod.color_lerp(base, light, l)
					libtcod.console_put_char_ex(game.con, x, y, game.current_map.tiles[x][y].icon, game.current_map.tiles[x][y].color, base)
				game.current_map.explored[x][y] = True

	# draw a line between the player and the mouse cursor
	if game.current_map.explored[game.path_dx][game.path_dy]:
		for i in range(libtcod.dijkstra_size(game.path_dijk)):
			x, y = libtcod.dijkstra_get(game.path_dijk, i)
			libtcod.console_set_char_background(game.con, x, y, libtcod.desaturated_yellow, libtcod.BKGND_SET)

	# move the player if using mouse
	if game.mouse_move:
		if not libtcod.dijkstra_is_empty(game.path_dijk):
			libtcod.console_put_char(game.con, game.char.x, game.char.y, ' ', libtcod.BKGND_NONE)
			game.char.x, game.char.y = libtcod.dijkstra_path_walk(game.path_dijk)
			libtcod.console_put_char(game.con, game.char.x, game.char.y, '@', libtcod.BKGND_NONE)
			game.path_recalculate = True
			game.fov_recompute = True
			game.player.add_turn()
		else:
			game.mouse_move = False

	if not game.mouse_move:
		(mx, my) = (game.mouse.cx - game.MAP_X, game.mouse.cy - 1)
		if mx in range(0, game.MAP_WIDTH - 1) and my in range(0, game.MAP_HEIGHT - 1):
			if game.current_map.explored[mx][my] and not game.current_map.tiles[mx][my].blocked:
				game.path_dx = mx
				game.path_dy = my
				libtcod.console_set_char_background(game.con, game.path_dx, game.path_dy, libtcod.white, libtcod.BKGND_SET)
				if game.mouse.lbutton_pressed:
					game.mouse_move = True
			else:
				game.path_dx = 0
				game.path_dy = 0
			if not game.current_map.tiles[game.path_dx][game.path_dy].blocked:
				game.path_recalculate = True

	#draw all objects in the list, except the player. we want it to
	#always appear over all other objects! so it's drawn later.
	for object in reversed(game.current_map.objects):
		if object != game.char:
			object.draw(game.con)
	game.char.draw(game.con)

	libtcod.console_print(game.con, 0, 0, get_names_under_mouse())
	libtcod.console_print(game.con, game.MAP_WIDTH - 9, 0, '(%3d fps)' % libtcod.sys_get_fps())
	libtcod.console_blit(game.con, 0, 0, game.MAP_WIDTH, game.MAP_HEIGHT, 0, game.MAP_X, game.MAP_Y)

	render_message_panel()
	render_player_stats_panel()
