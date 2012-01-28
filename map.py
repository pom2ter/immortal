import libtcodpy as libtcod
import math
import game


class Map(object):
	def __init__(self, location, level):
		self.location = location
		self.level = level
		self.tiles = None
		self.objects = None
		self.generate_map()

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
				self.tiles[x][y].icon = '.'
				self.tiles[x][y].name = 'floor'
				self.tiles[x][y].color = libtcod.light_gray
				self.tiles[x][y].dark_color = libtcod.dark_gray
				self.tiles[x][y].blocked = False
				self.tiles[x][y].block_sight = False

	def create_h_tunnel(self, x1, x2, y):
		#horizontal tunnel. min() and max() are used in case x1>x2
		for x in range(min(x1, x2), max(x1, x2) + 1):
			self.tiles[x][y].icon = '.'
			self.tiles[x][y].name = 'floor'
			self.tiles[x][y].color = libtcod.light_gray
			self.tiles[x][y].dark_color = libtcod.dark_gray
			self.tiles[x][y].blocked = False
			self.tiles[x][y].block_sight = False

	def create_v_tunnel(self, y1, y2, x):
		#vertical tunnel
		for y in range(min(y1, y2), max(y1, y2) + 1):
			self.tiles[x][y].icon = '.'
			self.tiles[x][y].name = 'floor'
			self.tiles[x][y].color = libtcod.light_gray
			self.tiles[x][y].dark_color = libtcod.dark_gray
			self.tiles[x][y].blocked = False
			self.tiles[x][y].block_sight = False

	def place_door(self):
		for y in range(1, game.MAP_HEIGHT - 1):
			for x in range(1, game.MAP_WIDTH - 1):
				if (self.tiles[x + 1][y].name == 'floor' and self.tiles[x - 1][y].name == 'floor' and self.tiles[x][y - 1].name == 'wall' and self.tiles[x][y + 1].name == 'wall') or (self.tiles[x + 1][y].name == 'wall' and self.tiles[x - 1][y].name == 'wall' and self.tiles[x][y - 1].name == 'floor' and self.tiles[x][y + 1].name == 'floor'):
					if libtcod.random_get_int(0, 1, 50) == 50:
						self.tiles[x][y].icon = '+'
						self.tiles[x][y].name = 'door'
						self.tiles[x][y].color = libtcod.dark_orange
						self.tiles[x][y].dark_color = libtcod.darkest_orange
						self.tiles[x][y].blocked = True
						self.tiles[x][y].block_sight = True

	def generate_map(self):
		#the list of objects with just the player
		self.objects = [game.char]

		#fill map with "blocked" tiles
		self.tiles = [[Tile('#', 'wall', libtcod.light_gray, libtcod.dark_gray, True)
			for y in range(game.MAP_HEIGHT)]
				for x in range(game.MAP_WIDTH)]

		rooms = []
		num_rooms = 0
		game.fov_noise = libtcod.noise_new(1, 1.0, 1.0)
		game.fov_torchx = 0.0

		for r in range(game.MAX_ROOMS):
			#random width and height
			w = libtcod.random_get_int(0, game.ROOM_MIN_SIZE, game.ROOM_MAX_SIZE)
			h = libtcod.random_get_int(0, game.ROOM_MIN_SIZE, game.ROOM_MAX_SIZE)
			#random position without going out of the boundaries of the map
			x = libtcod.random_get_int(0, 0, game.MAP_WIDTH - w - 1)
			y = libtcod.random_get_int(0, 0, game.MAP_HEIGHT - h - 1)

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

				#add some contents to this room, such as monsters
	#			self.place_objects(new_room)

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
					if libtcod.random_get_int(0, 0, 1) == 1:
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

		self.place_door()


class Tile(object):
	#a tile of the map and its properties
	def __init__(self, icon, name, color, dark_color, blocked, block_sight=None):
		self.blocked = blocked
		self.icon = icon
		self.name = name
		self.color = color
		self.dark_color = dark_color

		#all tiles start unexplored
		self.explored = False

		#by default, if a tile is blocked, it also blocks sight
		if block_sight is None:
			block_sight = blocked
		self.block_sight = block_sight


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
	def __init__(self, x, y, char, name, color, blocks=False, fighter=None, ai=None, item=None):
		self.x = x
		self.y = y
		self.char = char
		self.name = name
		self.color = color
		self.blocks = blocks
		self.fighter = fighter
		if self.fighter:  # let the fighter component know who owns it
			self.fighter.owner = self

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
			game.player.turns += 1
		elif map.tiles[self.x + dx][self.y + dy].name == 'door':
			game.message.new('You bump into a door!', game.player.turns)
		elif map.tiles[self.x + dx][self.y + dy].name == 'wall':
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

	def draw(self, con):
		#only show if it's visible to the player
		if libtcod.map_is_in_fov(game.fov_map, self.x, self.y):
			#set the color and then draw the character that represents this object at its position
			libtcod.console_set_default_foreground(con, self.color)
			libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)

	def clear(self, con):
		#erase the character that represents this object
		libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)
