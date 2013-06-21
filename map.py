import libtcodpy as libtcod
import math
import copy
import game
import util


class Map(object):
	def __init__(self, name, abbr, id, level, tlevel=1, mw=130, mh=60, typ='Dungeon', empty=False):
		self.location_name = name
		self.location_abbr = abbr
		self.location_id = id
		self.location_level = level
		self.threat_level = tlevel
		self.type = typ
		self.map_width = mw
		self.map_height = mh
		self.max_monsters = min(25, (mw * mh) / 300)
		self.max_items = min(25, (mw * mh) / 300)
		self.objects = None
		self.up_staircase = (0, 0)
		self.down_staircase = (0, 0)
		self.overworld_position = (0, 0, 0)
		self.tile = None
		self.generate(empty)

	# check if player position is inside map boundaries
	def check_player_position(self):
		if game.char.x >= self.map_width or game.char.y >= self.map_height:
			x = libtcod.random_get_int(game.rnd, 0, self.map_width - 1)
			y = libtcod.random_get_int(game.rnd, 0, self.map_height - 1)
			while self.is_blocked(x, y):
				x = libtcod.random_get_int(game.rnd, 0, self.map_width - 1)
				y = libtcod.random_get_int(game.rnd, 0, self.map_height - 1)
			game.char.x = x
			game.char.y = y
			game.message.new('You suddenly feel disoriented', game.turns)

	# create a map with a dungeon type
	# stuff to do: add cavern, town, maze type
	def create_dungeon(self):
		rooms = []
		num_rooms = 0
		for r in range((self.map_width * self.map_height) / 80):
			#random width and height
			w = libtcod.random_get_int(game.rnd, game.ROOM_MIN_SIZE, game.ROOM_MAX_SIZE)
			h = libtcod.random_get_int(game.rnd, game.ROOM_MIN_SIZE, game.ROOM_MAX_SIZE)
			#random position without going out of the boundaries of the map
			x = libtcod.random_get_int(game.rnd, 0, self.map_width - w - 1)
			y = libtcod.random_get_int(game.rnd, 0, self.map_height - h - 1)

			#'Rect' class makes rectangles easier to work with
			new_room = Rect(x, y, w, h)

			#run through the other rooms and see if they intersect with this one
			failed = False
			for other_room in rooms:
				if new_room.intersect(other_room):
					failed = True
					break

			if not failed:
				#this means there are no intersections, so this room is valid
				#'paint' it to the map's tiles
				self.create_room(new_room)

				#center coordinates of new room, will be useful later
				(new_x, new_y) = new_room.center()

				if num_rooms == 0:
					#this is the first room, where the player starts at
					game.char.x = new_x
					game.char.y = new_y
				else:
					#all rooms after the first:
					#connect it to the previous room with a tunnel
					#center coordinates of previous room
					(prev_x, prev_y) = rooms[num_rooms - 1].center()

					#draw a coin (random number that is either 0 or 1)
					if libtcod.random_get_int(game.rnd, 0, 1) == 1:
						#first move horizontally, then vertically
						self.create_h_tunnel(prev_x, new_x, prev_y)
						self.create_v_tunnel(prev_y, new_y, new_x)
					else:
						#first move vertically, then horizontally
						self.create_v_tunnel(prev_y, new_y, prev_x)
						self.create_h_tunnel(prev_x, new_x, new_y)

				#finally, append the new room to the list
				rooms.append(new_room)
				num_rooms += 1
		return rooms

	# create any outdoor map
	# stuff to do: add mountains, mtns peak maps, transitions
	def create_outdoor_map(self, default_tile):
		trees_tiles = 0
		rocks_tiles = 1
		shallow_water_tiles = 2
		deep_water_tiles = 3
		dirt_tiles = 4
		grass_tiles = 5
		medium_grass_tiles = 6
		tall_grass_tiles = 7
		sand_tiles = 8
		tiles = [0] * 9
		icons = ['tree', 'rock', 'shallow water', 'deep water', 'dirt', 'grass', 'medium grass', 'tall grass', 'sand']
		map_size = self.map_width * self.map_height

		# assign values per terrain types
		heightmap = game.worldmap.hm_list[self.location_level]
		if self.type in ['Hills', 'Mountains', 'Mountain Peak']:
			tiles[rocks_tiles] = libtcod.random_get_int(game.rnd, 40, 200)
			tiles[dirt_tiles] = libtcod.random_get_int(game.rnd, int(map_size * heightmap * 0.05), int(map_size * heightmap))
			tiles[grass_tiles] = libtcod.random_get_int(game.rnd, int(map_size * heightmap * 0.05), int(map_size * heightmap))
			tiles[medium_grass_tiles] = libtcod.random_get_int(game.rnd, int(map_size * heightmap * 0.05), int(map_size * heightmap))
			tiles[tall_grass_tiles] = libtcod.random_get_int(game.rnd, 15, 75)
		if self.type == 'Forest':
			tiles[trees_tiles] = libtcod.random_get_int(game.rnd, int(map_size * 0.006), int(map_size * 0.024)) * int(max(1, abs((250 - (heightmap * 1000)) / 80)))
			tiles[rocks_tiles] = libtcod.random_get_int(game.rnd, 30, 150)
			tiles[shallow_water_tiles] = libtcod.random_get_int(game.rnd, 2, 10)
			tiles[dirt_tiles] = libtcod.random_get_int(game.rnd, 40, 200)
			tiles[medium_grass_tiles] = libtcod.random_get_int(game.rnd, int(map_size * 0.006), int(map_size * 0.024)) * int(max(1, abs((250 - (heightmap * 1000)) / 80)))
			tiles[tall_grass_tiles] = libtcod.random_get_int(game.rnd, int(map_size * 0.006), int(map_size * 0.024)) * int(max(1, abs((250 - (heightmap * 1000)) / 80)))
		if self.type == 'Plains':
			tiles[trees_tiles] = libtcod.random_get_int(game.rnd, int(map_size * 0.001), int(map_size * 0.005)) * int(max(1, abs((175 - (heightmap * 1000)) / 12)))
			tiles[rocks_tiles] = libtcod.random_get_int(game.rnd, 20, 100)
			tiles[shallow_water_tiles] = libtcod.random_get_int(game.rnd, 5, 25)
			tiles[dirt_tiles] = libtcod.random_get_int(game.rnd, 30, 150)
			tiles[medium_grass_tiles] = libtcod.random_get_int(game.rnd, int(map_size * 0.001), int(map_size * 0.005)) * int(max(1, abs((175 - (heightmap * 1000)) / 12)))
			tiles[tall_grass_tiles] = libtcod.random_get_int(game.rnd, int(map_size * 0.001), int(map_size * 0.005)) * int(max(1, abs((175 - (heightmap * 1000)) / 12)))
			tiles[sand_tiles] = libtcod.random_get_int(game.rnd, int(map_size * 0.001), int(map_size * 0.005)) * int(max(1, abs((250 - (heightmap * 1000)) / 12)))
		if self.type == 'Coast':
			tiles[rocks_tiles] = libtcod.random_get_int(game.rnd, int(map_size * 0.005), int(map_size * 0.025))
			tiles[shallow_water_tiles] = libtcod.random_get_int(game.rnd, int(map_size * 0.001), int(map_size * 0.005))
			tiles[dirt_tiles] = libtcod.random_get_int(game.rnd, int(map_size * 0.005), int(map_size * 0.025))
			tiles[grass_tiles] = libtcod.random_get_int(game.rnd, int(map_size * 0.005), int(map_size * 0.025))
		if self.type == 'Shore':
			tiles[rocks_tiles] = libtcod.random_get_int(game.rnd, int(map_size * 0.003), int(map_size * 0.015))
			tiles[deep_water_tiles] = libtcod.random_get_int(game.rnd, int(map_size * 0.001), int(map_size * 0.005)) * int(max(1, abs((120 - (heightmap * 1000)) / 2)))
			tiles[sand_tiles] = libtcod.random_get_int(game.rnd, int(map_size * 0.005), int(map_size * 0.025))
		if self.type == 'Sea':
			tiles[shallow_water_tiles] = libtcod.random_get_int(game.rnd, int(map_size * 0.001), int(map_size * 0.005)) * int(max(1, abs((60 - (heightmap * 1000)) / 9)))

		# place tiles on map
		for j in range(len(tiles)):
			for i in range(tiles[j]):
				x = libtcod.random_get_int(game.rnd, 0, self.map_width - 1)
				y = libtcod.random_get_int(game.rnd, 0, self.map_height - 1)
				while (self.tile[x][y]['name'] != default_tile):
					x = libtcod.random_get_int(game.rnd, 0, self.map_width - 1)
					y = libtcod.random_get_int(game.rnd, 0, self.map_height - 1)
				self.set_tile_values(icons[j], x, y)
				if icons[j] == 'tree':
					dice = libtcod.random_get_int(game.rnd, 1, 100)
					if dice % 2 == 0:
						self.set_tile_values(icons[j], x, y, type='trees2')

				if icons[j] == 'shallow water' or (self.type == 'Shore' and icons[j] == 'deep water'):
					length = libtcod.random_get_int(game.rnd, 10, 20)
					direction = libtcod.random_get_int(game.rnd, 0, 39)
					startx = x
					starty = y
					while length > 0:
						nextstep = libtcod.random_get_int(game.rnd, 1, 7)
						stepx, stepy = 0, 0
						if nextstep > 2:
							if direction % 4 == 0:
								stepy -= 1
							if direction % 4 == 1:
								stepx += 1
							if direction % 4 == 2:
								stepy += 1
							if direction % 4 == 3:
								stepx -= 1
						if nextstep == 1:
							if direction % 4 == 0:
								stepx -= 1
							if direction % 4 == 1:
								stepy -= 1
							if direction % 4 == 2:
								stepx += 1
							if direction % 4 == 3:
								stepy += 1
						if nextstep == 2:
							if direction % 4 == 0:
								stepx += 1
							if direction % 4 == 1:
								stepy += 1
							if direction % 4 == 2:
								stepx -= 1
							if direction % 4 == 3:
								stepy -= 1
						startx += stepx
						starty += stepy
						if startx < self.map_width and starty < self.map_height:
							self.set_tile_values(icons[j], startx, starty)
						length -= 1
		self.place_dungeons()

	# go through the tiles in the rectangle and make them passable
	def create_room(self, room):
		for x in range(room.x1 + 1, room.x2):
			for y in range(room.y1 + 1, room.y2):
				self.set_tile_values('floor', x, y)

	# horizontal tunnel. min() and max() are used in case x1>x2
	def create_h_tunnel(self, x1, x2, y):
		for x in range(min(x1, x2), max(x1, x2) + 1):
			self.set_tile_values('floor', x, y)

	# vertical tunnel
	def create_v_tunnel(self, y1, y2, x):
		for y in range(min(y1, y2), max(y1, y2) + 1):
			self.set_tile_values('floor', x, y)

	# returns true if tile is animated
	def is_animate(self, x, y):
		if 'animate' in self.tile[x][y]:
			return True
		return False

	# returns true if tile is blocked
	def is_blocked(self, x, y, include_obj=True):
		if 'blocked' in self.tile[x][y]:
			return True
		if include_obj:
			for obj in self.objects:
				if obj.blocks and obj.x == x and obj.y == y:
					return True
		return False

	# returns true if tile is explored
	def is_explored(self, x, y):
		if 'explored' in self.tile[x][y]:
			return True
		return False

	# returns true if tile is invisible
	def is_invisible(self, x, y):
		if 'invisible' in self.tile[x][y]:
			return True
		return False

	# returns true if tile block your view
	def is_sight_blocked(self, x, y):
		if 'block_sight' in self.tile[x][y]:
			return True
		return False

	# place doors in dungeon level
	# stuff to do: add locked doors
	def place_doors(self):
		for y in range(1, self.map_height - 1):
			for x in range(1, self.map_width - 1):
				if (self.tile[x + 1][y]['name'] == 'floor' and self.tile[x - 1][y]['name'] == 'floor' and self.tile[x][y - 1]['name'] == 'wall' and self.tile[x][y + 1]['name'] == 'wall') or (self.tile[x + 1][y]['name'] == 'wall' and self.tile[x - 1][y]['name'] == 'wall' and self.tile[x][y - 1]['name'] == 'floor' and self.tile[x][y + 1]['name'] == 'floor'):
					if libtcod.random_get_int(game.rnd, 1, 50) == 50:
						self.set_tile_values('door', x, y)

	# place dungeon entrance on map if there is one
	def place_dungeons(self):
		for (id, name, abbr, x, y, tlevel) in game.worldmap.dungeons:
			if (y * game.WORLDMAP_WIDTH) + x == self.location_level:
				dx = libtcod.random_get_int(game.rnd, 0, self.map_width - 9)
				dy = libtcod.random_get_int(game.rnd, 0, self.map_height - 9)
				room = Rect(dx, dy, 8, 8)
				self.create_room(room)
				for i in range(dx, dx + 7):
					self.set_tile_values('wall', i + 1, dy + 1)
					self.set_tile_values('wall', i + 1, dy + 7)
				for i in range(dy, dy + 7):
					self.set_tile_values('wall', dx + 1, i + 1)
					self.set_tile_values('wall', dx + 7, i + 1)
				door = libtcod.random_get_int(game.rnd, 0, 4)
				doorx, doory = dx + 1, dy + 4
				if door == 0:
					doorx = dx + 4
					doory = dy + 1
				elif door == 1:
					doorx = dx + 7
					doory = dy + 4
				elif door == 2:
					doorx = dx + 4
					doory = dy + 7
				self.set_tile_values('opened door', doorx, doory)
				(stairs_x, stairs_y) = room.center()
				self.set_tile_values('stairs going down', stairs_x, stairs_y)
				self.down_staircase = (stairs_x, stairs_y)

	# place monsters on current map
	def place_monsters(self):
		x = libtcod.random_get_int(game.rnd, 0, self.map_width - 1)
		y = libtcod.random_get_int(game.rnd, 0, self.map_height - 1)
		while (self.is_blocked(x, y) or self.tile[x][y]['name'] in ['deep water', 'very deep water']):
			x = libtcod.random_get_int(game.rnd, 0, self.map_width - 1)
			y = libtcod.random_get_int(game.rnd, 0, self.map_height - 1)

		# fetch monster to place base on threat level
		dice = util.roll_dice(1, 100)
		if dice <= 80:
			d = game.monsters.get_monster_by_level(self.threat_level)
		elif dice <= 99:
			d = game.monsters.get_monster_by_level(self.threat_level + 1)
		else:
			d = game.monsters.get_monster_by_level(self.threat_level + 2)
		monster = Object(x, y, d.icon, d.name, d.color, blocks=True, entity=d)
		self.objects.insert(1, monster)

	# place the different 'objects' on current map
	def place_objects(self):
		num_monsters = libtcod.random_get_int(game.rnd, self.max_monsters / 5, self.max_monsters)
		num_items = libtcod.random_get_int(game.rnd, self.max_items / 5, self.max_items)
		if self.type in ['Sea', 'Ocean']:
			num_items, num_monsters = 0, 0
		for i in range(num_monsters):
			self.place_monsters()

		for i in range(num_items):
			x = libtcod.random_get_int(game.rnd, 0, self.map_width - 1)
			y = libtcod.random_get_int(game.rnd, 0, self.map_height - 1)
			while (self.is_blocked(x, y) or self.tile[x][y]['name'] in ['deep water', 'very deep water']):
				x = libtcod.random_get_int(game.rnd, 0, self.map_width - 1)
				y = libtcod.random_get_int(game.rnd, 0, self.map_height - 1)
			loot = game.baseitems.loot_generation(x, y, self.threat_level)
			self.objects.append(loot)

	# places up and down stairs on dungeon level
	def place_stairs(self, rooms):
		# place stairs going up based on character position
		if self.location_level > 1:
			self.set_tile_values('stairs going up', game.char.x, game.char.y)
			self.up_staircase = (game.char.x, game.char.y)
		else:
			stairs = libtcod.random_get_int(game.rnd, 1, len(rooms) - 1)
			(x, y) = rooms[stairs].center()
			self.set_tile_values('stairs going up', x, y)
			self.up_staircase = (x, y)
			game.char.x = x
			game.char.y = y

		# place stairs going down in a random spot
		stairs = libtcod.random_get_int(game.rnd, 1, len(rooms) - 1)
		(x, y) = rooms[stairs].center()
		while self.tile[x][y]['type'] == 'stairs':
			stairs = libtcod.random_get_int(game.rnd, 1, len(rooms) - 1)
			(x, y) = rooms[stairs].center()
		self.set_tile_values('stairs going down', x, y)
		self.down_staircase = (x, y)

	# place up to 3 traps in a dungeon level
	def place_traps(self):
		traps = libtcod.random_get_int(game.rnd, 1, 3)
		for i in range(0, traps):
			x = libtcod.random_get_int(game.rnd, 0, self.map_width - 1)
			y = libtcod.random_get_int(game.rnd, 0, self.map_height - 1)
			while (self.tile[x][y]['type'] != 'floor'):
				x = libtcod.random_get_int(game.rnd, 0, self.map_width - 1)
				y = libtcod.random_get_int(game.rnd, 0, self.map_height - 1)
			self.set_tile_values('trap', x, y, 'trap')
			temp_tile = game.tiles.get_tile('floor')
			self.tile[x][y].update({'icon': temp_tile.icon, 'color': temp_tile.color, 'dark_color': libtcod.color_lerp(libtcod.black, temp_tile.color, 0.3)})

	# set initial values for each tile of map
	def set_tile_values(self, default, x, y, type=None, reset=True):
		if reset:
			self.tile[x][y] = {}
		if type is not None:
			if type == 'trap':
				temp_tile = game.tiles.find_trap()
			else:
				temp_tile = game.tiles.get_tile_from_type(default, type)
		else:
			temp_tile = game.tiles.get_tile(default)

		self.tile[x][y].update({'icon': temp_tile.icon, 'name': temp_tile.name, 'type': temp_tile.type, 'article': temp_tile.article})
		self.tile[x][y].update({'color': temp_tile.color, 'dark_color': temp_tile.dark_color})
		self.tile[x][y].update({'dark_back_color': temp_tile.dark_back_color})
		if temp_tile.blocked:
			self.tile[x][y].update({'blocked': True})
		if temp_tile.block_sight:
			self.tile[x][y].update({'block_sight': True})
		if temp_tile.flags:
			for i in temp_tile.flags:
				self.tile[x][y].update({i: True})

		back_lerp = round(libtcod.random_get_float(game.rnd, 0, 1), 1)
		back_color = libtcod.color_lerp(temp_tile.back_color_high, temp_tile.back_color_low, back_lerp)
		if temp_tile.color_low != libtcod.black:
			fore_lerp = round(libtcod.random_get_float(game.rnd, 0, 1), 1)
			fore_color = libtcod.color_lerp(temp_tile.color, temp_tile.color_low, fore_lerp)
		else:
			fore_color = temp_tile.color
		if self.is_animate(x, y):
			self.tile[x][y].update({'back_light_color': temp_tile.back_color_high, 'back_dark_color': temp_tile.back_color_low, 'lerp': back_lerp})
		else:
			self.tile[x][y].update({'color': fore_color, 'back_light_color': back_color, 'back_dark_color': libtcod.color_lerp(libtcod.black, back_color, 0.2), 'lerp': back_lerp})

	# main function for generating a map
	def generate(self, empty=False):
		default_block_tiles = {'Dungeon': 'wall', 'Mountain Peak': 'high mountains', 'Mountains': 'mountains', 'Hills': 'hills', 'Forest': 'grass', 'Plains': 'grass', 'Coast': 'sand', 'Shore': 'shallow water', 'Sea': 'deep water', 'Ocean': 'very deep water'}
		self.objects = [game.char]
		self.tile = [[{} for y in range(self.map_height)] for x in range(self.map_width)]
		for x in range(self.map_width):
			for y in range(self.map_height):
				self.set_tile_values(default_block_tiles[self.type], x, y, reset=False)
		game.fov_noise = libtcod.noise_new(1, 1.0, 1.0)
		game.fov_torchx = 0.0

		if not empty:
			if self.type == 'Dungeon':
				rooms = self.create_dungeon()
				self.place_doors()
				self.place_objects()
				self.place_traps()
				self.place_stairs(rooms)
			elif not self.type in ['Mountains', 'Mountain Peak']:
				self.create_outdoor_map(default_block_tiles[self.type])
				self.place_objects()


