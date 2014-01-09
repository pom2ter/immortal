import libtcodpy as libtcod
import game
import util


# character sheet for stats
def character_sheet_attributes(con, width, height):
	character_sheet_ui(con, width, height, ' Character Sheet ')
	libtcod.console_set_color_control(libtcod.COLCTRL_1, libtcod.green, libtcod.black)
	libtcod.console_set_color_control(libtcod.COLCTRL_2, libtcod.red, libtcod.black)
	libtcod.console_set_color_control(libtcod.COLCTRL_3, libtcod.gold, libtcod.black)
	libtcod.console_set_color_control(libtcod.COLCTRL_4, libtcod.silver, libtcod.black)
	libtcod.console_set_color_control(libtcod.COLCTRL_5, libtcod.copper, libtcod.black)
	libtcod.console_print(con, 2, 2, game.player.name + ', a level ' + str(game.player.level) + ' ' + game.player.gender + ' ' + game.player.race + ' ' + game.player.profession)
	g, s, c = util.money_converter(game.player.money)

	if game.player.strength > game.player.base_strength:
		libtcod.console_print(con, 2, 4, 'Strength     : %c%i%c' % (libtcod.COLCTRL_1, game.player.strength, libtcod.COLCTRL_STOP))
	elif game.player.strength < game.player.base_strength:
		libtcod.console_print(con, 2, 4, 'Strength     : %c%i%c' % (libtcod.COLCTRL_2, game.player.strength, libtcod.COLCTRL_STOP))
	else:
		libtcod.console_print(con, 2, 4, 'Strength     : ' + str(game.player.strength))

	if game.player.dexterity > game.player.base_dexterity:
		libtcod.console_print(con, 2, 5, 'Dexterity    : %c%i%c' % (libtcod.COLCTRL_1, game.player.dexterity, libtcod.COLCTRL_STOP))
	elif game.player.dexterity < game.player.base_dexterity:
		libtcod.console_print(con, 2, 5, 'Dexterity    : %c%i%c' % (libtcod.COLCTRL_2, game.player.dexterity, libtcod.COLCTRL_STOP))
	else:
		libtcod.console_print(con, 2, 5, 'Dexterity    : ' + str(game.player.dexterity))

	if game.player.intelligence > game.player.intelligence:
		libtcod.console_print(con, 2, 6, 'Intelligence : %c%i%c' % (libtcod.COLCTRL_1, game.player.intelligence, libtcod.COLCTRL_STOP))
	elif game.player.intelligence < game.player.intelligence:
		libtcod.console_print(con, 2, 6, 'Intelligence : %c%i%c' % (libtcod.COLCTRL_2, game.player.intelligence, libtcod.COLCTRL_STOP))
	else:
		libtcod.console_print(con, 2, 6, 'Intelligence : ' + str(game.player.intelligence))

	if game.player.wisdom > game.player.wisdom:
		libtcod.console_print(con, 2, 7, 'Wisdom       : %c%i%c' % (libtcod.COLCTRL_1, game.player.wisdom, libtcod.COLCTRL_STOP))
	elif game.player.wisdom < game.player.wisdom:
		libtcod.console_print(con, 2, 7, 'Wisdom       : %c%i%c' % (libtcod.COLCTRL_2, game.player.wisdom, libtcod.COLCTRL_STOP))
	else:
		libtcod.console_print(con, 2, 7, 'Wisdom       : ' + str(game.player.wisdom))

	if game.player.endurance > game.player.endurance:
		libtcod.console_print(con, 2, 8, 'Endurance    : %c%i%c' % (libtcod.COLCTRL_1, game.player.endurance, libtcod.COLCTRL_STOP))
	elif game.player.endurance < game.player.endurance:
		libtcod.console_print(con, 2, 8, 'Endurance    : %c%i%c' % (libtcod.COLCTRL_2, game.player.endurance, libtcod.COLCTRL_STOP))
	else:
		libtcod.console_print(con, 2, 8, 'Endurance    : ' + str(game.player.endurance))

	libtcod.console_print(con, 2, 9, 'Karma        : ' + str(game.player.karma))
	libtcod.console_print(con, 30, 4, 'Health     : ' + str(game.player.health) + ' / ' + str(game.player.max_health))
	libtcod.console_print(con, 30, 5, 'Stamina    : ' + str(game.player.stamina) + ' / ' + str(game.player.max_stamina))
	libtcod.console_print(con, 30, 6, 'Mana       : ' + str(game.player.mana) + ' / ' + str(game.player.max_mana))
	libtcod.console_print(con, 30, 7, 'Experience : ' + str(game.player.xp))
	libtcod.console_print(con, 30, 8, 'Coins      : %c%s%c%c%c%c%i %c%s%c%c%c%c%i %c%s%c%c%c%c%i%c' % (libtcod.COLCTRL_3, chr(23), libtcod.COLCTRL_FORE_RGB, 255, 255, 255, g, libtcod.COLCTRL_4, chr(23), libtcod.COLCTRL_FORE_RGB, 255, 255, 255, s, libtcod.COLCTRL_5, chr(23), libtcod.COLCTRL_FORE_RGB, 255, 255, 255, c, libtcod.COLCTRL_STOP))
	libtcod.console_print(con, 2, 11, 'Attack Rating     : ' + str(game.player.attack_rating()))
	libtcod.console_print(con, 2, 12, 'Defense Rating    : ' + str(game.player.defense_rating()))
	libtcod.console_print(con, 2, 13, 'Carrying Capacity : ' + str(game.player.weight_carried()) + ' / ' + str(game.player.max_carrying_capacity()) + ' lbs')


