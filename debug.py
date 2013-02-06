import libtcodpy as libtcod
import game


class Debug(object):
	def __init__(self):
		self.enable = True

	def edit_attribute(self, stat):
		libtcod.console_print(0, game.PLAYER_STATS_WIDTH + 2, 1, stat)
		libtcod.console_flush()
		choice = game.messages.input('', 0, game.PLAYER_STATS_WIDTH + len(stat) + 1, 1)
		if choice.isdigit():
			return int(choice)

	def menu(self):
		if self.enable:
			contents = ['Edit strength stat', 'Edit dexterity stat', 'Edit intelligence stat', 'Edit wisdom stat', 'Edit endurance stat', 'Edit karma stat', 'Full health', 'Full mana']
			choice = game.messages.box('Debug Menu', None, game.PLAYER_STATS_WIDTH + (((game.MAP_WIDTH + 3) - (len(max(contents, key=len)) + 4)) / 2), ((game.MAP_HEIGHT + 1) - (len(contents) + 2)) / 2, len(max(contents, key=len)) + 4, len(contents) + 2, contents, mouse_exit=True)
			if choice == 0:
				game.player.strength = self.edit_attribute('Strength: _')
			if choice == 1:
				game.player.dexterity = self.edit_attribute('Dexterity: _')
			if choice == 2:
				game.player.intelligence = self.edit_attribute('Intelligence: _')
			if choice == 3:
				game.player.wisdom = self.edit_attribute('Wisdom: _')
			if choice == 4:
				game.player.endurance = self.edit_attribute('Endurance: _')
			if choice == 5:
				game.player.karma = self.edit_attribute('Karma: _')
			if choice == 6:
				game.player.heal_health(1000)
			if choice == 7:
				game.player.heal_mana(1000)
			game.redraw_gui = True