class Tile(object):
	def __init__(self, icon, name, color, color_low, dark_color, back_color_high, back_color_low, dark_back_color, blocked, block_sight=None, article=None, flags=None, typ=None):
		self.blocked = blocked
		self.name = name
		self.icon = icon
		self.type = typ
		self.color = libtcod.Color(color[0], color[1], color[2])
		self.color_low = libtcod.Color(color_low[0], color_low[1], color_low[2])
		self.dark_color = libtcod.Color(dark_color[0], dark_color[1], dark_color[2])
		self.back_color_high = libtcod.Color(back_color_high[0], back_color_high[1], back_color_high[2])
		self.back_color_low = libtcod.Color(back_color_low[0], back_color_low[1], back_color_low[2])
		self.dark_back_color = libtcod.Color(dark_back_color[0], dark_back_color[1], dark_back_color[2])
		self.article = article
		self.flags = flags

		# by default, if a tile is blocked, it also blocks sight
		if block_sight is None:
			block_sight = blocked
		self.block_sight = block_sight

	# returns true if this tile animates
	def is_animate(self):
		if 'animate' in self.flags:
			return True
		return False

	# returns true if this tile is invisible
	def is_invisible(self):
		if 'invisible' in self.flags:
			return True
		return False


class TileList(object):
	def __init__(self):
		self.list = []

	# setup the items structure and run parser
	def init_parser(self):
		parser = libtcod.parser_new()
		tile_type_struct = libtcod.parser_new_struct(parser, 'tile_type')
		libtcod.struct_add_property(tile_type_struct, 'type', libtcod.TYPE_STRING, True)
		libtcod.struct_add_property(tile_type_struct, 'icon', libtcod.TYPE_STRING, True)
		libtcod.struct_add_property(tile_type_struct, 'icon_color_h', libtcod.TYPE_COLOR, True)
		libtcod.struct_add_property(tile_type_struct, 'icon_color_l', libtcod.TYPE_COLOR, False)
		libtcod.struct_add_property(tile_type_struct, 'back_color_h', libtcod.TYPE_COLOR, False)
		libtcod.struct_add_property(tile_type_struct, 'back_color_l', libtcod.TYPE_COLOR, False)
		libtcod.struct_add_property(tile_type_struct, 'article', libtcod.TYPE_STRING, True)
		libtcod.struct_add_flag(tile_type_struct, 'blocked')
		libtcod.struct_add_flag(tile_type_struct, 'block_sight')
		libtcod.struct_add_flag(tile_type_struct, 'animate')
		libtcod.struct_add_flag(tile_type_struct, 'invisible')
		libtcod.struct_add_flag(tile_type_struct, 'fx_teleport')
		libtcod.struct_add_flag(tile_type_struct, 'fx_stuck')
		libtcod.struct_add_flag(tile_type_struct, 'fx_poison_gas')
		libtcod.struct_add_flag(tile_type_struct, 'fx_sleep_gas')
		libtcod.struct_add_flag(tile_type_struct, 'fx_fireball')
		libtcod.parser_run(parser, 'data/tiles.txt', TileListener())

	# add a tile to the list
	def add_to_list(self, tile=None):
		if tile is not None:
			if 'blocked' in tile.flags:
				tile.blocked = True
			if 'block_sight' in tile.flags:
				tile.block_sight = True
			self.list.append(tile)

	# get a tile from the list
	def get_tile(self, name):
		for tile in self.list:
			if name == tile.name:
				return tile
		return None

	# get a tile from a particular type
	def get_tile_from_type(self, name, type):
		for tile in self.list:
			if name == tile.name and type == tile.type:
				return tile
		return None

	# get a trap tile from the list
	def find_trap(self):
		tile = libtcod.random_get_int(game.rnd, 0, len(self.list) - 1)
		while self.list[tile].type != 'trap':
			tile = libtcod.random_get_int(game.rnd, 0, len(self.list) - 1)
		return self.list[tile]


