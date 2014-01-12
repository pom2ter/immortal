import libtcodpy as libtcod
import game
import IO


# death screens and final summaries for player
def death_screen(quit=False):
	scrolli, scrollm = 0, 0
	scrollx, scrolly = 0, 0
	(screen, score, line1, line2) = death_tombstone(quit)

	while True:
		libtcod.console_set_default_foreground(0, libtcod.white)
		libtcod.console_set_default_background(0, libtcod.black)
		libtcod.console_print(0, 4, game.SCREEN_HEIGHT - 3, '[T] - Tombstone and final score       [M] - Fully explored last map')
		libtcod.console_print(0, 4, game.SCREEN_HEIGHT - 2, '[I] - Fully identified inventory      [L] - Show message log            [X] - Exit')
		libtcod.console_flush()
		libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS, game.kb, game.mouse, True)
		key_char = chr(game.kb.c)

		if game.kb.vk == libtcod.KEY_UP or game.kb.vk == libtcod.KEY_KP8:
			if screen == 'inventory':
				if scrolli > 0:
					scrolli -= 1
					death_inventory(scrolli)
			if screen == 'message':
				if scrollm > 0:
					scrollm -= 1
					death_messagelog(scrollm)
			if screen == 'map':
				if scrolly > 0:
					scrolly -= 1
					death_showmap(scrollx, scrolly)
		elif game.kb.vk == libtcod.KEY_DOWN or game.kb.vk == libtcod.KEY_KP2:
			if screen == 'inventory':
				if game.SCREEN_HEIGHT - 10 + scrolli < len(game.player.inventory + game.player.equipment):
					scrolli += 1
					death_inventory(scrolli)
			if screen == 'message':
				if game.SCREEN_HEIGHT - 10 + scrollm < len(game.message.history):
					scrollm += 1
					death_messagelog(scrollm)
			if screen == 'map':
				if game.SCREEN_HEIGHT - 14 + scrolly < game.current_map.map_height:
					scrolly += 1
					death_showmap(scrollx, scrolly)
		elif game.kb.vk == libtcod.KEY_LEFT or game.kb.vk == libtcod.KEY_KP4:
			if screen == 'map':
				if scrollx > 0:
					scrollx -= 1
					death_showmap(scrollx, scrolly)
		elif game.kb.vk == libtcod.KEY_RIGHT or game.kb.vk == libtcod.KEY_KP6:
			if screen == 'map':
				if game.SCREEN_WIDTH - 8 + scrollx < game.current_map.map_width:
					scrollx += 1
					death_showmap(scrollx, scrolly)

		elif key_char == 'i':
			screen = death_inventory(scrolli)
		elif key_char == 'l':
			screen = death_messagelog(scrollm)
		elif key_char == 'm':
			screen = death_showmap(scrollx, scrolly)
		elif key_char == 't':
			(screen, score, line1, line2) = death_tombstone(quit)
		elif key_char == 'x':
			break

	game.highscore.append((score, line1, line2))
	game.highscore = sorted(game.highscore, reverse=True)
	if len(game.highscore) > 10:
		game.highscore.pop()
	IO.save_high_scores()
	IO.delete_game()


# death screen: show a fully indentified inventory
def death_inventory(scroll):
	libtcod.console_set_color_control(libtcod.COLCTRL_1, libtcod.gray, libtcod.black)
	libtcod.console_set_default_foreground(0, libtcod.white)
	libtcod.console_set_default_background(0, libtcod.black)
	game.messages.box_gui(0, 0, 0, game.SCREEN_WIDTH, game.SCREEN_HEIGHT, color=libtcod.Color(245, 222, 179), lines=[{'dir': 'h', 'x': 0, 'y': 2}, {'dir': 'h', 'x': 0, 'y': game.SCREEN_HEIGHT - 4}])
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 1, libtcod.BKGND_SET, libtcod.CENTER, 'INVENTORY')
	libtcod.console_rect(0, 1, 4, game.SCREEN_WIDTH - 2, game.SCREEN_HEIGHT - 10, True, libtcod.BKGND_SET)
	output = game.player.inventory + game.player.equipment
	for i in range(min(game.SCREEN_HEIGHT - 10, len(output))):
		if output[i + scroll].quality == 0:
			libtcod.console_print(0, 2, i + 4, '%c%s%c' % (libtcod.COLCTRL_1, output[i + scroll].full_name, libtcod.COLCTRL_STOP))
		else:
			libtcod.console_print(0, 2, i + 4, output[i + scroll].full_name)
	if scroll > 0:
		libtcod.console_put_char_ex(0, game.SCREEN_WIDTH - 2, 4, chr(24), libtcod.white, libtcod.black)
	if game.SCREEN_HEIGHT - 10 + scroll < len(output):
		libtcod.console_put_char_ex(0, game.SCREEN_WIDTH - 2, game.SCREEN_HEIGHT - 7, chr(25), libtcod.white, libtcod.black)
	return 'inventory'


