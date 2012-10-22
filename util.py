import libtcodpy as libtcod
import pickle
import os
import game


#######################################
# messages functions
#######################################

def choices(con, width, height, options, typ, posx=0, posy=0, default=0, blitmap=False, mouse_out=False):
	choice = False
	current, up, down = default, 0, height
	max_width = posx + width + posx
	max_height = posy + height + posy
	key = libtcod.Key()
	mouse = libtcod.Mouse()
	lerp = 1.0
	descending = True

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
					color = libtcod.black
					libtcod.console_set_default_foreground(con, libtcod.white)
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
					color = libtcod.color_lerp(color, libtcod.light_blue, lerp)
					libtcod.console_set_default_background(con, color)
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

		if blitmap:
			x = ((game.MAP_WIDTH - max_width) / 2) + game.MAP_X
			y = (game.MAP_HEIGHT - max_height) / 2
		else:
			x = (game.SCREEN_WIDTH - max_width) / 2
			y = (game.SCREEN_HEIGHT - max_height) / 2
		libtcod.console_blit(con, 0, 0, max_width, max_height, 0, x, y, 1.0, 0.9)
		libtcod.console_flush()

		(mx, my) = (mouse.cx, mouse.cy)
		if my in range(y + posy, y + height + posy) and mx in range(x + posx, x + width + posx):
			mpos = my - (y + posy) + up
			if mpos <= len(options) - 1:
				current = mpos

		if key.vk == libtcod.KEY_DOWN and ev == libtcod.EVENT_KEY_PRESS:
			current = (current + 1) % len(options)
			if current == down:
				down += 1
				up += 1
			if current == 0:
				down = height
				up = 0
			lerp = 1.0
			descending = True
		elif key.vk == libtcod.KEY_UP and ev == libtcod.EVENT_KEY_PRESS:
			current = (current - 1) % len(options)
			if current < up:
				up -= 1
				down -= 1
			if current == len(options) - 1:
				if current > height - 1:
					up = len(options) - height
					down = len(options)
			lerp = 1.0
			descending = True
		elif key.vk == libtcod.KEY_ESCAPE and ev == libtcod.EVENT_KEY_PRESS or (mouse_out and mouse.lbutton_pressed and mx == max_width + x - 4 and my == y):
			current = -1
			choice = -1
		elif (key.vk == libtcod.KEY_ENTER and ev == libtcod.EVENT_KEY_PRESS) or (mouse.lbutton_pressed and my in range(y + posy, y + height + posy) and mx in range(x + posx, x + width + posx) and (my - (y + posy) + up) <= len(options) - 1):
			choice = True
	return current


def text_box(con, x1, y1, x2, y2, header=None, color=libtcod.green):
	buffer = libtcod.ConsoleBuffer(x2 - x1, y2 - y1)
	for i in range(x1, x2):
		buffer.set_fore(i, y1, color.r, color.g, color.b, chr(205))
		buffer.set_fore(i, y2 - 1, color.r, color.g, color.b, chr(205))
	for i in range(y1, y2):
		buffer.set_fore(x1, i, color.r, color.g, color.b, chr(186))
		buffer.set_fore(x2 - 1, i, color.r, color.g, color.b, chr(186))
	buffer.set_back(x1, y1, color.r, color.g, color.b)
	buffer.set_back(x1, y2 - 1, color.r, color.g, color.b)
	buffer.set_back(x2 - 1, y1, color.r, color.g, color.b)
	buffer.set_back(x2 - 1, y2 - 1, color.r, color.g, color.b)
	buffer.blit(con, fill_fore=True, fill_back=True)

	if header != None:
		libtcod.console_set_default_foreground(con, libtcod.black)
		libtcod.console_set_default_background(con, color)
		libtcod.console_print_ex(con, x2 / 2, y1, libtcod.BKGND_SET, libtcod.CENTER, ' ' + header + ' ')


