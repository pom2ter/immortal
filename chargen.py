import libtcodpy as libtcod
import game
import util


#######################################
# character generation functions
#######################################

# output races and classes description during character generation
def character_description(typ, id):
	libtcod.console_set_default_foreground(0, libtcod.white)
	libtcod.console_set_default_background(0, libtcod.black)
	libtcod.console_rect(0, 1, 11, 52, 10, True, libtcod.BKGND_SET)
	if typ == 'race':
		libtcod.console_print_rect(0, 2, 12, 50, 10, game.RACE_DESC[id])
	if typ == 'class':
		libtcod.console_print_rect(0, 2, 12, 50, 10, game.CLASS_DESC[id])


# output all options during character generation
def chargen_options(posx, posy, width, options, typ):
	choice = False
	current = 0
	key = libtcod.Key()
	mouse = libtcod.Mouse()
	lerp = 1.0
	descending = True

	while not choice:
		if typ == 'race':
			character_description('race', current)
		if typ == 'class':
			character_description('class', current)
		ev = libtcod.sys_check_for_event(libtcod.EVENT_ANY, key, mouse)
		libtcod.console_set_default_foreground(0, libtcod.grey)
		libtcod.console_set_default_background(0, libtcod.black)

		for y in range(len(options)):
			if y == current:
				libtcod.console_set_default_foreground(0, libtcod.white)
				color, lerp, descending = util.color_lerp(lerp, descending)
				libtcod.console_set_default_background(0, color)
			else:
				libtcod.console_set_default_foreground(0, libtcod.grey)
				libtcod.console_set_default_background(0, libtcod.black)
			libtcod.console_rect(0, posx, y + posy, width, 1, True, libtcod.BKGND_SET)
			libtcod.console_print_ex(0, posx + 2, y + posy, libtcod.BKGND_SET, libtcod.LEFT, options[y])
		libtcod.console_flush()

		if key.vk == libtcod.KEY_DOWN and ev == libtcod.EVENT_KEY_PRESS:
			current = (current + 1) % len(options)
			lerp = 1.0
			descending = True
		elif key.vk == libtcod.KEY_UP and ev == libtcod.EVENT_KEY_PRESS:
			current = (current - 1) % len(options)
			lerp = 1.0
			descending = True
		elif key.vk == libtcod.KEY_ENTER and ev == libtcod.EVENT_KEY_PRESS:
			choice = True
	return current


# main function for character generation
def create_character():
	cancel = False
	cs_width = 55
	cs_height = game.SCREEN_HEIGHT - 4
	cs = libtcod.console_new(cs_width, cs_height)
	stats = libtcod.console_new(34, cs_height)
	while not cancel:
		game.messages.box_gui(0, 0, 0, game.SCREEN_WIDTH, game.SCREEN_HEIGHT, color=libtcod.Color(245, 222, 179), lines=[{'dir': 'h', 'x': 0, 'y': 2}, {'dir': 'v', 'x': game.SCREEN_WIDTH - 36, 'y': 2}])
		libtcod.console_set_default_foreground(0, libtcod.white)
		libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 1, libtcod.BKGND_NONE, libtcod.CENTER, 'CHARACTER GENERATION')
		show_stats_panel(stats)
		libtcod.console_print(0, 2, 4, 'Enter a name for your character: _')
		libtcod.console_flush()

		game.player.name = game.messages.input('chargen', 0, 35, 4, min=3, max=17)
		show_stats_panel(stats)
		libtcod.console_clear(cs)
		libtcod.console_print(cs, 1, 1, 'Select a gender:')
		libtcod.console_blit(cs, 0, 0, cs_width, cs_height, 0, 1, 3)
		game.player.gender = game.GENDER[chargen_options(2, 6, 10, game.GENDER, None)]

		show_stats_panel(stats, 0)
		libtcod.console_clear(cs)
		libtcod.console_print(cs, 1, 1, 'Select a race:')
		libtcod.console_print(cs, 16, 2, 'Modifiers')
		libtcod.console_print(cs, 16, 3, 'None')
		libtcod.console_print(cs, 16, 4, '+2 Int, +1 Wis, -2 Str, -1 End')
		libtcod.console_print(cs, 16, 5, '+2 Str, +3 End, -2 Dex, -2 Int, -1 Wis')
		libtcod.console_print(cs, 16, 6, '+1 Dex, +1 Int, -1 Str, -1 Wis')
		libtcod.console_blit(cs, 0, 0, cs_width, cs_height, 0, 1, 3)
		index = chargen_options(2, 6, 12, game.RACES, 'race')
		game.player.race = game.RACES[index]

		show_stats_panel(stats, index * 6)
		libtcod.console_clear(cs)
		libtcod.console_print(cs, 1, 1, 'Select a class:')
		libtcod.console_print(cs, 16, 2, 'Modifiers')
		libtcod.console_print(cs, 16, 3, '+3 Str, +2 End, -2 Int, -1 Wis')
		libtcod.console_print(cs, 16, 4, '+3 Dex, +1 Str, -1 Int, -1 End')
		libtcod.console_print(cs, 16, 5, '+3 Wis, +1 Str, -1 Dex, -1 End')
		libtcod.console_print(cs, 16, 6, '+4 Int, +1 Wis, -2 Str, -1 End')
		libtcod.console_print(cs, 16, 7, 'None')
		libtcod.console_blit(cs, 0, 0, cs_width, cs_height, 0, 1, 3)
		indexr = chargen_options(2, 6, 12, game.CLASSES, 'class')
		game.player.profession = game.CLASSES[indexr]

		show_stats_panel(stats, (index * 6) + indexr + 1, 0)
		libtcod.console_clear(cs)
		libtcod.console_print(cs, 1, 1, 'Options:')
		libtcod.console_blit(cs, 0, 0, cs_width, cs_height, 0, 1, 3)
		final_choice = False
		while not final_choice:
			choice = chargen_options(2, 6, 33, ['Reroll stats', 'Keep character and start game', 'Cancel and restart', 'Return to main menu'], None)
			if choice == 0:
				show_stats_panel(stats, (index * 6) + indexr + 1, 0)
			if choice == 1:
				final_choice = True
				libtcod.console_delete(cs)
				libtcod.console_delete(stats)
				return 'playing'
			if choice == 2:
				game.player.name = ''
				game.player.gender = ''
				game.player.race = ''
				game.player.profession = ''
				final_choice = True
			if choice == 3:
				final_choice = True
				libtcod.console_delete(cs)
				libtcod.console_delete(stats)
				return 'quit'


