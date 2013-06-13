import libtcodpy as libtcod
import game
import util
import map


#######################################
# Item Class
#######################################

class Item(object):
	def __init__(self, type, name, status, prefix, suffix, plural, icon, color, dark_color, level, weight, cost, prefix_cost, suffix_cost, dice, article, charge, duration, expiration, flags):
		self.type = type
		self.name = name
		self.full_name = status + prefix + name + suffix
		self.status = status
		self.prefix = prefix
		self.suffix = suffix
		self.plural = plural
		self.full_plural = status + prefix + plural + suffix
		self.icon = icon
		self.color = libtcod.Color(color[0], color[1], color[2])
		self.dark_color = libtcod.Color(dark_color[0], dark_color[1], dark_color[2])
		self.level = level
		self.weight = weight
		self.cost = cost * prefix_cost * suffix_cost
		self.dice = dice
		self.article = article
		self.duration = duration
		self.expiration = expiration
		self.cur_expiration = 0
		self.charges = charge
		self.quantity = 1
		self.turn_created = 0
		self.active = False
		self.flags = flags

	# return true (equal) if conditions are met
	def __eq__(self, other):
		return self.full_name == other.full_name and self.charges == other.charges and self.flags == other.flags and self.duration == other.duration and self.cur_expiration == other.cur_expiration and self.active == other.active

	# return item's name base of identity level
	def get_name(self, article=False):
		string = ''
		if article:
			string = self.article
		if "fully_identified" in self.flags:
			if self.quantity > 1:
				string = str(self.quantity) + ' ' + self.full_plural
			else:
				string += self.full_name
		elif "identified" in self.flags:
			if self.quantity > 1:
				string = str(self.quantity) + ' ' + self.prefix + self.plural + self.suffix
			else:
				string += self.prefix + self.name + self.suffix
		else:
			if self.quantity > 1:
				string = str(self.quantity) + ' ' + self.plural
			else:
				string += self.name
		return string

	# return the plural name of the item
	def get_plural_name(self):
		if "fully_identified" in self.flags:
			return self.full_plural
		elif "identified" in self.flags:
			return self.prefix + self.plural + self.suffix
		return self.plural

	# return true if item is active
	def is_active(self):
		if self.active:
			self.duration -= 1
			if self.duration == 0:
				return True
		return False

	# return true if item can be equipped
	def is_equippable(self):
		if 'equippable' in self.flags:
			return True
		return False

	# return true if item 'expiration date' has been reached
	def is_expired(self):
		if self.cur_expiration >= 1:
			self.cur_expiration -= 1
			if self.cur_expiration == 0:
				return True
		return False

	# return true if item is identified, always returns true for now
	def is_identified(self):
		if 'identified' in self.flags:
			return True
		return False

	# picks up the item
	def pick_up(self, ts):
		if self.type == 'money':
			gold = libtcod.random_get_int(game.rnd, 1, 100)
			game.message.new('You pick up ' + str(gold) + ' ' + self.name + ' pieces', game.turns, libtcod.gold)
			game.player.gold += gold
		else:
			self.quantity = 1
			game.message.new('You pick up ' + self.get_name(True), game.turns, libtcod.green)
			self.turn_created = ts
			game.player.inventory.append(self)
		util.add_turn()

	# use the item
	def use(self):
		if 'usable' in self.flags:
			if 'heal_health' in self.flags:
				if game.player.health == game.player.max_health:
					game.message.new('You are already at max health.', game.turns)
				else:
					heal = self.dice.roll_dice()
					game.player.heal_health(heal)
					game.message.new('You gain ' + str(heal) + ' hit points.', game.turns, libtcod.green)

			if 'heal_mana' in self.flags:
				if game.player.mana == game.player.max_mana:
					game.message.new('Your mana is already at maximum.', game.turns)
				else:
					heal = self.dice.roll_dice()
					game.player.heal_mana(heal)
					game.message.new('You gain ' + str(heal) + ' mana points.', game.turns, libtcod.green)

			if 'heal_stamina' in self.flags:
				if game.player.stamina == game.player.max_stamina:
					game.message.new('Your stamina is already at maximum.', game.turns)
				else:
					heal = self.dice.roll_dice()
					game.player.heal_stamina(heal)
					game.message.new('You gain ' + str(heal) + ' stamina.', game.turns, libtcod.green)

			if 'torchlight' in self.flags:
				if self.active:
					self.active = False
					game.fov_torch = any('torchlight' in x.flags and x.active for x in game.player.inventory)
					game.message.new('You extenguish the ' + self.name, game.turns, libtcod.gold)
				else:
					game.fov_torch = True
					self.active = True
					game.message.new('You light the ' + self.name, game.turns, libtcod.gold)
				game.fov_recompute = True

			if self.charges > 0:
				self.charges -= 1
				if self.charges == 0:
					game.player.inventory.remove(self)
			util.add_turn()
		else:
			game.message.new("You can't use that item.", game.turns)


