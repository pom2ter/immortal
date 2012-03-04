import libtcodpy as libtcod
import map
import game


def choices(con, width, height, options, typ, bspace=False):
	choice = False
	current, up, empty = 0, 0, 3
	down = height - empty
	while not choice and choice != -1:
		key = libtcod.console_check_for_keypress(libtcod.KEY_PRESSED)
		libtcod.console_set_default_foreground(con, libtcod.grey)
		libtcod.console_set_default_background(con, libtcod.black)
		libtcod.console_rect(con, 1, 2, width - 2, height - 4, True, libtcod.BKGND_SET)
		if up != 0:
			libtcod.console_print_ex(con, width - 2, 2, libtcod.BKGND_SET, libtcod.LEFT, chr(136))
		if down < len(options):
			libtcod.console_print_ex(con, width - 2, height - 4, libtcod.BKGND_SET, libtcod.LEFT, chr(142))
		for y in range(up, down):
			if y < len(options):
				if y == current:
					libtcod.console_set_default_foreground(con, libtcod.white)
					libtcod.console_set_default_background(con, libtcod.light_blue)
				else:
					libtcod.console_set_default_foreground(con, libtcod.grey)
					libtcod.console_set_default_background(con, libtcod.black)
				if typ == 'inventory':
					#text = '(' + chr((y - up) + 97) + ') ' + options[y].unidentified_name
					textl = options[y].unidentified_name
					textr = str(options[y].weight) + ' lbs'
				else:
					#text = '(' + chr((y - up) + 97) + ') ' + options[y]
					textl = options[y]
					textr = ''
				libtcod.console_rect(con, 2, (y - up) + 2, width - 4, 1, True, libtcod.BKGND_SET)
				libtcod.console_print_ex(con, 3, (y - up) + 2, libtcod.BKGND_SET, libtcod.LEFT, textl)
				libtcod.console_print_ex(con, width - 4, (y - up) + 2, libtcod.BKGND_SET, libtcod.RIGHT, textr)

		libtcod.console_blit(con, 0, 0, width, height, 0, (game.SCREEN_WIDTH - width) / 2, (game.SCREEN_HEIGHT - height) / 2, 1.0, 0.75)
		libtcod.console_flush()
		if key.vk == libtcod.KEY_DOWN:
			current = (current + 1) % len(options)
			if current == down:
				down += 1
				up += 1
			if current == 0:
				down = height - empty
				up = 0
		elif key.vk == libtcod.KEY_UP:
			current = (current - 1) % len(options)
			if current < up:
				up -= 1
				down -= 1
			if current == len(options) - 1:
				if current > height - empty:
					up = len(options) - (height - empty)
					down = len(options)
		elif key.vk == libtcod.KEY_BACKSPACE and bspace:
			obj = map.Object(game.char.x, game.char.y, options[current].icon, options[current].name, options[current].color, True, item=options[current])
			game.current_map.objects.append(obj)
			obj.send_to_back()
			game.player.inventory.pop(current)
			if current == len(options):
				current -= 1
			if len(options) == 0:
				choice = -1
		elif key.vk == libtcod.KEY_ESCAPE:
			current = -1
			choice = -1
		elif key.vk == libtcod.KEY_ENTER:
			choice = True
	return current


def msg_box(typ, header=None, footer=None):
	width = 60
	height = max(16, len(game.player.inventory) + 4)
	box = libtcod.console_new(width, height)
	libtcod.console_set_default_foreground(box, libtcod.white)
	libtcod.console_set_default_background(box, libtcod.black)
	libtcod.console_print_frame(box, 0, 0, width, height, True, libtcod.BKGND_NONE, header)
	if footer != None:
		libtcod.console_print_ex(box, width / 2, height - 1, libtcod.BKGND_SET, libtcod.CENTER, '[ ' + footer + ' ]')

	if typ == 'inv':
		choice = choices(box, width, height, game.player.inventory, 'inventory', bspace=True)
	if typ == 'drop':
		choice = choices(box, width, height, game.player.inventory, 'inventory')
	return choice