def msg_box(typ, header=None, footer=None, contents=None, box_width=60, box_height=5, center=False, default=0, color=libtcod.green, blitmap=False):
	box = libtcod.console_new(box_width, box_height)
	text_box(box, 0, 0, box_width, box_height, header, color)
	libtcod.console_set_default_foreground(box, color)
	libtcod.console_set_default_background(box, libtcod.black)
	if footer != None:
		libtcod.console_print_ex(box, box_width / 2, box_height - 1, libtcod.BKGND_SET, libtcod.CENTER, '[ ' + footer + ' ]')
	if typ in ['inv', 'drop', 'use', 'remove', 'equip', 'save', 'options']:
		libtcod.console_print_ex(box, box_width - 5, 0, libtcod.BKGND_SET, libtcod.LEFT, '[x]')
	libtcod.console_set_default_foreground(box, libtcod.white)

	if typ in ['inv', 'drop', 'use', 'remove', 'equip', 'pickup']:
		choice = choices(box, box_width - 4, box_height - 4, contents, 'inventory', 2, 2, blitmap=blitmap, mouse_out=True)
	if typ == 'save':
		choice = choices(box, box_width - 4, box_height - 4, contents, 'savegames', 2, 2, mouse_out=True)
	if typ in ['options', 'main_menu']:
		if typ == 'options':
			choice = choices(box, box_width - 2, box_height - 2, contents, 'options_menu', 1, 1, default, blitmap=blitmap, mouse_out=True)
		else:
			choice = choices(box, box_width - 2, box_height - 2, contents, 'options_menu', 1, 1, default, blitmap=blitmap)
	if typ == 'settings':
		change_settings(box, box_width, box_height, contents, blitmap=blitmap)
		choice = -1
	if typ in ['text', 'highscore', 'map']:
		if typ == 'highscore':
			for i, (score, line1, line2) in enumerate(game.highscore):
				libtcod.console_print_ex(box, 2, 2 + (i * 3), libtcod.BKGND_SET, libtcod.LEFT, str(score))
				libtcod.console_print_ex(box, 8, 2 + (i * 3), libtcod.BKGND_SET, libtcod.LEFT, line1)
				libtcod.console_print_ex(box, 8, 3 + (i * 3), libtcod.BKGND_SET, libtcod.LEFT, line2)
		if typ == 'text':
			for i, line in enumerate(contents.split('\n')):
				if center:
					libtcod.console_print_ex(box, box_width / 2, 2 + i, libtcod.BKGND_SET, libtcod.CENTER, line)
				else:
					libtcod.console_print_ex(box, 2, 2 + i, libtcod.BKGND_SET, libtcod.LEFT, line)
		if typ == 'map':
			#libtcod.image_blit(game.worldmap.mapimg_small, box, game.SCREEN_WIDTH / 2 + 1, game.SCREEN_HEIGHT / 2, libtcod.BKGND_SET, 1.0, 1.0, 0.0)
			libtcod.image_blit_2x(game.worldmap.mapimg_small, box, 1, 1)
		if blitmap:
			libtcod.console_blit(box, 0, 0, box_width, box_height, 0, ((game.MAP_WIDTH - box_width) / 2) + game.MAP_X, (game.MAP_HEIGHT - box_height) / 2, 1.0, 0.9)
		elif typ in ['text', 'highscore']:
			libtcod.console_blit(box, 0, 0, box_width, box_height, 0, (game.SCREEN_WIDTH - box_width) / 2, (game.SCREEN_HEIGHT - box_height) / 2, 1.0, 0.9)
		else:
			libtcod.console_blit(box, 0, 0, box_width, box_height, 0, (game.SCREEN_WIDTH - box_width) / 2, (game.SCREEN_HEIGHT - box_height) / 2, 1.0, 1.0)
		libtcod.console_flush()
		if contents != "Generating world map...":
			libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS, libtcod.Key(), libtcod.Mouse(), True)
		choice = -1
	return choice


#######################################
# miscellanous functions
#######################################