#######################################
# BaseItem Class
#######################################

class BaseItem(object):
	def __init__(self, typ, name, plural, icon, color, dark_color, level, weight, cost, dice, article, charge, duration, expiration, flags):
		self.type = typ
		self.name = name
		self.plural = plural
		self.icon = icon
		self.color = libtcod.Color(color[0], color[1], color[2])
		self.dark_color = libtcod.Color(dark_color[0], dark_color[1], dark_color[2])
		self.level = level
		self.weight = weight
		self.cost = cost
		self.dice = dice
		self.article = article
		self.charges = charge
		self.flags = flags
		self.turn_created = 0
		self.duration = duration
		self.expiration = expiration
		self.cur_expiration = 0
		self.quantity = 1
		self.active = False

	# return true (equal) if conditions are met
	def __eq__(self, other):
		return self.name == other.name and self.charges == other.charges and self.flags == other.flags and self.duration == other.duration and self.cur_expiration == other.cur_expiration and self.active == other.active


class BaseItemList(object):
	def __init__(self):
		self.list = []

	# setup the items structure and run parser
	def init_parser(self):
		parser = libtcod.parser_new()
		item_type_struct = libtcod.parser_new_struct(parser, 'item_type')
		libtcod.struct_add_property(item_type_struct, 'type', libtcod.TYPE_STRING, True)
		libtcod.struct_add_property(item_type_struct, 'plural', libtcod.TYPE_STRING, True)
		libtcod.struct_add_property(item_type_struct, 'icon', libtcod.TYPE_STRING, True)
		libtcod.struct_add_property(item_type_struct, 'icon_color', libtcod.TYPE_COLOR, True)
		libtcod.struct_add_property(item_type_struct, 'dark_color', libtcod.TYPE_COLOR, True)
		libtcod.struct_add_property(item_type_struct, 'level', libtcod.TYPE_INT, True)
		libtcod.struct_add_property(item_type_struct, 'weight', libtcod.TYPE_FLOAT, False)
		libtcod.struct_add_property(item_type_struct, 'cost', libtcod.TYPE_INT, False)
		libtcod.struct_add_property(item_type_struct, 'dices', libtcod.TYPE_DICE, False)
		libtcod.struct_add_property(item_type_struct, 'article', libtcod.TYPE_STRING, True)
		libtcod.struct_add_property(item_type_struct, 'charge', libtcod.TYPE_INT, False)
		libtcod.struct_add_property(item_type_struct, 'duration', libtcod.TYPE_INT, False)
		libtcod.struct_add_property(item_type_struct, 'expiration', libtcod.TYPE_INT, False)
		libtcod.struct_add_flag(item_type_struct, 'healing')
		libtcod.struct_add_flag(item_type_struct, 'mana_healing')
		libtcod.struct_add_flag(item_type_struct, 'stamina_healing')
		libtcod.struct_add_flag(item_type_struct, 'usable')
		libtcod.struct_add_flag(item_type_struct, 'equippable')
		libtcod.struct_add_flag(item_type_struct, 'consumable')
		libtcod.struct_add_flag(item_type_struct, 'torchlight')
		libtcod.struct_add_flag(item_type_struct, 'identified')
		libtcod.struct_add_flag(item_type_struct, 'weapon_dagger')
		libtcod.struct_add_flag(item_type_struct, 'weapon_sword')
		libtcod.struct_add_flag(item_type_struct, 'weapon_mace')
		libtcod.struct_add_flag(item_type_struct, 'weapon_axe')
		libtcod.struct_add_flag(item_type_struct, 'weapon_staff')
		libtcod.struct_add_flag(item_type_struct, 'weapon_polearm')
		libtcod.struct_add_flag(item_type_struct, 'weapon_bow')
		libtcod.struct_add_flag(item_type_struct, 'armor_shield')
		libtcod.struct_add_flag(item_type_struct, 'armor_head')
		libtcod.struct_add_flag(item_type_struct, 'armor_cloak')
		libtcod.struct_add_flag(item_type_struct, 'armor_body')
		libtcod.struct_add_flag(item_type_struct, 'armor_hands')
		libtcod.struct_add_flag(item_type_struct, 'armor_feet')
		libtcod.struct_add_flag(item_type_struct, 'armor_ring')
		libtcod.struct_add_flag(item_type_struct, 'corpse')
		libtcod.parser_run(parser, 'data/items.txt', BaseItemListener())

	# add an item to the list
	def add_to_list(self, item=None):
		if item is not None:
			self.list.append(item)

	# create a corpse 'item'
	def create_corpse(self, mname, weight):
		item = self.get_item('corpse')
		loot = Item(item.type, mname + ' ' + item.name, 'uncursed ', '', '', item.plural, item.icon, item.color, item.dark_color, item.level, weight, item.cost, 1, 1, item.dice, item.article, item.charges, item.duration, item.expiration, item.flags)
		return loot

	# create specific item
	def create_item(self, status, prefix, item, suffix):
		item = self.get_item(item)
		if prefix is not None:
			prefix = game.prefix.get_prefix(prefix)
		if suffix is not None:
			suffix = game.suffix.get_suffix(suffix)
		loot = self.generate_stats(status, prefix, item, suffix)
		return loot

	# generate some item stats
	def generate_stats(self, status, prefix, item, suffix):
		pname, sname = '', ''
		pcost, scost = 1, 1

		ilvl = item.level
		dice = item.dice
		flags = item.flags
		if prefix is not None:
			if prefix.level > ilvl:
				ilvl = prefix.level
			pcost = prefix.cost_multiplier
			pname = prefix.name
			if len(prefix.flags):
				flags += prefix.flags
		if suffix is not None:
			if suffix.level > ilvl:
				ilvl = suffix.level
			scost = suffix.cost_multiplier
			sname = suffix.name
			if suffix.dice.nb_faces > 0:
				dice = suffix.dice
			if len(suffix.flags):
				flags += suffix.flags
		flags.append('identified')
		loot = Item(item.type, item.name, status, pname, sname, item.plural, item.icon, item.color, item.dark_color, ilvl, item.weight, item.cost, pcost, scost, dice, item.article, item.charges, item.duration, item.expiration, list(set(flags)))
		return loot

	# fetch an item from the list
	def get_item(self, name):
		for item in self.list:
			if name == item.name:
				return item
		return None

	# choose a random item based on its level
	def get_item_by_level(self, level):
		item = libtcod.random_get_int(game.rnd, 0, len(self.list) - 1)
		while (self.list[item].level > level) or (self.list[item].type == 'corpse') or (self.list[item].type == 'money'):
			item = libtcod.random_get_int(game.rnd, 0, len(self.list) - 1)
		return self.list[item]

	# choose a random item based on its type
	def get_item_by_type(self, type, level=100):
		item = libtcod.random_get_int(game.rnd, 0, len(self.list) - 1)
		while (self.list[item].type != type) or (self.list[item].level > level):
			item = libtcod.random_get_int(game.rnd, 0, len(self.list) - 1)
		return self.list[item]

	# generate an item
	def loot_generation(self, x, y, level):
		prefix, suffix = None, None
		status = ''

		# generate base item
		dice = libtcod.random_get_int(game.rnd, 1, 100)
		if dice <= 10:
			d = self.get_item_by_type('money', level)
		else:
			if dice <= 80:
				d = self.get_item_by_level(level)
			elif dice <= 99:
				d = self.get_item_by_level(level + 1)
			else:
				d = self.get_item_by_level(level + 2)

			# generate prefix
			pdice = libtcod.random_get_int(game.rnd, 1, 100)
			if pdice <= 60:
				prefix = game.prefix.get_prefix_by_level(level)
			elif pdice <= 80:
				prefix = game.prefix.get_prefix_by_level(level + 1)

			# generate suffix
			sdice = libtcod.random_get_int(game.rnd, 1, 100)
			if sdice <= 60:
				suffix = game.suffix.get_suffix_by_level(level)
			elif sdice <= 80:
				suffix = game.suffix.get_suffix_by_level(level + 1)

			# generate status
			stdice = libtcod.random_get_int(game.rnd, 1, 100)
			if stdice <= 90:
				status = 'uncursed '
			elif stdice <= 95:
				status = 'blessed '
			else:
				status = 'cursed '

		loot = self.generate_stats(status, prefix, d, suffix)
		obj = map.Object(x, y, loot.icon, loot.name, loot.color, True, item=loot)
		return obj