def menu(header, options):
	choice = False
	current = 0
	width = 0
	height = len(options) + 2

	for option_text in options:
		if len(option_text) > width:
			width = len(option_text) + 5

	#create an off-screen console that represents the menu's window
	window = libtcod.console_new(width, height)
	libtcod.console_set_default_foreground(window, libtcod.white)
	libtcod.console_set_default_background(window, libtcod.black)
	libtcod.console_print_frame(window, 0, 0, width, height, True, libtcod.BKGND_NONE, header)

	while not choice:
		key = libtcod.console_check_for_keypress(libtcod.KEY_PRESSED)
		#print all the options
		for y in range(0, len(options)):
			if y == current:
				libtcod.console_set_default_foreground(window, libtcod.white)
				libtcod.console_set_default_background(window, libtcod.light_blue)
			else:
				libtcod.console_set_default_foreground(window, libtcod.grey)
				libtcod.console_set_default_background(window, libtcod.black)
			libtcod.console_rect(window, 1, y + 1, width - 2, 1, False, libtcod.BKGND_SET)
			libtcod.console_print_ex(window, 2, y + 1, libtcod.BKGND_SET, libtcod.LEFT, options[y])

		#blit the contents of "window" to the root console
		x = game.SCREEN_WIDTH / 2 - width / 2
		y = game.SCREEN_HEIGHT / 2 - height / 2
		libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.75)
		libtcod.console_flush()

		mouse = libtcod.mouse_get_status()
		(mx, my) = (mouse.cx, mouse.cy)
		if my in range(y + 1, len(options) + (y + 1)) and mx in range(x + 1, x + width - 1):
			current = my - (y + 1)

		if key.vk == libtcod.KEY_DOWN:
			current = (current + 1) % len(options)
		elif key.vk == libtcod.KEY_UP:
			current = (current - 1) % len(options)
		elif key.vk == libtcod.KEY_ENTER or (mouse.lbutton_pressed and my in range(y + 1, len(options) + (y + 1)) and mx in range(x + 1, x + width - 1)):
			choice = True
	return current


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
	libtcod.console_print_ex(con, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER, name + ': ' + str(value) + '/' + str(maximum))


def get_names_under_mouse():
	#return a string with the names of all objects under the mouse
	mouse = libtcod.mouse_get_status()
	(x, y) = (mouse.cx - game.PLAYER_STATS_WIDTH, mouse.cy)

	#create a list with the names of all objects at the mouse's coordinates and in FOV
	if x in range(0, game.MAP_WIDTH - 1) and y in range(0, game.MAP_HEIGHT - 1) and game.current_map.tiles[x][y].explored:
		names = [obj.name for obj in game.current_map.objects
			if obj.x == x and obj.y == y and libtcod.map_is_in_fov(game.fov_map, obj.x, obj.y)]

		if names == []:
			return 'you see a ' + game.current_map.tiles[x][y].name

		names = ', a '.join(names)  # join the names, separated by commas
		return 'you see a ' + names.capitalize()
	else:
		return ''


def initialize_fov():
	game.fov_map = libtcod.map_new(game.MAP_WIDTH, game.MAP_HEIGHT)
	for y in range(game.MAP_HEIGHT):
		for x in range(game.MAP_WIDTH):
			libtcod.map_set_properties(game.fov_map, x, y, not game.current_map.tiles[x][y].block_sight, game.current_map.tiles[x][y].explored and (not game.current_map.tiles[x][y].blocked))
	game.path_dijk = libtcod.dijkstra_new(game.fov_map)
	game.path_recalculate = True