# change game settings
def change_settings(box, width, height, options, blitmap=False):
	fonts = ['  Small  ', '  Large  ']
	confirm, cancel = False, False
	if game.font == 'large':
		current = 1
	else:
		current = 0

	key = libtcod.Key()
	libtcod.console_print_rect(box, 2, 2, width - 4, 2, '(You may need to restart the game for the changes to take effect)')
	libtcod.console_print(box, 2, 5, 'Font: ')

	while not confirm and not cancel:
		for i in range(0, len(fonts)):
			libtcod.console_set_default_background(box, libtcod.black)
			if current == i:
				libtcod.console_set_default_background(box, libtcod.light_blue)
			libtcod.console_print_ex(box, 10 + (i * 10), 5, libtcod.BKGND_SET, libtcod.LEFT, fonts[i])

		if blitmap:
			libtcod.console_blit(box, 0, 0, width, height, 0, ((game.MAP_WIDTH - width) / 2) + game.MAP_X, (game.MAP_HEIGHT - height) / 2, 1.0, 1.0)
		else:
			libtcod.console_blit(box, 0, 0, width, height, 0, (game.SCREEN_WIDTH - width) / 2, (game.SCREEN_HEIGHT - height) / 2, 1.0, 1.0)
		libtcod.console_flush()
		libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS, key, libtcod.Mouse(), True)

		if key.vk == libtcod.KEY_LEFT:
			current -= 1
			if current < 0:
				current = 1
		elif key.vk == libtcod.KEY_RIGHT:
			current += 1
			if current > 1:
				current = 0
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


# death screens and final score
def death():
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
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 10, libtcod.BKGND_SET, libtcod.CENTER, 'Killed by')
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 11, libtcod.BKGND_SET, libtcod.CENTER, game.killer)
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 12, libtcod.BKGND_SET, libtcod.CENTER, 'on level ' + str(game.current_map.location_level) + ' in the')
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 13, libtcod.BKGND_SET, libtcod.CENTER, game.current_map.location_name)

	score = game.player.score()
	line1 = game.player.name + ', the level ' + str(game.player.level) + ' ' + game.player.gender + ' ' + game.player.race + ' ' + game.player.profession + ','
	line2 = 'killed by ' + game.killer + ' on level ' + str(game.current_map.location_level) + ' in the ' + game.current_map.location_name + ' (' + str(game.player.turns) + ' turns)'
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


# return a string with the names of all objects under the mouse
def get_names_under_mouse():
	#create a list with the names of all objects at the mouse's coordinates and in FOV
	(x, y) = (game.mouse.cx - game.MAP_X, game.mouse.cy - 1)
	if x in range(0, game.MAP_WIDTH - 1) and y in range(0, game.MAP_HEIGHT - 1) and game.current_map.explored[x][y]:
		names = [obj for obj in game.current_map.objects if obj.x == x and obj.y == y]
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


# output names of items you pass by
def items_at_feet():
	objects = [obj for obj in game.current_map.objects if obj.item and obj.x == game.char.x and obj.y == game.char.y]
	if len(objects) > 1:
		game.message.new('You see several items at your feet.', game.player.turns)
	elif len(objects) == 1:
		game.message.new('You see ' + objects[0].item.article + objects[0].item.name, game.player.turns)


# check to see if you can auto-move with mouse
def mouse_auto_move():
	for obj in game.current_map.objects:
		if libtcod.map_is_in_fov(game.fov_map, obj.x, obj.y) and (obj.entity != None):
			game.message.new("Auto-move aborted: Monster is near", game.player.turns)
			game.mouse_move = False
			return False
	return True


def roll_dice(nb_dices, nb_faces, multiplier, bonus):
	return libtcod.random_get_int(game.rnd, nb_dices, nb_dices * nb_faces * multiplier) + bonus


def save_high_scores():
	f = open('data/highscores.dat', 'wb')
	pickle.dump(game.highscore, f)
	f.close()


#######################################
# main screen functions
#######################################

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


def render_gui(color):
	buffer = libtcod.ConsoleBuffer(game.SCREEN_WIDTH, game.SCREEN_HEIGHT)
	for i in range(0, game.SCREEN_WIDTH):
		buffer.set_fore(i, 0, color.r, color.g, color.b, chr(205))
		buffer.set_fore(i, game.SCREEN_HEIGHT - 1, color.r, color.g, color.b, chr(205))
	for i in range(game.MAP_X, game.SCREEN_WIDTH):
		buffer.set_fore(i, game.MESSAGE_Y - 1, color.r, color.g, color.b, chr(205))
	for i in range(0, game.SCREEN_HEIGHT):
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


