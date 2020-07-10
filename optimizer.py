import os
from pyomo.environ import *
from pyomo.opt import *

SCIP_TIMELIMIT = os.getenv('SCIP_TIMELIMIT', 4)

damage_reforges = {
    'sword': {
        'legendary': {
            'common': {'strength': 3, 'crit chance': 5, 'crit damage': 5, 'intelligence': 5, 'attack speed': 2},
            'uncommon': {'strength': 7, 'crit chance': 7, 'crit damage': 10, 'intelligence': 8, 'attack speed': 3},
            'rare': {'strength': 12, 'crit chance': 9, 'crit damage': 15, 'intelligence': 12, 'attack speed': 5},
            'epic': {'strength': 18, 'crit chance': 12, 'crit damage': 22, 'intelligence': 18, 'attack speed': 7},
            'legendary': {'strength': 25, 'crit chance': 15, 'crit damage': 28, 'intelligence': 25, 'attack speed': 10},
            'mythic': {'strength': 32, 'crit chance': 18, 'crit damage': 36, 'intelligence': 35, 'attack speed': 15},
            'blacksmith': True
        },
        'spicy': {
            'common': {'strength': 2, 'crit chance': 1, 'crit damage': 25, 'attack speed': 1},
            'uncommon': {'strength': 3, 'crit chance': 1, 'crit damage': 35, 'attack speed': 2},
            'rare': {'strength': 4, 'crit chance': 1, 'crit damage': 45, 'attack speed': 4},
            'epic': {'strength': 7, 'crit chance': 1, 'crit damage': 60, 'attack speed': 7},
            'legendary': {'strength': 10, 'crit chance': 1, 'crit damage': 80, 'attack speed': 10},
            'mythic': {'strength': 12, 'crit chance': 1, 'crit damage': 100, 'attack speed': 15},
            'blacksmith': True
        },
        'epic': {
            'common': {'strength': 15, 'crit damage': 10, 'attack speed': 1},
            'uncommon': {'strength': 20, 'crit damage': 15, 'attack speed': 2},
            'rare': {'strength': 25, 'crit damage': 20, 'attack speed': 4},
            'epic': {'strength': 32, 'crit damage': 27, 'attack speed': 7},
            'legendary': {'strength': 40, 'crit damage': 35, 'attack speed': 10},
            'mythic': {'strength': 50, 'crit damage': 45, 'attack speed': 15},
            'blacksmith': True
        },
        'odd': {
            'common': {'crit chance': 12, 'crit damage': 10, 'intelligence': -5},
            'uncommon': {'crit chance': 15, 'crit damage': 15, 'intelligence': -10},
            'rare': {'crit chance': 15, 'crit damage': 15, 'intelligence': -18},
            'epic': {'crit chance': 25, 'crit damage': 30, 'intelligence': -24},
            'legendary': {'crit chance': 30, 'crit damage': 40, 'intelligence': -36},
            'mythic': {'crit chance': 35, 'crit damage': 50, 'intelligence': -50},
            'blacksmith': True
        },
        'gentle': {
            'common': {'strength': 3, 'attack speed': 8},
            'uncommon': {'strength': 5, 'attack speed': 10},
            'rare': {'strength': 7, 'attack speed': 15},
            'epic': {'strength': 10, 'attack speed': 20},
            'legendary': {'strength': 15, 'attack speed': 25},
            'mythic': {'strength': 20, 'attack speed': 30},
            'blacksmith': True
        },
        'fast': {
            'common': {'attack speed': 10},
            'uncommon': {'attack speed': 20},
            'rare': {'attack speed': 30},
            'epic': {'attack speed': 40},
            'legendary': {'attack speed': 50},
            'mythic': {'attack speed': 60},
            'blacksmith': True
        },
		'fair': {
			'common': {'strength': 2, 'crit chance': 2, 'crit damage': 2, 'intelligence': 2, 'attack speed': 2},
			'uncommon': {'strength': 3, 'crit chance': 3, 'crit damage': 3, 'intelligence': 3, 'attack speed': 3},
			'rare': {'strength': 4, 'crit chance': 4, 'crit damage': 4, 'intelligence': 4, 'attack speed': 4},
			'epic': {'strength': 7, 'crit chance': 7, 'crit damage': 7, 'intelligence': 7, 'attack speed': 7},
			'legendary': {'strength': 10, 'crit chance': 10, 'crit damage': 10, 'intelligence': 10, 'attack speed': 10},
			'mythic': {'strength': 12, 'crit chance': 12, 'crit damage': 12, 'intelligence': 12, 'attack speed': 12},
			'blacksmith': True
		},
		'sharp': {
			'common': {'crit chance': 10, 'crit damage': 20},
			'uncommon': {'crit chance': 12, 'crit damage': 30},
			'rare': {'crit chance': 14, 'crit damage': 40},
			'epic': {'crit chance': 17, 'crit damage': 55},
			'legendary': {'crit chance': 20, 'crit damage': 75},
			'mythic': {'crit chance': 25, 'crit damage': 90},
			'blacksmith': True
		},
		'heroic': {
			'common': {'strength': 15, 'intelligence': 40, 'attack speed': 1},
			'uncommon': {'strength': 20, 'intelligence': 50, 'attack speed': 2},
			'rare': {'strength': 25, 'intelligence': 65, 'attack speed': 2},
			'epic': {'strength': 32, 'intelligence': 80, 'attack speed': 3},
			'legendary': {'strength': 40, 'intelligence': 100, 'attack speed': 5},
			'mythic': {'strength': 50, 'intelligence': 125, 'attack speed': 7},
			'blacksmith': True
		},
        'fabled': {
            # Your Critical hits have a chance to deal up to 20% extra damage (from 100% to 120%, randomly)
            'common': {'strength': 30, 'crit damage': 15},
            'uncommon': {'strength': 35, 'crit damage': 20},
            'rare': {'strength': 40, 'crit damage': 25},
            'epic': {'strength': 50, 'crit damage': 32},
            'legendary': {'strength': 60, 'crit damage': 40},
            'mythic': {'strength': 75, 'crit damage': 50},
            'blacksmith': False
        },
        'suspicious': {
            # Increase wep dmg +15
            'common': {'crit chance': 1, 'crit damage': 30},
            'uncommon': {'crit chance': 2, 'crit damage': 40},
            'rare': {'crit chance': 3, 'crit damage': 50},
            'epic': {'crit chance': 5, 'crit damage': 65},
            'legendary': {'crit chance': 7, 'crit damage': 85},
            'mythic': {'crit chance': 10, 'crit damage': 100},
            'blacksmith': False
        },
    },
    'bow': {
        'awkward': {
            'common': {'crit chance': 10, 'crit damage': 5, 'intelligence': -5},
     		'uncommon': {'crit chance': 12, 'crit damage': 10, 'intelligence': -10},
    		'rare': {'crit chance': 15, 'crit damage': 15, 'intelligence': -18},
    		'epic': {'crit chance': 20, 'crit damage': 22, 'intelligence': -32},
        	'legendary': {'crit chance': 25, 'crit damage': 30, 'intelligence': -50},
        	'mythic': {'crit chance': 30, 'crit damage': 40, 'intelligence': -60},
        	'blacksmith': True
        },
		'rich': {
			'common': {'strength': 2, 'crit chance': 10, 'crit damage': 1, 'intelligence': 20},
			'uncommon': {'strength': 3, 'crit chance': 12, 'crit damage': 2, 'intelligence': 25},
			'rare': {'strength': 4, 'crit chance': 14, 'crit damage': 4, 'intelligence': 30},
			'epic': {'strength': 7, 'crit chance': 17, 'crit damage': 7, 'intelligence': 40},
			'legendary': {'strength': 10, 'crit chance': 20, 'crit damage': 10, 'intelligence': 50},
			'mythic': {'strength': 12, 'crit chance': 25, 'crit damage': 15, 'intelligence': 75},
			'blacksmith': True
		},
        'fine': {
            'common': {'strength': 3, 'crit chance': 5, 'crit damage': 2},
            'uncommon': {'strength': 7, 'crit chance': 7, 'crit damage': 4},
            'rare': {'strength': 12, 'crit chance': 9, 'crit damage': 7},
            'epic': {'strength': 18, 'crit chance': 12, 'crit damage': 10},
            'legendary': {'strength': 25, 'crit chance': 15, 'crit damage': 15},
            'mythic': {'strength': 40, 'crit chance': 20, 'crit damage': 20},
            'blacksmith': True
        },
        'neat': {
            'common': {'crit chance': 10, 'crit damage': 4, 'intelligence': 3},
            'uncommon': {'crit chance': 12, 'crit damage': 8, 'intelligence': 6},
            'rare': {'crit chance': 14, 'crit damage': 14, 'intelligence': 10},
            'epic': {'crit chance': 17, 'crit damage': 20, 'intelligence': 15},
            'legendary': {'crit chance': 20, 'crit damage': 30, 'intelligence': 20},
            'mythic': {'crit chance': 25, 'crit damage': 40, 'intelligence': 30},
            'blacksmith': True
        },
        'hasty': {
            'common': {'strength': 3, 'crit chance': 20},
            'uncommon': {'strength': 5, 'crit chance': 25},
            'rare': {'strength': 7, 'crit chance': 30},
            'epic': {'strength': 10, 'crit chance': 40},
            'legendary': {'strength': 15, 'crit chance': 50},
            'mythic': {'strength': 20, 'crit chance': 60},
            'blacksmith': True
        },
        'grand': {
            'common': {'strength': 25},
            'uncommon': {'strength': 32},
            'rare': {'strength': 40},
            'epic': {'strength': 50},
            'legendary': {'strength': 60},
            'mythic': {'strength': 70},
            'blacksmith': True
        },
        'rapid': {
            'common': {'strength': 2, 'crit damage': 35},
            'uncommon': {'strength': 3, 'crit damage': 45},
            'rare': {'strength': 4, 'crit damage': 55},
            'epic': {'strength': 7, 'crit damage': 65},
            'legendary': {'strength': 10, 'crit damage': 75},
            'mythic': {'strength': 12, 'crit damage': 90},
            'blacksmith': True
        },
        'deadly': {
            'common': {'crit chance': 10, 'crit damage': 5},
            'uncommon': {'crit chance': 13, 'crit damage': 10},
            'rare': {'crit chance': 16, 'crit damage': 18},
            'epic': {'crit chance': 19, 'crit damage': 32},
            'legendary': {'crit chance': 22, 'crit damage': 50},
            'mythic': {'crit chance': 25, 'crit damage': 70},
            'blacksmith': True
        },
        'unreal': {
            'common': {'strength': 3, 'crit chance': 8, 'crit damage': 5},
            'uncommon': {'strength': 7, 'crit chance': 9, 'crit damage': 10},
            'rare': {'strength': 12, 'crit chance': 10, 'crit damage': 18},
            'epic': {'strength': 18, 'crit chance': 11, 'crit damage': 32},
            'legendary': {'strength': 25, 'crit chance': 13, 'crit damage': 50},
            'mythic': {'strength': 34, 'crit chance': 15, 'crit damage': 75},
            'blacksmith': True
        }
    },
    'armor': {
		'smart': {
			'common': {'defense': 4, 'health': 4, 'intelligence': 20},
			'uncommon': {'defense': 6, 'health': 6, 'intelligence': 40},
			'rare': {'defense': 9, 'health': 9, 'intelligence': 60},
			'epic': {'defense': 12, 'health': 12, 'intelligence': 80},
			'legendary': {'defense': 15, 'health': 15, 'intelligence': 100},
			'mythic': {'defense': 20, 'health': 20, 'intelligence': 120},
			'blacksmith': True
		},
		'clean': {
			'common': {'defense': 5, 'health': 5, 'crit chance': 2},
			'uncommon': {'defense': 7, 'health': 7, 'crit chance': 4},
			'rare': {'defense': 10, 'health': 10, 'crit chance': 6},
			'epic': {'defense': 15, 'health': 15, 'crit chance': 8},
			'legendary': {'defense': 20, 'health': 20, 'crit chance': 10},
			'mythic': {'defense': 25, 'health': 25, 'crit chance': 12},
			'blacksmith': True
		},
		'fierce': {
			'common': {'strength': 2, 'crit chance': 2, 'crit damage': 4},
			'uncommon': {'strength': 4, 'crit chance': 3, 'crit damage': 7},
			'rare': {'strength': 6, 'crit chance': 4, 'crit damage': 10},
			'epic': {'strength': 8, 'crit chance': 5, 'crit damage': 14},
			'legendary': {'strength': 10, 'crit chance': 6, 'crit damage': 18},
			'mythic': {'strength': 12, 'crit chance': 8, 'crit damage': 24},
			'blacksmith': True
		},
		'heavy': {
			'common': {'defense': 25, 'speed': -1, 'crit damage': -1},
			'uncommon': {'defense': 35, 'speed': -1, 'crit damage': -2},
			'rare': {'defense': 50, 'speed': -1, 'crit damage': -2},
			'epic': {'defense': 65, 'speed': -1, 'crit damage': -3},
			'legendary': {'defense': 80, 'speed': -1, 'crit damage': -5},
			'mythic': {'defense': 110, 'speed': -1, 'crit damage': -7},
			'blacksmith': True
		},
		'light': {
			'common': {'defense': 1, 'speed': 1, 'health': 5, 'crit chance': 1, 'attack speed': 1, 'crit damage': 1},
			'uncommon': {'defense': 2, 'speed': 2, 'health': 7, 'crit chance': 1,  'attack speed': 2, 'crit damage': 2},
			'rare': {'defense': 3, 'speed': 3, 'health': 10, 'crit chance': 2,  'attack speed': 3, 'crit damage': 3},
			'epic': {'defense': 4, 'speed': 4, 'health': 15, 'crit chance': 2,  'attack speed': 4, 'crit damage': 4},
			'legendary': {'defense': 5, 'speed': 5, 'health': 20, 'crit chance': 2,  'attack speed': 5, 'crit damage': 5},
			'mythic': {'defense': 6, 'speed': 6, 'health': 25, 'crit chance': 3,  'attack speed': 6, 'crit damage': 6},
			'blacksmith': True
		},
		'mythic': {
			'common': {'strength': 2, 'defense': 2, 'speed': 2, 'health': 2, 'crit chance': 1, 'intelligence': 20},
			'uncommon': {'strength': 4, 'defense': 4, 'speed': 2, 'health': 4, 'crit chance': 2, 'intelligence': 25},
			'rare': {'strength': 6, 'defense': 6, 'speed': 2, 'health': 6, 'crit chance': 3, 'intelligence': 30},
			'epic': {'strength': 8, 'defense': 8, 'speed': 2, 'health': 8, 'crit chance': 4, 'intelligence': 40},
			'legendary': {'strength': 10, 'defense': 10, 'speed': 2, 'health': 10, 'crit chance': 5, 'intelligence': 50},
			'mythic': {'strength': 12, 'defense': 12, 'speed': 2, 'health': 12, 'crit chance': 6, 'intelligence': 60},
			'blacksmith': True
		},
		'titanic': {
			'common': {'defense': 10, 'health': 10},
			'uncommon': {'defense': 15, 'health': 15},
			'rare': {'defense': 20, 'health': 20},
			'epic': {'defense': 25, 'health': 25},
			'legendary': {'defense': 35, 'health': 35},
			'mythic': {'defense': 50, 'health': 50},
			'blacksmith': True
		},
		'wise': {
			'common': {'speed': 1, 'health': 6, 'intelligence': 25},
			'uncommon': {'speed': 1, 'health': 8, 'intelligence': 50},
			'rare': {'speed': 1, 'health': 10, 'intelligence': 75},
			'epic': {'speed': 2, 'health': 12, 'intelligence': 100},
			'legendary': {'speed': 2, 'health': 15, 'intelligence': 125},
			'mythic': {'speed': 3, 'health': 20, 'intelligence': 150},
			'blacksmith': True
		},
		'pure': {
			'common': {'strength': 2, 'defense': 2, 'speed': 1, 'health': 2, 'crit chance': 2, 'crit damage': 2, 'intelligence': 2, 'attack speed': 1},
			'uncommon': {'strength': 3, 'defense': 3, 'speed': 1, 'health': 3, 'crit chance': 4, 'crit damage': 3, 'intelligence': 3, 'attack speed': 1},
			'rare': {'strength': 4, 'defense': 4, 'speed': 1, 'health': 4, 'crit chance': 6, 'crit damage': 4, 'intelligence': 4, 'attack speed': 2},
			'epic': {'strength': 6, 'defense': 6, 'speed': 1, 'health': 6, 'crit chance': 8, 'crit damage': 6, 'intelligence': 6, 'attack speed': 3},
			'legendary': {'strength': 8, 'defense': 8, 'speed': 1, 'health': 8, 'crit chance': 10, 'crit damage': 8, 'intelligence': 8, 'attack speed': 4},
			'mythic': {'strength': 10, 'defense': 10, 'speed': 1, 'health': 10, 'crit chance': 12, 'crit damage': 10, 'intelligence': 10, 'attack speed': 5},
			'blacksmith': True
		},
        # 'necrotic': {
        #     'common': {'intelligence': 50},
        #     'uncommon': {'intelligence': 75},
        #     'rare': {'intelligence': 100},
        #     'epic': {'intelligence': 120},
        #     'legendary': {'intelligence': 150},
        #     'mythic': {'intelligence': 175},
        #     'blacksmith': False
        # },
        # 'perfect': {
        #     'common': {'defense': 10},
        #     'uncommon': {'defense': 15},
        #     'rare': {'defense': 25},
        #     'epic': {'defense': 50},
        #     'legendary': {'defense': 75},
        #     'mythic': {'defense': 100},
        #     'blacksmith': False
        # },
        # 'undead': {
        #     'common': {'strength': 1, 'defense': 9, 'health': 9, 'attack speed': 1},
        #     'uncommon': {'strength': 2, 'defense': 12, 'health': 12, 'attack speed': 2},
        #     'rare': {'strength': 2, 'defense': 15, 'health': 15, 'attack speed': 3},
        #     'epic': {'strength': 3, 'defense': 18, 'health': 18, 'attack speed': 4},
        #     'legendary': {'strength': 5, 'defense': 23, 'health': 23, 'attack speed': 5},
        #     'mythic': {'strength': 7, 'defense': 25, 'health': 25, 'attack speed': 6},
        #     'blacksmith': False
        # },
        'spiked': {
            'common': {'strength': 3, 'defense': 2, 'speed': 1, 'health': 2, 'crit chance': 2, 'crit damage': 3, 'intelligence': 3, 'attack speed': 1},
            'uncommon': {'strength': 4, 'defense': 3, 'speed': 1, 'health': 3, 'crit chance': 4, 'crit damage': 4, 'intelligence': 4, 'attack speed': 1},
            'rare': {'strength': 6, 'defense': 4, 'speed': 1, 'health': 4, 'crit chance': 6, 'crit damage': 6, 'intelligence': 6, 'attack speed': 2},
            'epic': {'strength': 8, 'defense': 6, 'speed': 1, 'health': 6, 'crit chance': 8, 'crit damage': 8, 'intelligence': 8, 'attack speed': 3},
            'legendary': {'strength': 10, 'defense': 8, 'speed': 1, 'health': 8, 'crit chance': 10, 'crit damage': 10, 'intelligence': 10, 'attack speed': 4},
            'mythic': {'strength': 12, 'defense': 10, 'speed': 1, 'health': 10, 'crit chance': 12, 'crit damage': 12, 'intelligence': 12, 'attack speed': 5},
            'blacksmith': False
        },
        'renowned': {
            # Increases all your stats by 1% (similar to Superior passive)
            'common': {'strength': 3, 'defense': 3, 'speed': 2, 'health': 3, 'crit chance': 3, 'crit damage': 3, 'intelligence': 3, 'attack speed': 1},
            'uncommon': {'strength': 5, 'defense': 5, 'speed': 2, 'health': 5, 'crit chance': 5, 'crit damage': 5, 'intelligence': 5, 'attack speed': 2},
            'rare': {'strength': 7, 'defense': 7, 'speed': 2, 'health': 7, 'crit chance': 7, 'crit damage': 7, 'intelligence': 7, 'attack speed': 3},
            'epic': {'strength': 9, 'defense': 9, 'speed': 2, 'health': 9, 'crit chance': 9, 'crit damage': 9, 'intelligence': 9, 'attack speed': 4},
            'legendary': {'strength': 12, 'defense': 12, 'speed': 2, 'health': 12, 'crit chance': 12, 'crit damage': 12, 'intelligence': 12, 'attack speed': 5},
            'mythic': {'strength': 15, 'defense': 15, 'speed': 2, 'health': 15, 'crit chance': 15, 'crit damage': 15, 'intelligence': 15, 'attack speed': 6},
            'blacksmith': False
        },
    },
    'talisman': {
		'bizarre': {
			'common': {'strength': 1, 'crit damage': -1, 'health': 1, 'intelligence': 6},
			'uncommon': {'strength': 2, 'crit damage': -2, 'health': 1, 'intelligence': 8},
			'rare': {'strength': 2, 'crit damage': -2, 'health': 1, 'intelligence': 10},
			'epic': {'strength': 3, 'crit damage': -3, 'health': 1, 'intelligence': 14},
			'legendary': {'strength': 5, 'crit damage': -5, 'health': 1, 'intelligence': 20},
			'mythic': {'strength': 7, 'crit damage': -7, 'health': 2, 'intelligence': 30},
			'blacksmith': True
		},
        'itchy': {
            'common': {'strength': 1, 'crit damage': 3, 'attack speed': 0},
            'uncommon': {'strength': 1, 'crit damage': 4, 'attack speed': 0},
            'rare': {'strength': 1, 'crit damage': 5, 'attack speed': 1},
            'epic': {'strength': 2, 'crit damage': 7, 'attack speed': 1},
            'legendary': {'strength': 3, 'crit damage': 10, 'attack speed': 1},
            'mythic': {'strength': 4, 'crit damage': 15, 'attack speed': 1},
            'blacksmith': True
        },
		'unpleasant': {
			'common': {'crit chance': 1},
			'uncommon': {'crit chance': 1},
			'rare': {'crit chance': 1},
			'epic': {'crit chance': 2},
			'legendary': {'crit chance': 2},
			'mythic': {'crit chance': 3},
			'blacksmith': True
		},
        'superior': {
            'common': {'strength': 2, 'crit damage': 2},
            'uncommon': {'strength': 3, 'crit damage': 2},
            'rare': {'strength': 4, 'crit damage': 2},
            'epic': {'strength': 5, 'crit damage': 3},
            'legendary': {'strength': 7, 'crit damage': 3},
            'mythic': {'strength': 10, 'crit damage': 5},
            'blacksmith': True
        },
        'forceful': {
            'common': {'strength': 4},
            'uncommon': {'strength': 5},
            'rare': {'strength': 7},
            'epic': {'strength': 10},
            'legendary': {'strength': 15},
            'mythic': {'strength': 20},
            'blacksmith': True
        },
        'hurtful': {
            'common': {'crit damage': 4},
            'uncommon': {'crit damage': 5},
            'rare': {'crit damage': 7},
            'epic': {'crit damage': 10},
            'legendary': {'crit damage': 15},
            'mythic': {'crit damage': 20},
            'blacksmith': True
        },
        'strong': {
            'common': {'strength': 1, 'crit damage': 1, 'defense': 0},
            'uncommon': {'strength': 2, 'crit damage': 2, 'defense': 0},
            'rare': {'strength': 3, 'crit damage': 3, 'defense': 1},
            'epic': {'strength': 5, 'crit damage': 5, 'defense': 2},
            'legendary': {'strength': 8, 'crit damage': 8, 'defense': 3},
            'mythic': {'strength': 12, 'crit damage': 12, 'defense': 4},
            'blacksmith': True
        },
        'godly': {
            'common': {'strength': 1, 'crit damage': 2, 'intelligence': 1},
            'uncommon': {'strength': 2, 'crit damage': 2, 'intelligence': 1},
            'rare': {'strength': 3, 'crit damage': 3, 'intelligence': 1},
            'epic': {'strength': 5, 'crit damage': 4, 'intelligence': 2},
            'legendary': {'strength': 7, 'crit damage': 6, 'intelligence': 4},
            'mythic': {'strength': 10, 'crit damage': 8, 'intelligence': 6},
            'blacksmith': True
        },
		'demonic': {
			'common': {'strength': 1, 'intelligence': 5},
			'uncommon': {'strength': 2, 'intelligence': 7},
			'rare': {'strength': 2, 'intelligence': 9},
			'epic': {'strength': 3, 'intelligence': 12},
			'legendary': {'strength': 5, 'intelligence': 17},
			'mythic': {'strength': 7, 'intelligence': 24},
			'blacksmith': True
		},
		'zealous': {
			'common': {'strength': 1, 'speed': 0, 'crit damage': 1, 'intelligence': 1},
			'uncommon': {'strength': 2, 'speed': 0, 'crit damage': 2, 'intelligence': 2},
			'rare': {'strength': 2, 'speed': 1, 'crit damage': 2, 'intelligence': 3},
			'epic': {'strength': 3, 'speed': 1, 'crit damage': 3, 'intelligence': 5},
			'legendary': {'strength': 5, 'speed': 1, 'crit damage': 5, 'intelligence': 7},
			'mythic': {'strength': 7, 'speed': 2, 'crit damage': 7, 'intelligence': 10},
			'blacksmith': True
		},
        'strange': {
            'common': {'crit damage': 1, 'strength': 2, 'defense': 0, 'speed': 1, 'health': 0, 'intelligence': 1, 'attack speed': -1},
            'uncommon': {'crit damage': 2, 'strength': 1, 'defense': 3, 'speed': 0, 'health': 2, 'intelligence': -1, 'attack speed': 2},
            'rare': {'crit damage': 0, 'strength': -1, 'defense': 2, 'speed': 1, 'health': 1, 'intelligence': 2, 'attack speed': 0},
            'epic': {'crit damage': 1, 'strength': 3, 'defense': -1, 'speed': 0, 'health': 7, 'intelligence': 0, 'attack speed': 4},
            'legendary': {'crit damage': 7, 'strength': 0, 'defense': 1, 'speed': 3, 'health': -1, 'intelligence': 8, 'attack speed': 0},
            'mythic': {'crit damage': 9, 'strength': 4, 'defense': 1, 'speed': 3, 'health': 0, 'intelligence': 11, 'attack speed': 5},
            'blacksmith': True
        },
        'silky': {
            'common': {'crit damage': 5},
            'uncommon': {'crit damage': 6},
            'rare': {'crit damage': 8},
            'epic': {'crit damage': 10},
            'legendary': {'crit damage': 15},
            'mythic': {'crit damage': 20},
            'blacksmith': False
        },
        'bloody': {
            'common': {'strength': 1, 'crit damage': 3, 'attack speed': 1, 'speed': 1},
            'uncommon': {'strength': 1, 'crit damage': 4, 'attack speed': 1, 'speed': 1},
            'rare': {'strength': 1, 'crit damage': 5, 'attack speed': 1, 'speed': 1},
            'epic': {'strength': 2, 'crit damage': 6, 'attack speed': 2, 'speed': 1},
            'legendary': {'strength': 3, 'crit damage': 9, 'attack speed': 2, 'speed': 1},
            'mythic': {'strength': 4, 'crit damage': 12, 'attack speed': 3, 'speed': 1},
            'blacksmith': False
        },
    }
}