def render_message_panel():
	#prepare to render the message panel
	libtcod.console_set_default_background(game.panel, libtcod.black)
	libtcod.console_clear(game.panel)
	game.message.delete()

	#print the game messages, one line at a time
	y = 0
	for (line, color, turn) in game.message.log:
		new_color = libtcod.color_lerp(libtcod.darkest_grey, color, 1 - ((game.player.turns - turn) * 0.1))
		libtcod.console_set_default_foreground(game.panel, new_color)
		libtcod.console_print(game.panel, game.MSG_X, y, line)
		y += 1

	libtcod.console_blit(game.panel, 0, 0, game.SCREEN_WIDTH, game.PANEL_HEIGHT, 0, 0, game.PANEL_Y)


def render_player_stats_panel():
	render_bar(game.ps, 0, 5, game.PLAYER_STATS_WIDTH, 'HP', game.player.health, game.player.max_health, libtcod.red, libtcod.darker_red)
	render_bar(game.ps, 0, 6, game.PLAYER_STATS_WIDTH, 'MP', game.player.mana, game.player.max_mana, libtcod.blue, libtcod.darker_blue)
	libtcod.console_print(game.ps, 0, 0, game.player.name)
	libtcod.console_print(game.ps, 0, 1, game.player.race + " " + game.player.profession)
	libtcod.console_set_default_foreground(game.ps, libtcod.dark_green)
	libtcod.console_print(game.ps, 0, 3, game.current_map.location_name)
	libtcod.console_set_default_foreground(game.ps, libtcod.white)
	libtcod.console_print(game.ps, 0, 8, "LV: " + str(game.player.level))
	libtcod.console_print(game.ps, 0, 9, "XP: " + str(game.player.xp))
	libtcod.console_print(game.ps, 0, 10, "Str:  " + str(game.player.strength))
	libtcod.console_print(game.ps, 0, 11, "Dex:  " + str(game.player.dexterity))
	libtcod.console_print(game.ps, 0, 12, "Int:  " + str(game.player.intelligence))
	libtcod.console_print(game.ps, 0, 13, "End:  " + str(game.player.endurance))
	libtcod.console_print(game.ps, 0, 14, "Luck: " + str(game.player.luck))
	libtcod.console_blit(game.ps, 0, 0, game.PLAYER_STATS_WIDTH, game.PLAYER_STATS_HEIGHT, 0, 0, 0)


def render_all():
	libtcod.console_clear(game.con)
	# recompute FOV if needed (the player moved or something)
	if game.fov_recompute:
		initialize_fov()
		game.fov_recompute = False
		if game.TORCH_RADIUS > game.FOV_RADIUS:
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
				if game.current_map.tiles[x][y].explored:
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
				game.current_map.tiles[x][y].explored = True

	# draw a line between the player and the mouse cursor
	if game.current_map.tiles[game.path_dx][game.path_dy].explored:
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
			game.player.turns += 1
		else:
			game.mouse_move = False

	if not game.mouse_move:
		mouse = libtcod.mouse_get_status()
		(mx, my) = (mouse.cx - game.PLAYER_STATS_WIDTH, mouse.cy)
		if mx in range(0, game.MAP_WIDTH - 1) and my in range(0, game.MAP_HEIGHT - 1):
			if game.current_map.tiles[mx][my].explored and not game.current_map.tiles[mx][my].blocked:
				game.path_dx = mx
				game.path_dy = my
				libtcod.console_set_char_background(game.con, game.path_dx, game.path_dy, libtcod.white, libtcod.BKGND_SET)
				if mouse.lbutton_pressed:
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

	libtcod.console_print(game.con, 1, 0, get_names_under_mouse())
	libtcod.console_print(game.con, game.MAP_WIDTH - 9, 0, '(%3d fps)' % libtcod.sys_get_fps())
	libtcod.console_blit(game.con, 0, 0, game.MAP_WIDTH, game.MAP_HEIGHT, 0, 20, 0)

	render_message_panel()
	render_player_stats_panel()
