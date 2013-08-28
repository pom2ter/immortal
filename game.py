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
import mapgen
import worldgen
import chargen
import messages
import effects
import death
import debug as dbg

VERSION = '0.3.4.5'

#size of the gui windows
MAP_WIDTH = 71
MAP_HEIGHT = 31
MESSAGE_WIDTH = MAP_WIDTH
MESSAGE_HEIGHT = 6
PLAYER_STATS_WIDTH = 22
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
heightmap = 0
precipitation = 0
temperature = 0
biome = 0

#maps
current_map = None
current_backup = None
border_maps = [0] * 8
old_maps = []

#settings
setting_font = 'small'
setting_history = 50
setting_fullscreen = 'off'

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

#character generation stuff
RACES = ['Human', 'Elf', 'Dwarf', 'Halfling']
CLASSES = ['Fighter', 'Rogue', 'Priest', 'Mage', 'Explorer']
GENDER = ['Male', 'Female']
RACE_DESC = ["Humans are the most common race in the Realm. They are average at everything and thus don't have any racial bonuses or penalties.",
			"Elves are more dedicated to magic than combat. They have bonuses to intelligence and wisdow but penalties to strength and endurance.",
			"Dwarves are the strongest (but stupidest) people in the Realm. They are primarily used has 'tanks'. They have a bonus to strength and endurance and a penalty to everything else.",
			"Halfling are a small, friendly and clever folk, known for their thieving prowess. They have a bonus to dexterity and intelligence but a penalty to strength and wisdom."]
CLASS_DESC = ["Fighters are master of arms especially melee weapons but their magic skills are very limited. Their primary attribute is strength. This is the perfect class for dwarves. They start with moderate knowledge in all combat skills except ranged weapons.",
			"Rogues uses stealth to survive rather than weapons or magic. Their primary attribute is dexterity. This is a good class for halflings. They start with moderate knowledge in thieving skills.",
			"Priests are decent fighters that can use defensive and curative magic. Their primary attribute is wisdom. They start with some knowledge in both combat and magic skills.",
			"Mages are the opposite of fighters; great with magic, weak with weapons (except staves). Their primary attribute is intelligence. This is a good class for elves. They start with moderate knowledge in all magic skills.",
			"An explorer is basically a classless character so he doesnt have any specialties but gains more skill points per level to compensate. This 'class' is for those who likes to fine-tune their character from the very beginning."]
BASE_STATS = [[9, 9, 9, 9, 9], [12, 9, 7, 8, 11], [10, 12, 8, 9, 8], [10, 8, 9, 12, 8], [7, 9, 13, 10, 8], [9, 9, 9, 9, 9],
				[7, 9, 11, 10, 8], [10, 9, 9, 9, 10], [8, 12, 10, 10, 7], [8, 8, 11, 13, 7], [5, 9, 15, 11, 7], [7, 9, 11, 10, 8],
				[11, 7, 7, 8, 12], [14, 7, 5, 7, 14], [12, 10, 6, 8, 11], [12, 6, 7, 11, 11], [9, 7, 11, 9, 11], [11, 7, 7, 8, 12],
				[8, 10, 10, 8, 9], [11, 10, 8, 7, 11], [9, 13, 9, 8, 8], [9, 9, 10, 11, 8], [6, 10, 14, 9, 8], [8, 10, 10, 8, 9]]
EXPERIENCE_TABLES = [0, 100, 250, 500, 800, 1250, 1750, 2450, 3250, 4150, 5200, 6400, 7800, 9400, 11200, 13200, 16400, 18800, 21400, 24200, 27000]
FIGHTER_HP_GAIN = 10
FIGHTER_MP_GAIN = 2
FIGHTER_STAMINA_GAIN = 8
ROGUE_HP_GAIN = 8
ROGUE_MP_GAIN = 4
ROGUE_STAMINA_GAIN = 6
PRIEST_HP_GAIN = 6
PRIEST_MP_GAIN = 8
PRIEST_STAMINA_GAIN = 5
MAGE_HP_GAIN = 4
MAGE_MP_GAIN = 10
MAGE_STAMINA_GAIN = 2
EXPLORER_HP_GAIN = 6
EXPLORER_MP_GAIN = 6
EXPLORER_STAMINA_GAIN = 4

