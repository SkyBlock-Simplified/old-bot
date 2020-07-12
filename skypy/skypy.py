from skypy.constants.pets import *
from skypy.constants.constants import *
from skypy.constants.slayer import *
from skypy.exceptions import *

# API Calls
import aiohttp
import asyncio
from datetime import datetime
import time
# --------

_session = None

async def session():
	global _session
	if _session is None:
		_session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=3), raise_for_status=True)
	return _session

import re
from collections import defaultdict

# Inventory parsing
from base64 import b64decode as one
from gzip import decompress as two
from io import BytesIO as three
from struct import unpack
# -----------------

def decode_inventory_data(raw, player=None, backpack=False):
	"""Takes a raw string representing inventory data.
	Returns a json object with the inventory's contents"""

	if backpack:
		raw = three(two(raw))
	else:
		raw = three(two(one(raw)))	# Unzip raw string from the api

	def read(type, length):
		if type in 'chil':
			return int.from_bytes(raw.read(length), byteorder='big')
		if type == 's':
			return raw.read(length).decode('utf-8')
		return unpack(f'>{type}', raw.read(length))[0]

	def parse_list():
		subtype = read('c', 1)
		payload = []
		for _ in range(read('i', 4)):
			parse_next_tag(payload, subtype)
		return payload

	def parse_compound():
		payload = {}
		while parse_next_tag(payload) != 0:	 # Parse tags until we find an endcap (type == 0)
			pass  # Nothing needs to happen here
		return payload

	payloads = {
		1: lambda: read('c', 1),  # Byte
		2: lambda: read('h', 2),  # Short
		3: lambda: read('i', 4),  # Int
		4: lambda: read('l', 8),  # Long
		5: lambda: read('f', 4),  # Float
		6: lambda: read('d', 8),  # Double
		7: lambda: raw.read(read('i', 4)),	# Byte Array
		8: lambda: read('s', read('h', 2)),	 # String
		9: parse_list,	# List
		10: parse_compound,	 # Compound
		11: lambda: [read('i', 4) for _ in range(read('i', 4))],  # Int Array
		12: lambda: [read('l', 8) for _ in range(read('i', 4))]	 # Long Array
	}

	def parse_next_tag(dictionary, tag_id=None):
		if tag_id is None:	# Are we inside a list?
			tag_id = read('c', 1)
			if tag_id == 0:	 # Is this the end of a compound?
				return 0
			name = read('s', read('h', 2))

		payload = payloads[tag_id]()
		if isinstance(dictionary, dict):
			dictionary[name] = payload
		else:
			dictionary.append(payload)

	raw.read(3)	 # Remove file header (we ingore footer)
	root = {}
	parse_next_tag(root)

	return [Item(x, i, player) for i, x in enumerate(root['i']) if x and 'tag' in x and 'ExtraAttributes' in x['tag']]

def level_from_xp_table(xp, table):
	"""Takes a list of xp requirements and a xp value.
	Returns whatever level the thing should be at"""

	for level, requirement in enumerate(table):
		if requirement > xp:
			break
	else:
		level += 1
	return level

