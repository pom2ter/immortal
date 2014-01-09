import libtcodpy as libtcod
import cPickle as pickle
import glob
import os
import shutil
import game
import util


# autosave game
def autosave(border=True):
#	t0 = libtcod.sys_elapsed_seconds()
	if not os.path.exists('saves/' + game.player.name.lower()):
		os.makedirs('saves/' + game.player.name.lower())
	f = open('saves/' + game.player.name.lower() + '/player.tmp', 'wb')
	pickle.dump(game.player, f, game.PICKLE_PROTOCOL)
	f.close()
	f = open('saves/' + game.player.name.lower() + '/worldmap.tmp', 'wb')
	pickle.dump(game.worldmap, f, game.PICKLE_PROTOCOL)
	f.close()
	f = open('saves/' + game.player.name.lower() + '/messages.tmp', 'wb')
	pickle.dump(game.message, f, game.PICKLE_PROTOCOL)
	f.close()
	f = open('saves/' + game.player.name.lower() + '/stuff.tmp', 'wb')
	pickle.dump(game.rnd, f, game.PICKLE_PROTOCOL)
	pickle.dump(game.turns, f, game.PICKLE_PROTOCOL)
	pickle.dump(game.time, f, game.PICKLE_PROTOCOL)
	pickle.dump(game.fov_torch, f, game.PICKLE_PROTOCOL)
	pickle.dump(game.game_state, f, game.PICKLE_PROTOCOL)
	pickle.dump(game.times_saved, f, game.PICKLE_PROTOCOL)
	f.close()

	f = open('saves/' + game.player.name.lower() + '/map' + str(game.current_map.location_id) + '-' + str(game.current_map.location_level) + '.tmp', 'wb')
	pickle.dump(game.current_map, f, game.PICKLE_PROTOCOL)
	f.close()
#	with gzip.GzipFile('saves/' + game.player.name.lower() + '/current_map.tmp', 'wb', 2) as f:
#		pickle.dump(game.current_map, f, game.PICKLE_PROTOCOL)
	if border:
		for i in range(len(game.border_maps)):
			f = open('saves/' + game.player.name.lower() + '/map' + str(game.border_maps[i].location_id) + '-' + str(game.border_maps[i].location_level) + '.tmp', 'wb')
			pickle.dump(game.border_maps[i], f, game.PICKLE_PROTOCOL)
			f.close()

#	t1 = libtcod.sys_elapsed_seconds()
#	print 'maps save done! (%.3f seconds)' % (t1 - t0)


# autosave current map
def autosave_current_map():
	f = open('saves/' + game.player.name.lower() + '/current_map.tmp', 'wb')
	pickle.dump(game.current_map, f, game.PICKLE_PROTOCOL)
	f.close()


# delete save game and temp files
def delete_game():
	if game.player.name.lower() + '.sav' in game.savefiles:
		os.remove('saves/' + game.player.name.lower() + '.sav')
	if os.path.exists('saves/' + game.player.name.lower()):
		shutil.rmtree('saves/' + game.player.name.lower())


# fetch autosave if it exists to override save game data
def fetch_autosave():
	if os.path.exists('saves/' + game.player.name.lower() + '/player.tmp'):
		f = open('saves/' + game.player.name.lower() + '/player.tmp', 'rb')
		game.player = pickle.load(f)
		f.close()
	if os.path.exists('saves/' + game.player.name.lower() + '/worldmap.tmp'):
		f = open('saves/' + game.player.name.lower() + '/worldmap.tmp', 'rb')
		game.worldmap = pickle.load(f)
		f.close()
	if os.path.exists('saves/' + game.player.name.lower() + '/messages.tmp'):
		f = open('saves/' + game.player.name.lower() + '/messages.tmp', 'rb')
		game.message = pickle.load(f)
		f.close()
	if os.path.exists('saves/' + game.player.name.lower() + '/stuff.tmp'):
		f = open('saves/' + game.player.name.lower() + '/stuff.tmp', 'rb')
		game.rnd = pickle.load(f)
		game.turns = pickle.load(f)
		game.time = pickle.load(f)
		game.fov_torch = pickle.load(f)
		game.game_state = pickle.load(f)
		game.times_saved = pickle.load(f)
		f.close()

	oldmaps = glob.glob('saves/' + game.player.name.lower() + '/map*.tmp')
	if os.path.exists('saves/' + game.player.name.lower() + '/current_map.tmp'):
		f = open('saves/' + game.player.name.lower() + '/current_map.tmp', 'rb')
		game.current_map = pickle.load(f)
		f.close()
	for i in range(len(oldmaps)):
		f = open(oldmaps[i], 'rb')
		temp_map = pickle.load(f)
		util.store_map(temp_map)
		f.close()