# output the stats panel during character generation
def show_stats_panel(stats, attr=-1, roll=-1):
	libtcod.console_clear(stats)
	libtcod.console_set_default_foreground(stats, libtcod.light_red)
	libtcod.console_print(stats, 10, 1, game.player.name)
	libtcod.console_set_default_foreground(stats, libtcod.light_yellow)
	libtcod.console_print(stats, 10, 2, game.player.gender)
	libtcod.console_print(stats, 10, 3, game.player.race)
	libtcod.console_print(stats, 10, 4, game.player.profession)
	libtcod.console_set_default_foreground(stats, libtcod.white)
	libtcod.console_print(stats, 1, 1, 'Name   : ')
	libtcod.console_print(stats, 1, 2, 'Gender : ')
	libtcod.console_print(stats, 1, 3, 'Race   : ')
	libtcod.console_print(stats, 1, 4, 'Class  : ')
	libtcod.console_print(stats, 15, 7, 'Base  Bonus  Total')
	libtcod.console_print(stats, 1, 8, 'Strength:      ')
	libtcod.console_print(stats, 1, 9, 'Dexterity:     ')
	libtcod.console_print(stats, 1, 10, 'Intelligence:  ')
	libtcod.console_print(stats, 1, 11, 'Wisdom:        ')
	libtcod.console_print(stats, 1, 12, 'Endurance:     ')

	if not attr == -1:
		for i in range(5):
			libtcod.console_print_ex(stats, 17, i + 8, libtcod.BKGND_SET, libtcod.RIGHT, str(game.BASE_STATS[attr][i]))

	if not roll == -1:
		stat = []
		stat.append(libtcod.random_get_int(game.rnd, 0, 6))
		stat.append(libtcod.random_get_int(game.rnd, 0, 6))
		stat.append(libtcod.random_get_int(game.rnd, 0, 6))
		stat.append(libtcod.random_get_int(game.rnd, 0, 6))
		stat.append(libtcod.random_get_int(game.rnd, 0, 6))
		stat.append(libtcod.random_get_int(game.rnd, 0, 20))
		for i in range(5):
			libtcod.console_print(stats, 23, i + 8, str(stat[i]))
			libtcod.console_print_ex(stats, 30, i + 8, libtcod.BKGND_SET, libtcod.RIGHT, ' ' + str(game.BASE_STATS[attr][i] + stat[i]))
		game.player.base_strength = game.BASE_STATS[attr][0] + stat[0]
		game.player.base_dexterity = game.BASE_STATS[attr][1] + stat[1]
		game.player.base_intelligence = game.BASE_STATS[attr][2] + stat[2]
		game.player.base_wisdom = game.BASE_STATS[attr][3] + stat[3]
		game.player.base_endurance = game.BASE_STATS[attr][4] + stat[4]
		game.player.base_karma = stat[5]
		starting_stats()

	libtcod.console_blit(stats, 0, 0, 34, 20, 0, game.SCREEN_WIDTH - 35, 3)
	libtcod.console_flush()


