import libtcodpy as libtcod
import math
import game


class Map(object):
	def __init__(self, name, abbr, id, level, mw=120, mh=72, typ='Dungeon', empty=False):
		self.location_name = name
		self.location_abbr = abbr
		self.location_id = id
		self.location_level = level
		self.type = typ
		self.map_width = mw
		self.map_height = mh
		self.max_monsters = min(25, (mw * mh) / 300)
		self.max_items = min(25, (mw * mh) / 300)
		self.tiles = None
		self.explored = None
		self.objects = None
		self.up_staircase = (0, 0)
		self.down_staircase = (0, 0)
		self.overworld_position = (0, 0, 0)
		self.generate(empty)

	def is_blocked(self, x, y):
		#first test the map tile
		if self.tiles[x][y].blocked:
			return True

		#now check for any blocking objects
		for obj in self.objects:
			if obj.blocks and obj.x == x and obj.y == y:
				return True
		return False

	def create_room(self, room):
		#go through the tiles in the rectangle and make them passable
		for x in range(room.x1 + 1, room.x2):
			for y in range(room.y1 + 1, room.y2):
				self.tiles[x][y] = game.tiles.get_tile('floor')

	def create_h_tunnel(self, x1, x2, y):
		#horizontal tunnel. min() and max() are used in case x1>x2
		for x in range(min(x1, x2), max(x1, x2) + 1):
			self.tiles[x][y] = game.tiles.get_tile('floor')

	def create_v_tunnel(self, y1, y2, x):
		#vertical tunnel
		for y in range(min(y1, y2), max(y1, y2) + 1):
			self.tiles[x][y] = game.tiles.get_tile('floor')

	def place_doors(self):
		for y in range(1, self.map_height - 1):
			for x in range(1, self.map_width - 1):
				if (self.tiles[x + 1][y].name == 'floor' and self.tiles[x - 1][y].name == 'floor' and self.tiles[x][y - 1].name == 'wall' and self.tiles[x][y + 1].name == 'wall') or (self.tiles[x + 1][y].name == 'wall' and self.tiles[x - 1][y].name == 'wall' and self.tiles[x][y - 1].name == 'floor' and self.tiles[x][y + 1].name == 'floor'):
					if libtcod.random_get_int(game.rnd, 1, 50) == 50:
						self.tiles[x][y] = game.tiles.get_tile('door')

	def place_monsters(self):
		x, y = 0, 0
		#choose random spot for this monster
		while (self.is_blocked(x, y)):
			x = libtcod.random_get_int(game.rnd, 0, self.map_width - 1)
			y = libtcod.random_get_int(game.rnd, 0, self.map_height - 1)

		#only place it if the tile is not blocked
		dice = libtcod.random_get_int(game.rnd, 1, 100)
		if dice <= 60:
			d = game.monsters.get_monster_by_level(1)
		elif dice <= 90:
			d = game.monsters.get_monster_by_level(2)
		else:
			d = game.monsters.get_monster_by_level(3)
		monster = Object(x, y, d.icon, d.name, d.color, blocks=True, entity=d)
		self.objects.insert(1, monster)

	def place_objects(self):
		#choose random number of monsters
		num_monsters = libtcod.random_get_int(game.rnd, self.max_monsters / 5, self.max_monsters)
		for i in range(num_monsters):
			self.place_monsters()

		#choose random number of items
		num_items = libtcod.random_get_int(game.rnd, self.max_items / 5, self.max_items)
		if self.type in ['Sea', 'Ocean']:
			num_items = 0
		for i in range(num_items):
			#choose random spot for this item
			x, y = 0, 0
			while (self.is_blocked(x, y)):
				x = libtcod.random_get_int(game.rnd, 0, self.map_width - 1)
				y = libtcod.random_get_int(game.rnd, 0, self.map_height - 1)

			#only place it if the tile is not blocked
			dice = libtcod.random_get_int(game.rnd, 1, 100)
			if dice <= 10:
				d = game.items.get_item("gold")
			elif dice <= 60:
				d = game.items.get_item_by_level(1)
			elif dice <= 90:
				d = game.items.get_item_by_level(2)
			else:
				d = game.items.get_item_by_level(3)
			item = Object(x, y, d.icon, d.name, d.color, True, item=d)
			self.objects.append(item)

	def place_stairs(self, rooms):
		#place stairs going up based on character position
		if self.location_level > 1:
			self.tiles[game.char.x][game.char.y] = game.tiles.get_tile('stairs going up')
			self.up_staircase = (game.char.x, game.char.y)
		else:
			stairs = libtcod.random_get_int(game.rnd, 1, len(rooms) - 1)
			(x, y) = rooms[stairs].center()
			self.tiles[x][y] = game.tiles.get_tile('stairs going up')
			self.up_staircase = (x, y)
			game.char.x = x
			game.char.y = y

		#place stairs going down in a random spot
		stairs = libtcod.random_get_int(game.rnd, 1, len(rooms) - 1)
		(x, y) = rooms[stairs].center()
		self.tiles[x][y] = game.tiles.get_tile('stairs going down')
		self.down_staircase = (x, y)

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

			#"Rect" class makes rectangles easier to work with
			new_room = Rect(x, y, w, h)

			#run through the other rooms and see if they intersect with this one
			failed = False
			for other_room in rooms:
				if new_room.intersect(other_room):
					failed = True
					break

			if not failed:
				#this means there are no intersections, so this room is valid
				#"paint" it to the map's tiles
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

	def create_outdoor_map(self, default_tile):
		trees_tiles = 0
		rocks_tiles = 1
		shallow_water_tiles = 2
		deep_water_tiles = 3
		dirt_tiles = 4
		grass_tiles = 5
		grass2_tiles = 6
		tall_grass_tiles = 7
		sand_tiles = 8
		tiles = [0] * 9
		icons = ['tree', 'rock', 'shallow water', 'deep water', 'dirt', 'grass', 'grass2', 'tall grass', 'sand']

		# assign values per terrain types
		heightmap = game.worldmap.hm_list[self.location_level]
		if self.type in ['Forest', 'Hills', 'Mountains', 'Mountain Peak']:
			tiles[trees_tiles] = min(int((self.map_width * self.map_height) * 0.20), libtcod.random_get_int(game.rnd, int((self.map_width * self.map_height) * heightmap * 0.05), int((self.map_width * self.map_height) * heightmap)))
			tiles[rocks_tiles] = libtcod.random_get_int(game.rnd, 15, int((self.map_width * self.map_height) * 0.02))
			tiles[shallow_water_tiles] = libtcod.random_get_int(game.rnd, 15, 100)
			tiles[dirt_tiles] = libtcod.random_get_int(game.rnd, 15, 100)
			tiles[grass2_tiles] = min(int((self.map_width * self.map_height) * 0.15), libtcod.random_get_int(game.rnd, int((self.map_width * self.map_height) * heightmap * 0.05), int((self.map_width * self.map_height) * heightmap)))
			tiles[tall_grass_tiles] = min(int((self.map_width * self.map_height) * 0.15), libtcod.random_get_int(game.rnd, int((self.map_width * self.map_height) * heightmap * 0.05), int((self.map_width * self.map_height) * heightmap)))
		if self.type == 'Plains':
			tiles[trees_tiles] = libtcod.random_get_int(game.rnd, int((self.map_width * self.map_height) * heightmap * 0.05), int((self.map_width * self.map_height) * heightmap))
			tiles[rocks_tiles] = libtcod.random_get_int(game.rnd, 15, int((self.map_width * self.map_height) * 0.02))
			tiles[shallow_water_tiles] = libtcod.random_get_int(game.rnd, 30, 200)
			tiles[dirt_tiles] = libtcod.random_get_int(game.rnd, 30, 200)
			tiles[grass2_tiles] = libtcod.random_get_int(game.rnd, int((self.map_width * self.map_height) * heightmap * 0.05), int((self.map_width * self.map_height) * heightmap))
			tiles[tall_grass_tiles] = libtcod.random_get_int(game.rnd, int((self.map_width * self.map_height) * heightmap * 0.05), int((self.map_width * self.map_height) * heightmap))
			tiles[sand_tiles] = libtcod.random_get_int(game.rnd, int((self.map_width * self.map_height) * heightmap * 0.05), int((self.map_width * self.map_height) * heightmap))
		if self.type == 'Coast':
			tiles[rocks_tiles] = libtcod.random_get_int(game.rnd, 30, 200)
			tiles[shallow_water_tiles] = min(int((self.map_width * self.map_height) * 0.20), libtcod.random_get_int(game.rnd, int((self.map_width * self.map_height) * heightmap * 0.05), int((self.map_width * self.map_height) * heightmap)))
			tiles[dirt_tiles] = libtcod.random_get_int(game.rnd, 30, 200)
			tiles[grass2_tiles] = min(int((self.map_width * self.map_height) * 0.10), libtcod.random_get_int(game.rnd, int((self.map_width * self.map_height) * heightmap * 0.05), int((self.map_width * self.map_height) * heightmap)))
			tiles[tall_grass_tiles] = min(int((self.map_width * self.map_height) * 0.10), libtcod.random_get_int(game.rnd, int((self.map_width * self.map_height) * heightmap * 0.05), int((self.map_width * self.map_height) * heightmap)))
			tiles[grass_tiles] = min(int((self.map_width * self.map_height) * 0.15), libtcod.random_get_int(game.rnd, int((self.map_width * self.map_height) * heightmap * 0.05), int((self.map_width * self.map_height) * heightmap)))
		if self.type == 'Shore':
			tiles[rocks_tiles] = libtcod.random_get_int(game.rnd, 15, 100)
			tiles[deep_water_tiles] = min(int((self.map_width * self.map_height) * 0.20), libtcod.random_get_int(game.rnd, int((self.map_width * self.map_height) * heightmap * 0.05), int((self.map_width * self.map_height) * heightmap)))
			tiles[sand_tiles] = min(int((self.map_width * self.map_height) * 0.20), libtcod.random_get_int(game.rnd, int((self.map_width * self.map_height) * heightmap * 0.05), int((self.map_width * self.map_height) * heightmap)))
		if self.type == 'Sea':
			tiles[shallow_water_tiles] = min(int((self.map_width * self.map_height) * 0.20), libtcod.random_get_int(game.rnd, int((self.map_width * self.map_height) * heightmap * 0.05), int((self.map_width * self.map_height) * heightmap)))

		# place tiles on map
		for j in range(len(tiles)):
			for i in range(tiles[j]):
				x = libtcod.random_get_int(game.rnd, 0, self.map_width - 1)
				y = libtcod.random_get_int(game.rnd, 0, self.map_height - 1)
				while (self.tiles[x][y].name != default_tile):
					x = libtcod.random_get_int(game.rnd, 0, self.map_width - 1)
					y = libtcod.random_get_int(game.rnd, 0, self.map_height - 1)
				self.tiles[x][y] = game.tiles.get_tile(icons[j])

		# place dungeons on map
		for (id, name, abbr, x, y) in game.worldmap.dungeons:
			if (y * game.WORLDMAP_WIDTH) + x == self.location_level:
				dx = libtcod.random_get_int(game.rnd, 0, self.map_width - 9)
				dy = libtcod.random_get_int(game.rnd, 0, self.map_height - 9)
				room = Rect(dx, dy, 8, 8)
				self.create_room(room)
				for i in range(dx, dx + 7):
					self.tiles[i + 1][dy + 1] = game.tiles.get_tile('wall')
					self.tiles[i + 1][dy + 7] = game.tiles.get_tile('wall')
				for i in range(dy, dy + 7):
					self.tiles[dx + 1][i + 1] = game.tiles.get_tile('wall')
					self.tiles[dx + 7][i + 1] = game.tiles.get_tile('wall')
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
				self.tiles[doorx][doory] = game.tiles.get_tile('opened door')
				(stairs_x, stairs_y) = room.center()
				self.tiles[stairs_x][stairs_y] = game.tiles.get_tile('stairs going down')
				self.down_staircase = (stairs_x, stairs_y)

	def generate(self, empty=False):
		default_block_tiles = {'Dungeon': 'wall', 'Mountain Peak': 'dirt', 'Mountains': 'dirt', 'Hills': 'dirt', 'Forest': 'grass', 'Plains': 'grass', 'Coast': 'sand', 'Shore': 'shallow water', 'Sea': 'deep water', 'Ocean': 'very deep water'}
		self.objects = [game.char]
		self.tiles = [[game.tiles.get_tile(default_block_tiles[self.type]) for y in range(self.map_height)] for x in range(self.map_width)]
		self.explored = [[False for y in range(self.map_height)] for x in range(self.map_width)]
		game.fov_noise = libtcod.noise_new(1, 1.0, 1.0)
		game.fov_torchx = 0.0

		if not empty:
			if self.type == 'Dungeon':
				rooms = self.create_dungeon()
				self.place_doors()
				self.place_objects()
				self.place_stairs(rooms)
			elif self.type != 'Ocean':
				self.create_outdoor_map(default_block_tiles[self.type])
				self.place_objects()