class Item:
	def __init__(self, nbt, slot_number=0, player=None):
		self._nbt = nbt
		self.player = player

		self.stack_size = self._nbt.get('Count', 1)
		self.slot_number = slot_number

		tag = nbt.get('tag', {})
		extras = tag.get('ExtraAttributes', {})

		self.description = tag.get('display', {}).get('Lore', [])
		self.description_clean = [re.sub('§.[a-z]?', '', line) for line in self.description]
		self.description = '\n'.join(self.description)
		self.internal_name = extras.get('id', None)
		name = self.internal_name if self.internal_name else None
		self.hot_potatos = extras.get('hot_potato_count', 0)
		self.collection_date = extras.get('timestamp', '') # 'timestamp': '2/16/20 9:24 PM',
		self.runes = extras.get('runes', {}) # 'runes': {'ZOMBIE_SLAYER': 3},
		self.enchantments = extras.get('enchantments', {})
		self.reforge = extras.get('modifier', None)
		self.dungeon = False

		if self.description_clean:
			rarity_type = self.description_clean[-1].split()
			self.rarity = rarity_type[0].lower()
			self.type = rarity_type[2].lower() if len(rarity_type) > 2 else rarity_type[1].lower() if len(rarity_type) > 1 else None
			self.dungeon = True if len(rarity_type) > 2 and rarity_type[1].lower() == 'dungeon' else False

			if self != 'ENCHANTED_BOOK':
				for type, list in {'fishing rod': rod_enchants, 'bow': bow_enchants, 'sword': sword_enchants}.items():
					for e in list:
						if e in self.enchantments and e != 'looting' and e != 'dragon_hunter':
							self.type = type
							break
		else:
			self.rarity = None
			self.type = None

		self.name = re.sub('§.', '', self['tag']['display']['Name'])

		#Stats
		self.stats = Stats({})
		self.base_stats = Stats({})

		#Parse items from cake bag and backpacks
		self.contents = None
		if name:
			if name == 'NEW_YEAR_CAKE_BAG' or name.endswith('_BACKBACK'):
				for k, v in extras.items():
					if k == 'new_year_cake_bag_data' or k.endswith('_backpack_data'):
						self.contents = decode_inventory_data(v, player, backpack=True)
						break

			if name == 'RECLUSE_FANG':
				self.stats.__iadd__('strength', 370)
			elif name == 'POOCH_SWORD':
				self.stats.__iadd__('strength', 150)
			elif name == 'THE_SHREDDER':
				self.stats.__iadd__('damage', 115)
				self.stats.__iadd__('strength', 15)
			elif name == 'NIGHT_CRYSTAL' or name == 'DAY_CRYSTAL':
				self.stats.__iadd__('strength', 2.5)
				self.stats.__iadd__('defense', 2.5)
			elif name == 'NEW_YEAR_CAKE_BAG':
				self.stats.__iadd__('health', len(self.contents) if self.contents else 0)
			elif name == 'GRAVITY_TALISMAN':
				self.stats.__iadd__('strength', 10)
				self.stats.__iadd__('defense', 10)
			elif name == 'SPEED_TALISMAN':
				self.stats.__iadd__('speed', 1)
			elif name == 'SPEED_RING':
				self.stats.__iadd__('speed', 3)
			elif name == 'SPEED_ARTIFACT':
				self.stats.__iadd__('speed', 5)
			elif name == 'CAT_TALISMAN':
				self.stats.__iadd__('speed', 1)
			elif name == 'LYNX_TALISMAN':
				self.stats.__iadd__('speed', 2)
			elif name == 'CHEETAH_TALISMAN':
				self.stats.__iadd__('speed', 3)
			# elif name == 'PARTY_HAT_CRAB':
				# Get Intelligence base on how long player played (tbd)
			elif name == 'PIGMAN_SWORD':
				self.stats.__iadd__('defense', 50)
			elif self.player:
				# if name == 'POOCH_SWORD' and self.player.weapon == 'POOCH_SWORD':
				# 	self.stats.modifiers['damage'].insert(0, lambda stat: stat + player.stats['health'] // 50)
				if re.match('MUSHROOM_(HELMET|CHESTPLATE|LEGGINGS|BOOTS)', name) and self.player.armor == {'helmet': 'MUSHROOM_HELMET', 'chestplate': 'MUSHROOM_CHESTPLATE', 'leggings': 'MUSHROOM_LEGGINGS', 'boots': 'MUSHROOM_BOOTS'}:
					self.stats.multiplier *= 3
				elif re.match('END_(HELMET|CHESTPLATE|LEGGINGS|BOOTS)', name) and self.player.armor == {'helmet': 'END_HELMET', 'chestplate': 'END_CHESTPLATE', 'leggings': 'END_LEGGINGS', 'boots': 'END_BOOTS'}:
					self.stats.multiplier *= 2
				elif re.match('BAT_PERSON_(HELMET|CHESTPLATE|LEGGINGS|BOOTS)', name) and self.player.armor == {'helmet': 'BAT_PERSON_HELMET', 'chestplate': 'BAT_PERSON_CHESTPLATE', 'leggings': 'BAT_PERSON_LEGGINGS', 'boots': 'BAT_PERSON_BOOTS'}:
					self.stats.multiplier *= 3
				elif re.match('SNOW_SUIT_(HELMET|CHESTPLATE|LEGGINGS|BOOTS)', name) and self.player.armor == {'helmet': 'SNOW_SUIT_HELMET', 'chestplate': 'SNOW_SUIT_CHESTPLATE', 'leggings': 'SNOW_SUIT_LEGGINGS', 'boots': 'SNOW_SUIT_BOOTS'}:
					self.stats.multiplier *= 2

		if self.reforge == 'renowned' and player:
			player.stats.multiplier += 0.01

		r = re.compile('([\w ]*): \+(\d*\.?\d*)(.*)')
		r_r = re.compile('.*\(([\w ]*) \+(\d*)')

		for line in self.description_clean:
			match = r.match(line)
			if match:
				self.stats['attack speed' if match[1].lower() == 'bonus attack speed' else match[1].lower()] = float(match[2])
				match_r = r_r.match(match.group(3))
				reforge_stat = float(match_r[2]) if match_r else 0
				if float(match[2]) - reforge_stat == 0:
					continue
				self.base_stats['attack speed' if match[1].lower() == 'bonus attack speed' else match[1].lower()] = float(match[2]) - reforge_stat

	def __getitem__(self, name):
		return self._nbt[name]

	def __eq__(self, other):
		return self.internal_name == (other if isinstance(other, str) else other.internal_name)

	def __str__(self):
		return self.name

	def __repr__(self):
		return f"'{self.internal_name}'"