rarities = ['common', 'uncommon', 'rare', 'epic', 'legendary', 'mythic']


def format_counts(counts):
    result = {}
    for (equipment_type, rarity, reforge), count in counts.get_values().items():
        count = round(count)
        if count > 0:
            if equipment_type not in result:
                result[equipment_type] = {}
            if rarity not in result[equipment_type]:
                result[equipment_type][rarity] = {}

            result[equipment_type][rarity][reforge] = count

    return result


def solve(m):
    solver = SolverFactory('scip', executable='scip')
    solver.options['limits/time'] = SCIP_TIMELIMIT
    result = solver.solve(m)
    if result.solver.status == SolverStatus.aborted and result.solver.termination_condition == TerminationCondition.maxTimeLimit:
        return False
    return True


def create_model(counts, reforge_set, only_blacksmith_reforges):
    m = ConcreteModel()
    m.reforge_set = Set(
        initialize=[
            (i, j, k) for i, count in counts.items() for j in rarities for k, stats in
            damage_reforges[armor_check(i)].items()
            if j in stats and count[j] > 0 and (only_blacksmith_reforges is False or stats['blacksmith'] is True)
        ], ordered=True
    )
    m.reforge_counts = Var(m.reforge_set, domain=NonNegativeIntegers, initialize=0)
    m.eqn = ConstraintList()
    return m


