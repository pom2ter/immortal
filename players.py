import libtcodpy as libtcod
import game
import util
import mapgen
import effects


class Player(object):
	def __init__(self):
		self.name = ''
		self.race = ''
		self.gender = ''
		self.profession = ''
		self.strength = 9
		self.base_strength = 9
		self.dexterity = 9
		self.base_dexterity = 9
		self.intelligence = 9
		self.base_intelligence = 9
		self.wisdom = 9
		self.base_wisdom = 9
		self.endurance = 9
		self.base_endurance = 9
		self.karma = 9
		self.base_karma = 9
		self.icon = '@'
		self.icon_color = libtcod.white
		self.level = 1
		self.xp = 0
		self.health = 0
		self.max_health = 0
		self.base_health = 0
		self.mana = 0
		self.max_mana = 0
		self.base_mana = 0
		self.stamina = 0
		self.max_stamina = 0
		self.base_stamina = 0
		self.inventory = []
		self.equipment = []
		self.hunger = 500
		self.money = 0
		self.mks = 0
		self.skill_points = 0
		self.skills = [Skill('Sword', 'Combat', 0, 0), Skill('Axe', 'Combat', 0, 0), Skill('Mace', 'Combat', 0, 0),
						Skill('Dagger', 'Combat', 0, 0), Skill('Polearm', 'Combat', 0, 0), Skill('Staff', 'Combat', 0, 0),
						Skill('Bow', 'Combat', 0, 0), Skill('Missile', 'Combat', 0, 0), Skill('Hands', 'Combat', 0, 0),
						Skill('Detect Traps', 'Physical', 0, 0, True, 'detect_trap'), Skill('Disarm Traps', 'Physical', 0, 0, True), Skill('Swimming', 'Physical', 0, 0),
						Skill('Lockpicking', 'Physical', 0, 0, True), Skill('Artifacts', 'Academic', 0, 0, True), Skill('Mythology', 'Academic', 0, 0)]
		self.flags = ['normal']

	# attack an enemy
	def attack(self, target, ranged=False):
		attacker = util.roll_dice(1, 50)
		defender = util.roll_dice(1, 50)
		weapon = None
		weapon_type = 'weapon'
		missile = None
		missile_slot_type = 'missile'

		for i in range(len(self.equipment)):
			if self.equipment[i].type == 'weapon':
				weapon = self.equipment[i]
				for j in range(len(self.equipment[i].flags)):
					if 'missile_' in self.equipment[i].flags[j]:
						weapon_type = self.equipment[i].flags[j]
			if self.equipment[i].type == 'missile':
				missile = self.equipment[i]
				for j in range(len(self.equipment[i].flags)):
					if 'missile_' in self.equipment[i].flags[j]:
						missile_slot_type = self.equipment[i].flags[j]

		if ranged and weapon_type != missile_slot_type:
			game.message.new("You don't have any ammo for that weapon!", game.turns, libtcod.light_red)
		else:
			if not target.entity.is_hostile():
				target.entity.becomes_hostile()
			if ranged:
				effects.missile_attack(game.char.x, game.char.y, target.x, target.y)
			if (attacker != 1 and defender != 50 and ((attacker + self.attack_rating()) >= (defender + target.entity.defense_rating) or attacker == 50 or defender == 1)) or target.entity.is_disabled():
				damage = 0
				if weapon is not None:
					quality_bonus = 0.75 + (0.25 * weapon.quality)
					damage = int(weapon.dice.roll_dice() * quality_bonus)
					damage += self.damage_modifiers(weapon)
				if damage == 0:
					damage = util.roll_dice(1, 4)
				game.message.new('You hit ' + target.entity.get_name(True) + ' for ' + str(damage) + ' pts of damage.', game.turns, libtcod.light_yellow)
				target.entity.take_damage(target.x, target.y, damage, 'player')
				if target.entity.is_dead():
					game.message.new('The ' + target.entity.get_name() + ' dies!', game.turns, libtcod.light_orange)
					self.gain_xp(target.entity.give_xp())
					self.mks += 1
					target.entity.loot(target.x, target.y)
					target.delete()
				self.skills[self.find_weapon_type()].gain_xp(2)

			else:
				if ranged:
					item = game.baseitems.create_item(missile.status, missile.prefix, missile.name, missile.suffix, missile.flags)
					obj = mapgen.Object(target.x, target.y, item.icon, item.name, item.color, True, item=item)
					obj.first_appearance = game.turns
					game.current_map.objects.append(obj)
					obj.send_to_back()
				game.message.new('You missed the ' + target.entity.get_name() + '.', game.turns)
				self.skills[self.find_weapon_type()].gain_xp(1)
			if ranged:
				missile.lose_quantity()
			self.lose_stamina(1)
			game.player_move = True

	# calculates your attack rating....
	def attack_rating(self):
		ar = self.strength
		ar += self.dexterity * 0.25
		ar += self.karma * 0.25
		ar += self.skills[self.find_weapon_type()].level * 0.2
		self.attack_rating_modifiers()
		return ar

	# ....and apply modifiers
	def attack_rating_modifiers(self):
		modifier = 0
		for i in range(len(self.equipment)):
			if 'ar_bonus1' in self.equipment[i].flags:
				modifier += util.roll_dice(1, 4)
			if 'ar_bonus2' in self.equipment[i].flags:
				modifier += util.roll_dice(1, 4, 2)
			if 'ar_bonus3' in self.equipment[i].flags:
				modifier += util.roll_dice(1, 4, 3)
			if 'burdened' in self.flags:
				modifier -= util.roll_dice(1, 4)
			if 'strained' in self.flags:
				modifier -= util.roll_dice(1, 4, 2)
			if 'overburdened' in self.flags:
				modifier -= util.roll_dice(1, 4, 3)
			if 'hungry' in self.flags:
				modifier -= util.roll_dice(1, 4)
			if 'famished' in self.flags:
				modifier -= util.roll_dice(1, 4, 2)
			if 'starving' in self.flags:
				modifier -= util.roll_dice(1, 4, 3)
		return modifier

	# returns true if player can move
	def can_move(self):
		if 'stuck' in self.flags:
			return False
		return True

	# check weight carried for burdened status
	def check_burdened_status(self):
		self.flags[:] = (value for value in self.flags if value not in ['burdened', 'strained', 'overburdened'])
		weight = 100 * (self.weight_carried() / self.max_carrying_capacity())
		nb, hunger = 35, 0
		if weight >= 150:
			self.flags.append('overburdened')
			if game.turns % 9 == 0 and not self.is_disabled():
				self.lose_stamina(1)
			hunger = 2
		elif weight >= 100:
			self.flags.append('strained')
			hunger = 1
			nb = 100
		elif weight >= 75:
			self.flags.append('burdened')
			nb = 70
		if game.turns % (nb - self.strength) == 0:
			self.heal_stamina(1)
			if 'unconscious' in self.flags:
				game.message.new('You regain consciousness.', game.turns)
				self.flags.remove('unconscious')
		self.check_hunger_level(hunger)

	# checks player condition each turn
	def check_condition(self):
		if 'stuck' in self.flags:
			dice = util.roll_dice(1, 120)
			if self.strength + (self.karma / 2) >= dice:
				game.message.new('You can move freely again.', game.turns)
				self.flags.remove('stuck')
		if 'poison' in self.flags:
			dice = util.roll_dice(1, 120)
			if self.endurance + (self.karma / 2) >= dice:
				game.message.new('You are no longer poisoned.', game.turns)
				self.flags.remove('poison')
			else:
				self.take_damage(1, 'poison')
		if 'sleep' in self.flags:
			dice = util.roll_dice(1, 120)
			if self.wisdom + (self.karma / 2) >= dice:
				game.message.new('You wake up.', game.turns)
				self.flags.remove('sleep')

	# check hunger level
	def check_hunger_level(self, hunger=0):
		self.flags[:] = (value for value in self.flags if value not in ['bloated', 'full', 'normal', 'hungry', 'famished', 'starving'])
		self.hunger += hunger
		if self.hunger < 0:
			self.hunger = 0
		for key, value in game.hunger_levels.items():
			if value['start'] <= self.hunger <= value['end']:
				self.flags.append(key.lower())

	# calculates damage modifiers
	def damage_modifiers(self, obj):
		modifier = 0
		if 'damage_bonus1' in obj.flags:
			modifier += util.roll_dice(1, 6)
		if 'damage_bonus2' in obj.flags:
			modifier += util.roll_dice(1, 6, 2)
		if 'damage_bonus3' in obj.flags:
			modifier += util.roll_dice(1, 6, 3)
		return modifier

	# calculates your defense rating
	def defense_rating(self):
		dr = self.dexterity
		dr += self.wisdom * 0.25
		dr += self.karma * 0.25
		return dr

	# drops an item
	def drop_item(self, item, qty=1):
		for i in range(qty):
			for j in xrange(len(self.inventory)):
				if self.inventory[j] == item:
					pos = j
					break
			obj = mapgen.Object(game.char.x, game.char.y, self.inventory[pos].icon, self.inventory[pos].name, self.inventory[pos].color, True, item=self.inventory[pos])
			obj.first_appearance = self.inventory[pos].turn_created
			game.current_map.objects.append(obj)
			obj.send_to_back()
			self.inventory.pop(pos)

		if qty == 1:
			game.message.new('You drop ' + obj.item.get_name(True) + '.', game.turns, libtcod.red)
		else:
			game.message.new('You drop ' + str(qty) + ' ' + obj.item.get_plural_name() + '.', game.turns, libtcod.red)
		if game.current_map.tile[game.char.x][game.char.y]['type'] == 'trap':
			if self.is_above_ground():
				util.trigger_trap(game.char.x, game.char.y, obj.item.article.capitalize() + obj.item.get_name())
			else:
				util.trigger_trap(game.char.x, game.char.y)
		game.player_move = True

	# equips an item
	def equip_item(self, item):
		for i in xrange(len(self.inventory)):
			if self.inventory[i] == item:
				item = i
				break

		if any(i in self.inventory[item].type for i in ['armor', 'robe', 'cloak']):
			for flags in self.inventory[item].flags:
				if 'armor_' in flags:
					flag = flags
			switch = any(flag in obj.flags for obj in self.equipment)
		elif self.inventory[item].type == 'ring':
			switch = False
			if sum('armor_ring' in obj.flags for obj in self.equipment) > 1:
				switch = True
		else:
			switch = any(self.inventory[item].type in obj.type for obj in self.equipment)

		if switch:
			for obj in reversed(self.equipment):
				if any(i in self.inventory[item].type for i in ['armor', 'robe', 'cloak']):
					if flag in obj.flags:
						self.inventory.append(obj)
						self.equipment.remove(obj)
						old = obj
				else:
					if obj.type == self.inventory[item].type:
						self.inventory.append(obj)
						self.equipment.remove(obj)
						old = obj
						if obj.type == 'ring':
							break

		self.equipment.append(self.inventory[item])
		self.stats_bonus()
		if switch:
			if self.inventory[item].type != 'missile':
				game.message.new('You unequip the ' + old.get_name() + ' before equipping the ' + self.inventory[item].get_name() + '.', game.turns, libtcod.green)
			else:
				game.message.new('You change missile types.', game.turns, libtcod.green)
		else:
			game.message.new('You equip the ' + self.inventory[item].get_name() + '.', game.turns, libtcod.green)
		self.inventory.pop(item)
		game.player_move = True

	# return skill index
	def find_skill(self, skill):
		return [i.name for i in self.skills].index(skill)

	# returns the weapon type
	def find_weapon_type(self):
		for i in range(len(self.equipment)):
			if 'weapon_sword' in self.equipment[i].flags:
				return self.find_skill('Sword')
			if 'weapon_axe' in self.equipment[i].flags:
				return self.find_skill('Axe')
			if 'weapon_mace' in self.equipment[i].flags:
				return self.find_skill('Mace')
			if 'weapon_dagger' in self.equipment[i].flags:
				return self.find_skill('Dagger')
			if 'weapon_polearm' in self.equipment[i].flags:
				return self.find_skill('Polearm')
			if 'weapon_staff' in self.equipment[i].flags:
				return self.find_skill('Staff')
			if 'weapon_bow' in self.equipment[i].flags:
				return self.find_skill('Bow')
			if 'weapon_missile' in self.equipment[i].flags:
				return self.find_skill('Missile')
		return self.find_skill('Hands')

	# stuff to do when you gain a level
	def gain_level(self):
		self.level += 1
		game.message.new('You are now level ' + str(self.level) + '!', game.turns, libtcod.green)
		if self.profession == 'Fighter':
			hp_increase = libtcod.random_get_int(game.rnd, 2, game.FIGHTER_HP_GAIN)
			mp_increase = libtcod.random_get_int(game.rnd, 2, game.FIGHTER_MP_GAIN)
			stamina_increase = libtcod.random_get_int(game.rnd, 2, game.FIGHTER_STAMINA_GAIN)
			self.stat_gain(50, 15, 5, 10, 20)
		if self.profession == 'Rogue':
			hp_increase = libtcod.random_get_int(game.rnd, 2, game.ROGUE_HP_GAIN)
			mp_increase = libtcod.random_get_int(game.rnd, 2, game.ROGUE_MP_GAIN)
			stamina_increase = libtcod.random_get_int(game.rnd, 2, game.ROGUE_STAMINA_GAIN)
			self.stat_gain(20, 50, 10, 10, 10)
		if self.profession == 'Priest':
			hp_increase = libtcod.random_get_int(game.rnd, 2, game.PRIEST_HP_GAIN)
			mp_increase = libtcod.random_get_int(game.rnd, 2, game.PRIEST_MP_GAIN)
			stamina_increase = libtcod.random_get_int(game.rnd, 2, game.PRIEST_STAMINA_GAIN)
			self.stat_gain(20, 10, 10, 50, 10)
		if self.profession == 'Mage':
			hp_increase = libtcod.random_get_int(game.rnd, 2, game.MAGE_HP_GAIN)
			mp_increase = libtcod.random_get_int(game.rnd, 2, game.MAGE_MP_GAIN)
			stamina_increase = libtcod.random_get_int(game.rnd, 2, game.MAGE_STAMINA_GAIN)
			self.stat_gain(10, 15, 50, 20, 5)
		if self.profession == 'Explorer':
			hp_increase = libtcod.random_get_int(game.rnd, 2, game.EXPLORER_HP_GAIN)
			mp_increase = libtcod.random_get_int(game.rnd, 2, game.EXPLORER_MP_GAIN)
			stamina_increase = libtcod.random_get_int(game.rnd, 2, game.EXPLORER_STAMINA_GAIN)
			self.stat_gain(20, 20, 20, 20, 20)
			self.skill_points += 2
		self.skill_points += libtcod.random_get_int(game.rnd, 8, 15)
		if self.wisdom > 9:
			self.skill_points += (self.wisdom - 10) / 3
		else:
			self.skill_points += (self.wisdom - 12) / 3
		game.message.new('You have ' + str(self.skill_points) + ' skill points to spend.', game.turns, libtcod.light_fuchsia)
		self.base_health += hp_increase
		self.base_mana += mp_increase
		self.base_stamina += stamina_increase
		self.health += hp_increase
		self.mana += mp_increase
		self.stamina += stamina_increase
		self.set_max_health()
		self.set_max_mana()
		self.set_max_stamina()

	# raises your xp
	def gain_xp(self, xp):
		self.xp += xp
		if self.xp >= game.EXPERIENCE_TABLES[self.level]:
			self.gain_level()

	# heals the amount of health
	def heal_health(self, hp):
		old_health = self.health
		self.health += hp
		if self.health > self.max_health:
			self.health = self.max_health
		if old_health < self.health:
			game.hp_anim.append({'x': game.char.x, 'y': game.char.y, 'damage': str(self.health - old_health), 'color': libtcod.green, 'turns': 0, 'icon': game.char.char, 'icon_color': libtcod.green, 'player': True})

	# heals the amount of mana
	def heal_mana(self, mp):
		self.mana += mp
		if self.mana > self.max_mana:
			self.mana = self.max_mana

	# heals the amount of stamina
	def heal_stamina(self, st):
		self.stamina += st
		if self.stamina > self.max_stamina:
			self.stamina = self.max_stamina

	# calculates your health bonus
	def health_bonus(self):
		hb = self.endurance
		hb += self.karma * 0.25
		return int(hb)

	# returns true if player is not touching the ground
	def is_above_ground(self):
		if 'levitate' in self.flags:
			return True
		return False

	# returns true when dead
	def is_dead(self):
		if self.health < 1:
			return True
		return False

	# returns true if player is disabled
	def is_disabled(self):
		if any(i in self.flags for i in ['sleep', 'unconscious']):
			return True
		return False

	# finds out if something in your inventory has expired
	def item_expiration(self):
		for i in range(len(self.inventory) - 1, 0, -1):
			if self.inventory[i].is_expired():
				game.message.new('An item in your inventory just rotted away.', game.turns, libtcod.red)
				self.inventory.pop(i)

	# finds out if an active item in your inventory has expired
	def item_is_active(self):
		for i in range(len(self.inventory) - 1, 0, -1):
			if self.inventory[i].is_active():
				game.message.new('An item in your inventory just rotted away.', game.turns, libtcod.red)
				self.inventory.pop(i)
		for i in range(len(self.equipment) - 1, 0, -1):
			if self.equipment[i].is_active():
				game.message.new('An item in your inventory just rotted away.', game.turns, libtcod.red)
				self.equipment.pop(i)

	# reduce stamina
	def lose_stamina(self, damage):
		self.stamina -= damage
		self.no_stamina(True)

	# calculates your mana bonus
	def mana_bonus(self):
		mb = self.intelligence
		mb += self.wisdom * 0.75
		mb += self.karma * 0.25
		return int(mb)

	# calculates your max carrying capacity
	def max_carrying_capacity(self):
		cc = self.strength * 2.5
		cc += self.endurance * 1.25
		cc += self.karma * 0.5
		return round(cc, 2)

	# check if player has no stamina
	def no_stamina(self, text=False):
		if self.stamina <= 0:
			self.stamina == 0
			if 'unconscious' not in self.flags:
				self.flags.append('unconscious')
				if text:
					game.message.new('You fall unconscious from exaustion!', game.turns)
			return True
		return False

	# calculates your total score
	def score(self):
		score = 0
		score += (self.strength + self.dexterity + self.intelligence + self.wisdom + self.endurance + self.karma) / 5
		score += sum(c.level for c in self.skills) / 20
		score += self.xp / 5
		score += (self.level - 1) * 50
		score += game.turns / 50
		score += len(game.old_maps) * 10
		score += self.mks * 10
		return score

	# set your max health
	def set_max_health(self):
		self.max_health = self.base_health + self.health_bonus()
		if self.health > self.max_health:
			self.health = self.max_health

	# set your max mana
	def set_max_mana(self):
		self.max_mana = self.base_mana + self.mana_bonus()
		if self.mana > self.max_mana:
			self.mana = self.max_mana

	# set your max stamina
	def set_max_stamina(self):
		self.max_stamina = self.base_stamina + self.stamina_bonus()
		if self.stamina > self.max_stamina:
			self.stamina = self.max_stamina

	# calculates your stamina bonus
	def stamina_bonus(self):
		sb = self.strength
		sb += self.endurance * 0.75
		sb += self.dexterity * 0.5
		sb += self.karma * 0.25
		return int(sb)

	# stat gain when you raise a level
	def stat_gain(self, st, dx, iq, wi, en):
		fate = util.roll_dice(1, 100)
		msg = 'You gain '
		if fate <= st:
			self.strength += 1
			self.base_strength += 1
			msg += 'strength!'
		elif fate <= st + dx:
			self.dexterity += 1
			self.base_dexterity += 1
			msg += 'dexterity!'
		elif fate <= st + dx + iq:
			self.intelligence += 1
			self.base_intelligence += 1
			msg += 'intelligence!'
		elif fate <= st + dx + iq + wi:
			self.wisdom += 1
			self.base_wisdom += 1
			msg += 'wisdom!'
		elif fate <= st + dx + iq + wi + en:
			self.endurance += 1
			self.base_endurance += 1
			msg += 'endurance!'
		game.message.new(msg, game.turns, libtcod.light_fuchsia)

	# calculates stats bonuses
	def stats_bonus(self):
		self.strength = self.base_strength
		self.dexterity = self.base_dexterity
		self.intelligence = self.base_intelligence
		self.wisdom = self.base_wisdom
		self.endurance = self.base_endurance
		self.karma = self.base_karma
		self.set_max_health()
		self.set_max_mana()
		self.set_max_stamina()

		for i in range(len(self.equipment)):
			if 'str_bonus' in self.equipment[i].flags:
				self.strength += self.equipment[i].bonus
			if 'dex_bonus' in self.equipment[i].flags:
				self.dexterity += self.equipment[i].bonus
			if 'int_bonus' in self.equipment[i].flags:
				self.intelligence += self.equipment[i].bonus
			if 'wis_bonus' in self.equipment[i].flags:
				self.wisdom += self.equipment[i].bonus
			if 'end_bonus' in self.equipment[i].flags:
				self.endurance += self.equipment[i].bonus

			if 'health_bonus1' in self.equipment[i].flags:
				if self.equipment[i].bonus == 0:
					self.equipment[i].bonus = util.roll_dice(1, 6)
				self.max_health += self.equipment[i].bonus
			if 'mana_bonus1' in self.equipment[i].flags:
				if self.equipment[i].bonus == 0:
					self.equipment[i].bonus = util.roll_dice(1, 6)
				self.max_mana += self.equipment[i].bonus
			if 'stamina_bonus1' in self.equipment[i].flags:
				if self.equipment[i].bonus == 0:
					self.equipment[i].bonus = util.roll_dice(1, 6)
				self.max_stamina += self.equipment[i].bonus

	# reduce your health
	def take_damage(self, damage, source):
		self.health -= damage
		game.hp_anim.append({'x': game.char.x, 'y': game.char.y, 'damage': str(damage), 'color': libtcod.red, 'turns': 0, 'icon': game.char.char, 'icon_color': libtcod.red, 'player': True})
		if self.is_dead():
			game.message.new('You die...', game.turns, libtcod.light_orange)
			game.message.new('*** Press space ***', game.turns)
			game.killer = source
			game.game_state = 'death'
		elif source != 'poison':
			if "sleep" in self.flags:
				game.message.new('You wake up.', game.turns)
				self.flags.remove('sleep')

	# unequip an item
	def unequip(self, item):
		self.inventory.append(self.equipment[item])
		game.message.new('You unequip the ' + self.equipment[item].get_name() + '.', game.turns, libtcod.red)
		self.equipment.pop(item)
		self.stats_bonus()
		game.player_move = True

	# return carried weight
	def weight_carried(self):
		weight = sum(item.weight for item in self.inventory)
		weight += sum(item.weight for item in self.equipment)
		return round(weight, 2)