terrain = {'Mountain Peak': {'type': 'high mountains', 'elevation': 0.950, 'maxelev': 1.000},
		'Mountains': {'type': 'mountains', 'elevation': 0.825, 'maxelev': 0.949},
		'High Hills': {'type': 'hills', 'elevation': 0.700, 'maxelev': 0.824},
		'Low Hills': {'type': 'medium grass', 'elevation': 0.575, 'maxelev': 0.699},
		'Forest': {'type': 'grass', 'elevation': 0.230, 'maxelev': 0.574},
		'Plains': {'type': 'grass', 'elevation': 0.140, 'maxelev': 0.229},
		'Coast': {'type': 'sand', 'elevation': 0.120, 'maxelev': 0.139},
		'Shore': {'type': 'shallow water', 'elevation': 0.110, 'maxelev': 0.119},
		'Sea': {'type': 'deep water', 'elevation': 0.070, 'maxelev': 0.109},
		'Ocean': {'type': 'very deep water', 'elevation': 0.000, 'maxelev': 0.069},
		'Dungeon': {'type': 'wall', 'elevation': 2.000, 'maxelev': 2.000},
		'Cave': {'type': 'cavern wall', 'elevation': 3.000, 'maxelev': 3.000},
		'Maze': {'type': 'wall', 'elevation': 4.000, 'maxelev': 4.000}}

hunger_levels = {'Bloated': {'start': 0, 'end': 249},
		'Full': {'start': 250, 'end': 499},
		'Normal': {'start': 500, 'end': 1599},
		'Hungry': {'start': 1600, 'end': 1799},
		'Famished': {'start': 1800, 'end': 1999},
		'Starving': {'start': 2000, 'end': 9999}}

fonts = {'small': {'file': 'font-small.png', 'width': 10, 'height': 16},
		'medium': {'file': 'font-medium.png', 'width': 12, 'height': 19},
		'large': {'file': 'font-large.png', 'width': 14, 'height': 22}}

months = ['Phoenix', 'Manticore', 'Hydra', 'Golem', 'Centaur', 'Siren', 'Dragon', 'Werewolf', 'Gargoyle', 'Kraken', 'Basilisk', 'Unicorn']

# to-do's...
# thanatos, draconis, valamar, otatop, maurice the goblin
# scrolling, lockpicks, chest
# curse, bless
# monsters powers, location
# ranged combat
# spells, scrolls, tomes, npcs, towns, quests...
# transitions, worldmap travel?
# monsters blocks
# worldmap minmax each type


