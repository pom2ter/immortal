import libtcodpy as libtcod
import textwrap
import game
import util


class Message(object):
	def __init__(self):
		self.log = []
		self.history = []

	def delete(self):
		#remove old messages if needed
		for (line, color, turn) in reversed(self.log):
			if game.player.turns - turn > 10:
				self.log.remove((line, color, turn))

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


def box(header, footer, startx, starty, width, height, contents, color=libtcod.green):
	box = libtcod.console_new(width, height)
	if color != None:
		util.text_box(box, 0, 0, width, height, header, color)
	libtcod.console_set_default_foreground(box, color)
	libtcod.console_set_default_background(box, libtcod.black)
	if footer != None:
		libtcod.console_print_ex(box, width / 2, height - 1, libtcod.BKGND_SET, libtcod.CENTER, '[ ' + footer + ' ]')
	libtcod.console_set_default_foreground(box, libtcod.white)
	choice = box_choices(box, startx, starty, width - 2, height - 2, contents)
	return choice


def box_choices(con, posx, posy, width, height, options):
	choice = False
	current = 0
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
				util.msg_box('text', 'Error', contents='Names must be between 3 to 16 characters!', center=True, box_width=50, box_height=5)
			elif command.lower() in game.savefiles:
				util.msg_box('text', 'Error', contents='Name already exist!', center=True, box_width=50, box_height=5)
			else:
				done = True
		elif key.c in range(32, 127) and len(command) < 16:
			letter = chr(key.c)
			libtcod.console_set_char(con, x + posx, posy, letter)  # print new character at appropriate position on screen
			libtcod.console_set_char_foreground(con, x + posx, posy, libtcod.light_red)  # make it white or something
			libtcod.console_set_char(con, x + posx + 1, posy, chr(95))
			libtcod.console_set_char_foreground(con, x + posx + 1, posy, libtcod.white)
			command += letter  # add to the string
			x += 1

		libtcod.console_blit(con, 0, 0, game.SCREEN_WIDTH - 35, game.SCREEN_HEIGHT, 0, 0, 0)
		if not con2 == None:
			libtcod.console_blit(con2, 0, 0, 35, game.SCREEN_HEIGHT, 0, game.SCREEN_WIDTH - 35, 0)
		libtcod.console_flush()
	return command
