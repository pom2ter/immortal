import libtcodpy as libtcod
import game
import util


class Item(object):
	def __init__(self, typ, name, unid_name, plural, icon, color, dark_color, level, weight, cost, dice, article, charge, duration, expiration, flags):
		self.type = typ
		self.name = name
		self.unidentified_name = unid_name
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
		return True

	# picks up the item
	def pick_up(self, ts, silent=False):
		if self.type == 'money':
			gold = libtcod.random_get_int(game.rnd, 1, 100)
			if not silent:
				game.message.new('You pick up ' + str(gold) + ' gold pieces', game.turns, libtcod.gold)
			game.player.gold += gold
		else:
			if not silent:
				game.message.new('You pick up ' + self.article + self.unidentified_name, game.turns, libtcod.green)
			self.turn_created = ts
			game.player.inventory.append(self)
		if not silent:
			util.add_turn()

	# use the item
	def use(self):
		if 'usable' in self.flags:
			if 'healing' in self.flags:
				if game.player.health == game.player.max_health:
					game.message.new('You are already at max health.', game.turns)
				else:
					heal = self.dice.roll_dice()
					game.player.heal_health(heal)
					game.message.new('You gain ' + str(heal) + ' hit points.', game.turns, libtcod.green)

			if 'mana_healing' in self.flags:
				if game.player.mana == game.player.max_mana:
					game.message.new('Your mana is already at maximum.', game.turns)
				else:
					heal = self.dice.roll_dice()
					game.player.heal_mana(heal)
					game.message.new('You gain ' + str(heal) + ' mana points.', game.turns, libtcod.green)

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


class ItemList(object):
	def __init__(self):
		self.list = []

	# setup the items structure and run parser
	def init_parser(self):
		parser = libtcod.parser_new()
		item_type_struct = libtcod.parser_new_struct(parser, 'item_type')
		libtcod.struct_add_property(item_type_struct, 'type', libtcod.TYPE_STRING, True)
		libtcod.struct_add_property(item_type_struct, 'unidentified_name', libtcod.TYPE_STRING, True)
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
		libtcod.struct_add_flag(item_type_struct, 'usable')
		libtcod.struct_add_flag(item_type_struct, 'equippable')
		libtcod.struct_add_flag(item_type_struct, 'consumable')
		libtcod.struct_add_flag(item_type_struct, 'torchlight')
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
		libtcod.struct_add_flag(item_type_struct, 'corpse_goblin')
		libtcod.struct_add_flag(item_type_struct, 'corpse_kobold')
		libtcod.struct_add_flag(item_type_struct, 'corpse_orc')
		libtcod.struct_add_flag(item_type_struct, 'corpse_rat')
		libtcod.struct_add_flag(item_type_struct, 'corpse_cat')
		libtcod.struct_add_flag(item_type_struct, 'corpse_bat')
		libtcod.struct_add_flag(item_type_struct, 'corpse_dog')
		libtcod.struct_add_flag(item_type_struct, 'corpse_lizard')
		libtcod.struct_add_flag(item_type_struct, 'corpse_human')
		libtcod.struct_add_flag(item_type_struct, 'corpse_wolf')
		libtcod.struct_add_flag(item_type_struct, 'corpse_bear')
		libtcod.struct_add_flag(item_type_struct, 'corpse_troll')
		libtcod.struct_add_flag(item_type_struct, 'corpse_gnoll')
		libtcod.struct_add_flag(item_type_struct, 'corpse_hound')
		libtcod.parser_run(parser, 'data/items.txt', ItemListener())

	# add an item to the list
	def add_to_list(self, item=None):
		if item is not None:
			self.list.append(item)

	# get an item from the list
	def get_item(self, name):
		for item in self.list:
			if name == item.name:
				return item
		return None

	# choose a random item based on its level
	def get_item_by_level(self, level):
		item = libtcod.random_get_int(game.rnd, 0, len(self.list) - 1)
		while (self.list[item].level > level) or (self.list[item].type == 'corpse'):
			item = libtcod.random_get_int(game.rnd, 0, len(self.list) - 1)
		return self.list[item]


class Dice(object):
	def __init__(self, dices, faces, multi, bonus):
		self.nb_dices = dices
		self.nb_faces = faces
		self.multiplier = multi
		self.bonus = bonus

	# throws some dice
	def roll_dice(self):
		return libtcod.random_get_int(game.rnd, self.nb_dices, self.nb_dices * self.nb_faces * int(self.multiplier)) + int(self.bonus)


class ItemListener(object):
	def new_struct(self, struct, name):
		self.temp_item = Item('', '', '', '', '', [0, 0, 0], [0, 0, 0], 0, 0, 0, Dice(0, 0, 0, 0), '', 0, 0, 0, [])
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
			if name == 'unidentified_name':
				self.temp_item.unidentified_name = value
			if name == 'plural':
				self.temp_item.plural = value
		return True

	def end_struct(self, struct, name):
		self.temp_item.dark_color = libtcod.color_lerp(libtcod.black, self.temp_item.color, 0.3)
		game.items.add_to_list(self.temp_item)
		return True

	def error(self, msg):
		print 'error : ', msg
		return True