class TileListener(object):
	def new_struct(self, struct, name):
		self.temp_tile = Tile('', '', [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], False, False, '', [], '')
		self.temp_tile.name = name
		return True

	def new_flag(self, name):
		self.temp_tile.flags.append(name)
		return True

	def new_property(self, name, typ, value):
		if name == 'icon_color_h':
			self.temp_tile.color.r = value.r
			self.temp_tile.color.g = value.g
			self.temp_tile.color.b = value.b
		elif name == 'icon_color_l':
			self.temp_tile.color_low.r = value.r
			self.temp_tile.color_low.g = value.g
			self.temp_tile.color_low.b = value.b
		elif name == 'back_color_h':
			self.temp_tile.back_color_high.r = value.r
			self.temp_tile.back_color_high.g = value.g
			self.temp_tile.back_color_high.b = value.b
		elif name == 'back_color_l':
			self.temp_tile.back_color_low.r = value.r
			self.temp_tile.back_color_low.g = value.g
			self.temp_tile.back_color_low.b = value.b
		else:
			if name == 'type':
				self.temp_tile.type = value
			if name == 'icon':
				self.temp_tile.icon = value
			if name == 'article':
				self.temp_tile.article = value
		return True

	def end_struct(self, struct, name):
		self.temp_tile.dark_color = libtcod.color_lerp(libtcod.black, self.temp_tile.color, 0.2)
		self.temp_tile.dark_back_color = libtcod.color_lerp(libtcod.black, self.temp_tile.back_color_low, 0.2)
		if self.temp_tile.type == 'trees1':
			self.temp_tile.icon = chr(5)
		if self.temp_tile.type == 'trees2':
			self.temp_tile.icon = chr(6)
		game.tiles.add_to_list(self.temp_tile)
		return True

	def error(self, msg):
		print 'error : ', msg
		return True