def get_stat_with_reforges(stat, reforges, counts, player, only_blacksmith_reforges, m):
    value = sum(damage_reforges['talisman'][k][j].get(stat, 0) * count for (i, j, k), count in reforges.get_values().items() if i == 'talisman')
    for equip in counts:
        if equip != 'talisman':
            for k in player.stats.children:
                if k[0] == equip:
                    value += k[1].multiplier * sum(damage_reforges[armor_check(equip)][k][j].get(stat, 0) * count for (i, j, k), count in reforges.get_values().items() if i == equip)
    if only_blacksmith_reforges:
        return m * (value + player.stats.get_raw_base_stats(stat))
    else:
        return m() * (value + player.stats.get_raw_base_stats(stat))


def create_constraint_rule(stat, m, counts, player):
    rule = quicksum((damage_reforges['talisman'][k][j].get(stat, 0) * m.reforge_counts['talisman', j, k] for i, j, k in m.reforge_set if i == 'talisman'), linear=False)
    for equip in counts:
        if equip != 'talisman':
            for k in player.stats.children:
                if k[0] == equip:
                    rule += k[1].multiplier * quicksum((damage_reforges[armor_check(equip)][k][j].get(stat, 0) * m.reforge_counts[equip, j, k] for i, j, k in m.reforge_set if i == equip), linear=False)
    return rule


