import libtcodpy as libtcod
import game
import math


class World(object):
	def __init__(self):
		self.rnd = libtcod.random_new()
		self.noise = 0
		self.noise1d = 0
		self.noise2d = 0
		self.hm = 0
		self.hm2 = 0
		self.precipitation = 0
		self.sandheight = 0.12
		self.grassheight = 0.16
		self.clouds = [[None for y in range(game.WORLDMAP_HEIGHT)] for x in range(game.WORLDMAP_WIDTH)]
		self.clouddx = 0.0
		self.cloudtotaldx = 0.0
		self.worldint = [0] * (game.WORLDMAP_WIDTH * game.WORLDMAP_HEIGHT)
		self.worldimg = libtcod.image_new(game.WORLDMAP_WIDTH, game.WORLDMAP_HEIGHT)
		self.generate()

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
		self.build_base_map()
		self.compute_precipitations()

#	def update_clouds(self, elapsedtime):
#		self.cloudtotaldx += elapsedtime * 5
#		self.clouddx += elapsedtime * 5
#		if self.clouddx >= 1.0:
#			colsToTranslate = int(self.clouddx)
#			self.clouddx -= colsToTranslate
#			for x in range(colsToTranslate, game.WORLDMAP_WIDTH):
#				for y in range(0, game.WORLDMAP_HEIGHT):
#					self.clouds[x - colsToTranslate][y] = self.clouds[x][y]
#			f = [0] * 2
#			cdx = int(self.cloudtotaldx)
#			for x in range(game.WORLDMAP_WIDTH - colsToTranslate, game.WORLDMAP_WIDTH):
#				for y in range(0, game.WORLDMAP_HEIGHT):
#					f[0] = 6.0 * ((x + cdx) / game.WORLDMAP_WIDTH)
#					f[1] = 6.0 * (y / game.WORLDMAP_HEIGHT)
#					self.clouds[x][y] = 0.5 * (1.0 + 0.8 * libtcod.noise_get_fbm(self.noise, f, 4.0))

#	def get_cloud_thickness(self, x, y):
#		x += self.clouddx
#		ix, iy = int(x), int(y)
#		ix1, iy1 = min(game.WORLDMAP_WIDTH - 1, ix + 1), min(game.WORLDMAP_HEIGHT - 1, iy + 1)
#		fdx, fdy = x - ix, y - iy
#		v1, v2 = self.clouds[ix][iy], self.clouds[ix1][iy]
#		v3, v4 = self.clouds[ix][iy1], self.clouds[ix1][iy1]
#		vx1 = ((1.0 - fdx) * v1 + fdx * v2)
#		vx2 = ((1.0 - fdx) * v3 + fdx * v4)
#		v = ((1.0 - fdy) * vx1 + fdy * vx2)
#		return v

#	def get_interpolated_color(self, x, y):
#		w, h = libtcod.image_get_size(self.worldimg)
#		wx = max(0.0, min(x, w - 1))
#		wy = max(0.0, min(y, h - 1))
#		iwx = int(wx)
#		iwy = int(wy)
#		dx = wx - iwx
#		dy = wy - iwy

#		colNW = libtcod.image_get_pixel(self.worldimg, iwx, iwy)
#		colNE, colSW, colSE = colNW, colNW, colNW
#		if iwx < w - 1:
#			colNE = libtcod.image_get_pixel(self.worldimg, iwx + 1, iwy)
#		if iwy < h - 1:
#			colSW = libtcod.image_get_pixel(self.worldimg, iwx, iwy + 1)
#		if iwx < w - 1 and iwy < h - 1:
#			colSE = libtcod.image_get_pixel(self.worldimg, iwx + 1, iwy + 1)
#		colN = libtcod.color_lerp(colNW, colNE, dx)
#		colS = libtcod.color_lerp(colSW, colSE, dx)
#		col = libtcod.color_lerp(colN, colS, dy)
#		return col