class Tile(object):
	#a tile of the map and its properties
	def __init__(self, icon, name, color, dark_color, back_color, blocked, block_sight=None, article=None, flags=None, typ=None):
		self.blocked = blocked
		self.icon = icon
		self.name = name
		self.color = libtcod.Color(color[0], color[1], color[2])
		self.dark_color = libtcod.Color(dark_color[0], dark_color[1], dark_color[2])
		self.back_color = libtcod.Color(back_color[0], back_color[1], back_color[2])
		self.article = article
		self.flags = flags
		self.type = typ

		#by default, if a tile is blocked, it also blocks sight
		if block_sight is None:
			block_sight = blocked
		self.block_sight = block_sight


class TileList(object):
	def __init__(self):
		self.list = []

	# setup the items structure and run parser
	def init_parser(self):
		parser = libtcod.parser_new()
		tile_type_struct = libtcod.parser_new_struct(parser, 'tile_type')
		libtcod.struct_add_property(tile_type_struct, 'type', libtcod.TYPE_STRING, True)
		libtcod.struct_add_property(tile_type_struct, 'icon', libtcod.TYPE_STRING, True)
		libtcod.struct_add_property(tile_type_struct, 'icon_color', libtcod.TYPE_COLOR, True)
		libtcod.struct_add_property(tile_type_struct, 'dark_color', libtcod.TYPE_COLOR, False)
		libtcod.struct_add_property(tile_type_struct, 'back_color', libtcod.TYPE_COLOR, False)
		libtcod.struct_add_property(tile_type_struct, 'article', libtcod.TYPE_STRING, True)
		libtcod.struct_add_flag(tile_type_struct, 'blocked')
		libtcod.struct_add_flag(tile_type_struct, 'block_sight')
		libtcod.parser_run(parser, "data/tiles.txt", TileListener())

	def add_to_list(self, tile=None):
		if not tile == None:
			if 'blocked' in tile.flags:
				tile.blocked = True
			if 'block_sight' in tile.flags:
				tile.block_sight = True
			self.list.append(tile)

	def get_tile(self, name):
		for tile in self.list:
			if name in tile.name:
				return tile
		return None


