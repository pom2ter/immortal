import libtcodpy as libtcod
import game
import os
import time


class World(object):
	def __init__(self):
		self.rnd = libtcod.random_new()
		self.noise = 0
		self.hm = 0
		self.hmcopy = 0
		self.precipitation = 0
		self.temperature = 0
		self.mask = 0
		self.biomemap = [0] * (game.WORLDMAP_WIDTH * game.WORLDMAP_HEIGHT)
		self.sandheight = 0.12
		self.generate2()

	def generate_rivers(self):
		riverId = 0
		sx, sy = 0, 0
		dx, dy = 0, 0
		# get a random point near the coast
		sx = libtcod.random_get_int(self.rnd, 0, game.WORLDMAP_WIDTH - 1)
		sy = libtcod.random_get_int(self.rnd, game.WORLDMAP_HEIGHT / 5, 4 * game.WORLDMAP_HEIGHT / 5)
		h = libtcod.heightmap_get_value(self.hm, sx, sy)
		while h < self.sandheight - 0.02 or h >= self.sandheight:
			sx += 1
			if sx == game.WORLDMAP_WIDTH:
				sx = 0
				sy += 1
				if sy == game.WORLDMAP_HEIGHT:
					sy = 0
			h = libtcod.heightmap_get_value(self.hm, sx, sy)

		tree = []
		randPt = []
		tree.append(sx + sy * game.WORLDMAP_WIDTH)
		riverId += 1
		dx = sx
		dy = sy
		for i in range(0, libtcod.random_get_int(self.rnd, 50, 200)):
			rx = libtcod.random_get_int(self.rnd, sx - 200, sx + 200)
			ry = libtcod.random_get_int(self.rnd, sy - 200, sy + 200)
			randPt.append(rx + ry * game.WORLDMAP_WIDTH)

		for i in range(0, len(randPt)):
			rx = randPt[i] % game.WORLDMAP_WIDTH
			ry = randPt[i] / game.WORLDMAP_WIDTH
			minDist = 1 ** 10
			bestx, besty = -1, -1
			for j in range(0, len(tree)):
				tx = tree[j] % game.WORLDMAP_WIDTH
				ty = tree[j] / game.WORLDMAP_WIDTH
				dist = (tx - rx) * (tx - rx) + (ty - ry) * (ty - ry)
				if dist < minDist:
					minDist = dist
					bestx = tx
					besty = ty

	def generate(self):
		self.noise = libtcod.noise_new(2, self.rnd)
		self.noise1d = libtcod.noise_new(1)
		self.noise2d = libtcod.noise_new(2)
		self.hm = libtcod.heightmap_new(game.WORLDMAP_WIDTH, game.WORLDMAP_HEIGHT)
		self.hmcopy = libtcod.heightmap_new(game.WORLDMAP_WIDTH, game.WORLDMAP_HEIGHT)
		self.precipitation = libtcod.heightmap_new(game.WORLDMAP_WIDTH, game.WORLDMAP_HEIGHT)
		self.temperature = libtcod.heightmap_new(game.WORLDMAP_WIDTH, game.WORLDMAP_HEIGHT)

		self.build_base_map()
		self.compute_precipitations()
		self.smooth_map()
		self.set_land_mass(0.5, self.sandheight)
		t0 = libtcod.sys_elapsed_seconds()
		for i in range(0, 500):
			self.generate_rivers()
		t1 = libtcod.sys_elapsed_seconds()
		print "Rivers: ", t1 - t0

		self.smooth_precipitations()
		self.compute_temperatures_and_biomes()

	def generate2(self):
		self.noise = libtcod.noise_new(2, self.rnd)
		libtcod.noise_set_type(self.noise, libtcod.NOISE_PERLIN)
		self.hm = libtcod.heightmap_new(game.WORLDMAP_WIDTH, game.WORLDMAP_HEIGHT)
		self.hmcopy = libtcod.heightmap_new(game.WORLDMAP_WIDTH, game.WORLDMAP_HEIGHT)
		self.precipitation = libtcod.heightmap_new(game.WORLDMAP_WIDTH, game.WORLDMAP_HEIGHT)
		self.temperature = libtcod.heightmap_new(game.WORLDMAP_WIDTH, game.WORLDMAP_HEIGHT)
		self.mask = libtcod.heightmap_new(game.WORLDMAP_WIDTH, game.WORLDMAP_HEIGHT)

		self.add_landmass()
		self.smooth_edges()
		self.set_land_mass(libtcod.random_get_float(self.rnd, 0.35, 0.45), self.sandheight)
		#libtcod.heightmap_rain_erosion(self.hm, (game.WORLDMAP_WIDTH * game.WORLDMAP_HEIGHT) / 7, 0.70, 0.01, self.rnd)
		self.save_map()

	def add_landmass(self):
		# create some hills
		t0 = libtcod.sys_elapsed_seconds()
		for i in range(0, game.WORLDMAP_WIDTH / 2):
			radius = libtcod.random_get_float(self.rnd, 50 * (1.0 - 0.7), 50 * (1.0 + 0.7))
			x = libtcod.random_get_int(self.rnd, 0, game.WORLDMAP_WIDTH)
			y = libtcod.random_get_int(self.rnd, 0, game.WORLDMAP_HEIGHT)
			libtcod.heightmap_add_hill(self.hm, x, y, radius, 0.3)
		libtcod.heightmap_normalize(self.hm)
		libtcod.heightmap_add_fbm(self.hm, self.noise, 6.5, 6.5, 0, 0, 8.0, 1.0, 4.0)
		libtcod.heightmap_normalize(self.hm)
		t1 = libtcod.sys_elapsed_seconds()
		print "Adding Hills: ", t1 - t0

		# reduce mountainous regions