# death screen: show recent message log
def death_messagelog(scroll):
	libtcod.console_set_default_foreground(0, libtcod.white)
	libtcod.console_set_default_background(0, libtcod.black)
	game.messages.box_gui(0, 0, 0, game.SCREEN_WIDTH, game.SCREEN_HEIGHT, color=libtcod.Color(245, 222, 179), lines=[{'dir': 'h', 'x': 0, 'y': 2}, {'dir': 'h', 'x': 0, 'y': game.SCREEN_HEIGHT - 4}])
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 1, libtcod.BKGND_SET, libtcod.CENTER, 'MESSAGE LOG')
	libtcod.console_rect(0, 1, 4, game.SCREEN_WIDTH - 2, game.SCREEN_HEIGHT - 10, True, libtcod.BKGND_SET)
	for i in range(min(game.SCREEN_HEIGHT - 10, len(game.message.history))):
		libtcod.console_set_default_foreground(0, game.message.history[i + scroll][1])
		libtcod.console_print(0, 2, i + 4, game.message.history[i + scroll][0])
	if scroll > 0:
		libtcod.console_put_char_ex(0, game.SCREEN_WIDTH - 2, 4, chr(24), libtcod.white, libtcod.black)
	if game.SCREEN_HEIGHT - 10 + scroll < len(game.message.history):
		libtcod.console_put_char_ex(0, game.SCREEN_WIDTH - 2, game.SCREEN_HEIGHT - 7, chr(25), libtcod.white, libtcod.black)
	return 'message'


# death screen: show fully explored last map
def death_showmap(scrollx, scrolly):
	libtcod.console_set_default_foreground(0, libtcod.white)
	libtcod.console_set_default_background(0, libtcod.black)
	game.messages.box_gui(0, 0, 0, game.SCREEN_WIDTH, game.SCREEN_HEIGHT, color=libtcod.Color(245, 222, 179), lines=[{'dir': 'h', 'x': 0, 'y': 2}, {'dir': 'h', 'x': 0, 'y': game.SCREEN_HEIGHT - 4}])
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 1, libtcod.BKGND_SET, libtcod.CENTER, 'LAST MAP')

	if scrollx > 0:
		libtcod.console_put_char_ex(0, 2, 6, chr(27), libtcod.white, libtcod.black)
		libtcod.console_put_char_ex(0, 2, game.SCREEN_HEIGHT - 9, chr(27), libtcod.white, libtcod.black)
	if scrolly > 0:
		libtcod.console_put_char_ex(0, 4, 4, chr(24), libtcod.white, libtcod.black)
		libtcod.console_put_char_ex(0, game.SCREEN_WIDTH - 5, 4, chr(24), libtcod.white, libtcod.black)
	if game.SCREEN_WIDTH - 8 + scrollx < game.current_map.map_width:
		libtcod.console_put_char_ex(0, game.SCREEN_WIDTH - 3, 6, chr(26), libtcod.white, libtcod.black)
		libtcod.console_put_char_ex(0, game.SCREEN_WIDTH - 3, game.SCREEN_HEIGHT - 9, chr(26), libtcod.white, libtcod.black)
	if game.SCREEN_HEIGHT - 14 + scrolly < game.current_map.map_height:
		libtcod.console_put_char_ex(0, 4, game.SCREEN_HEIGHT - 7, chr(25), libtcod.white, libtcod.black)
		libtcod.console_put_char_ex(0, game.SCREEN_WIDTH - 5, game.SCREEN_HEIGHT - 7, chr(25), libtcod.white, libtcod.black)
	box = libtcod.console_new(game.current_map.map_width, game.current_map.map_height)
	for y in range(min(game.SCREEN_HEIGHT - 14, game.current_map.map_height)):
		for x in range(min(game.SCREEN_WIDTH - 8, game.current_map.map_width)):
			libtcod.console_put_char_ex(box, x, y, game.current_map.tile[x + scrollx][y + scrolly]['icon'], game.current_map.tile[x + scrollx][y + scrolly]['color'], game.current_map.tile[x + scrollx][y + scrolly]['back_light_color'])
	for obj in reversed(game.current_map.objects):
		if obj.name != 'player':
			if obj.x in range(scrollx, game.SCREEN_WIDTH - 8 + scrollx) and obj.y in range(scrolly, game.SCREEN_HEIGHT - 14 + scrolly):
				libtcod.console_put_char_ex(box, obj.x - scrollx, obj.y - scrolly, obj.char, obj.color, libtcod.BKGND_NONE)
	if game.char.x in range(scrollx, game.SCREEN_WIDTH - 8 + scrollx) and game.char.y in range(scrolly, game.SCREEN_HEIGHT - 14 + scrolly):
		libtcod.console_put_char_ex(box, game.char.x - scrollx, game.char.y - scrolly, '@', libtcod.white, libtcod.BKGND_NONE)
	libtcod.console_blit(box, 0, 0, game.SCREEN_WIDTH - 8, game.SCREEN_HEIGHT - 14, 0, 4, 6, 1.0, 1.0)
	libtcod.console_delete(box)
	return 'map'