# character sheet for skills
def character_sheet_skills(con, width, height, pick_skill, modify_skill, pool):
	character_sheet_ui(con, width, height, ' Skills ')
	skills_c, skills_p, skills_a = [], [], []
	for i in game.player.skills:
		if i.category == 'Combat':
			skills_c.append(i)
		if i.category == 'Physical':
			skills_p.append(i)
		if i.category == 'Academic':
			skills_a.append(i)

	count = 1
	libtcod.console_print(con, 2, 2, 'Combat')
	libtcod.console_print(con, 19, 2, 'Physical')
	libtcod.console_print(con, 41, 2, 'Academic')
	libtcod.console_print(con, 2, height - 5, 'Skill points: ' + str(pool))
	for i in range(len(skills_c)):
		if pick_skill == count:
			libtcod.console_set_default_foreground(con, libtcod.light_blue)
			libtcod.console_print(con, 11, i + 4, chr(27))
			libtcod.console_print(con, 15, i + 4, chr(26))
			if modify_skill > 0 or (modify_skill < 0 and skills_c[i].temp > 0):
				if skills_c[i].level + skills_c[i].temp + modify_skill <= 100:
					skills_c[i].temp += modify_skill
					pool -= modify_skill
		else:
			libtcod.console_set_default_foreground(con, libtcod.white)
		libtcod.console_print(con, 2, i + 4, skills_c[i].name)
		if skills_c[i].temp > 0:
			libtcod.console_set_default_foreground(con, libtcod.green)
		libtcod.console_print_ex(con, 14, i + 4, libtcod.BKGND_SET, libtcod.RIGHT, str(skills_c[i].level + skills_c[i].temp))
		count += 1

	for i in range(len(skills_p)):
		if pick_skill == count:
			libtcod.console_set_default_foreground(con, libtcod.light_blue)
			libtcod.console_print(con, 33, i + 4, chr(27))
			libtcod.console_print(con, 37, i + 4, chr(26))
			if modify_skill > 0 or (modify_skill < 0 and skills_p[i].temp > 0):
				if skills_p[i].level + skills_p[i].temp + modify_skill <= 100:
					skills_p[i].temp += modify_skill
					pool -= modify_skill
		else:
			libtcod.console_set_default_foreground(con, libtcod.white)
		if skills_p[i].temp > 0:
			libtcod.console_set_default_foreground(con, libtcod.green)
		libtcod.console_print(con, 19, i + 4, skills_p[i].name)
		libtcod.console_print_ex(con, 36, i + 4, libtcod.BKGND_SET, libtcod.RIGHT, str(skills_p[i].level + skills_p[i].temp))
		count += 1

	for i in range(len(skills_a)):
		if pick_skill == count:
			libtcod.console_set_default_foreground(con, libtcod.light_blue)
			libtcod.console_print(con, 52, i + 4, chr(27))
			libtcod.console_print(con, 56, i + 4, chr(26))
			if modify_skill > 0 or (modify_skill < 0 and skills_a[i].temp > 0):
				if skills_a[i].level + skills_a[i].temp + modify_skill <= 100:
					skills_a[i].temp += modify_skill
					pool -= modify_skill
		else:
			libtcod.console_set_default_foreground(con, libtcod.white)
		if skills_a[i].temp > 0:
			libtcod.console_set_default_foreground(con, libtcod.green)
		libtcod.console_print(con, 41, i + 4, skills_a[i].name)
		libtcod.console_print_ex(con, 55, i + 4, libtcod.BKGND_SET, libtcod.RIGHT, str(skills_a[i].level + skills_a[i].temp))
		count += 1
	return pool