class Dice(object):
	def __init__(self, dices, faces, multi, bonus):
		self.nb_dices = dices
		self.nb_faces = faces
		self.multiplier = multi
		self.bonus = bonus

	# throws some dice
	def roll_dice(self):
		return libtcod.random_get_int(game.rnd, self.nb_dices, self.nb_dices * self.nb_faces * int(self.multiplier)) + int(self.bonus)


class BaseItemListener(object):
	def new_struct(self, struct, name):
		self.temp_item = BaseItem('', '', '', '', [0, 0, 0], [0, 0, 0], 0, 0, 0, Dice(0, 0, 0, 0), '', 0, 0, 0, [])
		self.temp_item.name = name
		return True

	def new_flag(self, name):
		self.temp_item.flags.append(name)
		return True

	def new_property(self, name, typ, value):
		if name == 'icon_color':
			self.temp_item.color.r = value.r
			self.temp_item.color.g = value.g
			self.temp_item.color.b = value.b
		elif name == 'dark_color':
			self.temp_item.dark_color.r = value.r
			self.temp_item.dark_color.g = value.g
			self.temp_item.dark_color.b = value.b
		elif name == 'dices':
			self.temp_item.dice.nb_dices = value.nb_dices
			self.temp_item.dice.nb_faces = value.nb_faces
			self.temp_item.dice.multiplier = value.multiplier
			self.temp_item.dice.bonus = value.addsub
		else:
			if name == 'type':
				self.temp_item.type = value
			if name == 'cost':
				self.temp_item.cost = value
			if name == 'icon':
				self.temp_item.icon = value
			if name == 'level':
				self.temp_item.level = value
			if name == 'weight':
				self.temp_item.weight = value
			if name == 'article':
				self.temp_item.article = value
			if name == 'charge':
				self.temp_item.charges = value
			if name == 'duration':
				self.temp_item.duration = value
			if name == 'expiration':
				self.temp_item.expiration = value
				self.temp_item.cur_expiration = value
			if name == 'plural':
				self.temp_item.plural = value
		return True

	def end_struct(self, struct, name):
		self.temp_item.dark_color = libtcod.color_lerp(libtcod.black, self.temp_item.color, 0.3)
		game.baseitems.add_to_list(self.temp_item)
		return True

	def error(self, msg):
		print 'error : ', msg
		return True


