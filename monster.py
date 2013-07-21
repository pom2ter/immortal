import libtcodpy as libtcod
import math
import game
import util
import item
import map


class Monster(object):
	def __init__(self, typ, name, unid_name, icon, color, dark_color, level, health, damage, article, ar, dr, xp, weight, corpse, flags):
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
		self.weight = weight
		self.corpse = corpse
		self.flags = flags

	# monster attacks the enemy
	def attack(self):
		attacker = util.roll_dice(1, 50)
		defender = util.roll_dice(1, 50)
		if (attacker != 1 and defender != 50 and ((attacker + self.attack_rating) >= (defender + game.player.defense_rating()) or attacker == 50 or defender == 1)) or game.player.is_disabled():
			damage = self.damage.roll_dice()
			game.message.new(self.article.capitalize() + self.get_name() + ' hits you for ' + str(damage) + ' pts of damage', game.turns, libtcod.light_red)
			game.player.take_damage(damage, self.article + self.name)
		else:
			game.message.new(self.article.capitalize() + self.get_name() + ' attacks you but misses.', game.turns)

	# monster becomes hostile
	def becomes_hostile(self):
		self.flags.append('ai_hostile')
		self.flags[:] = (value for value in self.flags if value != 'ai_neutral' and value != 'ai_friendly')

	# returns true if monster can move
	def can_move(self, x, y):
		if 'stuck' in self.flags:
			return False
		if game.current_map.tile[x][y]['name'] in ['deep water', 'very deep water'] and 'land' in self.flags:
			return False
		if game.current_map.tile[x][y]['name'] not in ['deep water', 'very deep water'] and 'aquatic' in self.flags:
			return False
		return True

	# checks monster condition each turn
	def check_condition(self, x, y):
		if 'stuck' in self.flags:
			dice = util.roll_dice(1, 10)
			if dice == 10:
				self.flags.remove('stuck')
		if 'poison' in self.flags:
			dice = util.roll_dice(1, 5)
			if dice == 5:
				self.flags.remove('poison')
			else:
				self.take_damage(x, y, 1, 'poison')
		if 'sleep' in self.flags:
			dice = util.roll_dice(1, 5)
			if dice == 5:
				if libtcod.map_is_in_fov(game.fov_map, x, y):
					game.message.new('The ' + self.get_name() + 'woke up.', game.turns)
				self.flags.remove('sleep')

	# determines monster distance to player
	def distance_to_player(self, player, x, y):
		dx = player.x - x
		dy = player.y - y
		return math.sqrt(dx ** 2 + dy ** 2)

	# return monster's name base of identity level
	def get_name(self, article=False):
		string = ''
		if article:
			string = self.article
		if "identified" in self.flags:
			string += self.name
		else:
			string += self.unidentified_name + '(?)'
		return string

	# returns true if monster is not touching the ground
	def is_above_ground(self):
		if 'levitate' in self.flags:
			return True
		return False

	# returns true if monster is dead
	def is_dead(self):
		if self.health < 1:
			return True
		return False

	# returns true if monster is disabled
	def is_disabled(self):
		if any(i in self.flags for i in ['sleep', 'unconscious']) or self.is_dead():
			return True
		return False

	# returns true if monster is hostile
	def is_hostile(self):
		if 'ai_hostile' in self.flags:
			return True
		return False

	# return true if monster is identified
	def is_identified(self):
		if 'identified' in self.flags:
			return True
		return False

	# see if monster drops an item or a corpse when dying
	def loot(self, x, y):
		corpse = util.roll_dice(1, 100)
		if corpse <= self.corpse:
			d = game.baseitems.create_corpse(self.name, self.weight)
			drop = map.Object(x, y, d.icon, d.name, d.color, True, item=d)
			game.current_map.objects.append(drop)
		drop_chance = util.roll_dice(1, 100)
		if drop_chance >= 80:
			drop = game.baseitems.loot_generation(x, y, self.level)
			game.current_map.objects.append(drop)

	# monster move towards player
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

	# monster takes damage
	def take_damage(self, x, y, damage, source):
		self.health -= damage
		if libtcod.map_is_in_fov(game.fov_map, x, y):
			game.hp_anim.append([x, y, str(-damage), libtcod.light_yellow, 0])
		if source == 'player':
			if "sleep" in self.flags:
				if libtcod.map_is_in_fov(game.fov_map, x, y):
					game.message.new('The ' + self.get_name() + 'woke up.', game.turns)
				self.flags.remove('sleep')

	# monster takes its turn
	def take_turn(self, x, y):
		if libtcod.map_is_in_fov(game.fov_map, x, y) and self.is_hostile():
			#move towards player if far away
			dx, dy = 0, 0
			if self.distance_to_player(game.char, x, y) >= 2:
				dx, dy = self.move_towards_player(game.char, x, y)
				if not self.can_move(x + dx, y + dy):
					dx, dy = 0, 0
			else:
				self.attack()
		else:
			dx, dy = libtcod.random_get_int(game.rnd, -1, 1), libtcod.random_get_int(game.rnd, -1, 1)
			if x + dx < 0 or x + dx >= game.current_map.map_width:
				dx = 0
			if y + dy < 0 or y + dy >= game.current_map.map_height:
				dy = 0
			if not self.can_move(x + dx, y + dy):
				dx, dy = 0, 0
			if all(i == 'ai_neutral' and i != 'ai_hostile' for i in self.flags):
				if self.distance_to_player(game.char, x, y) <= 2:
					turn_hostile = util.roll_dice(1, 100)
					if turn_hostile <= 10:
						self.flags.append('ai_hostile')
			elif all(i in self.flags for i in ['ai_neutral', 'ai_hostile']):
				return_neutral = util.roll_dice(1, 100)
				if return_neutral <= 10:
					self.flags[:] = (value for value in self.flags if value != 'ai_hostile')
			#retry if destination is blocked
			while (game.current_map.is_blocked(x + dx, y + dy)):
				if dx == 0 and dy == 0:
					break
				dx, dy = libtcod.random_get_int(game.rnd, -1, 1), libtcod.random_get_int(game.rnd, -1, 1)
				if x + dx < 0 or x + dx >= game.current_map.map_width:
					dx = 0
				if y + dy < 0 or y + dy >= game.current_map.map_height:
					dy = 0
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
		libtcod.struct_add_property(monster_type_struct, 'icon_color2', libtcod.TYPE_COLOR, False)
		libtcod.struct_add_property(monster_type_struct, 'icon_color3', libtcod.TYPE_COLOR, False)
		libtcod.struct_add_property(monster_type_struct, 'icon_color4', libtcod.TYPE_COLOR, False)
		libtcod.struct_add_property(monster_type_struct, 'icon_color5', libtcod.TYPE_COLOR, False)
		libtcod.struct_add_property(monster_type_struct, 'dark_color', libtcod.TYPE_COLOR, True)
		libtcod.struct_add_property(monster_type_struct, 'level', libtcod.TYPE_INT, True)
		libtcod.struct_add_property(monster_type_struct, 'health', libtcod.TYPE_DICE, True)
		libtcod.struct_add_property(monster_type_struct, 'attack_rating', libtcod.TYPE_INT, True)
		libtcod.struct_add_property(monster_type_struct, 'defense_rating', libtcod.TYPE_INT, True)
		libtcod.struct_add_property(monster_type_struct, 'damage', libtcod.TYPE_DICE, True)
		libtcod.struct_add_property(monster_type_struct, 'article', libtcod.TYPE_STRING, True)
		libtcod.struct_add_property(monster_type_struct, 'xp', libtcod.TYPE_INT, True)
		libtcod.struct_add_property(monster_type_struct, 'weight', libtcod.TYPE_INT, False)
		libtcod.struct_add_property(monster_type_struct, 'corpse', libtcod.TYPE_INT, False)
		libtcod.struct_add_flag(monster_type_struct, 'ai_friendly')
		libtcod.struct_add_flag(monster_type_struct, 'ai_neutral')
		libtcod.struct_add_flag(monster_type_struct, 'ai_hostile')
		libtcod.struct_add_flag(monster_type_struct, 'identified')
		libtcod.struct_add_flag(monster_type_struct, 'land')
		libtcod.struct_add_flag(monster_type_struct, 'flying')
		libtcod.struct_add_flag(monster_type_struct, 'aquatic')
		libtcod.parser_run(parser, 'data/monsters.txt', MonsterListener())

	# add monster to the list
	def add_to_list(self, monster=None):
		if monster is not None:
			self.list.append(monster)

	# get a monster from the list
	def get_monster(self, name):
		for monster in self.list:
			if name == monster.name:
				return monster
		return None

	# choose a random monster based on its level
	def get_monster_by_level(self, level, tilename):
		if tilename in ['deep water', 'very deep water']:
			mob = [x for x in self.list if x.level <= level and 'land' not in x.flags]
		else:
			mob = [x for x in self.list if x.level <= level and 'aquatic' not in x.flags]
		if mob:
			return mob[libtcod.random_get_int(game.rnd, 0, len(mob) - 1)]
		return None

	# returns the number of monsters on the map
	def number_of_monsters_on_map(self):
		return sum(obj.entity is not None for obj in game.current_map.objects)

	# spawn a monster
	def spawn(self):
		if self.number_of_monsters_on_map() < game.current_map.max_monsters:
			number = util.roll_dice(1, 100)
			if number == 1:
				game.current_map.place_monsters()


