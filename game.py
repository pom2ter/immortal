import libtcodpy as libtcod
import shelve
import pickle
import os
import ctypes
from players import *
from messages import *
from item import *
from monster import *
import worldgen
import map
import commands
import util

VERSION = 'v0.2.3'
BUILD = '34'

#size of the gui windows
MAP_WIDTH = 70
MAP_HEIGHT = 28
MESSAGE_WIDTH = MAP_WIDTH
MESSAGE_HEIGHT = 5
PLAYER_STATS_WIDTH = 16
SCREEN_WIDTH = MAP_WIDTH + PLAYER_STATS_WIDTH + 3
SCREEN_HEIGHT = MAP_HEIGHT + MESSAGE_HEIGHT + 3
PLAYER_STATS_HEIGHT = SCREEN_HEIGHT - 2

WORLDMAP_WIDTH = 400
WORLDMAP_HEIGHT = 240

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

#fov
FOV_ALGO = 0
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 5
FOV_RADIUS = 9
SQUARED_TORCH_RADIUS = TORCH_RADIUS * TORCH_RADIUS
fov_recompute = True
fov_torch = True
fov_map = None
fov_noise = None
fov_torchx = 0.0

#dijkstra
path_dijk = None
path_recalculate = False
path_dx = 0
path_dy = 0

#different windows
con = 0
panel = 0
ps = 0

#worldmap
worldmap = None
hm = 0
hmcopy = 0
precipitation = 0
temperature = 0
mask = 0

#maps
current_map = None
current_backup = None
border_maps = [0] * 8
old_maps = []

#miscellaneous variables
char = None
savefiles = []
times_saved = 0
player_move = False
mouse_move = False
mouse = libtcod.Mouse()
rnd = None
killer = None
highscore = []
redraw_gui = True
font = 'small'
hp_anim = []
img = None
font_width = 12
font_height = 12
curx = 0
cury = 0