#		for x in range(0, game.WORLDMAP_WIDTH):
#			for y in range(0, game.WORLDMAP_HEIGHT):
#				h = libtcod.heightmap_get_value(self.hm, x, y)
#				if h > self.sandheight:
#					coef = (h - self.sandheight) / (1.0 - self.sandheight)
#					h = self.sandheight + coef * coef * coef * (1.0 - self.sandheight)
#					libtcod.heightmap_set_value(self.hm, x, y, h)

	def smooth_edges(self):
		# smooth edges so that land doesnt touch the map borders
		t0 = libtcod.sys_elapsed_seconds()
		for x in range(0, game.WORLDMAP_WIDTH):
			for y in range(0, game.WORLDMAP_HEIGHT):
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
				libtcod.heightmap_set_value(self.mask, x, y, h)
		libtcod.heightmap_normalize(self.mask)
		libtcod.heightmap_copy(self.hm, self.hmcopy)
		libtcod.heightmap_multiply_hm(self.hmcopy, self.mask, self.hm)
		libtcod.heightmap_normalize(self.hm)
		t1 = libtcod.sys_elapsed_seconds()
		print "Smooth Edges: ", t1 - t0

	def set_land_mass(self, landmass, waterlevel):
		t0 = libtcod.sys_elapsed_seconds()
		heightcount = [0] * 256
		for x in range(0, game.WORLDMAP_WIDTH):
			for y in range(0, game.WORLDMAP_HEIGHT):
				h = int(libtcod.heightmap_get_value(self.hm, x, y) * 255)
				heightcount[h] += 1

		i, totalcount = 0, 0
		while totalcount < game.WORLDMAP_WIDTH * game.WORLDMAP_HEIGHT * (1.0 - landmass):
			totalcount += heightcount[i]
			i += 1
		newwaterlevel = i / 255.0
		landcoef = (1.0 - waterlevel) / (1.0 - newwaterlevel)
		watercoef = waterlevel / newwaterlevel

		for x in range(0, game.WORLDMAP_WIDTH):
			for y in range(0, game.WORLDMAP_HEIGHT):
				h = libtcod.heightmap_get_value(self.hm, x, y)
				if h > newwaterlevel:
					h = waterlevel + (h - newwaterlevel) * landcoef
				else:
					h = h * watercoef
				libtcod.heightmap_set_value(self.hm, x, y, h)
		t1 = libtcod.sys_elapsed_seconds()
		print "Fixing Landmass: ", t1 - t0

	def save_map(self):
		t0 = libtcod.sys_elapsed_seconds()
		con = libtcod.console_new(game.WORLDMAP_WIDTH, game.WORLDMAP_HEIGHT)
		for x in range(0, game.WORLDMAP_WIDTH):
			for y in range(0, game.WORLDMAP_HEIGHT):
				cellheight = libtcod.heightmap_get_value(self.hm, x, y)
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

		img = libtcod.image_from_console(con)
		if not os.path.exists('maps'):
			os.makedirs('maps')
		libtcod.image_save(img, 'maps/' + time.strftime('%Y%m%d-%H%M%S') + '.png')
		t1 = libtcod.sys_elapsed_seconds()
		print "Saving map: ", t1 - t0