# death screen: tombstone and final score
def death_tombstone(quit=False):
	libtcod.console_set_default_foreground(0, libtcod.white)
	libtcod.console_set_default_background(0, libtcod.black)
	game.messages.box_gui(0, 0, 0, game.SCREEN_WIDTH, game.SCREEN_HEIGHT, color=libtcod.Color(245, 222, 179), lines=[{'dir': 'h', 'x': 0, 'y': 2}, {'dir': 'h', 'x': 0, 'y': game.SCREEN_HEIGHT - 4}])
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 1, libtcod.BKGND_SET, libtcod.CENTER, 'TOMBSTONE AND FINAL SCORE')

	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 4, libtcod.BKGND_SET, libtcod.CENTER, '___________________')
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 5, libtcod.BKGND_SET, libtcod.CENTER, '  /                   \ ')
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 6, libtcod.BKGND_SET, libtcod.CENTER, '  /                     \ ')
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 7, libtcod.BKGND_SET, libtcod.CENTER, '  /                       \ ')
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 8, libtcod.BKGND_SET, libtcod.CENTER, '|                       |')
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 9, libtcod.BKGND_SET, libtcod.CENTER, '|                       |')
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 10, libtcod.BKGND_SET, libtcod.CENTER, '|                       |')
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 11, libtcod.BKGND_SET, libtcod.CENTER, '|                       |')
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 12, libtcod.BKGND_SET, libtcod.CENTER, '|                       |')
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 13, libtcod.BKGND_SET, libtcod.CENTER, '|                       |')
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 14, libtcod.BKGND_SET, libtcod.CENTER, '|                       |')
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 15, libtcod.BKGND_SET, libtcod.CENTER, '|                       |')
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 16, libtcod.BKGND_SET, libtcod.CENTER, '|                       |')
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 17, libtcod.BKGND_SET, libtcod.CENTER, '*|     *     *     *     |*')
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 18, libtcod.BKGND_SET, libtcod.CENTER, '_____\(/____\-/___/|\___\/\____/)\_____')

	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 7, libtcod.BKGND_SET, libtcod.CENTER, 'R I P')
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 9, libtcod.BKGND_SET, libtcod.CENTER, game.player.name)
	if quit:
		line2 = 'quitted the game'
		libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 11, libtcod.BKGND_SET, libtcod.CENTER, line2)
	elif game.cause_of_death == 'drowning':
		line2 = 'drowned'
		libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 11, libtcod.BKGND_SET, libtcod.CENTER, line2)
	elif game.cause_of_death == 'starvation':
		line2 = 'starved to death'
		libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 11, libtcod.BKGND_SET, libtcod.CENTER, line2)
	else:
		libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 11, libtcod.BKGND_SET, libtcod.CENTER, 'Killed by')
		libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 12, libtcod.BKGND_SET, libtcod.CENTER, game.cause_of_death)
		line2 = 'was killed by ' + game.cause_of_death
	if game.current_map.location_id == 0:
		libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 13, libtcod.BKGND_SET, libtcod.CENTER, 'in the')
	else:
		libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 13, libtcod.BKGND_SET, libtcod.CENTER, 'on level ' + str(game.current_map.location_level) + ' in the')
	libtcod.console_print_ex(0, game.SCREEN_WIDTH / 2, 14, libtcod.BKGND_SET, libtcod.CENTER, game.current_map.location_name)

	score = game.player.score()
	line1 = game.player.name + ', the level ' + str(game.player.level) + ' ' + game.player.gender + ' ' + game.player.race + ' ' + game.player.profession + ','
	if game.current_map.location_id == 0:
		line2 += ' in the ' + game.current_map.location_name + ' (' + str(game.turns) + ' turns)'
	else:
		line2 += ' on level ' + str(game.current_map.location_level) + ' in the ' + game.current_map.location_name + ' (' + str(game.turns) + ' turns)'
	libtcod.console_print(0, 2, 21, 'Final score')
	libtcod.console_print(0, 2, 23, str(score))
	libtcod.console_print(0, 8, 23, line1)
	libtcod.console_print(0, 8, 24, line2)
	return 'tombstone', score, line1, line2
