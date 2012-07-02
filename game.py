import libtcodpy as libtcod
import shelve
import os
from players import *
from messages import *
from item import *
from monster import *
import map
import commands
import util

VERSION = 'v0.1.0'
BUILD = '15'

#size of the map
MAP_WIDTH = 72
MAP_HEIGHT = 30

#actual size of the window
PLAYER_STATS_WIDTH = 18
PLAYER_STATS_HEIGHT = 35
MESSAGE_WIDTH = 72
MESSAGE_HEIGHT = 4
SCREEN_WIDTH = MAP_WIDTH + PLAYER_STATS_WIDTH + 3
SCREEN_HEIGHT = MAP_HEIGHT + MESSAGE_HEIGHT + 3

#sizes and coordinates relevant for the GUI
PLAYER_STATS_X = 1
PLAYER_STATS_Y = 1
MAP_X = PLAYER_STATS_WIDTH + 2
MAP_Y = 1
MESSAGE_X = PLAYER_STATS_WIDTH + 2
MESSAGE_Y = MAP_HEIGHT + 2

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
FOV_RADIUS = 8
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
player_move = False

path_dijk = None
path_recalculate = False
path_dx = 0
path_dy = 0
mouse_move = False
mouse = libtcod.Mouse()


class Game(object):
	def __init__(self):
		global con, panel, ps, fov_noise, savefiles, items, tiles, monsters
		#img = libtcod.image_load('title_screen2.png')
		libtcod.console_set_custom_font('font.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
		libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Immortal ' + VERSION, False)
		#libtcod.sys_set_fps(60)
		con = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
		panel = libtcod.console_new(MESSAGE_WIDTH, MESSAGE_HEIGHT)
		ps = libtcod.console_new(PLAYER_STATS_WIDTH, PLAYER_STATS_HEIGHT)
		fov_noise = libtcod.noise_new(1, 1.0, 1.0)
		savefiles = os.listdir('saves')
		items = ItemList()
		items.init_parser()
		tiles = map.TileList()
		tiles.init_parser()
		monsters = MonsterList()
		monsters.init_parser()
		self.main_menu()

	# new game setup
	def new_game(self):
		global player, char, message, game_state, current_map
		message = Message()
		player = Player()
		char = map.Object(0, 0, player.icon, 'player', player.icon_color, blocks=True)
		game_state = create_character()
		#player.name = 'Ben'
		#game_state = 'playing'
		#game.player.inventory.append(items.list[1])
		#game.player.inventory.append(items.list[2])
		#game.player.inventory.append(items.list[0])
		#game.player.inventory.append(items.list[3])
		#game.player.inventory.append(items.list[2])
		#game.player.inventory.append(items.list[1])
		#game.player.inventory.append(items.list[2])
		if game_state == 'playing':
			current_map = map.Map('Starter Dungeon', 1, 1)
			self.play_game()

	# main game loop
	def play_game(self):
		global player_action
		libtcod.console_clear(0)
		util.initialize_fov()
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

			if game.player_move:
				monsters.spawn()
				game.player_move = False

	# save the game using the shelve module
	def save_game(self):
		if not os.path.exists('saves'):
			os.makedirs('saves')
		file = shelve.open('saves/' + player.name.lower(), 'n')
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
			util.msg_box('text', 'Saved games', contents='There are no save games.', center=True, box_height=5)
		else:
			choice = util.msg_box('save', 'Saved games', contents=savefiles, box_height=max(16, len(savefiles) + 4))
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
				self.play_game()

	# basic help text
	def help(self):
		contents = open('data/help.txt', 'r').read()
		util.msg_box('text', 'Help', contents=contents, box_width=40, box_height=22)

	# brings up the main menu
	def main_menu(self):
		global player_action
		player_action = None
		choice = 0
		#libtcod.console_credits()
		while not libtcod.console_is_window_closed():
			#libtcod.image_blit_2x(img, 0, 0, 0)
			libtcod.console_set_default_foreground(0, libtcod.light_yellow)
			libtcod.console_set_default_background(0, libtcod.black)
			libtcod.console_clear(0)
			libtcod.console_print_ex(0, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 5, libtcod.BKGND_SET, libtcod.CENTER, 'Immortal ' + VERSION)
			libtcod.console_print_ex(0, SCREEN_WIDTH / 2, SCREEN_HEIGHT - 2, libtcod.BKGND_SET, libtcod.CENTER, 'By Potatoman')
			contents = ['Start a new game', 'Load a saved game', 'Help', 'Options', 'Quit']
			choice = util.msg_box('main_menu', 'Main menu', contents=contents, box_width=21, box_height=len(contents) + 2, default=choice)

			if choice == 0:  # start new game
				self.new_game()
				if player_action == 'exit':
					break
			if choice == 1:  # load saved game
				self.load_game()
				if player_action == 'exit':
					break
			if choice == 2:  # help
				self.help()
			if choice == 4:  # quit
				break
