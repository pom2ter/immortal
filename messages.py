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
			if game.player.turns - turn > 10:
				self.log.remove((line, color, turn))

	# add a new message to the queue
	def new(self, new_msg, turn, color=libtcod.white):
		#split the message if necessary, among multiple lines
		new_msg_lines = textwrap.wrap(new_msg, game.MESSAGE_WIDTH)

		for line in new_msg_lines:
			#if the buffer is full, remove the first line to make room for the new one
			if len(self.log) == game.MESSAGE_HEIGHT:
				del self.log[0]

			#add the new line as a tuple, with the text and the color
			self.log.append((line, color, turn))
		util.render_message_panel()


# main function for the text box
def box(header, footer, startx, starty, width, height, contents, default=0, input=True, color=libtcod.green, align=libtcod.LEFT, nokeypress=False):
	box = libtcod.console_new(width, height)
	if color != None:
		box_gui(box, 0, 0, width, height, header, color)
	if header != None:
		libtcod.console_set_default_foreground(box, libtcod.black)
		libtcod.console_set_default_background(box, color)
		libtcod.console_print_ex(box, width / 2, 0, libtcod.BKGND_SET, libtcod.CENTER, ' ' + header + ' ')
	libtcod.console_set_default_foreground(box, color)
	libtcod.console_set_default_background(box, libtcod.black)
	if footer != None:
		libtcod.console_print_ex(box, width / 2, height - 1, libtcod.BKGND_SET, libtcod.CENTER, '[ ' + footer + ' ]')
	libtcod.console_set_default_foreground(box, libtcod.white)
	if input:
		choice = box_options(box, startx, starty, width - 2, height - 2, contents, default)
	else:
		for i, line in enumerate(contents):
			if align == libtcod.LEFT:
				libtcod.console_print_ex(box, 2, 2 + i, libtcod.BKGND_SET, libtcod.LEFT, line)
			if align == libtcod.CENTER:
				libtcod.console_print_ex(box, width / 2, 2 + i, libtcod.BKGND_SET, libtcod.CENTER, line)
		libtcod.console_blit(box, 0, 0, width, height, 0, startx, starty, 1.0, 0.9)
		libtcod.console_flush()
		if not nokeypress:
			libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS, libtcod.Key(), libtcod.Mouse(), True)
		choice = default
	return choice


# outline of the text box
def box_gui(con, x1, y1, x2, y2, header=None, color=libtcod.green):
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


# output options in the text box
def box_options(con, posx, posy, width, height, options, default=0):
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
			libtcod.console_rect(con, 1, y + 1, width, 1, True, libtcod.BKGND_SET)
			libtcod.console_print_ex(con, 2, y + 1, libtcod.BKGND_SET, libtcod.LEFT, options[y])

		libtcod.console_blit(con, 0, 0, width + 2, height + 2, 0, posx, posy, 1.0, 0.9)
		libtcod.console_flush()

		(mx, my) = (mouse.cx, mouse.cy)
		if my in range(posy + 1, height + posy + 1) and mx in range(posx + 1, width + posx + 1):
			mpos = my - posy - 1
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
		elif key.vk == libtcod.KEY_ESCAPE and ev == libtcod.EVENT_KEY_PRESS:
			current = -1
			choice = -1
		elif (key.vk == libtcod.KEY_ENTER and ev == libtcod.EVENT_KEY_PRESS) or (mouse.lbutton_pressed and my in range(posy + 1, height + posy + 1) and mx in range(posx + 1, width + posx + 1) and (my - posy - 1) <= len(options) - 1):
			choice = True
	return current


# waits for player input
def input(typ, con, posx, posy, con2=None):
	command = ''
	x = 0
	done = False
	key = libtcod.Key()
	while done == False:
		libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS, key, libtcod.Mouse(), True)
		if key.vk == libtcod.KEY_BACKSPACE and x > 0:
			libtcod.console_set_char(con, x + posx - 1, posy, chr(95))
			libtcod.console_set_char_foreground(con, x + posx - 1, posy, libtcod.white)
			libtcod.console_set_char(con, x + posx, posy, ' ')
			command = command[:-1]
			x -= 1
		elif key.vk == libtcod.KEY_ENTER:
			if not len(command) in range(3, 17):
#				util.msg_box('text', 'Error', contents='Names must be between 3 to 16 characters!', center=True, box_width=50, box_height=5)
				contents = ['Names must be between 3 to 16 characters!']
				game.messages.box('Error', None, (game.SCREEN_WIDTH - (len(max(contents, key=len)) + 20)) / 2, (game.SCREEN_HEIGHT - (len(contents) + 4)) / 2, len(max(contents, key=len)) + 20, len(contents) + 4, contents, input=False, align=libtcod.CENTER)
			elif command.lower() in game.savefiles:
#				util.msg_box('text', 'Error', contents='Name already exist!', center=True, box_width=50, box_height=5)
				contents = ['Name already exist!']
				game.messages.box('Error', None, (game.SCREEN_WIDTH - (len(max(contents, key=len)) + 20)) / 2, (game.SCREEN_HEIGHT - (len(contents) + 4)) / 2, len(max(contents, key=len)) + 20, len(contents) + 4, contents, input=False, align=libtcod.CENTER)
			else:
				done = True
		elif key.c in range(32, 127) and len(command) < 16:
			letter = chr(key.c)
			libtcod.console_set_char(con, x + posx, posy, letter)  # print new character at appropriate position on screen
			libtcod.console_set_char_foreground(con, x + posx, posy, libtcod.light_red)
			libtcod.console_set_char(con, x + posx + 1, posy, chr(95))
			libtcod.console_set_char_foreground(con, x + posx + 1, posy, libtcod.white)
			command += letter  # add to the string
			x += 1

		libtcod.console_blit(con, 0, 0, game.SCREEN_WIDTH - 35, game.SCREEN_HEIGHT, 0, 0, 0)
		if not con2 == None:
			libtcod.console_blit(con2, 0, 0, 35, game.SCREEN_HEIGHT, 0, game.SCREEN_WIDTH - 35, 0)
		libtcod.console_flush()
	return command