# character sheet for equipment
def character_sheet_equipment(con, width, height):
	character_sheet_ui(con, width, height, ' Equipment ')
	libtcod.console_print(con, 2, 2, 'Head       :')
	libtcod.console_print(con, 2, 3, 'Cloak      :')
	libtcod.console_print(con, 2, 4, 'Neck       :')
	libtcod.console_print(con, 2, 5, 'Body       :')
	libtcod.console_print(con, 2, 6, 'Right Hand :')
	libtcod.console_print(con, 2, 7, 'Left Hand  :')
	libtcod.console_print(con, 2, 8, 'Ring       :')
	libtcod.console_print(con, 2, 9, 'Ring       :')
	libtcod.console_print(con, 2, 10, 'Gauntlets  :')
	libtcod.console_print(con, 2, 11, 'Boots      :')
	libtcod.console_print(con, 2, 12, 'Missile(s) :')
	ring = 0
	for i in range(len(game.player.equipment)):
		if 'armor_head' in game.player.equipment[i].flags:
			y = 2
		if 'armor_cloak' in game.player.equipment[i].flags:
			y = 3
		if 'armor_neck' in game.player.equipment[i].flags:
			y = 4
		if 'armor_body' in game.player.equipment[i].flags:
			y = 5
		if 'armor_ring' in game.player.equipment[i].flags:
			ring += 1
			y = 7 + ring
		if 'armor_hands' in game.player.equipment[i].flags:
			y = 10
		if 'armor_feet' in game.player.equipment[i].flags:
			y = 11
		if game.player.equipment[i].type == 'weapon':
			y = 6
		if game.player.equipment[i].type == 'shield':
			y = 7
		if game.player.equipment[i].type == 'missile':
			y = 12
		libtcod.console_print(con, 13, y, ': ' + game.player.equipment[i].get_name())
		libtcod.console_print_ex(con, width - 3, y, libtcod.BKGND_SET, libtcod.RIGHT, str(round(game.player.equipment[i].weight * game.player.equipment[i].quantity, 1)) + ' lbs')


# character sheet for inventory
def character_sheet_inventory(con, width, height):
	character_sheet_ui(con, width, height, ' Inventory ')
	libtcod.console_set_color_control(libtcod.COLCTRL_1, libtcod.gray, libtcod.black)
	output = util.item_stacking(game.player.inventory)
	for i in range(len(output)):
		text_left = output[i].get_name()
		if output[i].duration > 0:
			text_left += ' (' + str(output[i].duration) + ' turns left)'
		text_right = str(round(output[i].weight * output[i].quantity, 1)) + ' lbs'
		if output[i].is_identified() and output[i].quality == 0:
			libtcod.console_print(con, 2, i + 2, '%c%s%c' % (libtcod.COLCTRL_1, text_left, libtcod.COLCTRL_STOP))
			libtcod.console_print_ex(con, width - 3, i + 2, libtcod.BKGND_SET, libtcod.RIGHT, '%c%s%c' % (libtcod.COLCTRL_1, text_right, libtcod.COLCTRL_STOP))
		else:
			libtcod.console_print(con, 2, i + 2, text_left)
			libtcod.console_print_ex(con, width - 3, i + 2, libtcod.BKGND_SET, libtcod.RIGHT, text_right)
	util.reset_quantity(game.player.inventory)


