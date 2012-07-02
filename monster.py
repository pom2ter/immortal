import libtcodpy as libtcod
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

	def take_turn(self, dx, dy):
		x, y = libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1)
		while (game.current_map.is_blocked(dx + x, dy + y)):
			if x == 0 and y == 0:
				break
			x, y = libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1)
		return dx + x, dy + y


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
