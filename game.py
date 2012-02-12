import libtcodpy as libtcod
import shelve
from players import *
from messages import *
from item import *
import map
import commands
import util

VERSION = 'v0.0.1.6'

#actual size of the window
SCREEN_WIDTH = 100
SCREEN_HEIGHT = 32

#size of the map
MAP_WIDTH = 80
MAP_HEIGHT = 28

#sizes and coordinates relevant for the GUI
BAR_WIDTH = 20
PLAYER_STATS_WIDTH = 20
PLAYER_STATS_HEIGHT = 32
PANEL_HEIGHT = 4
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
MSG_X = BAR_WIDTH + 2
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
char = None

path_dijk = None
path_recalculate = False
path_dx = 0
path_dy = 0
mouse_move = False


class Game(object):
	def __init__(self):
		global con, panel, ps
		#img = libtcod.image_load('title_screen2.png')
		libtcod.console_set_custom_font('fonts/ph_font.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
		libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Immortal ' + VERSION, False)
		#libtcod.sys_set_fps(30)
		con = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
		panel = libtcod.console_new(MAP_WIDTH, PANEL_HEIGHT)
		ps = libtcod.console_new(PLAYER_STATS_WIDTH, PLAYER_STATS_HEIGHT)
		self.main_menu()

	def init_items(self):
		global items
		items = ItemList()
		parser = libtcod.parser_new()
		item_type_struct = libtcod.parser_new_struct(parser, 'item_type')
		libtcod.struct_add_property(item_type_struct, 'unidentified_name', libtcod.TYPE_STRING, True)
		libtcod.struct_add_property(item_type_struct, 'icon', libtcod.TYPE_STRING, True)
		libtcod.struct_add_property(item_type_struct, 'icon_color', libtcod.TYPE_COLOR, True)
		libtcod.struct_add_property(item_type_struct, 'dark_color', libtcod.TYPE_COLOR, True)
		libtcod.struct_add_property(item_type_struct, 'weight', libtcod.TYPE_INT, True)
		libtcod.parser_run(parser, "data/items.txt", ItemListener())

	def new_game(self):
		global player, char, message, game_state, current_map
		player = Player()
		char = map.Object(0, 0, player.icon, 'player', player.icon_color, blocks=True)
		#status = create_character()
		player.name = 'Ben'
		status = 'play'
		self.init_items()
		if status == 'play':
			libtcod.console_clear(0)
			current_map = map.Map('Starter Dungeon', 1, 1)
			util.initialize_fov()
			game_state = 'playing'
			message = Message()
			self.play_game()

	def play_game(self):
		player_action = None

		while not libtcod.console_is_window_closed():
			#render the screen
			util.render_all()
			libtcod.console_flush()

			#erase all objects at their old locations, before they move
			for object in current_map.objects:
				object.clear(con)

			#handle keys and exit game if needed
			player_action = commands.handle_keys()
			if player_action == 'exit':
				self.save_game()
				break

			#let monsters take their turn
#			if game_state == 'playing' and player_action != 'didnt-take-turn':
#				for object in objects:
#					if object.ai:
#						object.ai.take_turn()

	def save_game(self):
		#open a new empty shelve (possibly overwriting an old one) to write the game data
		file = shelve.open('savegame', 'n')
		file['map'] = current_map
		file['objects'] = current_map.objects
		file['player_index'] = current_map.objects.index(char)  # index of player in objects list
#		file['inventory'] = inventory
		file['messages'] = message
		file['game_state'] = game_state
		file.close()

	def load_game(self):
		#open the previously saved shelve and load the game data
		global char, inventory, message, game_state, current_map
		file = shelve.open('savegame', 'r')
		current_map = file['map']
		current_map.objects = file['objects']
		char = current_map.objects[file['player_index']]  # get index of player in objects list and access it
#		inventory = file['inventory']
		message = file['messages']
		game_state = file['game_state']
		file.close()
		util.initialize_fov()

	def main_menu(self):
		libtcod.console_credits()
		while not libtcod.console_is_window_closed():
			#libtcod.image_blit_2x(img, 0, 0, 0)
			libtcod.console_set_default_foreground(0, libtcod.light_yellow)
			libtcod.console_set_default_background(0, libtcod.black)
			libtcod.console_clear(0)
			libtcod.console_print_ex(0, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 5, libtcod.BKGND_SET, libtcod.CENTER, 'Immortal ' + VERSION)
			libtcod.console_print_ex(0, SCREEN_WIDTH / 2, SCREEN_HEIGHT - 2, libtcod.BKGND_SET, libtcod.CENTER, 'By Potatoman')

			#show options and wait for the player's choice
			choice = util.menu('Main menu', ['Start a new game', 'Load a saved game', 'Manual', 'Options', 'Quit'])

			if choice == 0:  # new game
				self.new_game()
				break
#			if choice == 1:  # load last game
#				try:
#					self.load_game()
#				except:
#					msgbox('\n No saved game to load.\n', 24)
#					continue
#				play_game()
			if choice == 4:  # quit
				break
