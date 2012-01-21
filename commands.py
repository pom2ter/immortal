import libtcodpy as libtcod
import util
import game


def handle_keys():
	key = libtcod.console_check_for_keypress(libtcod.KEY_PRESSED)

	if key.vk == libtcod.KEY_ENTER and key.lalt:
		#Alt+Enter: toggle fullscreen
		libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
	elif key.vk == libtcod.KEY_ESCAPE:
		return 'exit'  # exit game

	if game.game_state == 'playing':
		#movement keys
		if key.vk == libtcod.KEY_UP:
			player_move_or_attack(0, -1)
		elif key.vk == libtcod.KEY_DOWN:
			player_move_or_attack(0, 1)
		elif key.vk == libtcod.KEY_LEFT:
			player_move_or_attack(-1, 0)
		elif key.vk == libtcod.KEY_RIGHT:
			player_move_or_attack(1, 0)
		else:
			#test for other keys
			key_char = chr(key.c)

			if key_char == 'c':
				close_door()
			if key_char == 'o':
				open_door()

#			if key_char == 'g':
#				#pick up an item
#				for object in objects:  # look for an item in the player's tile
#					if object.x == char.x and object.y == char.y and object.item:
#						object.item.pick_up()
#						break

#			if key_char == 'i':
#				#show the inventory; if an item is selected, use it
#				chosen_item = inventory_menu('Press the key next to an item to use it, or any other to cancel.\n')
#				if chosen_item is not None:
#					chosen_item.use()

#			if key_char == 'd':
#				#show the inventory; if an item is selected, drop it
#				chosen_item = inventory_menu('Press the key next to an item to drop it, or any other to cancel.\n')
#				if chosen_item is not None:
#					chosen_item.drop()

			return 'didnt-take-turn'


def player_move_or_attack(dx, dy):
	#the coordinates the player is moving to/attacking
	x = game.char.x + dx
	y = game.char.y + dy

	#try to find an attackable object there
	target = None
#	for object in maps.objects:
#		if object.fighter and object.x == x and object.y == y:
#			target = object
#			break

	#attack if target found, move otherwise
	if target is not None:
		game.char.fighter.attack(target)
	else:
		game.char.move(dx, dy, game.current_map)
		game.fov_recompute = True


def open_door():
	util.message('Open door in which direction?')
	util.render_all()
	libtcod.console_flush()
	dx = 0
	dy = 0

	key = libtcod.console_wait_for_keypress(True)
	if key.vk == libtcod.KEY_UP:
		dy = -1
	elif key.vk == libtcod.KEY_DOWN:
		dy = 1
	elif key.vk == libtcod.KEY_LEFT:
		dx = -1
	elif key.vk == libtcod.KEY_RIGHT:
		dx = 1

	if game.current_map.tiles[game.char.x + dx][game.char.y + dy].name == 'door':
		game.current_map.tiles[game.char.x + dx][game.char.y + dy].icon = '/'
		game.current_map.tiles[game.char.x + dx][game.char.y + dy].name = 'opened_door'
		game.current_map.tiles[game.char.x + dx][game.char.y + dy].color = libtcod.dark_orange
		game.current_map.tiles[game.char.x + dx][game.char.y + dy].dark_color = libtcod.darkest_orange
		game.current_map.tiles[game.char.x + dx][game.char.y + dy].blocked = False
		game.current_map.tiles[game.char.x + dx][game.char.y + dy].block_sight = False
		util.message('You open the door.')
		game.fov_recompute = True
		util.initialize_fov()
		util.render_all()
	elif dx != 0 or dy != 0:
		util.message('There is no door in that direction!', libtcod.red)


def close_door():
	util.message('Close door in which direction?')
	util.render_all()
	libtcod.console_flush()
	dx = 0
	dy = 0

	key = libtcod.console_wait_for_keypress(True)
	if key.vk == libtcod.KEY_UP:
		dy = -1
	elif key.vk == libtcod.KEY_DOWN:
		dy = 1
	elif key.vk == libtcod.KEY_LEFT:
		dx = -1
	elif key.vk == libtcod.KEY_RIGHT:
		dx = 1

	if game.current_map.tiles[game.char.x + dx][game.char.y + dy].name == 'opened_door':
		game.current_map.tiles[game.char.x + dx][game.char.y + dy].icon = '+'
		game.current_map.tiles[game.char.x + dx][game.char.y + dy].name = 'door'
		game.current_map.tiles[game.char.x + dx][game.char.y + dy].color = libtcod.dark_orange
		game.current_map.tiles[game.char.x + dx][game.char.y + dy].dark_color = libtcod.darkest_orange
		game.current_map.tiles[game.char.x + dx][game.char.y + dy].blocked = True
		game.current_map.tiles[game.char.x + dx][game.char.y + dy].block_sight = True
		util.message('You close the door.')
		game.fov_recompute = True
		util.initialize_fov()
		util.render_all()
	elif dx != 0 or dy != 0:
		util.message('There is no door in that direction!', libtcod.red)