# starting stats and equipment after character generation
def starting_stats():
	game.player.inventory = []
	game.player.money = util.roll_dice(1, 50)
	if game.player.profession == 'Fighter':
		game.player.base_health = libtcod.random_get_int(game.rnd, 2, game.FIGHTER_HP_GAIN)
		game.player.base_mana = libtcod.random_get_int(game.rnd, 2, game.FIGHTER_MP_GAIN)
		game.player.base_stamina = libtcod.random_get_int(game.rnd, 2, game.FIGHTER_STAMINA_GAIN)
		game.player.inventory.append(game.baseitems.create_item('uncursed ', '', 'short sword', '', 'identified'))
		game.player.inventory.append(game.baseitems.create_item('uncursed ', 'leather ', 'armor', '', 'identified'))
		game.player.skills[game.player.find_skill('Sword')].set_level(20)
		game.player.skills[game.player.find_skill('Axe')].set_level(20)
		game.player.skills[game.player.find_skill('Mace')].set_level(10)
		game.player.skills[game.player.find_skill('Dagger')].set_level(15)
		game.player.skills[game.player.find_skill('Polearm')].set_level(20)
		game.player.skills[game.player.find_skill('Hands')].set_level(5)

	if game.player.profession == 'Rogue':
		game.player.base_health = libtcod.random_get_int(game.rnd, 2, game.ROGUE_HP_GAIN)
		game.player.base_mana = libtcod.random_get_int(game.rnd, 2, game.ROGUE_MP_GAIN)
		game.player.base_stamina = libtcod.random_get_int(game.rnd, 2, game.ROGUE_STAMINA_GAIN)
		game.player.inventory.append(game.baseitems.create_item('uncursed ', '', 'dagger', '', 'identified'))
		game.player.inventory.append(game.baseitems.create_item('uncursed ', 'leather ', 'armor', '', 'identified'))
		game.player.skills[game.player.find_skill('Dagger')].set_level(20)
		game.player.skills[game.player.find_skill('Bow')].set_level(5)
		game.player.skills[game.player.find_skill('Missile')].set_level(5)
		game.player.skills[game.player.find_skill('Hands')].set_level(5)
		game.player.skills[game.player.find_skill('Detect Traps')].set_level(15)
		game.player.skills[game.player.find_skill('Disarm Traps')].set_level(15)
		game.player.skills[game.player.find_skill('Lockpicking')].set_level(15)

	if game.player.profession == 'Priest':
		game.player.base_health = libtcod.random_get_int(game.rnd, 2, game.PRIEST_HP_GAIN)
		game.player.base_mana = libtcod.random_get_int(game.rnd, 2, game.PRIEST_MP_GAIN)
		game.player.base_stamina = libtcod.random_get_int(game.rnd, 2, game.PRIEST_STAMINA_GAIN)
		game.player.inventory.append(game.baseitems.create_item('uncursed ', '', 'mace', '', 'identified'))
		game.player.inventory.append(game.baseitems.create_item('uncursed ', 'leather ', 'armor', '', 'identified'))
		game.player.skills[game.player.find_skill('Sword')].set_level(5)
		game.player.skills[game.player.find_skill('Mace')].set_level(20)
		game.player.skills[game.player.find_skill('Dagger')].set_level(5)
		game.player.skills[game.player.find_skill('Staff')].set_level(5)

	if game.player.profession == 'Mage':
		game.player.base_health = libtcod.random_get_int(game.rnd, 2, game.MAGE_HP_GAIN)
		game.player.base_mana = libtcod.random_get_int(game.rnd, 2, game.MAGE_MP_GAIN)
		game.player.base_stamina = libtcod.random_get_int(game.rnd, 2, game.MAGE_STAMINA_GAIN)
		game.player.inventory.append(game.baseitems.create_item('uncursed ', '', 'quarterstaff', '', 'identified'))
		game.player.inventory.append(game.baseitems.create_item('uncursed ', '', 'robes', '', 'identified'))
		game.player.skills[game.player.find_skill('Staff')].set_level(20)

	if game.player.profession == 'Explorer':
		game.player.base_health = libtcod.random_get_int(game.rnd, 2, game.EXPLORER_HP_GAIN)
		game.player.base_mana = libtcod.random_get_int(game.rnd, 2, game.EXPLORER_MP_GAIN)
		game.player.base_stamina = libtcod.random_get_int(game.rnd, 2, game.EXPLORER_STAMINA_GAIN)
		game.player.inventory.append(game.baseitems.create_item('uncursed ', '', 'dagger', '', 'identified'))
		game.player.inventory.append(game.baseitems.create_item('uncursed ', 'leather ', 'armor', '', 'identified'))

	game.player.inventory.append(game.baseitems.create_item('uncursed ', '', 'torch', '', 'identified'))
	game.player.inventory.append(game.baseitems.create_item('uncursed ', '', 'torch', '', 'identified'))
	game.player.inventory.append(game.baseitems.create_item('uncursed ', '', 'ration', '', 'identified'))
	game.player.inventory.append(game.baseitems.create_item('uncursed ', 'exceptional ', 'quarterstaff', ' of minor healing'))

	game.player.strength = game.player.base_strength
	game.player.dexterity = game.player.base_dexterity
	game.player.intelligence = game.player.base_intelligence
	game.player.wisdom = game.player.base_wisdom
	game.player.endurance = game.player.base_endurance
	game.player.karma = game.player.base_karma

	game.player.set_max_health()
	game.player.set_max_mana()
	game.player.set_max_stamina()
	game.player.health = game.player.max_health
	game.player.mana = game.player.max_mana
	game.player.stamina = game.player.max_stamina
	game.player.stats_bonus()