class Rect(object):
	# a rectangle on the map. used to characterize a room.
	def __init__(self, x, y, w, h):
		self.x1 = x
		self.y1 = y
		self.x2 = x + w
		self.y2 = y + h

	# return center of a rectangle
	def center(self):
		center_x = (self.x1 + self.x2) / 2
		center_y = (self.y1 + self.y2) / 2
		return (center_x, center_y)

	# returns true if this rectangle intersects with another one
	def intersect(self, other):
		return (self.x1 <= other.x2 and self.x2 >= other.x1 and
				self.y1 <= other.y2 and self.y2 >= other.y1)


class Object(object):
	# this is a generic object: the player, a monster, an item, the stairs...
	# it's always represented by a character on screen.
	def __init__(self, x, y, char, name, color, pickup=False, blocks=False, entity=None, item=None):
		self.x = x
		self.y = y
		self.name = name
		self.color = color
		self.can_be_pickup = pickup
		self.first_appearance = game.turns
		self.blocks = blocks

		self.char = char
		self.item = item
		if entity is not None:
			self.entity = copy.deepcopy(entity)
		else:
			self.entity = entity

	# move by the given amount, if the destination is not blocked
	def move(self, dx, dy, map):
		if not map.is_blocked(self.x + dx, self.y + dy):
			self.x += dx
			self.y += dy
			util.add_turn()
		elif map.tile[self.x + dx][self.y + dy]['type'] == 'wall':
			game.message.new('The wall laughs at your attempt to pass through it.', game.turns)

	# return the distance to another object
	def distance_to(self, other):
		dx = other.x - self.x
		dy = other.y - self.y
		return math.sqrt(dx ** 2 + dy ** 2)

	# return the distance to some coordinates
	def distance(self, x, y):
		return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

	# make this object be drawn first, so all others appear above it if they're in the same tile.
	def send_to_back(self):
		game.current_map.objects.remove(self)
		game.current_map.objects.insert(1, self)

	# delete this object
	def delete(self):
		game.current_map.objects.remove(self)

	# draw objects on console only if it's visible to the player
	def draw(self, con):
		if libtcod.map_is_in_fov(game.fov_map, self.x, self.y):
			libtcod.console_set_default_foreground(con, self.color)
			libtcod.console_put_char(con, self.x - game.curx, self.y - game.cury, self.char, libtcod.BKGND_NONE)
		elif game.current_map.is_explored(self.x, self.y) and self.can_be_pickup:
			libtcod.console_set_default_foreground(con, self.item.dark_color)
			libtcod.console_put_char(con, self.x - game.curx, self.y - game.cury, self.char, libtcod.BKGND_NONE)

	# erase the character that represents this object
	def clear(self, con):
		libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)

	# return coordinates of object
	def coordinates(self):
		return self.x, self.y


