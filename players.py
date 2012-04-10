import libtcodpy as libtcod
import game
from messages import *

RACES = ["Human", "Elf", "Dwarf", "Halfling"]
CLASSES = ["Fighter", "Rogue", "Priest", "Mage"]
GENDER = ["Male", "Female"]
BASE_STATS = [[9, 9, 8, 9, 9], [12, 9, 6, 11, 8], [10, 12, 7, 8, 9], [9, 8, 10, 10, 9], [7, 10, 12, 8, 9],
				[7, 9, 10, 8, 10], [10, 9, 8, 10, 9], [8, 12, 9, 7, 10], [7, 8, 12, 9, 10], [5, 10, 14, 7, 10],
				[11, 7, 6, 12, 8], [14, 7, 4, 14, 7], [12, 10, 5, 11, 8], [11, 6, 8, 13, 8], [9, 8, 10, 11, 8],
				[8, 10, 7, 9, 10], [11, 10, 5, 11, 9], [9, 13, 6, 8, 10], [8, 9, 9, 10, 10], [6, 11, 11, 8, 10],
				]


def create_character():
	cancel = False
	key = libtcod.Key()
	while not cancel:
		cs_width = game.SCREEN_WIDTH - 35
		cs = libtcod.console_new(cs_width, game.SCREEN_HEIGHT)
		stats = libtcod.console_new(35, game.SCREEN_HEIGHT)
		show_stats(stats, "")

		libtcod.console_print(cs, 0, 0, 'CHARACTER GENERATION')
		libtcod.console_print(cs, 0, 2, 'Enter a name for your character: _' + game.player.name)
		libtcod.console_blit(cs, 0, 0, cs_width, game.SCREEN_HEIGHT, 0, 0, 0)
		libtcod.console_flush()

		game.player.name = game.message.input('chargen', cs, 33, 2, stats)
		show_stats(stats, "")
		libtcod.console_rect(cs, 0, 2, cs_width, game.SCREEN_HEIGHT, True, libtcod.BKGND_SET)
		libtcod.console_print(cs, 0, 2, 'Select a gender:')
		libtcod.console_print(cs, 0, 4, '1) Male')
		libtcod.console_print(cs, 0, 5, '2) Female')
		libtcod.console_blit(cs, 0, 0, cs_width, game.SCREEN_HEIGHT, 0, 0, 0)
		libtcod.console_flush()

		gender_choice = False
		while not gender_choice:
			libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS, key, libtcod.Mouse(), True)
			index = key.c - ord('1')
			if index >= 0 and index < len(GENDER):
				game.player.gender = GENDER[index]
				gender_choice = True

		show_stats(stats, game.player.gender, 0)
		libtcod.console_rect(cs, 0, 2, cs_width, game.SCREEN_HEIGHT, True, libtcod.BKGND_SET)
		libtcod.console_print(cs, 0, 2, 'Select a race:')
		libtcod.console_print(cs, 15, 3, 'Modifiers')
		libtcod.console_print(cs, 0, 4, '1) Human       None')
		libtcod.console_print(cs, 0, 5, '2) Elf         +2 Int, +1 Luck, -2 Str, -1 End')
		libtcod.console_print(cs, 0, 6, '3) Dwarf       +2 Str, +3 End, -2 Int, -2 Dex, -1 Luck')
		libtcod.console_print(cs, 0, 7, '4) Halfling    +1 Dex, +1 Luck, -1 Int, -1 Str')
		libtcod.console_blit(cs, 0, 0, cs_width, game.SCREEN_HEIGHT, 0, 0, 0)
		libtcod.console_flush()

		race_choice = False
		while not race_choice:
			libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS, key, libtcod.Mouse(), True)
			index = key.c - ord('1')
			if index >= 0 and index < len(RACES):
				game.player.race = RACES[index]
				race_choice = True

		show_stats(stats, game.player.gender + " " + game.player.race, index * 5)
		libtcod.console_rect(cs, 0, 2, cs_width, game.SCREEN_HEIGHT, True, libtcod.BKGND_SET)
		libtcod.console_print(cs, 0, 2, 'Select a class:')
		libtcod.console_print(cs, 15, 3, 'Modifiers')
		libtcod.console_print(cs, 0, 4, '1) Fighter     +3 Str, +2 End, -2 Int, -1 Luck')
		libtcod.console_print(cs, 0, 5, '2) Rogue       +3 Dex, +1 Str, -1 Int, -1 End')
		libtcod.console_print(cs, 0, 6, '3) Priest      +2 Int, +1 End, -1 Dex')
		libtcod.console_print(cs, 0, 7, '4) Mage        +4 Int, +1 Dex, -2 Str, -1 End')
		libtcod.console_blit(cs, 0, 0, cs_width, game.SCREEN_HEIGHT, 0, 0, 0)
		libtcod.console_flush()

		class_choice = False
		while not class_choice:
			libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS, key, libtcod.Mouse(), True)
			indexr = key.c - ord('1')
			if indexr >= 0 and indexr < len(CLASSES):
				game.player.profession = CLASSES[indexr]
				class_choice = True

		show_stats(stats, game.player.gender + " " + game.player.race + " " + game.player.profession, (index * 5) + indexr + 1, 0)
		libtcod.console_print(cs, 0, 11, '(r)eroll')
		libtcod.console_print(cs, 0, 12, '(k)eep character and start game')
		libtcod.console_print(cs, 0, 13, '(c)ancel and restart')
		libtcod.console_print(cs, 0, 14, '<ESC> Return to main menu')
		libtcod.console_blit(cs, 0, 0, cs_width, game.SCREEN_HEIGHT, 0, 0, 0)
		libtcod.console_flush()

		final_choice = False
		while not final_choice:
			libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS, key, libtcod.Mouse(), True)
			if key.vk == libtcod.KEY_ESCAPE:
				final_choice = True
				return "quit"
			if chr(key.c) == 'r':
				show_stats(stats, game.player.gender + " " + game.player.race + " " + game.player.profession, (index * 5) + indexr + 1, 0)
			if chr(key.c) == 'k':
				final_choice = True
				return "playing"
			if chr(key.c) == 'c':
				game.player.name = ""
				final_choice = True