class Game(object):
	def __init__(self):
		global debug, font_width, font_height, rnd, con, panel, ps, fov_noise, savefiles, baseitems, prefix, suffix, tiles, monsters
		self.load_settings()
		debug = dbg.Debug()
		debug.enable = True
		for key, value in fonts.items():
			if setting_font == key:
				libtcod.console_set_custom_font(value['file'], libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
				font_width = value['width']
				font_height = value['height']
		self.init_root_console()
		#libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Immortal ' + VERSION, False)

		rnd = libtcod.random_new()
		con = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
		panel = libtcod.console_new(MESSAGE_WIDTH, MESSAGE_HEIGHT)
		ps = libtcod.console_new(PLAYER_STATS_WIDTH, PLAYER_STATS_HEIGHT)
		fov_noise = libtcod.noise_new(1, 1.0, 1.0)
		savefiles = os.listdir('saves')
		self.load_high_scores()
		baseitems = BaseItemList()
		baseitems.init_parser()
		prefix = PrefixList()
		prefix.init_parser()
		suffix = SuffixList()
		suffix.init_parser()
		tiles = mapgen.TileList()
		tiles.init_parser()
		monsters = MonsterList()
		monsters.init_parser()
		self.main_menu()

	# create the root console based on desktop resolution and font size
	def init_root_console(self):
		global MAP_WIDTH, MAP_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT, MESSAGE_WIDTH, PLAYER_STATS_HEIGHT, MESSAGE_Y, setting_fullscreen
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
		if setting_fullscreen == 'on':
			libtcod.console_set_fullscreen(True)

	# new game setup
	def new_game(self):
		global message, player, char, game_state, worldmap, current_map, gametime
		cardinal = [-(WORLDMAP_WIDTH - 1), -(WORLDMAP_WIDTH), -(WORLDMAP_WIDTH + 1), -1, 1, WORLDMAP_WIDTH - 1, WORLDMAP_WIDTH, WORLDMAP_WIDTH + 1]
		message = messages.Message()
		player = Player()
		char = mapgen.Object(libtcod.random_get_int(rnd, 40, 80), libtcod.random_get_int(rnd, 26, 46), player.icon, 'player', player.icon_color, blocks=True)
		game_state = chargen.create_character()
		if game_state == 'playing':
			contents = ['Generating world map...']
			messages.box(None, None, 'center_screenx', 'center_screeny', len(max(contents, key=len)) + 16, len(contents) + 4, contents, input=False, align=libtcod.CENTER, nokeypress=True)
			worldmap = worldgen.World()
			current_map = mapgen.Map('Wilderness', 'WD', 0, (worldmap.player_positiony * WORLDMAP_WIDTH) + worldmap.player_positionx, type=mapgen.find_terrain_type((worldmap.player_positiony * WORLDMAP_WIDTH) + worldmap.player_positionx))
			for i in range(len(border_maps)):
				border_maps[i] = mapgen.Map('Wilderness', 'WD', 0, (worldmap.player_positiony * WORLDMAP_WIDTH) + worldmap.player_positionx + cardinal[i], type=mapgen.find_terrain_type((worldmap.player_positiony * WORLDMAP_WIDTH) + worldmap.player_positionx + cardinal[i]))
			mapgen.combine_maps()
			message.new('Welcome to Immortal, ' + player.name + '!', turns, libtcod.Color(96, 212, 238))
			gametime = Time()
			self.play_game()

	# main game loop
	def play_game(self):
		global player_action, draw_gui, player_move
		libtcod.console_clear(0)
		util.initialize_fov()
		player_action = ''
		while not libtcod.console_is_window_closed():
			if draw_gui:
				util.render_gui(libtcod.Color(70, 80, 90))
				util.render_message_panel()
				util.render_player_stats_panel()
				draw_gui = False
			util.render_map()
			libtcod.console_flush()

			# player movement
			if not game.player.is_disabled() and not ('overburdened' in game.player.flags and game.turns % 3 == 0):
				player_action = commands.keyboard_commands()
			else:
				player_move = True
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
				for obj in reversed(current_map.objects):
					if game_state != 'death':
						if obj.item:
							if obj.item.is_active():
								obj.delete()
							if obj.item.is_expired() or ((turns >= (obj.first_appearance + obj.item.expiration)) and obj.item.expiration > 0):
								obj.delete()
						if obj.entity:
							if not obj.entity.is_disabled():
								obj.x, obj.y = obj.entity.take_turn(obj.x, obj.y)
								if game.current_map.tile[obj.x][obj.y]['type'] == 'trap' and not obj.entity.is_above_ground() and obj.entity.can_move(obj.x, obj.y):
									if game.current_map.tile_is_invisible(obj.x, obj.y):
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
					monsters.spawn()
					effects.check_active_effects()
					util.add_turn()
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
			mapgen.decombine_maps()
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
		if not savefiles:
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
					mapgen.load_old_maps(0, current_map.location_level)
					mapgen.combine_maps()
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
		width, height = 44, 10
		box = libtcod.console_new(width, height)
		messages.box_gui(box, 0, 0, width, height, libtcod.green)
		libtcod.console_set_default_foreground(box, libtcod.black)
		libtcod.console_set_default_background(box, libtcod.green)
		libtcod.console_print_ex(box, 20, 0, libtcod.BKGND_SET, libtcod.CENTER, ' Settings ')
		libtcod.console_set_default_foreground(box, libtcod.white)
		util.change_settings(box, width, height, blitmap=False)
		libtcod.console_delete(box)
		self.load_settings()

	# load game settings
	# stuff to do: add more options
	def load_settings(self):
		global setting_font, setting_history, setting_fullscreen
		if os.path.exists('settings.ini'):
			contents = open('settings.ini', 'r')
			while 1:
				line = contents.readline().rstrip()
				if line == '[Font]':
					setting_font = contents.readline().rstrip()
				if line == '[History]':
					setting_history = int(contents.readline().rstrip())
				if line == '[Fullscreen]':
					setting_fullscreen = contents.readline().rstrip()
				if not line:
					break
			contents.close()
			if not any(setting_font == i for i in ['small', 'medium', 'large']):
				setting_font = 'small'
			if not setting_history in range(50, 1000):
				setting_history = 50
			if not any(setting_fullscreen == i for i in ['on', 'off']):
				setting_fullscreen = 'off'

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
		contents = ['Start a new game  ', 'Load a saved game  ', 'Read the manual  ', 'Change settings  ', 'View high scores  ', 'Quit game  ']
		img = libtcod.image_load('title.png')
		libtcod.image_scale(img, int(SCREEN_WIDTH * 2.2), SCREEN_HEIGHT * 2)
		choice = 0

		while not libtcod.console_is_window_closed():
			libtcod.console_clear(0)
			libtcod.image_blit_2x(img, 0, 0, 0)
			libtcod.console_set_default_foreground(0, libtcod.light_yellow)
			libtcod.console_print_ex(0, 2, SCREEN_HEIGHT - 2, libtcod.BKGND_NONE, libtcod.LEFT, 'Immortal ' + VERSION)
			libtcod.console_print_ex(0, SCREEN_WIDTH - 3, SCREEN_HEIGHT - 2, libtcod.BKGND_NONE, libtcod.RIGHT, 'Copyright (c) 2012-13 -- Mr.Potatoman')
			libtcod.console_print_ex(0, SCREEN_WIDTH - 5, SCREEN_HEIGHT - 22, libtcod.BKGND_NONE, libtcod.RIGHT, 'Main Menu')
			if choice == -1:
				choice = 0
			choice = messages.box(None, None, (SCREEN_WIDTH - len(max(contents, key=len)) - 6), ((SCREEN_HEIGHT + 4) - len(contents)) / 2, len(max(contents, key=len)) + 5, len(contents) + 2, contents, choice, color=None, align=libtcod.RIGHT)

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