def damage(weapon_dmg, strength, crit_dmg, ench_modifier):
	return (5 + weapon_dmg + strength // 5) * (1 + strength / 100) * (1 + crit_dmg / 100) * (1 + ench_modifier / 100)

async def fetch_uuid_uname(uname_or_uuid):
	s = await session()

	try:
		async with s.get(f'https://api.mojang.com/users/profiles/minecraft/{uname_or_uuid}') as r:

			json = await r.json(content_type=None)
			if json is None:

				async with s.get(f'https://api.mojang.com/user/profiles/{uname_or_uuid}/names') as r:
					json = await r.json(content_type=None)
					if json is None:
						raise BadNameError(uname_or_uuid, 'Malformed uuid or username') from None

					return json[-1]['name'], uname_or_uuid

			return json['name'], json['id']
	except asyncio.TimeoutError:
		raise ExternalAPIError('Could not connect to https://api.mojang.com') from None
	except aiohttp.ClientResponseError:
		raise BadNameError(uname_or_uuid, 'Can\'t get player name or uuid')

class Pet:
	def __init__(self, nbt):
		self._nbt = nbt
		self.xp = nbt.get('exp', 0)
		self.active = nbt.get('active', False)
		self.rarity = nbt.get('tier', 'COMMON').lower()
		self.item_internal_name = nbt.get('heldItem', None)
		if self.item_internal_name:
			self.item_name = ' '.join([
				s.capitalize() for s in
				re.sub('_COMMON|_UNCOMMON|_RARE|_EPIC|_LEGENDARY', '', self.item_internal_name[9:]).split('_')
			])
			if self.item_name == 'Tier Boost':
				self.rarity = pet_rarity[pet_rarity.index(self.rarity) + 1]
		else:
			self.item_name = None
		self.internal_name = nbt.get('type', 'BEE')
		self.level = level_from_xp_table(self.xp, pet_xp[self.rarity])
		self.name = pets[self.internal_name]['name']
		self.title = f'[Lvl {self.level}] {self.name}'
		self.xp_remaining = pet_xp[self.rarity][-1] - self.xp
		self.candy_used = nbt.get('candyUsed', 0)
		self.stats = Stats({stat: function(self.level) for stat, function in pets[self.internal_name]['stats'].items()})

		if self.item_name:
			if self.item_name == 'Textbook':
				self.stats.modifiers['intelligence'].append(lambda stat: stat * 2)
			elif self.item_name == 'Hardened Scales':
				self.stats.__iadd__('defense', 25)
			elif self.item_name == 'Iron Claws':
				self.stats.modifiers['crit chance'].append(lambda stat: stat * 1.4)
				self.stats.modifiers['crit damage'].append(lambda stat: stat * 1.4)
			elif self.item_name == 'Sharpened Claws':
				self.stats.__iadd__('crit damage', 15)
			elif self.item_name == 'Big Teeth':
				self.stats.__iadd__('crit chance', 5)
			elif self.item_name == 'Lucky Clover':
				self.stats.__iadd__('magic find', 7)

	def __str__(self):
		return self.name

	def __repr__(self):
		return f"'{self.internal_name}'"

class Stats:
	# A list of stats that are unaffected by global multipliers
	statics = ['speed cap', 'enchantment modifier', 'ability damage', 'gear score']

	def __init__(self, args={}):
		self._dict = args
		self.multiplier = 1
		self.modifiers = defaultdict(list)
		self.children = []
		self.base_children = []

	def __getitem__(self, key):
		if isinstance(key, str):
			base = self._dict.get(key, 0) + sum(c[key] for t, c in self.children)
			for f in self.modifiers[key]:
				base = f(base)
			return base if key in Stats.statics else base * self.multiplier
		else:
			raise TypeError

	def __iadd__(self, other, value=None):
		if isinstance(other, Stats):
			for k, v in other:
				self[k] += v
		elif isinstance(other, str) and isinstance(value, (int, float)):
			if other in self._dict:
				self._dict[other] += value
			else:
				self._dict[other] = value
		else:
			raise NotImplementedError
		return self

	def __setitem__(self, key, value):
		if isinstance(value, (int, float)):
				self._dict[key] = value
		else:
			raise ValueError

	def __str__(self):
		return str(self._dict)

	def __repr__(self):
		return str(self._dict)

	def __len__(self):
		return len(self._dict)

	def get_stats_with_base(self, key):
		if isinstance(key, str):
			base = self._dict.get(key, 0) + sum(self.children[i][1].multiplier*c[key] for i, (t, c) in enumerate(self.base_children))
			for f in self.modifiers[key]:
				base = f(base)
			return base if key in Stats.statics else base * self.multiplier
		else:
			raise TypeError

	def get_raw_base_stats(self, key):
		if isinstance(key, str):
			return self._dict.get(key, 0) + sum(self.children[i][1].multiplier*c[key] for i, (t, c) in enumerate(self.base_children))
		else:
			raise TypeError

	@staticmethod
	def _gen(cls):
		for k in cls._dict.keys():
			yield k, cls[k]

	def __iter__(self):
		return Stats._gen(self)

class ApiInterface:
	def __next_key__(self):
		self.__key_id__ += 1
		if self.__key_id__ == len(self._api_keys):
			self.__key_id__ = 0
		return self._api_keys[self.__key_id__]

	async def __call_api__(self, api, **kwargs):
		kwargs['key'] = self.__next_key__()
		url = f'https://api.hypixel.net{api}'

		try:
			async with (await session()).get(url, params=kwargs) as data:
				data = await data.json(content_type=None)

				if data['success']:
					return data

				elif data['cause'] == 'Invalid API key!':
					raise APIKeyError(kwargs["key"], f'Invalid API key!')

				else:
					raise ExternalAPIError(data['cause'])

		except asyncio.TimeoutError:
			return await self.__call_api__(api, **kwargs)

		except aiohttp.ClientResponseError as e:
			if e.status == 403:
				raise HypixelError(f'Your request to {url} was not granted')

			elif e.status == 429:
				raise HypixelError('You are being ratelimited')

			elif e.status == 500:
				raise HypixelError('Hypixel\'s servers could not complete your request')

			elif e.status == 502:
				raise HypixelError('Hypixel\'s API is currently not working. Please try again in a few minutes.')

			else:
				raise e from None

	async def __new__(cls, keys, *args, **kwargs):
		instance = super().__new__(cls)

		if isinstance(keys, str):
			instance._api_keys = [keys]
		else:
			instance._api_keys = keys

		instance.__key_id__ = 0

		await instance.__init__(*args, **kwargs)
		return instance

class Player(ApiInterface):
	"""A class representing a Skyblock player.
	Instantiate the class with Player(api_key, username) or Player(api_key, uuid)
	Use profiles() and set_profile() to retrieve and define all the profile data.
	Use weapons() and set_weapon() to retrieve and set the player's weapon."""

	async def __init__(self, *, uname=None, uuid=None, guild=False, _profiles=None, _achivements=None):
		self.online=False
		if uname and uuid:
			self.uname = uname
			self.uuid = uuid
		elif uname and not uuid:
			self.uname, self.uuid = await fetch_uuid_uname(uname)
		elif uuid and not uname:
			self.uname, self.uuid = await fetch_uuid_uname(uuid)
		else:
			raise DataError('You need to provide either a minecraft username or uuid!')

		if _profiles and _achivements:
			self.profiles = _profiles
			self.achievements = _achivements
		else:
			try:
				self.profiles = {}
				player = await self.__call_api__('/player', uuid=self.uuid)
				profile_ids = player['player']['stats']['SkyBlock']['profiles']
				player_data = player['player']
				self.online = player_data['lastLogout'] < player_data['lastLogin']

				self.achievements = player['player']['achievements']

				for k, v in profile_ids.items():
					self.profiles[v['cute_name']] = k

			except (KeyError, TypeError):
				raise NeverPlayedSkyblockError(self.uname) from None
			if not self.profiles:
				raise NeverPlayedSkyblockError(self.uname)

		if guild:
			id = (await self.__call_api__('/findGuild', byUuid=self.uuid))['guild']
			if id:
				self.guild_id = id
				self.guild_info = (await self.__call_api__('/guild', id=self.guild_id))['guild']
				self.guild = self.guild_info['name']
			else:
				self.guild_id = None
				self.guild_info = None
				self.guild = None

		self._profile_set = False

	def __str__(self):
		return self.uname

	def __repr__(self):
		return f"'{self.uname}'"

	def avatar(self, size=None):
		if size:
			return f'https://mc-heads.net/avatar/{self.uuid}/{size}'
		else:
			return f'https://mc-heads.net/avatar/{self.uuid}'

	async def set_profile_automatically(self, attribute=lambda player: player.total_slayer_xp, threshold=None):
		"""Sets a player profile automatically
		<attribute> is a function that takes a <Player> class and returns whatever value you want to set it based on
		example: player.set_profile_automatically(lambda player: player.skill_xp['combat'])"""
		best = None
		max = 0

		async def create_canadate(profile):
			player = await Player(
				self._api_keys,
				uname=self.uname,
				uuid=self.uuid,
				_profiles=self.profiles,
				_achivements=self.achievements
			)
			await player.set_profile(profile)
			return player

		profile_ids = list(self.profiles.values())

		if threshold:
			best = profile_ids[0]
			for profile in reversed(profile_ids):
				try:
					canidate = await create_canadate(profile)
				except HypixelError:
					continue

				if attribute(canidate) >= threshold:
					best = profile
					break
		else:
			for canidate in asyncio.as_completed([create_canadate(profile) for profile in profile_ids]):
				try:
					canidate = await canidate
					current = attribute(canidate)
					if best is None or current > max:
						max = current
						best = canidate.profile
				except HypixelError:
					pass

		await self.set_profile(best)

	@staticmethod
	def _parse_collection(v, data):
		try:
			tuples = []
			for s in v[data]:
				temp = re.split('_(?!.*_)', s, maxsplit=1)
				temp[1] = int(temp[1])
				tuples.append(temp)
			dictionary = {}
			for s in set(name for name, level in tuples):
				max = 0
				for name, level in tuples:
					if name == s and level > max:
						max = level
				dictionary[s.lower().replace('_', ' ')] = max
			return dictionary
		except KeyError:
			return {}

	async def set_profile(self, profile):
		"""Sets a player's profile based on the provided profile ID"""

		if self._profile_set:
			raise DataError('This player already has their profile set!')
		self._profile_set = True

		self.profile = profile
		for cute_name, id in self.profiles.items():
			if id == profile:
				self.profile_name = cute_name
				break
		else:
			raise DataError('Bad profile ID!')

		self._nbt = (await self.__call_api__('/skyblock/profile', profile=self.profile))['profile']
		self.enabled_api = {'skills': False, 'collection': False, 'inventory': False, 'banking': False}

		v = self._nbt['members'][self.uuid]

		def parse_inventory(v, *path):
			try:
				result = v
				for key in path:
					result = result[key]
				return decode_inventory_data(result, self)
			except KeyError:
				return []

		#Loads a player's numeric stats
		self.stats = Stats(base_player_stats.copy())

		#Loads all of a player's inventories
		self.armor = {'helmet': None, 'chestplate': None, 'leggings': None, 'boots': None}
		for armor in parse_inventory(v, 'inv_armor', 'data'):
			if armor.type == 'hatccessory':
				self.armor['helmet'] = armor
			else:
				self.armor[armor.type] = armor
		self.inventory = parse_inventory(v, 'inv_contents', 'data')
		self.echest = parse_inventory(v, 'ender_chest_contents', 'data')
		self.weapons = [item for item in self.inventory + self.echest if item.type in ('sword', 'bow', 'fishing rod')]
		self.candy_bag = parse_inventory(v, 'candy_inventory_contents', 'data')
		self.talisman_bag = parse_inventory(v, 'talisman_bag', 'data')
		self.potion_bag = parse_inventory(v, 'potion_bag', 'data')
		self.fish_bag = parse_inventory(v, 'fishing_bag', 'data')
		self.quiver = parse_inventory(v, 'quiver', 'data')
		self.wardrobe = parse_inventory(v, 'wardrobe_contents', 'data')

		if self.inventory or self.echest or self.talisman_bag:
			self.enabled_api['inventory'] = True

		self.talismans = [talisman for talisman in self.inventory + self.talisman_bag if talisman.type in ('accessory', 'hatccessory')]

		talismans_dup = []

		for talisman in self.talismans:
			talisman.active = True
			# Check for duplicate talismans
			if self.talismans.count(talisman) > 1:
				talisman.active = False
				if not talisman in talismans_dup:
					talismans_dup.append(talisman)
				continue

			# Check for talisman families
			if talisman.internal_name in tiered_talismans:
				for other in tiered_talismans[talisman.internal_name]:
					if other in self.talismans:
						talisman.active = False
						break

		for talisman in talismans_dup:
			talisman.active=True

		#Loads a player's minion slots and collections
		try:
			self.collections = {name.lower().replace('_', ' '): level for name, level in v['collection'].items()}
			self.enabled_api['collection'] = True

		except KeyError:
			self.collections = {}

		self.unlocked_collections = Player._parse_collection(v, 'unlocked_coll_tiers')
		self.minions = Player._parse_collection(v, 'crafted_generators')

		self.unique_minions = max(
			self.achievements.get('skyblock_minion_lover', 0),
			sum(self.minions.values())
		)

		self.minion_slots = level_from_xp_table(self.unique_minions, minion_slot_requirements)

		#Loads a player's skill and slayer data
		if 'experience_skill_farming' in v:
			self.enabled_api['skills'] = True

			self.skill_xp = {}
			self.skills = {}

			for skill in skills:
				xp = int(v.get(f'experience_skill_{skill}', 0))
				self.skill_xp[skill] = xp
				self.skills[skill] = level_from_xp_table(
					xp,
					runecrafting_xp_requirements if skill == 'runecrafting' else skill_xp_requirements
				)
		else:
			self.enabled_api['skills'] = False

			self.skill_xp = {
				'carpentry': 0,
				'runecrafting': 0
			}
			self.skills = {
				'carpentry': 0,
				'runecrafting': 0
			}

			for skill, achievement in [
					('farming', 'skyblock_harvester'),
					('mining', 'skyblock_excavator'),
					('foraging', 'skyblock_gatherer'),
					('combat', 'skyblock_combat'),
					('enchanting', 'skyblock_augmentation'),
					('alchemy', 'skyblock_concoctor'),
					('fishing', 'skyblock_angler'),
					('taming', '')
				]:

				level = self.achievements.get(achievement, 0)
				self.skills[skill] = level
				self.skill_xp[skill] = 0 if level == 0 else skill_xp_requirements[level - 1]

		self.skill_average = sum(self.skills[skill] for skill in skills if skill not in cosmetic_skills) / (len(skills) - len(cosmetic_skills))

		self.slayer_xp = {}
		self.slayers = {}
		for slayer in slayers:
			xp = v.get('slayer_bosses', {}).get(slayer, {}).get('xp', 0)
			self.slayer_xp[slayer] = xp
			self.slayers[slayer] = level_from_xp_table(xp, slayer_level_requirements[slayer])

		self.total_slayer_xp = sum(self.slayer_xp.values())

		#Loads a player's kills and deaths
		self.kills = int(v.get('stats', {'kills': 0}).get('kills', 0))
		self.specifc_kills = {name.replace('kills_', '').replace('_', ' '): int(amount)
							  for name, amount in v['stats'].items() if re.match('kills_', name)}
		self.deaths = int(v.get('stats', {'deaths': 0}).get('deaths', 0))
		self.specifc_deaths = {name.replace('deaths_', '').replace('_', ' '): int(amount)
							   for name, amount in v['stats'].items() if re.match('deaths_', name)}

		#Loads a player's bank balance and purse
		if 'banking' in self._nbt:
			self.enabled_api['banking'] = True
			self.bank_balance = float(self._nbt['banking'].get('balance', 0))
		else:
			self.bank_balance = 0

		self.purse = float(self._nbt['members'][self.uuid].get('coin_purse', 0))

		#Loads a player's misc stats
		self.join_date = datetime.fromtimestamp(v.get('first_join', 0) / 1000.0)
		self.fairy_souls = v.get('fairy_souls_collected', 0)

		for slayer, level in self.slayers.items():
			self.stats += Stats(slayer_rewards[slayer][level])

		for skill, level in self.skills.items():
			self.stats += Stats(skill_rewards[skill][level])

		self.stats.__iadd__('health', fairy_soul_hp_bonus[self.fairy_souls // 5])
		self.stats.__iadd__('defense', self.fairy_souls // 5 + self.fairy_souls // 25)
		self.stats.__iadd__('strength', self.fairy_souls // 5 + self.fairy_souls // 25)
		self.stats.__iadd__('speed', self.fairy_souls // 50)

		self.stats.children = [(p.type, p.stats) for p in self.armor.values() if p] + [(t.type, t.stats) for t in self.talismans if t.active]
		self.stats.base_children = [(p.type, p.base_stats) for p in self.armor.values() if p]\
								   + [(t.type, t.base_stats) for t in self.talismans if t.active]

		#Set Bonuses
		if self.armor == {'helmet': 'SUPERIOR_DRAGON_HELMET', 'chestplate': 'SUPERIOR_DRAGON_CHESTPLATE', 'leggings': 'SUPERIOR_DRAGON_LEGGINGS', 'boots': 'SUPERIOR_DRAGON_BOOTS'}:
			self.stats.multiplier += 0.05
		# elif self.armor == {'helmet': 'YOUNG_HELMET', 'chestplate': 'YOUNG_CHESTPLATE', 'leggings': 'YOUNG_LEGGINGS', 'boots': 'YOUNG_BOOTS'}: #name maybe wrong check later
		# 	self.stats.__iadd__('speed cap', 100)
		# elif self.armor == {'helmet': 'MASTIFF_HELMET', 'chestplate': 'MASTIFF_CHESTPLATE', 'leggings': 'MASTIFF_LEGGINGS', 'boots': 'MASTIFF_BOOTS'}:
		# 	self.stats.modifiers['crit damage'].append(lambda stat: stat / 2)
		# 	self.stats.modifiers['health'].append(lambda stat: stat + self.stats['crit damage'] * 50)
		elif self.armor['helmet'] == 'TARANTULA_HELMET':
			self.stats.modifiers['crit damage'].insert(0, lambda stat: stat + self.stats['strength'] / 10)

		#Loads all of a player's pets
		self.pets = []
		self.pet = None
		if 'pets' in v:
			for data in v['pets']:
				pet = Pet(data)
				self.pets.append(pet)
				if pet.active:
					self.pet = pet

		if self.pet:
			self.stats.children.append((self.pet.internal_name, self.pet.stats))
			self.stats.base_children.append((self.pet.internal_name, self.pet.stats))

	def set_weapon(self, weapon):
		self.weapon = weapon
		self.stats.children.append((weapon.type, weapon.stats))
		self.stats.base_children.append((weapon.type, weapon.base_stats))

		if self.pet:
			pet_ability = pets[self.pet.internal_name]['ability']
			if callable(pet_ability):
				pet_ability(self)

	async def is_online(self):
		player_data = (await self.__call_api__('/player', uuid=self.uuid))['player']
		return player_data['lastLogout'] < player_data['lastLogin']

	async def auctions(self):
		r = await self.__call_api__('/skyblock/auction', uuid=self.uuid, profile=self.profile)

		return [
			{
				'item': decode_inventory_data(auction['item_bytes']['data'])[0],
				'start': auction['start'],
				'end': auction['end'],
				'starting_bid': auction['starting_bid'],
				'highest_bid': auction['highest_bid_amount'],
				'bids': auction['bids'],
				'buyer': auction['bids'][-1]['bidder'] if auction['bids'] else None
			}
			for auction in r['auctions']
			if auction['claimed'] is False
		]
