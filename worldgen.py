import libtcodpy as libtcod
import math
import game


class World(object):
	def __init__(self):
		self.rnd = libtcod.random_new()
		self.noise = 0
		self.hm_list = [0] * (game.WORLDMAP_WIDTH * game.WORLDMAP_HEIGHT)
		self.sandheight = game.terrain['Coast']['elevation']
		self.map_image_big = None
		self.map_image_small = None
		self.player_positionx = 0
		self.player_positiony = 0
		self.originx = 0
		self.originy = 0
		self.max_distance = 0
		self.dungeons = []
		self.generate()

	# add some land by creating hills
	def add_landmass(self):
		print 'Creating landmass....'
		t0 = libtcod.sys_elapsed_seconds()
		for i in range(int(game.WORLDMAP_WIDTH * 0.55)):
			radius = self.randomize('float', 50 * (1.0 - 0.7), 50 * (1.0 + 0.7), 3)
			x = self.randomize('int', 0, game.WORLDMAP_WIDTH, 3)
			y = self.randomize('int', 0, game.WORLDMAP_HEIGHT, 3)
			libtcod.heightmap_add_hill(game.heightmap, x, y, radius, 0.3)
		libtcod.heightmap_normalize(game.heightmap)
		libtcod.heightmap_add_fbm(game.heightmap, self.noise, 6.5, 6.5, 0, 0, 8.0, 1.0, 4.0)
		libtcod.heightmap_normalize(game.heightmap)
		t1 = libtcod.sys_elapsed_seconds()
		print '    done! (%.3f seconds)' % (t1 - t0)

	# add some rivers, lets limit this to the rain erosion function for now
	def add_rivers(self):
		print 'Adding rivers....'
		t0 = libtcod.sys_elapsed_seconds()
		libtcod.heightmap_rain_erosion(game.heightmap, int((game.WORLDMAP_WIDTH * game.WORLDMAP_HEIGHT) * 1.00), 0.06, 0.01, self.rnd)
		t1 = libtcod.sys_elapsed_seconds()
		print '    done! (%.3f seconds)' % (t1 - t0)

	# checks to see if everything is in order
	def analyse_world(self):
		print 'Analysing worldmap....'
		t0 = libtcod.sys_elapsed_seconds()
		mountain_peak = 0
		mountains = 0
		high_hills = 0
		low_hills = 0
		forest = 0
		plains = 0
		coast = 0
		shore = 0
		sea = 0
		ocean = 0
		accepted = True

		for x in range(game.WORLDMAP_WIDTH):
			for y in range(game.WORLDMAP_HEIGHT):
				cellheight = libtcod.heightmap_get_value(game.heightmap, x, y)
				if cellheight >= game.terrain['Mountain Peak']['elevation']:
					mountain_peak += 1
				elif cellheight >= game.terrain['Mountains']['elevation']:
					mountains += 1
				elif cellheight >= game.terrain['High Hills']['elevation']:
					high_hills += 1
				elif cellheight >= game.terrain['Low Hills']['elevation']:
					low_hills += 1
				elif cellheight >= game.terrain['Forest']['elevation']:
					forest += 1
				elif cellheight >= game.terrain['Plains']['elevation']:
					plains += 1
				elif cellheight >= game.terrain['Coast']['elevation']:
					coast += 1
				elif cellheight >= game.terrain['Shore']['elevation']:
					shore += 1
				elif cellheight >= game.terrain['Sea']['elevation']:
					sea += 1
				else:
					ocean += 1

		if mountain_peak < 15 or mountains < 150 or high_hills < 600 or low_hills < 1500 or coast < 2500:
			accepted = False
		if forest > 22000 or plains > 10000 or shore > 8000 or sea > 28000 or ocean > 30000:
			accepted = False
		t1 = libtcod.sys_elapsed_seconds()
		if accepted:
			print '    accepted! (%.3f seconds)' % (t1 - t0)
		else:
			self.player_positionx = 0
			self.max_distance = 0
			self.dungeons = []
			print '    rejected! (%.3f seconds)' % (t1 - t0)
		return accepted

	# create and save worldmap image in different sizes
	def create_map_images(self, mode=0):
		if mode == 0:
			print 'Creating images....'
			t0 = libtcod.sys_elapsed_seconds()
		con = libtcod.console_new(game.WORLDMAP_WIDTH, game.WORLDMAP_HEIGHT)
		self.map_image_small = libtcod.image_new(game.WORLDMAP_WIDTH, game.WORLDMAP_HEIGHT)
		self.create_map_legend(con, mode)
		libtcod.image_scale(self.map_image_small, (game.SCREEN_WIDTH - 2) * 2, (game.SCREEN_HEIGHT - 2) * 2)

		if mode == 0:
			while self.player_positionx == 0:
				start = self.randomize('int', 0, (game.WORLDMAP_WIDTH * game.WORLDMAP_HEIGHT) - 1, 3)
				if int(self.hm_list[start] * 1000) in range(int(game.terrain['Forest']['elevation'] * 1000), int(game.terrain['Forest']['maxelev'] * 1000)):
					self.player_positionx = start % game.WORLDMAP_WIDTH
					self.player_positiony = start / game.WORLDMAP_WIDTH
					self.originx = self.player_positionx
					self.originy = self.player_positiony

					path_dijk = self.set_dijkstra_map()
					for y in range(game.WORLDMAP_HEIGHT):
						for x in range(game.WORLDMAP_WIDTH):
							dist = libtcod.dijkstra_get_distance(path_dijk, x, y)
							if dist > self.max_distance:
								self.max_distance = int(round(dist))
					#libtcod.image_put_pixel(self.map_image_small, self.player_positionx, self.player_positiony, libtcod.white)

		if mode == 2:
			self.map_image_big = libtcod.image_from_console(con)
			libtcod.image_save(self.map_image_big, 'maps/worldmap-' + game.player.name + '.png')
			self.map_image_big = None
		libtcod.console_delete(con)
		if mode == 0:
			t1 = libtcod.sys_elapsed_seconds()
			print '    done! (%.3f seconds)' % (t1 - t0)

	# colors for the map legend
	def create_map_legend(self, con, mode=0):
		for x in range(game.WORLDMAP_WIDTH):
			for y in range(game.WORLDMAP_HEIGHT):
				if mode == 0:
					cellheight = libtcod.heightmap_get_value(game.heightmap, x, y)
				else:
					cellheight = self.hm_list[(y * game.WORLDMAP_WIDTH) + x]
				if cellheight >= game.terrain['Mountain Peak']['elevation']:
					# mountain peak
					bcolor = libtcod.color_lerp(libtcod.silver, libtcod.grey, (1.000 - cellheight) / 0.050)
				elif cellheight >= game.terrain['Mountains']['elevation']:
					# mountains
					bcolor = libtcod.color_lerp(libtcod.grey, libtcod.Color(40, 24, 12), (game.terrain['Mountain Peak']['elevation'] - cellheight) / 0.125)
				elif cellheight >= game.terrain['High Hills']['elevation']:
					# hills
					bcolor = libtcod.color_lerp(libtcod.Color(40, 24, 12), libtcod.Color(53, 33, 16), (game.terrain['Mountains']['elevation'] - cellheight) / 0.125)
				elif cellheight >= game.terrain['Low Hills']['elevation']:
					# forest
					bcolor = libtcod.color_lerp(libtcod.Color(53, 33, 16), libtcod.Color(40, 67, 25), (game.terrain['High Hills']['elevation'] - cellheight) / 0.125)
				elif cellheight >= game.terrain['Forest']['elevation']:
					# forest
					bcolor = libtcod.color_lerp(libtcod.Color(40, 67, 25), libtcod.Color(80, 134, 50), (game.terrain['Low Hills']['elevation'] - cellheight) / 0.345)
				elif cellheight >= game.terrain['Plains']['elevation']:
					# plains
					bcolor = libtcod.color_lerp(libtcod.Color(80, 134, 50), libtcod.Color(112, 150, 80), (game.terrain['Forest']['elevation'] - cellheight) / 0.090)
				elif cellheight >= game.terrain['Coast']['elevation']:
					# coast
					bcolor = libtcod.color_lerp(libtcod.Color(112, 150, 80), libtcod.Color(176, 176, 153), (game.terrain['Plains']['elevation'] - cellheight) / 0.020)
				elif cellheight >= game.terrain['Shore']['elevation']:
					# shallow water
					bcolor = libtcod.color_lerp(libtcod.Color(176, 176, 153), libtcod.Color(47, 67, 103), (game.terrain['Coast']['elevation'] - cellheight) / 0.010)
				elif cellheight >= game.terrain['Sea']['elevation']:
					# deep water
					bcolor = libtcod.color_lerp(libtcod.Color(47, 67, 103), libtcod.Color(8, 32, 72), (game.terrain['Shore']['elevation'] - cellheight) / 0.040)
				else:
					# ocean
					bcolor = libtcod.Color(8, 32, 72)
				libtcod.console_put_char_ex(con, x, y, ' ', bcolor, bcolor)
				if mode != 3:
					libtcod.image_put_pixel(self.map_image_small, x, y, bcolor)
				if mode == 0:
					self.hm_list[(y * game.WORLDMAP_WIDTH) + x] = float("{0:.4f}".format(cellheight))

	# place all dungeons after terrain generation
	def place_dungeons(self):
		print 'Placing dungeons....'
		t0 = libtcod.sys_elapsed_seconds()
		path_dijk = self.set_dijkstra_map()
		for i in range(game.MAX_THREAT_LEVEL):
			done = False
			attempt = 0
			while not done and attempt <= 1000:
				x = libtcod.random_get_int(self.rnd, 0, game.WORLDMAP_WIDTH - 1)
				y = libtcod.random_get_int(self.rnd, 0, game.WORLDMAP_HEIGHT - 1)
				cellheight = int(libtcod.heightmap_get_value(game.heightmap, x, y) * 1000)
				threat = self.set_threat_level(x, y, path_dijk)
				dice = libtcod.random_get_int(self.rnd, 1, 100)
				if dice <= 65:
					dtype = 'Dungeon'
				elif dice <= 95:
					dtype = 'Cave'
				else:
					dtype = 'Maze'
				if cellheight in range(int(game.terrain['Plains']['elevation'] * 1000), int(game.terrain['High Hills']['maxelev'] * 1000)) and threat == i + 1:
					self.dungeons.append((len(self.dungeons) + 1, 'Dungeon', 'Dng', x, y, threat + 1, dtype))
					done = True
				attempt += 1

		starter_dungeon = libtcod.random_get_int(self.rnd, 1, 4)
		if starter_dungeon == 1:
			self.dungeons.append((len(self.dungeons) + 1, 'Starter Dungeon', 'SD', self.player_positionx, self.player_positiony - 1, 1, 'Dungeon'))
		elif starter_dungeon == 2:
			self.dungeons.append((len(self.dungeons) + 1, 'Starter Dungeon', 'SD', self.player_positionx + 1, self.player_positiony, 1, 'Dungeon'))
		elif starter_dungeon == 3:
			self.dungeons.append((len(self.dungeons) + 1, 'Starter Dungeon', 'SD', self.player_positionx, self.player_positiony + 1, 1, 'Dungeon'))
		else:
			self.dungeons.append((len(self.dungeons) + 1, 'Starter Dungeon', 'SD', self.player_positionx - 1, self.player_positiony, 1, 'Dungeon'))
		t1 = libtcod.sys_elapsed_seconds()
		print '    done! (%.3f seconds)' % (t1 - t0)

	# randomize the random generator
	def randomize(self, type, min, max, times):
		result = 0
		if type == 'float':
			for i in range(times):
				result += libtcod.random_get_float(self.rnd, min, max)
		if type == 'int':
			for i in range(times):
				result += libtcod.random_get_int(self.rnd, min, max)
		return result / times

	# set dijkstra map base on point of origin
	def set_dijkstra_map(self):
		dijk_map = libtcod.map_new(game.WORLDMAP_WIDTH, game.WORLDMAP_HEIGHT)
		for y in range(game.WORLDMAP_HEIGHT):
			for x in range(game.WORLDMAP_WIDTH):
				libtcod.map_set_properties(dijk_map, x, y, True, True)
		path_dijk = libtcod.dijkstra_new(dijk_map)
		libtcod.dijkstra_compute(path_dijk, self.originx, self.originy)
		return path_dijk

	# reduce landmass to the appropriate level
	def set_landmass(self, landmass, waterlevel):
		print 'Reducing landmass....'
		t0 = libtcod.sys_elapsed_seconds()
		heightcount = [0] * 256
		for x in range(game.WORLDMAP_WIDTH):
			for y in range(game.WORLDMAP_HEIGHT):
				h = int(libtcod.heightmap_get_value(game.heightmap, x, y) * 255)
				heightcount[h] += 1

		i, totalcount = 0, 0
		while totalcount < game.WORLDMAP_WIDTH * game.WORLDMAP_HEIGHT * (1.0 - landmass):
			totalcount += heightcount[i]
			i += 1
		newwaterlevel = i / 255.0
		landcoef = (1.0 - waterlevel) / (1.0 - newwaterlevel)
		watercoef = waterlevel / newwaterlevel

		for x in range(game.WORLDMAP_WIDTH):
			for y in range(game.WORLDMAP_HEIGHT):
				h = libtcod.heightmap_get_value(game.heightmap, x, y)
				if h > newwaterlevel:
					h = waterlevel + (h - newwaterlevel) * landcoef
				else:
					h = h * watercoef
				libtcod.heightmap_set_value(game.heightmap, x, y, h)
		t1 = libtcod.sys_elapsed_seconds()
		print '    done! (%.3f seconds)' % (t1 - t0)

	# set threat level of a overworld map based on the player point of origin
	# the farther it is, the more dangerous it is
	def set_threat_level(self, posx, posy, path=None):
		if path is None:
			path = self.set_dijkstra_map()
		dist = libtcod.dijkstra_get_distance(path, posx, posy)
		tlevel = int(math.ceil(dist / (self.max_distance / (game.MAX_THREAT_LEVEL + 2))))
		if tlevel > game.MAX_THREAT_LEVEL:
			tlevel = game.MAX_THREAT_LEVEL
		return tlevel

	# smooth edges so that land doesnt touch the map borders
	def smooth_edges(self):
		print 'Smoothing edges....'
		t0 = libtcod.sys_elapsed_seconds()
		hmcopy = libtcod.heightmap_new(game.WORLDMAP_WIDTH, game.WORLDMAP_HEIGHT)
		mask = libtcod.heightmap_new(game.WORLDMAP_WIDTH, game.WORLDMAP_HEIGHT)
		for x in range(game.WORLDMAP_WIDTH):
			for y in range(game.WORLDMAP_HEIGHT):
				ix = x * 0.04
				if x > game.WORLDMAP_WIDTH / 2:
					ix = (game.WORLDMAP_WIDTH - x - 1) * 0.04
				iy = y * 0.04
				if y > game.WORLDMAP_HEIGHT / 2:
					iy = (game.WORLDMAP_HEIGHT - y - 1) * 0.04
				if ix > 1.0:
					ix = 1.0
				if iy > 1.0:
					iy = 1.0
				h = min(ix, iy)
				libtcod.heightmap_set_value(mask, x, y, h)
		libtcod.heightmap_normalize(mask)
		libtcod.heightmap_copy(game.heightmap, hmcopy)
		libtcod.heightmap_multiply_hm(hmcopy, mask, game.heightmap)
		libtcod.heightmap_normalize(game.heightmap)
		t1 = libtcod.sys_elapsed_seconds()
		print '    done! (%.3f seconds)' % (t1 - t0)

	# main function for generating the worldmap
	# stuff to do: place towns
	def generate(self):
		print 'Starting world map generation....'
		t0 = libtcod.sys_elapsed_seconds()
		accepted = False
		world = 1
		while not accepted:
			print 'World #' + str(world) + '....'
			self.noise = libtcod.noise_new(2, self.rnd)
			libtcod.noise_set_type(self.noise, libtcod.NOISE_PERLIN)
			game.heightmap = libtcod.heightmap_new(game.WORLDMAP_WIDTH, game.WORLDMAP_HEIGHT)
			#game.precipitation = libtcod.heightmap_new(game.WORLDMAP_WIDTH, game.WORLDMAP_HEIGHT)
			#game.temperature = libtcod.heightmap_new(game.WORLDMAP_WIDTH, game.WORLDMAP_HEIGHT)
			#game.biome = libtcod.heightmap_new(game.WORLDMAP_WIDTH, game.WORLDMAP_HEIGHT)

			self.add_landmass()
			self.smooth_edges()
			self.set_landmass(self.randomize('float', 0.30, 0.45, 3), self.sandheight)
			self.add_rivers()
			self.create_map_images()
			self.place_dungeons()
			accepted = self.analyse_world()
			world += 1
			print '-------------'
		t1 = libtcod.sys_elapsed_seconds()
		print 'World map generation finished.... (%.3f seconds)' % (t1 - t0)
