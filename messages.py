import libtcodpy as libtcod
import textwrap
import game


class Message(object):
	def __init__(self):
		self.log = []
		self.history = []

	def new(self, new_msg, color=libtcod.white):
		#split the message if necessary, among multiple lines
		new_msg_lines = textwrap.wrap(new_msg, game.MSG_WIDTH)

		for line in new_msg_lines:
			#if the buffer is full, remove the first line to make room for the new one
			if len(self.log) == game.MSG_HEIGHT:
				del self.log[0]

			#add the new line as a tuple, with the text and the color
			self.log.append((line, color))

	def input(self, con, posx, posy):
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
