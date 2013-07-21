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
import effects
import death
import debug as dbg

VERSION = 'v0.3.3'

#size of the gui windows
MAP_WIDTH = 71
MAP_HEIGHT = 31
MESSAGE_WIDTH = MAP_WIDTH
MESSAGE_HEIGHT = 5
PLAYER_STATS_WIDTH = 18
SCREEN_WIDTH = MAP_WIDTH + PLAYER_STATS_WIDTH + 3
SCREEN_HEIGHT = MAP_HEIGHT + MESSAGE_HEIGHT + 3
PLAYER_STATS_HEIGHT = SCREEN_HEIGHT - 2

WORLDMAP_WIDTH = 400
WORLDMAP_HEIGHT = 240
MAX_THREAT_LEVEL = 20

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
fov_torchx = 0.0

#dijkstra
path_dijk = None
path_dx = -1
path_dy = -1

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

#settings
setting_font = 'small'
setting_history = 50

#miscellaneous variables
char = None
times_saved = 0
player_move = False
mouse_move = False
mouse = libtcod.Mouse()
killer = None
highscore = []
hp_anim = []
font_width = 10
font_height = 16
curx = 0
cury = 0
turns = 0
traps = []
old_msg = 0
draw_gui = True
draw_map = True

# thanatos, draconis, valamar, otatop, maurice the goblin
# mountains peak type, transitions
# caverns, maze types
# scrolling, lockpicks, chest
# burdened, food, money
# curse, bless
# apprentice, journeyman, adept, master

terrain = [{'name': 'Mountain Peak', 'type': 'dirt', 'elevation': 0.950}, {'name': 'Mountains', 'type': 'dirt', 'elevation': 0.850},
		{'name': 'Hills', 'type': 'dirt', 'elevation': 0.700}, {'name': 'Forest', 'type': 'grass', 'elevation': 0.250},
		{'name': 'Plains', 'type': 'grass', 'elevation': 0.175}, {'name': 'Coast', 'type': 'sand', 'elevation': 0.120},
		{'name': 'Shore', 'type': 'shallow water', 'elevation': 0.110}, {'name': 'Sea', 'type': 'deep water', 'elevation': 0.060},
		{'name': 'Ocean', 'type': 'very deep water', 'elevation': 0.000}, {'name': 'Dungeon', 'type': 'wall', 'elevation': 0.000}]

months = ['Phoenix', 'Manticore', 'Hydra', 'Golem', 'Centaur', 'Siren', 'Dragon', 'Werewolf', 'Gargoyle', 'Kraken', 'Basilisk', 'Unicorn']


