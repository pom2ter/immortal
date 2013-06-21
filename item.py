import libtcodpy as libtcod
import game
import util
import map


#########################################
# Item Class
#########################################

class Item(object):
	def __init__(self, type, name, status, prefix, suffix, plural, icon, color, dark_color, level, weight, cost, prefix_cost, suffix_cost, dice, article, charge, duration, expiration, bonus, quality, flags):
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
		self.quality = quality
		self.bonus = bonus
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

	# return true if item is identified
	def is_identified(self):
		if any(i in self.flags for i in ['fully_identified', 'identified']):
			return True
		return False

	# picks up the item
	def pick_up(self, ts):
		if self.type == 'money':
			gold = util.roll_dice(1, 20)
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


#########################################
# BaseItem Class
#########################################

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
		loot = Item(item.type, mname + ' ' + item.name, 'uncursed ', '', '', item.plural, item.icon, item.color, item.dark_color, item.level, weight, item.cost, 1, 1, item.dice, item.article, item.charges, item.duration, item.expiration, 0, 1, item.flags)
		return loot

	# create specific item
	def create_item(self, status, prefix, item, suffix):
		item = self.get_item(item)
		if prefix is not None:
			prefix = game.prefix.get_prefix(prefix)
		if suffix is not None:
			suffix = game.suffix.get_suffix(suffix)
		loot = self.generate_item_stats(status, prefix, item, suffix)
		return loot

	# generate some item stats
	def generate_item_stats(self, status, prefix, item, suffix):
		pname, sname = '', ''
		pcost, scost = 1, 1
		pquality = 1
		bonus = 0

		ilvl = item.level
		dice = item.dice
		flags = item.flags
		if item.type == 'armor':
			if prefix is None:
				pname = 'leather '
		if prefix is not None:
			if prefix.level > ilvl:
				ilvl = prefix.level
			pcost = prefix.cost_multiplier
			pname = prefix.name
			pquality = prefix.quality
			if len(prefix.flags):
				flags += prefix.flags
		if suffix is not None:
			if suffix.level > ilvl:
				ilvl = suffix.level
			scost = suffix.cost_multiplier
			sname = suffix.name
			bonus = suffix.bonus
			if suffix.dice.nb_faces > 0:
				dice = suffix.dice
			if len(suffix.flags):
				flags += suffix.flags
#		flags.append('fully_identified')
		loot = Item(item.type, item.name, status, pname, sname, item.plural, item.icon, item.color, item.dark_color, ilvl, item.weight, item.cost, pcost, scost, dice, item.article, item.charges, item.duration, item.expiration, bonus, pquality, list(set(flags)))
		return loot

	# fetch an item from the list
	def get_item(self, name):
		for item in self.list:
			if name == item.name:
				return item
		return None

	# choose a random item based on its level
	def get_item_by_level(self, level):
		item = [x for x in self.list if x.level <= level and x.type != 'corpse' and x.type != 'money']
		if item:
			return item[libtcod.random_get_int(game.rnd, 0, len(item) - 1)]
		return None

	# choose a random item based on its type
	def get_item_by_type(self, type, level=100):
		item = [x for x in self.list if x.level <= level and x.type == type]
		if item:
			return item[libtcod.random_get_int(game.rnd, 0, len(item) - 1)]
		return None

	# generate an item
	def loot_generation(self, x, y, level):
		prefix, suffix = None, None
		status = ''

		# generate base item
		dice = util.roll_dice(1, 100)
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
			pdice = util.roll_dice(1, 100)
			if pdice >= 100 - (level * 6):
				if pdice <= 85:
					prefix = game.prefix.get_prefix_by_level(level, d.type)
				else:
					prefix = game.prefix.get_prefix_by_level(level + 1, d.type)

			# generate suffix
			sdice = util.roll_dice(1, 100)
			if sdice >= 100 - (level * 6):
				if sdice <= 85:
					suffix = game.suffix.get_suffix_by_level(level, d.type)
				else:
					suffix = game.suffix.get_suffix_by_level(level + 1, d.type)

			# generate status
			stdice = util.roll_dice(1, 100)
			if stdice <= 90:
				status = 'uncursed '
			elif stdice <= 95:
				status = 'blessed '
			else:
				status = 'cursed '

		loot = self.generate_item_stats(status, prefix, d, suffix)
		obj = map.Object(x, y, loot.icon, loot.name, loot.color, True, item=loot)
		return obj


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


#########################################
# Prefix Class
#########################################

