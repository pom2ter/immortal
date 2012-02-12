import libtcodpy as libtcod
import game


class Item(object):
	def __init__(self, name, unid_name, icon, color, dark_color, weight):
		self.name = name
		self.unidentified_name = unid_name
		self.icon = icon
		self.color = libtcod.Color(color[0], color[1], color[2])
		self.dark_color = libtcod.Color(dark_color[0], dark_color[1], dark_color[2])
		self.weight = 0.0
		self.cost = 0
		self.dice = Dice(0, 0, 0, 0)

	def pick_up(self):
		if self.name == "gold":
			gold = libtcod.random_get_int(0, 1, 100)
			game.message.new('You pick up ' + str(gold) + ' gold pieces', game.player.turns, libtcod.gold)
			game.player.gold += gold
		else:
			game.message.new('You pick up a ' + self.unidentified_name, game.player.turns, libtcod.green)
			game.player.inventory.append(self)


class ItemList(object):
	def __init__(self):
		self.list = []

	def additem(self, name=None, unid_name=None, icon=None, color=[0, 0, 0], dark_color=[0, 0, 0], weight=0):
		self.list.append(Item(name, unid_name, icon, color, dark_color, weight))

	def getitem(self, name):
		for item in self.list:
			if name in item.name:
				return item
		return None


class Dice(object):
	def __init__(self, dices, faces, multi, bonus):
		self.nb_dices = dices
		self.nb_faces = faces
		self.multiplier = multi
		self.bonus = bonus


class ItemListener(object):
	temp_item = None

	def new_struct(self, struct, name):
		self.temp_item = Item('', '', '', [0, 0, 0], [0, 0, 0], 0)
		self.temp_item.name = name
		return True

	def new_flag(self, name):
		#print 'new flag named ', name
		return True

	def new_property(self, name, typ, value):
		type_names = ['NONE', 'BOOL', 'CHAR', 'INT', 'FLOAT', 'STRING', 'COLOR', 'DICE']
		if name == 'icon_color':
			self.temp_item.color.r = value.r
			self.temp_item.color.g = value.g
			self.temp_item.color.b = value.b
		elif name == 'dark_color':
			self.temp_item.dark_color.r = value.r
			self.temp_item.dark_color.g = value.g
			self.temp_item.dark_color.b = value.b
		elif name == 'dice_field' or type_names[typ] == "DICE":
			self.temp_item.dice.nb_dices = value.nb_dices
			self.temp_item.dice.nb_faces = value.nb_faces
			self.temp_item.dice.multiplier = value.multiplier
			self.temp_item.dice.bonus = value.addsub
		else:
			if name == "icon":
				self.temp_item.icon = value
			if name == "weight":
				self.temp_item.weight = value
			if name == "unidentified_name":
				self.temp_item.unidentified_name = value
		return True

	def end_struct(self, struct, name):
		game.items.additem(self.temp_item.name, self.temp_item.unidentified_name, self.temp_item.icon, self.temp_item.color, self.temp_item.dark_color, self.temp_item.weight)
		return True

	def error(self, msg):
		print 'error : ', msg
		return True