def armor_check(armor):
    return 'armor' if armor in ('helmet', 'chestplate', 'leggings', 'boots') else armor

# TODO: Add gap limit = 0.10%
# TODO: Add solver time
# TODO: optimize the performance, possibly a thread limit = 4?
def damage_optimizer(player, *, perfect_crit_chance, include_attack_speed, only_blacksmith_reforges):
    armor_types = [type for type, piece in player.armor.items() if armor_check(type) == 'armor' and piece]
    equipment_types = ['talisman', player.weapon.type] + armor_types
    counts = {
        'talisman': {rarity: sum(talisman.rarity == rarity for talisman in player.talismans if talisman.active) for rarity in rarities},
        player.weapon.type: {rarity: int(player.weapon.rarity == rarity) for rarity in rarities},
        'helmet': {rarity: int(player.armor['helmet'].rarity == rarity) for rarity in rarities} if player.armor[
            'helmet'] else {rarity: 0 for rarity in rarities},
        'chestplate': {rarity: int(player.armor['chestplate'].rarity == rarity) for rarity in rarities} if player.armor[
            'chestplate'] else {rarity: 0 for rarity in rarities},
        'leggings': {rarity: int(player.armor['leggings'].rarity == rarity) for rarity in rarities} if player.armor[
            'leggings'] else {rarity: 0 for rarity in rarities},
        'boots': {rarity: int(player.armor['boots'].rarity == rarity) for rarity in rarities} if player.armor[
            'boots'] else {rarity: 0 for rarity in rarities},
    }

    m = create_model(counts, damage_reforges, only_blacksmith_reforges)

    for equipment_type in equipment_types:
        reforges = damage_reforges[armor_check(equipment_type)]
        sums = {rarity: [] for rarity in rarities}
        for reforge in reforges.keys():
            for rarity in reforges[reforge].keys():
                if rarity != 'blacksmith' and (
                        only_blacksmith_reforges is False or reforges[reforge]['blacksmith'] is True):
                    if counts[equipment_type][rarity] > 0:
                        sums[rarity].append(m.reforge_counts[equipment_type, rarity, reforge])
        for rarity in rarities:
            if counts[equipment_type][rarity] > 0:
                m.eqn.add(quicksum(sums[rarity], linear=False) == counts[equipment_type][rarity])

    # for stat in ['strength', 'crit damage'] + ['crit chance'] * perfect_crit_chance + ['attack speed'] * include_attack_speed:
    #     player.stats.modifiers[stat].insert(0,
    #                                         lambda stat: stat + quicksum(
    #                                             damage_reforges[armor_check(i)][k][j].get(stat, 0) * m.reforge_counts[
    #                                                 i, j, k] for i, j, k in m.reforge_set))

    # --- variables ---
    m.s = Var(domain=Reals, initialize=400)
    m.cd = Var(domain=Reals, initialize=400)
    m.damage = Var(domain=Reals, initialize=10000)
    m.floored_strength = Var(domain=Integers, initialize=60)
    m.cc = Var(domain=Reals, initialize=100)
    m.a = Var(domain=Reals, initialize=50)
    if only_blacksmith_reforges:
        m.m = player.stats.multiplier
    else:
        m.m = Var(domain=Reals, initialize=1)
    # ---

    # --- modifiers ---
    # manually add it here now, will find a better way to do it
    cd_tara_helm = m.s / 10 if player.armor['helmet'] == 'TARANTULA_HELMET' else 0
    # ---

    # --- multiplier ---
    if not only_blacksmith_reforges:
        m.eqn.add(m.m == player.stats.multiplier + (quicksum((m.reforge_counts[i, j, k]*0.01 for i, j, k in m.reforge_set if i in armor_types and k == 'renowned'), linear=False) if not only_blacksmith_reforges else 0))
    # ---

    # --- crit chance ---
    cc_rule = create_constraint_rule('crit chance', m, counts, player)
    m.eqn.add(m.cc == m.m * (cc_rule + player.stats.get_raw_base_stats('crit chance')))
    if perfect_crit_chance:
        m.eqn.add(99.5 <= m.cc)  # may need to change to 100 instead of 99.5, idk how hypixel round it
    # ---

    # --- attack speed ---
    a_rule = create_constraint_rule('attack speed', m, counts, player)
    m.eqn.add(m.a == m.m * (a_rule + player.stats.get_raw_base_stats('attack speed')))
    if include_attack_speed:
        m.eqn.add(100.5 >= m.a)
    # ---

    # --- strength ---
    strength_rule = create_constraint_rule('strength', m, counts, player)
    m.eqn.add(m.s == m.m * (strength_rule + player.stats.get_raw_base_stats('strength')))
    # ---

    # --- crit damage ---
    cd_rule = create_constraint_rule('crit damage', m, counts, player)
    m.eqn.add(m.cd == m.m * (cd_rule + player.stats.get_raw_base_stats('crit damage') + cd_tara_helm))
    # ---

    m.eqn.add(m.floored_strength >= m.s / 5 - 0.9999)
    m.eqn.add(m.floored_strength <= m.s / 5)
    m.eqn.add(m.damage == (5 + player.weapon.stats['damage'] + m.floored_strength) * (1 + m.s / 100) * (1 + m.cd / 100))

    m.objective = Objective(expr=m.damage * (((m.a+100) / 100) / 0.5) if include_attack_speed else m.damage, sense=maximize)
    optimized = solve(m)

    # from pyomo.util.infeasible import log_infeasible_constraints
    # log_infeasible_constraints(m, log_expression=True, log_variables=True)

    result = {'strength': m.s(),
              'crit damage': m.cd(),
              'crit chance': m.cc(),
              'attack speed': m.a(),
              'is optimized': optimized}
    # if perfect_crit_chance:
    #     result['crit chance'] = m.cc()
    # if include_attack_speed:
    #     result['attack speed'] = m.a() - 100
    return result, format_counts(m.reforge_counts)