class MonsterListener(object):
	def new_struct(self, struct, name):
		self.temp_monster = Monster('', '', '', '', [0, 0, 0], [0, 0, 0], 0, item.Dice(0, 0, 0, 0), item.Dice(0, 0, 0, 0), '', 0, 0, 0, 0, 0, [])
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
		elif name == 'health':
			self.temp_monster.health.nb_dices = value.nb_dices
			self.temp_monster.health.nb_faces = value.nb_faces
			self.temp_monster.health.multiplier = value.multiplier
			self.temp_monster.health.bonus = value.addsub
		else:
			if name == 'type':
				self.temp_monster.type = value
			if name == 'icon':
				self.temp_monster.icon = value
			if name == 'level':
				self.temp_monster.level = value
			if name == 'attack_rating':
				self.temp_monster.attack_rating = value
			if name == 'defense_rating':
				self.temp_monster.defense_rating = value
			if name == 'xp':
				self.temp_monster.xp = value
			if name == 'weight':
				self.temp_monster.weight = value
			if name == 'corpse':
				self.temp_monster.corpse = value
			if name == 'article':
				self.temp_monster.article = value
			if name == 'unidentified_name':
				self.temp_monster.unidentified_name = value
		return True

	def end_struct(self, struct, name):
		self.temp_monster.dark_color = libtcod.color_lerp(libtcod.black, self.temp_monster.color, 0.3)
		if self.temp_monster.level == 1:
			self.temp_monster.flags.append('identified')
		game.monsters.add_to_list(self.temp_monster)
		return True

	def error(self, msg):
		print 'error : ', msg
		return True