class Skill(object):
	def __init__(self, name, cat, level, xp, can_use=False, flag=None):
		self.name = name
		self.category = cat
		self.level = level
		self.base_level = level
		self.xp = xp
		self.can_use = can_use
		self.flag = flag
		self.temp = 0

	# set a skill active
	def active(self):
		if not self.can_use:
			game.message.new("You can't use this skill that way.", game.turns)
		elif self.flag in game.player.flags:
			game.player.flags.remove(self.flag)
			game.message.new('The ' + self.name + ' skill is now inactive.', game.turns)
		else:
			game.player.flags.append(self.flag)
			game.message.new('The ' + self.name + ' skill is now active.', game.turns)

	# raises your skill level
	def gain_level(self):
		if self.level < 100:
			self.level += 1
			self.base_level += 1
			self.xp = 0
			game.message.new('Your ' + self.name + ' skill increased to ' + str(self.level) + '!', game.turns, libtcod.light_green)

	# raises your skill xp
	def gain_xp(self, xp):
		if self.level < 100:
			self.xp += xp
			if self.xp >= (self.level + 1) * 5:
				self.xp = 0
				self.level += 1
				self.base_level += 1
				game.message.new('Your ' + self.name + ' skill increased to ' + str(self.level) + '!', game.turns, libtcod.light_green)

	# set skill level
	def set_level(self, level):
		self.level = level
		self.base_level = level