#######################################
# Prefix Class
#######################################

class Prefix(object):
	def __init__(self, name, level, cost, quality, flags):
		self.name = name
		self.level = level
		self.cost_multiplier = cost
		self.quality = quality
		self.flags = flags


class PrefixList(object):
	def __init__(self):
		self.list = []

	# setup the items structure and run parser
	def init_parser(self):
		parser = libtcod.parser_new()
		prefix_type_struct = libtcod.parser_new_struct(parser, 'prefix_type')
		libtcod.struct_add_property(prefix_type_struct, 'cost_multiplier', libtcod.TYPE_FLOAT, True)
		libtcod.struct_add_property(prefix_type_struct, 'level', libtcod.TYPE_INT, True)
		libtcod.struct_add_property(prefix_type_struct, 'quality', libtcod.TYPE_INT, False)
		libtcod.parser_run(parser, 'data/prefix.txt', PrefixListener())

	# add a prefix to the list
	def add_to_list(self, prefix=None):
		if prefix is not None:
			self.list.append(prefix)

	# fetch a prefix from the list
	def get_prefix(self, name):
		for prefix in self.list:
			if name == prefix.name:
				return prefix
		return None

	# choose a random prefix based on its level
	def get_prefix_by_level(self, level):
		prefix = libtcod.random_get_int(game.rnd, 0, len(self.list) - 1)
		while self.list[prefix].level > level:
			prefix = libtcod.random_get_int(game.rnd, 0, len(self.list) - 1)
		return self.list[prefix]