# def ehp_optimizer(player, talisman_rarity_counts, *, only_blacksmith_reforges):
    # equipment_types = ['talisman', 'armor']
    # m = create_model(equipment_types, ehp_reforges)
    #
    # m.m = 1 + player.stats['multiplier'] / 100
    #
    # m.hp = Var(domain=Reals, initialize=1400)
    # m.eqn.add(m.hp == max(0, m.m * (quicksum(ehp_reforges[i][k][j].get('health', 0) * m.reforge_counts[i, j, k] for i, j, k in m.reforge_set) + player.stats['health'])))
    # m.d = Var(domain=Reals, initialize=700)
    # m.eqn.add(m.d == max(0, m.m * (quicksum(ehp_reforges[i][k][j].get('defense', 0) * m.reforge_counts[i, j, k] for i, j, k in m.reforge_set) + player.stats['defense'])))
    #
    # counts = {'talisman': talisman_rarity_counts, 'armor': armor_rarity_counts}
    # for equipment_type in equipment_types:
    #     reforges = ehp_reforges[equipment_type]
    #     sums = {rarity: [] for rarity in rarities}
    #     for reforge in reforges.keys():
    #         for rarity in reforges[reforge].keys():
    #             sums[rarity].append(m.reforge_counts[equipment_type, rarity, reforge])
    #     for rarity in rarities:
    #         m.eqn.add(quicksum(sums[rarity]) == counts[equipment_type][rarity])
    # m.objective = Objective(expr=(m.hp * (1 + m.d / 100)), sense=maximize)
    # solve(m)
    #
    # return {'ehp': m.objective(), 'health': m.hp(), 'defense': m.d()}, format_counts(m.reforge_counts)


