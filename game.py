import libtcodpy as libtcod
import shelve
import os
from players import *
from messages import *
from item import *
import map
import commands
import util

VERSION = 'v0.0.4'
BUILD = '13'

#size of the map
MAP_WIDTH = 75
MAP_HEIGHT = 28

#actual size of the window
PLAYER_STATS_WIDTH = 20
PLAYER_STATS_HEIGHT = 32
PANEL_HEIGHT = 4
SCREEN_WIDTH = MAP_WIDTH + PLAYER_STATS_WIDTH
SCREEN_HEIGHT = MAP_HEIGHT + PANEL_HEIGHT

#sizes and coordinates relevant for the GUI
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
MSG_X = PLAYER_STATS_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - PLAYER_STATS_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT
INVENTORY_WIDTH = 50

#parameters for dungeon generator
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30
MAX_MONSTERS_PER_LEVEL = 8
MAX_ITEMS_PER_LEVEL = 10

#fov
FOV_ALGO = 0
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 6
FOV_RADIUS = 6
SQUARED_TORCH_RADIUS = TORCH_RADIUS * TORCH_RADIUS

con = 0
panel = 0
ps = 0

fov_recompute = True
fov_torch = True
fov_map = None
fov_noise = None
fov_torchx = 0.0
current_map = None
old_maps = []
char = None
savefiles = []
times_saved = 0

path_dijk = None
path_recalculate = False
path_dx = 0
path_dy = 0
mouse_move = False


class Game(object):
	def __init__(self):
		global con, panel, ps, fov_noise, savefiles
		#img = libtcod.image_load('title_screen2.png')
		libtcod.console_set_custom_font('fonts/immortal.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
		libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Immortal ' + VERSION, False)
		#libtcod.sys_set_fps(30)
		con = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
		panel = libtcod.console_new(MAP_WIDTH, PANEL_HEIGHT)
		ps = libtcod.console_new(PLAYER_STATS_WIDTH, PLAYER_STATS_HEIGHT)
		fov_noise = libtcod.noise_new(1, 1.0, 1.0)
		savefiles = os.listdir('saves')
		self.main_menu()

	# setup the items structure and run parser
	def init_items(self):
		global items
		items = ItemList()
		parser = libtcod.parser_new()
		item_type_struct = libtcod.parser_new_struct(parser, 'item_type')
		libtcod.struct_add_property(item_type_struct, 'type', libtcod.TYPE_STRING, True)
		libtcod.struct_add_property(item_type_struct, 'unidentified_name', libtcod.TYPE_STRING, True)
		libtcod.struct_add_property(item_type_struct, 'icon', libtcod.TYPE_STRING, True)
		libtcod.struct_add_property(item_type_struct, 'icon_color', libtcod.TYPE_COLOR, True)
		libtcod.struct_add_property(item_type_struct, 'dark_color', libtcod.TYPE_COLOR, True)
		libtcod.struct_add_property(item_type_struct, 'weight', libtcod.TYPE_FLOAT, False)
		libtcod.struct_add_property(item_type_struct, 'cost', libtcod.TYPE_INT, False)
		libtcod.struct_add_property(item_type_struct, 'dices', libtcod.TYPE_DICE, False)
		libtcod.struct_add_flag(item_type_struct, 'healing')
		libtcod.struct_add_flag(item_type_struct, 'usable')
		libtcod.struct_add_flag(item_type_struct, 'equippable')
		libtcod.parser_run(parser, "data/items.txt", ItemListener())
		game.player.inventory.append(items.list[1])
		game.player.inventory.append(items.list[2])
		game.player.inventory.append(items.list[0])
		game.player.inventory.append(items.list[3])
		game.player.inventory.append(items.list[2])

	# new game setup
	def new_game(self):
		global player, char, message, game_state, current_map
		message = Message()
		player = Player()
		char = map.Object(0, 0, player.icon, 'player', player.icon_color, blocks=True)
		game_state = create_character()
		#player.name = 'Ben'
		#game_state = 'playing'
		self.init_items()
		if game_state == 'playing':
			libtcod.console_clear(0)
			current_map = map.Map('Starter Dungeon', 1, 1)
			util.initialize_fov()
			self.play_game()

	# main game loop
	def play_game(self):
		global player_action
		while not libtcod.console_is_window_closed():
			util.render_all()
			libtcod.console_flush()

			for object in current_map.objects:
				object.clear(con)

			player_action = commands.handle_keys()
			if player_action == 'save':
				self.save_game()
				player_action = 'exit'
				break
			if player_action == 'exit':
				break

			#let monsters take their turn
#			if game_state == 'playing' and player_action != 'didnt-take-turn':
#				for object in objects:
#					if object.ai:
#						object.ai.take_turn()

	# save the game using the shelve module
	def save_game(self):
		if not os.path.exists('saves'):
			os.makedirs('saves')
		file = shelve.open('saves/' + player.name, 'n')
		file['current_map'] = current_map
		file['maps'] = old_maps
		file['player'] = player
		file['messages'] = message
		file['game_state'] = game_state
		file['times_saved'] = times_saved + 1
		file.close()

	# load the game using the shelve module
	def load_game(self):
		global current_map, old_maps, player, char, message, game_state, times_saved
		if len(savefiles) == 0:
			util.msg_box('message', 'Saved games', contents='There are no save games.', box_height=5)
		else:
			choice = util.msg_box('save', 'Saved games', box_height=len(savefiles))
			if choice != -1:
				file = shelve.open('saves/' + savefiles[choice], 'r')
				current_map = file['current_map']
				old_maps = file['maps']
				player = file['player']
				message = file['messages']
				game_state = file['game_state']
				times_saved = file['times_saved']
				file.close()
				char = current_map.objects[0]
				self.init_items()
				libtcod.console_clear(0)
				util.initialize_fov()
				self.play_game()

	# brings up the main menu
	def main_menu(self):
		global player_action
		player_action = None
		libtcod.console_credits()
		while not libtcod.console_is_window_closed():
			#libtcod.image_blit_2x(img, 0, 0, 0)
			libtcod.console_set_default_foreground(0, libtcod.light_yellow)
			libtcod.console_set_default_background(0, libtcod.black)
			libtcod.console_clear(0)
			libtcod.console_print_ex(0, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 5, libtcod.BKGND_SET, libtcod.CENTER, 'Immortal ' + VERSION)
			libtcod.console_print_ex(0, SCREEN_WIDTH / 2, SCREEN_HEIGHT - 2, libtcod.BKGND_SET, libtcod.CENTER, 'By Potatoman')
			choice = util.menu('Main menu', ['Start a new game', 'Load a saved game', 'Manual', 'Options', 'Quit'])
			#choice = 0

			if choice == 0:  # new game
				self.new_game()
				if player_action == 'exit':
					break
			if choice == 1:  # load last game
				self.load_game()
				if player_action == 'exit':
					break
			if choice == 4:  # quit
				break
