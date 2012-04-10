import libtcodpy as libtcod
import textwrap
import game
import util


class Message(object):
	def __init__(self):
		self.log = []
		self.history = []

	def new(self, new_msg, turn, color=libtcod.white):
		#split the message if necessary, among multiple lines
		new_msg_lines = textwrap.wrap(new_msg, game.MESSAGE_WIDTH)

		for line in new_msg_lines:
			#if the buffer is full, remove the first line to make room for the new one
			if len(self.log) == game.MESSAGE_HEIGHT:
				del self.log[0]

			#add the new line as a tuple, with the text and the color
			self.log.append((line, color, turn))

	def input(self, typ, con, posx, posy, con2=None):
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

	def delete(self):
		#remove old messages if needed
		for (line, color, turn) in reversed(self.log):
			if game.player.turns - turn > 10:
				self.log.remove((line, color, turn))