class TileListener(object):
	def new_struct(self, struct, name):
		self.temp_tile = Tile('', '', [0, 0, 0], [0, 0, 0], [0, 0, 0], False, False, '', [], '')
		self.temp_tile.name = name
		return True

	def new_flag(self, name):
		self.temp_tile.flags.append(name)
		return True

	def new_property(self, name, typ, value):
		if name == 'icon_color':
			self.temp_tile.color.r = value.r
			self.temp_tile.color.g = value.g
			self.temp_tile.color.b = value.b
		elif name == 'dark_color':
			self.temp_tile.dark_color.r = value.r
			self.temp_tile.dark_color.g = value.g
			self.temp_tile.dark_color.b = value.b
		elif name == 'back_color':
			self.temp_tile.back_color.r = value.r
			self.temp_tile.back_color.g = value.g
			self.temp_tile.back_color.b = value.b
		else:
			if name == "type":
				self.temp_tile.type = value
			if name == "icon":
				self.temp_tile.icon = value
			if name == "article":
				self.temp_tile.article = value
		return True

	def end_struct(self, struct, name):
		self.temp_tile.dark_color = libtcod.color_lerp(libtcod.black, self.temp_tile.color, 0.3)
		game.tiles.add_to_list(self.temp_tile)
		return True

	def error(self, msg):
		print 'error : ', msg
		return True