def render_message_panel():
	#print the game messages, one line at a time
	libtcod.console_clear(game.panel)
	game.message.delete()
	for y, (line, color, turn) in enumerate(game.message.log):
		new_color = libtcod.color_lerp(libtcod.darkest_grey, color, 1 - ((game.player.turns - turn) * 0.1))
		libtcod.console_set_default_foreground(game.panel, new_color)
		libtcod.console_print(game.panel, 0, y, line)
	libtcod.console_blit(game.panel, 0, 0, game.MESSAGE_WIDTH, game.MESSAGE_HEIGHT, 0, game.MESSAGE_X, game.MESSAGE_Y)


def render_player_stats_panel():
	render_bar(game.ps, 0, 5, game.PLAYER_STATS_WIDTH, 'HP', game.player.health, game.player.max_health, libtcod.red, libtcod.darker_red)
	render_bar(game.ps, 0, 6, game.PLAYER_STATS_WIDTH, 'MP', game.player.mana, game.player.max_mana, libtcod.blue, libtcod.darker_blue)
	libtcod.console_print(game.ps, 0, 0, game.player.name)
	libtcod.console_print(game.ps, 0, 1, game.player.race + " " + game.player.profession)
	libtcod.console_print(game.ps, 0, 3, game.current_map.location_abbr + '-' + str(game.current_map.location_level))
	libtcod.console_print(game.ps, 0, 8, "LV: " + str(game.player.level))
	libtcod.console_print(game.ps, 0, 9, "XP: " + str(game.player.xp))
	libtcod.console_print(game.ps, 0, 10, "Str: " + str(game.player.strength) + ' ')
	libtcod.console_print(game.ps, 0, 11, "Dex: " + str(game.player.dexterity) + ' ')
	libtcod.console_print(game.ps, 0, 12, "Int: " + str(game.player.intelligence) + ' ')
	libtcod.console_print(game.ps, 0, 13, "Wis: " + str(game.player.wisdom) + ' ')
	libtcod.console_print(game.ps, 0, 14, "End: " + str(game.player.endurance) + ' ')
	libtcod.console_print(game.ps, 0, 15, "Karma: " + str(game.player.karma) + ' ')
	libtcod.console_print(game.ps, 0, 17, "Turns: " + str(game.player.turns) + ' ')
	libtcod.console_blit(game.ps, 0, 0, game.PLAYER_STATS_WIDTH, game.PLAYER_STATS_HEIGHT, 0, game.PLAYER_STATS_X, game.PLAYER_STATS_Y)


def render_damage_animations():
	for i, (obj, line, color, turn) in enumerate(reversed(game.hp_anim)):
		new_color = libtcod.color_lerp(libtcod.black, color, 1 - ((turn / 30) * 0.2))
		libtcod.console_set_default_foreground(game.con, new_color)
		x, y = obj.x, obj.y
		libtcod.console_print_ex(game.con, x, y - (turn / 30), libtcod.BKGND_NONE, libtcod.CENTER, line)
		game.hp_anim[len(game.hp_anim) - i - 1] = (obj, line, color, turn + 1)
		if turn > 120:
			game.hp_anim.pop(len(game.hp_anim) - i - 1)


def render_all():
	# recompute FOV if needed (the player moved or something)
	libtcod.console_clear(game.con)
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
					libtcod.console_put_char_ex(game.con, x, y, game.current_map.tiles[x][y].icon, game.current_map.tiles[x][y].dark_color,  libtcod.black)
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
		if not libtcod.dijkstra_is_empty(game.path_dijk) and mouse_auto_move():
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
		if mx in range(0, game.MAP_WIDTH) and my in range(0, game.MAP_HEIGHT):
			game.path_dx = mx
			game.path_dy = my
			libtcod.console_set_char_background(game.con, game.path_dx, game.path_dy, libtcod.white, libtcod.BKGND_SET)
			if game.current_map.explored[mx][my] and not game.current_map.tiles[mx][my].blocked:
				if game.mouse.lbutton_pressed:
					if mouse_auto_move():
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
	render_damage_animations()
	libtcod.console_blit(game.con, 0, 0, game.MAP_WIDTH, game.MAP_HEIGHT, 0, game.MAP_X, game.MAP_Y)