# character sheet box ui
def character_sheet_ui(con, width, height, header):
	game.messages.box_gui(con, 0, 0, width, height)
	libtcod.console_set_default_foreground(con, libtcod.black)
	libtcod.console_set_default_background(con, libtcod.green)
	libtcod.console_print_ex(con, width / 2, 0, libtcod.BKGND_SET, libtcod.CENTER, header)
	libtcod.console_print_ex(con, width / 2, height - 1, libtcod.BKGND_SET, libtcod.CENTER, ' [ Arrow keys to change page, +/- to change skill pts ] ')
	libtcod.console_set_default_foreground(con, libtcod.green)
	libtcod.console_set_default_background(con, libtcod.black)
	libtcod.console_print_ex(con, width - 5, 0, libtcod.BKGND_SET, libtcod.LEFT, '[x]')
	libtcod.console_print(con, 2, height - 3, '<<<')
	libtcod.console_print(con, width - 5, height - 3, '>>>')
	libtcod.console_set_default_foreground(con, libtcod.white)


# character sheet
def character_sheet(screen=0):
	width, height = 62, 23
	pick_skill, modify_skill = 0, 0
	stats = libtcod.console_new(width, height)
	pool = game.player.skill_points
	posx = ((game.MAP_WIDTH - width) / 2) + game.MAP_X
	posy = ((game.MAP_HEIGHT - height) / 2) + 1

	while True:
		if screen == 0:
			character_sheet_attributes(stats, width, height)
		elif screen == 1:
			pool = character_sheet_skills(stats, width, height, pick_skill, modify_skill, pool)
		elif screen == 2:
			character_sheet_equipment(stats, width, height)
		elif screen == 3:
			character_sheet_inventory(stats, width, height)
		modify_skill = 0

		libtcod.console_blit(stats, 0, 0, width, height, 0, posx, posy, 1.0, 1.0)
		libtcod.console_flush()
		ev = libtcod.sys_check_for_event(libtcod.EVENT_ANY, game.kb, game.mouse)
		(mx, my) = (game.mouse.cx, game.mouse.cy)
		key_char = chr(game.kb.c)

		if screen == 1 and ev == libtcod.EVENT_KEY_PRESS:
			if game.kb.vk == libtcod.KEY_UP:
				pick_skill -= 1
				if pick_skill < 1:
					pick_skill = 1
			elif game.kb.vk == libtcod.KEY_DOWN:
				pick_skill += 1
				if pick_skill > len(game.player.skills):
					pick_skill = len(game.player.skills)
			elif key_char == '+':
				if pick_skill in range(1, len(game.player.skills)) and pool > 0:
					modify_skill = 1
			elif key_char == '-':
				if pick_skill in range(1, len(game.player.skills)) and (pool > 0 or (pool == 0 and game.player.skill_points > 0)):
					modify_skill = -1

		if (game.kb.vk == libtcod.KEY_LEFT and ev == libtcod.EVENT_KEY_PRESS) or (game.mouse.lbutton_pressed and mx in range(posx + 2, posx + 5) and my == posy + height - 3 and ev == libtcod.EVENT_MOUSE_RELEASE):
			screen -= 1
			if screen < 0:
				screen = 3
		elif (game.kb.vk == libtcod.KEY_RIGHT and ev == libtcod.EVENT_KEY_PRESS) or (game.mouse.lbutton_pressed and mx in range(posx + width - 5, posx + width - 2) and my == posy + height - 3 and ev == libtcod.EVENT_MOUSE_RELEASE):
			screen += 1
			if screen > 3:
				screen = 0
		elif (game.kb.vk == libtcod.KEY_ESCAPE and ev == libtcod.EVENT_KEY_PRESS) or (game.mouse.lbutton_pressed and mx == posx + width - 4 and my == posy and ev == libtcod.EVENT_MOUSE_RELEASE):
			break

	for i in range(len(game.player.skills)):
		if game.player.skills[i].temp > 0:
			game.player.skill_points -= game.player.skills[i].temp
			game.player.skills[i].base_level += game.player.skills[i].temp
			game.player.skills[i].level += game.player.skills[i].temp
			game.player.skills[i].temp = 0
	libtcod.console_delete(stats)
	game.draw_gui = True