def show_stats(stats, text, attr=-1, roll=-1):
	libtcod.console_set_default_foreground(stats, libtcod.light_red)
	libtcod.console_print(stats, 2, 1, game.player.name)
	libtcod.console_set_default_foreground(stats, libtcod.light_yellow)
	libtcod.console_print(stats, 2, 2, text)
	libtcod.console_set_default_foreground(stats, libtcod.white)
	libtcod.console_print(stats, 16, 4, 'Base  Bonus  Total')
	libtcod.console_print(stats, 2, 5, 'Strength:      ')
	libtcod.console_print(stats, 2, 6, 'Dexterity:     ')
	libtcod.console_print(stats, 2, 7, 'Intelligence:  ')
	libtcod.console_print(stats, 2, 8, 'Endurance:     ')
	libtcod.console_print(stats, 2, 9, 'Luck:          ')

	if not attr == -1:
		for i in range(0, 5):
			libtcod.console_print(stats, 17, i + 5, str(BASE_STATS[attr][i]))

	if not roll == -1:
		stat = []
		libtcod.random_get_instance()
		stat.append(libtcod.random_get_int(0, 0, 8))
		stat.append(libtcod.random_get_int(0, 0, 8))
		stat.append(libtcod.random_get_int(0, 0, 8))
		stat.append(libtcod.random_get_int(0, 0, 8))
		stat.append(libtcod.random_get_int(0, 0, 8))
		for i in range(0, 5):
			libtcod.console_print(stats, 24, i + 5, str(stat[i]) + ' ')
			libtcod.console_print(stats, 30, i + 5, str(BASE_STATS[attr][i] + stat[i]) + ' ')
		game.player.strength = BASE_STATS[attr][0] + stat[0]
		game.player.dexterity = BASE_STATS[attr][1] + stat[1]
		game.player.intelligence = BASE_STATS[attr][2] + stat[2]
		game.player.endurance = BASE_STATS[attr][3] + stat[3]
		game.player.luck = BASE_STATS[attr][4] + stat[4]
		game.player.gold = libtcod.random_get_int(0, 1, 50)

	for i in range(0, game.SCREEN_HEIGHT):
		libtcod.console_print(stats, 0, i, chr(179))
	libtcod.console_blit(stats, 0, 0, 35, game.SCREEN_HEIGHT, 0, game.SCREEN_WIDTH - 35, 0)
	libtcod.console_flush()


class Player(object):
	def __init__(self):
		self.name = ""
		self.race = RACES[0]
		self.gender = GENDER[0]
		self.profession = CLASSES[0]
		self.strength = 9
		self.dexterity = 9
		self.intelligence = 8
		self.endurance = 9
		self.luck = 9
		self.icon = '@'
		self.icon_color = libtcod.white
		self.level = 1
		self.xp = 0
		self.health = 2
		self.max_health = 12
		self.mana = 2
		self.max_mana = 2
		self.inventory = []
		self.equipment = []
		self.turns = 0
		self.gold = 0

	def add_turn(self):
		self.turns += 1

	def equip(self, item):
		self.equipment.append(self.inventory[item])
		self.add_turn()
		game.message.new("You equip the " + self.inventory[item].unidentified_name, self.turns, libtcod.green)
		self.inventory.pop(item)

	def unequip(self, item):
		self.inventory.append(self.equipment[item])
		self.add_turn()
		game.message.new("You unequip the " + self.equipment[item].unidentified_name, self.turns, libtcod.green)
		self.equipment.pop(item)
