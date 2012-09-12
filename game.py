import libtcodpy as libtcod
import shelve
import pickle
import os
from players import *
from messages import *
from item import *
from monster import *
import worldgen
import map
import commands
import util

VERSION = 'v0.2.2'
BUILD = '31'

#size of the map
MAP_WIDTH = 70
MAP_HEIGHT = 28

#actual size of the window
PLAYER_STATS_WIDTH = 16
MESSAGE_WIDTH = MAP_WIDTH
MESSAGE_HEIGHT = 5
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
MAX_ROOMS = 30
MAX_MONSTERS_PER_LEVEL = 8
MAX_ITEMS_PER_LEVEL = 10

#fov
FOV_ALGO = 0
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 6
FOV_RADIUS = 8
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

#miscellaneous variables
worldmap = None
current_map = None
old_maps = []
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


class Game(object):
	def __init__(self):
		global con, panel, ps, fov_noise, savefiles, items, tiles, monsters, rnd
		self.load_settings()
		#img = libtcod.image_load('title_screen2.png')
		if game.font == 'large':
			libtcod.console_set_custom_font('font-large.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
		else:
			libtcod.console_set_custom_font('font-small.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
		libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Immortal ' + VERSION, False)
		libtcod.sys_set_fps(600)
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

	# new game setup
	def new_game(self):
		global player, char, message, game_state, current_map
		message = Message()
		player = Player()
		char = map.Object(0, 0, player.icon, 'player', player.icon_color, blocks=True)
		game_state = create_character()
		if game_state == 'playing':
			current_map = map.Map('Starter Dungeon', 'SD', 1, 1)
			self.play_game()

	# main game loop
	def play_game(self):
		global player_action
		libtcod.console_clear(0)
		util.initialize_fov()
		while not libtcod.console_is_window_closed():
			if game.redraw_gui:
				util.render_gui(libtcod.red)
				util.render_message_panel()
				util.render_player_stats_panel()
				game.redraw_gui = False
			util.render_all()
			libtcod.console_flush()

			#player movement
			player_action = commands.handle_keys()
			if player_action == 'save':
				self.save_game()
				player_action = 'exit'
			if player_action == 'exit':
				break

			#let monsters take their turn
			if game.player_move:
				monsters.spawn()
				for object in reversed(current_map.objects):
					if object.item != None:
						if object.item.type == "corpse" and (game.player.turns - object.first_appearance > 500):
							object.delete()
					if object.entity != None:
						object.x, object.y = object.entity.take_turn(object.x, object.y)
				game.player_move = False

			#death screen summary
			if game_state == 'death':
				key = libtcod.Key()
				util.render_all()
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
			desc = []
			for i in range(0, len(savefiles)):
				file = shelve.open('saves/' + savefiles[i], 'r')
				file['current_map']
				file['maps']
				pl = file['player']
				desc.append(savefiles[i] + ', a level ' + str(pl.level) + ' ' + pl.gender + ' ' + pl.race + ' ' + pl.profession)
				file.close()
			choice = util.msg_box('save', 'Saved games', contents=desc, box_height=max(16, len(savefiles) + 4))
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
		util.msg_box('text', 'Help', contents=contents, box_width=40, box_height=24)

	# loading and changin game settings
	def settings(self):
		util.msg_box('settings', 'Settings', contents=game.font, box_width=40, box_height=8, center=True)
		self.load_settings()

	def load_settings(self):
		if os.path.exists('settings.ini'):
			contents = open('settings.ini', 'r')
			for line in contents:
				game.font = line.rstrip()
			if game.font != 'large':
				game.font = 'small'
			contents.close()

	# loading and showing the high scores screen
	def show_high_scores(self):
		if os.path.exists('data/highscores.dat'):
			self.load_high_scores()
			util.msg_box('highscore', 'High scores', contents=game.highscore, box_width=game.SCREEN_WIDTH, box_height=game.SCREEN_HEIGHT)
		else:
			util.msg_box('text', 'High scores', contents="The high scores file is empty.", box_width=41, box_height=5, center=True)

	def load_high_scores(self):
		if os.path.exists('data/highscores.dat'):
			contents = open('data/highscores.dat', 'rb')
			game.highscore = pickle.load(contents)
			contents.close()

	# testing the world generation
	def world_generation(self):
		game.worldmap = worldgen.World()
		key = libtcod.Key()
		mouse = libtcod.Mouse()
		curx, cury = 0, 0

		while not libtcod.console_is_window_closed():
			libtcod.sys_check_for_event(libtcod.EVENT_ANY, key, mouse)
			mx = curx + mouse.cx
			my = cury + mouse.cy
			if key.vk == libtcod.KEY_UP:
				if cury > 3:
					cury -= 4
			if key.vk == libtcod.KEY_DOWN:
				if cury <= game.WORLDMAP_HEIGHT - game.SCREEN_HEIGHT - 3:
					cury += 4
			if key.vk == libtcod.KEY_LEFT:
				if curx > 3:
					curx -= 4
			if key.vk == libtcod.KEY_RIGHT:
				if curx <= game.WORLDMAP_WIDTH - game.SCREEN_WIDTH - 3:
					curx += 4
			if key.vk == libtcod.KEY_ESCAPE:
				break

			for px in range(0, game.SCREEN_WIDTH):
				for py in range(0, game.SCREEN_HEIGHT):
					wx = px + curx
					wy = py + cury
					cellheight = libtcod.heightmap_get_value(game.worldmap.hm, wx, wy)
					hcolor = libtcod.darkest_blue
					if cellheight >= 0.060:
						hcolor = libtcod.blue
					if cellheight >= 0.110:
						hcolor = libtcod.light_blue
					if cellheight >= 0.118:
						hcolor = libtcod.light_yellow
					if cellheight >= 0.126:
						hcolor = libtcod.light_green
					if cellheight >= 0.250:
						hcolor = libtcod.green
					if cellheight >= 0.450:
						hcolor = libtcod.dark_green
					if cellheight >= 0.575:
						hcolor = libtcod.Color(53, 33, 16)
					if cellheight >= 0.700:
						hcolor = libtcod.grey
					if cellheight >= 0.900:
						hcolor = libtcod.silver

					if hcolor == libtcod.darkest_blue:
						libtcod.console_put_char_ex(0, px, py, '~', libtcod.Color(24, 24, 240), libtcod.Color(0, 0, 80))
					elif hcolor == libtcod.blue:
						libtcod.console_put_char_ex(0, px, py, '~', libtcod.Color(60, 60, 220), libtcod.Color(24, 24, 240))
					elif hcolor == libtcod.light_blue:
						libtcod.console_put_char_ex(0, px, py, '~', libtcod.Color(172, 172, 255), libtcod.Color(135, 135, 255))
					else:
						libtcod.console_put_char_ex(0, px, py, ' ', hcolor, hcolor)

			cellheight = libtcod.heightmap_get_value(game.worldmap.hm, mx, my)
			libtcod.console_set_default_foreground(0, libtcod.black)
			libtcod.console_print(0, 0, game.SCREEN_HEIGHT - 2, 'X: ' + str(mx) + ' Y: ' + str(my) + '   ')
			libtcod.console_print(0, 0, game.SCREEN_HEIGHT - 1, str(cellheight) + '   ')
			libtcod.console_flush()

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
			libtcod.console_print_ex(0, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 7, libtcod.BKGND_SET, libtcod.CENTER, 'Immortal ' + VERSION)
			libtcod.console_print_ex(0, SCREEN_WIDTH / 2, SCREEN_HEIGHT - 2, libtcod.BKGND_SET, libtcod.CENTER, 'By Potatoman')
			contents = ['Start a new game', 'Load a saved game', 'World Generation', 'Help', 'Settings', 'High Scores', 'Quit']
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
			if choice == 2:  # world generation
				self.world_generation()
			if choice == 3:  # help
				self.help()
			if choice == 4:  # settings
				self.settings()
			if choice == 5:  # high scores
				self.show_high_scores()
			if choice == 6:  # quit
				break
