import libtcodpy as libtcod
import math
import game
import util
import item
import map


class Monster(object):
	def __init__(self, typ, name, unid_name, icon, color, dark_color, level, health, damage, article, ar, dr, xp, corpse, flags):
		self.type = typ
		self.name = name
		self.unidentified_name = unid_name
		self.icon = icon
		self.color = libtcod.Color(color[0], color[1], color[2])
		self.dark_color = libtcod.Color(dark_color[0], dark_color[1], dark_color[2])
		self.level = level
		self.health = health
		self.damage = damage
		self.article = article
		self.attack_rating = ar
		self.defense_rating = dr
		self.xp = xp
		self.corpse = corpse
		self.flags = flags

	def is_hostile(self):
		if "ai_hostile" in self.flags:
			return True
		return False

	def becomes_hostile(self):
		self.flags.append("ai_hostile")
		self.flags[:] = (value for value in self.flags if value != "ai_neutral" and value != "ai_friendly")

	def loot(self, x, y):
		#see if monster drops an item or a corpse when dying
		corpse = libtcod.random_get_int(game.rnd, 1, 100)
		if corpse <= self.corpse:
			if "corpse_goblin" in self.flags:
				d = game.items.get_item("goblin corpse")
			elif "corpse_kobold" in self.flags:
				d = game.items.get_item("kobold corpse")
			elif "corpse_rat" in self.flags:
				d = game.items.get_item("rat corpse")
			elif "corpse_lizard" in self.flags:
				d = game.items.get_item("lizard corpse")
			elif "corpse_bat" in self.flags:
				d = game.items.get_item("bat corpse")
			elif "corpse_dog" in self.flags:
				d = game.items.get_item("dog corpse")
			elif "corpse_orc" in self.flags:
				d = game.items.get_item("orc corpse")
			drop = map.Object(x, y, d.icon, d.name, d.color, True, item=d)
			game.current_map.objects.append(drop)
		drop_chance = libtcod.random_get_int(game.rnd, 1, 100)
		if drop_chance >= 80:
			dice = libtcod.random_get_int(game.rnd, 1, 100)
			if dice <= 60:
				d = game.items.get_item_by_level(1)
			elif dice <= 90:
				d = game.items.get_item_by_level(2)
			else:
				d = game.items.get_item_by_level(3)
			drop = map.Object(x, y, d.icon, d.name, d.color, True, item=d)
			game.current_map.objects.append(drop)

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
			dx, dy = libtcod.random_get_int(game.rnd, -1, 1), libtcod.random_get_int(game.rnd, -1, 1)
		return dx, dy

	def take_turn(self, x, y):
		if self.is_hostile() and libtcod.map_is_in_fov(game.fov_map, x, y):
			#move towards player if far away
			dx, dy = 0, 0
			if self.distance_to_player(game.char, x, y) >= 2:
				dx, dy = self.move_towards_player(game.char, x, y)
			else:
				self.attack()
		else:
			dx, dy = libtcod.random_get_int(game.rnd, -1, 1), libtcod.random_get_int(game.rnd, -1, 1)
			if all(i == "ai_neutral" and i != "ai_hostile" for i in self.flags):
				if self.distance_to_player(game.char, x, y) <= 2:
					turn_hostile = libtcod.random_get_int(game.rnd, 1, 100)
					if turn_hostile <= 10:
						self.flags.append("ai_hostile")
			#elif set(['ai_neutral', 'ai_hostile']).issubset(self.flags):
			elif all(i in self.flags for i in ["ai_neutral", "ai_hostile"]):
				return_neutral = libtcod.random_get_int(game.rnd, 1, 100)
				if return_neutral <= 10:
					self.flags[:] = (value for value in self.flags if value != "ai_hostile")
			#retry if destination is blocked
			while (game.current_map.is_blocked(x + dx, y + dy)):
				if dx == 0 and dy == 0:
					break
				dx, dy = libtcod.random_get_int(game.rnd, -1, 1), libtcod.random_get_int(game.rnd, -1, 1)
		return x + dx, y + dy

	def attack(self):
		attacker = util.roll_dice(1, 50, 1, 0)
		defender = util.roll_dice(1, 50, 1, 0)
		if attacker != 1 and defender != 50 and ((attacker + self.attack_rating) >= (defender + game.player.defense_rating()) or attacker == 50 or defender == 1):
			damage = self.damage.roll_dice()
			game.message.new('The ' + self.name + ' hits you for ' + str(damage) + ' pts of damage', game.player.turns, libtcod.light_red)
			game.player.health -= damage
			game.hp_anim.append([game.char, str(-damage), libtcod.red, 0])
			if game.player.health < 1:
				game.message.new('You die...', game.player.turns, libtcod.light_orange)
				game.message.new('*** Press space ***', game.player.turns)
				game.killer = self.article + self.name
				game.game_state = "death"
		else:
			game.message.new('The ' + self.name + ' attack but misses.', game.player.turns)


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
		libtcod.struct_add_property(monster_type_struct, 'level', libtcod.TYPE_INT, True)
		libtcod.struct_add_property(monster_type_struct, 'health', libtcod.TYPE_INT, True)
		libtcod.struct_add_property(monster_type_struct, 'attack_rating', libtcod.TYPE_INT, True)
		libtcod.struct_add_property(monster_type_struct, 'defense_rating', libtcod.TYPE_INT, True)
		libtcod.struct_add_property(monster_type_struct, 'damage', libtcod.TYPE_DICE, True)
		libtcod.struct_add_property(monster_type_struct, 'article', libtcod.TYPE_STRING, True)
		libtcod.struct_add_property(monster_type_struct, 'xp', libtcod.TYPE_INT, True)
		libtcod.struct_add_property(monster_type_struct, 'corpse', libtcod.TYPE_INT, False)
		libtcod.struct_add_flag(monster_type_struct, 'ai_friendly')
		libtcod.struct_add_flag(monster_type_struct, 'ai_neutral')
		libtcod.struct_add_flag(monster_type_struct, 'ai_hostile')
		libtcod.struct_add_flag(monster_type_struct, 'flying')
		libtcod.struct_add_flag(monster_type_struct, 'corpse_goblin')
		libtcod.struct_add_flag(monster_type_struct, 'corpse_kobold')
		libtcod.struct_add_flag(monster_type_struct, 'corpse_orc')
		libtcod.struct_add_flag(monster_type_struct, 'corpse_rat')
		libtcod.struct_add_flag(monster_type_struct, 'corpse_bat')
		libtcod.struct_add_flag(monster_type_struct, 'corpse_dog')
		libtcod.struct_add_flag(monster_type_struct, 'corpse_lizard')
		libtcod.parser_run(parser, "data/monsters.txt", MonsterListener())

	def add_to_list(self, monster=None):
		if not monster == None:
			self.list.append(monster)

	def get_monster(self, name):
		for monster in self.list:
			if name in monster.name:
				return monster
		return None

	def get_monster_by_level(self, level):
		mst = libtcod.random_get_int(game.rnd, 0, len(self.list) - 1)
		while self.list[mst].level > level:
			mst = libtcod.random_get_int(game.rnd, 0, len(self.list) - 1)
		return self.list[mst]

	def number_of_monsters_on_map(self):
		number = 0
		for obj in game.current_map.objects:
			if obj.entity != None:
				number += 1
		return number

	def spawn(self):
		if self.number_of_monsters_on_map() < game.MAX_MONSTERS_PER_LEVEL:
			number = libtcod.random_get_int(game.rnd, 1, 100)
			if number == 1:
				game.current_map.place_monsters()


class MonsterListener(object):
	def new_struct(self, struct, name):
		self.temp_monster = Monster('', '', '', '', [0, 0, 0], [0, 0, 0], 0, 0, item.Dice(0, 0, 0, 0), '', 0, 0, 0, 0, [])
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
		elif name == 'damage':
			self.temp_monster.damage.nb_dices = value.nb_dices
			self.temp_monster.damage.nb_faces = value.nb_faces
			self.temp_monster.damage.multiplier = value.multiplier
			self.temp_monster.damage.bonus = value.addsub
		else:
			if name == "type":
				self.temp_monster.type = value
			if name == "icon":
				self.temp_monster.icon = value
			if name == "level":
				self.temp_monster.level = value
			if name == "health":
				self.temp_monster.health = value
			if name == "attack_rating":
				self.temp_monster.attack_rating = value
			if name == "defense_rating":
				self.temp_monster.defense_rating = value
			if name == "xp":
				self.temp_monster.xp = value
			if name == "corpse":
				self.temp_monster.corpse = value
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