# main functions for building the overworld maps
def change_maps(did, dlevel):
	util.loadgen_message()
	decombine_maps()
	game.old_maps.append(game.current_map)
	for i in range(len(game.border_maps)):
		game.old_maps.append(game.border_maps[i])
	load_old_maps(did, dlevel)
	combine_maps()
	util.initialize_fov()
	game.fov_recompute = True


# check to see if destination map already exist, if so fetch it, if not generate it
def load_old_maps(did, dlevel):
	coord = [dlevel - game.WORLDMAP_WIDTH - 1, dlevel - game.WORLDMAP_WIDTH, dlevel - game.WORLDMAP_WIDTH + 1, dlevel - 1, dlevel + 1, dlevel + game.WORLDMAP_WIDTH - 1, dlevel + game.WORLDMAP_WIDTH, dlevel + game.WORLDMAP_WIDTH + 1, dlevel]
	game.rnd = libtcod.random_new()
	for j in range(len(coord)):
		generate = True
		for i in xrange(len(game.old_maps)):
			if game.old_maps[i].location_id == did and game.old_maps[i].location_level == coord[j]:
				temp_map = game.old_maps[i]
				game.old_maps.pop(i)
				generate = False
				break
		if generate:
			temp_map = Map(game.current_map.location_name, game.current_map.location_abbr, did, coord[j], game.worldmap.set_threat_level(coord[j] % game.WORLDMAP_WIDTH, coord[j] / game.WORLDMAP_WIDTH), game.current_map.map_width, game.current_map.map_height, find_terrain_type(coord[j]))
		if j == len(coord) - 1:
			game.current_map = temp_map
		else:
			game.border_maps[j] = temp_map


