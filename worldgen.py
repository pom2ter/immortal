import libtcodpy as libtcod
import math
import os
import game


class World(object):
	def __init__(self):
		self.rnd = libtcod.random_new()
		self.noise = 0
		self.hm_list = [0] * (game.WORLDMAP_WIDTH * game.WORLDMAP_HEIGHT)
		self.sandheight = 0.12
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
		for i in range(game.WORLDMAP_WIDTH / 2):
			radius = libtcod.random_get_float(self.rnd, 50 * (1.0 - 0.7), 50 * (1.0 + 0.7))
			x = libtcod.random_get_int(self.rnd, 0, game.WORLDMAP_WIDTH)
			y = libtcod.random_get_int(self.rnd, 0, game.WORLDMAP_HEIGHT)
			libtcod.heightmap_add_hill(game.hm, x, y, radius, 0.3)
		libtcod.heightmap_normalize(game.hm)
		libtcod.heightmap_add_fbm(game.hm, self.noise, 6.5, 6.5, 0, 0, 8.0, 1.0, 4.0)
		libtcod.heightmap_normalize(game.hm)

	# create and save worldmap image in different sizes
	def create_map_images(self, mode=0):
		con = libtcod.console_new(game.WORLDMAP_WIDTH, game.WORLDMAP_HEIGHT)
		self.map_image_small = libtcod.image_new(game.WORLDMAP_WIDTH, game.WORLDMAP_HEIGHT)
		for x in range(game.WORLDMAP_WIDTH):
			for y in range(game.WORLDMAP_HEIGHT):
				if mode == 0:
					cellheight = libtcod.heightmap_get_value(game.hm, x, y)
				else:
					cellheight = self.hm_list[(y * game.WORLDMAP_WIDTH) + x]
				if cellheight >= 0.950:
					# mountain peak
					bcolor = libtcod.color_lerp(libtcod.white, libtcod.silver, (1.000 - cellheight) / 0.050)
				elif cellheight >= 0.850:
					# mountains
					bcolor = libtcod.color_lerp(libtcod.silver, libtcod.grey, (0.950 - cellheight) / 0.100)
				elif cellheight >= 0.700:
					# hills
					bcolor = libtcod.color_lerp(libtcod.grey, libtcod.Color(53, 33, 16), (0.850 - cellheight) / 0.150)
				elif cellheight >= 0.250:
					# forest
					bcolor = libtcod.color_lerp(libtcod.Color(53, 33, 16), libtcod.dark_green, (0.700 - cellheight) / 0.450)
				elif cellheight >= 0.175:
					# plains
					bcolor = libtcod.color_lerp(libtcod.dark_green, libtcod.green, (0.250 - cellheight) / 0.075)
				elif cellheight >= 0.120:
					# coast
					bcolor = libtcod.color_lerp(libtcod.light_green, libtcod.Color(252, 208, 160), (0.175 - cellheight) / 0.055)
				elif cellheight >= 0.110:
					# shallow water
					bcolor = libtcod.color_lerp(libtcod.Color(135, 135, 255), libtcod.Color(24, 24, 240), (0.120 - cellheight) / 0.010)
				elif cellheight >= 0.060:
					# deep water
					bcolor = libtcod.color_lerp(libtcod.Color(24, 24, 240), libtcod.Color(0, 0, 80), (0.110 - cellheight) / 0.050)
				else:
					# ocean
					bcolor = libtcod.Color(0, 0, 80)
				libtcod.console_put_char_ex(con, x, y, ' ', bcolor, bcolor)
				libtcod.image_put_pixel(self.map_image_small, x, y, bcolor)
				if mode == 0:
					self.hm_list[(y * game.WORLDMAP_WIDTH) + x] = float("{0:.4f}".format(cellheight))

		libtcod.image_scale(self.map_image_small, (game.SCREEN_WIDTH - 2) * 2, (game.SCREEN_HEIGHT - 2) * 2)
		if mode == 0:
			while self.player_positionx == 0:
				start = libtcod.random_get_int(self.rnd, 0, (game.WORLDMAP_WIDTH * game.WORLDMAP_HEIGHT) - 1)
				if int(self.hm_list[start] * 1000) in range(250, 699):
					self.player_positionx = start % game.WORLDMAP_WIDTH
					self.player_positiony = start / game.WORLDMAP_WIDTH
					self.originx = self.player_positionx
					self.originy = self.player_positiony

					dijk_map = libtcod.map_new(game.WORLDMAP_WIDTH, game.WORLDMAP_HEIGHT)
					for y in range(game.WORLDMAP_HEIGHT):
						for x in range(game.WORLDMAP_WIDTH):
							libtcod.map_set_properties(dijk_map, x, y, True, True)
					path_dijk = libtcod.dijkstra_new(dijk_map)
					libtcod.dijkstra_compute(path_dijk, self.originx, self.originy)
					for y in range(game.WORLDMAP_HEIGHT):
						for x in range(game.WORLDMAP_WIDTH):
							dist = libtcod.dijkstra_get_distance(path_dijk, x, y)
							if dist > self.max_distance:
								self.max_distance = dist
					for i in range(len(self.dungeons)):
						(id, name, abbr, x, y, tlevel) = self.dungeons[i]
						self.dungeons[i] = (id, name, abbr, x, y, self.set_threat_level(self.dungeons[i][3], self.dungeons[i][4]) + 1)

					starter_dungeon = libtcod.random_get_int(self.rnd, 0, 4)
					if starter_dungeon == 1:
						self.dungeons.append((len(self.dungeons) + 1, 'Starter Dungeon', 'SD', self.player_positionx, self.player_positiony - 1, 1))
					elif starter_dungeon == 2:
						self.dungeons.append((len(self.dungeons) + 1, 'Starter Dungeon', 'SD', self.player_positionx + 1, self.player_positiony, 1))
					elif starter_dungeon == 3:
						self.dungeons.append((len(self.dungeons) + 1, 'Starter Dungeon', 'SD', self.player_positionx, self.player_positiony + 1, 1))
					else:
						self.dungeons.append((len(self.dungeons) + 1, 'Starter Dungeon', 'SD', self.player_positionx - 1, self.player_positiony, 1))
					#libtcod.image_put_pixel(self.map_image_small, self.player_positionx, self.player_positiony, libtcod.white)

		if mode == 2:
			self.map_image_big = libtcod.image_from_console(con)
			if not os.path.exists('maps'):
				os.makedirs('maps')
			libtcod.image_save(self.map_image_big, 'maps/worldmap-' + game.player.name + '.png')
			#libtcod.image_save(self.map_image_small, 'maps/' + time.strftime('%Y%m%d-%H%M%S') + '.png')
			self.map_image_big = None

	# place all dungeons after terrain generation
	def place_dungeons(self):
		number_of_dungeons = libtcod.random_get_int(self.rnd, 12, 18)
		while len(self.dungeons) != number_of_dungeons:
			x = libtcod.random_get_int(self.rnd, 0, game.WORLDMAP_WIDTH - 1)
			y = libtcod.random_get_int(self.rnd, 0, game.WORLDMAP_HEIGHT - 1)
			cellheight = int(libtcod.heightmap_get_value(game.hm, x, y) * 1000)
			if cellheight in range(250, 699):
				self.dungeons.append((len(self.dungeons) + 1, 'Dungeon', 'Dng', x, y, libtcod.random_get_int(self.rnd, 1, 20)))

	# reduce landmass to the appropriate level
	def set_land_mass(self, landmass, waterlevel):
		heightcount = [0] * 256
		for x in range(game.WORLDMAP_WIDTH):
			for y in range(game.WORLDMAP_HEIGHT):
				h = int(libtcod.heightmap_get_value(game.hm, x, y) * 255)
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
				h = libtcod.heightmap_get_value(game.hm, x, y)
				if h > newwaterlevel:
					h = waterlevel + (h - newwaterlevel) * landcoef
				else:
					h = h * watercoef
				libtcod.heightmap_set_value(game.hm, x, y, h)

	# set threat level of a overworld map based on the player point of origin
	# the farther it is, the more dangerous it is
	def set_threat_level(self, posx, posy):
		dijk_map = libtcod.map_new(game.WORLDMAP_WIDTH, game.WORLDMAP_HEIGHT)
		for y in range(game.WORLDMAP_HEIGHT):
			for x in range(game.WORLDMAP_WIDTH):
				libtcod.map_set_properties(dijk_map, x, y, True, True)
		path_dijk = libtcod.dijkstra_new(dijk_map)
		libtcod.dijkstra_compute(path_dijk, self.originx, self.originy)
		dist = libtcod.dijkstra_get_distance(path_dijk, posx, posy)
		tlevel = int(math.ceil(dist / (self.max_distance / game.MAX_THREAT_LEVEL)))
		if tlevel > game.MAX_THREAT_LEVEL:
			tlevel = game.MAX_THREAT_LEVEL
		return tlevel

	# smooth edges so that land doesnt touch the map borders
	def smooth_edges(self):
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
				libtcod.heightmap_set_value(game.mask, x, y, h)
		libtcod.heightmap_normalize(game.mask)
		libtcod.heightmap_copy(game.hm, game.hmcopy)
		libtcod.heightmap_multiply_hm(game.hmcopy, game.mask, game.hm)
		libtcod.heightmap_normalize(game.hm)

	# main function for generating the worldmap
	# stuff to do: add rivers, place towns
	def generate(self):
		self.noise = libtcod.noise_new(2, self.rnd)
		libtcod.noise_set_type(self.noise, libtcod.NOISE_PERLIN)
		game.hm = libtcod.heightmap_new(game.WORLDMAP_WIDTH, game.WORLDMAP_HEIGHT)
		game.hmcopy = libtcod.heightmap_new(game.WORLDMAP_WIDTH, game.WORLDMAP_HEIGHT)
		#game.precipitation = libtcod.heightmap_new(game.WORLDMAP_WIDTH, game.WORLDMAP_HEIGHT)
		#game.temperature = libtcod.heightmap_new(game.WORLDMAP_WIDTH, game.WORLDMAP_HEIGHT)
		game.mask = libtcod.heightmap_new(game.WORLDMAP_WIDTH, game.WORLDMAP_HEIGHT)

		self.add_landmass()
		self.smooth_edges()
		self.set_land_mass(libtcod.random_get_float(self.rnd, 0.35, 0.45), self.sandheight)
		#libtcod.heightmap_rain_erosion(game.hm, (game.WORLDMAP_WIDTH * game.WORLDMAP_HEIGHT) / 7, 0.70, 0.01, self.rnd)
		self.place_dungeons()
		self.create_map_images()