# def mastiff_ehp_optimizer(only_blacksmith_reforges):
#     if only_blacksmith_reforges:
#         return '''Reforge all your armor to fierce
# Reforge all your talismans to hurtful
# Reforge your sword/fishing rod to spicy
# Reforge your bow to rapid'''
#     else:
#         return '''Reforge all your armor to fierce
# Reforge all your talismans to hurtful
# Reforge your sword/fishing rod to spicy or fabled
# Reforge your bow to rapid'''
#
#
# def intelligence_optimizer(only_blacksmith_reforges):
#     if only_blacksmith_reforges:
#         return '''Reforge all your armor to wise
# Reforge all your common talismans to demonic
# Reforge all your other talismans to bizzare
# Reforge your sword/fishing rod to heroic
# Reforge your bow to deadly'''
#     else:
#         return '''Reforge all your armor to necrotic
# Reforge all your common talismans to demonic
# Reforge all your other talismans to bizzare
# Reforge your sword/fishing rod to heroic
# Reforge your bow to deadly'''
#
#
# def speed_optimizer(only_blacksmith_reforges):
#     if only_blacksmith_reforges:
#         return '''Reforge your common talismans to simple
# Reforge your other talismans to vivid
# Reforge your common and uncommon armor to mythic
# Reforge your other armor to light
# Sword/bow/fishing rod reforges don't matter'''
#     else:
#         return '''Reforge your common talismans to simple
# Reforge your other talismans to vivid
# Reforge your common and uncommon armor to renowned or spiked
# Reforge your other armor to light
# Sword/bow/fishing rod reforges don't matter'''


def ehp_optimizer(only_blacksmith_reforges=False):
    return '''Unavailable for now'''


def intelligence_optimizer(only_blacksmith_reforges=False):
    return '''Unavailable for now'''


def speed_optimizer(only_blacksmith_reforges=False):
    return '''Unavailable for now'''