class PrefixListener(object):
	def new_struct(self, struct, name):
		self.temp_prefix = Prefix('', 0, 0, 0, [])
		self.temp_prefix.name = name
		return True

	def new_flag(self, name):
		self.temp_prefix.flags.append(name)
		return True

	def new_property(self, name, typ, value):
		if name == 'cost_multiplier':
			self.temp_prefix.cost_multiplier = value
		if name == 'level':
			self.temp_prefix.level = value
		if name == 'quality':
			self.temp_prefix.quality = value
		return True

	def end_struct(self, struct, name):
		game.prefix.add_to_list(self.temp_prefix)
		return True

	def error(self, msg):
		print 'error : ', msg
		return True


#######################################
# Suffix Class
#######################################

class Suffix(object):
	def __init__(self, name, color, dark_color, level, cost, dice, flags):
		self.name = name
		self.color = libtcod.Color(color[0], color[1], color[2])
		self.dark_color = libtcod.Color(dark_color[0], dark_color[1], dark_color[2])
		self.level = level
		self.cost_multiplier = cost
		self.dice = dice
		self.flags = flags


class SuffixList(object):
	def __init__(self):
		self.list = []

	# setup the items structure and run parser
	def init_parser(self):
		parser = libtcod.parser_new()
		suffix_type_struct = libtcod.parser_new_struct(parser, 'suffix_type')
		libtcod.struct_add_property(suffix_type_struct, 'icon_color', libtcod.TYPE_COLOR, False)
		libtcod.struct_add_property(suffix_type_struct, 'cost_multiplier', libtcod.TYPE_FLOAT, True)
		libtcod.struct_add_property(suffix_type_struct, 'level', libtcod.TYPE_INT, True)
		libtcod.struct_add_property(suffix_type_struct, 'dices', libtcod.TYPE_DICE, False)
		libtcod.struct_add_flag(suffix_type_struct, 'heal_health')
		libtcod.struct_add_flag(suffix_type_struct, 'heal_mana')
		libtcod.struct_add_flag(suffix_type_struct, 'heal_stamina')
		libtcod.struct_add_flag(suffix_type_struct, 'protect')
		libtcod.struct_add_flag(suffix_type_struct, 'regenerate')
		libtcod.parser_run(parser, 'data/suffix.txt', SuffixListener())

	# add a suffix to the list
	def add_to_list(self, suffix=None):
		if suffix is not None:
			self.list.append(suffix)

	# fetch a suffix from the list
	def get_suffix(self, name):
		for suffix in self.list:
			if name == suffix.name:
				return suffix
		return None

	# choose a random suffix based on its level
	def get_suffix_by_level(self, level):
		suffix = libtcod.random_get_int(game.rnd, 0, len(self.list) - 1)
		while self.list[suffix].level > level:
			suffix = libtcod.random_get_int(game.rnd, 0, len(self.list) - 1)
		return self.list[suffix]


class SuffixListener(object):
	def new_struct(self, struct, name):
		self.temp_suffix = Suffix('', [0, 0, 0], [0, 0, 0], 0, 0, Dice(0, 0, 0, 0), [])
		self.temp_suffix.name = name
		return True

	def new_flag(self, name):
		self.temp_suffix.flags.append(name)
		return True

	def new_property(self, name, typ, value):
		if name == 'icon_color':
			self.temp_suffix.color.r = value.r
			self.temp_suffix.color.g = value.g
			self.temp_suffix.color.b = value.b
		elif name == 'dices':
			self.temp_suffix.dice.nb_dices = value.nb_dices
			self.temp_suffix.dice.nb_faces = value.nb_faces
			self.temp_suffix.dice.multiplier = value.multiplier
			self.temp_suffix.dice.bonus = value.addsub
		else:
			if name == 'cost_multiplier':
				self.temp_suffix.cost_multiplier = value
			if name == 'level':
				self.temp_suffix.level = value
		return True

	def end_struct(self, struct, name):
		self.temp_suffix.dark_color = libtcod.color_lerp(libtcod.black, self.temp_suffix.color, 0.3)
		game.suffix.add_to_list(self.temp_suffix)
		return True

	def error(self, msg):
		print 'error : ', msg
		return True