# combine some overworld maps into a super map
def combine_maps():
	mapid = [[0, 1, 2], [3, 0, 4], [5, 6, 7]]
	super_map = Map(game.current_map.location_name, game.current_map.location_abbr, game.current_map.location_id, game.current_map.location_level, game.current_map.threat_level, game.current_map.map_width * 3, game.current_map.map_height * 3, game.current_map.type, True)
	game.char.x += game.current_map.map_width
	game.char.y += game.current_map.map_height
	super_map.objects.append(game.char)
	for i in range(3):
		for j in range(3):
			if i == 1 and j == 1:
				current = game.current_map
			else:
				current = game.border_maps[mapid[i][j]]
			for x in range(game.current_map.map_width):
				for y in range(game.current_map.map_height):
					super_map.tile[x + (j * game.current_map.map_width)][y + (i * game.current_map.map_height)] = current.tile[x][y]
			for obj in current.objects:
				if obj.name != 'player':
					obj.x = obj.x + (j * game.current_map.map_width)
					obj.y = obj.y + (i * game.current_map.map_height)
					super_map.objects.append(obj)
	game.current_backup = game.current_map
	game.current_map = super_map


# decombine the super map into their respective smaller chunks
def decombine_maps():
	mapid = [[0, 1, 2], [3, 0, 4], [5, 6, 7]]
	super_map = game.current_map
	for i in range(3):
		for j in range(3):
			if i == 1 and j == 1:
				current = game.current_backup
			else:
				current = game.border_maps[mapid[i][j]]
			for x in range(current.map_width):
				for y in range(current.map_height):
					current.tile[x][y] = super_map.tile[x + (j * current.map_width)][y + (i * current.map_height)]
			current.objects = []
			current.objects.append(game.char)
			for obj in super_map.objects:
				if obj.name != 'player' and obj.x / (super_map.map_width / 3) == j and obj.y / (super_map.map_height / 3) == i:
					obj.x = obj.x - (j * (super_map.map_width / 3))
					obj.y = obj.y - (i * (super_map.map_height / 3))
					current.objects.append(obj)
			if i == 1 and j == 1:
				game.current_map = current
			else:
				game.border_maps[mapid[i][j]] = current
	if game.char.x >= game.current_map.map_width * 2:
		game.char.x -= game.current_map.map_width * 2
	elif game.char.x >= game.current_map.map_width:
		game.char.x -= game.current_map.map_width
	if game.char.y >= game.current_map.map_height * 2:
		game.char.y -= game.current_map.map_height * 2
	elif game.char.y >= game.current_map.map_height:
		game.char.y -= game.current_map.map_height


# find terrain type base on elevation
def find_terrain_type(coord):
	heightmap = game.worldmap.hm_list[coord]
	for i in range(len(game.terrain)):
		if heightmap >= game.terrain[i]['elevation']:
			terrain = game.terrain[i]['name']
			break
	return terrain
