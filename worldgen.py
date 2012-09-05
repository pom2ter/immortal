import libtcodpy as libtcod
import game
import math

TUNDRA = libtcod.Color(200, 240, 255)
COLD_DESERT = libtcod.Color(180, 210, 210)
GRASSLAND = libtcod.sea
BOREAL_FOREST = libtcod.Color(14, 93, 43)
TEMPERATE_FOREST = libtcod.Color(44, 177, 83)
TROPICAL_MONTANE_FOREST = libtcod.Color(185, 232, 164)
HOT_DESERT = libtcod.Color(235, 255, 210)
SAVANNA = libtcod.Color(255, 205, 20)
TROPICAL_DRY_FOREST = libtcod.Color(60, 130, 40)
TROPICAL_EVERGREEN_FOREST = libtcod.green
THORN_FOREST = libtcod.Color(192, 192, 112)

ARTIC_ALPINE = 0
COLD = 1
TEMPERATE = 2
WARM = 3
TROPICAL = 4

biomes = [[TUNDRA, TUNDRA, TUNDRA, TUNDRA, TUNDRA],
	[COLD_DESERT, GRASSLAND, BOREAL_FOREST, BOREAL_FOREST, BOREAL_FOREST],
	[COLD_DESERT, GRASSLAND, TEMPERATE_FOREST, TEMPERATE_FOREST, TROPICAL_MONTANE_FOREST],
	[HOT_DESERT, SAVANNA, TROPICAL_DRY_FOREST, TROPICAL_EVERGREEN_FOREST, TROPICAL_EVERGREEN_FOREST],
	[HOT_DESERT, THORN_FOREST, TROPICAL_DRY_FOREST, TROPICAL_EVERGREEN_FOREST, TROPICAL_EVERGREEN_FOREST]]

EClimate = [ARTIC_ALPINE, COLD, TEMPERATE, WARM, TROPICAL]
EBiome = [TUNDRA, COLD_DESERT, GRASSLAND, BOREAL_FOREST, TEMPERATE_FOREST, TROPICAL_MONTANE_FOREST, HOT_DESERT, SAVANNA, TROPICAL_DRY_FOREST, TROPICAL_EVERGREEN_FOREST, THORN_FOREST]