class Game(object):
	def __init__(self):
		global debug, img, font_width, font_height, rnd, con, panel, ps, fov_noise, savefiles, baseitems, prefix, suffix, tiles, monsters
		self.load_settings()
		debug = dbg.Debug()
		debug.enable = True
		img = libtcod.image_load('title.png')
		if setting_font == 'large':
			libtcod.console_set_custom_font('font-large.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
			font_width = 14
			font_height = 22
		else:
			libtcod.console_set_custom_font('font-small.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
		os.putenv("SDL_VIDEO_CENTERED", "1")
		self.init_root_console()
		#libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Immortal ' + VERSION, False)
		libtcod.image_scale(img, SCREEN_WIDTH * 2, SCREEN_HEIGHT * 2)

		libtcod.sys_set_fps(500)
		rnd = libtcod.random_new()
		con = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
		panel = libtcod.console_new(MESSAGE_WIDTH, MESSAGE_HEIGHT)
		ps = libtcod.console_new(PLAYER_STATS_WIDTH, PLAYER_STATS_HEIGHT)
		fov_noise = libtcod.noise_new(1, 1.0, 1.0)
		if not os.path.exists('saves'):
			os.makedirs('saves')
		savefiles = os.listdir('saves')
		self.load_high_scores()
		baseitems = BaseItemList()
		baseitems.init_parser()
		prefix = PrefixList()
		prefix.init_parser()
		suffix = SuffixList()
		suffix.init_parser()
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
			if MAP_WIDTH > 71:
				MAP_WIDTH = 71
			MESSAGE_WIDTH = MAP_WIDTH
			SCREEN_WIDTH = MAP_WIDTH + PLAYER_STATS_WIDTH + 3
		if max_height_size > SCREEN_HEIGHT:
			MAP_HEIGHT = MAP_HEIGHT + (max_height_size - SCREEN_HEIGHT)
			if MAP_HEIGHT > 31:
				MAP_HEIGHT = 31
			SCREEN_HEIGHT = MAP_HEIGHT + MESSAGE_HEIGHT + 3
			PLAYER_STATS_HEIGHT = SCREEN_HEIGHT - 2
			MESSAGE_Y = MAP_HEIGHT + 2
		libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Immortal ' + VERSION, False)

	# new game setup
	def new_game(self):
		global message, player, char, game_state, worldmap, current_map, gametime
		cardinal = [-(WORLDMAP_WIDTH - 1), -(WORLDMAP_WIDTH), -(WORLDMAP_WIDTH + 1), -1, 1, WORLDMAP_WIDTH - 1, WORLDMAP_WIDTH, WORLDMAP_WIDTH + 1]
		message = messages.Message()
		player = Player()
		char = map.Object(libtcod.random_get_int(rnd, 40, 80), libtcod.random_get_int(rnd, 26, 46), player.icon, 'player', player.icon_color, blocks=True)
		game_state = create_character()
		if game_state == 'playing':
			contents = ['Generating world map...']
			messages.box(None, None, 'center_screenx', 'center_screeny', len(max(contents, key=len)) + 16, len(contents) + 4, contents, input=False, align=libtcod.CENTER, nokeypress=True)
			worldmap = worldgen.World()
			current_map = map.Map('Wilderness', 'WD', 0, (worldmap.player_positiony * WORLDMAP_WIDTH) + worldmap.player_positionx, typ=map.find_terrain_type((worldmap.player_positiony * WORLDMAP_WIDTH) + worldmap.player_positionx))
			for i in range(len(border_maps)):
				border_maps[i] = map.Map('Wilderness', 'WD', 0, (worldmap.player_positiony * WORLDMAP_WIDTH) + worldmap.player_positionx + cardinal[i], typ=map.find_terrain_type((worldmap.player_positiony * WORLDMAP_WIDTH) + worldmap.player_positionx + cardinal[i]))
			map.combine_maps()
			message.new('Welcome to Immortal, ' + player.name + '!', turns, libtcod.Color(96, 212, 238))
			gametime = Time()
			self.play_game()

	# main game loop
	def play_game(self):
		global player_action, draw_gui, player_move
		libtcod.console_clear(0)
		util.initialize_fov()
		while not libtcod.console_is_window_closed():
			if draw_gui:
				util.render_gui(libtcod.red)
				util.render_message_panel()
				util.render_player_stats_panel()
				draw_gui = False
			util.render_map()
			libtcod.console_flush()

			# player movement
			if not game.player.is_disabled():
				player_action = commands.keyboard_commands()
			else:
				util.add_turn()
			if player_action == 'save':
				self.save_game()
				break
			if player_action == 'quit':
				death.death_screen(True)
				break
			if player_action == 'exit':
				break

			# let monsters take their turn
			if player_move:
				monsters.spawn()
				for obj in reversed(current_map.objects):
					if obj.item is not None:
						if obj.item.is_active():
							obj.delete()
						if obj.item.is_expired() or ((turns >= (obj.first_appearance + obj.item.expiration)) and obj.item.expiration > 0):
							obj.delete()
					if obj.entity is not None and game_state != 'death':
						if not obj.entity.is_disabled():
							obj.x, obj.y = obj.entity.take_turn(obj.x, obj.y)
							if game.current_map.tile[obj.x][obj.y]['type'] == 'trap' and not obj.entity.is_above_ground() and obj.entity.can_move(obj.x, obj.y):
								if game.current_map.is_invisible(obj.x, obj.y):
									util.spring_trap(obj.x, obj.y, obj.entity.article.capitalize() + obj.entity.get_name())
								elif libtcod.map_is_in_fov(game.fov_map, obj.x, obj.y):
									game.message.new('The ' + obj.entity.get_name() + ' sidestep the ' + game.current_map.tile[obj.x][obj.y]['name'], game.turns)
						obj.entity.check_condition(obj.x, obj.y)
						if obj.entity.is_dead():
							if libtcod.map_is_in_fov(game.fov_map, obj.x, obj.y):
								game.message.new('The ' + obj.entity.get_name() + ' dies!', game.turns, libtcod.light_orange)
							else:
								game.message.new('You hear a dying scream.', game.turns)
							obj.entity.loot(obj.x, obj.y)
							obj.delete()
				if game_state != 'death':
					effects.check_active_effects()
				player_move = False

			# death screen summary
			if game_state == 'death':
				key = libtcod.Key()
				util.render_map()
				libtcod.console_flush()
				while not key.vk == libtcod.KEY_SPACE:
					libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS, key, libtcod.Mouse(), True)
				death.death_screen()
				player_action = 'exit'
				break

	# save the game using the shelve module
	def save_game(self):
		global old_maps
		contents = ['Saving.....']
		messages.box(None, None, 'center_screenx', 'center_screeny', len(max(contents, key=len)) + 28, len(contents) + 4, contents, input=False, align=libtcod.CENTER, nokeypress=True)
		if current_map.location_id == 0:
			map.decombine_maps()
			old_maps.append(current_map)
			for i in range(len(border_maps)):
				old_maps.append(border_maps[i])

		file = shelve.open('saves/' + player.name.lower(), 'n')
		file['worldmap'] = worldmap
		file['current_map'] = current_map
		file['maps'] = old_maps
		file['player'] = player
		file['messages'] = message
		file['turns'] = turns
		file['gametime'] = gametime
		file['fov_torch'] = fov_torch
		file['game_state'] = game_state
		file['times_saved'] = times_saved + 1
		file.close()

	# load the game using the shelve module
	def load_game(self):
		global worldmap, current_map, current_backup, border_maps, old_maps, player, message, turns, gametime, fov_torch, game_state, times_saved, char, draw_gui
		if len(savefiles) == 0:
			contents = ['There are no saved games.']
			messages.box('Saved games', None, 'center_screenx', 'center_screeny', len(max(contents, key=len)) + 16, len(contents) + 4, contents, input=False, align=libtcod.CENTER)
		else:
			desc = []
			for i in range(len(savefiles)):
				file = shelve.open('saves/' + savefiles[i], 'r')
				pl = file['player']
				desc.append(savefiles[i] + ', a level ' + str(pl.level) + ' ' + pl.gender + ' ' + pl.race + ' ' + pl.profession)
				file.close()
			choice = messages.box('Saved games', None, (SCREEN_WIDTH - (max(60, len(max(desc, key=len)) + 20))) / 2, ((SCREEN_HEIGHT + 1) - max(16, len(desc) + 4)) / 2, max(60, len(max(desc, key=len)) + 20), max(16, len(desc) + 4), desc, step=2, mouse_exit=True)
			if choice != -1:
				contents = ['Loading.....']
				messages.box(None, None, 'center_screenx', 'center_screeny', len(max(contents, key=len)) + 16, len(contents) + 4, contents, input=False, align=libtcod.CENTER, nokeypress=True)
				file = shelve.open('saves/' + savefiles[choice], 'r')
				player = file['player']
				worldmap = file['worldmap']
				current_map = file['current_map']
				old_maps = file['maps']
				message = file['messages']
				turns = file['turns']
				gametime = file['gametime']
				fov_torch = file['fov_torch']
				game_state = file['game_state']
				times_saved = file['times_saved']
				file.close()
				char = current_map.objects[0]
				worldmap.create_map_images(1)
				message.empty()
				message.trim_history()
				message.new('Welcome back, ' + player.name + '!', turns, libtcod.Color(96, 212, 238))
				if current_map.location_id == 0:
					map.load_old_maps(0, current_map.location_level)
					map.combine_maps()
				current_map.check_player_position()
				#print worldmap.dungeons
				self.play_game()

	# basic help text
	# stuff to do: change manual system
	def help(self):
		contents = open('data/help.txt', 'r').read()
		contents = contents.split('\n')
		messages.box('Help', None, 'center_screenx', 'center_screeny', len(max(contents, key=len)) + 16, len(contents) + 4, contents, input=False)

	# brings up settings menu
	def settings(self):
		width, height = 44, 9
		box = libtcod.console_new(width, height)
		messages.box_gui(box, 0, 0, width, height, libtcod.green)
		libtcod.console_set_default_foreground(box, libtcod.black)
		libtcod.console_set_default_background(box, libtcod.green)
		libtcod.console_print_ex(box, 20, 0, libtcod.BKGND_SET, libtcod.CENTER, ' Settings ')
		libtcod.console_set_default_foreground(box, libtcod.white)
		util.change_settings(box, width, height, blitmap=False)
		self.load_settings()

	# load game settings
	# stuff to do: add more options
	def load_settings(self):
		global setting_font, setting_history
		if os.path.exists('settings.ini'):
			contents = open('settings.ini', 'r')
			while 1:
				line = contents.readline().rstrip()
				if line == '[Font]':
					setting_font = contents.readline().rstrip()
				if line == '[History]':
					setting_history = int(contents.readline().rstrip())
				if not line:
					break
			contents.close()
			if setting_font != 'large':
				setting_font = 'small'
			if not setting_history in range(50, 1000):
				setting_history = 50

	# loading and showing the high scores screen
	def show_high_scores(self):
		if os.path.exists('highscores.dat'):
			self.load_high_scores()
			contents = []
			for (score, line1, line2) in highscore:
				contents.append(str(score).ljust(6) + line1)
				contents.append('      ' + line2)
				contents.append(' ')
			messages.box('High scores', None, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, contents, input=False)
		else:
			contents = ['The high scores file is empty.']
			messages.box('High scores', None, 'center_screenx', 'center_screeny', len(max(contents, key=len)) + 16, len(contents) + 4, contents, input=False, align=libtcod.CENTER)

	def load_high_scores(self):
		global highscore
		if os.path.exists('highscores.dat'):
			contents = open('highscores.dat', 'rb')
			highscore = pickle.load(contents)
			contents.close()

	# reset some variables after saving or quitting current game
	def reset_game(self):
		global savefiles, turns, old_msg, draw_gui, fov_recompute, draw_map
		savefiles = os.listdir('saves')
		turns = 0
		old_msg = 0
		draw_gui = True
		draw_map = True
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
