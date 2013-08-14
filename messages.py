import libtcodpy as libtcod
import textwrap
import game
import util


class Message(object):
	def __init__(self):
		self.log = []
		self.history = []

	# remove old messages if needed
	def delete(self):
		for (line, color, turn) in reversed(self.log):
			if game.turns - turn > 10:
				self.log.remove((line, color, turn))

	# delete message log history
	def delete_history(self):
		self.history = []

	# empty message log
	def empty(self):
		self.log = []

	# add a new message to the queue
	def new(self, new_msg, turn, color=libtcod.white):
		#split the message if necessary, among multiple lines
		new_msg_lines = textwrap.wrap(new_msg, game.MESSAGE_WIDTH - 2)

		for line in new_msg_lines:
			#if the buffer is full, remove the first line to make room for the new one
			if len(self.log) == 15:  # game.MESSAGE_HEIGHT:
				del self.log[0]

			#add the new line as a tuple, with the text and the color
			self.log.append((line, color, turn))
			if len(self.history) == game.setting_history:
				del self.history[0]
			self.history.append((line, color, turn))
		game.old_msg = 0
		util.render_message_panel()

	# trim history after changing the size in the settings
	def trim_history(self):
		if len(self.history) > game.setting_history:
			self.history = self.history[(len(self.history) - game.setting_history):]


# main function for the text box
def box(header, footer, startx, starty, width, height, contents, default=0, input=True, color=libtcod.green, align=libtcod.LEFT, nokeypress=False, inv=False, step=1, mouse_exit=False):
	box = libtcod.console_new(width, height)
	if startx == 'center_screenx':
		startx = (game.SCREEN_WIDTH - (len(max(contents, key=len)) + 16)) / 2
	if startx == 'center_mapx':
		startx = game.PLAYER_STATS_WIDTH + ((game.MAP_WIDTH - (width - 4)) / 2)
	if starty == 'center_screeny':
		starty = (game.SCREEN_HEIGHT - (len(contents) + 4)) / 2
	if starty == 'center_mapy':
		starty = ((game.MAP_HEIGHT + 2) - height) / 2
	if color is not None:
		box_gui(box, 0, 0, width, height, color)
	if header is not None:
		libtcod.console_set_default_foreground(box, libtcod.black)
		libtcod.console_set_default_background(box, color)
		libtcod.console_print_ex(box, width / 2, 0, libtcod.BKGND_SET, libtcod.CENTER, ' ' + header + ' ')
	libtcod.console_set_default_foreground(box, color)
	libtcod.console_set_default_background(box, libtcod.black)
	if footer is not None:
		libtcod.console_print_ex(box, width / 2, height - 1, libtcod.BKGND_SET, libtcod.CENTER, '[ ' + footer + ' ]')
	if mouse_exit:
		libtcod.console_print_ex(box, width - 5, 0, libtcod.BKGND_SET, libtcod.LEFT, '[x]')
	libtcod.console_set_default_foreground(box, libtcod.white)

	if input:
		choice = box_options(box, startx, starty, width - 2, height - 2, contents, default, inv, step, mouse_exit, align)
	else:
		for i, line in enumerate(contents):
			if align == libtcod.LEFT:
				libtcod.console_print_ex(box, 2, 2 + i, libtcod.BKGND_SET, libtcod.LEFT, line)
			if align == libtcod.RIGHT:
				libtcod.console_print_ex(box, width - 2, 2 + i, libtcod.BKGND_SET, libtcod.RIGHT, line)
			if align == libtcod.CENTER:
				libtcod.console_print_ex(box, width / 2, 2 + i, libtcod.BKGND_SET, libtcod.CENTER, line)
		libtcod.console_blit(box, 0, 0, width, height, 0, startx, starty, 1.0, 0.9)
		libtcod.console_flush()
		if not nokeypress:
			libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS, libtcod.Key(), libtcod.Mouse(), True)
		choice = default
	libtcod.console_delete(box)
	return choice


# outline of the text box
def box_gui(con, x1, y1, x2, y2, color=libtcod.green, lines=None):
	buffer = libtcod.ConsoleBuffer(x2 - x1, y2 - y1)
	for i in range(x1, x2):
		buffer.set_fore(i, y1, color.r, color.g, color.b, chr(205))
		buffer.set_fore(i, y2 - 1, color.r, color.g, color.b, chr(205))
	for i in range(y1, y2):
		buffer.set_fore(x1, i, color.r, color.g, color.b, chr(186))
		buffer.set_fore(x2 - 1, i, color.r, color.g, color.b, chr(186))

	if lines is not None:
		for i in lines:
			if i['dir'] == 'h':
				for x in range(i['x'], x2):
					buffer.set_fore(x, i['y'], color.r, color.g, color.b, chr(205))
				buffer.set_back(i['x'], i['y'], color.r, color.g, color.b)
				buffer.set_back(x2 - 1, i['y'], color.r, color.g, color.b)
			if i['dir'] == 'v':
				for y in range(i['y'], y2):
					buffer.set_fore(i['x'], y, color.r, color.g, color.b, chr(186))
				buffer.set_back(i['x'], i['y'], color.r, color.g, color.b)
				buffer.set_back(i['x'], y2 - 1, color.r, color.g, color.b)

	buffer.set_back(x1, y1, color.r, color.g, color.b)
	buffer.set_back(x1, y2 - 1, color.r, color.g, color.b)
	buffer.set_back(x2 - 1, y1, color.r, color.g, color.b)
	buffer.set_back(x2 - 1, y2 - 1, color.r, color.g, color.b)
	buffer.blit(con, fill_fore=True, fill_back=True)


