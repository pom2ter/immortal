import libtcodpy as libtcod
import math
import game
import item


class Monster(object):
	def __init__(self, typ, name, unid_name, icon, color, dark_color, health, damage, article, strength, xp, flags):
		self.type = typ
		self.name = name
		self.unidentified_name = unid_name
		self.icon = icon
		self.color = libtcod.Color(color[0], color[1], color[2])
		self.dark_color = libtcod.Color(dark_color[0], dark_color[1], dark_color[2])
		self.health = health
		self.damage = damage
		self.article = article
		self.strength = strength
		self.xp = xp
		self.flags = flags

	def is_hostile(self):
		if "ai_hostile" in self.flags:
			return True
		return False

	def distance_to_player(self, player, x, y):
		#return the distance relative to the player
		dx = player.x - x
		dy = player.y - y
		return math.sqrt(dx ** 2 + dy ** 2)

	def move_towards_player(self, player, x, y):
		#vector from this object to the target, and distance
		dx = player.x - x
		dy = player.y - y
		distance = math.sqrt(dx ** 2 + dy ** 2)

		#normalize it to length 1 (preserving direction), then round it and convert to integer so the movement is restricted to the map grid
		dx = int(round(dx / distance))
		dy = int(round(dy / distance))
		while (game.current_map.is_blocked(x + dx, y + dy)):
			if dx == 0 and dy == 0:
				break
			dx, dy = libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1)
		return dx, dy

	def take_turn(self, x, y):
		if self.is_hostile() and libtcod.map_is_in_fov(game.fov_map, x, y):
			#move towards player if far away
			dx, dy = 0, 0
			if self.distance_to_player(game.char, x, y) >= 2:
				dx, dy = self.move_towards_player(game.char, x, y)
		else:
			dx, dy = libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1)
			if all(i == "ai_neutral" and i != "ai_hostile" for i in self.flags):
				if self.distance_to_player(game.char, x, y) <= 2:
					turn_hostile = libtcod.random_get_int(0, 0, 100)
					if turn_hostile < 10:
						self.flags.append("ai_hostile")
			#elif set(['ai_neutral', 'ai_hostile']).issubset(self.flags):
			elif all(i in self.flags for i in ["ai_neutral", "ai_hostile"]):
				print self.flags
				return_neutral = libtcod.random_get_int(0, 0, 100)
				if return_neutral < 10:
					self.flags[:] = (value for value in self.flags if value != "ai_hostile")
			#retry if destination is blocked
			while (game.current_map.is_blocked(x + dx, y + dy)):
				if dx == 0 and dy == 0:
					break
				dx, dy = libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1)
		return x + dx, y + dy


class MonsterList(object):
	def __init__(self):
		self.list = []

	# setup the items structure and run parser
	def init_parser(self):
		parser = libtcod.parser_new()
		monster_type_struct = libtcod.parser_new_struct(parser, 'monster_type')
		libtcod.struct_add_property(monster_type_struct, 'type', libtcod.TYPE_STRING, True)
		libtcod.struct_add_property(monster_type_struct, 'unidentified_name', libtcod.TYPE_STRING, True)
		libtcod.struct_add_property(monster_type_struct, 'icon', libtcod.TYPE_STRING, True)
		libtcod.struct_add_property(monster_type_struct, 'icon_color', libtcod.TYPE_COLOR, True)
		libtcod.struct_add_property(monster_type_struct, 'dark_color', libtcod.TYPE_COLOR, True)
		libtcod.struct_add_property(monster_type_struct, 'health', libtcod.TYPE_INT, False)
		libtcod.struct_add_property(monster_type_struct, 'strength', libtcod.TYPE_INT, False)
		libtcod.struct_add_property(monster_type_struct, 'damage', libtcod.TYPE_DICE, False)
		libtcod.struct_add_property(monster_type_struct, 'article', libtcod.TYPE_STRING, True)
		libtcod.struct_add_property(monster_type_struct, 'xp', libtcod.TYPE_INT, True)
		libtcod.struct_add_flag(monster_type_struct, 'ai_friendly')
		libtcod.struct_add_flag(monster_type_struct, 'ai_neutral')
		libtcod.struct_add_flag(monster_type_struct, 'ai_hostile')
		libtcod.parser_run(parser, "data/monsters.txt", MonsterListener())

	def add_to_list(self, monster=None):
		if not monster == None:
			self.list.append(monster)

	def getmonster(self, name):
		for monster in self.list:
			if name in monster.name:
				return monster
		return None

	def number_of_monsters_on_map(self):
		number = 0
		for obj in game.current_map.objects:
			if obj.entity != None:
				number += 1
		return number

	def spawn(self):
		if self.number_of_monsters_on_map() < game.MAX_MONSTERS_PER_LEVEL:
			number = libtcod.random_get_int(0, 0, 100)
			if number == 1:
				game.current_map.place_monsters()


class MonsterListener(object):
	def new_struct(self, struct, name):
		self.temp_monster = Monster('', '', '', '', [0, 0, 0], [0, 0, 0], 0, item.Dice(0, 0, 0, 0), '', 0, 0, [])
		self.temp_monster.name = name
		return True

	def new_flag(self, name):
		self.temp_monster.flags.append(name)
		return True

	def new_property(self, name, typ, value):
		if name == 'icon_color':
			self.temp_monster.color.r = value.r
			self.temp_monster.color.g = value.g
			self.temp_monster.color.b = value.b
		elif name == 'dark_color':
			self.temp_monster.dark_color.r = value.r
			self.temp_monster.dark_color.g = value.g
			self.temp_monster.dark_color.b = value.b
		elif name == 'dices':
			self.temp_monster.damage.nb_dices = value.nb_dices
			self.temp_monster.damage.nb_faces = value.nb_faces
			self.temp_monster.damage.multiplier = value.multiplier
			self.temp_monster.damage.bonus = value.addsub
		else:
			if name == "type":
				self.temp_monster.type = value
			if name == "icon":
				self.temp_monster.icon = value
			if name == "health":
				self.temp_monster.health = value
			if name == "strength":
				self.temp_monster.strength = value
			if name == "xp":
				self.temp_monster.xp = value
			if name == "article":
				self.temp_monster.article = value
			if name == "unidentified_name":
				self.temp_monster.unidentified_name = value
		return True

	def end_struct(self, struct, name):
		game.monsters.add_to_list(self.temp_monster)
		return True

	def error(self, msg):
		print 'error : ', msg
		return True