class Time(object):
	def __init__(self):
		self.day = libtcod.random_get_int(game.rnd, 1, 30)
		self.month = libtcod.random_get_int(game.rnd, 1, 12)
		self.year = libtcod.random_get_int(game.rnd, 500, 1000)
		self.hour = 12
		self.minute = 0

	# update the game time
	def update(self, min=1):
		self.minute += min
		if self.minute >= 60:
			self.minute -= 60
			self.hour += 1
		if self.hour >= 24:
			self.hour -= 24
			self.day += 1
		if self.day > 30:
			self.day -= 30
			self.month += 1
		if self.month > 12:
			self.month -= 12
			self.year += 1
		game.player.check_hunger_level(min)

	# returns a formatted string of the game time
	def time_to_text(self):
		if self.hour > 11:
			self.hour = self.hour - 12
			if self.hour == 0:
				self.hour = 12
			time = str(self.hour) + ':' + str(self.minute).rjust(2, '0') + ' pm'
		else:
			if self.hour == 0:
				self.hour = 12
			time = str(self.hour) + ':' + str(self.minute).rjust(2, '0') + ' am'
		if self.day == 1:
			suffix = 'st'
		elif self.day == 2:
			suffix = 'nd'
		elif self.day == 3:
			suffix = 'rd'
		else:
			suffix = 'th'
		string = 'The time is ' + time
		string += ', on the ' + str(self.day) + suffix + ' day of the month of the ' + game.months[self.month - 1]
		string += ', in the year ' + str(self.year)
		return string