class Rect(object):
	#a rectangle on the map. used to characterize a room.
	def __init__(self, x, y, w, h):
		self.x1 = x
		self.y1 = y
		self.x2 = x + w
		self.y2 = y + h

	def center(self):
		center_x = (self.x1 + self.x2) / 2
		center_y = (self.y1 + self.y2) / 2
		return (center_x, center_y)

	def intersect(self, other):
		#returns true if this rectangle intersects with another one
		return (self.x1 <= other.x2 and self.x2 >= other.x1 and
				self.y1 <= other.y2 and self.y2 >= other.y1)


class Object(object):
	#this is a generic object: the player, a monster, an item, the stairs...
	#it's always represented by a character on screen.
	def __init__(self, x, y, char, name, color, pickup=False, blocks=False, entity=None, ai=None, item=None):
		self.x = x
		self.y = y
		self.char = char
		self.name = name
		self.color = color
		self.can_be_pickup = pickup
		self.first_appearance = game.player.turns
		self.blocks = blocks
		self.entity = entity
		if self.entity:  # let the fighter component know who owns it
			self.entity.owner = self

		self.ai = ai
		if self.ai:  # let the AI component know who owns it
			self.ai.owner = self

		self.item = item
		if self.item:  # let the Item component know who owns it
			self.item.owner = self

	def move(self, dx, dy, map):
		#move by the given amount, if the destination is not blocked
		if not map.is_blocked(self.x + dx, self.y + dy):
			self.x += dx
			self.y += dy
			game.path_recalculate = True
			game.player.add_turn()
		elif map.tiles[self.x + dx][self.y + dy].type == 'wall':
			game.message.new('The wall laughs at your attempt to pass through it.', game.player.turns)

	def move_towards(self, target_x, target_y):
		#vector from this object to the target, and distance
		dx = target_x - self.x
		dy = target_y - self.y
		distance = math.sqrt(dx ** 2 + dy ** 2)

		#normalize it to length 1 (preserving direction), then round it and
		#convert to integer so the movement is restricted to the map grid
		dx = int(round(dx / distance))
		dy = int(round(dy / distance))
		self.move(dx, dy)

	def distance_to(self, other):
		#return the distance to another object
		dx = other.x - self.x
		dy = other.y - self.y
		return math.sqrt(dx ** 2 + dy ** 2)

	def distance(self, x, y):
		#return the distance to some coordinates
		return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

	def send_to_back(self):
		#make this object be drawn first, so all others appear above it if they're in the same tile.
		game.current_map.objects.remove(self)
		game.current_map.objects.insert(0, self)

	def delete(self):
		game.current_map.objects.remove(self)

	def draw(self, con):
		#only show if it's visible to the player
		if libtcod.map_is_in_fov(game.fov_map, self.x, self.y):
			#set the color and then draw the character that represents this object at its position
			libtcod.console_set_default_foreground(con, self.color)
			libtcod.console_put_char(con, self.x - game.curx, self.y - game.cury, self.char, libtcod.BKGND_NONE)
		elif game.current_map.explored[self.x][self.y] and self.can_be_pickup:
			libtcod.console_set_default_foreground(con, self.item.dark_color)
			libtcod.console_put_char(con, self.x - game.curx, self.y - game.cury, self.char, libtcod.BKGND_NONE)

	def clear(self, con):
		#erase the character that represents this object
		libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)

	def coordinates(self):
		return self.x, self.y
