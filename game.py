import libtcodpy as libtcod
import shelve
import pickle
import os
import ctypes
from players import *
from item import *
from monster import *
import util
import commands
import map
import worldgen
import messages

VERSION = 'v0.3.0'
BUILD = '38'

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
fov_torch = False
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

terrain = [{'name': 'Mountain Peak', 'type': 'dirt', 'elevation': 0.950}, {'name': 'Mountains', 'type': 'dirt', 'elevation': 0.850},
		{'name': 'Hills', 'type': 'dirt', 'elevation': 0.700}, {'name': 'Forest', 'type': 'grass', 'elevation': 0.250},
		{'name': 'Plains', 'type': 'grass', 'elevation': 0.175}, {'name': 'Coast', 'type': 'sand', 'elevation': 0.120},
		{'name': 'Shore', 'type': 'shallow water', 'elevation': 0.110}, {'name': 'Sea', 'type': 'deep water', 'elevation': 0.060},
		{'name': 'Ocean', 'type': 'very deep water', 'elevation': 0.000}, {'name': 'Dungeon', 'type': 'wall', 'elevation': 0.000}
		]


class Game(object):
	def __init__(self):
		global img, font_width, font_height, message, rnd, con, panel, ps, fov_noise, savefiles, items, tiles, monsters
		self.load_settings()
		img = libtcod.image_load('title.png')
		if font == 'large':
			libtcod.console_set_custom_font('font-large.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
			font_width = 14
			font_height = 22
		else:
			libtcod.console_set_custom_font('font-small.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
		self.init_root_console()
		#libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Immortal ' + VERSION, False)
		libtcod.image_scale(img, SCREEN_WIDTH * 2, SCREEN_HEIGHT * 2)

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
		global MAP_WIDTH, MAP_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT, MESSAGE_WIDTH, PLAYER_STATS_HEIGHT, MESSAGE_Y
		user32 = ctypes.windll.user32
		desktop_width = user32.GetSystemMetrics(0)
		desktop_height = user32.GetSystemMetrics(1)
		max_width_size = (desktop_width / font_width) - 6
		max_height_size = (desktop_height / font_height) - 6
		if max_width_size > SCREEN_WIDTH:
			MAP_WIDTH = MAP_WIDTH + (max_width_size - SCREEN_WIDTH)
			if MAP_WIDTH > 74:
				MAP_WIDTH = 74
			MESSAGE_WIDTH = MAP_WIDTH
			SCREEN_WIDTH = MAP_WIDTH + PLAYER_STATS_WIDTH + 3
		if max_height_size > SCREEN_HEIGHT:
			MAP_HEIGHT = MAP_HEIGHT + (max_height_size - SCREEN_HEIGHT)
			if MAP_HEIGHT > 32:
				MAP_HEIGHT = 32
			SCREEN_HEIGHT = MAP_HEIGHT + MESSAGE_HEIGHT + 3
			PLAYER_STATS_HEIGHT = SCREEN_HEIGHT - 2
			MESSAGE_Y = MAP_HEIGHT + 2
		libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Immortal ' + VERSION, False)

	# new game setup
	def new_game(self):
		global message, player, char, game_state, worldmap, current_map
		cardinal = [-(WORLDMAP_WIDTH - 1), -(WORLDMAP_WIDTH), -(WORLDMAP_WIDTH + 1), -1, 1, WORLDMAP_WIDTH - 1, WORLDMAP_WIDTH, WORLDMAP_WIDTH + 1]
		message = messages.Message()
		player = Player()
		char = map.Object(libtcod.random_get_int(game.rnd, 40, 80), libtcod.random_get_int(game.rnd, 26, 46), player.icon, 'player', player.icon_color, blocks=True)
		game_state = create_character()
		if game_state == 'playing':
#			util.msg_box('text', contents='Generating world map...', center=True, box_width=50, box_height=5)
			contents = ["Generating world map..."]
			messages.box(None, None, (SCREEN_WIDTH - (len(max(contents, key=len)) + 20)) / 2, (SCREEN_HEIGHT - (len(contents) + 4)) / 2, len(max(contents, key=len)) + 20, len(contents) + 4, contents, input=False, align=libtcod.CENTER, nokeypress=True)
			worldmap = worldgen.World()
			current_map = map.Map('Wilderness', 'WD', 0, (worldmap.player_positiony * WORLDMAP_WIDTH) + worldmap.player_positionx, typ='Forest')
			for i in range(len(border_maps)):
				border_maps[i] = map.Map('Wilderness', 'WD', 0, (worldmap.player_positiony * WORLDMAP_WIDTH) + worldmap.player_positionx + cardinal[i], typ=util.find_terrain_type((worldmap.player_positiony * WORLDMAP_WIDTH) + worldmap.player_positionx + cardinal[i]))
			util.combine_maps()
			message.new("Welcome to Immortal, " + player.name + '!', player.turns, libtcod.Color(96, 212, 238))
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

			# player movement
			player_action = commands.handle_keys()
			if player_action == 'save':
				self.save_game()
				break
			if player_action == 'quit':
				util.death(True)
				break
			if player_action == 'exit':
				break

			# let monsters take their turn
			if player_move:
				monsters.spawn()
				for object in reversed(current_map.objects):
					if object.item != None:
						if object.item.is_active():
							object.delete()
						if object.item.is_expired() or ((game.player.turns >= (object.first_appearance + object.item.expiration)) and object.item.expiration > 0):
							object.delete()
					if object.entity != None:
						object.x, object.y = object.entity.take_turn(object.x, object.y)
				player_move = False

			# death screen summary
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
		file['fov_torch'] = fov_torch
		file['game_state'] = game_state
		file['times_saved'] = times_saved + 1
		file.close()

	# load the game using the shelve module
	def load_game(self):
		global worldmap, current_map, current_backup, border_maps, old_maps, player, message, fov_torch, game_state, times_saved, char, redraw_gui
		if len(savefiles) == 0:
#			util.msg_box('text', 'Saved games', contents='There are no saved games.', center=True, box_height=5)
			contents = ["There are no saved games."]
			messages.box('Saved games', None, (SCREEN_WIDTH - (len(max(contents, key=len)) + 20)) / 2, (SCREEN_HEIGHT - (len(contents) + 4)) / 2, len(max(contents, key=len)) + 20, len(contents) + 4, contents, input=False, align=libtcod.CENTER)
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
				fov_torch = file['fov_torch']
				game_state = file['game_state']
				times_saved = file['times_saved']
				file.close()
				char = current_map.objects[0]
				worldmap.create_map_images(1)
				self.play_game()

	# basic help text
	def help(self):
		contents = open('data/help.txt', 'r').read()
		contents = contents.split("\n")
#		util.msg_box('text', 'Help', contents=contents, box_width=40, box_height=26)
		messages.box('Help', None, (SCREEN_WIDTH - (len(max(contents, key=len)) + 20)) / 2, (SCREEN_HEIGHT - (len(contents) + 4)) / 2, len(max(contents, key=len)) + 20, len(contents) + 4, contents, input=False)

	# loading and changing game settings
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
#			util.msg_box('highscore', 'High scores', contents=highscore, box_width=SCREEN_WIDTH, box_height=SCREEN_HEIGHT)
			contents = []
			for (score, line1, line2) in highscore:
				contents.append(str(score).ljust(6) + line1)
				contents.append("      " + line2)
				contents.append(" ")
			messages.box('High scores', None, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, contents, input=False)
		else:
#			util.msg_box('text', 'High scores', contents="The high scores file is empty.", box_width=41, box_height=5, center=True)
			contents = ["The high scores file is empty."]
			messages.box('High scores', None, (SCREEN_WIDTH - (len(max(contents, key=len)) + 18)) / 2, (SCREEN_HEIGHT - (len(contents) + 4)) / 2, len(max(contents, key=len)) + 18, len(contents) + 4, contents, input=False, align=libtcod.CENTER)

	def load_high_scores(self):
		global highscore
		if os.path.exists('data/highscores.dat'):
			contents = open('data/highscores.dat', 'rb')
			highscore = pickle.load(contents)
			contents.close()

	# reset some variables after saving of quitting current game
	def reset_game(self):
		global savefiles, redraw_gui, fov_recompute
		savefiles = os.listdir('saves')
		redraw_gui = True
		fov_recompute = True

	# brings up the main menu
	def main_menu(self):
		choice = 0
		while not libtcod.console_is_window_closed():
			libtcod.console_clear(0)
			libtcod.image_blit_2x(img, 0, 0, 0)
			libtcod.console_set_default_foreground(0, libtcod.light_yellow)
			libtcod.console_print_ex(0, 10, 1, libtcod.BKGND_NONE, libtcod.LEFT, "#.")
			libtcod.console_print_ex(0, 10, 2, libtcod.BKGND_NONE, libtcod.LEFT, "##. .######.  .######.  .######.  .######.  .#######. .######.  .#")
			libtcod.console_print_ex(0, 10, 3, libtcod.BKGND_NONE, libtcod.LEFT, "#.# ## ## ##. ## ## ##. ##    ##. ##    ##.    #.#    ##    ##. ##")
			libtcod.console_print_ex(0, 10, 4, libtcod.BKGND_NONE, libtcod.LEFT, "#.# ## ## #.# ## ## #.# ##    #.# ##    #.#    #.#    ##    #.# ##")
			libtcod.console_print_ex(0, 10, 5, libtcod.BKGND_NONE, libtcod.LEFT, "#.# ## ## #.# ## ## #.# ##    #.# ## .####.    #.#    ####. #.# ##")
			libtcod.console_print_ex(0, 10, 6, libtcod.BKGND_NONE, libtcod.LEFT, "#.# ##    #.# ##    #.# ##    #.# ##    #.#    #.#    ##    #.# ##")
			libtcod.console_print_ex(0, 10, 7, libtcod.BKGND_NONE, libtcod.LEFT, "#.# ##    #.# ##    #.# ##    #.# ##    #.#    #.#    ##    #.# ##")
			libtcod.console_print_ex(0, 10, 8, libtcod.BKGND_NONE, libtcod.LEFT, "#.# ##    #.# ##    #.# ##    #.# ##    #.#    #.#    ##    #.# ##    ###")
			libtcod.console_print_ex(0, 10, 9, libtcod.BKGND_NONE, libtcod.LEFT, "##' ##    ##' ##    ##' `#######' `#    ##'    ##'    ##    ##' `#######'")
			libtcod.console_print_ex(0, 1, SCREEN_HEIGHT - 2, libtcod.BKGND_NONE, libtcod.LEFT, VERSION)
			libtcod.console_print_ex(0, SCREEN_WIDTH / 2, SCREEN_HEIGHT - 2, libtcod.BKGND_NONE, libtcod.CENTER, 'Copyright (c) 2012-13 -- Mr.Potatoman')
			contents = ['Start a new game', 'Load a saved game', 'Read the manual', 'Change settings', 'View high scores', 'Quit game']
			if choice == -1:
				choice = 0
#			choice = util.msg_box('main_menu', header=None, contents=contents, box_width=21, box_height=len(contents) + 2, default=choice)
			choice = messages.box(None, None, ((SCREEN_WIDTH - 4) - len(max(contents, key=len))) / 2, ((SCREEN_HEIGHT + 4) - len(contents)) / 2, len(max(contents, key=len)) + 4, len(contents) + 2, contents, choice)

			if choice == 0:  # start new game
				self.new_game()
				self.reset_game()
			if choice == 1:  # load saved game
				self.load_game()
				self.reset_game()
			if choice == 2:  # help
				self.help()
			if choice == 3:  # settings
				self.settings()
			if choice == 4:  # high scores
				self.show_high_scores()
			if choice == 5:  # quit
				for fade in range(255, 0, -8):
					libtcod.console_set_fade(fade, libtcod.black)
					libtcod.console_flush()
				break