class Game(object):
	def __init__(self):
		global img, font_width, font_height, rnd, con, panel, ps, fov_noise, savefiles, items, tiles, monsters
		self.load_settings()
		#img = libtcod.image_load('title_screen2.png')
		if font == 'large':
			libtcod.console_set_custom_font('font-large.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
			font_width = 17
			font_height = 22
		else:
			libtcod.console_set_custom_font('font-small.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
		self.init_root_console()
		#libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Immortal ' + VERSION, False)

		libtcod.sys_set_fps(500)
		rnd = libtcod.random_new()
		con = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
		panel = libtcod.console_new(MESSAGE_WIDTH, MESSAGE_HEIGHT)
		ps = libtcod.console_new(PLAYER_STATS_WIDTH, PLAYER_STATS_HEIGHT)
		fov_noise = libtcod.noise_new(1, 1.0, 1.0)
		savefiles = os.listdir('saves')
		self.load_high_scores()
		items = ItemList()
		items.init_parser()
		tiles = map.TileList()
		tiles.init_parser()
		monsters = MonsterList()
		monsters.init_parser()
		self.main_menu()

	# create the root console based on desktop resolution and font size
	def init_root_console(self):
		global MAP_WIDTH, MAP_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT, MESSAGE_WIDTH, PLAYER_STATS_HEIGHT, MESSAGE_Y, buffer
		user32 = ctypes.windll.user32
		desktop_width = user32.GetSystemMetrics(0)
		desktop_height = user32.GetSystemMetrics(1)
		max_width_size = (desktop_width / font_width) - 6
		max_height_size = (desktop_height / font_height) - 6
		if max_width_size > SCREEN_WIDTH:
			MAP_WIDTH = MAP_WIDTH + (max_width_size - SCREEN_WIDTH)
			if MAP_WIDTH > 90:
				MAP_WIDTH = 90
			MESSAGE_WIDTH = MAP_WIDTH
			SCREEN_WIDTH = MAP_WIDTH + PLAYER_STATS_WIDTH + 3
		if max_height_size > SCREEN_HEIGHT:
			MAP_HEIGHT = MAP_HEIGHT + (max_height_size - SCREEN_HEIGHT)
			if MAP_HEIGHT > 54:
				MAP_HEIGHT = 54
			SCREEN_HEIGHT = MAP_HEIGHT + MESSAGE_HEIGHT + 3
			PLAYER_STATS_HEIGHT = SCREEN_HEIGHT - 2
			MESSAGE_Y = MAP_HEIGHT + 2
		libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Immortal ' + VERSION, False)

	# new game setup
	def new_game(self):
		global message, player, char, game_state, worldmap, current_map
		cardinal = [-(WORLDMAP_WIDTH - 1), -(WORLDMAP_WIDTH), -(WORLDMAP_WIDTH + 1), -1, 1, WORLDMAP_WIDTH - 1, WORLDMAP_WIDTH, WORLDMAP_WIDTH + 1]
		message = Message()
		player = Player()
		char = map.Object(50, 50, player.icon, 'player', player.icon_color, blocks=True)
		game_state = create_character()
		if game_state == 'playing':
			util.msg_box('text', contents='Generating world map...', center=True, box_width=50, box_height=5)
			worldmap = worldgen.World()
			current_map = map.Map('Wilderness', 'WD', 0, (worldmap.player_positiony * WORLDMAP_WIDTH) + worldmap.player_positionx, typ='Forest')
			for i in range(len(border_maps)):
				border_maps[i] = map.Map('Wilderness', 'WD', 0, (worldmap.player_positiony * WORLDMAP_WIDTH) + worldmap.player_positionx + cardinal[i], typ='Forest')
			util.combine_maps()
			self.play_game()

	# main game loop
	def play_game(self):
		global player_action, redraw_gui, player_move
		libtcod.console_clear(0)
		util.initialize_fov()
		while not libtcod.console_is_window_closed():
			if redraw_gui:
				util.render_gui(libtcod.red)
				util.render_message_panel()
				util.render_player_stats_panel()
				redraw_gui = False
			util.render_map()
			libtcod.console_flush()

			#player movement
			player_action = commands.handle_keys()
			if player_action == 'save':
				self.save_game()
				player_action = 'exit'
			if player_action == 'exit':
				break

			#let monsters take their turn
			if player_move:
				monsters.spawn()
				for object in reversed(current_map.objects):
					if object.item != None:
						if object.item.type == "corpse" and (player.turns - object.first_appearance > 500):
							object.delete()
					if object.entity != None:
						object.x, object.y = object.entity.take_turn(object.x, object.y)
				player_move = False

			#death screen summary
			if game_state == 'death':
				key = libtcod.Key()
				util.render_map()
				libtcod.console_flush()
				while not key.vk == libtcod.KEY_SPACE:
					libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS, key, libtcod.Mouse(), True)
				util.death()
				player_action = 'exit'
				break

	# save the game using the shelve module
	def save_game(self):
		global worldmap, current_map, border_maps, old_maps, player, message, game_state, times_saved
		if not os.path.exists('saves'):
			os.makedirs('saves')
		file = shelve.open('saves/' + player.name.lower(), 'n')
		file['worldmap'] = worldmap
		file['current_map'] = current_map
		file['current_backup'] = current_backup
		file['border_maps'] = border_maps
		file['maps'] = old_maps
		file['player'] = player
		file['messages'] = message
		file['game_state'] = game_state
		file['times_saved'] = times_saved + 1
		file.close()

	# load the game using the shelve module
	def load_game(self):
		global worldmap, current_map, current_backup, border_maps, old_maps, player, message, game_state, times_saved, char
		if len(savefiles) == 0:
			util.msg_box('text', 'Saved games', contents='There are no save games.', center=True, box_height=5)
		else:
			desc = []
			for i in range(len(savefiles)):
				file = shelve.open('saves/' + savefiles[i], 'r')
				file['worldmap']
				file['current_map']
				file['maps']
				pl = file['player']
				desc.append(savefiles[i] + ', a level ' + str(pl.level) + ' ' + pl.gender + ' ' + pl.race + ' ' + pl.profession)
				file.close()
			choice = util.msg_box('save', 'Saved games', contents=desc, box_height=max(16, len(savefiles) + 4))
			if choice != -1:
				file = shelve.open('saves/' + savefiles[choice], 'r')
				worldmap = file['worldmap']
				current_map = file['current_map']
				current_backup = file['current_backup']
				border_maps = file['border_maps']
				old_maps = file['maps']
				player = file['player']
				message = file['messages']
				game_state = file['game_state']
				times_saved = file['times_saved']
				file.close()
				char = current_map.objects[0]
				worldmap.create_map_images(1)
				self.play_game()

	# basic help text
	def help(self):
		contents = open('data/help.txt', 'r').read()
		util.msg_box('text', 'Help', contents=contents, box_width=40, box_height=25)

	# loading and changin game settings
	def settings(self):
		util.msg_box('settings', 'Settings', contents=font, box_width=40, box_height=8, center=True)
		self.load_settings()

	def load_settings(self):
		global font
		if os.path.exists('settings.ini'):
			contents = open('settings.ini', 'r')
			for line in contents:
				font = line.rstrip()
			if font != 'large':
				font = 'small'
			contents.close()

	# loading and showing the high scores screen
	def show_high_scores(self):
		if os.path.exists('data/highscores.dat'):
			self.load_high_scores()
			util.msg_box('highscore', 'High scores', contents=highscore, box_width=SCREEN_WIDTH, box_height=SCREEN_HEIGHT)
		else:
			util.msg_box('text', 'High scores', contents="The high scores file is empty.", box_width=41, box_height=5, center=True)

	def load_high_scores(self):
		global highscore
		if os.path.exists('data/highscores.dat'):
			contents = open('data/highscores.dat', 'rb')
			highscore = pickle.load(contents)
			contents.close()

	# brings up the main menu
	def main_menu(self):
		global player_action
		player_action = None
		choice = 0
		#libtcod.console_credits()
		while not libtcod.console_is_window_closed():
			libtcod.console_set_default_foreground(0, libtcod.light_yellow)
			libtcod.console_set_default_background(0, libtcod.black)
			libtcod.console_clear(0)
			#libtcod.image_blit_2x(img, 0, 0, 0)
			#libtcod.image_blit(img, 0, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, libtcod.BKGND_SET, 1.0, 1.0, 0.0)
			contents = ['Start a new game', 'Load a saved game', 'Help', 'Settings', 'High Scores', 'Quit']
			libtcod.console_print_ex(0, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - len(contents), libtcod.BKGND_SET, libtcod.CENTER, 'Immortal ' + VERSION)
			libtcod.console_print_ex(0, SCREEN_WIDTH / 2, SCREEN_HEIGHT - 2, libtcod.BKGND_SET, libtcod.CENTER, 'By Potatoman')
			if choice == -1:
				choice = 0
			choice = util.msg_box('main_menu', header=None, contents=contents, box_width=21, box_height=len(contents) + 2, default=choice)

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
			if choice == 3:  # settings
				self.settings()
			if choice == 4:  # high scores
				self.show_high_scores()
			if choice == 5:  # quit
				break