# output options in the text box
def box_options(con, posx, posy, width, height, options, default, inv, step, mouse_exit, align):
	choice = False
	current = default
	key = libtcod.Key()
	mouse = libtcod.Mouse()
	lerp = 1.0
	descending = True

	while not choice:
		ev = libtcod.sys_check_for_event(libtcod.EVENT_ANY, key, mouse)
		libtcod.console_set_default_foreground(con, libtcod.grey)
		libtcod.console_set_default_background(con, libtcod.black)
		libtcod.console_rect(con, 1, 1, width, height, True, libtcod.BKGND_SET)

		for y in range(len(options)):
			if y == current:
				libtcod.console_set_default_foreground(con, libtcod.white)
				color, lerp, descending = util.color_lerp(lerp, descending)
				libtcod.console_set_default_background(con, color)
			else:
				libtcod.console_set_default_foreground(con, libtcod.grey)
				libtcod.console_set_default_background(con, libtcod.black)
			if inv:
				text_left, text_right = util.inventory_output(options[y])
			else:
				text_left = options[y]
				text_right = ''
			libtcod.console_rect(con, step, y + step, width - ((step - 1) * 2), 1, True, libtcod.BKGND_SET)
			if align == libtcod.LEFT:
				libtcod.console_print_ex(con, 1 + step, y + step, libtcod.BKGND_SET, libtcod.LEFT, text_left)
			if align == libtcod.RIGHT:
				libtcod.console_print_ex(con, width - 1 + step, y + step, libtcod.BKGND_SET, libtcod.RIGHT, text_left)
			libtcod.console_print_ex(con, width - step, y + step, libtcod.BKGND_SET, libtcod.RIGHT, text_right)

		libtcod.console_blit(con, 0, 0, width + 2, height + 2, 0, posx, posy, 1.0, 0.9)
		libtcod.console_flush()

		(mx, my) = (mouse.cx, mouse.cy)
		if my in range(posy + step, height + posy + step) and mx in range(posx + step, width + posx + 2 - step):
			mpos = my - posy - step
			if mpos <= len(options) - 1:
				current = mpos

		if key.vk == libtcod.KEY_DOWN and ev == libtcod.EVENT_KEY_PRESS:
			current = (current + 1) % len(options)
			lerp = 1.0
			descending = True
		elif key.vk == libtcod.KEY_UP and ev == libtcod.EVENT_KEY_PRESS:
			current = (current - 1) % len(options)
			lerp = 1.0
			descending = True
		elif (key.vk == libtcod.KEY_ESCAPE and ev == libtcod.EVENT_KEY_PRESS) or (mouse_exit and mouse.lbutton_pressed and mx == width + posx - 2 and my == posy):
			current = -1
			choice = -1
		elif (key.vk == libtcod.KEY_ENTER and ev == libtcod.EVENT_KEY_PRESS) or (mouse.lbutton_pressed and my in range(posy + step, height + posy + step) and mx in range(posx + step, width + posx + 2 - step) and (my - posy - step) <= len(options) - 1):
			choice = True
	return current


# waits for player input
def input(typ, con, posx, posy, min=0, max=100):
	command = ''
	x = 0
	done = False
	key = libtcod.Key()
	while done is False:
		libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS, key, libtcod.Mouse(), True)
		if key.vk == libtcod.KEY_BACKSPACE and x > 0:
			libtcod.console_set_char(con, x + posx - 1, posy, chr(95))
			libtcod.console_set_char_foreground(con, x + posx - 1, posy, libtcod.white)
			libtcod.console_set_char(con, x + posx, posy, ' ')
			command = command[:-1]
			x -= 1
		elif key.vk == libtcod.KEY_ENTER:
			if not len(command) in range(min, max):
				libtcod.console_set_default_foreground(0, libtcod.dark_red)
				libtcod.console_print(con, 2, posy + 2, 'Player name must be between ' + str(min) + ' to ' + str(max - 1) + ' characters!')
			elif typ == 'chargen':
				if command.lower() in game.savefiles:
					libtcod.console_set_default_foreground(0, libtcod.dark_red)
					libtcod.console_rect(con, 2, posy + 2, 50, 1, True)
					libtcod.console_print(con, 2, posy + 2, 'That name already exist!')
				else:
					done = True
			else:
				done = True
		elif key.c in range(32, 127) and len(command) < 16:
			libtcod.console_set_char(con, x + posx, posy, chr(key.c))  # print new character at appropriate position on screen
			libtcod.console_set_char_foreground(con, x + posx, posy, libtcod.light_red)
			libtcod.console_set_char(con, x + posx + 1, posy, chr(95))
			libtcod.console_set_char_foreground(con, x + posx + 1, posy, libtcod.white)
			command += chr(key.c)  # add to the string
			x += 1

		libtcod.console_blit(con, 0, 0, game.SCREEN_WIDTH, game.SCREEN_HEIGHT, 0, 0, 0)
		libtcod.console_flush()
	return command
