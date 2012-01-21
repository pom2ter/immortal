import libtcodpy as libtcod
import textwrap
import game


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


def text_input(con, posx, posy):
	command = ''
	x = 0
	key = libtcod.console_wait_for_keypress(True)
	while key.vk != libtcod.KEY_ENTER:
		if key.vk == libtcod.KEY_BACKSPACE and x > 0:
			libtcod.console_set_char(con, x + posx - 1, posy, " ")
			libtcod.console_set_char_foreground(con, x + posx - 1, posy, libtcod.white)
			command = command[:-1]
			x -= 1
		elif key.vk == libtcod.KEY_ENTER:
			break
#		elif key.vk == libtcod.KEY_ESCAPE:
#			command = ""
#			break
		elif key.c > 0:
			letter = chr(key.c)
			libtcod.console_set_char(con, x + posx, posy, letter)  # print new character at appropriate position on screen
			libtcod.console_set_char_foreground(con, x + posx, posy, libtcod.light_red)  # make it white or something
			command += letter  # add to the string
			x += 1

		libtcod.console_blit(con, 0, 0, game.SCREEN_WIDTH - 40, game.SCREEN_HEIGHT, 0, 0, 0)
		libtcod.console_flush()
		key = libtcod.console_check_for_keypress(libtcod.KEY_PRESSED)

	return command


def message(new_msg, color=libtcod.white):
	#split the message if necessary, among multiple lines
	new_msg_lines = textwrap.wrap(new_msg, game.MSG_WIDTH)

	for line in new_msg_lines:
		#if the buffer is full, remove the first line to make room for the new one
		if len(game.messages) == game.MSG_HEIGHT:
			del game.messages[0]

		#add the new line as a tuple, with the text and the color
		game.messages.append((line, color))


def menu(header, options, width):
	if len(options) > 26:
		raise ValueError('Cannot have a menu with more than 26 options.')

	#calculate total height for the header (after auto-wrap) and one line per option
	header_height = libtcod.console_get_height_rect(game.con, 0, 0, width, game.SCREEN_HEIGHT, header)
	if header == '':
		header_height = 0
	height = len(options) + header_height

	#create an off-screen console that represents the menu's window
	window = libtcod.console_new(width, height)

	#print the header, with auto-wrap
	libtcod.console_set_default_foreground(window, libtcod.white)
	libtcod.console_print(window, 0, 0, header)

	#print all the options
	y = header_height
	letter_index = ord('a')
	for option_text in options:
		text = '(' + chr(letter_index) + ') ' + option_text
		libtcod.console_print(window, 0, y, text)
		y += 1
		letter_index += 1

	#blit the contents of "window" to the root console
	x = game.SCREEN_WIDTH / 2 - width / 2
	y = game.SCREEN_HEIGHT / 2 - height / 2
	libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

	#present the root console to the player and wait for a key-press
	libtcod.console_flush()
	key = libtcod.console_wait_for_keypress(True)

	if key.vk == libtcod.KEY_ENTER and key.lalt:  # (special case) Alt+Enter: toggle fullscreen
		libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

	#convert the ASCII code to an index; if it corresponds to an option, return it
	index = key.c - ord('a')
	if index >= 0 and index < len(options):
		return index
	return None


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
			libtcod.map_set_properties(game.fov_map, x, y, not game.current_map.tiles[x][y].blocked, not game.current_map.tiles[x][y].block_sight)

	libtcod.console_clear(game.con)  # unexplored areas start black (which is the default background color)