# load the game using the pickle module
def load_game():
	if not game.savefiles:
		contents = ['There are no saved games.']
		game.messages.box('Saved games', None, 'center_screenx', 'center_screeny', len(max(contents, key=len)) + 16, len(contents) + 4, contents, input=False, align=libtcod.CENTER)
	else:
		desc = []
		for i in range(len(game.savefiles)):
			f = open('saves/' + game.savefiles[i], 'rb')
			pl = pickle.load(f)
			desc.append(pl.name + ', a level ' + str(pl.level) + ' ' + pl.gender + ' ' + pl.race + ' ' + pl.profession)
			f.close()
		choice = game.messages.box('Saved games', None, (game.SCREEN_WIDTH - (max(60, len(max(desc, key=len)) + 20))) / 2, ((game.SCREEN_HEIGHT + 1) - max(16, len(desc) + 4)) / 2, max(60, len(max(desc, key=len)) + 20), max(16, len(desc) + 4), desc, step=2, mouse_exit=True)
		if choice != -1:
			contents = ['Loading.....']
			game.messages.box(None, None, 'center_screenx', 'center_screeny', len(max(contents, key=len)) + 16, len(contents) + 4, contents, input=False, align=libtcod.CENTER, nokeypress=True)
			f = open('saves/' + game.savefiles[choice], 'rb')
			game.player = pickle.load(f)
			game.worldmap = pickle.load(f)
			game.current_map = pickle.load(f)
			game.old_maps = pickle.load(f)
			game.message = pickle.load(f)
			game.rnd = pickle.load(f)
			game.turns = pickle.load(f)
			game.time = pickle.load(f)
			game.fov_torch = pickle.load(f)
			game.game_state = pickle.load(f)
			game.times_saved = pickle.load(f)
			f.close()
			fetch_autosave()
			game.rnd = libtcod.random_new_from_seed(game.rnd)
			game.char = game.current_map.objects[0]
			game.mouse.lbutton_pressed = False
			game.worldmap.create_map_images(1)
			game.message.empty()
			game.message.trim_history()
			game.message.new('Welcome back, ' + game.player.name + '!', game.turns, libtcod.Color(96, 212, 238))
			if game.current_map.location_id == 0:
				util.fetch_border_maps()
				util.combine_maps()
			game.current_map.check_player_position()
			#print game.worldmap.dungeons
			return True
	return False


# load high scores
def load_high_scores():
	if os.path.exists('highscores.dat'):
		contents = open('highscores.dat', 'rb')
		game.highscore = pickle.load(contents)
		contents.close()


# load manual
def load_manual():
	contents = open('data/help.txt', 'r').read()
	contents = contents.split('\n')
	return contents


# load game settings
# stuff to do: add more options
def load_settings():
	if os.path.exists('settings.ini'):
		contents = open('settings.ini', 'r')
		while True:
			line = contents.readline().rstrip()
			if line == '[Font]':
				game.setting_font = contents.readline().rstrip()
			if line == '[History]':
				game.setting_history = int(contents.readline().rstrip())
			if line == '[Fullscreen]':
				game.setting_fullscreen = contents.readline().rstrip()
			if not line:
				break
		contents.close()
		if not any(game.setting_font == i for i in ['small', 'medium', 'large']):
			game.setting_font = 'small'
		if not game.setting_history in range(50, 1000):
			game.setting_history = 50
		if not any(game.setting_fullscreen == i for i in ['on', 'off']):
			game.setting_fullscreen = 'off'


# save the game using the pickle module
def save_game(chargen=False):
	if not chargen:
		contents = ['Saving.....']
		game.messages.box(None, None, 'center_screenx', 'center_screeny', len(max(contents, key=len)) + 28, len(contents) + 4, contents, input=False, align=libtcod.CENTER, nokeypress=True)
		delete_game()
	if game.current_map.location_id == 0:
		if not chargen:
			util.decombine_maps()
		util.store_map(game.current_map)
		for i in range(len(game.border_maps)):
			util.store_map(game.border_maps[i])

	f = open('saves/' + game.player.name.lower() + '.sav', 'wb')
	pickle.dump(game.player, f, game.PICKLE_PROTOCOL)
	pickle.dump(game.worldmap, f, game.PICKLE_PROTOCOL)
	pickle.dump(game.current_map, f, game.PICKLE_PROTOCOL)
	pickle.dump(game.old_maps, f, game.PICKLE_PROTOCOL)
	pickle.dump(game.message, f, game.PICKLE_PROTOCOL)
	pickle.dump(game.rnd, f, game.PICKLE_PROTOCOL)
	pickle.dump(game.turns, f, game.PICKLE_PROTOCOL)
	pickle.dump(game.time, f, game.PICKLE_PROTOCOL)
	pickle.dump(game.fov_torch, f, game.PICKLE_PROTOCOL)
	pickle.dump(game.game_state, f, game.PICKLE_PROTOCOL)
	pickle.dump(game.times_saved + 1, f, game.PICKLE_PROTOCOL)
	f.close()


# save changes to the highscores
def save_high_scores():
	f = open('highscores.dat', 'wb')
	pickle.dump(game.highscore, f, game.PICKLE_PROTOCOL)
	f.close()


# save changes to the game settings
def save_settings(font, history, fs):
	f = open('settings.ini', 'wb')
	f.write('[Font]\n')
	f.write(font + '\n')
	f.write('[History]\n')
	f.write(history + '\n')
	f.write('[Fullscreen]\n')
	f.write(fs + '\n')
	f.close()