class Prefix(object):
	def __init__(self, name, type, level, cost, quality, flags):
		self.name = name
		self.type = type
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
		libtcod.struct_add_property(prefix_type_struct, 'type', libtcod.TYPE_STRING, True)
		libtcod.struct_add_property(prefix_type_struct, 'cost_multiplier', libtcod.TYPE_FLOAT, True)
		libtcod.struct_add_property(prefix_type_struct, 'level', libtcod.TYPE_INT, True)
		libtcod.struct_add_property(prefix_type_struct, 'quality', libtcod.TYPE_INT, False)
		libtcod.struct_add_flag(prefix_type_struct, 'armor')
		libtcod.struct_add_flag(prefix_type_struct, 'robe')
		libtcod.struct_add_flag(prefix_type_struct, 'cloak')
		libtcod.struct_add_flag(prefix_type_struct, 'shield')
		libtcod.struct_add_flag(prefix_type_struct, 'weapon')
		libtcod.struct_add_flag(prefix_type_struct, 'ring')
		libtcod.struct_add_flag(prefix_type_struct, 'potion')
		libtcod.struct_add_flag(prefix_type_struct, 'damage_bonus1')
		libtcod.struct_add_flag(prefix_type_struct, 'damage_bonus2')
		libtcod.struct_add_flag(prefix_type_struct, 'damage_bonus3')
		libtcod.struct_add_flag(prefix_type_struct, 'ar_bonus1')
		libtcod.struct_add_flag(prefix_type_struct, 'ar_bonus2')
		libtcod.struct_add_flag(prefix_type_struct, 'ar_bonus3')
		libtcod.struct_add_flag(prefix_type_struct, 'fire_bonus1')
		libtcod.struct_add_flag(prefix_type_struct, 'fire_bonus2')
		libtcod.struct_add_flag(prefix_type_struct, 'fire_bonus3')
		libtcod.struct_add_flag(prefix_type_struct, 'cold_bonus1')
		libtcod.struct_add_flag(prefix_type_struct, 'cold_bonus2')
		libtcod.struct_add_flag(prefix_type_struct, 'cold_bonus3')
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
	def get_prefix_by_level(self, level, item_type):
		prefix = [x for x in self.list if x.level <= level and item_type in x.flags]
		if prefix:
			return prefix[libtcod.random_get_int(game.rnd, 0, len(prefix) - 1)]
		return None


class PrefixListener(object):
	def new_struct(self, struct, name):
		self.temp_prefix = Prefix('', '', 0, 0, 1, [])
		self.temp_prefix.name = name
		return True

	def new_flag(self, name):
		self.temp_prefix.flags.append(name)
		return True

	def new_property(self, name, typ, value):
		if name == 'type':
			self.temp_prefix.type = value
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


#########################################
# Suffix Class
#########################################

class Suffix(object):
	def __init__(self, name, color, dark_color, level, cost, dice, bonus, flags):
		self.name = name
		self.color = libtcod.Color(color[0], color[1], color[2])
		self.dark_color = libtcod.Color(dark_color[0], dark_color[1], dark_color[2])
		self.level = level
		self.cost_multiplier = cost
		self.dice = dice
		self.bonus = bonus
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
		libtcod.struct_add_property(suffix_type_struct, 'bonus', libtcod.TYPE_INT, False)
		libtcod.struct_add_flag(suffix_type_struct, 'armor')
		libtcod.struct_add_flag(suffix_type_struct, 'robe')
		libtcod.struct_add_flag(suffix_type_struct, 'cloak')
		libtcod.struct_add_flag(suffix_type_struct, 'shield')
		libtcod.struct_add_flag(suffix_type_struct, 'weapon')
		libtcod.struct_add_flag(suffix_type_struct, 'ring')
		libtcod.struct_add_flag(suffix_type_struct, 'potion')
		libtcod.struct_add_flag(suffix_type_struct, 'heal_health')
		libtcod.struct_add_flag(suffix_type_struct, 'heal_mana')
		libtcod.struct_add_flag(suffix_type_struct, 'heal_stamina')
		libtcod.struct_add_flag(suffix_type_struct, 'protect')
		libtcod.struct_add_flag(suffix_type_struct, 'regenerate')
		libtcod.struct_add_flag(suffix_type_struct, 'resist_fire')
		libtcod.struct_add_flag(suffix_type_struct, 'resist_ice')
		libtcod.struct_add_flag(suffix_type_struct, 'resist_poison')
		libtcod.struct_add_flag(suffix_type_struct, 'health_bonus1')
		libtcod.struct_add_flag(suffix_type_struct, 'mana_bonus1')
		libtcod.struct_add_flag(suffix_type_struct, 'stamina_bonus1')
		libtcod.struct_add_flag(suffix_type_struct, 'str_bonus')
		libtcod.struct_add_flag(suffix_type_struct, 'dex_bonus')
		libtcod.struct_add_flag(suffix_type_struct, 'int_bonus')
		libtcod.struct_add_flag(suffix_type_struct, 'wis_bonus')
		libtcod.struct_add_flag(suffix_type_struct, 'end_bonus')
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
	def get_suffix_by_level(self, level, item_type):
		suffix = [x for x in self.list if x.level <= level and item_type in x.flags]
		if suffix:
			return suffix[libtcod.random_get_int(game.rnd, 0, len(suffix) - 1)]
		return None


class SuffixListener(object):
	def new_struct(self, struct, name):
		self.temp_suffix = Suffix('', [0, 0, 0], [0, 0, 0], 0, 0, Dice(0, 0, 0, 0), 0, [])
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
			if name == 'bonus':
				self.temp_suffix.bonus = value
		return True

	def end_struct(self, struct, name):
		self.temp_suffix.dark_color = libtcod.color_lerp(libtcod.black, self.temp_suffix.color, 0.3)
		game.suffix.add_to_list(self.temp_suffix)
		return True

	def error(self, msg):
		print 'error : ', msg
		return True


#########################################
# Dice Class
#########################################

class Dice(object):
	def __init__(self, dices, faces, multi, bonus):
		self.nb_dices = dices
		self.nb_faces = faces
		self.multiplier = multi
		self.bonus = bonus

	# throws some dice
	def roll_dice(self):
		return libtcod.random_get_int(game.rnd, self.nb_dices * int(self.multiplier), self.nb_dices * self.nb_faces * int(self.multiplier)) + int(self.bonus)