def render_all():
	if game.fov_recompute:
		#recompute FOV if needed (the player moved or something)
		game.fov_recompute = False
		if game.TORCH_RADIUS > game.FOV_RADIUS:
			libtcod.map_compute_fov(game.fov_map, game.char.x, game.char.y, game.TORCH_RADIUS, game.FOV_LIGHT_WALLS, game.FOV_ALGO)
		else:
			libtcod.map_compute_fov(game.fov_map, game.char.x, game.char.y, game.FOV_RADIUS, game.FOV_LIGHT_WALLS, game.FOV_ALGO)
	if game.fov_torch:
		# slightly change the perlin noise parameter
		game.fov_torchx += 0.2
		# randomize the light position between -1.5 and 1.5
		tdx = [game.fov_torchx + 20.0]
		dx = libtcod.noise_get(game.fov_noise, tdx, libtcod.NOISE_SIMPLEX) * 1.5
		tdx[0] += 30.0
		dy = libtcod.noise_get(game.fov_noise, tdx, libtcod.NOISE_SIMPLEX) * 1.5
		di = 0.4 * libtcod.noise_get(game.fov_noise, [game.fov_torchx], libtcod.NOISE_SIMPLEX)

	#go through all tiles, and set their background color according to the FOV
	for y in range(game.MAP_HEIGHT):
		for x in range(game.MAP_WIDTH):
			visible = libtcod.map_is_in_fov(game.fov_map, x, y)
			if not visible:
				#if it's not visible right now, the player can only see it if it's explored
				if game.current_map.tiles[x][y].explored:
					libtcod.console_put_char_ex(game.con, x, y, game.current_map.tiles[x][y].icon, game.current_map.tiles[x][y].dark_color, libtcod.black)
			else:
				if not game.fov_torch:
					#it's visible
					libtcod.console_put_char_ex(game.con, x, y, game.current_map.tiles[x][y].icon, game.current_map.tiles[x][y].color, libtcod.black)
				else:
					base = libtcod.black
					light = libtcod.gold
					# cell distance to torch (squared)
					r = float(x - game.char.x + dx) * (x - game.char.x + dx) + (y - game.char.y + dy) * (y - game.char.y + dy)
					if r < game.SQUARED_TORCH_RADIUS:
						l = (game.SQUARED_TORCH_RADIUS - r) / game.SQUARED_TORCH_RADIUS + di
						if l < 0.0:
							l = 0.0
						elif l > 1.0:
							l = 1.0
						base = libtcod.color_lerp(base, light, l)
					libtcod.console_put_char_ex(game.con, x, y, game.current_map.tiles[x][y].icon, game.current_map.tiles[x][y].color, base)
				#since it's visible, explore it
				game.current_map.tiles[x][y].explored = True

	#draw all objects in the list, except the player. we want it to
	#always appear over all other objects! so it's drawn later.
	for object in game.current_map.objects:
		if object != game.char:
			object.draw()
	game.char.draw(game.con)

	#blit the contents of "con" to the root console
	libtcod.console_print(game.con, 0, 0, get_names_under_mouse())
	libtcod.console_blit(game.con, 0, 0, game.MAP_WIDTH, game.MAP_HEIGHT, 0, 20, 0)

### message panel
	#prepare to render the message panel
	libtcod.console_set_default_background(game.panel, libtcod.black)
	libtcod.console_clear(game.panel)

	#print the game messages, one line at a time
	y = 0
	for (line, color) in game.messages:
		libtcod.console_set_default_foreground(game.panel, color)
		libtcod.console_print(game.panel, game.MSG_X, y, line)
		y += 1

	#display names of objects under the mouse
	libtcod.console_set_default_foreground(game.panel, libtcod.light_gray)
	libtcod.console_print(game.panel, 0, 0, get_names_under_mouse())

	#blit the contents of "panel" to the root console
	libtcod.console_blit(game.panel, 0, 0, game.SCREEN_WIDTH, game.PANEL_HEIGHT, 0, 0, game.PANEL_Y)

### player panel
	#show the player's stats
	render_bar(game.ps, 0, 3, game.BAR_WIDTH, 'HP', game.player.health, game.player.max_health, libtcod.red, libtcod.darker_red)
	render_bar(game.ps, 0, 4, game.BAR_WIDTH, 'MP', game.player.mana, game.player.max_mana, libtcod.blue, libtcod.darker_blue)

	libtcod.console_print(game.ps, 0, 0, game.player.name)
	libtcod.console_print(game.ps, 0, 1, game.player.race + " " + game.player.profession)
	libtcod.console_print(game.ps, 0, 6, "LV: " + str(game.player.level))
	libtcod.console_print(game.ps, 0, 7, "XP: " + str(game.player.xp))
	libtcod.console_print(game.ps, 0, 9, "Str: " + str(game.player.strength))
	libtcod.console_print(game.ps, 0, 10, "Dex: " + str(game.player.dexterity))
	libtcod.console_print(game.ps, 0, 11, "Int: " + str(game.player.intelligence))
	libtcod.console_print(game.ps, 0, 12, "End: " + str(game.player.endurance))
	libtcod.console_print(game.ps, 0, 13, "Luck: " + str(game.player.luck))

	libtcod.console_blit(game.ps, 0, 0, game.PLAYER_STATS_WIDTH, game.PLAYER_STATS_HEIGHT, 0, 0, 0)
