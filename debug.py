import libtcodpy as libtcod
import game
import util
import mapgen


class Debug(object):
	def __init__(self):
		self.enable = True

	def edit_attribute(self, stat):
		libtcod.console_print(0, game.MAP_X, 1, stat)
		libtcod.console_flush()
		choice = game.messages.input('', 0, game.MAP_X + len(stat), 1)
		if choice.isdigit():
			return int(choice)

	def add_player_flag(self):
		libtcod.console_print(0, game.MAP_X, 1, 'Add player flag: ')
		libtcod.console_flush()
		choice = game.messages.input('', 0, game.MAP_X + 17, 1)
		if choice != '':
			game.player.flags.append(choice)

	def fully_identify_inventory(self):
		for i in range(len(game.player.inventory)):
			if 'fully_identified' not in game.player.inventory[i].flags:
				game.player.inventory[i].flags.append('fully_identified')
		for i in range(len(game.player.equipment)):
			if 'fully_identified' not in game.player.equipment[i].flags:
				game.player.equipment[i].flags.append('fully_identified')

	def set_hunger_level(self):
		libtcod.console_print(0, game.MAP_X, 1, 'Set hunger level: ')
		libtcod.console_flush()
		choice = game.messages.input('', 0, game.MAP_X + 18, 1)
		if choice.isdigit():
			return int(choice)

	def reset_dungeon_level(self):
		temp_map = game.current_map
		game.current_map = mapgen.Map(temp_map.location_name, temp_map.location_abbr, temp_map.location_id, temp_map.location_level, temp_map.threat_level, temp_map.map_width, temp_map.map_height, temp_map.type)
		game.current_map.overworld_position = temp_map.overworld_position
		util.initialize_fov()
		game.fov_recompute = True
		game.draw_map = True
		libtcod.console_clear(game.con)

	def show_current_map(self):
		for x in range(game.current_map.map_width):
			for y in range(game.current_map.map_height):
				game.current_map.tile[x][y].update({'explored': True})
		util.initialize_fov()
		game.fov_recompute = True
		game.draw_map = True

	def hide_current_map(self):
		for x in range(game.current_map.map_width):
			for y in range(game.current_map.map_height):
				game.current_map.tile[x][y].pop('explored', None)
		util.initialize_fov()
		game.fov_recompute = True
		game.draw_map = True
		libtcod.console_clear(game.con)

	def teleport_anywhere_manual(self):
		libtcod.console_print(0, game.MAP_X, 1, 'x, y coordinates: ')
		libtcod.console_flush()
		choice = game.messages.input('', 0, game.MAP_X + 18, 1)
		if choice != '':
			coord = choice.split(',')
			if int(coord[0]) in range(game.WORLDMAP_WIDTH) and int(coord[1]) in range(game.WORLDMAP_HEIGHT):
				game.worldmap.player_positionx = int(coord[0])
				game.worldmap.player_positiony = int(coord[1])
				if game.current_map.location_id > 0:
					util.loadgen_message()
					game.old_maps.append(game.current_map)
				else:
					mapgen.change_maps(0, (game.worldmap.player_positiony * game.WORLDMAP_WIDTH + game.worldmap.player_positionx))
			game.draw_map = True
			libtcod.console_clear(game.con)

	def menu(self):
		if self.enable:
			contents = ['Edit strength stat', 'Edit dexterity stat', 'Edit intelligence stat', 'Edit wisdom stat', 'Edit endurance stat', 'Edit karma stat', 'Edit gold', 'Heal health', 'Heal stamina', 'Heal mana', 'Add player flag', 'Fully identify inventory', 'Set hunger level', 'Reset dungeon level', 'Show current map', 'Hide current map', 'Teleport (manual)']
			choice = game.messages.box('Debug Menu', None, game.PLAYER_STATS_WIDTH + (((game.MAP_WIDTH + 3) - (len(max(contents, key=len)) + 4)) / 2), ((game.MAP_HEIGHT + 1) - (len(contents) + 2)) / 2, len(max(contents, key=len)) + 4, len(contents) + 2, contents, mouse_exit=True)
			if choice == 0:
				game.player.strength = self.edit_attribute('Strength: ')
			if choice == 1:
				game.player.dexterity = self.edit_attribute('Dexterity: ')
			if choice == 2:
				game.player.intelligence = self.edit_attribute('Intelligence: ')
			if choice == 3:
				game.player.wisdom = self.edit_attribute('Wisdom: ')
			if choice == 4:
				game.player.endurance = self.edit_attribute('Endurance: ')
			if choice == 5:
				game.player.karma = self.edit_attribute('Karma: ')
			if choice == 6:
				game.player.money = self.edit_attribute('Coins: ')
			if choice == 7:
				game.player.heal_health(1000)
			if choice == 8:
				game.player.heal_stamina(1000)
			if choice == 9:
				game.player.heal_mana(1000)
			if choice == 10:
				self.add_player_flag()
			if choice == 11:
				self.fully_identify_inventory()
			if choice == 12:
				game.player.hunger = self.set_hunger_level()
			if choice == 13:
				self.reset_dungeon_level()
			if choice == 14:
				self.show_current_map()
			if choice == 15:
				self.hide_current_map()
			if choice == 16:
				self.teleport_anywhere_manual()
			game.draw_gui = True