class World(object):
	def __init__(self):
		self.rnd = libtcod.random_new()
		self.noise = 0
		self.noise1d = 0
		self.noise2d = 0
		self.hm = 0
		self.hm2 = 0
		self.precipitation = 0
		self.temperature = 0
		self.biomemap = [0] * (game.WORLDMAP_WIDTH * game.WORLDMAP_HEIGHT)
		self.sandheight = 0.12
		self.grassheight = 0.15
		self.clouds = [[None for y in range(game.WORLDMAP_HEIGHT)] for x in range(game.WORLDMAP_WIDTH)]
		self.clouddx = 0.0
		self.cloudtotaldx = 0.0
		self.worldint = [0] * (game.WORLDMAP_WIDTH * game.WORLDMAP_HEIGHT)
		self.worldimg = libtcod.image_new(game.WORLDMAP_WIDTH, game.WORLDMAP_HEIGHT)
		self.generate2()

	def add_hill(self, nbHill, baseRadius, radiusVar, height):
		for i in range(0, nbHill):
			hillMinRadius = baseRadius * (1.0 - radiusVar)
			hillMaxRadius = baseRadius * (1.0 + radiusVar)
			radius = libtcod.random_get_float(self.rnd, hillMinRadius, hillMaxRadius)
			xh = libtcod.random_get_int(self.rnd, 0, game.WORLDMAP_WIDTH - 1)
			yh = libtcod.random_get_int(self.rnd, 0, game.WORLDMAP_HEIGHT - 1)
			libtcod.heightmap_add_hill(self.hm, float(xh), float(yh), radius, height)

	def set_land_mass(self, landmass, waterlevel):
		t0 = libtcod.sys_elapsed_seconds()
		heightcount = [0] * 256
		for x in range(0, game.WORLDMAP_WIDTH):
			for y in range(0, game.WORLDMAP_HEIGHT):
				h = libtcod.heightmap_get_value(self.hm, x, y)
				ih = int(h * 255)
				ih = max(0, min(ih, 255))
				heightcount[ih] += 1

		i, totalcount = 0, 0
		while totalcount < game.WORLDMAP_WIDTH * game.WORLDMAP_HEIGHT * (1.0 - landmass):
			totalcount += heightcount[i]
			i += 1
		newwaterlevel = i / 255.0
		landcoef = (1.0 - waterlevel) / (1.0 - newwaterlevel)
		watercoef = waterlevel / newwaterlevel

		print newwaterlevel, landcoef, watercoef

		for x in range(0, game.WORLDMAP_WIDTH):
			for y in range(0, game.WORLDMAP_HEIGHT):
				h = libtcod.heightmap_get_value(self.hm, x, y)
				if h > newwaterlevel:
					h = waterlevel + (h - newwaterlevel) * landcoef
				else:
					h = h * watercoef
				libtcod.heightmap_set_value(self.hm, x, y, h)

		t1 = libtcod.sys_elapsed_seconds()
		print "Landmass: ", t1 - t0

	def build_base_map(self):
		t0 = libtcod.sys_elapsed_seconds()
		self.add_hill(300, 32.0, 0.7, 0.3)
		libtcod.heightmap_normalize(self.hm)
		t1 = libtcod.sys_elapsed_seconds()
		print "Hills: ", t1 - t0

		t0 = t1
		libtcod.heightmap_add_fbm(self.hm, self.noise, 2.20 * game.WORLDMAP_WIDTH / 400, 2.20 * game.WORLDMAP_HEIGHT / 400, 0, 0, 10.0, 1.0, 2.05)
		libtcod.heightmap_normalize(self.hm)
		libtcod.heightmap_copy(self.hm, self.hm2)
		t1 = libtcod.sys_elapsed_seconds()
		print "Fbm: ", t1 - t0
		self.set_land_mass(0.5, self.sandheight)

		t0 = libtcod.sys_elapsed_seconds()
		for x in range(0, game.WORLDMAP_WIDTH):
			for y in range(0, game.WORLDMAP_HEIGHT):
				h = libtcod.heightmap_get_value(self.hm, x, y)
				if h > self.sandheight:
					coef = (h - self.sandheight) / (1.0 - self.sandheight)
					h = self.sandheight + coef * coef * coef * (1.0 - self.sandheight)
					libtcod.heightmap_set_value(self.hm, x, y, h)
		t1 = libtcod.sys_elapsed_seconds()
		print "Flatten plains: ", t1 - t0

	def compute_precipitations(self):
		wateradd = 0.03
		slopeCoef = 2.0
		basePrecip = 0.01
		t0 = libtcod.sys_elapsed_seconds()
		for diry in range(-1, 2, 2):
			for x in range(0, game.WORLDMAP_WIDTH):
				noisex = float(x) * 5 / game.WORLDMAP_WIDTH
				wateramount = (1.0 + libtcod.noise_get_fbm(self.noise1d, [noisex], 3.0))
				if diry == -1:
					starty = game.WORLDMAP_HEIGHT - 1
					endy = -1
				else:
					starty = 0
					endy = game.WORLDMAP_HEIGHT
			y = starty
			while y != endy:
				h = libtcod.heightmap_get_value(self.hm, x, y)
				if h < self.sandheight:
					wateramount += wateradd
				elif wateramount > 0.0:
					if y + diry < game.WORLDMAP_HEIGHT:
						slope = libtcod.heightmap_get_value(self.hm, x, y + diry) - h
					else:
						slope = h - libtcod.heightmap_get_value(self.hm, x, y - diry)
					if slope >= 0.0:
						precip = wateramount * (basePrecip + slope * slopeCoef)
						libtcod.heightmap_set_value(self.precipitation, x, y, libtcod.heightmap_get_value(self.precipitation, x, y) + precip)
						wateramount -= precip
						wateramount = max(0.0, wateramount)
				y += diry
		t1 = libtcod.sys_elapsed_seconds()
		print "North/south winds: ", t1 - t0
		t0 = t1

		for dirx in range(-1, 2, 2):
			for y in range(0, game.WORLDMAP_HEIGHT):
				noisey = float(y) * 5 / game.WORLDMAP_HEIGHT
				wateramount = (1.0 + libtcod.noise_get_fbm(self.noise1d, [noisey], 3.0))
				if dirx == -1:
					startx = game.WORLDMAP_WIDTH - 1
					endx = -1
				else:
					startx = 0
					endx = game.WORLDMAP_WIDTH
			x = startx
			while x != endx:
				h = libtcod.heightmap_get_value(self.hm, x, y)
				if h < self.sandheight:
					wateramount += wateradd
				elif wateramount > 0.0:
					if x + dirx < game.WORLDMAP_WIDTH:
						slope = libtcod.heightmap_get_value(self.hm, x + dirx, y) - h
					else:
						slope = h - libtcod.heightmap_get_value(self.hm, x - dirx, y)
					if slope >= 0.0:
						precip = wateramount * (basePrecip + slope * slopeCoef)
						libtcod.heightmap_set_value(self.precipitation, x, y, libtcod.heightmap_get_value(self.precipitation, x, y) + precip)
						wateramount -= precip
						wateramount = max(0.0, wateramount)
				x += dirx
		t1 = libtcod.sys_elapsed_seconds()
		print "East/west winds: ", t1 - t0
		t0 = t1

		mn, mx = libtcod.heightmap_get_minmax(self.precipitation)
		for y in range(game.WORLDMAP_HEIGHT / 4, 3 * game.WORLDMAP_HEIGHT / 4):
			lat = float(y - game.WORLDMAP_HEIGHT / 4) * 2 / game.WORLDMAP_HEIGHT
			coef = math.sin(2 * 3.1415926 * lat)
			for x in range(0, game.WORLDMAP_WIDTH):
				f = [float(x) / game.WORLDMAP_WIDTH, float(y) / game.WORLDMAP_HEIGHT]
				xcoef = coef + 0.5 * libtcod.noise_get_fbm(self.noise2d, f, 3.0)
				precip = libtcod.heightmap_get_value(self.precipitation, x, y)
				precip += (mx - mn) * xcoef * 0.1
				libtcod.heightmap_set_value(self.precipitation, x, y, precip)
		t1 = libtcod.sys_elapsed_seconds()
		print "Latitude: ", t1 - t0
		t0 = t1

		factor = 8
		smallWidth = (game.WORLDMAP_WIDTH + factor - 1) / factor
		smallHeight = (game.WORLDMAP_HEIGHT + factor - 1) / factor
		lowResMap = [0] * (smallWidth * smallHeight)
		for x in range(0, game.WORLDMAP_WIDTH):
			for y in range(0, game.WORLDMAP_HEIGHT):
				v = libtcod.heightmap_get_value(self.precipitation, x, y)
				ix = x / factor
				iy = y / factor
				lowResMap[ix + iy * smallWidth] += v
		coef = 1.0 / factor
		for x in range(0, game.WORLDMAP_WIDTH):
			for y in range(0, game.WORLDMAP_HEIGHT):
				v = self.get_interpolated_intensity(lowResMap, x * coef, y * coef, smallWidth, smallHeight)
				libtcod.heightmap_set_value(self.precipitation, x, y, v)

	def smooth_map(self):
		smoothKernelSize = 9
		smoothKernelDx = [-1, 0, 1, -1, 0, 1, -1, 0, 1]
		smoothKernelDy = [-1, -1, -1, 0, 0, 0, 1, 1, 1]
		smoothKernelWeight = [2, 8, 2, 8, 20, 8, 2, 8, 2]

		t0 = libtcod.sys_elapsed_seconds()
		libtcod.heightmap_kernel_transform(self.hm, smoothKernelSize, smoothKernelDx, smoothKernelDy, smoothKernelWeight, -1000, 1000)
		libtcod.heightmap_kernel_transform(self.hm2, smoothKernelSize, smoothKernelDx, smoothKernelDy, smoothKernelWeight, -1000, 1000)
		libtcod.heightmap_normalize(self.hm)
		t1 = libtcod.sys_elapsed_seconds()
		print "Blur: ", t1 - t0

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

	def smooth_precipitations(self):
		t0 = libtcod.sys_elapsed_seconds()
		temphm = libtcod.heightmap_new(game.WORLDMAP_WIDTH, game.WORLDMAP_HEIGHT)
		libtcod.heightmap_copy(self.precipitation, temphm)

		for i in range(4, 0):
			for x in range(0, game.WORLDMAP_WIDTH):
				minx = x - 2
				maxx = x + 2
				miny = 0
				maxy = 2
				summ = 0.0
				count = 0
				minx = max(0, minx)
				maxx = min(game.WORLDMAP_WIDTH - 1, maxx)
				# compute the kernel sum at x,0
				for ix in range(minx, maxx):
					for iy in range(miny, maxy):
						summ += libtcod.heightmap_get_value(self.precipitation, ix, iy)
						count += 1
				libtcod.heightmap_set_value(temphm, x, 0, summ / count)
				for y in range(1, game.WORLDMAP_HEIGHT):
					if y - 2 >= 0:
						# remove the top-line sum
						for ix in range(minx, maxx):
							summ -= libtcod.heightmap_get_value(self.precipitation, ix, y - 2)
							count -= 1
					if y + 2 < game.WORLDMAP_HEIGHT:
						# add the bottom-line sum
						for ix in range(minx, maxx):
							summ += libtcod.heightmap_get_value(self.precipitation, ix, y + 2)
							count += 1
					libtcod.heightmap_set_value(temphm, x, y, summ / count)

		libtcod.heightmap_copy(temphm, self.precipitation)
		t1 = libtcod.sys_elapsed_seconds()
		print "Blur: ", t1 - t0
		t0 = t1
		libtcod.heightmap_normalize(self.precipitation)
		t1 = libtcod.sys_elapsed_seconds()
		print "Normalization: ", t1 - t0

	def compute_temperatures_and_biomes(self):
		sandCoef = 1.0 / (1.0 - self.sandheight)
		waterCoef = 1.0 / self.sandheight
		for y in range(0, game.WORLDMAP_HEIGHT):
			lat = float(y - game.WORLDMAP_HEIGHT / 2) * 2 / game.WORLDMAP_HEIGHT
			latTemp = 0.5 * (1.0 + math.pow(math.sin(3.1415926 * (lat + 0.5)), 5))  # between 0 and 1
			if (latTemp > 0.0):
				latTemp = math.sqrt(latTemp)
			latTemp = -30 + latTemp * 60
			for x in range(0, game.WORLDMAP_WIDTH):
				h0 = libtcod.heightmap_get_value(self.hm, x, y)
				h = h0 - self.sandheight
				if h < 0.0:
					h *= waterCoef
				else:
					h *= sandCoef
				altShift = -35 * h
				temp = latTemp + altShift
				libtcod.heightmap_set_value(self.temperature, x, y, temp)
				humid = libtcod.heightmap_get_value(self.precipitation, x, y)
				climate = self.get_climate_from_temp(temp)
				iHumid = int(humid * 5)
				iHumid = min(4, iHumid)
				biome = biomes[climate][iHumid]
				self.biomemap[x + y * game.WORLDMAP_WIDTH] = biome
		tmin, tmax = libtcod.heightmap_get_minmax(self.temperature)
		print "Temperatures min/max: ", tmin, " / ", tmax

	def get_climate_from_temp(self, temp):
		if temp <= -5:
			return ARTIC_ALPINE
		if temp <= 5:
			return COLD
		if temp <= 15:
			return TEMPERATE
		if temp <= 20:
			return WARM
		return TROPICAL

	def compute_sun_light(self, light):
		for x in range(0, game.WORLDMAP_WIDTH):
			for y in range(0, game.WORLDMAP_HEIGHT):
				self.worldint[x + y * game.WORLDMAP_WIDTH] = self.get_map_intensity(x + 0.5, y + 0.5, light)

	def get_map_intensity(self, worldx, worldy, light):
		wx = max(0.0, min(worldx, game.WORLDMAP_WIDTH - 1))
		wy = max(0.0, min(worldy, game.WORLDMAP_HEIGHT - 1))
		normal = libtcod.heightmap_get_normal(self.hm2, wx, wy, self.sandheight)
		intensity = 0.75 - (normal[0] * light[0] + normal[1] * light[1] + (normal[2] * 3.0) * light[2]) * 0.75
		intensity = max(0.75, min(intensity, 1.5))
		return intensity

	def get_interpolated_intensity(self, arr, x, y, width, height):
		wx = max(0.0, min(x, width - 1))
		wy = max(0.0, min(y, height - 1))
		iwx = int(wx)
		iwy = int(wy)
		dx = wx - iwx
		dy = wy - iwy

		iNW = arr[iwx + iwy * width]
		iNE, iSW, iSE = iNW, iNW, iNW
		if iwx < width - 1:
			iNE = arr[iwx + 1 + iwy * width]
		if iwy < height - 1:
			iSW = arr[iwx + (iwy + 1) * width]
		if iwx < width - 1 and iwy < height - 1:
			iSE = arr[iwx + (iwy + 1) * width]
		iN = (1.0 - dx) * iNW + dx * iNE
		iS = (1.0 - dx) * iSW + dx * iSE
		return (1.0 - dy) * iN + dy * iS

	def generate(self):
		self.noise = libtcod.noise_new(2, self.rnd)
		self.noise1d = libtcod.noise_new(1)
		self.noise2d = libtcod.noise_new(2)
		self.hm = libtcod.heightmap_new(game.WORLDMAP_WIDTH, game.WORLDMAP_HEIGHT)
		self.hm2 = libtcod.heightmap_new(game.WORLDMAP_WIDTH, game.WORLDMAP_HEIGHT)
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
		self.noise1d = libtcod.noise_new(1)
		self.noise2d = libtcod.noise_new(2)
		self.hm = libtcod.heightmap_new(game.WORLDMAP_WIDTH, game.WORLDMAP_HEIGHT)
		self.precipitation = libtcod.heightmap_new(game.WORLDMAP_WIDTH, game.WORLDMAP_HEIGHT)
		self.temperature = libtcod.heightmap_new(game.WORLDMAP_WIDTH, game.WORLDMAP_HEIGHT)

		self.add_landmass()
		self.set_land_mass(0.5, self.sandheight)
		self.save_world()

	def add_landmass(self):
		# create some hills
		for i in range(0, 300):
			radius = libtcod.random_get_float(self.rnd, 32 * (1.0 - 0.7), 32 * (1.0 + 0.7))
			x = libtcod.random_get_int(self.rnd, int(radius) - 5, game.WORLDMAP_WIDTH - int(radius) - 5)
			y = libtcod.random_get_int(self.rnd, int(radius) - 5, game.WORLDMAP_HEIGHT - int(radius) - 5)
			libtcod.heightmap_add_hill(self.hm, x, y, radius, 0.3)
		libtcod.heightmap_normalize(self.hm)
		libtcod.heightmap_add_fbm(self.hm, self.noise, 2.25, 2.25, 0, 0, 10.0, 1.0, 2.0)
		libtcod.heightmap_normalize(self.hm)

		# reduce mountainous regions
		for x in range(0, game.WORLDMAP_WIDTH):
			for y in range(0, game.WORLDMAP_HEIGHT):
				h = libtcod.heightmap_get_value(self.hm, x, y)
				if h > self.sandheight:
					coef = (h - self.sandheight) / (1.0 - self.sandheight)
					h = self.sandheight + coef * coef * coef * (1.0 - self.sandheight)
					libtcod.heightmap_set_value(self.hm, x, y, h)

	def save_world(self):
		con = libtcod.console_new(game.WORLDMAP_WIDTH, game.WORLDMAP_HEIGHT)
		for x in range(0, game.WORLDMAP_WIDTH):
			for y in range(0, game.WORLDMAP_HEIGHT):
				cellheight = libtcod.heightmap_get_value(self.hm, x, y)
				hcolor = libtcod.darkest_blue
				if cellheight >= 0.065:
					hcolor = libtcod.blue
				if cellheight >= 0.114:
					hcolor = libtcod.light_blue
				if cellheight >= 0.12:
					hcolor = libtcod.light_yellow
				if cellheight >= 0.126:
					hcolor = libtcod.light_green
				if cellheight >= 0.25:
					hcolor = libtcod.green
				if cellheight >= 0.45:
					hcolor = libtcod.dark_green
				if cellheight >= 0.575:
					hcolor = libtcod.Color(53, 33, 16)
				if cellheight >= 0.675:
					hcolor = libtcod.grey
				if cellheight >= 0.90:
					hcolor = libtcod.silver

				if hcolor == libtcod.darkest_blue:
					libtcod.console_put_char_ex(con, x, y, '~', libtcod.Color(24, 24, 240), libtcod.Color(0, 0, 96))
				elif hcolor == libtcod.blue:
					libtcod.console_put_char_ex(con, x, y, '~', libtcod.Color(60, 60, 220), libtcod.Color(24, 24, 240))
				elif hcolor == libtcod.light_blue:
					libtcod.console_put_char_ex(con, x, y, '~', libtcod.Color(172, 172, 255), libtcod.Color(135, 135, 255))
				else:
					libtcod.console_put_char_ex(con, x, y, ' ', hcolor, hcolor)

		img = libtcod.image_from_console(con)
		libtcod.image_save(img, 'worldgen.png')
