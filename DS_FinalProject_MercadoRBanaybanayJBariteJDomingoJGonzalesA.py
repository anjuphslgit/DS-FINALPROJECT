
# Imports the libraries used for our program.

import os         # We use this for clearing the screen and handling file operations.
import math       # We use this when battle or reward calculations need math functions.
import json       # Our session data is written and restored as JSON.
import io         # We use in-memory text streams when collecting output.
import copy       # We need full copies of saved states before risky changes or Undo.
import shutil     # We use this to copy older data files while saving safely.
import tempfile   # We write temporary files first instead of risking the original save.
import random     # We use randomness for battle hits, damage, and item chances.
import sys        # We check the terminal and write animation output through this module.
import textwrap   # We wrap descriptions and story messages so our console layout stays neat.
import time       # We use short delays in the story and battle animations.
from datetime import datetime  # We save the actual date and time of each game event.
from pathlib import Path       # We check whether our record files and folders exist.


# File names used to save the game records
# We keep account stats and saved progress in this TXT file.
ACCOUNT_FILE = "1_player_accounts.txt"
# We store enemy profiles here; the enemy list is not created only for the Queue.
ENEMY_FILE = "2_enemy_records.txt"
# We keep consumable items and their effects separate from player inventory.
ITEM_FILE = "3_item_records.txt"
# We save shop equipment here so the admin and player use the same records.
EQUIPMENT_FILE = "4_equipment_records.txt"
# We keep the six room names and descriptions in this file.
ROOM_FILE = "5_room_records.txt"
# We save which rooms are connected and the names of their passages.
CONNECTION_FILE = "6_room_connections.txt"
# We keep the questions and correct answers used during challenges.
QUESTION_FILE = "7_question_records.txt"
# We save finished battle results so our reports have actual records.
BATTLE_HISTORY_FILE = "8_battle_history_records.txt"
# We keep the action history with unique action IDs.
BATTLE_LOG_FILE = "9_battle_activity_log.txt"
# We store an overall record of game runs and their progress here.
GAME_RECORD_FILE = "10_dungeon_game_records.txt"
# Our exported report text files are saved inside this folder.
REPORT_FOLDER = "11_reports"
# We keep unfinished battles and undo snapshots in this JSON file.
BATTLE_SESSION_FILE = "12_battle_session_records.json"

# ---------------------------------------------------------------
# GAME BALANCE
# ---------------------------------------------------------------

# Starting attributes for newly registered players
# These values are used only when we create a new player.
STARTING_STATS = {"hp": 100, "max_hp": 100, "atk": 14, "gold": 60}
# New players receive one starter Health Potion.
STARTING_ITEMS = {"ITM-001": 1}

# Player attack rules
# Our attack damage can move up or down by this random amount.
PLAYER_DAMAGE_SPREAD = 3
# This is the base chance that a player attack fails to hit.
PLAYER_MISS_CHANCE = 7
# This is the base chance of landing a critical hit.
PLAYER_CRIT_CHANCE = 12
# We multiply attack damage by this value when a player lands a critical hit.
PLAYER_CRIT_MULTIPLIER = 1.75

# Enemy attack rules
# Enemy damage also varies a little each turn.
ENEMY_DAMAGE_SPREAD = 2
# Harder enemies have higher critical-hit chances.
ENEMY_CRIT_CHANCE = {"Weak": 5, "Intermediate": 8, "Strong": 10, "Boss": 12}
# Enemy critical attacks use this damage multiplier.
ENEMY_CRIT_MULTIPLIER = 1.5
# Vharok deals more damage after the boss-enrage condition is reached.
BOSS_ENRAGE_MULTIPLIER = 1.3

# Battle action rules
# While defending, only this fraction of the attack gets through before other reductions.
DEFEND_DAMAGE_TAKEN = 0.4
# Defending prepares this extra value for the next counterattack.
DEFEND_COUNTER_BONUS = 30
# Our stun items succeed with this percentage chance.
STUN_CHANCE = 75
# Attack boosts are active for this many player attacks.
BOOST_ATTACKS = 3

# We give these rewards after 3 wins in one regular difficulty (not after every enemy).
# We add this much base ATK after meeting a level quota.
ATTACK_BONUS_PER_LEVEL = 5
# We add this much Max HP after meeting a level quota.
MAX_HP_BONUS_PER_LEVEL = 20
# Each regular tier gives its own one-time extra Gold reward.
LEVEL_COMPLETION_GOLD = {"Weak": 40, "Intermediate": 80, "Strong": 150}

# Camp and defeat rules
# The player must have this much Gold before resting.
REST_COST = 40
# Resting heals this percentage of Max HP, capped at the player's HP limit.
REST_HEAL_PERCENT = 50
# We take this percentage of current Gold when the player loses.
DEFEAT_GOLD_LOSS_PERCENT = 25
# After defeat, we restore this percentage of the player's Max HP.
DEFEAT_REVIVE_PERCENT = 50
# The player earns this score when the final escape is completed.
ESCAPE_SCORE_BONUS = 500

# ---------------------------------------------------------------
# THE SIX-ROOM DUNGEON (fixed route, one room per difficulty)
# ENTRANCE -> WEAK -> INTERMEDIATE -> STRONG -> BOSS -> EXIT
# ---------------------------------------------------------------

# We keep the fixed entrance-to-exit room IDs in travel order.
ROOM_ORDER = ["ROOM-000", "ROOM-001", "ROOM-002", "ROOM-003", "ROOM-004",
              "ROOM-005"]
# We use one constant for the entrance ID in travel and defeat messages.
ENTRANCE_ROOM_ID = ROOM_ORDER[0]
# We use one constant for the exit ID rather than copying the text everywhere.
EXIT_ROOM_ID = ROOM_ORDER[5]

# Each difficulty level lives in exactly one room
# Our difficulty-to-room mapping makes newly added enemies appear in the correct area.
ROOM_FOR_DIFFICULTY = {
    "Weak": "ROOM-001",
    "Intermediate": "ROOM-002",
    "Strong": "ROOM-003",
    "Boss": "ROOM-004"
}

DIFFICULTY_ORDER = {"Weak": 1, "Intermediate": 2, "Strong": 3, "Boss": 4}
# Rank progression requires three victories at each regular difficulty.
# Do not let admin edits remove enemies needed to unlock the next stage.
# We keep at least three enemies per normal tier so progression stays possible.
MIN_ENEMIES_PER_DIFFICULTY = {"Weak": 3, "Intermediate": 3,
                              "Strong": 3, "Boss": 1}
LEVEL_ORDER = ["Weak", "Intermediate", "Strong", "Boss"]
PLAYER_STATUSES = ["Active", "In Battle", "Defeated", "Retreated", "Victorious"]

# ---------------------------------------------------------------
# EQUIPMENT (Sword, Shield, Armor in four progression tiers)
# ---------------------------------------------------------------

# These are the three types of gear the player can equip at once.
EQUIPMENT_SLOTS = ["sword", "shield", "armor"]

# We unlock the next level after 3 victories in the previous difficulty. Each unlocked
# level grants three FREE pieces; the shop sells only optional CURRENT-level
# alternatives (two upgrade choices per slot).
TIER_UNLOCK_REQUIREMENT = {
    "Weak": None, "Intermediate": "Weak", "Strong": "Intermediate",
    "Boss": "Strong"
}
EQUIPMENT_LEVELS = ["Weak", "Intermediate", "Strong", "Boss"]

SLOT_STAT_TEXT = {
    "sword": "ATK: +{b}",
    "shield": "BLOCK: {b}%",
    "armor": "DEF: -{b} per hit"
}

# Purchasable equipment is grouped by difficulty and equipment slot.
# Fields: id, name, slot, tier, bonus, price, description, speed.
# Sword speed affects accuracy and critical-hit chance.

# These are our starter shop gear records; each one has a slot, tier, price, and bonus.
DEFAULT_EQUIPMENT = [
    ("EQP-001", "Rusty Sword +1", "sword", "Weak", 4, 40,
     "A nimble sewer blade; a first taste of faster strikes.", 2),
    ("EQP-002", "Rusty Sword +2", "sword", "Weak", 6, 75,
     "An unusually sharp saber that rewards quick hands.", 4),
    ("EQP-003", "Wooden Shield +1", "shield", "Weak", 7, 35,
     "Lightweight protection for sewer skirmishes.", 0),
    ("EQP-004", "Wooden Shield +2", "shield", "Weak", 10, 65,
     "Metal-bound timber gives extra protection.", 0),
    ("EQP-005", "Cloth Armor +1", "armor", "Weak", 2, 35,
     "Patched leather dulls the edge of enemy hits.", 0),
    ("EQP-006", "Cloth Armor +2", "armor", "Weak", 3, 70,
     "Extra rivets reinforce weak seams.", 0),
    ("EQP-007", "Bloodstone Sword +1", "sword", "Intermediate", 8, 95,
     "A balanced sword forged from the Bloodstone ore.", 6),
    ("EQP-008", "Bloodstone Sword +2", "sword", "Intermediate", 10, 145,
     "A swift crystal-edged blade with a stronger bite.", 8),
    ("EQP-009", "Iron Shield +1", "shield", "Intermediate", 12, 90,
     "Layered bone plates brace against heavier attacks.", 0),
    ("EQP-010", "Iron Shield +2", "shield", "Intermediate", 15, 135,
     "A thick bloodsteel shield built for hardened foes.", 0),
    ("EQP-011", "Chainmail Armor +1", "armor", "Intermediate", 3, 85,
     "Reinforced chains absorb force from each strike.", 0),
    ("EQP-012", "Chainmail Armor +2", "armor", "Intermediate", 4, 130,
     "Stone-lined plates spread the force of each blow.", 0),
    ("EQP-013", "Steel Sword +1", "sword", "Strong", 13, 175,
     "A fierce warblade with relentless momentum.", 11),
    ("EQP-014", "Steel Sword +2", "sword", "Strong", 16, 260,
     "Its deadly edge turns speed into precision.", 13),
    ("EQP-015", "Steel Shield +1", "shield", "Strong", 18, 160,
     "A towering shield that can endure savage blows.", 0),
    ("EQP-016", "Steel Shield +2", "shield", "Strong", 22, 240,
     "A heavy bulwark shaped from ancient fortress steel.", 0),
    ("EQP-017", "Steel Armor +1", "armor", "Strong", 5, 155,
     "Forged plates soften the impact of heavy weapons.", 0),
    ("EQP-018", "Steel Armor +2", "armor", "Strong", 7, 235,
     "A sturdy shell crafted for prolonged battles.", 0),
    ("EQP-019", "Darksteel Sword +1", "sword", "Boss", 17, 290,
     "A blade honed to challenge the ruler of ruin.", 16),
    ("EQP-020", "Darksteel Sword +2", "sword", "Boss", 20, 420,
     "A legendary sword said to cut through darkness.", 19),
    ("EQP-021", "Darksteel Shield +1", "shield", "Boss", 27, 270,
     "Its enchanted face turns aside powerful attacks.", 0),
    ("EQP-022", "Darksteel Shield +2", "shield", "Boss", 32, 395,
     "A rare shield built to withstand the World Eater.", 0),
    ("EQP-023", "Darksteel Armor +1", "armor", "Boss", 7, 265,
     "Dense armor prepared for the final confrontation.", 0),
    ("EQP-024", "Darksteel Armor +2", "armor", "Boss", 9, 385,
     "Ancient armor that softens devastating strikes.", 0)
]



# Each unlocked level supplies a standard equipment set.
# Purchased equipment stays in the player's inventory when the tier changes.
# Tuples: name, combat bonus, sword speed (0 for shield and armor).
# We automatically provide standard gear when a new tier is unlocked.
STANDARD_EQUIPMENT = {
    "sword": [
        ("Rusty Sword", 2, 0), ("Bloodstone Sword", 6, 4),
        ("Steel Sword", 10, 8), ("Darksteel Sword", 14, 12)
    ],
    "shield": [
        ("Wooden Shield", 4, 0), ("Iron Shield", 9, 0),
        ("Steel Shield", 15, 0), ("Darksteel Shield", 23, 0)
    ],
    "armor": [
        ("Cloth Armor", 1, 0), ("Chainmail Armor", 2, 0),
        ("Steel Armor", 4, 0), ("Darksteel Armor", 6, 0)
    ]
}
STANDARD_UPGRADE_LEVELS = ["Weak", "Intermediate", "Strong"]

# ---------------------------------------------------------------
# GOLD ECONOMY (battle rewards, level rewards, and treasure chests)
# ---------------------------------------------------------------

# One treasure chest per fighting room, opened once after the room is
# cleared: room id -> (chest name, rarity, gold)
# Each fighting room has a separate one-time chest reward.
TREASURES = {
    "ROOM-001": ("Mossy Supply Chest", "Basic", 25),
    "ROOM-002": ("Bloodstone Coffer", "Better", 40),
    "ROOM-003": ("War-Torn Strongbox", "Better", 50),
    "ROOM-004": ("Throne Hoard", "Rare", 75)
}
TREASURE_SCORE = 10

# A correct challenge answer grants the question's bonus attack damage.
# Challenges never grant Gold; the bonus applies to that attack only.

# What each item effect does with its power value
ITEM_EFFECTS = {
    "heal": "Restores {power}% of Max HP",
    "boost": "+{power}% damage on your next 3 attacks",
    "stun": "75% chance the enemy loses its next {power} turns",
    "damage": "Deals {low}-{high} damage that never misses"
}

# ---------------------------------------------------------------
# STORY TEXT
# ---------------------------------------------------------------

STORY_INTRO = [
    "While playing Dreadveil: The Last Gate, you discover a mysterious "
    "treasure chest glowing beneath a veil of black mist. From inside, "
    "a voice whispers: \"Can you find and kill me?\"",
    "You accept the challenge. The screen darkens, the world disappears, "
    "and you awaken inside the cursed dungeon known as Dreadveil.",
    "Vharok, the World Eater, holds the Last Gate shut. Defeat the "
    "guardians of the Weak, Intermediate and Strong halls, face him "
    "in the Throne of Ruin, and cross the final gate to return home."
]

ROOM_STORY = {
    "ROOM-000": [
        "A cold stone gate slams shut behind you. Torches flicker beneath "
        "a curtain of black mist: the veil that gives Dreadveil its name.",
        "Beyond the Rusted Grate lie the Rotting Sewers. Your only path "
        "forward leads deeper into the curse."
    ],
    "ROOM-001": [
        "Rotting water echoes through the sewers. Claws scrape stone "
        "while the first guardians emerge from the dark.",
        "Learn to attack, defend and use potions. Defeat three Weak "
        "guardians to unseal the Crimson Gate. Extra enemies are optional."
    ],
    "ROOM-002": [
        "Bloodstone crystals glow through the walls like trapped stars. "
        "Dreadveil's mist coils between their crimson reflections.",
        "The guardians here strike harder. Use careful defense and "
        "timing to unseal the Iron Drawbridge. Three victories are enough."
    ],
    "ROOM-003": [
        "Broken shields cover the War-Torn Catacombs. The veil grows "
        "heavier, and the strongest guardians bar the road to Vharok.",
        "Prepare your equipment, recover your strength and defeat three "
        "Strong guardians to unseal the Throne Gate."
    ],
    "ROOM-004": [
        "The Throne Gate groans open. Black mist circles the Throne "
        "of Ruin, where Vharok, the World Eater, awaits.",
        "He is the voice from the treasure chest and the keeper of "
        "the Last Gate. There is no way past him without a fight."
    ],
    "ROOM-005": [
        "The Sealed Exit Door stands open at last. Beyond it, a narrow "
        "beam of daylight cuts through the fading veil.",
        "This is the Last Gate. One final step will break the curse "
        "and carry you out of Dreadveil."
    ]
}

ENCOUNTER_TEXT = {
    "Weak": "A guardian rises from Dreadveil's shadows!",
    "Intermediate": "A Bloodstone guardian blocks the passage through the veil!",
    "Strong": "A fierce guardian steps from the mist before the Throne Gate!",
    "Boss": "Vharok rises as the darkness gathers around the Throne of Ruin."
}

BOSS_INTRO = [
    "Vharok, the World Eater, opens a thousand-year-old eye. "
    "Dreadveil's black mist gathers at his feet.",
    "\"You answered the whisper from my chest, little hero. "
    "Now you have found me. Will you break my veil, or be lost within it?\"",
    "Behind his throne waits the Last Gate, sealed by his power. "
    "The final battle begins."
]

BOSS_DEFEAT = [
    "Vharok lets out a final roar and crumbles to ash. The black "
    "mist surrounding the throne begins to unravel.",
    "Dreadveil's curse is breaking. Behind the throne, the Sealed "
    "Exit Door opens, revealing the path to the Last Gate."
]

ENDING_TEXT = [
    "You take one final step through the Last Gate. Behind you, the "
    "Throne of Ruin trembles as Dreadveil's black mist breaks apart. "
    "Vharok's curse can no longer hold you.",
    "The cold stone beneath your feet vanishes. A flash of light fills "
    "your eyes, and you wake up in front of your own screen. You are "
    "back in the world where the adventure began.",
    "On the screen, the mysterious treasure chest closes for the "
    "last time. The voice that once asked, 'Can you find and kill me?' "
    "is silent. In its place, a final message appears:",
    "YOU FOUND ME. YOU DEFEATED ME. YOU ARE FREE.",
    "The Last Gate fades from view. Dreadveil is behind you now, "
    "and your journey is complete."
]

# ---------------------------------------------------------------
# DEFAULT RECORDS (written to the text files on the first run)
# ---------------------------------------------------------------

# We create these demo profiles only if the account file has no usable records.
DEFAULT_ACCOUNTS = [
    # username, password, role, hp, max_hp, atk, gold, score, wins, losses,
    # defeated ids, completed levels, inventory
    ("admin", "admin123", "Admin", 0, 0, 0, 0, 0, 0, 0, [], [], {}),
    ("player", "player123", "Player", 100, 100, 14, 60, 0, 0, 0, [], [], {"ITM-001": 1})
]

# Our starter list includes three regular enemies per tier and one boss.
DEFAULT_ENEMIES = [
    # id, name, type, max_hp, atk, gold, score, room
    ("ENM-001", "Gravefang Rat", "Weak", 55, 7, 25, 40, "ROOM-001"),
    ("ENM-002", "Hollowbone Goblin", "Weak", 70, 9, 30, 60, "ROOM-001"),
    ("ENM-003", "Ashen Ghoul", "Weak", 85, 11, 35, 80, "ROOM-001"),
    ("ENM-004", "Ironjaw Reaver", "Intermediate", 105, 12, 50, 100,
     "ROOM-002"),
    ("ENM-005", "Boneguard Executioner", "Intermediate", 120, 13, 60, 120,
     "ROOM-002"),
    ("ENM-006", "Hellchain Marauder", "Intermediate", 135, 14, 70, 140,
     "ROOM-002"),
    ("ENM-007", "Dreadfang Berserker", "Strong", 150, 16, 85, 180,
     "ROOM-003"),
    ("ENM-008", "Abyssal Death Knight", "Strong", 165, 17, 95, 200,
     "ROOM-003"),
    ("ENM-009", "Soulreaper Wraith", "Strong", 180, 18, 110, 220,
     "ROOM-003"),
    ("BS-001", "Vharok, the World Eater", "Boss", 320, 22, 300, 600,
     "ROOM-004")
]

# We create these starting consumables when there is no saved item catalog.
DEFAULT_ITEMS = [
    # id, name, effect, power, price, max carry, description
    ("ITM-001", "Health Potion", "heal", 35, 30, 10,
     "A bitter red brew that closes wounds."),
    ("ITM-002", "Strength Tonic", "boost", 50, 70, 5,
     "Fills your arms with burning strength."),
    ("ITM-003", "Paralysis Bomb", "stun", 2, 110, 5,
     "Releases a numbing cloud of spores."),
    ("ITM-004", "Poison Dagger", "damage", 35, 120, 5,
     "A throwing blade coated in venom.")
]

# Keep every original room name except ROOM-000, whose official name
# is Dreadveil Entrance. Room IDs and game progression never change.
# These are the original room names, with ROOM-000 named Dreadveil Entrance.
DEFAULT_ROOMS = [
    ("ROOM-000", "Dreadveil Entrance", "A cold stone gate where every expedition begins."),
    ("ROOM-001", "Rotting Sewers", "Knee-deep filth and the scratching of claws. Home of the Weak enemies."),
    ("ROOM-002", "Bloodstone Hall", "Red crystals pulse inside the walls. Home of the Intermediate enemies."),
    ("ROOM-003", "War-Torn Catacombs", "Broken shields of a forgotten army. Home of the Strong enemies."),
    ("ROOM-004", "Throne of Ruin", "The seat of the World Eater. The Boss Room."),
    ("ROOM-005", "The Last Gate", "A stairway of daylight. The real dungeon exit.")
]

# These saved passages make the dungeon a connected graph rather than a plain room list.
DEFAULT_CONNECTIONS = [
    # Original passage names are retained.
    ("ROOM-000", "ROOM-001", "Rusted Grate"),
    ("ROOM-001", "ROOM-002", "Crimson Gate"),
    ("ROOM-002", "ROOM-003", "Iron Drawbridge"),
    ("ROOM-003", "ROOM-004", "Throne Gate"),
    ("ROOM-004", "ROOM-005", "Sealed Exit Door")
]

# Only known built-in names and descriptions are migrated.
# Admin-customized values are left unchanged. This works with both
# the old original save files and the last themed-version save files.
# We recognize older built-in text so we can restore the correct names without overwriting custom names.
KNOWN_BUILTIN_ROOMS = {
    "ROOM-000": [
        ("Dungeon Entrance", "A cold stone gate where every expedition begins."),
        ("Dreadveil Entrance", "The mist-covered gateway where adventurers begin and recover after defeat.")],
    "ROOM-001": [
        ("Veilrot Sewers", "The cursed sewers beneath Dreadveil, where Weak guardians lurk in black mist.")],
    "ROOM-002": [
        ("Bloodstone Hall", "A crimson-lit chamber of Bloodstone guarded by Intermediate enemies.")],
    "ROOM-003": [
        ("Ashen Catacombs", "A ruined burial hall of shattered shields and Strong guardians.")],
    "ROOM-004": [
        ("Throne of Ruin", "The throne of Vharok, the World Eater, and the final Boss encounter.")],
    "ROOM-005": [
        ("The Last Gate", "The final passage out of Dreadveil, unsealed only when Vharok falls.")]
}
# We recognize earlier themed passage labels and can restore the original labels.
KNOWN_THEMED_PASSAGE_LABELS = {
    frozenset(("ROOM-000", "ROOM-001")): "Veilrot Grate",
    frozenset(("ROOM-002", "ROOM-003")): "Ashen Drawbridge",
    frozenset(("ROOM-004", "ROOM-005")): "Last Gate Archway"
}

# Each enemy has its own challenge question. Bonuses become stronger as the
# dungeon advances: Weak < Intermediate < Strong < Boss.
# The final boss uses question BQST-001.
BOSS_CHALLENGE_ID = "BQST-001"
# We assign each challenge question to an existing enemy.
DEFAULT_QUESTIONS = [
    # id, question, choices, correct answer, attack bonus, assigned enemy
    ("QST-001", "Which data structure follows First-In, First-Out (FIFO)?",
     ["Stack", "Queue", "Tree", "Graph"], 2, 10, "ENM-001"),
    ("QST-002", "Which data structure follows Last-In, First-Out (LIFO)?",
     ["Queue", "Array", "Stack", "Graph"], 3, 12, "ENM-002"),
    ("QST-003", "What adds an item to a stack?",
     ["Pop", "Push", "Peek", "Enqueue"], 2, 14, "ENM-003"),
    ("QST-004", "What removes an item from a stack?",
     ["Pop", "Push", "Peek", "Enqueue"], 1, 18, "ENM-004"),
    ("QST-005", "What adds an item to a queue?",
     ["Push", "Pop", "Enqueue", "Dequeue"], 3, 20, "ENM-005"),
    ("QST-006", "What removes an item from a queue?",
     ["Push", "Pop", "Enqueue", "Dequeue"], 4, 22, "ENM-006"),
    ("QST-007", "What connects vertices in a graph?",
     ["Root", "Edge", "Leaf", "Index"], 2, 28, "ENM-007"),
    ("QST-008", "What is the top node of a tree called?",
     ["Leaf", "Branch", "Root", "Edge"], 3, 32, "ENM-008"),
    ("QST-009", "Which tree traversal visits the root before its subtrees?",
     ["Inorder", "Postorder", "Preorder", "Level-order"], 3, 36, "ENM-009"),
    ("BQST-001", "Papasa ba ako sa Data Structure?",
     ["Oo", "Yes", "Syempre", "God is good!"], 4, 50, "BS-001")
]

# Standard bonus values for recognizing saved challenge question records.
LEGACY_QUESTION_BONUSES = {
    "QST-001": 10, "QST-002": 10, "QST-003": 15,
    "QST-004": 15, "QST-005": 15, "QST-006": 15,
    "QST-007": 20, "QST-008": 20, "QST-009": 50
}
DEFAULT_QUESTION_BY_ID = {record[0]: record for record in DEFAULT_QUESTIONS}


# ---------------------------------------------------------------
# LIVE RECORDS
# ---------------------------------------------------------------

# Stores all registered accounts (players and admins)
# Our dictionary stores all loaded player and admin profiles by username.
account_records = {}

# Information of the player who is currently logged in
# This holds the account that is currently logged in.
player = {}

# Enemy, item, equipment, room, connection and question records
# Our list contains enemy profiles the Queue and battles use.
mob_list = []
# We look up item effects and shop prices from this dictionary.
item_records = {}
# We look up equipment bonuses and shop prices using equipment IDs.
equipment_records = {}
# Our graph vertices are the room IDs in this dictionary.
room_records = {}
# Our graph edges are the passages between those rooms.
room_connections = []
# These question records are used during battle challenges.
question_records = []
# We keep each player's saved battle history and undo snapshots separate.
session_archive = {"next_action_number": 1, "next_account_numbers": {"PLY": 1, "ADM": 1}, "players": {}}
outcome_save_active = False
outcome_actions_pending = []
outcome_checkpoint = None

# Tracks changes to the saved dungeon room layout
ROOMS_RESET = False

# QUEUE: enemies of the current room, ordered from front to rear
# This list is our FIFO Queue: we add to the end and remove from index zero.
encounter_lineup = []

# STACK 1: log of every battle action (top = last item)
# We store actual battle events in the order they happened.
battle_history = []

# STACK 2: UNDO stack. A snapshot is pushed BEFORE each reversible action
# and popped when the player chooses Undo (LIFO).
# This is our LIFO Stack of reversible state snapshots.
undo_stack = []

# Stores the enemy currently being fought
# We use this ID to know which enemy is currently being fought.
current_enemy_id = None

# Gives each battle action its own ID
# This counter helps give each recorded battle action an ID.
action_counter = 0

# Temporary battle effects
boost_turns_left = 0
boost_percent = 0
guard_bonus_ready = False
enemy_stunned_turns = 0
challenge_used = False
boss_enrage_announced = False
battle_turns = 0

# The opening story is shown once per login session
intro_shown = False


# ---------------------------------------------------------------
# GENERAL HELPERS
# ---------------------------------------------------------------

# Draws the heading used by every screen so the menus have the same layout.
def header(txt):
    # Boxed title bar used by every screen
    # We print the same heading box on every screen so our menus look consistent.
    print()
    print(color("+" + "=" * 103 + "+", "cyan"))
    print(color("|" + f" {txt.upper()} ".center(103) + "|", "bold"))
    print(color("+" + "=" * 103 + "+", "cyan"))


# Stops the menu from changing until the player has read the result.
def pause():
    # We stop the screen here so the player has time to read the result.
    input("\nPress Enter to continue...")


# Prints menu options in columns instead of one long vertical list.
def print_menu_row(*options, width=26):
    # Prints menu options side by side in fixed-width columns
    # We arrange menu choices side by side instead of printing one option per line.
    print("".join(f"{option:<{width}}" for option in options).rstrip())


# Separates the options on a screen into smaller labeled groups.
def section(title):
    # Small coloured section title used inside menus
    # We use a smaller divider to separate parts of a long menu.
    print("\n" + color(f"-- {title} " + "-" * max(3, 101 - len(title)),
                       "yellow"))


# Wraps each story line inside a box and adds a short delay for the story effect.
def story_panel(title, lines, tone="cyan"):
    # Story box: shown for room entries, boss scenes and the ending.
    # It uses the same width as every screen header and table.
    # We wrap the story into a bordered panel and reveal it one line at a time.
    width = 105
    edge = "+" + "=" * (width - 2) + "+"

    print()
    print(color(edge, tone))
    print(color("| " + title.upper().center(width - 4) + " |", tone))
    print(color("+" + "-" * (width - 2) + "+", tone))

    for line in lines:
        for part in textwrap.wrap(line, width - 4) or [""]:
            print(color("| ", tone) + part.ljust(width - 4)
                  + color(" |", tone))
            wait(0.12)
        print(color("| " + " " * (width - 4) + " |", tone))

    print(color(edge, tone))


# Checks whether a table value looks numeric so it can be aligned properly.
def is_number_text(text):
    # True for values such as 55, 55/100, +30 or 75%
    # We check whether table values look numeric so the columns can be aligned correctly.
    digits = text.replace("/", "").replace("%", "").replace("+", "")
    return digits.replace("-", "", 1).isdigit()


# Measures column widths, wraps long cells, and builds the table one row at a time.
# The same function is used for records, rewards, and reports.
def table_lines(columns, rows, max_width=24):
    # Builds a bordered text table. Long values wrap onto extra lines,
    # "\n" starts a new line inside a cell, and number columns are
    # aligned to the right.
    # We calculate column widths, wrap long entries, and build one readable table.
    rows = [[str(value) for value in row] for row in rows]

    widths = []
    numeric = []

    for index, title in enumerate(columns):
        values = [row[index] for row in rows]
        longest = max(
            [len(part) for value in values for part in value.split("\n")],
            default=0
        )
        widths.append(max(len(title), min(longest, max_width)))
        numeric.append(bool(values) and all(
            is_number_text(value) or value == "-" for value in values
        ))

    # Splits a long table value into shorter lines that fit its column.
    def wrap_cell(value, width):
        lines = []

        for part in value.split("\n"):
            lines += textwrap.wrap(part, width) or [""]

        return lines

    # Adds the table borders around one row of text.
    def text_row(cells):
        return "| " + " | ".join(cells) + " |"

    border = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    lines = [
        border,
        text_row(f"{title:<{w}}" for title, w in zip(columns, widths)),
        border.replace("-", "=")
    ]

    wrapped_rows = [
        [wrap_cell(value, w) for value, w in zip(row, widths)]
        for row in rows
    ]
    multi_line = any(len(cell) > 1 for row in wrapped_rows for cell in row)

    for number, cells in enumerate(wrapped_rows):
        height = max(len(cell) for cell in cells)

        for line in range(height):
            parts = []

            for cell, w, right in zip(cells, widths, numeric):
                text = cell[line] if line < len(cell) else ""
                parts.append(f"{text:>{w}}" if right else f"{text:<{w}}")

            lines.append(text_row(parts))

        # Rows that wrap get a divider so each record stays readable
        if multi_line and number + 1 < len(wrapped_rows):
            lines.append(border)

    lines.append(border)
    return lines


# Adds optional row numbers and prints the table produced by table_lines().
def print_table(columns, rows, max_width=24, numbered=False):
    # We optionally number the rows before sending everything to our table printer.
    if numbered:
        columns = ["No."] + list(columns)
        rows = [[str(number)] + list(row)
                for number, row in enumerate(rows, 1)]
    for line in table_lines(columns, rows, max_width):
        print(line)


# Clears the terminal before opening another screen; Windows and other systems differ.
def clear_screen():
    # Clears the console so each menu starts on a fresh screen
    # We clear the previous menu before displaying the next one.
    os.system("cls" if os.name == "nt" else "clear")


INVALID_CHOICE_TEXT = "Invalid menu option. Please enter a valid choice."


# Shows the standard message whenever the user picks an unknown menu option.
def invalid_choice():
    # The menu is shown again right away, so no Enter press is needed
    # We reuse this message whenever someone chooses an option that does not exist.
    print(f"\n{INVALID_CHOICE_TEXT}")


# Gets the date and time used in battle records and saved activity.
def now_text():
    # We use the current date and time when saving action and battle history.
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Keeps asking for a nonempty value. On edit screens, Enter keeps the old value.
# It also rejects characters that would break the text-file record format.
def ask_text(prompt, default=None, banned="|"):
    # Asks for text that must not be blank. During updates, pressing
    # Enter keeps the current value (the default).
    # We keep asking until a required text field is valid; updates may keep their old value.
    # We repeat this menu or action until the player gives a valid choice or leaves.
    while True:
        value = input(prompt).strip()

        if not value and default is not None:
            return default

        if not value:
            print("Input must not be blank.")
            continue

        if any(ch in value for ch in banned):
            print(f"Input must not contain: {' '.join(banned)}")
            continue

        return value


# Converts typed input to an integer and repeats the question if it is invalid.
# Minimum and maximum limits prevent negative prices, impossible HP, and bad choices.
def ask_int(prompt, minimum=0, maximum=None, default=None):
    # Asks for a whole number inside the allowed range
    # We check that the input is a whole number within the allowed range.
    # We repeat this menu or action until the player gives a valid choice or leaves.
    while True:
        raw = input(prompt).strip()

        if not raw and default is not None:
            return default

        if not raw:
            print("Input must not be blank.")
            continue

        # We handle reading, conversion, or save errors here instead of letting one problem crash the program.
        try:
            value = int(raw)
        except ValueError:
            print("Please enter a whole number.")
            continue

        if value < minimum:
            print(f"The value must be at least {minimum}.")
            continue

        if maximum is not None and value > maximum:
            print(f"The value must not be greater than {maximum}.")
            continue

        return value


# Accepts Y or YES when the player confirms an action.
def ask_yes_no(prompt):
    # We accept Y or YES in either letter case as confirmation.
    return input(prompt).strip().lower() in ("y", "yes")


# Shows a numbered list and returns the item chosen by the user, not its number.
def ask_option(title, options, default=None):
    # Lets the user pick one value from a numbered list
    # We show numbered choices and return the actual selected value.
    print(title)

    for number, option in enumerate(options, 1):
        print(f"  [{number}] {option}")

    default_number = None

    if default in options:
        default_number = options.index(default) + 1

    suffix = f" [{default_number}]" if default_number else ""
    number = ask_int(
        f"Choose [1-{len(options)}]{suffix}: ",
        1,
        len(options),
        default_number
    )

    return options[number - 1]


# Looks at existing IDs and chooses the next available number for a new record.
# Player/admin IDs use a separate saved counter so deleted account IDs are not reused.
def next_record_id(prefix, existing_ids, start=1):
    # Creates the next unique ID such as ENM-011
    # We look for the highest existing number so the next record ID does not duplicate it.
    highest = start - 1

    for record_id in existing_ids:
        if record_id.startswith(prefix + "-"):
            # We handle reading, conversion, or save errors here instead of letting one problem crash the program.
            try:
                highest = max(highest, int(record_id.split("-")[1]))
            except (ValueError, IndexError):
                pass

    return f"{prefix}-{highest + 1:03d}"


# Converts current HP into filled and empty characters for the health bar.
def hp_bar(current, maximum, width=20):
    # Draws a small health bar for the battle screen
    # We convert the health percentage into filled and empty parts of a text bar.
    if maximum <= 0:
        return "[" + " " * width + "]"

    filled = round(width * max(0, current) / maximum)
    return "[" + "#" * filled + "." * (width - filled) + "]"


# ---------------------------------------------------------------
# BATTLE ANIMATIONS
# Small text animations that make the battle screen feel alive.
# They are skipped when the output is not a real terminal.
# ---------------------------------------------------------------

ANIMATIONS_ON = sys.stdout.isatty()

if os.name == "nt":
    # Turns on colour codes in the Windows console
    os.system("")

COLORS = {
    "red": "\033[91m", "green": "\033[92m", "yellow": "\033[93m",
    "blue": "\033[94m", "magenta": "\033[95m", "cyan": "\033[96m",
    "bold": "\033[1m", "reset": "\033[0m"
}


# Chooses the health-bar color based on how much HP is left.
def hp_color(current, maximum):
    # Green when healthy, yellow when hurt, red when in danger
    # We pick the health-bar color based on how much HP remains.
    percent = current * 100 // maximum if maximum > 0 else 0

    if percent > 60:
        return "green"
    return "yellow" if percent >= 30 else "red"


# Adds terminal colors only when the terminal supports animations.
def color(text, name):
    # We only print ANSI color codes when the current terminal supports animations.
    if not ANIMATIONS_ON:
        return text
    return f"{COLORS[name]}{text}{COLORS['reset']}"


# Skips animation delays when output is redirected or the game is being tested.
def wait(seconds):
    # We skip animation delays when the program is running without an interactive terminal.
    if ANIMATIONS_ON:
        time.sleep(seconds)


# Replaces the current terminal line to make the attack animation move.
def draw_line(text):
    # Redraws the current console line in place
    # We redraw one console line to create the moving battle effect.
    sys.stdout.write("\r\033[K" + text)
    sys.stdout.flush()


# Displays story text one character at a time in an interactive terminal.
def type_out(text, delay=0.02, name=None):
    # Prints text one letter at a time
    # We print letters gradually during animations but use normal printing in tests.
    if not ANIMATIONS_ON:
        print(text)
        return

    for letter in text:
        sys.stdout.write(color(letter, name) if name else letter)
        sys.stdout.flush()
        time.sleep(delay)
    print()


# Moves an attack symbol toward the enemy and shows miss or critical effects.
def animate_strike(attacker, target, missed=False, critical=False):
    # A projectile flies from the attacker to the target
    # We animate the attack moving toward the target and show a different result for misses or critical hits.
    if not ANIMATIONS_ON:
        return

    gap = 24
    shot = "==>>" if critical else "-->"

    for step in range(0, gap - len(shot) + 1, 2):
        lane = " " * step + shot + " " * (gap - len(shot) - step)
        draw_line(f"  {attacker} {color(lane, 'yellow')} {target}")
        time.sleep(0.025)

    if missed:
        draw_line(f"  {attacker} {' ' * gap} {target}  "
                  + color("~ whoosh ~", "cyan"))
        time.sleep(0.35)
    else:
        burst = "*CRITICAL*" if critical else "*SLASH*"
        # The target flashes and shakes when it is hit
        for offset in (0, 2, 0, 2, 0):
            draw_line(f"  {attacker} {' ' * (gap + offset)} "
                      + color(f"{target} {burst}", "red"))
            time.sleep(0.07)
        time.sleep(0.15)

    draw_line("")


# Animates the health bar from the old HP to the new HP after damage or healing.
def animate_hp_change(label, before, after, maximum, width=20):
    # Drains (or refills) the health bar a little at a time
    # We move from the old HP value to the new HP value in several small steps.
    if not ANIMATIONS_ON or before == after:
        return

    bar_color = "green" if after > before else "red"
    frames = 12

    for frame in range(1, frames + 1):
        value = round(before + (after - before) * frame / frames)
        draw_line(f"  {label}: "
                  + color(hp_bar(value, maximum, width), bar_color)
                  + f" {value}/{maximum} HP")
        time.sleep(0.04)

    print()


# Shows a short effect animation for potions, guards, and status changes.
def animate_effect(text, name, symbol="*", frames=6):
    # Short sparkle used for potions, guards and status effects
    # We show a short sparkle message for an item or special combat effect.
    if not ANIMATIONS_ON:
        return

    for frame in range(frames):
        pad = symbol * (frame % 3 + 1)
        draw_line(color(f"  {pad} {text} {pad}", name))
        time.sleep(0.09)

    draw_line("")


# Shows the player and enemy facing each other before the fight starts.
def animate_battle_intro(mob):
    # "VS" splash shown when a battle starts
    # We show the player and the enemy facing each other before combat.
    if not ANIMATIONS_ON:
        return

    name = "PLAYER"
    for gap in range(30, 3, -3):
        draw_line(color(name, "cyan") + " " * gap
                  + color("VS", "bold") + " " * gap
                  + color(mob["name"].upper(), "red"))
        time.sleep(0.04)

    for _ in range(3):
        draw_line(color(f"{name}   >>  VS  <<   {mob['name'].upper()}",
                        "yellow"))
        time.sleep(0.12)
        draw_line(f"{name}   >>  VS  <<   {mob['name'].upper()}")
        time.sleep(0.12)

    print()


# Prints the victory or defeat banner; flashing is optional for non-terminal output.
def animate_banner(text, name):
    # Big blinking banner for victory and defeat
    # We display a noticeable victory or defeat title without changing any game stats.
    border = "+" + "-" * (len(text) + 6) + "+"
    middle = f"|   {text}   |"

    if ANIMATIONS_ON:
        for _ in range(3):
            draw_line(color(middle, name))
            time.sleep(0.15)
            draw_line(" " * len(middle))
            time.sleep(0.1)
        draw_line("")

    print(color(border, name))
    print(color(middle, name))
    print(color(border, name))


# ---------------------------------------------------------------
# FILE HANDLING
# ---------------------------------------------------------------

# Reads a saved text file into fields separated by the vertical bar (|).
# Header lines and blank lines are ignored so only actual records are loaded.
def read_record_rows(path):
    # Reads a "|" separated text file. Missing files return no rows.
    # We load pipe-separated TXT records and ignore blank lines and column headers.
    rows = []

    if not Path(path).exists():
        return rows

    # We handle reading, conversion, or save errors here instead of letting one problem crash the program.
    try:
        # We use a file context here so the file is properly closed after reading or writing.
        with open(path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                rows.append([part.strip() for part in line.split("|")])

    except OSError:
        print(f"\nThere was a problem reading {path}.")

    return rows


# Builds a readable table-shaped text string for writing a record file.
def render_record_rows(title, columns, rows):
    # We turn our record values into a readable TXT table with column names.
    names = columns.split("|")
    texts = [[str(value) for value in row] for row in rows]
    widths = [
        max([len(name)] + [len(row[i]) for row in texts if i < len(row)])
        for i, name in enumerate(names)
    ]

    # Adds spaces so the values line up with the text-file column headings.
    def padded(values):
        return " | ".join(
            value.ljust(widths[i]) if i < len(widths) else value
            for i, value in enumerate(values)
        ).rstrip()

    return (f"# {title}\n# {padded(names)}\n"
            + "".join(f"  {padded(row)}\n" for row in texts))


# Writes new data to temporary files first instead of replacing saves immediately.
# If one replacement fails, it restores the old files to avoid half-saved results.
# A backup session file is also attempted if the normal session path cannot be saved.
def atomic_record_updates(updates, allow_session_recovery=True):
    # We save several related files together and restore their old versions if a write fails.
    # Our TXT and JSON files are separate, so we first write temporary copies before replacing anything.
    # If one replace operation fails, we use the backups to put earlier records back.
    pending = {str(k): v for k, v in updates.items()}
    for attempt in range(2):
        temporary = {}
        backups = {}
        changed = []
        failed_path = None
        # We handle reading, conversion, or save errors here instead of letting one problem crash the program.
        try:
            # Write each new file in the same directory first so it can be replaced
            # safely.
            for name, content in pending.items():
                target = Path(name)
                # We use a file context here so the file is properly closed after reading or writing.
                with tempfile.NamedTemporaryFile(
                        mode="w", encoding="utf-8", prefix=".dreadveil_",
                        suffix=".tmp", dir=str(target.parent), delete=False) as file:
                    temporary[name] = Path(file.name)
                    file.write(content)
                    file.flush()
                    # We flush the write to disk before treating the temporary file as ready.
                    os.fsync(file.fileno())
                if target.exists():
                    # We use a file context here so the file is properly closed after reading or writing.
                    with tempfile.NamedTemporaryFile(
                            prefix=".dreadveil_backup_", suffix=".tmp",
                            dir=str(target.parent), delete=False) as backup:
                        backups[name] = Path(backup.name)
                    # We keep the previous file so we can restore it if another write fails.
                    shutil.copyfile(target, backups[name])
                else:
                    backups[name] = None
            # Only replace the original files after all temporary copies are complete.
            for name, staged in temporary.items():
                failed_path = name
                # We replace the destination with the finished temporary file only after writing succeeds.
                os.replace(staged, name)
                changed.append(name)
            if BATTLE_SESSION_FILE in pending:
                alternate = Path(BATTLE_SESSION_FILE).with_name(
                    Path(BATTLE_SESSION_FILE).stem + ".recovery.json")
                if str(alternate) not in pending:
                    # We handle reading, conversion, or save errors here instead of letting one problem crash the program.
                    try:
                        alternate.unlink(missing_ok=True)
                    except OSError:
                        pass
            return True
        except OSError as error:
            rollback_ok = True
            # If a write fails, put the earlier versions back in reverse order.
            for name in reversed(changed):
                # We handle reading, conversion, or save errors here instead of letting one problem crash the program.
                try:
                    if backups[name] is None:
                        Path(name).unlink(missing_ok=True)
                    else:
                        os.replace(backups[name], name)
                except OSError:
                    rollback_ok = False
                    print(f"Unable to restore the earlier copy of {name}.")
            if not rollback_ok:
                print("Some files could not be rolled back. Check backups before continuing.")
                return False
            if (allow_session_recovery and attempt == 0 and
                    failed_path == BATTLE_SESSION_FILE):
                recovered = str(Path(BATTLE_SESSION_FILE).with_name(
                    Path(BATTLE_SESSION_FILE).stem + ".recovery.json"))
                pending[recovered] = pending.pop(BATTLE_SESSION_FILE)
                continue
            print(f"Unable to save records: {error}")
            return False
        finally:
            for candidate in list(temporary.values()) + [b for b in backups.values() if b]:
                # We handle reading, conversion, or save errors here instead of letting one problem crash the program.
                try:
                    candidate.unlink(missing_ok=True)
                except OSError:
                    pass
    return False


# Uses the common file format and saves the generated record text.
def write_record_rows(path, title, columns, rows, content_only=False):
    # Writes records into a "|" separated text file. The columns are
    # padded so the file reads like a table (spaces are ignored when
    # the file is loaded again).
    # We prepare a TXT file and either return its text or save it immediately.
    content = render_record_rows(title, columns, rows)
    if content_only:
        return content
    return atomic_record_updates({path: content})

# Changes the inventory dictionary into item ID and quantity pairs for saving.
def inventory_to_text(inventory):
    # We write item quantities as item-ID and quantity pairs inside an account record.
    return ",".join(
        f"{item_id}:{qty}"
        for item_id, qty in inventory.items()
        if qty > 0
    )


# Converts saved item quantities back into a dictionary and ignores bad entries.
def inventory_from_text(text):
    # We rebuild the player's item quantities from the saved account text.
    inventory = {}

    for entry in text.split(","):
        if ":" not in entry:
            continue

        item_id, qty = entry.split(":", 1)

        # We handle reading, conversion, or save errors here instead of letting one problem crash the program.
        try:
            qty = int(qty)
        except ValueError:
            continue

        if qty > 0:
            inventory[item_id.strip()] = qty

    return inventory


# Splits comma-separated IDs and removes empty entries from saved lists.
def id_list_from_text(text):
    # We turn a comma-separated list of saved IDs into a Python list.
    return [x.strip() for x in text.split(",") if x.strip()]


# Stores each equipment slot and its selected item ID in a short text value.
def equipped_to_text(equipped):
    # Example: sword=EQP-001;shield=EQP-003
    # We save the currently equipped item IDs beside their sword, shield, or armor slots.
    return ";".join(f"{slot}={eid}" for slot, eid in equipped.items() if eid)


# Reads equipped-item values and ignores slots the game does not recognize.
def equipped_from_text(text):
    # We read the saved slot assignments and ignore invalid slot names.
    equipped = {}

    for entry in text.split(";"):
        if "=" in entry:
            slot, eid = entry.split("=", 1)

            if slot.strip() in EQUIPMENT_SLOTS and eid.strip():
                equipped[slot.strip()] = eid.strip()

    return equipped


# ----- Accounts -----

# Creates the starting values for a new player or administrator account.
# All the fields are included here so every new account has the same structure.
def new_account_data(player_id, password, role="Player"):
    # Creates an account using the starting player stats
    # We prepare every field a new account needs, including progress, inventory, and location.
    return {
        "id": player_id,
        "password": password,
        "role": role,
        "hp": STARTING_STATS["hp"],
        "max_hp": STARTING_STATS["max_hp"],
        "atk": STARTING_STATS["atk"],
        "gold": STARTING_STATS["gold"] if role == "Player" else 0,
        "score": 0,
        "wins": 0,
        "losses": 0,
        "status": "Active",
        "defeated_ids": [],
        "completed_levels": [],
        "inventory": dict(STARTING_ITEMS) if role == "Player" else {},
        "lineup": [],
        "wounds": {},
        "owned_equipment": [],
        "equipped": {},
        "location": ENTRANCE_ROOM_ID,
        "treasures": []
    }


# Creates the first admin and player accounts when there is no account file yet.
def create_default_accounts():
    # Creates the first account file if none exists yet
    # We create starter admin and player profiles only when there are no saved accounts.
    account_records.clear()
    player_number = 0

    for (username, password, role, hp, max_hp, atk, gold, score, wins,
         losses, defeated, completed, inventory) in DEFAULT_ACCOUNTS:

        if role == "Admin":
            player_id = "ADM-001"
        else:
            player_number += 1
            player_id = f"PLY-{player_number:03d}"

        data = new_account_data(player_id, password, role)
        data.update({
            "hp": hp, "max_hp": max_hp, "atk": atk, "gold": gold,
            "score": score, "wins": wins, "losses": losses,
            "defeated_ids": list(defeated),
            "completed_levels": list(completed),
            "inventory": dict(inventory)
        })
        account_records[username] = data

    save_all_accounts()


# Turns one current-format account record into the fields used by the game.
def parse_account_row(parts):
    # Current format: role, inventory, saved queue, wounds, equipment, room
    # We read one current-format account row and convert numeric and list fields back into Python values.
    return parts[0], {
        "id": parts[1],
        "password": parts[2],
        "role": parts[3] if parts[3] in ("Admin", "Player") else "Player",
        "hp": int(parts[4]),
        "max_hp": int(parts[5]),
        "atk": int(parts[6]),
        "gold": int(parts[7]),
        "score": int(parts[8]),
        "wins": int(parts[9]),
        "losses": int(parts[10]),
        "status": parts[11],
        "defeated_ids": id_list_from_text(parts[12]),
        "completed_levels": id_list_from_text(parts[13]),
        "inventory": inventory_from_text(parts[14]),
        "lineup": id_list_from_text(parts[15]) if len(parts) > 15 else [],
        "wounds": inventory_from_text(parts[16]) if len(parts) > 16 else {},
        "owned_equipment": (
            id_list_from_text(parts[17]) if len(parts) > 17 else []
        ),
        "equipped": (
            equipped_from_text(parts[18]) if len(parts) > 18 else {}
        ),
        "location": (
            parts[19] if len(parts) > 19 and parts[19] else ENTRANCE_ROOM_ID
        ),
        "treasures": id_list_from_text(parts[20]) if len(parts) > 20 else []
    }


# Reads older account records so players can still use previous save formats.
def parse_legacy_account_row(parts):
    # Reads account rows containing fixed inventory fields
    # We convert a supported older account layout into the fields our current game uses.
    data = new_account_data(parts[1], parts[2])
    data.update({
        "hp": int(parts[3]),
        "max_hp": int(parts[4]),
        "atk": int(parts[5]),
        "score": int(parts[10]),
        "gold": int(parts[11]),
        "wins": int(parts[12]),
        "losses": int(parts[13]),
        "status": parts[14],
        "defeated_ids": id_list_from_text(parts[15]),
        "completed_levels": (
            id_list_from_text(parts[16]) if len(parts) > 16 else []
        ),
        "inventory": {}
    })

    for column, item_id in zip(range(6, 10), DEFAULT_ITEMS):
        qty = int(parts[column])

        if qty > 0:
            data["inventory"][item_id[0]] = qty

    return parts[0], data


# Loads saved accounts and skips records that cannot be parsed.
# It also repairs old item/status values and creates a default admin if needed.
def load_accounts():
    # Loads all saved accounts from the text file
    # We read all valid accounts, clean outdated values, and restore default accounts only when needed.
    account_records.clear()

    # Read accounts one at a time, so a damaged row does not stop all logins.
    for parts in read_record_rows(ACCOUNT_FILE):
        # We handle reading, conversion, or save errors here instead of letting one problem crash the program.
        try:
            if len(parts) in range(15, 22) and not parts[3].isdigit():
                username, data = parse_account_row(parts)
            elif len(parts) in (16, 17):
                username, data = parse_legacy_account_row(parts)
            else:
                continue
        except (ValueError, IndexError):
            continue

        if username and username not in account_records:
            account_records[username] = data

    # Remove inventory entries that have no matching item record.
    legacy_data_cleaned = False
    # We check each related saved record so this result uses actual game data.
    for data in account_records.values():
        inventory = data.get("inventory", {})
        for item_id in list(inventory):
            if item_id not in item_records:
                inventory.pop(item_id)
                legacy_data_cleaned = True
        if data["status"] == "Escaped":
            data["status"] = "Retreated"
            legacy_data_cleaned = True

    if legacy_data_cleaned:
        save_all_accounts()

    # Create starter profiles only when no valid saved accounts were loaded.
    # We make default accounts only if there are no saved accounts to load.
    if not account_records:
        create_default_accounts()
        return

    # Ensure an administrator account is available
    if not any(d["role"] == "Admin" for d in account_records.values()):
        if "admin" not in account_records:
            account_records["admin"] = new_account_data(
                "ADM-001", "admin123", "Admin"
            )
            save_all_accounts()


# Collects the latest account data and writes it to the player account file.
def save_all_accounts(content_only=False):
    # Saves all registered accounts into the account file
    # We write the current accounts and progress back into the player-account TXT file.
    rows = []

    # We check each related saved record so this result uses actual game data.
    for username, data in account_records.items():
        rows.append([
            username, data["id"], data["password"], data["role"],
            data["hp"], data["max_hp"], data["atk"], data["gold"],
            data["score"], data["wins"], data["losses"], data["status"],
            ",".join(data.get("defeated_ids", [])),
            ",".join(data.get("completed_levels", [])),
            inventory_to_text(data.get("inventory", {})),
            ",".join(data.get("lineup", [])),
            inventory_to_text(data.get("wounds", {})),
            ",".join(data.get("owned_equipment", [])),
            equipped_to_text(data.get("equipped", {})),
            data.get("location", ENTRANCE_ROOM_ID),
            ",".join(data.get("treasures", []))
        ])

    text = render_record_rows(
        "DREADVEIL: THE LAST GATE PLAYER ACCOUNTS",
        "username|player_id|password|role|hp|max_hp|atk|gold|score|wins|"
        "losses|status|defeated_enemy_ids|completed_levels|inventory|"
        "encounter_queue|wounded_enemy_hp|owned_equipment|equipped|"
        "current_room|treasures_opened",
        rows
    )
    if content_only:
        return text
    return atomic_record_updates({ACCOUNT_FILE: text})


# ----- Enemies -----

# Creates an enemy dictionary using the stats entered by the admin or starter records.
def make_enemy(enemy_id, name, enemy_type, max_hp, atk, gold, score, room):
    # We build an enemy record with its starting HP, difficulty, rewards, and room.
    return {
        "id": enemy_id,
        "name": name,
        "type": enemy_type,
        "max_hp": max_hp,
        "hp": max_hp,
        "atk": atk,
        "gold_reward": gold,
        "score_reward": score,
        "room": room,
        "defeated": False,
        "engaged": False
    }


# Keeps each enemy in the room assigned to its difficulty level.
def sync_enemy_rooms():
    # Every difficulty level lives in exactly one room
    # We keep each enemy in the room assigned to its difficulty.
    changed = False

    # We check each related saved record so this result uses actual game data.
    for mob in mob_list:
        target = ROOM_FOR_DIFFICULTY[mob["type"]]

        if mob["room"] != target:
            mob["room"] = target
            changed = True

    if changed:
        save_enemies()


# Loads unique enemy records, validates the difficulty, and creates defaults if empty.
def load_enemies():
    # We read the enemy profiles from disk and create the starter enemies if the file has no valid records.
    mob_list.clear()

    for parts in read_record_rows(ENEMY_FILE):
        if len(parts) != 8 or parts[2] not in DIFFICULTY_ORDER:
            continue

        if get_enemy_by_id(parts[0]) is not None:
            continue

        # We handle reading, conversion, or save errors here instead of letting one problem crash the program.
        try:
            mob_list.append(make_enemy(
                parts[0], parts[1], parts[2], int(parts[3]),
                int(parts[4]), int(parts[5]), int(parts[6]), parts[7]
            ))
        except ValueError:
            continue

    # We use the starter enemies only when the saved enemy list is empty.
    if not mob_list:
        for record in DEFAULT_ENEMIES:
            mob_list.append(make_enemy(*record))
        save_enemies()

    sync_enemy_rooms()


# Saves all enemy profiles and the gold/score values used in battles.
def save_enemies(content_only=False):
    # We write current enemy profiles to the TXT file used by our admin menu.
    return write_record_rows(
        ENEMY_FILE,
        "DREADVEIL: THE LAST GATE ENEMY RECORDS",
        "enemy_id|name|difficulty|max_hp|atk|gold_reward|score_reward|room_id",
        [
            [m["id"], m["name"], m["type"], m["max_hp"], m["atk"],
             m["gold_reward"], m["score_reward"], m["room"]]
            for m in mob_list
        ],
        content_only=content_only
    )


# ----- Items -----

# Loads usable item profiles and removes old item types the game no longer supports.
def load_items():
    # We read usable items and skip unsupported or duplicate item records.
    item_records.clear()

    legacy_escape_items_removed = False

    for parts in read_record_rows(ITEM_FILE):
        if len(parts) == 7 and parts[2] == "escape":
            legacy_escape_items_removed = True
            continue
        if len(parts) != 7 or parts[2] not in ITEM_EFFECTS:
            continue

        if parts[0] in item_records:
            continue

        # We handle reading, conversion, or save errors here instead of letting one problem crash the program.
        try:
            item_records[parts[0]] = {
                "id": parts[0],
                "name": parts[1],
                "effect": parts[2],
                "power": int(parts[3]),
                "price": int(parts[4]),
                "max_carry": int(parts[5]),
                "description": parts[6]
            }
        except ValueError:
            continue

    # We create starter items only when no usable saved items were loaded.
    if not item_records:
        for (item_id, name, effect, power, price, carry,
             description) in DEFAULT_ITEMS:
            item_records[item_id] = {
                "id": item_id, "name": name, "effect": effect,
                "power": power, "price": price, "max_carry": carry,
                "description": description
            }
        save_items()
    elif legacy_escape_items_removed:
        save_items()


# Saves the item stats, prices, carry limits, and effects used in shops and battles.
def save_items(content_only=False):
    # We save item effects, prices, carrying limits, and descriptions.
    return write_record_rows(
        ITEM_FILE,
        "DREADVEIL: THE LAST GATE ITEM RECORDS",
        "item_id|name|effect|power|price|max_carry|description",
        [
            [i["id"], i["name"], i["effect"], i["power"], i["price"],
             i["max_carry"], i["description"]]
            for i in item_records.values()
        ],
        content_only=content_only
    )


# ----- Equipment -----

# Sorts equipment by tier, slot, and stats for a consistent shop display.
def ordered_equipment_records(items):
    # We sort equipment by difficulty and slot so the shop stays easy to browse.
    tier_positions = {tier: index for index, tier in enumerate(EQUIPMENT_LEVELS)}
    slot_positions = {slot: index for index, slot in enumerate(EQUIPMENT_SLOTS)}
    return sorted(items, key=lambda e: (
        tier_positions.get(e["tier"], len(tier_positions)),
        slot_positions.get(e["slot"], len(slot_positions)),
        e["bonus"], e.get("speed", 0), e["id"]
    ))


# Loads equipment and checks that its slot and tier belong to the allowed choices.
def load_equipment():
    # We rebuild equipment records, including sword speed when the saved format contains it.
    equipment_records.clear()

    for parts in read_record_rows(EQUIPMENT_FILE):
        if len(parts) not in (7, 8):
            continue
        if parts[2] not in EQUIPMENT_SLOTS:
            continue
        if parts[3] not in TIER_UNLOCK_REQUIREMENT:
            continue
        if parts[0] in equipment_records:
            continue

        # We handle reading, conversion, or save errors here instead of letting one problem crash the program.
        try:
            equipment_records[parts[0]] = {
                "id": parts[0], "name": parts[1], "slot": parts[2],
                "tier": parts[3], "bonus": int(parts[4]),
                "price": int(parts[5]), "description": parts[6],
                "speed": int(parts[7]) if len(parts) == 8 else 0
            }
        except ValueError:
            continue

    # We restore the default equipment catalog only when necessary.
    if not equipment_records:
        for (eid, name, slot, tier, bonus, price,
             description, speed) in DEFAULT_EQUIPMENT:
            equipment_records[eid] = {
                "id": eid, "name": name, "slot": slot, "tier": tier,
                "bonus": bonus, "price": price, "description": description,
                "speed": speed
            }
        save_equipment()


# Writes the equipment catalog in the same sorted order used on screen.
def save_equipment(content_only=False):
    # We write equipment records in a consistent order.
    return write_record_rows(
        EQUIPMENT_FILE,
        "DREADVEIL: THE LAST GATE EQUIPMENT RECORDS",
        "equipment_id|name|slot|tier|bonus|price|description|speed",
        [
            [e["id"], e["name"], e["slot"], e["tier"], e["bonus"],
             e["price"], e["description"], e.get("speed", 0)]
            for e in ordered_equipment_records(equipment_records.values())
        ],
        content_only=content_only
    )


# ----- Rooms and connections (graph) -----

# Loads the six required room records. Missing or extra room IDs reset to the route.
# Room names/descriptions may still be edited without changing those required IDs.
def load_rooms():
    # Verify that saved rooms match the required six-room dungeon layout.
    # We load the six built-in rooms and update recognized old names without overwriting custom admin changes.
    # ROOM-000 is called Dreadveil Entrance; the other five original names stay as saved.
    # We only update a recognized built-in old name, not a custom name chosen by the admin.
    global ROOMS_RESET

    # We reset the room dictionary before rebuilding it from the selected records.
    room_records.clear()
    ROOMS_RESET = False

    for parts in read_record_rows(ROOM_FILE):
        if len(parts) != 3 or parts[0] in room_records:
            continue

        room_records[parts[0]] = {
            "id": parts[0], "name": parts[1], "description": parts[2]
        }

    # The dungeon uses six fixed room IDs; the names can still be customized.
    if set(room_records) != set(ROOM_ORDER):
        room_records.clear()

        for room_id, name, description in DEFAULT_ROOMS:
            room_records[room_id] = {
                "id": room_id, "name": name, "description": description
            }

        ROOMS_RESET = True
        save_rooms()

    # Keeps the rooms in route order
    ordered = {r: room_records[r] for r in ROOM_ORDER}
    room_records.clear()
    room_records.update(ordered)

    # Normalize only known built-in room labels from either earlier version.
    # A manually customized name or description is always preserved.
    names_changed = False
    defaults = {room_id: (name, description)
                for room_id, name, description in DEFAULT_ROOMS}
    for room_id, record in room_records.items():
        new_name, new_description = defaults[room_id]
        for old_name, old_description in KNOWN_BUILTIN_ROOMS[room_id]:
            if record["name"] == old_name and old_name != new_name:
                record["name"] = new_name
                names_changed = True
            if (record["description"] == old_description
                    and old_description != new_description):
                record["description"] = new_description
                names_changed = True
    if names_changed:
        save_rooms()


# Saves the room vertices used by both the dungeon map and the travel system.
def save_rooms():
    # We save the room names and descriptions that the graph uses.
    return write_record_rows(
        ROOM_FILE,
        "DREADVEIL: THE LAST GATE ROOM RECORDS (GRAPH VERTICES)",
        "room_id|name|description",
        [[r["id"], r["name"], r["description"]]
         for r in room_records.values()]
    )


# Loads the room passages and keeps only connections allowed by the route rules.
def load_connections():
    # We load saved passages, keep valid room links, and restore default passages if necessary.
    # We accept only passages that connect real rooms and meet the graph rules.
    # The passage labels come from saved data, so changing a label also changes what the map shows.
    # We clear old graph edges before rebuilding the current passage list.
    room_connections.clear()
    file_existed = Path(CONNECTION_FILE).exists()

    # Keep valid saved passages when an existing map is loaded.
    if file_existed and not ROOMS_RESET:
        for parts in read_record_rows(CONNECTION_FILE):
            if len(parts) != 3:
                continue

            # Only valid links between existing rooms are kept
            if validate_connection(parts[0], parts[1]) is None:
                room_connections.append(
                    {"a": parts[0], "b": parts[1], "label": parts[2]}
                )

    # Use the starter passages only when the map was reset or is missing.
    if ROOMS_RESET or not file_existed:
        room_connections.clear()

        for room_a, room_b, label in DEFAULT_CONNECTIONS:
            if validate_connection(room_a, room_b) is None:
                room_connections.append(
                    {"a": room_a, "b": room_b, "label": label}
                )

        save_connections()
    else:
        # Reverse the last version's thematic passage renames only.
        # Retain any manually customized passage labels.
        new_labels = {frozenset((a, b)): label for a, b, label
                      in DEFAULT_CONNECTIONS}
        # Older built-in labels are updated, but custom admin labels should remain
        # untouched.
        changed_labels = False
        # We check each related saved record so this result uses actual game data.
        for connection in room_connections:
            key = frozenset((connection["a"], connection["b"]))
            old_theme_label = KNOWN_THEMED_PASSAGE_LABELS.get(key)
            if (old_theme_label is not None and key in new_labels
                    and connection["label"] == old_theme_label):
                connection["label"] = new_labels[key]
                changed_labels = True
        if changed_labels:
            save_connections()


# Saves the passage labels and connected room IDs used in graph operations.
def save_connections():
    # We save our graph edges with both room IDs and the passage name.
    return write_record_rows(
        CONNECTION_FILE,
        "DREADVEIL: THE LAST GATE ROOM CONNECTIONS (GRAPH EDGES, TWO-WAY)",
        "room_a|room_b|passage_name",
        [[c["a"], c["b"], c["label"]] for c in room_connections]
    )


# ----- Challenge questions -----

# Finds the challenge question assigned to the selected enemy.
def question_for_enemy(mob):
    # We find the question assigned to the selected enemy.
    # We stop here if the enemy ID does not match an existing enemy.
    if mob is None:
        return None
    if mob["type"] == "Boss":
        return next((q for q in question_records
                     if q["id"] == BOSS_CHALLENGE_ID), None)
    pool = [q for q in question_records if q.get("difficulty") == mob["type"]]
    return random.choice(pool) if pool else None


# Loads challenge questions and checks their answer choices and enemy links.
def load_questions():
    # We load challenge questions and check that their enemy references are usable.
    question_records.clear()
    changed = False
    for parts in read_record_rows(QUESTION_FILE):
        if len(parts) not in (5, 6):
            continue
        choices = [c.strip() for c in parts[2].split(";")]
        # We handle reading, conversion, or save errors here instead of letting one problem crash the program.
        try:
            answer = int(parts[3])
            bonus = int(parts[4])
        except ValueError:
            continue
        if len(choices) != 4 or any(not c for c in choices) or not 1 <= answer <= 4 or bonus < 0:
            continue
        if any(q["id"] == parts[0] for q in question_records):
            continue
        default = DEFAULT_QUESTION_BY_ID.get(parts[0])
        category = parts[5].strip() if len(parts) == 6 else ""
        if category.startswith("ENM-"):
            mob = get_enemy_by_id(category)
            category = mob["type"] if mob else ""
            changed = True
        if not category and default:
            mob = get_enemy_by_id(default[5])
            category = mob["type"] if mob else ""
            changed = True
        if category not in LEVEL_ORDER:
            continue
        if parts[0] == BOSS_CHALLENGE_ID:
            changed = True
            continue
        if category == "Boss":
            continue
        question_records.append({"id": parts[0], "question": parts[1],
                                 "choices": choices, "answer": answer,
                                 "bonus": bonus, "difficulty": category})

    for level in ("Weak", "Intermediate", "Strong"):
        if not any(q["difficulty"] == level for q in question_records):
            for default in DEFAULT_QUESTIONS:
                mob = get_enemy_by_id(default[5])
                if mob and mob["type"] == level:
                    used = {q["id"] for q in question_records}
                    qid = default[0] if default[0] not in used else next_record_id("QST", used)
                    question_records.append({"id": qid, "question": default[1],
                                             "choices": list(default[2]),
                                             "answer": default[3], "bonus": default[4],
                                             "difficulty": level})
                    changed = True

    boss = DEFAULT_QUESTION_BY_ID[BOSS_CHALLENGE_ID]
    question_records.append({"id": boss[0], "question": boss[1],
                             "choices": list(boss[2]), "answer": boss[3],
                             "bonus": boss[4], "difficulty": "Boss"})
    question_records.sort(key=lambda q: (LEVEL_ORDER.index(q["difficulty"]), q["id"]))
    if changed or not Path(QUESTION_FILE).exists():
        save_questions()


# Saves the questions, correct answers, and extra damage bonuses.
def save_questions():
    # We write question text, answer choices, correct answers, and bonuses.
    return write_record_rows(
        QUESTION_FILE, "DREADVEIL: THE LAST GATE CHALLENGE QUESTIONS",
        "question_id|question|choices_separated_by_semicolon|"
        "correct_choice_number|bonus_damage|difficulty",
        [[q["id"], q["question"], ";".join(q["choices"]), q["answer"],
          q["bonus"], q["difficulty"]] for q in question_records]
    )


# Restores saved battle sessions, undo snapshots, and action-number counters.
# The newest readable save or recovery file is used; older activity logs are also
# checked.
# This avoids restarting action numbers after reopening the game.
def load_session_archive():
    # We restore battle sessions, undo states, and ID counters from the JSON file or its recovery copy.
    # We prefer the newest usable JSON copy and check its shape before trusting the values.
    # We also scan older logs so action IDs remain unique across game sessions.
    global session_archive
    session_archive = {"next_action_number": 1,
                       "next_account_numbers": {"PLY": 1, "ADM": 1},
                       "players": {}}
    path = Path(BATTLE_SESSION_FILE)
    recovery = path.with_name(path.stem + ".recovery.json")
    candidates = sorted((p for p in (path, recovery) if p.exists()),
                        key=lambda p: (p.stat().st_mtime, p == recovery),
                        reverse=True)
    # Try the newest valid session file first, then the recovery copy if needed.
    for candidate in candidates:
        # We handle reading, conversion, or save errors here instead of letting one problem crash the program.
        try:
            data = json.loads(candidate.read_text(encoding="utf-8"))
            if isinstance(data, dict) and isinstance(data.get("players"), dict):
                session_archive["players"] = data["players"]
                saved_ids = data.get("next_account_numbers", {})
                if isinstance(saved_ids, dict):
                    for prefix in ("PLY", "ADM"):
                        # We handle reading, conversion, or save errors here instead of letting one problem crash the program.
                        try:
                            session_archive["next_account_numbers"][prefix] = max(
                                1, int(saved_ids.get(prefix, 1)))
                        except (TypeError, ValueError):
                            pass
                session_archive["next_action_number"] = max(
                    1, int(data.get("next_action_number", 1)))
                break
        except (ValueError, OSError, TypeError):
            continue
    else:
        if candidates:
            print("Saved session data could not be loaded. Check the files.")
    # Look for the highest saved ACT number so a new action ID will not be repeated.
    largest = 0
    for line in Path(BATTLE_LOG_FILE).read_text(encoding="utf-8").splitlines() if Path(BATTLE_LOG_FILE).exists() else []:
        if line.startswith("ACT-"):
            # We handle reading, conversion, or save errors here instead of letting one problem crash the program.
            try:
                largest = max(largest, int(line.split(" |", 1)[0][4:]))
            except ValueError:
                continue
    # We check each related saved record so this result uses actual game data.
    for saved in session_archive["players"].values():
        if isinstance(saved, dict):
            for action in saved.get("history", []):
                # We handle reading, conversion, or save errors here instead of letting one problem crash the program.
                try:
                    largest = max(largest, int(action["action_id"][4:]))
                except (ValueError, TypeError, KeyError):
                    pass
    session_archive["next_action_number"] = max(session_archive["next_action_number"], largest + 1)
    if Path(BATTLE_LOG_FILE).exists():
        lines = Path(BATTLE_LOG_FILE).read_text(encoding="utf-8").splitlines()
        owners = {record["id"]: username for username, record in account_records.items()}
        for index, line in enumerate(lines):
            if not line.startswith("ACT-"):
                continue
            parts = line.split(" | ", 5)
            if len(parts) != 6 or not parts[3].startswith("Player "):
                continue
            username = owners.get(parts[3][7:])
            if not username or username in session_archive["players"]:
                continue
            # We handle reading, conversion, or save errors here instead of letting one problem crash the program.
            try:
                stamp = parts[1]
                hp_text = lines[index + 1] if index + 1 < len(lines) else ""
                player_hp = hp_text.split("Player HP: ", 1)[1].split(" | ", 1)[0]
                enemy_hp = hp_text.split("Enemy HP: ", 1)[1]
                player_before, player_after = [int(v) for v in player_hp.split(" -> ")]
                enemy_before, enemy_after = [int(v) for v in enemy_hp.split(" -> ")]
            except (IndexError, ValueError):
                continue
            action = {"action_id": parts[0], "date_time": stamp,
                      "action_type": parts[2], "player_id": parts[3][7:],
                      "enemy_id": parts[4][6:],
                      "description": parts[5],
                      "player_hp_before": player_before, "player_hp_after": player_after,
                      "enemy_hp_before": enemy_before, "enemy_hp_after": enemy_after}
            session_archive["players"].setdefault(
                username, {"history": [], "undo": [], "current_enemy_id": None,
                           "effects": []})["history"].append(action)

    # Existing saves made before account counters were introduced are upgraded
    # using all IDs found in current records, battle history and activity logs.
    synchronize_account_id_counters()


# Checks current accounts and historical records before choosing future IDs.
# This prevents a new player from receiving an ID that already appears in battle
# history.
def synchronize_account_id_counters():
    """Do not recycle an ID when its old account was deleted."""
    # We check current and past IDs so deleting an account will not let us reuse its ID.
    counters = session_archive.setdefault(
        "next_account_numbers", {"PLY": 1, "ADM": 1})
    # IDs must remain unique even after their accounts are deleted.
    ids = [data["id"] for data in account_records.values()]
    ids.extend(row[1] for row in read_record_rows(BATTLE_HISTORY_FILE)
               if len(row) >= 2)
    ids.extend(row[3][7:] for row in read_record_rows(BATTLE_LOG_FILE)
               if len(row) >= 4 and row[3].startswith("Player "))
    # We check each related saved record so this result uses actual game data.
    for saved in session_archive.get("players", {}).values():
        if not isinstance(saved, dict):
            continue
        ids.extend(action.get("player_id", "")
                   for action in saved.get("history", [])
                   if isinstance(action, dict))
    for candidate in ids:
        if not isinstance(candidate, str) or "-" not in candidate:
            continue
        prefix, number = candidate.split("-", 1)
        if prefix in ("PLY", "ADM") and number.isdigit():
            counters[prefix] = max(counters.get(prefix, 1), int(number) + 1)


# Reserves the next player or admin ID and moves the saved counter forward.
def allocate_account_id(prefix):
    """Reserve a monotonically increasing ID; caller persists it atomically."""
    # We reserve the next player or admin ID and increase its saved counter.
    synchronize_account_id_counters()
    number = session_archive["next_account_numbers"][prefix]
    session_archive["next_account_numbers"][prefix] = number + 1
    return f"{prefix}-{number:03d}"


# Creates an account and saves the record plus ID counter together.
# If the files cannot be saved, the new account and counter change are canceled.
def create_account_with_unique_id(username, password, role="Player"):
    """Write the new account and ID counter together or revert both."""
    # We save the new account and its ID counter as one operation so both stay in sync.
    if (not username or not password or role not in ("Player", "Admin")
            or "|" in username or "," in username or "|" in password
            or any(name.lower() == username.lower() for name in account_records)):
        return False
    # Keep the old counter in case the new account cannot be saved.
    # We copy nested data so changing the new state will not also change our backup.
    prior_counters = copy.deepcopy(session_archive["next_account_numbers"])
    prefix = "ADM" if role == "Admin" else "PLY"
    record_id = allocate_account_id(prefix)
    account_records[username] = new_account_data(record_id, password, role)
    updates = {
        ACCOUNT_FILE: save_all_accounts(content_only=True),
        # We turn the session archive into JSON while keeping its nested battle data.
        BATTLE_SESSION_FILE: json.dumps(session_archive,
                                         ensure_ascii=False, indent=2)
    }
    # We save the linked records as one group so partial changes do not get left behind.
    if atomic_record_updates(updates):
        return True
    account_records.pop(username, None)
    session_archive["next_account_numbers"] = prior_counters
    return False


session_save_mode = "Ready"


# Writes the current sessions to JSON and keeps a recovery copy when needed.
def save_session_archive():
    # We write saved sessions to JSON, with a recovery-file fallback if the main write fails.
    global session_save_mode
    # We turn the session archive into JSON while keeping its nested battle data.
    text = json.dumps(session_archive, ensure_ascii=False, indent=2)
    saved = atomic_record_updates({BATTLE_SESSION_FILE: text})
    recovery = Path(BATTLE_SESSION_FILE).with_name(
        Path(BATTLE_SESSION_FILE).stem + ".recovery.json")
    if not saved:
        # We handle reading, conversion, or save errors here instead of letting one problem crash the program.
        try:
            # We use a file context here so the file is properly closed after reading or writing.
            with open(recovery, "w", encoding="utf-8") as file:
                file.write(text)
                file.flush()
                # We flush the write to disk before treating the temporary file as ready.
                os.fsync(file.fileno())
            saved = True
        except OSError as error:
            print(f"Unable to save the session recovery file: {error}")
    session_save_mode = ("Save failed" if not saved else
                         "Recovery file" if recovery.exists() else "Saved")
    return saved

# Copies the current player's battle history, undo stack, and effects into the
# archive.
def sync_active_session():
    # We copy this player's history, undo list, active enemy, and effects into the session archive.
    username = player.get("name")
    if not username or username not in account_records:
        return False
    # The archive keeps each player session separate by username.
    # We store each player's session separately so accounts do not share histories.
    session_archive["players"][username] = {
        "history": [dict(a) for a in battle_history],
        "undo": [dict(s) for s in undo_stack],
        "current_enemy_id": current_enemy_id,
        "effects": [boost_turns_left, boost_percent, guard_bonus_ready,
                    enemy_stunned_turns, challenge_used,
                    boss_enrage_announced, battle_turns]
    }
    return True


# Saves the current player session after syncing the active battle information.
def save_battle_state():
    # We synchronize the active battle before writing the session JSON.
    if not sync_active_session():
        return False
    return save_session_archive()

# Restores an unfinished fight only if the saved enemy is still the queue front.
# Invalid or outdated battle state is not resumed, which avoids fighting the wrong
# enemy.
def restore_battle_state():
    # We resume a saved battle only when the saved enemy still matches the queue front.
    global current_enemy_id, boost_turns_left, boost_percent, guard_bonus_ready
    global enemy_stunned_turns, challenge_used, boss_enrage_announced, battle_turns
    # We restore only the logged-in player's own session, not another player's battle.
    data = session_archive["players"].get(player["name"], {})
    battle_history[:] = data.get("history", [])
    undo_stack[:] = data.get("undo", [])
    candidate = data.get("current_enemy_id")
    # Only resume if the enemy is still active AND still first in the queue.
    if (player["status"] == "In Battle" and candidate in encounter_lineup
            and candidate == encounter_lineup[0]
            and get_enemy_by_id(candidate) is not None
            and not get_enemy_by_id(candidate)["defeated"]):
        current_enemy_id = candidate
        get_enemy_by_id(candidate)["engaged"] = True
        effects = data.get("effects", [])
        if len(effects) == 7:
            (boost_turns_left, boost_percent, guard_bonus_ready,
             enemy_stunned_turns, challenge_used, boss_enrage_announced,
             battle_turns) = effects
    else:
        current_enemy_id = None
        if player["status"] == "In Battle":
            player["status"] = "Active"
        undo_stack[:] = [s for s in undo_stack if s.get("enemy_id") is None]


# Appends one action to the activity log instead of replacing the earlier actions.
def append_battle_log_action(action):
    # We format one battle activity and add it to the permanent text log.
    # We handle reading, conversion, or save errors here instead of letting one problem crash the program.
    try:
        # We use a file context here so the file is properly closed after reading or writing.
        with open(BATTLE_LOG_FILE, "a", encoding="utf-8") as file:
            file.write(
                f"{action['action_id']} | {action['date_time']} | "
                f"{action['action_type']} | Player {action['player_id']} | "
                f"Enemy {action['enemy_id']} | {action['description']}\n")
            file.write(
                f"    Player HP: {action['player_hp_before']} -> "
                f"{action['player_hp_after']} | "
                f"Enemy HP: {action['enemy_hp_before']} -> "
                f"{action['enemy_hp_after']}\n")
    except OSError as error:
        print(f"Unable to record battle activity: {error}")


# ----- Battle history (permanent record of every battle result) -----

# Records the completed fight with its result, gold change, score, and turn count.
# This history is later used for the admin reports.
def record_battle_result(mob, result, gold_change, score_change, turns=0):
    # Adds one line to the permanent battle history file. The whole file
    # is rewritten so every column stays lined up like a table.
    # We save one completed battle result together with the updated records needed by reports.
    # Reports need completed results, so we record the result and changed balances together.
    # We handle reading, conversion, or save errors here instead of letting one problem crash the program.
    try:
        if Path(BATTLE_HISTORY_FILE).exists():
            Path(BATTLE_HISTORY_FILE).read_text(encoding="utf-8")
    except OSError as error:
        print(f"Battle history cannot be read: {error}")
        return False
    rows = [
        [r["date_time"], r["player_id"], r["username"], r["enemy_id"],
         r["enemy_name"], r["result"], r["turns"], r["gold"], r["score"]]
        for r in load_battle_results()
    ]
    rows.append([
        now_text(), player["id"], player["name"],
        mob["id"] if mob else "N/A",
        mob["name"] if mob else room_name(EXIT_ROOM_ID),
        result, turns, gold_change, score_change
    ])

    history = render_record_rows(

        "DREADVEIL: THE LAST GATE BATTLE HISTORY",
        "date_time|player_id|username|enemy_id|enemy_name|result|turns|"
        "gold|score",
        rows
    )
    username = player.get("name")
    if not username or username not in account_records:
        return False
    # We copy nested data so changing the new state will not also change our backup.
    previous_account = copy.deepcopy(account_records[username])
    previous_session = copy.deepcopy(session_archive["players"].get(username))
    record = account_records[username]
    for key in ("id", "hp", "max_hp", "atk", "gold", "score", "wins", "losses", "status", "location"):
        record[key] = player[key]
    for key in ("defeated_ids", "completed_levels", "owned_equipment", "treasures"):
        record[key] = list(player[key])
    for key in ("inventory", "wounds", "equipped"):
        record[key] = dict(player[key])
    record["lineup"] = list(encounter_lineup)
    sync_active_session()
    updates = {
        BATTLE_HISTORY_FILE: history,
        ACCOUNT_FILE: save_all_accounts(content_only=True),
        # We turn the session archive into JSON while keeping its nested battle data.
        BATTLE_SESSION_FILE: json.dumps(session_archive, ensure_ascii=False, indent=2),
        GAME_RECORD_FILE: write_game_snapshot(content_only=True)
    }
    if outcome_actions_pending:
        # We handle reading, conversion, or save errors here instead of letting one problem crash the program.
        try:
            original_log = Path(BATTLE_LOG_FILE).read_text(encoding="utf-8") if Path(BATTLE_LOG_FILE).exists() else ""
        except OSError as error:
            account_records[username] = previous_account
            if previous_session is None:
                session_archive["players"].pop(username, None)
            else:
                # We store each player's session separately so accounts do not share histories.
                session_archive["players"][username] = previous_session
            print(f"Unable to read the activity log: {error}")
            return False
        lines = []
        for action in outcome_actions_pending:
            lines.append(f"{action['action_id']} | {action['date_time']} | "
                         f"{action['action_type']} | Player {action['player_id']} | "
                         f"Enemy {action['enemy_id']} | {action['description']}\n"
                         f"    Player HP: {action['player_hp_before']} -> "
                         f"{action['player_hp_after']} | "
                         f"Enemy HP: {action['enemy_hp_before']} -> "
                         f"{action['enemy_hp_after']}\n")
        updates[BATTLE_LOG_FILE] = original_log + "".join(lines)
    # We save the linked records as one group so partial changes do not get left behind.
    if atomic_record_updates(updates):
        return True
    account_records[username] = previous_account
    if previous_session is None:
        session_archive["players"].pop(username, None)
    else:
        session_archive["players"][username] = previous_session
    print("The battle result was not saved. Check the record files.")
    return False


# Reads past fight results so reports can include battles from previous sessions.
def load_battle_results():
    # We read saved battle results so reports use real past outcomes.
    results = []

    for parts in read_record_rows(BATTLE_HISTORY_FILE):
        if len(parts) != 9:
            continue

        results.append({
            "date_time": parts[0], "player_id": parts[1],
            "username": parts[2], "enemy_id": parts[3],
            "enemy_name": parts[4], "result": parts[5],
            "turns": parts[6], "gold": parts[7], "score": parts[8]
        })

    return results




# Loads the profiles and related save files in an order that preserves references.
def load_all_records():
    # Rooms load before connections so that links can be validated
    # We load game data in the correct order because some records depend on others.
    load_rooms()
    load_connections()
    load_items()
    load_equipment()
    load_enemies()
    load_questions()
    load_accounts()
    load_session_archive()


# ---------------------------------------------------------------
# PLAYER SESSION
# ---------------------------------------------------------------

# Looks up an enemy using its saved ID instead of assuming a list position.
def get_enemy_by_id(enemy_id):
    # Finds an enemy using its ID
    # We search our enemy list for one exact enemy ID.
    # We check each related saved record so this result uses actual game data.
    for mob in mob_list:
        if mob["id"].upper() == enemy_id.upper():
            return mob
    return None


# Returns the enemy involved in the currently active battle, if any.
def get_current_enemy():
    # Gets the enemy currently being fought
    # We return the opponent being fought, or nothing if no fight is active.
    # We check whether the player currently has an active enemy.
    if current_enemy_id is None:
        return None
    return get_enemy_by_id(current_enemy_id)


# Converts saved enemy flags into the status shown on screen.
def enemy_status(mob):
    # We give the interface a short label for an enemy's current state.
    # We do not allow defeated enemies to be treated as available opponents.
    if mob["defeated"]:
        return "Defeated"
    return "Fighting" if mob.get("engaged") else "Active"


# Looks up the current room name so messages match admin-edited room records.
def room_name(room_id):
    # We look up the saved room name instead of repeating a hard-coded name in messages.
    room = room_records.get(room_id)
    return room["name"] if room else f"Unknown Room ({room_id})"


# Clears one-battle effects before another encounter begins.
def reset_battle_effects():
    # Clears every temporary battle effect
    # We clear temporary buffs and status effects so they do not carry into another fight.
    global boost_turns_left, boost_percent, guard_bonus_ready
    global enemy_stunned_turns, challenge_used, boss_enrage_announced
    global battle_turns

    boost_turns_left = 0
    boost_percent = 0
    guard_bonus_ready = False
    enemy_stunned_turns = 0
    challenge_used = False
    boss_enrage_announced = False
    battle_turns = 0


# Clears temporary login data without deleting the player's saved account.
def reset_session_state():
    # Clears temporary battle information when changing accounts
    # We clear the previous player's active battle data before another login.
    global current_enemy_id, action_counter, intro_shown

    # We empty the old lineup because the player is starting again after defeat.
    encounter_lineup.clear()
    battle_history.clear()
    undo_stack.clear()
    current_enemy_id = None
    action_counter = 0
    intro_shown = False
    reset_battle_effects()

    # We check each related saved record so this result uses actual game data.
    for mob in mob_list:
        mob["engaged"] = False


# Copies a selected account into the active player state and restores their session.
def load_player_from_account(username):
    # Copies the selected account into the active player data
    # We copy a saved player profile into the active player and rebuild their battle state.
    data = account_records[username]

    player.clear()
    player.update({
        "id": data["id"],
        "name": username,
        "role": data["role"],
        "hp": data["hp"],
        "max_hp": data["max_hp"],
        "atk": data["atk"],
        "gold": data["gold"],
        "score": data["score"],
        "wins": data["wins"],
        "losses": data["losses"],
        "status": data["status"],
        "defeated_ids": list(data.get("defeated_ids", [])),
        "completed_levels": list(data.get("completed_levels", [])),
        "inventory": dict(data.get("inventory", {})),
        "wounds": dict(data.get("wounds", {})),
        "owned_equipment": [
            e for e in data.get("owned_equipment", [])
            if e in equipment_records
        ],
        "equipped": dict(data.get("equipped", {})),
        "location": data.get("location", ENTRANCE_ROOM_ID),
        "treasures": [
            t for t in data.get("treasures", []) if t in TREASURES
        ]
    })

    # Equipped items must be owned and must exist
    for slot, eid in list(player["equipped"].items()):
        rec = equipment_records.get(eid)

        if (rec is None or eid not in player["owned_equipment"]
                or rec["slot"] != slot):
            del player["equipped"][slot]

    if player["location"] not in room_records:
        # We return the player to the entrance room after losing the fight.
        player["location"] = ENTRANCE_ROOM_ID

    apply_player_enemy_progress()
    migrated_milestones = reconcile_threshold_rewards_for_existing_player()
    for slot, eid in list(player["equipped"].items()):
        if equipment_records[eid]["tier"] != current_equipment_tier():
            del player["equipped"][slot]
    restore_saved_lineup(data.get("lineup", []))
    restore_battle_state()
    if migrated_milestones:
        # Restore and save active battle/queue state BEFORE changing files.
        # The corrected threshold must never erase an unfinished encounter.
        # We cancel or reverse the change when the player record cannot be saved.
        if not save_current_player_account():
            print("Progression rewards could not be saved; retry after checking access.")
    if (player["status"] == "Defeated" and player["hp"] > 0
            and player["location"] == ENTRANCE_ROOM_ID):
        player["status"] = "Active"
        save_current_player_account()


# Restores the player's queued enemies, leaving out invalid or already defeated IDs.
def restore_saved_lineup(saved_ids):
    # Rebuilds the saved Encounter Queue in the same FIFO order.
    # Enemies that were deleted, defeated or are no longer in the player's
    # room are skipped so the queue always follows the game rules.
    # We restore the saved encounter order but discard enemies that should no longer be queued.
    # We empty the old lineup because the player is starting again after defeat.
    encounter_lineup.clear()
    skipped = []

    for enemy_id in saved_ids:
        mob = get_enemy_by_id(enemy_id)

        if (
            mob is None
            or mob["defeated"]
            or enemy_id in encounter_lineup
            or not can_player_select_enemy(mob)
            or not is_enemy_reachable(mob)
            or mob["room"] != player["location"]
        ):
            skipped.append(enemy_id)
            continue

        # We add a valid enemy to the REAR of the queue.
        encounter_lineup.append(mob["id"])

    return skipped


# Copies the active player values into account records before saving.
# Related session and battle files are written together so one change is not lost.
def save_current_player_account(new_action=None):
    # We save the active player's account, queue, and session details after a real game change.
    username = player.get("name")
    # Only a real logged-in player can write gameplay progress.
    # We do not leave a partial account or session update after a failed save.
    if not username or username not in account_records:
        return False

    # We copy nested data so changing the new state will not also change our backup.
    previous_account = copy.deepcopy(account_records[username])
    previous_session = copy.deepcopy(session_archive["players"].get(username))
    record = account_records[username]

    for key in ("id", "hp", "max_hp", "atk", "gold", "score", "wins",
                "losses", "status", "location"):
        record[key] = player[key]

    record["defeated_ids"] = list(player["defeated_ids"])
    record["completed_levels"] = list(player["completed_levels"])
    record["inventory"] = dict(player["inventory"])
    # Save the encounter order so FIFO is the same after relaunching.
    record["lineup"] = list(encounter_lineup)
    wounds = dict(player["wounds"])
    # We check if a battle is already active before allowing this action.
    if current_enemy_id is not None:
        mob = get_current_enemy()
        # We do not allow defeated enemies to be treated as available opponents.
        if mob is not None and not mob["defeated"]:
            wounds[mob["id"]] = mob["hp"]
    record["wounds"] = wounds
    record["owned_equipment"] = list(player["owned_equipment"])
    record["equipped"] = dict(player["equipped"])
    record["treasures"] = list(player["treasures"])
    sync_active_session()

    updates = {
        ACCOUNT_FILE: save_all_accounts(content_only=True),
        # We turn the session archive into JSON while keeping its nested battle data.
        BATTLE_SESSION_FILE: json.dumps(session_archive, ensure_ascii=False, indent=2),
        GAME_RECORD_FILE: write_game_snapshot(content_only=True)
    }
    if new_action is not None:
        line = (f"{new_action['action_id']} | {new_action['date_time']} | "
                f"{new_action['action_type']} | Player {new_action['player_id']} | "
                f"Enemy {new_action['enemy_id']} | {new_action['description']}\n"
                f"    Player HP: {new_action['player_hp_before']} -> "
                f"{new_action['player_hp_after']} | "
                f"Enemy HP: {new_action['enemy_hp_before']} -> "
                f"{new_action['enemy_hp_after']}\n")
        # We handle reading, conversion, or save errors here instead of letting one problem crash the program.
        try:
            previous_log = Path(BATTLE_LOG_FILE).read_text(encoding="utf-8") if Path(BATTLE_LOG_FILE).exists() else ""
            updates[BATTLE_LOG_FILE] = previous_log + line
        except OSError as error:
            # Restore the in-memory copy if saving fails.
            account_records[username] = previous_account
            if previous_session is None:
                session_archive["players"].pop(username, None)
            else:
                # We store each player's session separately so accounts do not share histories.
                session_archive["players"][username] = previous_session
            print(f"Unable to read the activity log: {error}")
            return False
    # Accounts, battles, and session updates must succeed together.
    # We save the linked records as one group so partial changes do not get left behind.
    if atomic_record_updates(updates):
        return True

    account_records[username] = previous_account
    if previous_session is None:
        session_archive["players"].pop(username, None)
    else:
        session_archive["players"][username] = previous_session
    return False

# Applies a player's saved defeated enemies and wounded-enemy HP to the current room.
def apply_player_enemy_progress():
    # Updates enemy status for the active player. Retreat and defeat
    # clear the affected enemy's saved wounds, so its HP reloads fully.
    # We rebuild enemy defeat or wound information from the active player's saved progress.
    defeated = set(player.get("defeated_ids", []))
    wounds = player.get("wounds", {})

    # We check each related saved record so this result uses actual game data.
    for mob in mob_list:
        mob["defeated"] = mob["id"] in defeated
        mob["engaged"] = False

        # We do not allow defeated enemies to be treated as available opponents.
        if mob["defeated"]:
            mob["hp"] = 0
        else:
            mob["hp"] = min(mob["max_hp"], wounds.get(mob["id"], mob["max_hp"]))


# Changes the status shown in player statistics and the main game screen.
def set_player_status(status):
    # A player who already escaped the dungeon keeps the Victorious status
    # We keep the active status and saved account status consistent.
    if player["status"] != "Victorious":
        player["status"] = status


# Reads how many copies of an item the player currently owns.
def item_quantity(item_id):
    # We read how many of a specific item the player currently owns.
    return player["inventory"].get(item_id, 0)


# Adds or removes an item quantity while keeping inventory values valid.
def change_item_quantity(item_id, amount):
    # We add or remove item quantities without allowing a negative inventory.
    new_qty = item_quantity(item_id) + amount

    if new_qty > 0:
        player["inventory"][item_id] = new_qty
    else:
        player["inventory"].pop(item_id, None)


# Makes a readable description from the item's effect type and power.
def describe_item_effect(item):
    # We turn an item effect and its power into a description the player can understand.
    text = ITEM_EFFECTS.get(item["effect"], "No effect")
    return text.format(
        power=item["power"],
        low=max(1, item["power"] - 5),
        high=item["power"] + 5
    )


# ---------------------------------------------------------------
# EQUIPMENT STATISTICS
# Equipped items change the real battle numbers.
# ---------------------------------------------------------------

# Formats the equipment bonuses shown in shop and inventory screens.
def describe_equipment(item):
    # We show what bonus an equipment record gives in battle.
    return describe_piece(item)


# Finds the standard gear tier that belongs to the current player progress.
def standard_level():
    # The current gear tier is the current unlocked level. Clearing Boss
    # ends the game without inventing a fifth equipment tier.
    # We identify the standard gear level that matches the player's progress.
    done = player.get("completed_levels", [])
    return min(3, sum(1 for level in STANDARD_UPGRADE_LEVELS if level in done))


# Gets the tier of equipment currently available to the player.
def current_equipment_tier():
    # We identify which difficulty tier of free equipment the player has reached.
    return EQUIPMENT_LEVELS[standard_level()]


# Returns the free standard sword, shield, or armor for the current tier.
def standard_piece(slot, level=None):
    # We build the default sword, shield, or armor for the unlocked tier.
    level = standard_level() if level is None else level
    name, bonus, speed = STANDARD_EQUIPMENT[slot][level]
    return {"id": None, "name": name, "slot": slot, "bonus": bonus,
            "speed": speed, "tier": EQUIPMENT_LEVELS[level],
            "source": f"Free {EQUIPMENT_LEVELS[level]} Gear"}


# Returns the currently used equipment for a slot, or standard gear if none is set.
def equipped_piece(slot):
    # Gear from cleared levels remains owned but cannot replace current-tier gear.
    # We find the selected gear in a slot, or use the unlocked standard piece.
    eid = player.get("equipped", {}).get(slot)
    rec = equipment_records.get(eid)
    if (rec is not None and rec["slot"] == slot
            and rec["tier"] == current_equipment_tier()
            and eid in player.get("owned_equipment", [])):
        return {"id": eid, "name": rec["name"], "slot": slot,
                "bonus": rec["bonus"], "speed": rec.get("speed", 0),
                "tier": rec["tier"], "source": "Shop Upgrade"}
    return standard_piece(slot)


# Reads the stat bonus from the equipment currently being used.
def equipped_bonus(slot):
    # We get the combat bonus from one equipped slot.
    return equipped_piece(slot)["bonus"]


# Gets the speed modifier used when calculating hit and critical chances.
def sword_speed():
    # We read the sword speed used in miss and critical-hit calculations.
    return equipped_piece("sword").get("speed", 0)


# Calculates the player's miss chance after equipment modifiers.
def player_miss_chance():
    # Sword speed makes strikes more accurate (at least 1% miss chance).
    # We adjust the chance of missing based on the equipped sword.
    return max(1, PLAYER_MISS_CHANCE - sword_speed() // 2)


# Calculates the player's critical-hit chance from the current equipment.
def player_crit_chance():
    # Each speed point adds one percentage point to critical-hit chance.
    # We adjust the chance of a critical hit based on the equipped sword.
    return min(35, PLAYER_CRIT_CHANCE + sword_speed())


# Converts one sword, shield, or armor record into its displayed stats.
def describe_piece(piece):
    # We format a piece of equipment and its combat effects.
    result = SLOT_STAT_TEXT[piece["slot"]].format(b=piece["bonus"])
    if piece["slot"] == "sword":
        result += f" | SPD: +{piece.get('speed', 0)}%"
    return result


# Formats the old and new gear stats so the player can compare upgrades.
def compare_text(eq):
    # An actionable comparison with gear currently equipped (not with an
    # unseen locked item). The sword compares BOTH attack and speed.
    # We compare an available piece of gear with what the player has equipped.
    worn = equipped_piece(eq["slot"])
    diff = eq["bonus"] - worn["bonus"]
    label = {"sword": "ATK", "shield": "BLOCK", "armor": "DEF"}[eq["slot"]]
    suffix = "%" if eq["slot"] == "shield" else ""
    changes = [f"{label}: {diff:+}{suffix}"]
    if eq["slot"] == "sword":
        changes.append(f"SPD: {eq.get('speed', 0) - worn.get('speed', 0):+}%")
    return ", ".join(changes)


# Adds the player's base attack and equipped sword bonus.
def total_atk():
    # We combine base attack power and equipment bonuses.
    return player["atk"] + equipped_bonus("sword")


# Reads the damage reduction provided by the equipped armor.
def armor_defense():
    # We return the damage reduction supplied by armor.
    return equipped_bonus("armor")


# Reads the block percentage provided by the equipped shield.
def shield_block():
    # We return the shield's percentage reduction for incoming damage.
    return min(75, equipped_bonus("shield"))


# Applies armor and blocking rules to incoming damage.
def mitigate_damage(damage):
    # Armor reduces raw damage first, then shield blocks a percentage.
    # We subtract armor protection and apply the shield reduction to an enemy hit.
    damage = max(1, damage - armor_defense())
    return max(1, damage * (100 - shield_block()) // 100)


# Checks whether the player completed the previous tier required for this gear.
def tier_unlocked(tier):
    # We check whether the player has reached the required equipment tier.
    required = TIER_UNLOCK_REQUIREMENT.get(tier)
    return tier in TIER_UNLOCK_REQUIREMENT and (
        required is None or required in player["completed_levels"])


# Explains which three enemy victories are needed to unlock the next gear tier.
def tier_requirement_text(tier):
    # We explain which difficulty must be completed before equipment can be unlocked.
    required = TIER_UNLOCK_REQUIREMENT.get(tier)
    return f"Defeat 3 {required} enemies to unlock this tier" if required else ""


# Labels equipment as equipped, owned, archived, or not yet owned.
def equipment_state(eid):
    # We report the gear the player currently owns and has equipped.
    rec = equipment_records[eid]
    if eid in player["owned_equipment"] and rec["tier"] != current_equipment_tier():
        return "Archived (previous level)"
    if player["equipped"].get(rec["slot"]) == eid:
        return "Equipped"
    if eid in player["owned_equipment"]:
        return "Owned"
    return "Not owned"

# ---------------------------------------------------------------
# PROGRESSION (rank and level completion)
# ---------------------------------------------------------------

# Counts unique defeated enemies from THIS difficulty only.
# Extra Weak victories cannot replace the three Intermediate victories needed later.
def defeated_count_for_difficulty(difficulty, defeated_ids=None):
    """Count distinct saved enemy IDs of this tier, not total wins.

    Admin-added enemies count just like starter enemies. Extra victories
    after the 3 required kills remain optional and never remove progress.
    """
    # We count unique defeated enemies of one difficulty, not all wins mixed together.
    if defeated_ids is None:
        defeated_ids = player.get("defeated_ids", [])
    # We use a set here so the same enemy ID is not counted twice.
    defeated = set(defeated_ids)
    # We count distinct enemy IDs that match this difficulty, not repeated fights.
    return sum(m["id"] in defeated and m["type"] == difficulty
               for m in mob_list)


# Sets the rank from three Weak, three Intermediate, and three Strong victories.
# Total wins are shown in statistics, but only the right tier counts for a room
# unlock.
def get_rank_info(wins, defeated_ids=None):
    """Rank is earned by 3 unique victories in EACH preceding tier.

    The wins value is retained for caller compatibility and statistics,
    but cannot substitute for the required tier-specific victories.
    """
    # We unlock ranks using three Weak, three Intermediate, and three Strong victories in order.
    # Three Weak victories unlock Intermediate; another three Intermediate unlock Strong.
    # Three Strong victories unlock Boss. More wins in an earlier tier are optional.
    if defeated_ids is None:
        defeated_ids = player.get("defeated_ids", [])
    # Count victories by tier so extra weaker enemies do not skip a level.
    # We count wins for this specific tier; extra weaker enemies cannot skip the next tier.
    weak = defeated_count_for_difficulty("Weak", defeated_ids)
    intermediate = defeated_count_for_difficulty("Intermediate", defeated_ids)
    strong = defeated_count_for_difficulty("Strong", defeated_ids)
    # We unlock the boss only after all three regular tiers have reached their own quota.
    if weak >= 3 and intermediate >= 3 and strong >= 3:
        return {"rank": "Master", "max_difficulty": "Boss",
                "max_order": 4, "next_unlock": "All difficulties unlocked"}
    # We unlock Strong only when both Weak and Intermediate requirements are satisfied.
    if weak >= 3 and intermediate >= 3:
        return {"rank": "Elite", "max_difficulty": "Strong",
                "max_order": 3, "next_unlock":
                f"Boss unlocks after 3 Strong victories ({min(strong,3)}/3)"}
    # We unlock Intermediate after three Weak victories, even with more Weak enemies left.
    if weak >= 3:
        return {"rank": "Adventurer", "max_difficulty": "Intermediate",
                "max_order": 2, "next_unlock":
                f"Strong unlocks after 3 Intermediate victories ({min(intermediate,3)}/3)"}
    return {"rank": "Beginner", "max_difficulty": "Weak",
            "max_order": 1, "next_unlock":
            f"Intermediate unlocks after 3 Weak victories ({min(weak,3)}/3)"}


# Gets the active player's rank using their saved defeated enemy IDs.
def get_player_rank_info():
    # We calculate the current player's rank from their saved defeated enemy IDs.
    # We check the tier-specific victory counts to decide the currently unlocked difficulty.
    return get_rank_info(player["wins"], player.get("defeated_ids", []))


# Makes the text list of difficulty levels the player may currently enter.
def get_unlocked_difficulties():
    # Creates a list of the difficulty levels currently available
    # We list only the enemy difficulty tiers that the player may enter.
    rank = get_player_rank_info()

    return ", ".join(
        difficulty
        for difficulty, order in DIFFICULTY_ORDER.items()
        if order <= rank["max_order"]
    )


# Stops players from selecting an enemy above their unlocked difficulty.
def can_player_select_enemy(mob):
    # Stops the player from selecting an enemy above their rank
    # We reject opponents whose difficulty is still locked.
    return DIFFICULTY_ORDER[mob["type"]] <= get_player_rank_info()["max_order"]


# Checks the three-victory quota, or the defeated boss for the final tier.
# Extra enemies in a room are optional once the required quota is reached.
def is_level_complete(difficulty, defeated_ids=None):
    """A tier is completed at its required quota, not full room exhaustion."""
    # We consider a regular level complete after three wins in that tier, even if extra enemies remain.
    if difficulty == "Boss":
        return all_bosses_defeated(
            player.get("defeated_ids", []) if defeated_ids is None else defeated_ids)
    # We count wins for this specific tier; extra weaker enemies cannot skip the next tier.
    return defeated_count_for_difficulty(difficulty, defeated_ids) >= 3


# Updates old save files that already reached three victories but missed their reward.
# Completed-level flags make sure the reward is not given twice.
def reconcile_threshold_rewards_for_existing_player():
    """Apply newly-earned tier rewards on legacy saves exactly once.

    Old versions waited until *every* enemy died. When admins had added
    extra enemies, a player with 3 victories might have been denied their
    one-time level reward. The completed_levels list is the idempotent flag.
    """
    # We grant missing one-time level bonuses when an older save already meets the new three-win rule.
    newly_completed = []
    for difficulty in LEVEL_ORDER:
        # Check which levels were earned on an old save but not rewarded yet.
        if (is_level_complete(difficulty)
                and difficulty not in player["completed_levels"]):
            # We remember this milestone so extra enemies do not give another level bonus.
            player["completed_levels"].append(difficulty)
            # We permanently increase the player's base attack after earning the level reward.
            player["atk"] += ATTACK_BONUS_PER_LEVEL
            # We permanently raise the HP limit as part of the level reward.
            player["max_hp"] += MAX_HP_BONUS_PER_LEVEL
            # We raise the current HP with the new HP limit so the bonus is immediately useful.
            player["hp"] += MAX_HP_BONUS_PER_LEVEL
            player["gold"] += LEVEL_COMPLETION_GOLD.get(difficulty, 0)
            newly_completed.append(difficulty)
    return newly_completed


# Gives one-time ATK, Max HP, and Gold rewards when a quota is first met.
# It saves the actual Gold before/after values for the reward table.
# The next standard equipment tier is added without charging the player.
def process_level_completion(difficulty, enemy):
    # We give the level reward only once for each difficulty.
    # We apply the one-time level reward and record the real before-and-after Gold values.
    # We give this bonus once per difficulty, not every time another optional enemy is defeated.
    # The Gold Before amount is taken after the enemy reward and before the separate level bonus.
    # We use the completed-level list to prevent earning this reward twice.
    if difficulty in player["completed_levels"]:
        return None

    # No reward until three enemies from this exact difficulty are defeated.
    if not is_level_complete(difficulty):
        return None

    # We remember all the starting stats before applying this level reward.
    old_atk = player["atk"]
    old_max_hp = player["max_hp"]
    # Remember the gold balance before adding the level bonus.
    # We save the Gold balance before the bonus so our reward table can show a real Before value.
    old_gold = player["gold"]
    bonus_gold = LEVEL_COMPLETION_GOLD.get(difficulty, 0)
    old_gear = {slot: equipped_piece(slot) for slot in EQUIPMENT_SLOTS}
    old_tier = current_equipment_tier()

    # Remember this completion permanently to avoid duplicate bonuses.
    # We remember this milestone so extra enemies do not give another level bonus.
    player["completed_levels"].append(difficulty)
    # We permanently increase the player's base attack after earning the level reward.
    player["atk"] += ATTACK_BONUS_PER_LEVEL
    # We permanently raise the HP limit as part of the level reward.
    player["max_hp"] += MAX_HP_BONUS_PER_LEVEL
    # We raise the current HP with the new HP limit so the bonus is immediately useful.
    player["hp"] += MAX_HP_BONUS_PER_LEVEL
    # We add the level-completion Gold only after the required victories are met.
    player["gold"] += bonus_gold

    display_name = difficulty

    description = (
        f"{display_name} level completed. Attack {old_atk} -> "
        f"{player['atk']}, Max HP {old_max_hp} -> {player['max_hp']}."
    )

    if bonus_gold:
        description += f" Level completion bonus: {bonus_gold} Gold."

    push_battle_action("Level Complete", description, enemy=enemy)

    # Equip the standard gear set whenever the next difficulty is unlocked.
    # Owned equipment remains available without additional charges.
    gear_notes = []
    gear_changes = []
    if current_equipment_tier() != old_tier:
        # We switch to the next free standard gear set while keeping purchased gear owned.
        player["equipped"].clear()
        for slot in EQUIPMENT_SLOTS:
            new_piece = standard_piece(slot)
            gear_notes.append(
                f"{slot.title()}: {old_gear[slot]['name']} -> "
                f"{new_piece['name']} ({describe_piece(new_piece)})"
            )
            gear_changes.append((slot.title(), old_gear[slot]["name"],
                                 new_piece["name"], describe_piece(new_piece)))

    if gear_notes:
        push_battle_action(
            "Equipment Upgrade",
            "Standard-Issue gear upgraded for free: "
            + "; ".join(gear_notes) + ".",
            enemy=enemy
        )

    # We return the before-and-after data so the reward screen can show actual numbers.
    return {
        "gear_notes": gear_notes,
        "gear_changes": gear_changes,
        "next_tier": (current_equipment_tier()
                      if current_equipment_tier() != old_tier else None),
        "difficulty": display_name,
        "old_atk": old_atk,
        "new_atk": player["atk"],
        "old_max_hp": old_max_hp,
        "new_max_hp": player["max_hp"],
        # We include the original Gold balance so the display can compare it with the result.
        "old_gold": old_gold,
        # We include the updated Gold balance after adding the bonus.
        "new_gold": player["gold"],
        "gold_bonus": bonus_gold
    }


# Shows the real stats before and after the new level reward.
# We show actual Gold before and after the level bonus; enemy Gold was added earlier.
def show_level_completion_rewards(reward, old_rank, new_rank):
    """Readable reward summary after meeting a difficulty milestone."""
    # We display the stat changes, Gold bonus, new gear, and next-room instructions.
    section(f"LEVEL REQUIREMENT MET: {reward['difficulty'].upper()}")
    # We only show this part when the corresponding reward was actually granted.
    if reward["difficulty"] == "Boss":
        print("The final Boss has been defeated. Well done!")
    else:
        print(f"3 required {reward['difficulty']} victories achieved! ")
        print("The next room is unlocked; remaining enemies are optional.")

    section("YOUR LEVEL REWARDS")
    # We show each reward with its previous value, new value, and actual increase.
    print_table(
        ["Stat", "Before", "After", "Gained"],
        [["Base ATK", reward["old_atk"], reward["new_atk"],
          f"+{reward['new_atk'] - reward['old_atk']}"],
         ["Max HP", reward["old_max_hp"], reward["new_max_hp"],
          f"+{reward['new_max_hp'] - reward['old_max_hp']}"],
         # Show the actual Gold balance before and after the level bonus.
         ["Gold", reward["old_gold"], reward["new_gold"],
          f"+{reward['gold_bonus']} Gold"]],
        max_width=22
    )

    if old_rank["rank"] != new_rank["rank"]:
        print(f"Rank Up: {old_rank['rank']} -> {new_rank['rank']}")

    # We only show this part when the corresponding reward was actually granted.
    if reward["gear_changes"]:
        section("FREE EQUIPMENT - AUTOMATICALLY EQUIPPED")
        print_table(["Slot", "Previously Using", "New Free Gear", "New Stats"],
                    reward["gear_changes"], max_width=30)
        print("Your old shop purchases remain owned and can be found in Inventory.")

    section("NEWLY UNLOCKED")
    # We only show this part when the corresponding reward was actually granted.
    if reward["next_tier"]:
        print(f"Next Level: {reward['next_tier']}")
        print(f"New Shop Upgrades: {reward['next_tier']} equipment is now available.")
        print("Next Step: Choose Travel to Room and explore the next area.")
        print("Beyond the next gate, the veil hides stronger steel...")
    else:
        print("Vharok has fallen! Dreadveil\'s seal on the Last Gate is broken.")
        print("Next Step: Travel to the Last Gate and leave the curse behind.")


# Shows how many wins count toward each three-enemy requirement.
def show_progress_summary():
    # We show the player's current rank and how many wins count in each tier.
    # We show how close the player is to the three-victory quota for each tier.
    rank = get_player_rank_info()

    print(f"Rank                 : {rank['rank']}")
    print(f"Total Wins           : {player['wins']}")
    for difficulty in ("Weak", "Intermediate", "Strong"):
        # We count wins for this specific tier; extra weaker enemies cannot skip the next tier.
        count = defeated_count_for_difficulty(difficulty)
        print(f"{difficulty:<20} : {min(count, 3)}/3 required"
              f" ({max(0, count - 3)} bonus victories)")
    print(f"Unlocked Difficulties: {get_unlocked_difficulties()}")
    print(f"Next Goal            : {rank['next_unlock']}")
    print(
        f"Completed Levels     : "
        f"{', '.join(player['completed_levels']) or 'None'}"
    )
    print(
        f"Level Clear Bonus    : +{ATTACK_BONUS_PER_LEVEL} ATK, "
        f"+{MAX_HP_BONUS_PER_LEVEL} Max HP"
    )


# ---------------------------------------------------------------
# DUNGEON MAP (GRAPH)
# Rooms are vertices and passages are two-way labelled edges.
# A room can be entered only if a path from the entrance exists that
# passes through quota-completed rooms, in difficulty order.
# ---------------------------------------------------------------

# Finds all connected rooms from the saved passages, not a prewritten route.
def get_neighbors(room_id):
    # Returns every room connected to the given room
    # We find directly connected rooms from our stored graph edges.
    neighbors = []

    # We check each related saved record so this result uses actual game data.
    for link in room_connections:
        if link["a"] == room_id:
            neighbors.append((link["b"], link["label"]))
        elif link["b"] == room_id:
            neighbors.append((link["a"], link["label"]))

    return sorted(neighbors)


# Gets only the enemies assigned to the requested room.
def get_room_enemies(room_id):
    # We select the enemies assigned to a particular room.
    return [mob for mob in mob_list if mob["room"] == room_id]


# Returns true if every enemy in a room was defeated by this player.
# This is separate from meeting the three-victory requirement for progression.
def is_room_cleared(room_id, cleared_ids):
    # A room is cleared when every enemy inside it is in cleared_ids
    # We check if every enemy in the room has been beaten, which matters for optional treasure rewards.
    return all(mob["id"] in cleared_ids for mob in get_room_enemies(room_id))


# Makes a set of enemy IDs the current player has defeated.
def player_cleared_ids():
    # Only enemies the player really defeated count as cleared
    # We retrieve the IDs of enemies this player has already defeated.
    return set(player.get("defeated_ids", []))


# Checks whether the current tier reached three victories before opening the next
# gate.
# The exit has a separate condition: the boss must be defeated.
def room_gate_satisfied(room_id, cleared_ids):
    """A gate needs three defeated enemies from the preceding room's tier.

    Clearing every enemy is OPTIONAL. The exit still requires Boss defeat.
    """
    # We check the room unlock requirement before allowing travel through a gate.
    # The room gate uses required tier wins, so we never need to defeat every extra admin-added enemy.
    if room_id in (ENTRANCE_ROOM_ID, EXIT_ROOM_ID):
        return True
    difficulty = next((tier for tier, rid in ROOM_FOR_DIFFICULTY.items()
                       if rid == room_id), None)
    if difficulty == "Boss":
        return all_bosses_defeated(cleared_ids)
    return (difficulty is not None and
            # We count wins for this specific tier; extra weaker enemies cannot skip the next tier.
            defeated_count_for_difficulty(difficulty, cleared_ids) >= 3)


# Uses a graph search from the entrance to find rooms the player can enter.
# A room is included only when the required earlier tiers have been completed.
def get_accessible_rooms(cleared_ids=None):
    # We walk the saved graph while respecting the player's unlocked routes.
    if cleared_ids is None:
        cleared_ids = player_cleared_ids()
    if ENTRANCE_ROOM_ID not in room_records:
        return set()
    visited = {ENTRANCE_ROOM_ID}
    frontier = [ENTRANCE_ROOM_ID]
    # We keep going while this condition is still true.
    while frontier:
        room_id = frontier.pop(0)
        # We read neighbors from stored passages rather than assuming every room is connected.
        for neighbor, _ in get_neighbors(room_id):
            if neighbor in visited or neighbor not in room_records:
                continue
            position = ROOM_ORDER.index(neighbor)
            required = ROOM_ORDER[1:position]
            if any(not room_gate_satisfied(rid, cleared_ids) for rid in required):
                continue
            # The Last Gate stays locked until Vharok has been defeated.
            if neighbor == EXIT_ROOM_ID and not all_bosses_defeated(cleared_ids):
                continue
            visited.add(neighbor)
            frontier.append(neighbor)
    return visited


# Checks whether the enemy's room is currently reachable.
def is_enemy_reachable(mob, cleared_ids=None):
    # We check whether the opponent's room can currently be reached.
    return mob["room"] in get_accessible_rooms(cleared_ids)


# Reads the player's saved position and falls back to the entrance if invalid.
def current_room_id():
    # The room the player is standing in (saved with the account)
    # We read the player's present room ID with an entrance fallback.
    location = player.get("location", ENTRANCE_ROOM_ID)
    return location if location in room_records else ENTRANCE_ROOM_ID


# Marks rooms as locked, open, quota met, or completely cleared for the map.
def get_room_status(room_id, defeated_ids, accessible):
    # We describe whether a room is locked, available, or has optional enemies remaining.
    if room_id == ENTRANCE_ROOM_ID:
        return "Entrance"
    if room_id not in accessible:
        return "Locked"
    # A fully cleared room is different from one with optional enemies left.
    if get_room_enemies(room_id) and is_room_cleared(room_id, defeated_ids):
        return "Cleared"
    if room_gate_satisfied(room_id, defeated_ids):
        return "Level completed / extras optional"
    return "Open"


# Uses breadth-first search (BFS) to find a shortest route through room links.
# The parent records are followed backward to reconstruct the final route.
def find_route(start_id, target_id):
    # Breadth-first search for the shortest list of rooms between two rooms
    # We use breadth-first search to find a valid path between rooms on our saved map.
    # Our breadth-first search explores one layer of rooms at a time to find a short valid path.
    if start_id not in room_records or target_id not in room_records:
        return None

    # Remember where each visited room came from to rebuild the shortest path.
    parents = {start_id: (None, None)}
    frontier = [start_id]

    # We keep going while this condition is still true.
    while frontier:
        room_id = frontier.pop(0)

        if room_id == target_id:
            break

        # We read neighbors from stored passages rather than assuming every room is connected.
        for neighbor, label in get_neighbors(room_id):
            if neighbor not in parents:
                parents[neighbor] = (room_id, label)
                frontier.append(neighbor)

    if target_id not in parents:
        return None

    route = []
    room_id = target_id

    # We keep going while this condition is still true.
    while room_id is not None:
        parent, label = parents[room_id]
        route.append((room_id, label))
        room_id = parent

    # The route was built backward from the target, so reverse it for display.
    route.reverse()
    return route


# Uses a stack to visit connected rooms deeply before returning to earlier paths.
def depth_first_traversal(start_id):
    # Visits rooms by going as deep as possible before backtracking
    # We visit rooms by depth-first search to show a real graph traversal.
    # Our depth-first traversal explores as far as possible before coming back to another route.
    order = []
    visited = set()
    # DFS uses a stack and remembers visited rooms to avoid repeating a loop.
    stack = [start_id]

    # We keep going while this condition is still true.
    while stack:
        room_id = stack.pop()

        if room_id in visited or room_id not in room_records:
            continue

        visited.add(room_id)
        order.append(room_id)

        # We read neighbors from stored passages rather than assuming every room is connected.
        for neighbor, _ in reversed(get_neighbors(room_id)):
            if neighbor not in visited:
                stack.append(neighbor)

    return order


# Builds the map from actual room, enemy, and passage records.
# The Q marker means progression is unlocked but optional enemies remain.
def dungeon_map_lines(defeated_ids, lineup_ids=()):
    # Builds the map display from the live room and enemy records
    # We generate the map from the current rooms and connections.
    accessible = get_accessible_rooms(set(defeated_ids))
    markers = {"Entrance": "E", "Locked": "L", "Cleared": "C", "Open": "O",
               "Level completed / extras optional": "Q"}

    lines = ["Legend: [E] Entrance  [O] Open  [Q] Quota met/optional foes  "
             "[C] Cleared all  [L] Locked", ""]

    for room_id, room in room_records.items():
        status = get_room_status(room_id, set(defeated_ids), accessible)
        lines.append(f"[{markers[status]}] {room_id} {room['name']} ({status})")

        for mob in get_room_enemies(room_id):
            if mob["id"] in defeated_ids:
                state = "Defeated"
            elif mob["id"] in lineup_ids:
                state = "In Queue"
            else:
                state = "Active"
            lines.append(
                f"      Enemy : {mob['id']} {mob['name']} "
                f"({mob['type']}, {state})"
            )

        # We read neighbors from stored passages rather than assuming every room is connected.
        neighbors = get_neighbors(room_id)

        if not neighbors:
            lines.append("      Links : none")

        for neighbor, label in neighbors:
            lines.append(
                f"      Link  : <-> {neighbor} {room_name(neighbor)} "
                f"via {label}"
            )

    return lines


# Size of the map drawing. Boxes shrink when a row holds many rooms.
MAP_MAX_WIDTH = 80
MAP_MAX_BOX_WIDTH = 31
MAP_BOX_GAP = 3


# Prepares each room's enemy and completion details for the visual map.
def get_room_levels():
    # Groups rooms by their distance (in steps) from the entrance using
    # breadth-first search. Each group becomes one row of the drawing.
    # We organize graph rooms by their position in the dungeon layout.
    if ENTRANCE_ROOM_ID not in room_records:
        return []

    depth = {ENTRANCE_ROOM_ID: 0}
    frontier = [ENTRANCE_ROOM_ID]

    # We keep going while this condition is still true.
    while frontier:
        room_id = frontier.pop(0)

        # We read neighbors from stored passages rather than assuming every room is connected.
        for neighbor, _ in get_neighbors(room_id):
            if neighbor not in depth and neighbor in room_records:
                depth[neighbor] = depth[room_id] + 1
                frontier.append(neighbor)

    levels = [[] for _ in range(max(depth.values()) + 1)]

    for room_id, level in depth.items():
        levels[level].append(room_id)

    # Orders each row under its parents to reduce crossing lines
    for number in range(1, len(levels)):
        above = levels[number - 1]

        # Finds where the connected room belongs in the map drawing.
        def parent_position(room_id):
            parents = [
                above.index(n) for n, _ in get_neighbors(room_id) if n in above
            ]
            return (sum(parents) / len(parents) if parents else 0, room_id)

        levels[number].sort(key=parent_position)

    return levels


# Draws the text box for one room using its real name, status, and contents.
def room_box_lines(room_id, status, defeated_ids, lineup_ids, box_width,
                   here=False):
    # Builds the four text lines of one room box. The player's room is
    # drawn with a double border.
    # We draw one room box with its name and status for the text-based map.
    markers = {"Entrance": "E", "Locked": "L", "Cleared": "C", "Open": "O",
               "Level completed / extras optional": "Q"}
    inner = box_width - 4

    title = f"[{markers[status]}] {room_name(room_id)}"
    enemies = get_room_enemies(room_id)

    if not enemies:
        if room_id == ENTRANCE_ROOM_ID:
            detail = "Start here"
        elif room_id == EXIT_ROOM_ID:
            detail = "LAST GATE EXIT"
        else:
            detail = "(empty)"
    else:
        mob = enemies[0]

        if mob["id"] in defeated_ids:
            tag = "x"
        elif mob["id"] in lineup_ids:
            tag = "Q"
        else:
            tag = mob["type"][0]

        extra = f" +{len(enemies) - 1}" if len(enemies) > 1 else ""
        detail = f"{mob['name'][:inner - 4 - len(extra)]}{extra} ({tag})"

    edge = "+" + ("=" if here else "-") * (box_width - 2) + "+"

    return [
        edge,
        f"| {title[:inner]:<{inner}} |",
        f"| {detail[:inner]:<{inner}} |",
        edge
    ]


# Joins the room boxes and passages into the map displayed in the terminal.
def dungeon_drawing_lines(defeated_ids, lineup_ids=(), here=None,
                          color_current=False):
    # Draws the dungeon graph as rows of room boxes joined by lines.
    # Everything is generated from the live room and passage records.
    # We combine the room boxes and passage labels into the finished console map.
    levels = get_room_levels()

    if not levels:
        return ["The dungeon has no entrance."]

    accessible = get_accessible_rooms(set(defeated_ids))
    most_rooms = max(len(level) for level in levels)
    box_width = max(
        14, min(MAP_MAX_BOX_WIDTH, MAP_MAX_WIDTH // most_rooms - MAP_BOX_GAP)
    )
    step = box_width + MAP_BOX_GAP
    width = most_rooms * step

    # Works out the centre column of every room box
    centre = {}

    for level in levels:
        offset = (width - len(level) * step) // 2

        for index, room_id in enumerate(level):
            centre[room_id] = offset + index * step + step // 2

    lines = []
    drawn = set()

    for number, level in enumerate(levels):
        boxes = [
            room_box_lines(
                room_id,
                get_room_status(room_id, set(defeated_ids), accessible),
                defeated_ids,
                lineup_ids,
                box_width,
                room_id == here
            )
            for room_id in level
        ]

        for row in range(4):
            text = [" "] * width

            for room_id, box in zip(level, boxes):
                start = centre[room_id] - box_width // 2
                text[start:start + box_width] = box[row]

            line = "".join(text).rstrip()
            if color_current and here in level:
                start = centre[here] - box_width // 2
                end = start + box_width
                line = line[:start] + color(line[start:end], "green") + line[end:]
            lines.append(line)

        if number + 1 == len(levels):
            break

        # Two rows of / | \ lines towards the rooms in the next row
        links = [
            (room_id, neighbor)
            for room_id in level
            # We read neighbors from stored passages rather than assuming every room is connected.
            for neighbor, _ in get_neighbors(room_id)
            if neighbor in levels[number + 1]
        ]

        for row in (1, 2):
            text = [" "] * width

            for room_id, neighbor in links:
                start_x, end_x = centre[room_id], centre[neighbor]
                x = round(start_x + (end_x - start_x) * row / 3)

                if end_x == start_x:
                    text[x] = "|"
                else:
                    text[x] = "\\" if end_x > start_x else "/"

            lines.append("".join(text).rstrip())

        drawn.update(frozenset(link) for link in links)

    # Passages that do not go to the next row are listed underneath
    extra = [
        link for link in room_connections
        if frozenset((link["a"], link["b"])) not in drawn
    ]

    lines.append("")
    lines.append("Rooms  : [E] Entrance  [O] Open  [Q] Quota met; extras optional")
    lines.append("         [C] Fully cleared  [L] Locked")
    lines.append("Enemies: (W)eak (I)ntermediate (S)trong (B)oss "
                 "(Q) In Queue (x) Defeated")

    if here in room_records:
        lines.append(f"You    : +====+ box = you are here "
                     f"({room_name(here)})")

    if extra:
        lines.append("Other passages:")

        for link in extra:
            lines.append(f"  {room_name(link['a'])} <-> "
                         f"{room_name(link['b'])} via {link['label']}")

    unreachable = [r for r in room_records if r not in centre]

    if unreachable:
        lines.append("Rooms with no passage from the entrance: "
                     + ", ".join(room_name(r) for r in unreachable))

    return lines


# Prints the dungeon graph so players can see connected and locked rooms.
def display_dungeon_map(pause_after=True):
    # We print the current graph instead of using a picture that never changes.
    header("Dungeon Map (Graph)")

    print(f"Current room: {color(room_name(current_room_id()), 'green')}")
    for line in dungeon_drawing_lines(
        player["defeated_ids"], encounter_lineup, current_room_id(),
        color_current=True
    ):
        print(line)

    if pause_after:
        pause()


# Shows a selected room's information using the current room records.
def display_room_details():
    # We show the saved room information and its connecting passages.
    header("Room Details and Passages")

    # We check each related saved record so this result uses actual game data.
    for line in dungeon_map_lines(player["defeated_ids"], encounter_lineup):
        print(line)

    pause()


# Lets the player choose a room from a numbered list of valid options.
def choose_room(prompt="Enter Room ID or number: ", allow_entrance=True):
    # We ask for a destination and reject unknown room IDs.
    key = input(prompt).strip().upper()
    rooms = list(room_records)
    room_id = (rooms[int(key) - 1] if key.isdigit()
               and 1 <= int(key) <= len(rooms) else key)
    if not room_id:
        print("\nRoom ID must not be blank.")
        return None
    if room_id not in room_records:
        print("\nRoom record not found.")
        return None
    if not allow_entrance and room_id == ENTRANCE_ROOM_ID:
        print(f"\n{room_name(ENTRANCE_ROOM_ID)} cannot be selected here.")
        return None
    return room_id


# Finds and shows a route plus whether the player can actually travel it.
def show_route_to_room():
    # Shortest path search (BFS) from the player's room to a chosen room
    # We find the route to a selected destination and explain any locked gate.
    header("Find Route to Room")

    print_table(["Room ID", "Name"],
                [[room_id, room["name"]]
                 for room_id, room in room_records.items()], numbered=True)

    target = choose_room("\nEnter destination Room ID or No.: ")

    if target is None:
        pause()
        return

    start = current_room_id()
    # We search the real graph to build the route shown to the player.
    route = find_route(start, target)

    if route is None:
        print("\nThere is no passage leading to that room.")
        pause()
        return

    accessible = get_accessible_rooms()

    section(f"Shortest Route (BFS): {len(route) - 1} passage(s)")
    route_text = " -> ".join(room_name(room_id) for room_id, _ in route)
    print(color(textwrap.fill(route_text, width=94), "cyan"))
    route_rows = []
    for room_id, label in route:
        status = get_room_status(room_id, set(player["defeated_ids"]), accessible)
        position = "YOU ARE HERE" if room_id == start else status
        route_rows.append([room_id, room_name(room_id), label or "Start", position])
    print_table(["Room ID", "Room", "Passage", "Access"], route_rows,
                max_width=29, numbered=True)

    blocked = [
        room_id for room_id, _ in route[:-1]
        if room_id != ENTRANCE_ROOM_ID
        and not room_gate_satisfied(room_id, player_cleared_ids())
    ]

    if target not in accessible:
        print("\nThe destination is still sealed.")

    if blocked:
        print("You must meet the 3-enemy requirement in these rooms first: "
              + ", ".join(room_name(r) for r in blocked))
    elif target in accessible:
        print("\nThe route is open.")

    pause()


# Prints the DFS visit order so the graph traversal can be demonstrated.
def show_traversal():
    # Depth-first traversal of the whole dungeon from the entrance
    # We display the order returned by the graph traversal code.
    header("Dungeon Exploration Order (DFS)")

    # We visit rooms in DFS order using saved connections.
    order = depth_first_traversal(ENTRANCE_ROOM_ID)

    for step, room_id in enumerate(order, 1):
        print(f"{step:2}. {room_id} {room_name(room_id)}")

    unreachable = [r for r in room_records if r not in order]

    if unreachable:
        print("\nRooms with no path from the entrance: "
              + ", ".join(unreachable))

    pause()


# Groups the player's map, room details, route search, and traversal options.
def dungeon_map_menu():
    # We let the player choose the map, room details, route search, or traversal.
    # We repeat this menu or action until the player gives a valid choice or leaves.
    while True:
        header("Dungeon Map and Routes")
        print("[1] View Dungeon Map")
        print("[2] Room Details and Passages")
        print("[3] Find Route to a Room (BFS)")
        print("[4] Exploration Order (DFS Traversal)")
        print("\n[0] Back")

        choice = input("\nEnter choice [0-4]: ").strip()

        if choice == "1":
            display_dungeon_map()
        elif choice == "2":
            display_room_details()
        elif choice == "3":
            show_route_to_room()
        elif choice == "4":
            show_traversal()
        elif choice == "0":
            break
        else:
            invalid_choice()


# ---------------------------------------------------------------
# LOGIN
# ---------------------------------------------------------------

# Checks signup details and saves a new player record with a unique ID.
def register_new_account(username, password):
    # IDs are reserved in the session archive, even after account deletion.
    # We start player registration from the login menu.
    return create_account_with_unique_id(username, password)


# Asks for account credentials, checks the saved records, and opens the right menu.
def login_screen():
    # Main screen before entering the game
    # We check the username and password, then load only that account's saved progress.
    # We repeat this menu or action until the player gives a valid choice or leaves.
    while True:
        header("Dreadveil: The Last Gate")

        print("[1] Login")
        print("[2] Create New Account")
        print("\n[0] Exit Game")

        choice = input("\nEnter choice [0-2]: ").strip()

        if choice == "1":
            username = input("Enter Username: ").strip()
            password = input("Enter Password: ").strip()

            if not username or not password:
                print("\nUsername and password must not be blank.")
                pause()
                continue

            if (
                username in account_records
                and account_records[username]["password"] == password
            ):
                # Clears temporary data from the last login session
                reset_session_state()
                load_player_from_account(username)

                print(f"\nWelcome back, {username}!")

                if player["role"] == "Admin":
                    print("Role: Administrator")
                    pause()
                    admin_menu()
                else:
                    print("Your saved progress has been loaded.")
                    if player["status"] == "Victorious":
                        print("Your journey is complete. You have escaped "
                              "Dreadveil through the Last Gate.")
                    else:
                        print(f"You are standing in: "
                              f"{room_name(current_room_id())}")

                    if encounter_lineup:
                        print(
                            f"Your Encounter Queue was restored "
                            f"({len(encounter_lineup)} enemies waiting)."
                        )

                    pause()
                    open_adventure_menu()

            else:
                print("\nInvalid username or password.")

                if ask_yes_no(
                    "Would you like to create a new account? (Y/N): "
                ):
                    signup_screen()
                else:
                    print("\nReturning to the main menu.")
                    pause()

        elif choice == "2":
            signup_screen()

        elif choice == "0":
            print("\nThank you for playing Dreadveil: The Last Gate!")
            print("Goodbye.")
            break

        else:
            invalid_choice()


# Collects the new player's details and confirms the account was created.
def signup_screen():
    # Creates a new player account after checking the input
    # We collect the new account details and reject names that are already taken.
    header("Create Account")

    username = input("Enter New Username: ").strip()

    if not username:
        print("\nUsername must not be blank.")
        pause()
        return

    if "|" in username or "," in username:
        print("\nUsername must not contain | or , characters.")
        pause()
        return

    if any(name.lower() == username.lower() for name in account_records):
        print("\nThat username already exists.")
        pause()
        return

    password = input("Enter New Password: ").strip()

    if not password:
        print("\nPassword must not be blank.")
        pause()
        return

    if "|" in password:
        print("\nPassword must not contain the | character.")
        pause()
        return

    if not register_new_account(username, password):
        print("\nAccount could not be saved. Please check access to the records.")
        pause()
        return

    print(f"\nAccount created successfully for {username}!")
    print(f"Your Player ID is {account_records[username]['id']}.")
    print("You can now log in using your new account.")

    pause()


# ---------------------------------------------------------------
# PLAYER MENU
# ---------------------------------------------------------------

# Opens the player's options after a successful login.
def open_adventure_menu():
    # Main menu after a player logs in
    # We load the logged-in player's game and show their available actions.
    # We repeat this menu or action until the player gives a valid choice or leaves.
    while True:
        header("Dreadveil: The Last Gate")

        show_live_panel()

        print("\n[1] " + ("View Completed Journey" if player["status"]
                          == "Victorious" else "Enter Dungeon"))
        print("[2] View Player Statistics")
        print("[3] Dungeon Map and Routes")
        print("[4] Enemy Information")
        print("[5] How to Play")
        print("\n[0] Logout")

        choice = input("\nEnter choice [0-5]: ").strip()

        if choice == "1":
            if player["status"] == "Victorious":
                story_panel("Dreadveil: Journey Complete", ENDING_TEXT, "green")
                print(f"Final Score: {player['score']}")
                pause()
            elif dungeon_menu():
                reset_session_state()
                print("\nYour journey has ended. Returning to the main menu...")
                break
        elif choice == "2":
            view_stats()
        elif choice == "3":
            dungeon_map_menu()
        elif choice == "4":
            view_enemy_records()
        elif choice == "5":
            show_instructions()
        elif choice == "0":
            # Saves the player (including the queue) before logging out
            # We cancel or reverse the change when the player record cannot be saved.
            if not save_current_player_account():
                print("\nProgress could not be saved. Please check file access.")
                pause()
                continue
            reset_session_state()

            print("\nYour progress has been saved.")
            print("Logging out...")
            break
        else:
            invalid_choice()


# Displays the current player's rank, stats, location, and progression.
def view_stats(pause_after=True):
    # Shows the player's current information
    # We show the player's actual rank, HP, attack, Gold, and progress.
    header("Player Statistics")

    print(f"Player ID         : {player['id']}")
    print(f"Player Name       : {player['name']}")
    print(f"Location          : {room_name(current_room_id())}")
    print(f"Health Points     : {player['hp']}/{player['max_hp']}")
    print(f"Attack Power      : {total_atk()} (base {player['atk']} "
          f"+ sword {equipped_bonus('sword')})")
    print(f"Armor Defense     : -{armor_defense()} damage per hit")
    print(f"Shield Block      : {shield_block()}% damage blocked")
    print(f"Sword Speed       : +{sword_speed()}% "
          f"(crit {player_crit_chance()}%, miss {player_miss_chance()}%)")
    print(f"Current Gear Tier : {current_equipment_tier()}")
    print(f"Current Score     : {player['score']}")
    print(f"Gold              : {player['gold']}")
    print(f"Wins              : {player['wins']}")
    print(f"Losses            : {player['losses']}")
    print(f"Status            : {player['status']}")

    section("Progression")
    show_progress_summary()
    view_inventory(pause_after=False, show_header=False)

    if pause_after:
        pause()


# Shows items and equipment from the player's actual saved inventory.
def view_inventory(pause_after=True, show_header=True):
    # Shows how many items the player currently has
    # We display owned items and equipment using the current account records.
    if show_header:
        header("Inventory")

    section("Items")

    rows = [
        [item["name"], f"{item_quantity(item_id)}/{item['max_carry']}",
         describe_item_effect(item)]
        for item_id, item in item_records.items()
        if item_quantity(item_id) > 0
    ]

    if rows:
        print_table(["Item", "Owned", "Effect"], rows, max_width=40)
    else:
        print("Your inventory is empty.")

    section("Equipment")

    # Free Standard-Issue pieces first, then anything bought in the shop
    gear = []

    for slot in EQUIPMENT_SLOTS:
        std = standard_piece(slot)
        gear.append([
            std["name"], slot.title(), std["source"], describe_piece(std),
            "Equipped" if equipped_piece(slot)["id"] is None else "Available"
        ])

    for e in player["owned_equipment"]:
        if e in equipment_records:
            eq = equipment_records[e]
            gear.append([eq["name"], eq["slot"].title(),
                         f"Shop ({eq['tier']})", describe_equipment(eq),
                         equipment_state(e)])

    print_table(["Name", "Slot", "Source", "Effect", "State"], gear,
                max_width=30)

    if not player["owned_equipment"]:
        print("No optional upgrades bought yet. See the Dungeon Shop.")

    if pause_after:
        pause()


# Lists enemies and optionally filters out enemies that cannot be fought now.
def view_enemy_records(pause_after=True, only_available=False,
                       show_header=True):
    # Shows information about all enemies. When another screen already
    # printed the main title, only a sub-heading is shown.
    # We show real enemies from the stored records, with optional room and availability filters.
    if show_header:
        header("Enemy Information")
    else:
        section("Available Enemies")

    rank = get_player_rank_info()
    accessible = get_accessible_rooms()
    here = current_room_id()

    print(f"Current Rank    : {rank['rank']}")
    print(f"Unlocked Levels : {get_unlocked_difficulties()}")
    print(f"Next Goal       : {rank['next_unlock']}")
    print(f"You Are In      : {room_name(here)}")
    print()

    rows = []
    # When choosing an enemy to queue, only show enemies of this room
    visible_mobs = available_room_enemies() if only_available else mob_list

    for mob in visible_mobs:

        # We do not allow defeated enemies to be treated as available opponents.
        if mob["defeated"]:
            status = "Defeated"
        elif mob["id"] in encounter_lineup:
            status = "In Queue"
        else:
            status = "Active"

        if not can_player_select_enemy(mob):
            access = "Rank locked"
        elif mob["room"] not in accessible:
            access = "Room locked"
        elif mob["room"] != here:
            access = "Other room"
        else:
            access = "Unlocked"

        rows.append([
            mob["id"], mob["name"], mob["type"],
            f"{mob['hp']}/{mob['max_hp']}", mob["atk"],
            f"{mob['gold_reward']}/{mob['score_reward']}",
            room_name(mob["room"]), status, access
        ])

    if rows:
        print_table(
            ["ID", "Name", "Difficulty", "HP", "ATK", "Gold/Score", "Room",
             "Status", "Access"],
            rows,
            max_width=18,
            numbered=True
        )
    else:
        print("No available enemies in this room.")

    if pause_after:
        pause()


# Explains the actual game rules, including three required wins and optional enemies.
def show_instructions():
    # Gives the player the basic rules of the game
    # We explain the controls, combat rules, and three-victory unlock system before playing.
    header("How to Play")

    section("Goal")
    print(f"- Begin at {room_name(ENTRANCE_ROOM_ID)}. Defeat three guardians")
    print(f"  in each regular difficulty, face Vharok in {room_name('ROOM-004')},")
    print(f"  and escape through {room_name(EXIT_ROOM_ID)}.")

    section("The Six Rooms (one room per difficulty)")
    print("  " + " -> ".join(room_name(room_id) for room_id in ROOM_ORDER))
    print("- Move only through connected passages shown on the live map.")
    print("- Unlock Intermediate with 3 Weak victories (3 total minimum).")
    print("- Unlock Strong with 3 Intermediate victories (6 total minimum).")
    print("- Unlock the Boss room with 3 Strong victories (9 total minimum).")
    print("- Defeat Vharok to open The Last Gate; step through to finish.")

    section("Progression")
    print("- Beginner: 0-2 Weak victories; Weak available.")
    print("- Adventurer: 3 Weak victories; Intermediate available.")
    print("- Elite: 3 Weak + 3 Intermediate victories; Strong available.")
    print("- Master: 3 Weak + 3 Intermediate + 3 Strong; Boss available.")
    print("- Extra enemies added by the admin are OPTIONAL once that")
    print("  difficulty's 3-victory requirement has been met.")
    print("- You may revisit previous rooms to fight remaining enemies.")
    print("- A treasure chest requires clearing EVERY enemy in its room,")
    print("  but collecting it is not required to unlock the next room.")
    print(f"- Meeting a difficulty's requirement gives +{ATTACK_BONUS_PER_LEVEL} ATK "
          f"and +{MAX_HP_BONUS_PER_LEVEL} Max HP once")
    print("  and upgrades your free Standard-Issue Sword, Shield and Armor.")

    section("Encounter Queue (FIFO)")
    print("- Start Battle fights the first queued enemy.")
    print("  If the queue is empty, the first available enemy is chosen.")
    print("- Add Enemy to Queue lets you choose the fighting order.")
    print("  Enemies are fought in the order they were added (FIFO).")
    print("- View Queue shows queued and available enemies.")
    print("- View Next Enemy shows who you will fight next.")
    print("- Victory removes the first queued enemy; retreat keeps it.")
    print("- View Queue also lets you remove the front enemy without fighting.")
    print("- Progress and battle actions are saved automatically.")

    section("Battle (every action uses your turn)")
    print("- Attack  : can miss or land a critical hit")
    print(f"- Defend  : take {int(DEFEND_DAMAGE_TAKEN * 100)}% damage, "
          f"next attack +{DEFEND_COUNTER_BONUS}%")
    print("- Items   : using an item also lets the enemy strike back")
    print("- Challenge: a random question comes from the enemy's difficulty.")
    print("             Admin can add more Weak, Intermediate, or Strong questions.")
    print("             The Boss has one fixed challenge question.")
    print("             Correct = guaranteed hit with bonus damage for this attack.")
    print("             Wrong = you lose the turn. Challenges award no Gold.")
    print("- Retreat : leave the battle for free; the enemy fully heals")
    print("- The Boss becomes ENRAGED below half health.")

    section("Player Undo Stack")
    print("- The player menu shows only actions available to undo.")
    print("- Admins can inspect the complete activity history separately.")
    print("- An empty Undo Stack is shown clearly after permanent results.")
    print("- Each reversible action (attack, defend, item, challenge,")
    print("  purchase, equip, rest) pushes a snapshot on the Undo Stack.")
    print("- Undo pops the newest snapshot first (LIFO) and restores HP, gold,")
    print("  score, items, equipment, enemy HP and battle effects.")
    print("- Travel can be undone until a new battle or permanent result.")
    print("- Victories, defeats, retreats and final escape cannot be undone.")

    section("Camp (between battles)")
    print("- After a victory or retreat, HP stays as it was.")
    print(f"- After defeat, you revive with {DEFEAT_REVIVE_PERCENT}% of Max HP.")
    print(f"- Rest at Camp heals {REST_HEAL_PERCENT}% Max HP "
          f"for {REST_COST} Gold.")
    print("- Treasure chests (one per fighting room) pay Gold once the room")
    print("  is cleared. Use Open Treasure Chest while standing in the room.")
    print("- The Dungeon Shop sells potions and current-level upgrades.")
    print("  Future equipment unlocks after three victories in the required difficulty.")

    section("Defeat")
    print(f"- Lose {DEFEAT_GOLD_LOSS_PERCENT}% of your Gold and respawn at "
          f"{room_name(ENTRANCE_ROOM_ID)} with "
          f"{DEFEAT_REVIVE_PERCENT}% of your Max HP.")
    print("- Your Encounter Queue is cleared. Earlier victories, unlocked")
    print("  rooms and collected rewards remain saved.")
    print("- The enemy that defeated you returns to FULL HP, just like")
    print("  retreat. Its previous wounds will NOT persist on reload.")
    print("- Retreat keeps the enemy in the queue; defeat clears the queue.")

    section("Items")
    # We check each related saved record so this result uses actual game data.
    for item in item_records.values():
        print(f"- {item['name']} ({item['price']} Gold, carry "
              f"{item['max_carry']}): {describe_item_effect(item)}")

    section("Standard-Issue Equipment (free, automatic)")
    print(f"- Everyone starts at {room_name(ENTRANCE_ROOM_ID)} with free Weak-tier gear.")
    print("- Finishing Weak / Intermediate / Strong automatically equips")
    print("  the next level's three free pieces. Old purchases stay owned.")
    print("- Shop gear is optional; two choices per equipment type per tier.")
    print("- Sword SPD raises critical hit chance and reduces missed attacks.")

    print(f"- Your current gear level: {current_equipment_tier()}")
    for slot in EQUIPMENT_SLOTS:
        piece = equipped_piece(slot)
        print(f"- {slot.title()}: {piece['name']} ({describe_piece(piece)})")
    print("- Which weapons lie beyond the next gate? Keep exploring to find out.")

    section("Optional Shop Equipment (costs Gold)")
    print("- Shop reveals only the upgrades for your current level.")
    print("- Old-tier purchases are archived in Inventory, not sold again.")

    pause()


# ---------------------------------------------------------------
# ENCOUNTER QUEUE (FIFO)
# ---------------------------------------------------------------

# Returns undefeated enemies that can be selected in the current room.
def available_room_enemies():
    # Finds eligible enemies not in the queue, ordered by enemy ID.
    # We find opponents in the current room who have not already been defeated.
    return sorted(
        (mob for mob in mob_list
         if mob["room"] == current_room_id()
         and not mob["defeated"]
         and mob["id"] not in encounter_lineup
         and can_player_select_enemy(mob)
         and is_enemy_reachable(mob)),
        key=lambda mob: mob["id"]
    )


# Shows the FIFO encounter queue with its FRONT and REAR positions.
# The dequeue menu is available when no battle is active.
def display_encounter_lineup(pause_after=False, show_header=True):
    # Displays the queue and eligible enemies in the current room.
    # We show which enemy is at the FRONT and REAR of our FIFO queue.
    # FRONT is the first enemy to be fought. REAR is the last enemy waiting.
    if show_header:
        header("Dungeon Encounter Queue")
    else:
        section("Dungeon Encounter Queue")

    print(f"Room: {room_name(current_room_id())}  |  Waiting: {len(encounter_lineup)}")
    # We handle an empty queue before trying to use its front item.
    if not encounter_lineup:
        print("Queue is empty. Add an enemy or choose Start Battle.")
    else:
        queued = []
        # Use the current list order to mark the front and rear, not fixed enemy IDs.
        # We check each related saved record so this result uses actual game data.
        for position, enemy_id in enumerate(encounter_lineup, 1):
            mob = get_enemy_by_id(enemy_id)
            # We stop here if the enemy ID does not match an existing enemy.
            if mob is None:
                continue
            marker = "FRONT / REAR" if len(encounter_lineup) == 1 else (
                "FRONT" if position == 1 else
                "REAR" if position == len(encounter_lineup) else "Waiting")
            queued.append([mob["id"], mob["name"],
                           f"{mob['hp']}/{mob['max_hp']}", marker])
        print_table(["Enemy ID", "Enemy", "HP", "Position"], queued,
                    max_width=27, numbered=True)

    section("Available Room Enemies")
    remaining = available_room_enemies()
    if not remaining:
        print("None available in this room.")
    else:
        print_table(["Enemy ID", "Enemy", "HP", "Difficulty"],
                    [[m["id"], m["name"], f"{m['hp']}/{m['max_hp']}",
                      m["type"]] for m in remaining], numbered=True)

    if pause_after:
        # We check if a battle is already active before allowing this action.
        if current_enemy_id is not None:
            pause()
        else:
            print("\n[1] Dequeue Front Enemy\n[0] Back")
            choice = input("\nChoose [0-1]: ").strip()
            if choice == "1":
                dequeue_front_from_menu()
            elif choice != "0":
                invalid_choice()


# Removes only the front enemy after confirmation and records the change.
# If saving fails, the enemy is put back so the queue stays correct.
def dequeue_front_from_menu():
    # Do not let a player remove the enemy while fighting it.
    # We let the player remove the first waiting enemy when no battle is active.
    # We check if a battle is already active before allowing this action.
    if current_enemy_id is not None:
        print("You cannot remove an enemy during a battle.")
        pause()
        return
    # An empty queue should display a message instead of causing pop(0) to fail.
    # We handle an empty queue before trying to use its front item.
    if not encounter_lineup:
        print("The Encounter Queue is empty.")
        pause()
        return
    mob = get_enemy_by_id(encounter_lineup[0])
    # We leave the current values unchanged if the player does not confirm.
    if not ask_yes_no(f"Remove {mob['name']} from the Queue? (Y/N): "):
        return
    undo_stack.clear()
    before = lineup_line()
    # We remove the FRONT enemy first because our encounter queue follows FIFO.
    # We take only the FRONT enemy out, preserving the order behind it.
    removed = encounter_lineup.pop(0)
    if not push_battle_action("Dequeue", f"Removed {mob['name']} from the Encounter Queue."):
        encounter_lineup.insert(0, removed)
        print("The Queue was not changed because saving failed.")
        pause()
        return
    section("Queue Updated (FIFO)")
    print(f"Before: {before}")
    print(f"Removed from FRONT: {mob['name']}")
    print(f"After : {lineup_line()}")
    pause()


# Builds a short FRONT-to-REAR queue display for before/after messages.
def lineup_line():
    # One-line view of the queue from front to rear
    # We join queued enemy names in the same order they will be fought.
    # We handle an empty queue before trying to use its front item.
    if not encounter_lineup:
        return "(empty)"

    names = " -> ".join(get_enemy_by_id(e)["name"] for e in encounter_lineup)
    return f"FRONT [{names}] REAR"


# Validates the selected enemy before adding it to the back of the queue.
# Already defeated, duplicate, locked, or wrong-room enemies are rejected.
def add_enemy_to_lineup():
    # ENQUEUE: lets the player choose an enemy of the current room
    # We check an enemy's ID, room, defeat status, and difficulty before adding it to the queue rear.
    header("Add Enemy to Encounter Queue")

    # We check the player's current location before deciding what is allowed.
    if current_room_id() in (ENTRANCE_ROOM_ID, EXIT_ROOM_ID):
        print(f"There are no enemies in {room_name(current_room_id())}.")
        print("Use Travel to Connected Room to find the next enemy room.")
        pause()
        return

    view_enemy_records(pause_after=False, only_available=True,
                       show_header=False)

    eligible = available_room_enemies()
    if not eligible:
        print("No available enemies to add.")
        pause()
        return
    enemy_id = input("\nEnter Enemy ID or No.: ").strip().upper()
    if enemy_id.isdigit() and 1 <= int(enemy_id) <= len(eligible):
        enemy_id = eligible[int(enemy_id) - 1]["id"]

    if not enemy_id:
        print("\nEnemy ID must not be blank.")
        pause()
        return

    mob = get_enemy_by_id(enemy_id)

    # We stop here if the enemy ID does not match an existing enemy.
    if mob is None:
        print("\nEnemy record not found.")
        pause()
        return

    # We do not allow defeated enemies to be treated as available opponents.
    if mob["defeated"]:
        print("\nEnemy has already been defeated and cannot be added "
              "to the Queue.")
        pause()
        return

    # Block duplicate queue entries for the same enemy.
    # We do not place the same enemy in the active queue more than once.
    if mob["id"] in encounter_lineup:
        print("\nEnemy is already waiting in the Encounter Queue.")
        pause()
        return

    # Do not allow enemies from locked difficulty levels.
    if not can_player_select_enemy(mob):
        rank = get_player_rank_info()

        print("\nThat enemy is still locked.")
        print(f"Your Rank: {rank['rank']}")
        print(f"Enemy Level: {mob['type']}")
        print(f"Next Goal: {rank['next_unlock']}")
        pause()
        return

    # Only enemies in the current room may be queued.
    # We check the player's current location before deciding what is allowed.
    if mob["room"] != current_room_id():
        print(f"\n{mob['name']} lurks in {room_name(mob['room'])}.")
        print("You can only face enemies of the room you are standing in.")
        print("Use Travel to Connected Room to get there.")
        pause()
        return

    if not is_enemy_reachable(mob):
        print(f"\n{room_name(mob['room'])} cannot be reached yet.")
        pause()
        return

    # Adds the selected enemy to the rear of the queue
    before = lineup_line()
    undo_stack.clear()
    # We add a valid enemy to the REAR of the queue.
    # We place the selected enemy at the REAR after all checks pass.
    encounter_lineup.append(mob["id"])
    if not push_battle_action("Enqueue", f"Added {mob['name']} to the Encounter Queue."):
        encounter_lineup.pop()
        print("The Queue was not changed because saving failed.")
        pause()
        return

    section("Queue Updated (FIFO)")
    print(f"Before: {before}")
    print(f"Added to REAR: {mob['id']} | {mob['name']}")
    print(f"After : {lineup_line()}")
    pause()


# Peeks at the next enemy without removing it from the queue.
def view_next_enemy():
    # Shows the next opponent without changing the queue.
    # We peek at the next opponent without removing anyone from the queue.
    header("Next Enemy")

    if encounter_lineup:
        mob = get_enemy_by_id(encounter_lineup[0])
        selection = "Queued"
    else:
        remaining = available_room_enemies()
        mob = remaining[0] if remaining else None
        selection = "Room order"

    # We stop here if the enemy ID does not match an existing enemy.
    if mob is None:
        print("No available enemy in this room.")
        pause()
        return

    print(f"Enemy        : {mob['name']}")
    print(f"Enemy ID     : {mob['id']}")
    print(f"Selection    : {selection}")
    print(f"Health       : {mob['hp']}/{mob['max_hp']}")
    print(f"Attack Power : {mob['atk']}")
    print(f"Difficulty   : {mob['type']}")
    print(f"Gold Reward  : {mob['gold_reward']}")
    print(f"Score Reward : {mob['score_reward']}")
    print(f"Room         : {room_name(mob['room'])}")

    if mob["type"] == "Boss":
        print("Warning      : becomes ENRAGED below half health!")

    pause()


# Removes the queue front when a battle result is completed.
# The enemy is restored if the account update cannot be saved.
def remove_front_enemy():
    # DEQUEUE: removes the enemy at the front of the FIFO queue
    # We pop the front enemy after an encounter and put it back if saving fails.
    # We handle an empty queue before trying to use its front item.
    if not encounter_lineup:
        return None

    # We remove the FRONT enemy first because our encounter queue follows FIFO.
    removed = encounter_lineup.pop(0)
    if not outcome_save_active:
        # We cancel or reverse the change when the player record cannot be saved.
        if not save_current_player_account():
            encounter_lineup.insert(0, removed)
            return None
    return removed


# ---------------------------------------------------------------
# BATTLE ACTION HISTORY (STACK, LIFO)
# ---------------------------------------------------------------

# Takes a checkpoint of player, enemy, queue, history, and session data.
# This lets the game undo a result in memory if saving the outcome fails.
def begin_outcome_save():
    # We keep a full checkpoint before changing records for a win, defeat, or retreat.
    global outcome_save_active, outcome_checkpoint
    global outcome_actions_pending
    if outcome_save_active:
        return False
    # Keep the old values until the final result is written successfully.
    outcome_checkpoint = {
        # We copy nested data so changing the new state will not also change our backup.
        "player": copy.deepcopy(player),
        "account": copy.deepcopy(account_records.get(player.get("name"))),
        "queue": list(encounter_lineup),
        "history": copy.deepcopy(battle_history),
        "undo": copy.deepcopy(undo_stack),
        "archive": copy.deepcopy(session_archive),
        "mobs": [(m["id"], m["hp"], m["defeated"], m["engaged"]) for m in mob_list],
        "current_enemy": current_enemy_id,
        "effects": (boost_turns_left, boost_percent, guard_bonus_ready,
                    enemy_stunned_turns, challenge_used,
                    boss_enrage_announced, battle_turns)
    }
    outcome_actions_pending = []
    outcome_save_active = True
    return True


# Finishes saving a battle result or restores the checkpoint on failure.
# Without this, Gold, HP, and queue entries might disagree after a failed write.
def finish_outcome_save(saved):
    # We either keep a successful battle result or restore the checkpoint after a failed save.
    global outcome_save_active, outcome_checkpoint, outcome_actions_pending
    global current_enemy_id, boost_turns_left, boost_percent, guard_bonus_ready
    global enemy_stunned_turns, challenge_used, boss_enrage_announced, battle_turns
    outcome_save_active = False
    # Put the old state back if saving the victory, defeat, or retreat failed.
    if not saved and outcome_checkpoint is not None:
        checkpoint = outcome_checkpoint
        player.clear()
        player.update(checkpoint["player"])
        if checkpoint["account"] is not None:
            account_records[player["name"]] = checkpoint["account"]
        encounter_lineup[:] = checkpoint["queue"]
        battle_history[:] = checkpoint["history"]
        undo_stack[:] = checkpoint["undo"]
        session_archive.clear()
        session_archive.update(checkpoint["archive"])
        for mob_id, hp, defeated, engaged in checkpoint["mobs"]:
            mob = get_enemy_by_id(mob_id)
            if mob is not None:
                mob["hp"], mob["defeated"], mob["engaged"] = hp, defeated, engaged
        current_enemy_id = checkpoint["current_enemy"]
        (boost_turns_left, boost_percent, guard_bonus_ready,
         enemy_stunned_turns, challenge_used,
         boss_enrage_announced, battle_turns) = checkpoint["effects"]
        print("The result was not saved. Check file access before continuing.")
    outcome_actions_pending = []
    outcome_checkpoint = None
    return saved


# Gives the action a persistent ID and records its player, enemy, HP, and time.
# The action is saved right away except when a full battle outcome is being saved
# together.
def push_battle_action(
    action_type, description, enemy=None, player_hp_before=None,
    player_hp_after=None, enemy_hp_before=None, enemy_hp_after=None
):
    # We give each action a saved ID and write its HP changes to the battle history.
    # An activity record keeps both the player and enemy HP before and after the action.
    # The history log is separate from the undo stack, which stores reversible game states.
    global action_counter
    # Use a saved counter so ACT IDs do not start at 1 after each login.
    # We read the persistent counter instead of restarting action numbers on login.
    action_counter = session_archive["next_action_number"]
    # We move the saved action counter forward so a later action gets a different ID.
    session_archive["next_action_number"] += 1
    if enemy is None:
        enemy = get_current_enemy()
    action = {
        "action_id": f"ACT-{action_counter:06d}",
        "player_id": player["id"],
        "enemy_id": enemy["id"] if enemy else "N/A",
        "action_type": action_type,
        "description": description,
        "player_hp_before": player["hp"] if player_hp_before is None else player_hp_before,
        "player_hp_after": player["hp"] if player_hp_after is None else player_hp_after,
        "enemy_hp_before": (enemy["hp"] if enemy and enemy_hp_before is None
                            else enemy_hp_before),
        "enemy_hp_after": (enemy["hp"] if enemy and enemy_hp_after is None
                           else enemy_hp_after),
        "date_time": now_text()
    }
    # Each valid action goes to the history in the order it happened.
    # We add the newest activity to the end of our history list.
    battle_history.append(action)
    if outcome_save_active:
        # We hold outcome actions together until the final result is ready to save.
        outcome_actions_pending.append(action)
        return True
    # We cancel or reverse the change when the player record cannot be saved.
    if not save_current_player_account(new_action=action):
        battle_history.pop()
        session_archive["next_action_number"] = action_counter
        print("Action was not saved. Check file access before continuing.")
        return False
    return True


# Shows undoable snapshots from newest to oldest; TOP is the latest snapshot.
# These are reversible states, not the full permanent activity log.
def display_player_undo_actions(offset=0, limit=10):
    # We display the most recent reversible snapshot at the TOP of our undo stack.
    header("Player Action Stack")
    total = len(undo_stack)
    if not total:
        print("Stack Status : EMPTY")
        print("Available    : 0")
        print("TOP          : None")
        return
    offset = max(0, min(offset, total - 1))
    shown = list(reversed(undo_stack))[offset:offset + limit]
    print(f"Available: {total}  |  TOP: {undo_stack[-1]['label']}")
    print(f"Showing {offset + 1}-{offset + len(shown)} of {total}")
    rows = [[state['label'], f"{state['hp']}/{player['max_hp']}",
             state['gold'], room_name(state.get('location', current_room_id()))]
            for state in shown]
    print_table(["Action Available to Undo", "Saved HP", "Saved Gold", "Saved Room"],
                rows, max_width=34, numbered=True)


# Lets the player scroll through actions that are currently safe to undo.
def view_player_undo_actions():
    # We allow paging through undoable actions without changing the stack.
    offset = 0
    # We repeat this menu or action until the player gives a valid choice or leaves.
    while True:
        clear_screen()
        display_player_undo_actions(offset)
        total = len(undo_stack)
        if total == 0:
            pause()
            return
        older = offset + 10 < total
        newer = offset > 0
        if older:
            print("\n[1] Older Undo Actions")
        if newer:
            print("[2] Newer Undo Actions")
        print("[0] Back")
        choice = input("\nEnter choice: ").strip()
        if choice == "1" and older:
            offset += 10
        elif choice == "2" and newer:
            offset = max(0, offset - 10)
        elif choice == "0":
            return
        else:
            invalid_choice()


# Peeks at the newest undo snapshot without removing it.
def view_latest_undo_action():
    # We peek at the newest saved undo snapshot without removing it.
    header("Latest Undo Action")
    # We handle an empty undo stack so there is nothing invalid to pop.
    if not undo_stack:
        print("Stack is EMPTY. No saved action can be undone.")
    else:
        latest = undo_stack[-1]
        print(f"TOP Action: {latest['label']}")
        rows = undo_preview_rows(latest)
        if rows:
            print_table(["Value", "Current", "After Undo"], rows, max_width=35)
        else:
            print("Saved state is available for this action.")
    pause()


# Shows the latest saved battle activity without changing the action log.
def view_latest_battle_action():
    # PEEK: shows the latest action without removing it
    # We show the last recorded battle event without changing the permanent log.
    header("Latest Activity")

    # We show a clear empty-history message instead of reading a missing action.
    if not battle_history:
        print("No activities have been recorded.")
        pause()
        return

    action = battle_history[-1]

    print(f"Action ID : {action['action_id']}")
    print(f"Action    : {action['action_type']}")
    print(textwrap.fill(action['description'], width=100,
                        initial_indent="Details   : ",
                        subsequent_indent=" " * 12,
                        break_long_words=False))
    print(f"Player HP : {action['player_hp_before']} -> "
          f"{action['player_hp_after']}")
    if action["enemy_hp_before"] is not None:
        print(f"Enemy HP  : {action['enemy_hp_before']} -> "
              f"{action['enemy_hp_after']}")
    print(f"Time      : {action['date_time']}")

    pause()




# ---------------------------------------------------------------
# UNDO SYSTEM (STACK, LIFO)
# A snapshot is PUSHED before each reversible action and POPPED by Undo.
# ---------------------------------------------------------------

# Copies the current values needed to restore the game before an undoable action.
def snapshot_state(label):
    # Saves everything an undo has to restore
    # We copy the HP, inventory, enemy, queue, and effects needed to reverse an action.
    # We save the old values before the action so an Undo can restore them exactly.
    mob = get_current_enemy()

    return {
        "label": label,
        "hp": player["hp"],
        "gold": player["gold"],
        "score": player["score"],
        "inventory": dict(player["inventory"]),
        "owned_equipment": list(player["owned_equipment"]),
        "equipped": dict(player["equipped"]),
        "location": current_room_id(),
        "lineup": list(encounter_lineup),
        "status": player["status"],
        "enemy_id": mob["id"] if mob else None,
        "enemy_hp": mob["hp"] if mob else None,
        "effects": (boost_turns_left, boost_percent, guard_bonus_ready,
                    enemy_stunned_turns, challenge_used,
                    boss_enrage_announced, battle_turns),
        "log_size": len(battle_history)
    }


# Pushes a snapshot before a reversible action so Undo can restore the previous
# values.
def push_undo(label):
    # PUSH: remember the state from before the action
    # Push the old state to the top of the stack before changing the game.
    # We save the current state before a reversible action so we can undo it later.
    # We push a copy of the previous state on TOP of the undo stack.
    undo_stack.append(snapshot_state(label))


# Copies a saved snapshot back into the player, enemy, and battle state.
def restore_snapshot(snap):
    # We put all saved values from a snapshot back into the live game state.
    global boost_turns_left, boost_percent, guard_bonus_ready
    global enemy_stunned_turns, challenge_used, boss_enrage_announced
    global battle_turns

    player["hp"] = snap["hp"]
    player["gold"] = snap["gold"]
    player["score"] = snap["score"]
    player["inventory"] = dict(snap["inventory"])
    player["owned_equipment"] = list(snap["owned_equipment"])
    player["equipped"] = dict(snap["equipped"])
    if "location" in snap:
        player["location"] = snap["location"]
    if "lineup" in snap:
        encounter_lineup[:] = list(snap["lineup"])
    if "status" in snap:
        player["status"] = snap["status"]

    mob = get_enemy_by_id(snap["enemy_id"]) if snap["enemy_id"] else None

    if mob is not None and snap["enemy_hp"] is not None:
        mob["hp"] = snap["enemy_hp"]

    (boost_turns_left, boost_percent, guard_bonus_ready,
     enemy_stunned_turns, challenge_used, boss_enrage_announced,
     battle_turns) = snap["effects"]

    # The log entries made after the snapshot are popped off (LIFO)
    # We keep going while this condition is still true.
    while len(battle_history) > snap["log_size"]:
        battle_history.pop()


# Shows the current undo stack with the newest entry at the top.
def display_undo_stack():
    # We show the undo stack's TOP and available saved states.
    header("Undo Stack")
    # We handle an empty undo stack so there is nothing invalid to pop.
    if not undo_stack:
        print("Stack Status: EMPTY")
        print("No saved actions to undo.")
        return

    print(f"Available: {len(undo_stack)}  |  TOP is next to undo")
    rows = [[s["label"], f"{s['hp']}/{player['max_hp']}",
             s["gold"], room_name(s.get("location", current_room_id()))]
            for s in reversed(undo_stack)]
    print_table(["Action", "Saved HP", "Saved Gold", "Saved Room"],
                rows, max_width=32, numbered=True)


# Prepares a before/after comparison so the player knows what Undo will change.
def undo_preview_rows(snap):
    # We compare current values with the values that an Undo would restore.
    rows = []
    old_lineup = list(snap.get("lineup", encounter_lineup))
    comparisons = [
        ("HP", player["hp"], snap["hp"]),
        ("Gold", player["gold"], snap["gold"]),
        ("Score", player["score"], snap["score"]),
        ("Room", room_name(current_room_id()),
         room_name(snap.get("location", current_room_id())))
    ]
    if old_lineup != encounter_lineup:
        comparisons.append(("Queue", " -> ".join(encounter_lineup) or "(empty)",
                            " -> ".join(old_lineup) or "(empty)"))
    for label, before, after in comparisons:
        if str(before) != str(after):
            rows.append([label, before, after])
    if player["inventory"] != snap["inventory"]:
        rows.append(["Inventory", str(player["inventory"]),
                     str(snap["inventory"])])
    if (player["equipped"] != snap["equipped"] or
            player["owned_equipment"] != snap["owned_equipment"]):
        rows.append(["Equipment", "Current gear", "Previous gear"])
    if snap.get("enemy_id"):
        mob = get_enemy_by_id(snap["enemy_id"])
        if mob is not None and mob["hp"] != snap["enemy_hp"]:
            rows.append([f"{mob['name']} HP", mob["hp"], snap["enemy_hp"]])
    return rows


# Pops the latest undo snapshot and restores the earlier state.
# The game does not allow undoing permanent completed battle results.
def undo_latest_action(pause_after=True):
    # We pop the newest snapshot and restore it, but reverse the change if saving fails.
    # We copy the current values before popping, so a failed save can cancel the Undo safely.
    # Undo works in reverse order: the last reversible action is restored first.
    global boost_turns_left, boost_percent, guard_bonus_ready
    global enemy_stunned_turns, challenge_used, boss_enrage_announced, battle_turns
    # POP: restores the state from before the most recent reversible action
    header("Undo Latest Action")

    # Show a clear empty-stack message instead of trying to remove an item.
    # We handle an empty undo stack so there is nothing invalid to pop.
    if not undo_stack:
        print("Stack is EMPTY. No action is available to undo.")

        if pause_after:
            pause()

        return False

    top = undo_stack[-1]  # peek

    # Safety: a snapshot of another battle must never be applied
    if top["enemy_id"] != current_enemy_id:
        undo_stack.clear()
        save_battle_state()
        print("The saved state belongs to a different situation and was "
              "discarded.")

        if pause_after:
            pause()

        return False

    print(f"Next Undo: {top['label']}")
    rows = undo_preview_rows(top)
    if rows:
        print_table(["Value", "Current", "After Undo"], rows, max_width=35)
    else:
        print("This will restore the saved action state.")
    # We leave the current values unchanged if the player does not confirm.
    if not ask_yes_no("\nConfirm Undo? (Y/N): "):
        print("Undo cancelled. No changes were made.")
        if pause_after:
            pause()
        return False

    # We copy nested data so changing the new state will not also change our backup.
    before_player = copy.deepcopy(player)
    before_actions = copy.deepcopy(battle_history)
    before_undo = copy.deepcopy(undo_stack)
    before_session = copy.deepcopy(session_archive)
    before_mob_hp = {mob["id"]: mob["hp"] for mob in mob_list}
    before_effects = (boost_turns_left, boost_percent, guard_bonus_ready,
                      enemy_stunned_turns, challenge_used,
                      boss_enrage_announced, battle_turns)
    # We remove the latest saved state first because our stack follows LIFO.
    snap = undo_stack.pop()
    restore_snapshot(snap)

    if not push_battle_action("Undo", f"Undid: {snap['label']}."):
        player.clear()
        player.update(before_player)
        battle_history[:] = before_actions
        undo_stack[:] = before_undo
        session_archive.clear()
        session_archive.update(before_session)
        # We check each related saved record so this result uses actual game data.
        for mob in mob_list:
            mob["hp"] = before_mob_hp[mob["id"]]
        (boost_turns_left, boost_percent, guard_bonus_ready,
         enemy_stunned_turns, challenge_used,
         boss_enrage_announced, battle_turns) = before_effects
        print("Undo was cancelled because the required records could not be saved.")
        if pause_after:
            pause()
        return False

    print("Previous game state restored successfully.")
    print(f"State restored -> HP: {player['hp']}/{player['max_hp']} | "
          f"Gold: {player['gold']} | Score: {player['score']}")

    mob = get_current_enemy()

    if mob is not None:
        print(f"{mob['name']} HP restored to {mob['hp']}/{mob['max_hp']}.")

    print(f"Undo Stack now holds {len(undo_stack)} saved state(s).")
    if pause_after:
        pause()

    return True


# Keeps battle history viewing separate from undoing a reversible action.
def battle_log_menu():
    # We keep viewing the undo stack separate from actually undoing an action.
    # This screen shows actions that can still be undone; the separate activity history is permanent.
    # We repeat this menu or action until the player gives a valid choice or leaves.
    while True:
        header("Player Action Stack")
        print(f"Available Undo Actions: {len(undo_stack)}")
        print("[1] View Player Actions (Undoable)")
        print("[2] View Latest Undoable Action")
        print("[3] Undo Latest Action")
        print("\n[0] Back")
        choice = input("\nEnter choice [0-3]: ").strip()
        if choice == "1":
            view_player_undo_actions()
        elif choice == "2":
            view_latest_undo_action()
        elif choice == "3":
            undo_latest_action()
        elif choice == "0":
            break
        else:
            invalid_choice()


# ---------------------------------------------------------------
# BATTLE
# ---------------------------------------------------------------

# Starts a battle using the queue front and checks that the enemy is valid.
# The opponent stays at the front until the encounter is resolved.
def start_battle_with_next_enemy():
    # Uses the queue front or enqueues the first eligible room enemy.
    # We pick the queue's front enemy and check that the fight can legally begin.
    # The enemy must be in the proper room and unlocked difficulty before combat begins.
    # We keep the encounter at the queue front until the result is resolved.
    global current_enemy_id

    header("Start Battle with Next Enemy")

    # We check if a battle is already active before allowing this action.
    if current_enemy_id is not None:
        print(f"You are already fighting {get_current_enemy()['name']}.")
        pause()
        return

    # A player with no HP cannot begin another fight.
    if player["hp"] <= 0:
        print("Your health must be above 0. Rest at camp first.")
        pause()
        return

    # If the queue is empty, this game selects the first eligible room enemy.
    if not encounter_lineup:
        remaining = available_room_enemies()
        next_enemy = remaining[0] if remaining else None

        if next_enemy is None:
            print("No available enemies remain in this room.")
            print("Travel to a room with undefeated enemies to continue.")
            pause()
            return

        # We add a valid enemy to the REAR of the queue.
        encounter_lineup.append(next_enemy["id"])
        # We cancel or reverse the change when the player record cannot be saved.
        if not save_current_player_account():
            encounter_lineup.pop()
            print("The opponent could not be saved to the Queue.")
            pause()
            return
        print(f"\nOpponent: {next_enemy['id']} | {next_enemy['name']}")

    mob = get_enemy_by_id(encounter_lineup[0])

    # We stop here if the enemy ID does not match an existing enemy.
    if mob is None or mob["defeated"]:
        remove_front_enemy()
        save_current_player_account()
        print("\nThe front enemy is no longer available and was removed.")
        pause()
        return

    # Clear an outdated queue instead of fighting an enemy from another room.
    # We check the player's current location before deciding what is allowed.
    if mob["room"] != current_room_id():
        # We empty the old lineup because the player is starting again after defeat.
        encounter_lineup.clear()
        save_current_player_account()
        print("\nThe queued enemy is not in this room. The queue was cleared.")
        pause()
        return

    if not confirm_risky_battle(mob):
        print("\nYou stay back. Rest at camp, buy potions or use the Shop "
              "first.")
        pause()
        return

    current_enemy_id = mob["id"]
    mob["engaged"] = True
    reset_battle_effects()
    undo_stack.clear()  # camp actions cannot be undone inside a battle
    set_player_status("In Battle")

    if mob["type"] == "Boss":
        story_panel("Vharok - Keeper of the Last Gate", BOSS_INTRO, "red")
    else:
        print(f"\n{color(contextual_story([ENCOUNTER_TEXT[mob['type']]])[0], 'yellow')}")

    print()
    animate_battle_intro(mob)

    print(f"\nNext enemy: {mob['name']}.")
    print(f"Enemy HP     : {mob['hp']}/{mob['max_hp']}")
    print(f"Enemy Attack : {mob['atk']}")
    print(f"Difficulty   : {mob['type']}")
    print(f"Room         : {room_name(mob['room'])}")
    print(f"\nYour HP      : {player['hp']}/{player['max_hp']}")
    print(f"Your Attack  : {total_atk()}")

    push_battle_action(
        "Battle Start",
        f"Battle started with {mob['name']}.",
        enemy=mob
    )

    print("\nBattle started successfully.")
    pause()


# Estimates the fight based on current player and enemy stats for a warning.
def estimate_battle(mob):
    # Rough forecast if the player only attacks: how many attacks it
    # takes to win and how much damage the enemy deals meanwhile
    # We estimate how difficult the battle may be from the current combat stats.
    average_hit = (
        total_atk()
        * (100 - player_miss_chance()) / 100
        * (1 + player_crit_chance() / 100 * (PLAYER_CRIT_MULTIPLIER - 1))
    )
    attacks = max(1, math.ceil(mob["hp"] / max(1, average_hit)))
    enemy_hit = mitigate_damage(get_enemy_attack_power(mob))

    # The enemy does not strike back after the killing blow
    return attacks, enemy_hit, (attacks - 1) * enemy_hit


# Warns the player before starting a fight with a high chance of defeat.
def confirm_risky_battle(mob):
    # Returns False if the player decides not to start a likely loss
    # We warn the player if the opponent looks especially dangerous.
    attacks, enemy_hit, damage = estimate_battle(mob)

    if damage < player["hp"]:
        return True

    print()
    print(color("WARNING: this fight looks dangerous.", "red"))
    print(f"  {mob['name']} hits for about {enemy_hit} per turn.")
    print(f"  You need about {attacks} attacks to win and would take "
          f"about {damage} damage.")
    print(f"  You have {player['hp']}/{player['max_hp']} HP.")
    print("  Defending, potions and items can still turn it around.")

    return ask_yes_no("\nFight anyway? (Y/N): ")


# Rejects a combat command when there is no valid active battle.
def validate_battle_action():
    # Returns the current enemy if the player can act, otherwise None
    # We stop attacks and items when there is no valid active enemy or usable player HP.
    mob = get_current_enemy()

    # We stop here if the enemy ID does not match an existing enemy.
    if mob is None:
        print("\nNo active battle is available.")
        pause()
        return None

    if player["hp"] <= 0:
        print("\nYou cannot act with 0 HP.")
        pause()
        return None

    return mob


# Calculates damage from attack power, equipped gear, miss, and critical rules.
def calculate_player_attack(sure_hit=False):
    # Calculates the damage for the player's attack
    # We calculate randomized damage, misses, critical hits, buffs, and challenge bonuses.
    global boost_turns_left, guard_bonus_ready

    multiplier = 1.0
    notes = []

    if boost_turns_left > 0:
        multiplier += boost_percent / 100
        boost_turns_left -= 1
        notes.append(f"Tonic +{boost_percent}%")

    if guard_bonus_ready:
        multiplier += DEFEND_COUNTER_BONUS / 100
        guard_bonus_ready = False
        notes.append(f"Counter +{DEFEND_COUNTER_BONUS}%")

    # Small chance for the player's attack to miss
    if not sure_hit and random.randint(1, 100) <= player_miss_chance():
        return 0, False, True, notes

    atk = total_atk()
    strike = random.randint(
        max(1, atk - PLAYER_DAMAGE_SPREAD),
        atk + PLAYER_DAMAGE_SPREAD
    )
    strike = int(strike * multiplier)

    # Apply critical-hit rules to this single attack.
    critical = random.randint(1, 100) <= player_crit_chance()

    if critical:
        strike = int(strike * PLAYER_CRIT_MULTIPLIER)

    return strike, critical, False, notes


# Calculates the enemy attack value, including its special boss state.
def get_enemy_attack_power(mob):
    # The Boss hits harder once it drops below half health
    # We calculate the enemy's attack strength, including boss enrage when active.
    if mob["type"] == "Boss" and mob["hp"] <= mob["max_hp"] // 2:
        return int(mob["atk"] * BOSS_ENRAGE_MULTIPLIER)
    return mob["atk"]


# Calculates the enemy's hit using its stats and critical chance.
def calculate_enemy_attack(mob, guarding=False):
    # Calculates the enemy's damage (armor and shield reduce it)
    # We calculate enemy damage and critical hits before protection is applied.
    atk = get_enemy_attack_power(mob)

    damage = random.randint(
        max(1, atk - ENEMY_DAMAGE_SPREAD),
        atk + ENEMY_DAMAGE_SPREAD
    )

    critical = (
        random.randint(1, 100) <= ENEMY_CRIT_CHANCE.get(mob["type"], 5)
    )

    if critical:
        damage = int(damage * ENEMY_CRIT_MULTIPLIER)

    damage = mitigate_damage(damage)

    if guarding:
        damage = max(1, int(damage * DEFEND_DAMAGE_TAKEN))

    return damage, critical


# Runs the enemy's turn and applies defending, armor, and stun effects.
# It updates the player HP and records the enemy attack.
def process_enemy_counterattack(mob, guarding=False):
    # The enemy attacks after every player action unless it is stunned
    # We apply the enemy's reply attack and update player HP and temporary effects.
    global enemy_stunned_turns, boss_enrage_announced

    if enemy_stunned_turns > 0:
        enemy_stunned_turns -= 1

        print()
        animate_effect(f"{mob['name']} twitches... zzzt!", "yellow", "~")
        print(f"{mob['name']} is paralyzed and cannot attack!")

        push_battle_action(
            "Paralysis",
            f"{mob['name']} was paralyzed and lost its turn.",
            enemy=mob
        )
        return

    if (
        mob["type"] == "Boss"
        and mob["hp"] <= mob["max_hp"] // 2
        and not boss_enrage_announced
    ):
        boss_enrage_announced = True
        print()
        animate_effect(f"{mob['name']} ROARS", "red", "!", frames=9)
        print(color(f"{mob['name']} becomes ENRAGED! "
                    "Its attacks grow stronger.", "red"))
        push_battle_action(
            "Enrage", f"{mob['name']} became enraged.", enemy=mob
        )

    hp_before = player["hp"]
    damage, critical = calculate_enemy_attack(mob, guarding)

    player["hp"] = max(0, player["hp"] - damage)

    print()
    wait(0.3)
    animate_strike(mob["name"], "Player", critical=critical)

    if guarding:
        animate_effect("CLANG! Your guard holds", "blue", "#", frames=4)

    animate_hp_change("PLAYER", hp_before, player["hp"], player["max_hp"])

    if critical:
        print(color(f"Critical hit from {mob['name']}!", "red"))

    guard_text = " (blocked by your guard)" if guarding else ""

    print(f"{mob['name']} attacked Player for {damage} damage{guard_text}. "
          f"Player HP: {player['hp']}/{player['max_hp']}")

    push_battle_action(
        "Enemy Attack",
        f"{mob['name']} attacked Player for {damage} damage{guard_text}.",
        enemy=mob,
        player_hp_before=hp_before,
        player_hp_after=player["hp"],
        enemy_hp_before=mob["hp"],
        enemy_hp_after=mob["hp"]
    )

    print("Enemy attack recorded in Activity History.")

    if player["hp"] <= 0:
        resolve_player_defeat(mob)


# Updates temporary effects and turn counters after the player's action.
def finish_player_turn(mob, guarding=False):
    # After every player action the enemy either falls or strikes back
    # We end the player's turn and handle the counterattack when needed.
    if mob["hp"] <= 0:
        resolve_enemy_victory(mob)
    else:
        process_enemy_counterattack(mob, guarding)

    save_current_player_account()
    pause()


# Processes the player attack, records HP changes, and checks for victory.
# If the enemy survives, the enemy takes its turn afterward.
def attack_current_enemy():
    # Handles one complete attack turn
    # We apply player attack damage, log the action, and check for victory.
    global battle_turns

    mob = validate_battle_action()

    # We stop here if the enemy ID does not match an existing enemy.
    if mob is None:
        return

    push_undo(f"Attack on {mob['name']}")

    battle_turns += 1
    enemy_hp_before = mob["hp"]
    print()

    strike, critical, missed, notes = calculate_player_attack()
    bonus_text = f" ({', '.join(notes)})" if notes else ""

    animate_strike("Player", mob["name"], missed, critical)

    if missed:
        print(f"You attacked {mob['name']} but missed!")
        description = f"Player attacked {mob['name']} but missed."
    else:
        mob["hp"] = max(0, mob["hp"] - strike)

        animate_hp_change("ENEMY ", enemy_hp_before, mob["hp"], mob["max_hp"])

        crit_text = color("CRITICAL! ", "yellow") if critical else ""

        print(f"{crit_text}Player attacked {mob['name']} for {strike} damage"
              f"{bonus_text}. {mob['name']} HP: {mob['hp']}/{mob['max_hp']}")
        description = (
            f"Player attacked {mob['name']} for {strike} damage"
            f"{' (critical)' if critical else ''}."
        )

    push_battle_action(
        "Attack",
        description,
        enemy=mob,
        enemy_hp_before=enemy_hp_before,
        enemy_hp_after=mob["hp"]
    )

    print("Player attack recorded in Activity History.")

    finish_player_turn(mob)


# Reduces incoming damage for a turn and prepares the defensive counter effect.
def defend_against_enemy():
    # Raises the guard: less damage now, stronger counterattack next
    # We lower the damage taken this turn and prepare the defense counter bonus.
    global battle_turns, guard_bonus_ready

    mob = validate_battle_action()

    # We stop here if the enemy ID does not match an existing enemy.
    if mob is None:
        return

    push_undo(f"Defend against {mob['name']}")

    battle_turns += 1
    guard_bonus_ready = True

    print()
    animate_effect("[ ] You raise your shield [ ]", "blue", "#")
    print(f"You raise your guard. Next attack +{DEFEND_COUNTER_BONUS}% damage.")

    push_battle_action(
        "Defend",
        f"Player defended against {mob['name']}.",
        enemy=mob
    )

    finish_player_turn(mob, guarding=True)


# Validates potion stock, heals without going over Max HP, and saves the new quantity.
def use_health_potion():
    # Uses the first healing item the player owns
    # We spend one potion only when it can actually restore health.
    mob = validate_battle_action()

    # We stop here if the enemy ID does not match an existing enemy.
    if mob is None:
        return

    # We check each related saved record so this result uses actual game data.
    for item_id, item in item_records.items():
        if item["effect"] == "heal" and item_quantity(item_id) > 0:
            apply_item_effect(item, mob)
            return

    print("\nInsufficient potion quantity. No potion is available.")
    print("Buy Health Potions at the Dungeon Shop between battles.")
    pause()


# Lets the player choose an inventory item that can be used in battle.
def use_item():
    # Lets the player choose any item from the inventory
    # We verify the selected item is owned and usable before applying its effect.
    mob = validate_battle_action()

    # We stop here if the enemy ID does not match an existing enemy.
    if mob is None:
        return

    # We repeat this menu or action until the player gives a valid choice or leaves.
    while True:
        header("Use Item")

        owned = [
            item_id for item_id in item_records
            if item_quantity(item_id) > 0
        ]

        if not owned:
            print("Your inventory is empty.")
            print("Buy items at the Dungeon Shop between battles.")
            pause()
            return

        print_table(["ID", "Item", "Owned", "Effect"],
                    [[item_id, item_records[item_id]["name"],
                      item_quantity(item_id),
                      describe_item_effect(item_records[item_id])]
                     for item_id in owned], max_width=32, numbered=True)

        print("\n[0] Back")

        choice = input(f"\nChoose an item [0-{len(owned)}]: ").strip()

        if choice == "0":
            return

        if not choice.isdigit() or not 1 <= int(choice) <= len(owned):
            invalid_choice()
            continue

        # One item per turn, so the menu closes after a successful use
        if apply_item_effect(item_records[owned[int(choice) - 1]], mob):
            return


# Applies the selected item's heal, boost, stun, or damage effect.
# The item quantity and battle action are updated after a valid use.
def apply_item_effect(item, mob):
    # Applies one item. Returns True if the player's turn was used.
    # We apply healing, damage, attack boost, or stun according to that item's saved effect.
    global battle_turns, boost_turns_left, boost_percent
    global enemy_stunned_turns

    effect = item["effect"]

    if effect == "heal" and player["hp"] >= player["max_hp"]:
        print("\nYour HP is already full.")
        pause()
        return False

    if effect == "boost" and boost_turns_left > 0:
        print(f"\nA tonic is still active ({boost_turns_left} attacks left).")
        pause()
        return False

    if effect == "stun" and enemy_stunned_turns > 0:
        print(f"\n{mob['name']} is already paralyzed.")
        pause()
        return False

    push_undo(f"Use {item['name']}")

    battle_turns += 1
    change_item_quantity(item["id"], -1)
    remaining = item_quantity(item["id"])

    print()

    if effect == "heal":
        hp_before = player["hp"]
        heal = max(1, player["max_hp"] * item["power"] // 100)
        player["hp"] = min(player["max_hp"], player["hp"] + heal)

        animate_effect("glug glug... healing light", "green", "+")
        animate_hp_change("PLAYER", hp_before, player["hp"], player["max_hp"])

        print("Potion used successfully. Player health has been restored.")
        print(f"HP: {hp_before} -> {player['hp']} | "
              f"{item['name']} left: {remaining}")

        push_battle_action(
            "Potion Use",
            f"Player used one {item['name']} and restored "
            f"{player['hp'] - hp_before} HP.",
            enemy=mob,
            player_hp_before=hp_before,
            player_hp_after=player["hp"]
        )

    elif effect == "boost":
        boost_turns_left = BOOST_ATTACKS
        boost_percent = item["power"]

        animate_effect("Power surges through you", "magenta", "^")
        print(f"{item['name']} used! Next {BOOST_ATTACKS} attacks "
              f"+{boost_percent}% damage. ({remaining} left)")

        push_battle_action(
            "Item Use",
            f"Player used {item['name']} (+{boost_percent}% damage).",
            enemy=mob
        )

    elif effect == "stun":
        animate_strike("Player", mob["name"])

        if random.randint(1, 100) <= STUN_CHANCE:
            animate_effect("zzzt! ZZZT!", "yellow", "~")
            enemy_stunned_turns = item["power"]
            message = (
                f"{mob['name']} was paralyzed for {item['power']} turns."
            )
            print(f"Success! {message}")
        else:
            message = f"{item['name']} failed against {mob['name']}."
            print(f"{mob['name']} resisted the {item['name']}!")

        print(f"({remaining} {item['name']} left)")
        push_battle_action("Item Use", message, enemy=mob)

    elif effect == "damage":
        enemy_hp_before = mob["hp"]
        damage = random.randint(max(1, item["power"] - 5), item["power"] + 5)
        mob["hp"] = max(0, mob["hp"] - damage)

        animate_strike("Player", mob["name"], critical=True)
        animate_effect("BOOM!", "red", "*")
        animate_hp_change("ENEMY ", enemy_hp_before, mob["hp"], mob["max_hp"])

        print(f"{item['name']} dealt {damage} damage! "
              f"{mob['name']} HP: {mob['hp']}/{mob['max_hp']} "
              f"({remaining} left)")

        push_battle_action(
            "Item Use",
            f"Player dealt {damage} damage to {mob['name']} "
            f"using {item['name']}.",
            enemy=mob,
            enemy_hp_before=enemy_hp_before,
            enemy_hp_after=mob["hp"]
        )

    finish_player_turn(mob)
    return True


# Checks the selected answer and applies extra damage when the answer is correct.
def answer_challenge_question():
    # Once per battle: a correct answer is a sure hit with bonus damage
    # We check the selected quiz answer and apply the attack bonus only when correct.
    global battle_turns, challenge_used

    mob = validate_battle_action()

    # We stop here if the enemy ID does not match an existing enemy.
    if mob is None:
        return

    if challenge_used:
        print("You already answered a challenge in this battle.")
        pause()
        return

    question = question_for_enemy(mob)
    if question is None:
        print("There is no Challenge question available for this difficulty.")
        pause()
        return
    correct_text = question["choices"][question["answer"] - 1]

    # The choices are shuffled so players cannot memorise the numbers
    choices = list(question["choices"])
    random.shuffle(choices)

    section(f"Challenge: {mob['type']} Level")
    print(f"Enemy: {mob['name']}")
    print(f"Question: {question['question']}")
    print(f"Attack Bonus: +{question['bonus']} damage on a correct answer")
    print("Effect: Guaranteed hit with bonus damage (this attack only)")
    print()

    for number, choice in enumerate(choices, 1):
        print(f"  [{number}] {choice}")

    picked = ask_int(f"\nYour answer [1-{len(choices)}]: ", 1, len(choices))

    push_undo(f"Challenge question {question['id']}")

    battle_turns += 1
    challenge_used = True

    if choices[picked - 1] == correct_text:
        enemy_hp_before = mob["hp"]
        strike, critical, _, _ = calculate_player_attack(sure_hit=True)
        strike += question["bonus"]
        mob["hp"] = max(0, mob["hp"] - strike)

        print()
        animate_effect("Correct! Knowledge is power", "green", "?")
        animate_strike("Player", mob["name"], critical=True)
        animate_hp_change("ENEMY ", enemy_hp_before, mob["hp"], mob["max_hp"])

        crit_text = " CRITICAL!" if critical else ""

        section("Challenge Success")
        print(f"Result: Correct!{crit_text}")
        print(f"Attack Bonus: +{question['bonus']} damage")
        print(f"Total Damage: {strike}")
        print(f"Enemy HP: {mob['hp']}/{mob['max_hp']}")

        push_battle_action(
            "Challenge",
            f"Player answered {question['id']} correctly and earned "
            f"+{question['bonus']} challenge attack damage; "
            f"dealt {strike} total damage to {mob['name']}.",
            enemy=mob,
            enemy_hp_before=enemy_hp_before,
            enemy_hp_after=mob["hp"]
        )
    else:
        print(f"\nIncorrect. The correct answer was: {correct_text}")
        print("Attack Bonus: +0")
        print("You lose this turn. No bonus attack damage awarded.")

        push_battle_action(
            "Challenge",
            f"Player answered {question['id']} incorrectly.",
            enemy=mob
        )

    finish_player_turn(mob)


# Confirms that the player wants to retreat instead of finishing the fight.
def retreat_from_battle():
    # Free retreat: the battle is interrupted, never "won"
    # We ask for confirmation before the player leaves the active fight.
    mob = get_current_enemy()

    # We stop here if the enemy ID does not match an existing enemy.
    if mob is None:
        print("\nNo active battle is available.")
        pause()
        return

    print(f"\nRetreating leaves {mob['name']} in the Encounter Queue and it "
          "heals fully.")

    # We leave the current values unchanged if the player does not confirm.
    if not ask_yes_no("Retreat? (Y/N): "):
        print("\nYou stand your ground.")
        pause()
        return

    resolve_retreat(mob)
    pause()


# Clears temporary fight state so it cannot leak into the next encounter.
def end_current_battle():
    # Once a battle ends, we clear the Undo Stack because the result is final.
    # emptied. Otherwise Undo could duplicate rewards or skip defeats.
    # We clear temporary battle state and pending undo snapshots after a final result.
    global current_enemy_id

    mob = get_current_enemy()

    if mob is not None:
        mob["engaged"] = False

    current_enemy_id = None
    undo_stack.clear()
    reset_battle_effects()
    if not outcome_save_active:
        save_battle_state()


# Resets the enemy according to the retreat rule and ends the current fight.
# The retreat is recorded without giving a victory or level reward.
def resolve_retreat(mob):
    # Interrupts the battle. The enemy is NOT defeated and is NOT
    # dequeued: it keeps its place in the queue with full HP.
    # We leave the enemy in the queue with full HP but do not award a victory.
    # Retreat is not a victory: we do not award enemy Gold or count the enemy as defeated.
    # The enemy returns to full HP and remains at the front of the queue.
    begin_outcome_save()
    turns = battle_turns

    push_battle_action(
        "Retreat",
        f"Player retreated from {mob['name']}.",
        enemy=mob
    )

    # We restore this enemy to its full HP so a future attempt starts fairly.
    mob["hp"] = mob["max_hp"]
    mob["defeated"] = False
    player["wounds"].pop(mob["id"], None)
    set_player_status("Retreated")

    # We clear active combat flags and temporary effects after resolving the result.
    end_current_battle()
    # We stop if the whole battle result could not be saved consistently.
    if not finish_outcome_save(record_battle_result(mob, "Retreated", 0, 0, turns)):
        return False

    print(f"You retreat from {mob['name']}. It was not defeated.")
    print(f"{mob['name']} recovers its health "
          f"({mob['hp']}/{mob['max_hp']}) and waits in the queue.")
    print(f"Queue: {lineup_line()}")
    return True


# Marks the enemy defeated, adds gold and score, and dequeues that enemy.
# It also checks whether this is the third required victory for the difficulty.
def resolve_enemy_victory(mob):
    # Gives rewards and removes the defeated enemy from the queue
    # We award the enemy's Gold and score, update progress, then dequeue the defeated enemy.
    # We apply regular enemy rewards before checking for a separate one-time level bonus.
    # The defeated enemy is removed from the FRONT, then we save the completed encounter.
    begin_outcome_save()
    old_rank = get_player_rank_info()
    turns = battle_turns

    mob["hp"] = 0
    mob["defeated"] = True

    if mob["id"] not in player["defeated_ids"]:
        player["defeated_ids"].append(mob["id"])

    player["wounds"].pop(mob["id"], None)
    # The win, Gold, and score updates happen together with the enemy defeat.
    # We increase the win total after the enemy is actually defeated.
    player["wins"] += 1
    # We add the enemy reward separately from any one-time level-completion bonus.
    player["gold"] += mob["gold_reward"]
    # We add the enemy score only after the victory is confirmed.
    player["score"] += mob["score_reward"]
    # We make the player active again after the encounter ends.
    set_player_status("Active")

    push_battle_action("Victory", f"Player defeated {mob['name']}.",
                       enemy=mob, enemy_hp_after=0)
    push_battle_action("Reward", f"Player received {mob['gold_reward']} gold.",
                       enemy=mob)

    push_battle_action("Reward",
                       f"Player earned {mob['score_reward']} score points.",
                       enemy=mob)

    # The third required victory may give an extra one-time level reward.
    # We check for the third required victory after awarding the normal enemy reward.
    level_reward = process_level_completion(mob["type"], mob)
    new_rank = get_player_rank_info()

    if old_rank["rank"] != new_rank["rank"]:
        push_battle_action(
            "Progression",
            f"Rank increased from {old_rank['rank']} to {new_rank['rank']}.",
            enemy=mob
        )

    print()
    animate_banner("V I C T O R Y !", "green")
    section("Battle Result")
    print_table(["Enemy", "Result", "Gold", "Score", "Total Wins"],
                [[mob["name"], "Victory", f"+{mob['gold_reward']}",
                  f"+{mob['score_reward']}", player["wins"]]],
                max_width=30)

    if level_reward is not None:
        show_level_completion_rewards(level_reward, old_rank, new_rank)

    # Shows the queue before and after the defeated enemy is dequeued
    print(f"Queue before dequeue: {lineup_line()}")

    # After victory, take the defeated enemy off the FRONT of the queue.
    removed_id = remove_front_enemy()

    if removed_id != mob["id"]:
        print("\nThe lineup could not be updated correctly.")

    # We clear active combat flags and temporary effects after resolving the result.
    end_current_battle()
    # We stop if the whole battle result could not be saved consistently.
    if not finish_outcome_save(record_battle_result(
        mob, "Victory",
        mob["gold_reward"]
        + (level_reward["gold_bonus"] if level_reward else 0),
        mob["score_reward"],
        turns
    )):
        return False

    print(f"Queue after dequeue : {lineup_line()}")

    print(f"Progress: HP: {player['hp']}/{player['max_hp']} | "
          f"Wins: {player['wins']} | Score: {player['score']} | "
          f"Gold: {player['gold']} | ATK: {total_atk()}")

    if old_rank["rank"] != new_rank["rank"] and level_reward is None:
        print(f"Rank Up: {old_rank['rank']} -> {new_rank['rank']}. "
              f"You can now fight {new_rank['max_difficulty']} enemies.")

    # Unlock the path to the Last Gate after the final boss is defeated
    if mob["type"] == "Boss" and mob["id"] in player["defeated_ids"]:
        story_panel("Dreadveil\'s Curse Is Broken", contextual_story(BOSS_DEFEAT), "green")
        print(f"{room_name(EXIT_ROOM_ID)} is now accessible. "
              f"Use Travel to Connected Room via "
              f"{passage_name('ROOM-004', EXIT_ROOM_ID)}.")

    return True


# Records the loss, restores the enemy to FULL HP, and clears the queue.
# The player returns to the saved entrance name with half their Max HP.
# Earlier victories and unlocked rooms remain saved.
def resolve_player_defeat(mob):
    # Ends the battle when the player's HP reaches zero
    # We record the loss, reset the enemy to full HP, and respawn at the entrance.
    # We keep earlier victories and unlocked rooms, but clear the current encounter queue.
    # We reset the enemy to full HP and remove its saved wounds so it stays healed after reload.
    # The entrance message reads its real name from the room record, not a hard-coded phrase.
    begin_outcome_save()
    turns = battle_turns
    # Losing a battle takes the configured percentage of current Gold.
    # We calculate the Gold penalty using the player's balance at the time of defeat.
    gold_lost = player["gold"] * DEFEAT_GOLD_LOSS_PERCENT // 100

    # We count this encounter as a loss for the player.
    player["losses"] += 1
    # We deduct the configured percentage of Gold after a defeat.
    player["gold"] -= gold_lost
    # We record the defeat before the respawn values are applied.
    set_player_status("Defeated")

    push_battle_action(
        "Player Defeat",
        f"Player was defeated by {mob['name']} and lost {gold_lost} gold.",
        enemy=mob,
        player_hp_after=0
    )

    print()
    animate_banner("D E F E A T", "red")
    section("Battle Result")
    print_table(["Enemy", "Result", "Gold Lost", "Total Losses"],
                [[mob["name"], "Defeat", gold_lost, player["losses"]]],
                max_width=30)

    # Empty the encounter queue after the player is defeated
    # The old encounter queue is cleared when the player respawns.
    # We empty the old lineup because the player is starting again after defeat.
    encounter_lineup.clear()
    print(f"Defeated! You are returned to {room_name(ENTRANCE_ROOM_ID)}. "
          "Your Encounter Queue was cleared.")

    # As with Retreat, the surviving enemy fully recovers after winning.
    # Clear this player's saved wounds so revisiting the room or reloading
    # cannot restore the enemy's pre-defeat damaged HP.
    # We restore this enemy to its full HP so a future attempt starts fairly.
    mob["hp"] = mob["max_hp"]
    mob["defeated"] = False
    # We remove any saved partial HP for this enemy, so it reloads at full health.
    player["wounds"].pop(mob["id"], None)
    push_battle_action(
        "Enemy Recovery",
        f"{mob['name']} fully recovered after the player's defeat "
        f"({mob['hp']}/{mob['max_hp']} HP).",
        enemy=mob, enemy_hp_after=mob["hp"]
    )
    print(f"{mob['name']} returns to FULL HP "
          f"({mob['hp']}/{mob['max_hp']}). You can challenge it again later.")

    # The player returns to Dreadveil Entrance with the established
    # 50%-Max-HP revive rule; existing cleared enemies remain cleared.
    # Revive the player with the configured share of Max HP, never below 1.
    # We revive the player at the configured share of Max HP, with at least one HP.
    player["hp"] = max(1, player["max_hp"] * DEFEAT_REVIVE_PERCENT // 100)
    # We return the player to the entrance room after losing the fight.
    player["location"] = ENTRANCE_ROOM_ID
    # We make the player active again after the encounter ends.
    set_player_status("Active")
    print(f"You awaken at {room_name(ENTRANCE_ROOM_ID)} "
          f"with {player['hp']}/{player['max_hp']} HP.")
    print("Your unlocked rooms and earlier victories are preserved. "
          "Travel through the connected rooms to challenge the enemy again.")

    # We clear active combat flags and temporary effects after resolving the result.
    end_current_battle()
    # We stop if the whole battle result could not be saved consistently.
    if not finish_outcome_save(record_battle_result(mob, "Defeat", -gold_lost, 0, turns)):
        return False
    return True


# ---------------------------------------------------------------
# CAMP ACTIONS (shop, equipment, rest, travel, dungeon exit)
# ---------------------------------------------------------------

# Calculates how much more Gold the player needs for a purchase.
def shortfall_message(price, what="item"):
    # Exact amount of Gold still missing for a purchase
    # We calculate the missing Gold when the player cannot afford a purchase.
    missing = price - player["gold"]
    return f"You need {missing} more Gold to purchase this {what}."


# Displays the item price, current Gold, and missing amount after a failed purchase.
def show_shortfall(price, what="item"):
    # Same "not enough Gold" notice for every shop. Nothing is deducted.
    # We show the price and the amount of additional Gold required.
    print(f"\n{color(shortfall_message(price, what), 'red')}")
    print(f"  Current Gold : {player['gold']}")
    print(f"  Price        : {price}")
    print(f"  Missing Gold : {price - player['gold']}")


# Prints a simple confirmation after a purchase changes the player inventory.
def show_purchase_receipt(title, lines):
    # Same "purchase successful" notice for every shop
    # We print what was purchased and the updated account balance.
    print(f"\n{color('Purchase successful!', 'green')}")
    print(f"  Item         : {title}")

    for line in lines:
        print(f"  {line}")

    print(f"  Gold left    : {player['gold']}")


# Prepares the displayed name and price for a shop item.
def shop_entry(number, name, price, tag, detail):
    # One shop listing: used by both the Supplies and Equipment shops
    # We format one item or equipment option for the shop menu.
    print(f"[{number}] {name} - {price} Gold ({tag})")
    print(f"    {detail}")


# Lets the player choose between consumable supplies and equipment upgrades.
def dungeon_shop():
    # The player can buy items and equipment here between battles
    # We let the player choose between supplies and equipment.
    # We check if a battle is already active before allowing this action.
    if current_enemy_id is not None:
        print("\nYou cannot shop during a battle.")
        pause()
        return

    # We repeat this menu or action until the player gives a valid choice or leaves.
    while True:
        header("Dungeon Shop")

        print(f"Gold: {player['gold']}")

        section("Departments")
        print("[1] Supplies (potions and battle items)")
        print("[2] Equipment (two upgrades per slot at current level)")
        print("\n[0] Back")

        choice = input("\nEnter choice [0-2]: ").strip()

        if choice == "1":
            supplies_shop()
        elif choice == "2":
            equipment_shop()
        elif choice == "0":
            print("\nYou leave the Dungeon Shop.")
            break
        else:
            invalid_choice()


# Checks item availability, carry limit, and Gold before buying supplies.
# The player is charged only when the purchase is valid.
def supplies_shop():
    # We validate item prices, carrying limits, and Gold before taking payment.
    # We repeat this menu or action until the player gives a valid choice or leaves.
    while True:
        header("Dungeon Shop - Supplies")

        print(f"Gold: {player['gold']}")

        section("Potions and Battle Items")

        items = list(item_records.values())

        print_table(["ID", "Item", "Gold", "Owned/Max", "Effect"],
                    [[item["id"], item["name"], item["price"],
                      f"{item_quantity(item['id'])}/{item['max_carry']}",
                      describe_item_effect(item)] for item in items],
                    max_width=34, numbered=True)

        print("\n[0] Back")

        choice = input(f"\nChoose an item [0-{len(items)}]: ").strip()

        if choice == "0":
            break

        if not choice.isdigit() or not 1 <= int(choice) <= len(items):
            invalid_choice()
            continue

        item = items[int(choice) - 1]
        space = item["max_carry"] - item_quantity(item["id"])

        if space <= 0:
            print(f"\nYou cannot carry more than {item['max_carry']} "
                  f"{item['name']}.")
            pause()
            continue

        qty = ask_int(f"How many? [1-{space}] (default 1): ", 1, space, 1)
        total = item["price"] * qty

        # Not enough Gold: nothing is deducted and nothing is added
        # We compare the price with the player's Gold before charging anything.
        if player["gold"] < total:
            show_shortfall(total, "item")
            pause()
            continue

        # We leave the current values unchanged if the player does not confirm.
        if not ask_yes_no(f"Buy {qty} {item['name']} for {total} Gold? (Y/N): "):
            print("\nPurchase cancelled.")
            pause()
            continue

        push_undo(f"Buy {qty} {item['name']}")

        player["gold"] -= total
        change_item_quantity(item["id"], qty)

        push_battle_action(
            "Purchase", f"Player bought {qty} {item['name']} for {total} gold."
        )
        save_current_player_account()

        show_purchase_receipt(
            f"{item['name']} x{qty}",
            [f"Quantity     : {item_quantity(item['id'])}"]
        )

        pause()


# Checks the unlocked tier, owned equipment, and Gold before buying gear.
def equipment_shop():
    # We offer gear from the currently unlocked tier and avoid invalid purchases.
    # We repeat this menu or action until the player gives a valid choice or leaves.
    while True:
        tier = current_equipment_tier()
        header(f"Dungeon Shop - {tier} Equipment")
        print(f"Current Level: {tier} | Gold: {player['gold']}")
        print("Every level grants free gear. Shop upgrades are optional.")

        section("YOUR CURRENT EQUIPMENT")
        rows = []
        for slot in EQUIPMENT_SLOTS:
            piece = equipped_piece(slot)
            rows.append([slot.title(), piece["name"], describe_piece(piece),
                         piece["source"]])
        print_table(["Slot", "Currently Worn", "Combat Stats", "Origin"],
                    rows, max_width=29)

        # List only the purchasable upgrades for the current equipment tier.
        available = [e for e in equipment_records.values()
                     if e["tier"] == tier]
        available.sort(key=lambda e: (EQUIPMENT_SLOTS.index(e["slot"]),
                                      e["bonus"], e.get("speed", 0)))

        choices = []
        for slot in EQUIPMENT_SLOTS:
            section(f"{slot.upper()} UPGRADES")
            rows = []
            for eq in available:
                if eq["slot"] != slot:
                    continue
                state = equipment_state(eq["id"])
                worn = equipped_piece(slot)
                # An inferior unsold piece is a downgrade, not an upgrade.
                if (state == "Not owned" and eq["bonus"] <= worn["bonus"]
                        and (slot != "sword" or
                             eq.get("speed", 0) <= worn.get("speed", 0))):
                    continue
                number = "-" if state != "Not owned" else str(len(choices) + 1)
                if state == "Not owned":
                    choices.append(eq)
                rows.append([number, eq["name"], describe_equipment(eq),
                             compare_text(eq), eq["price"],
                             "Owned" if state != "Not owned" else "For sale"])
            if rows:
                print_table(["No.", "Upgrade", "Combat Stats", "vs Worn",
                             "Gold", "Status"], rows, max_width=26)
            else:
                print("No upgrades for this slot at your current level.")

        section("A WHISPER FROM THE ARMORY")
        if tier != "Boss":
            print("\"The veil hides stronger steel beyond each gate. Win three")
            print(" battles at this difficulty, and the next armory will answer.\"")
        else:
            print("\"Vharok awaits beyond the throne. Choose your gear wisely;")
            print(" the Last Gate will open only when he falls.\"")

        if not choices:
            print("\nYou own every upgrade available at this level.")
        print("\n[0] Back to Dungeon Shop")

        choice = input(f"\nBuy which upgrade? [0-{len(choices)}]: ").strip()
        if choice == "0":
            break
        if not choice.isdigit() or not 1 <= int(choice) <= len(choices):
            invalid_choice()
            continue

        eq = choices[int(choice) - 1]
        if eq["id"] in player["owned_equipment"]:
            print("\nYou already own that upgrade.")
            pause()
            continue
        if eq["tier"] != current_equipment_tier():
            print("\nOnly current-level upgrades can be purchased.")
            pause()
            continue
        # We compare the price with the player's Gold before charging anything.
        if player["gold"] < eq["price"]:
            show_shortfall(eq["price"], "equipment")
            pause()
            continue

        print(f"\n{eq['name']} | {describe_equipment(eq)}")
        print(f"Compared with your current gear: {compare_text(eq)}")
        # We leave the current values unchanged if the player does not confirm.
        if not ask_yes_no(f"Buy for {eq['price']} Gold? (Y/N): "):
            print("\nPurchase cancelled.")
            pause()
            continue

        push_undo(f"Buy {eq['name']}")
        worn_before = equipped_piece(eq["slot"])
        player["gold"] -= eq["price"]
        player["owned_equipment"].append(eq["id"])

        stronger = eq["bonus"] > worn_before["bonus"]
        if eq["slot"] == "sword" and eq.get("speed", 0) > worn_before.get("speed", 0):
            stronger = True
        if stronger:
            player["equipped"][eq["slot"]] = eq["id"]
            equipped_note = f"Equipped     : yes; replaced {worn_before['name']}"
        else:
            equipped_note = ("Equipped     : no; use Equipment to choose "
                             "a previously purchased item")

        push_battle_action(
            "Purchase", f"Player bought {eq['name']} for {eq['price']} gold."
        )
        save_current_player_account()
        show_purchase_receipt(
            f"{eq['name']} ({describe_equipment(eq)})", [equipped_note]
        )
        pause()


# Lists owned equipment and lets the player equip or unequip allowed items.
def equipment_menu():
    # Players may equip only their current-level purchases or the free default.
    # We show owned equipment and let the player change sword, shield, or armor.
    # We check if a battle is already active before allowing this action.
    if current_enemy_id is not None:
        print("\nYou cannot change equipment during a battle.")
        pause()
        return

    # We repeat this menu or action until the player gives a valid choice or leaves.
    while True:
        header(f"Equipment - {current_equipment_tier()} Level")
        print(f"ATK: {total_atk()} | SPD: +{sword_speed()}% | "
              f"DEF: -{armor_defense()} | BLOCK: {shield_block()}%")
        print("Previous-level purchases are kept in Inventory but cannot "
              "replace the current level's gear.")
        options = []

        for slot in EQUIPMENT_SLOTS:
            section(slot.upper())
            std = standard_piece(slot)
            worn = equipped_piece(slot)
            rows = []
            options.append((slot, None))
            state = "Equipped" if worn["id"] is None else "Available"
            rows.append([len(options), std["name"], describe_piece(std),
                         f"Free / {state}"])
            for eid in player["owned_equipment"]:
                eq = equipment_records.get(eid)
                if (eq is None or eq["slot"] != slot
                        or eq["tier"] != current_equipment_tier()):
                    continue
                options.append((slot, eid))
                rows.append([len(options), eq["name"], describe_equipment(eq),
                             equipment_state(eid)])
            print_table(["No.", "Equipment", "Stats", "Status"], rows,
                        max_width=30)

        print("\n[0] Back")
        choice = input(f"\nWear which piece? [0-{len(options)}]: ").strip()
        if choice == "0":
            break
        if not choice.isdigit() or not 1 <= int(choice) <= len(options):
            invalid_choice()
            continue

        slot, eid = options[int(choice) - 1]
        if eid is None:
            piece = standard_piece(slot)
            if equipped_piece(slot)["id"] is None:
                print(f"\n{piece['name']} is already equipped.")
                pause()
                continue
            push_undo(f"Equip {piece['name']}")
            player["equipped"].pop(slot, None)
            push_battle_action("Equip", f"Player equipped {piece['name']}.")
            save_current_player_account()
            print(f"\n{piece['name']} equipped. {describe_piece(piece)}")
            pause()
            continue

        eq = equipment_records[eid]
        if eq["tier"] != current_equipment_tier():
            print("\nThat gear belongs to a previous level.")
            pause()
            continue
        if player["equipped"].get(slot) == eid:
            print(f"\n{eq['name']} is already equipped.")
            pause()
            continue
        push_undo(f"Equip {eq['name']}")
        player["equipped"][slot] = eid
        push_battle_action("Equip", f"Player equipped {eq['name']}.")
        save_current_player_account()
        print(f"\n{eq['name']} equipped. {describe_equipment(eq)}")
        pause()


# Allows one treasure reward per room after every enemy there is defeated.
# Treasure completion is optional and separate from the three-victory gate quota.
def open_treasure_chest():
    # Optional full-clear bonus: chests still require every enemy in
    # the room to be defeated. Room progression needs only 3 tier victories.
    # We give the one-time chest reward only after every enemy in that room is defeated.
    # A chest has a different rule from level unlocking: all enemies in the room must be defeated.
    # We also save which chest was opened so the player cannot collect it twice.
    header("Treasure Chest")

    # We check if a battle is already active before allowing this action.
    if current_enemy_id is not None:
        print("You cannot open a chest during a battle.")
        pause()
        return

    here = current_room_id()
    chest = TREASURES.get(here)

    if chest is None:
        print(f"There is no treasure chest in {room_name(here)}.")
        chest_rooms = ", ".join(room_name(room_id) for room_id in TREASURES)
        print(f"Treasure chests are hidden in: {chest_rooms}.")
        pause()
        return

    name, rarity, gold = chest

    if here in player["treasures"]:
        print(f"The {name} has already been opened.")
        pause()
        return

    remaining = [m for m in get_room_enemies(here) if not m["defeated"]]

    if remaining:
        print(f"The {name} is guarded.")
        print(f"Defeat every enemy in {room_name(here)} first "
              f"({len(remaining)} remaining).")
        pause()
        return

    # Opening a chest clears reversible states from other actions
    undo_stack.clear()
    player["treasures"].append(here)
    player["gold"] += gold
    player["score"] += TREASURE_SCORE

    push_battle_action(
        "Treasure",
        f"Player opened the {name} ({rarity}) and found {gold} gold."
    )
    save_current_player_account()

    print(f"You open the {name} ({rarity} treasure).")
    print(f"  Gold found : +{gold}")
    print(f"  Score      : +{TREASURE_SCORE}")
    print(f"  Gold now   : {player['gold']}")
    pause()


# Charges the stated Gold amount and restores HP using the camp rest rule.
def rest_at_camp():
    # Pays gold to recover part of the player's health
    # We charge the rest fee and restore a portion of missing HP when resting is allowed.
    header("Rest at Camp")

    # We check if a battle is already active before allowing this action.
    if current_enemy_id is not None:
        print("You cannot rest during a battle.")
        pause()
        return

    if player["hp"] >= player["max_hp"]:
        print("Your HP is already full.")
        pause()
        return

    # We compare the price with the player's Gold before charging anything.
    if player["gold"] < REST_COST:
        print(f"Resting costs {REST_COST} Gold.")
        show_shortfall(REST_COST, "rest")
        pause()
        return

    heal = player["max_hp"] * REST_HEAL_PERCENT // 100
    hp_before = player["hp"]

    print(f"Resting restores up to {heal} HP for {REST_COST} Gold.")

    # We leave the current values unchanged if the player does not confirm.
    if not ask_yes_no("Rest now? (Y/N): "):
        print("\nYou keep moving.")
        pause()
        return

    push_undo("Rest at camp")

    player["gold"] -= REST_COST
    player["hp"] = min(player["max_hp"], player["hp"] + heal)

    push_battle_action(
        "Camp Rest",
        f"Player rested and restored {player['hp'] - hp_before} HP.",
        player_hp_before=hp_before
    )
    save_current_player_account()

    print(f"\nHP: {hp_before} -> {player['hp']}")
    print(f"Gold left: {player['gold']}")
    pause()


# Checks whether the final boss requirement has been completed.
def all_bosses_defeated(defeated_ids):
    # We check whether the boss has been defeated before unlocking the exit.
    bosses = [mob for mob in mob_list if mob["type"] == "Boss"]
    return bool(bosses) and all(m["id"] in defeated_ids for m in bosses)


# Returns the reason a destination is blocked, including required enemy victories.
def travel_block_reason(destination):
    # Explains why a connected room cannot be entered yet (or None)
    # We explain which saved graph rule or missing victory prevents a move.
    if destination in get_accessible_rooms():
        return None

    # Explain the boss requirement when the player tries to enter the exit early.
    if destination == EXIT_ROOM_ID:
        return (f"{room_name(EXIT_ROOM_ID)} is sealed by Vharok's power. "
                f"Defeat Vharok in {room_name(ROOM_FOR_DIFFICULTY['Boss'])} first.")

    # We check the previous room's required victory quota before opening the next gate.
    index = ROOM_ORDER.index(destination) if destination in ROOM_ORDER else 0
    previous = ROOM_ORDER[index - 1] if index > 0 else None

    if previous:
        previous_difficulty = next(
            (tier for tier, rid in ROOM_FOR_DIFFICULTY.items() if rid == previous), None)
        required = 1 if previous_difficulty == "Boss" else 3
        # We count wins for this specific tier; extra weaker enemies cannot skip the next tier.
        current = (defeated_count_for_difficulty(previous_difficulty)
                   if previous_difficulty != "Boss" else
                   int(all_bosses_defeated(player.get("defeated_ids", []))))
        return (f"{room_name(destination)} is sealed. Defeat {required} "
                f"{previous_difficulty} guardian(s) in {room_name(previous)} "
                f"to open this passage ({min(current, required)}/{required}). "
                "Any extra enemies are optional after the requirement.")

    return f"{room_name(destination)} cannot be reached."


# Allows travel only through an existing passage to an unlocked room.
# Previously visited rooms can still be entered to fight optional enemies.
def travel_to_room():
    # Moves the player along a graph edge (passage) to a connected room
    # We check an actual passage and the room gate before changing the player's location.
    # We only follow a connection that exists in the stored graph, and we reject locked destinations.
    header("Travel to Connected Room")

    # Travel is blocked in the middle of a battle.
    # We check if a battle is already active before allowing this action.
    if current_enemy_id is not None:
        print("You cannot travel during a battle.")
        pause()
        return

    here = current_room_id()
    # We read neighbors from stored passages rather than assuming every room is connected.
    neighbors = get_neighbors(here)

    print(f"You are in: {room_name(here)}\n")

    if not neighbors:
        print("This room has no passages.")
        pause()
        return

    accessible = get_accessible_rooms()

    print_table(["Room", "Passage", "Access"],
                [[room_name(room_id), label,
                  "Open" if room_id in accessible else "SEALED"]
                 for room_id, label in neighbors], numbered=True)

    print("\n[0] Back")

    choice = input(f"\nWhere to? [0-{len(neighbors)}]: ").strip()

    if choice == "0":
        return

    if not choice.isdigit() or not 1 <= int(choice) <= len(neighbors):
        invalid_choice()
        pause()
        return

    destination, label = neighbors[int(choice) - 1]

    # Locked or invalid movement is rejected
    reason = travel_block_reason(destination)

    # Display the actual reason for a locked destination.
    if reason:
        print(f"\n{color(reason, 'red')}")
        pause()
        return

    if encounter_lineup:
        print("\nThe enemies waiting in your queue stay behind.")

    prior_queue = list(encounter_lineup)
    # We copy nested data so changing the new state will not also change our backup.
    prior_undo = copy.deepcopy(undo_stack)
    push_undo(f"Travel to {room_name(destination)}")
    # We empty the old lineup because the player is starting again after defeat.
    encounter_lineup.clear()
    # Update the current room only after all travel checks have passed.
    player["location"] = destination

    if not push_battle_action("Travel", f"Player traveled to {room_name(destination)}"
                                        f" via {label}."):
        player["location"] = here
        encounter_lineup[:] = prior_queue
        undo_stack[:] = prior_undo
        print("Travel was cancelled because progress could not be saved.")
        pause()
        return

    announce_room(destination)

    if destination == EXIT_ROOM_ID:
        return offer_exit()
    else:
        pause()


# Finds the saved passage label between two connected rooms.
def passage_name(a, b):
    # Resolve a live passage label rather than assuming a static default.
    # We look up the current admin-editable passage label between two rooms.
    # We read neighbors from stored passages rather than assuming every room is connected.
    return next((label for neighbor, label in get_neighbors(a)
                 if neighbor == b), "an unnamed passage")


# Builds room story text using actual room names to avoid mismatched notifications.
def contextual_story(lines):
    # If an admin customizes a room or passage, story references match it.
    # We make story text use the saved room and passage names whenever possible.
    substitutions = {
        "Rusted Grate": passage_name("ROOM-000", "ROOM-001"),
        "Rotting Sewers": room_name("ROOM-001"),
        "Crimson Gate": passage_name("ROOM-001", "ROOM-002"),
        "Bloodstone Hall": room_name("ROOM-002"),
        "Iron Drawbridge": passage_name("ROOM-002", "ROOM-003"),
        "War-Torn Catacombs": room_name("ROOM-003"),
        "Throne Gate": passage_name("ROOM-003", "ROOM-004"),
        "Sealed Exit Door": passage_name("ROOM-004", "ROOM-005"),
        "Throne of Ruin": room_name("ROOM-004"),
    }
    result = []
    for line in lines:
        for original, current in substitutions.items():
            line = line.replace(original, current)
        result.append(line)
    return result


# Shows the room story and current objective after arriving at a room.
def announce_room(room_id):
    # Story panel shown when a room is entered
    # We display the room's actual saved name and its story when the player arrives.
    tone = "red" if room_id == ROOM_FOR_DIFFICULTY["Boss"] else "cyan"
    story_panel(room_name(room_id), contextual_story(ROOM_STORY.get(room_id, [])), tone)

    enemies = [m for m in get_room_enemies(room_id) if not m["defeated"]]

    if enemies:
        print(f"Enemies remaining here: "
              f"{', '.join(m['name'] for m in enemies)}")
    elif get_room_enemies(room_id):
        print(f"{room_name(room_id)} is fully cleared.")


# Explains how to finish the game when the Last Gate becomes available.
def offer_exit():
    # Reaching the Last Room offers the final step
    # We offer the final escape choice after the boss has been defeated.
    print()

    if ask_yes_no("Step through the exit now? (Y/N): "):
        return escape_dungeon()
    else:
        print("\nThe Last Gate awaits. Choose 'Escape Dungeon' when ready.")
        pause()
    return False


# Completes the adventure only after the final boss and exit conditions are met.
def escape_dungeon():
    # Wins the game. Only possible in the Last Room after the Boss falls.
    # We verify the player reached the Last Gate and update the winning status.
    header("The Last Gate")

    # We check if a battle is already active before allowing this action.
    if current_enemy_id is not None:
        print("Finish the current battle first.")
        pause()
        return False

    if player["status"] == "Victorious":
        print("You have already crossed the Last Gate. You are free!")
        pause()
        return False

    if not all_bosses_defeated(player["defeated_ids"]):
        print("The Last Gate remains sealed by Vharok's power.")
        print(f"Defeat Vharok in {room_name(ROOM_FOR_DIFFICULTY['Boss'])} "
              "to open it.")
        pause()
        return False

    # We check the player's current location before deciding what is allowed.
    if current_room_id() != EXIT_ROOM_ID:
        print("The Last Gate is open, but you have not reached it yet.")
        print(f"Travel to {room_name(EXIT_ROOM_ID)} to leave the dungeon.")
        pause()
        return False

    begin_outcome_save()
    player["score"] += ESCAPE_SCORE_BONUS
    player["status"] = "Victorious"
    undo_stack.clear()

    push_battle_action(
        "Dungeon Escape",
        f"Player escaped the dungeon and earned {ESCAPE_SCORE_BONUS} score."
    )
    # We stop if the whole battle result could not be saved consistently.
    if not finish_outcome_save(record_battle_result(None, "Escaped Dungeon", 0, ESCAPE_SCORE_BONUS)):
        pause()
        return False

    story_panel("Beyond the Last Gate", contextual_story(ENDING_TEXT), "green")
    animate_banner("DREADVEIL CONQUERED - YOU ESCAPED!", "green")
    print(f"Escape bonus: +{ESCAPE_SCORE_BONUS} Score")
    print(f"Final Score: {player['score']}")
    print(f"Wins / Losses: {player['wins']} / {player['losses']}")
    print("Your victory has been saved. Press Enter to return to the main menu.")
    pause()
    return True


# ---------------------------------------------------------------
# SAVE GAME TRANSACTION
# ---------------------------------------------------------------

# Writes a readable snapshot of the current dungeon and player progress.
# The report is generated from live records, not a fixed example.
def write_game_snapshot(content_only=False):
    # We record the current player run, location, and results for later reports.
    # We handle reading, conversion, or save errors here instead of letting one problem crash the program.
    try:
        now = now_text()

        # We use a file context here so the file is properly closed after reading or writing.
        with io.StringIO() as game_file:
            game_file.write("DREADVEIL: THE LAST GATE - SAVED GAME\n")
            game_file.write(f"Saved At: {now}\n\n")

            game_file.write("PLAYER INFORMATION\n")

            for key, value in player.items():
                game_file.write(f"{key}: {value}\n")

            game_file.write(f"Current Room: {room_name(current_room_id())}\n")

            rank = get_player_rank_info()

            game_file.write("\nPROGRESSION\n")
            game_file.write(f"Rank: {rank['rank']}\n")
            game_file.write(
                f"Unlocked Difficulties: {get_unlocked_difficulties()}\n"
            )
            game_file.write(f"Next Goal: {rank['next_unlock']}\n")
            game_file.write(
                "Completed Levels: "
                + (", ".join(player["completed_levels"]) or "None") + "\n"
            )

            game_file.write("\nINVENTORY\n")

            for item_id, qty in player["inventory"].items():
                name = item_records.get(item_id, {}).get("name", item_id)
                game_file.write(f"{item_id} | {name} | {qty}\n")

            game_file.write("\nEQUIPMENT\n")

            for slot in EQUIPMENT_SLOTS:
                worn = equipped_piece(slot)
                game_file.write(
                    f"Worn {slot}: {worn['name']} | "
                    f"{describe_piece(worn)} | {worn['source']}\n"
                )

            for eid in player["owned_equipment"]:
                eq = equipment_records.get(eid)

                if eq:
                    game_file.write(
                        f"{eid} | {eq['name']} | {eq['tier']} {eq['slot']} | "
                        f"{equipment_state(eid)}\n"
                    )

            game_file.write("\nENEMY INFORMATION\n")

            # We check each related saved record so this result uses actual game data.
            for mob in mob_list:
                game_file.write(
                    f"{mob['id']} | {mob['name']} | "
                    f"HP: {mob['hp']}/{mob['max_hp']} | ATK: {mob['atk']} | "
                    f"Difficulty: {mob['type']} | Status: {enemy_status(mob)} | "
                    f"Gold: {mob['gold_reward']} | Score: {mob['score_reward']} | "
                    f"Room: {room_name(mob['room'])}\n"
                )

            game_file.write("\nDUNGEON ENCOUNTER QUEUE (FRONT TO REAR)\n")

            if encounter_lineup:
                # We check each related saved record so this result uses actual game data.
                for enemy_id in encounter_lineup:
                    mob = get_enemy_by_id(enemy_id)
                    game_file.write(
                        f"{mob['id']} | {mob['name']} | "
                        f"HP: {mob['hp']}/{mob['max_hp']}\n"
                    )
            else:
                game_file.write("NO ENEMIES WAITING\n")

            game_file.write("\nCURRENT BATTLE\n")

            if current_enemy_id:
                mob = get_current_enemy()
                game_file.write(f"{mob['id']} | {mob['name']}\n")
            else:
                game_file.write("NO ACTIVE BATTLE\n")

            game_file.write("\nUNDO STACK (TOP TO BOTTOM)\n")

            if undo_stack:
                # We check each related saved record so this result uses actual game data.
                for snap in reversed(undo_stack):
                    game_file.write(f"Before: {snap['label']}\n")
            else:
                game_file.write("EMPTY\n")

            game_file.write("\nDUNGEON MAP\n")

            for line in dungeon_map_lines(
                player["defeated_ids"], encounter_lineup
            ):
                game_file.write(line + "\n")

            text = game_file.getvalue()

        if content_only:
            return text
        return atomic_record_updates({GAME_RECORD_FILE: text})
    except OSError as error:
        print(f"Unable to save game snapshot: {error}")
        return False


# ---------------------------------------------------------------
# DUNGEON MENUS
# ---------------------------------------------------------------

# Brings a previously defeated or retreated player into a valid active state.
def restore_player_for_new_transaction():
    # Prepares the player when entering the dungeon
    # We prepare saved progress before opening a new player transaction.
    if player["hp"] <= 0:
        # We revive the player at the configured share of Max HP, with at least one HP.
        player["hp"] = max(1, player["max_hp"] * DEFEAT_REVIVE_PERCENT // 100)

    if player["status"] in ("Defeated", "Retreated", "Escaped") or (
            player["status"] == "In Battle" and current_enemy_id is None):
        player["status"] = "Active"

    save_current_player_account()


# Chooses the next objective from the player's actual location and quota progress.
def current_objective_text():
    # We explain the next useful goal based on the player's current difficulty.
    if player["status"] == "Victorious":
        return "Journey complete - you escaped Dreadveil."
    here = current_room_id()
    if here == EXIT_ROOM_ID:
        return f"Step through {room_name(EXIT_ROOM_ID)} to finish the adventure."
    enemies = get_room_enemies(here)
    if enemies:
        remaining = [m for m in enemies if not m["defeated"]]
        tier = next((name for name, rid in ROOM_FOR_DIFFICULTY.items()
                     if rid == here), None)
        if tier and tier != "Boss":
            # We count wins for this specific tier; extra weaker enemies cannot skip the next tier.
            defeated = defeated_count_for_difficulty(tier)
            if defeated >= 3:
                if remaining:
                    return (f"{tier} requirement COMPLETE (3/3). Next room open. "
                            f"{len(remaining)} optional enemy/enemies remain here; "
                            "you may return to fight them anytime.")
                if here in TREASURES and here not in player["treasures"]:
                    return "Room fully cleared. Open the chest or travel onward."
            else:
                return (f"Defeat {3 - defeated} more {tier} enemy/enemies "
                        f"to unlock the next room ({defeated}/3).")
        if tier == "Boss" and remaining:
            return "Defeat the Boss to open the Last Gate."
        if here in TREASURES and here not in player["treasures"]:
            return "Room fully cleared. Open the chest or travel onward."
    index = ROOM_ORDER.index(here)
    if index + 1 < len(ROOM_ORDER):
        destination = ROOM_ORDER[index + 1]
        return f"Travel to {room_name(destination)} when the passage is open."
    return "Explore the dungeon."


# Shows current HP, Gold, rank, room, and queue/stack details on the game screen.
def show_live_panel():
    # Live view of the player, the queue and the top of the stack
    # We display current HP, Gold, rank, room, and the next progression objective.
    mob = get_current_enemy()
    rank = get_player_rank_info()["rank"]
    player_bar = color(hp_bar(player["hp"], player["max_hp"]),
                       hp_color(player["hp"], player["max_hp"]))
    print(f"  ACCOUNT:   {player['name']} ({player['id']})  |  "
          f"RANK: {rank}  |  STATUS: {player['status']}")
    print(f"  HEALTH:    {player_bar}  {player['hp']}/{player['max_hp']} HP")
    print(f"  COMBAT:    ATK {total_atk()}  |  SPD +{sword_speed()}%  |  "
          f"DEF -{armor_defense()}  |  BLOCK {shield_block()}%")
    print(f"  REWARDS:   GOLD {player['gold']}  |  SCORE {player['score']}  |  "
          f"WINS {player['wins']} / LOSSES {player['losses']}")
    print(color("  " + "-" * 99, "cyan"))
    print(f"  LOCATION:  {room_name(current_room_id())}")
    print(textwrap.fill(current_objective_text(), width=101,
                        initial_indent="  OBJECTIVE: ",
                        subsequent_indent="            "))
    if mob:
        enemy_bar = color(hp_bar(mob["hp"], mob["max_hp"]),
                          hp_color(mob["hp"], mob["max_hp"]))
        enraged = " (ENRAGED)" if (mob["type"] == "Boss" and
                    mob["hp"] <= mob["max_hp"] // 2) else ""
        print(f"  OPPONENT:  {mob['name']}{enraged}")
        print(f"  ENEMY HP:  {enemy_bar}  {mob['hp']}/{mob['max_hp']} HP")
        effects = []
        if boost_turns_left:
            effects.append(f"Tonic +{boost_percent}% ({boost_turns_left})")
        if guard_bonus_ready:
            effects.append("Counter ready")
        if enemy_stunned_turns:
            effects.append(f"Paralyzed ({enemy_stunned_turns})")
        if challenge_used:
            effects.append("Challenge used")
        print(f"  EFFECTS:   {', '.join(effects) or 'None'}")
    print(color("  " + "-" * 99, "cyan"))
    front = get_enemy_by_id(encounter_lineup[0]) if encounter_lineup else None
    rear = get_enemy_by_id(encounter_lineup[-1]) if encounter_lineup else None
    print(f"  QUEUE:     {len(encounter_lineup)} waiting  |  "
          f"FRONT: {front['name'] if front else '-'}  |  "
          f"REAR: {rear['name'] if rear else '-'}")
    top = undo_stack[-1] if undo_stack else None
    latest = top["label"] if top else "EMPTY"
    latest = textwrap.shorten(latest, width=65, placeholder="...")
    print(f"  STACK:     {len(undo_stack)} undo actions  |  TOP: {latest}")
    print(f"  AUTOSAVE:  {session_save_mode}")


# Displays battle choices and repeats until the fight is finished or abandoned.
def battle_menu():
    # Actions available while fighting the enemy at the queue front
    # We show only the battle commands relevant to the ongoing fight.
    notice = ""

    # We keep going while this condition is still true.
    while current_enemy_id is not None:
        clear_screen()
        header(f"Battle: {get_current_enemy()['name']}")
        show_live_panel()

        potions = sum(
            item_quantity(i) for i, item in item_records.items()
            if item["effect"] == "heal"
        )
        question = ("used" if challenge_used else
                    "ready" if any(q["difficulty"] == get_current_enemy()["type"]
                                        for q in question_records) else "unavailable")

        print()
        print_menu_row("[1] Attack", "[2] Defend", f"[3] Potion (x{potions})",
                       width=32)
        print_menu_row("[4] Other Item", f"[5] Challenge ({question})",
                       "[6] Stats", width=32)
        print_menu_row("[7] View Queue", "[8] Player Action Stack",
                       f"[9] Undo Action ({len(undo_stack)} available)", width=32)
        print_menu_row("[10] Retreat", width=32)

        if notice:
            print(f"\n{notice}")
            notice = ""

        choice = input("\nEnter choice [1-10]: ").strip()

        if choice == "1":
            attack_current_enemy()
        elif choice == "2":
            defend_against_enemy()
        elif choice == "3":
            use_health_potion()
        elif choice == "4":
            use_item()
        elif choice == "5":
            answer_challenge_question()
        elif choice == "6":
            view_stats()
        elif choice == "7":
            display_encounter_lineup(pause_after=True)
        elif choice == "8":
            battle_log_menu()
        elif choice == "9":
            undo_latest_action()
        elif choice == "10":
            retreat_from_battle()
        else:
            notice = INVALID_CHOICE_TEXT


# Handles the player camp and exploration controls between battles.
def dungeon_menu():
    # Camp menu between battles. Battles open the battle menu.
    # We connect exploration, shopping, Queue, Stack, travel, and saving in one menu.
    global intro_shown

    restore_player_for_new_transaction()
    notice = ""

    # Show the opening scene once at the start of the adventure
    if not intro_shown and player["wins"] == 0 \
            and current_room_id() == ENTRANCE_ROOM_ID:
        story_panel("Dreadveil: The Last Gate", STORY_INTRO, "magenta")
        announce_room(ENTRANCE_ROOM_ID)
        pause()

    intro_shown = True

    # We check if a battle is already active before allowing this action.
    if current_enemy_id is not None:
        battle_menu()

    # We repeat this menu or action until the player gives a valid choice or leaves.
    while True:
        clear_screen()
        header("Dreadveil - Expedition Camp")
        show_live_panel()

        section("EXPLORE AND BATTLE")
        print_menu_row("[1] Start Battle", "[2] Add Enemy to Queue",
                       "[3] View Queue", width=32)
        print_menu_row("[4] View Next Enemy", "[5] Travel to Room",
                       "[6] Open Treasure Chest", width=32)
        section("CAMP")
        print_menu_row("[7] Dungeon Shop", "[8] Equipment",
                       f"[9] Rest ({REST_COST} Gold)", width=32)
        print_menu_row("[10] Inventory", "[11] Dungeon Map", width=32)

        section("RECORDS")
        print_menu_row("[12] Player Stats", "[13] Player Action Stack",
                       f"[14] Undo Action ({len(undo_stack)} available)", width=32)
        print_menu_row("[15] Save & Exit", "[16] Escape Dungeon",
                       width=32)

        if notice:
            print(f"\n{notice}")
            notice = ""

        choice = input("\nEnter choice [1-16]: ").strip()

        if choice == "1":
            start_battle_with_next_enemy()
            battle_menu()
        elif choice == "2":
            add_enemy_to_lineup()
        elif choice == "3":
            display_encounter_lineup(pause_after=True)
        elif choice == "4":
            view_next_enemy()
        elif choice == "5":
            if travel_to_room():
                return True
        elif choice == "6":
            open_treasure_chest()
        elif choice == "7":
            dungeon_shop()
        elif choice == "8":
            equipment_menu()
        elif choice == "9":
            rest_at_camp()
        elif choice == "10":
            view_inventory()
        elif choice == "11":
            dungeon_map_menu()
        elif choice == "12":
            view_stats()
        elif choice == "13":
            battle_log_menu()
        elif choice == "14":
            undo_latest_action()
        elif choice == "15":
            # Save the encounter queue with the current player progress
            # We cancel or reverse the change when the player record cannot be saved.
            if not save_current_player_account():
                print("\nSave failed. Check access to the game files before exiting.")
                pause()
                continue
            print("\nGame saved. Your Encounter Queue is saved. See you next time!")
            break
        elif choice == "16":
            if escape_dungeon():
                return True
        else:
            notice = INVALID_CHOICE_TEXT


# ---------------------------------------------------------------
# ADMIN: DASHBOARD
# ---------------------------------------------------------------

# Returns the profiles that belong to players rather than admin accounts.
def player_accounts():
    # Only player accounts (admins are excluded from game reports)
    # We filter out admins so game statistics only count real player profiles.
    return {
        username: data
        for username, data in account_records.items()
        if data["role"] == "Player"
    }


# Builds live admin totals using current accounts and enemy/room information.
def admin_dashboard():
    # We calculate record totals and game activity from the latest saved records.
    header("Administrator Dashboard")

    players = player_accounts()
    results = load_battle_results()

    section("Record Summary")
    print(f"Player Accounts   : {len(players)}")
    print(f"Admin Accounts    : {len(account_records) - len(players)}")

    tier_counts = ", ".join(
        f"{tier} {sum(1 for m in mob_list if m['type'] == tier)}"
        for tier in LEVEL_ORDER
    )
    print(f"Enemies           : {len(mob_list)} ({tier_counts})")
    print(f"Items             : {len(item_records)}")
    print(f"Equipment         : {len(equipment_records)}")
    print(f"Rooms / Passages  : {len(room_records)} / {len(room_connections)}")
    print(f"Challenge Quizzes : {len(question_records)}")

    section("Game Activity")
    print(f"Battles Recorded  : {len(results)}")
    print(f"Total Wins        : {sum(d['wins'] for d in players.values())}")
    print(f"Total Losses      : {sum(d['losses'] for d in players.values())}")
    print(f"Retreats          : "
          f"{sum(1 for r in results if r['result'] == 'Retreated')}")

    boss_beaten = [
        u for u, d in players.items() if all_bosses_defeated(d["defeated_ids"])
    ]
    victorious = [u for u, d in players.items() if d["status"] == "Victorious"]

    print(f"Boss Defeated By  : {', '.join(boss_beaten) or 'Nobody yet'}")
    print(f"Escaped Dungeon   : {', '.join(victorious) or 'Nobody yet'}")

    if players:
        top = max(players.items(), key=lambda pair: pair[1]["score"])
        print(f"Top Scorer        : {top[0]} ({top[1]['score']} score)")

    if results:
        last = results[-1]
        print(f"Latest Battle     : {last['date_time']} - {last['username']} "
              f"vs {last['enemy_name']} ({last['result']})")

    pause()


# ---------------------------------------------------------------
# ADMIN: PROFILING (FILE MAINTENANCE / CRUD)
# ---------------------------------------------------------------

# Runs the common Add, View, Search, Update, and Delete menu layout.
def crud_menu(title, actions, extra=None):
    # Shows the standard CRUD options for one type of record
    # We reuse the same Add, View, Search, Update, and Delete layout for admin records.
    extra = extra or []

    # We repeat this menu or action until the player gives a valid choice or leaves.
    while True:
        header(title)

        print("[1] Add Record")
        print("[2] View All Records")
        print("[3] Search Record")
        print("[4] Update Record")
        print("[5] Delete Record")

        for number, (label, _) in enumerate(extra, 6):
            print(f"[{number}] {label}")

        max_option = 5 + len(extra)
        print("\n[0] Back")

        choice = input(f"\nEnter choice [0-{max_option}]: ").strip()

        if choice in ("1", "2", "3", "4", "5"):
            actions[int(choice) - 1]()
        elif choice.isdigit() and 6 <= int(choice) <= max_option:
            extra[int(choice) - 6][1]()
        elif choice == "0":
            break
        else:
            invalid_choice()


# Groups room editing, passage connections, and map viewing for the admin.
def room_maintenance_menu():
    # We keep room editing, passage changes, and map viewing in one admin menu.
    # We repeat this menu or action until the player gives a valid choice or leaves.
    while True:
        header("Room and Passage Maintenance")
        print("[1] View All Rooms")
        print("[2] Search Room")
        print("[3] Update Room")
        print("[4] Add Passage (Graph Edge)")
        print("[5] Remove Passage")
        print("[6] View Dungeon Map")
        print("\n[0] Back")
        choice = input("\nEnter choice [0-6]: ").strip()
        if choice == "1":
            view_room_records()
        elif choice == "2":
            search_room_record()
        elif choice == "3":
            update_room_record()
        elif choice == "4":
            add_connection_record()
        elif choice == "5":
            remove_connection_record()
        elif choice == "6":
            admin_view_map()
        elif choice == "0":
            break
        else:
            invalid_choice()


# Opens the maintenance screens for the records used by game transactions.
def profiling_menu():
    # We let the admin choose which type of player, enemy, item, equipment, room, or question record to maintain.
    # We repeat this menu or action until the player gives a valid choice or leaves.
    while True:
        header("Profiling (File Maintenance)")

        print("[1] Player Account Maintenance")
        print("[2] Enemy Maintenance")
        print("[3] Item Maintenance")
        print("[4] Equipment Maintenance")
        print("[5] Room and Passage Maintenance")
        print("[6] Question and Challenge Maintenance")
        print("\n[0] Back")

        choice = input("\nEnter choice [0-6]: ").strip()

        if choice == "1":
            crud_menu("Player Account Maintenance", [
                add_account_record, view_account_records,
                search_account_record, update_account_record,
                delete_account_record
            ])
        elif choice == "2":
            crud_menu("Enemy Maintenance", [
                add_enemy_record, view_enemy_record_table,
                search_enemy_record, update_enemy_record, delete_enemy_record
            ])
        elif choice == "3":
            crud_menu("Item Maintenance", [
                add_item_record, view_item_records, search_item_record,
                update_item_record, delete_item_record
            ])
        elif choice == "4":
            crud_menu("Equipment Maintenance", [
                add_equipment_record, view_equipment_records,
                search_equipment_record, update_equipment_record,
                delete_equipment_record
            ])
        elif choice == "5":
            room_maintenance_menu()
        elif choice == "6":
            crud_menu("Question and Challenge Maintenance", [
                add_question_record, view_question_records,
                search_question_record, update_question_record,
                delete_question_record
            ])
        elif choice == "0":
            break
        else:
            invalid_choice()


# ----- Player accounts -----

# Shows account fields in a table so changes can be checked after editing.
def print_account_table(accounts):
    # accounts is a list of (username, data) pairs
    # We format player and admin account fields for the records screen.
    print_table(
        ["ID", "Username", "Role", "HP", "ATK", "Gold", "Score", "W/L",
         "Status"],
        [
            [data["id"], username, data["role"],
             f"{data['hp']}/{data['max_hp']}", data["atk"], data["gold"],
             data["score"], f"{data['wins']}/{data['losses']}",
             data["status"]]
            for username, data in accounts
        ],
        numbered=True
    )


# Looks up a player or admin account from the entered value.
def find_account(prompt="Enter Username, Player ID, or number: ", show_list=True):
    # We find a saved account by username or account ID.
    accounts = list(account_records.items())
    if show_list:
        print("EXISTING ACCOUNTS")
        print_account_table(accounts)
        print()
    key = input(prompt).strip()
    if not key:
        print("\nInput must not be blank.")
        return None
    if key.isdigit() and 1 <= int(key) <= len(accounts):
        return accounts[int(key)-1][0]
    for username, data in accounts:
        if username.lower() == key.lower() or data["id"].upper() == key.upper():
            return username
    print("\nPlayer record not found.")
    return None


# Uses the validated account-creation flow so new IDs stay unique.
def add_account_record():
    # We validate a new account before assigning a unique permanent ID.
    header("Add Account")

    username = ask_text("Username: ", banned="|,")

    if any(name.lower() == username.lower() for name in account_records):
        print("\nThat username already exists.")
        pause()
        return

    password = ask_text("Password: ")
    role = ask_option("Role:", ["Player", "Admin"], "Player")

    if not create_account_with_unique_id(username, password, role):
        print("Account could not be saved. No record was added.")
        pause()
        return

    print(f"\nAccount {username} ({account_records[username]['id']}) added successfully.")
    pause()


# Displays all account records currently saved in memory.
def view_account_records():
    # We display all saved profiles in a table.
    header("All Accounts")

    print_account_table(account_records.items())

    print(f"\nTotal records: {len(account_records)}")
    pause()


# Filters accounts by the entered name or identifying details.
def search_account_record():
    # We look for accounts matching the entered username or ID.
    header("Search Account")

    key = ask_text("Enter part of a username or Player ID: ").lower()
    matches = [
        (u, d) for u, d in account_records.items()
        if key in u.lower() or key in d["id"].lower()
    ]

    if not matches:
        print("\nPlayer record not found.")
    else:
        print_account_table(matches)

        rows = []

        for username, data in matches:
            items = "\n".join(
                f"{item_records.get(i, {}).get('name', i)} x{q}"
                for i, q in data["inventory"].items()
            )
            gear = "\n".join(
                equipment_records[e]["name"]
                for e in data["owned_equipment"] if e in equipment_records
            )
            rows.append([
                username,
                ", ".join(data["defeated_ids"]) or "None",
                items or "Empty",
                gear or "None",
                room_name(data["location"]),
                ", ".join(data["lineup"]) or "Empty"
            ])

        print()
        print_table(["Username", "Defeated", "Inventory", "Equipment",
                     "Room", "Queue"], rows)

    pause()


# Changes allowed account details while keeping the record ID and role valid.
def update_account_record():
    # We change allowed account fields and save them without losing other records.
    header("Update Account")

    username = find_account()

    if username is None:
        pause()
        return

    data = account_records[username]
    # We copy nested data so changing the new state will not also change our backup.
    prior_data = copy.deepcopy(data)

    if username == player.get("name") and data["role"] == "Admin":
        print("Note: you are editing your own admin account.")

    print("Press Enter to keep the current value.\n")

    data["password"] = ask_text(f"Password [{data['password']}]: ",
                                data["password"])

    if data["role"] == "Player":
        data["max_hp"] = ask_int(f"Max HP [{data['max_hp']}]: ", 1,
                                 default=data["max_hp"])
        data["hp"] = ask_int(f"HP [{min(data['hp'], data['max_hp'])}]: ",
                             0, data["max_hp"],
                             min(data["hp"], data["max_hp"]))
        data["atk"] = ask_int(f"Attack [{data['atk']}]: ", 1,
                              default=data["atk"])
        data["gold"] = ask_int(f"Gold [{data['gold']}]: ", 0,
                               default=data["gold"])
        data["score"] = ask_int(f"Score [{data['score']}]: ", 0,
                                default=data["score"])
        data["wins"] = ask_int(f"Wins [{data['wins']}]: ", 0,
                               default=data["wins"])
        data["losses"] = ask_int(f"Losses [{data['losses']}]: ", 0,
                                 default=data["losses"])
        data["status"] = ask_option("Status:", PLAYER_STATUSES,
                                    data["status"])

    # We keep the existing accounts if the save cannot finish.
    if not save_all_accounts():
        account_records[username] = prior_data
        print("Account was not updated because saving failed.")
        pause()
        return
    print(f"\nAccount {username} updated successfully.")
    pause()


# Deletes the selected account after confirmation, without reusing its ID.
def delete_account_record():
    # We check whether removing an account is allowed before deleting it.
    header("Delete Account")

    username = find_account()

    if username is None:
        pause()
        return

    if username == player.get("name"):
        print("\nYou cannot delete the account you are logged in with.")
        pause()
        return

    print_account_table([(username, account_records[username])])

    # We leave the current values unchanged if the player does not confirm.
    if not ask_yes_no("\nDelete this account permanently? (Y/N): "):
        print("\nNothing was deleted.")
        pause()
        return

    # We copy nested data so changing the new state will not also change our backup.
    prior_account = copy.deepcopy(account_records[username])
    prior_session = copy.deepcopy(session_archive["players"].get(username))
    del account_records[username]
    session_archive["players"].pop(username, None)
    updates = {
        ACCOUNT_FILE: save_all_accounts(content_only=True),
        # We turn the session archive into JSON while keeping its nested battle data.
        BATTLE_SESSION_FILE: json.dumps(session_archive, ensure_ascii=False, indent=2)
    }
    # We save the linked records as one group so partial changes do not get left behind.
    if not atomic_record_updates(updates):
        account_records[username] = prior_account
        if prior_session is not None:
            # We store each player's session separately so accounts do not share histories.
            session_archive["players"][username] = prior_session
        print("Account was not deleted because saving failed.")
        pause()
        return

    print(f"\nAccount {username} deleted.")
    pause()


# ----- Enemies -----
# Each enemy lives in the one room that belongs to its difficulty.

# Checks whether an enemy is still used in an active queue, battle, or undo snapshot.
def enemy_has_active_player_state(mob):
    """Avoid resetting enemy HP or difficulty during a saved encounter."""
    # We find out whether an enemy is involved in any active or saved player battle.
    enemy_id = mob["id"]
    if any(enemy_id in data.get("lineup", [])
           or enemy_id in data.get("wounds", {})
           for data in account_records.values()):
        return True
    # We check each related saved record so this result uses actual game data.
    for saved in session_archive.get("players", {}).values():
        if not isinstance(saved, dict):
            continue
        if saved.get("current_enemy_id") == enemy_id:
            return True
        if any(state.get("enemy_id") == enemy_id
               for state in saved.get("undo", [])
               if isinstance(state, dict)):
            return True
    return False


# Checks existing saved data before letting the admin remove an enemy.
def enemy_record_is_referenced(mob):
    """Protect a player's saved progress and immutable battle history."""
    # We check saved records that still refer to an enemy before removing it.
    enemy_id = mob["id"]
    if any(enemy_id in data.get("defeated_ids", [])
           or enemy_id in data.get("lineup", [])
           or enemy_id in data.get("wounds", {})
           for data in account_records.values()):
        return True
    if any(row[3] == enemy_id for row in read_record_rows(BATTLE_HISTORY_FILE)
           if len(row) >= 4):
        return True
    # We check each related saved record so this result uses actual game data.
    for saved in session_archive.get("players", {}).values():
        if not isinstance(saved, dict):
            continue
        if saved.get("current_enemy_id") == enemy_id:
            return True
        if any(state.get("enemy_id") == enemy_id
               or enemy_id in state.get("lineup", [])
               for state in saved.get("undo", [])
               if isinstance(state, dict)):
            return True
    return False


# Prevents enemy changes that would leave fewer than three required enemies in a tier.
def enemy_change_block_reason(mob, new_difficulty=None):
    """Reject deletes/moves that break rank unlocks or corrupt player saves."""
    # We stop an admin edit that could break the minimum enemies needed for progression.
    old_difficulty = mob["type"]
    minimum = MIN_ENEMIES_PER_DIFFICULTY[old_difficulty]
    remaining = sum(m["type"] == old_difficulty for m in mob_list) - 1
    if remaining < minimum:
        return (f"Cannot remove {mob['name']} from {old_difficulty}: "
                f"at least {minimum} {old_difficulty} enemies are required "
                "for dungeon progression.")
    if enemy_record_is_referenced(mob):
        return ("This enemy is already referenced by saved player progress, "
                "a battle record, or an active/undo session. "
                "Changing its difficulty or deleting it would alter history.")
    return None


# Formats enemy profiles for the admin view and search screens.
def print_enemy_table(mobs):
    # We display enemy stats, difficulty, rewards, and room in columns.
    print_table(
        ["ID", "Name", "Difficulty", "HP", "ATK", "Gold", "Score", "Room"],
        [
            [mob["id"], mob["name"], mob["type"], mob["max_hp"], mob["atk"],
             mob["gold_reward"], mob["score_reward"],
             f"{mob['room']} {room_name(mob['room'])}"]
            for mob in mobs
        ],
        numbered=True
    )


# Looks for the enemy ID entered by the admin.
def find_enemy_record(show_list=True):
    # We locate the enemy record that the admin selected.
    if show_list:
        print("EXISTING ENEMIES")
        print_enemy_table(mob_list)
        print()
    key = input("Enter Enemy ID or number: ").strip().upper()
    if key.isdigit() and 1 <= int(key) <= len(mob_list):
        return mob_list[int(key)-1]
    mob = get_enemy_by_id(key)
    # We stop here if the enemy ID does not match an existing enemy.
    if mob is None:
        print("\nEnemy record not found.")
    return mob


# Adds an enemy to the selected difficulty and its assigned room.
def add_enemy_record():
    # We create an enemy in the room for its difficulty using a new ID.
    header("Add Enemy")

    enemy_id = next_record_id("ENM", [m["id"] for m in mob_list])
    print(f"New Enemy ID: {enemy_id}")

    name = ask_text("Name: ")
    enemy_type = ask_option("Difficulty:", ["Weak", "Intermediate", "Strong"])
    max_hp = ask_int("Max HP: ", 1)
    atk = ask_int("Attack Power: ", 1)
    gold = ask_int("Gold Reward: ", 0)
    score = ask_int("Score Reward: ", 0)
    room = ROOM_FOR_DIFFICULTY[enemy_type]

    mob_list.append(make_enemy(enemy_id, name, enemy_type, max_hp, atk,
                               gold, score, room))
    # We keep the old enemy records if writing the update failed.
    if not save_enemies():
        mob_list.pop()
        print("The enemy could not be saved. No record was added.")
        pause()
        return

    print(f"\nEnemy {enemy_id} {name} added successfully.")
    print(f"It was placed in {room_name(room)} (the {enemy_type} room).")
    pause()


# Lists the available enemy profiles and their saved stats.
def view_enemy_record_table():
    # We show every current enemy profile, including optional extras.
    header("All Enemies")

    print_enemy_table(mob_list)

    print(f"\nTotal records: {len(mob_list)}")
    pause()


# Searches enemy IDs, names, and difficulties without changing records.
def search_enemy_record():
    # We search enemies by ID, name, or difficulty.
    header("Search Enemy")

    key = ask_text("Enter part of an Enemy ID, name or difficulty: ").lower()
    matches = [
        m for m in mob_list
        if key in m["id"].lower() or key in m["name"].lower()
        or key in m["type"].lower()
    ]

    if not matches:
        print("\nEnemy record not found.")

    if matches:
        print_enemy_table(matches)

    pause()


# Edits enemy stats only when a saved encounter is not depending on them.
def update_enemy_record():
    # We validate new enemy values and restore the original record if saving fails.
    header("Update Enemy")

    mob = find_enemy_record()

    # We stop here if the enemy ID does not match an existing enemy.
    if mob is None:
        pause()
        return

    # Changing an enemy mid-battle could invalidate someone's saved HP.
    if enemy_has_active_player_state(mob):
        print("This enemy is in a saved queue, battle or undo state. "
              "Finish the encounter before editing its stats or difficulty.")
        pause()
        return

    print("Press Enter to keep the current value.\n")
    # We copy nested data so changing the new state will not also change our backup.
    prior_mob = copy.deepcopy(mob)

    mob["name"] = ask_text(f"Name [{mob['name']}]: ", mob["name"])
    allowed = ["Boss"] if mob["id"] == "BS-001" else ["Weak", "Intermediate", "Strong"]
    chosen_type = ask_option("Difficulty:", allowed, mob["type"])
    if chosen_type != mob["type"]:
        reason = enemy_change_block_reason(mob, chosen_type)
        if reason:
            print(f"\n{reason}")
            pause()
            return
    mob["type"] = chosen_type
    mob["max_hp"] = ask_int(f"Max HP [{mob['max_hp']}]: ", 1,
                            default=mob["max_hp"])
    mob["atk"] = ask_int(f"Attack [{mob['atk']}]: ", 1, default=mob["atk"])
    mob["gold_reward"] = ask_int(f"Gold Reward [{mob['gold_reward']}]: ", 0,
                                 default=mob["gold_reward"])
    mob["score_reward"] = ask_int(f"Score Reward [{mob['score_reward']}]: ",
                                  0, default=mob["score_reward"])
    mob["room"] = ROOM_FOR_DIFFICULTY[mob["type"]]
    # We restore this enemy to its full HP so a future attempt starts fairly.
    mob["hp"] = mob["max_hp"]

    # We keep the old enemy records if writing the update failed.
    if not save_enemies():
        mob.clear()
        mob.update(prior_mob)
        print("Enemy was not updated because saving failed.")
        pause()
        return
    print(f"\nEnemy {mob['id']} updated successfully.")
    print(f"Room: {room_name(mob['room'])} (set by difficulty).")
    pause()


# Blocks deletion when a required enemy or saved reference still needs the record.
def delete_enemy_record():
    # We prevent deleting required or referenced enemies that would break current game data.
    header("Delete Enemy")

    mob = find_enemy_record()

    # We stop here if the enemy ID does not match an existing enemy.
    if mob is None:
        pause()
        return

    print_enemy_table([mob])

    reason = enemy_change_block_reason(mob)
    # An enemy cannot be deleted when that would break progression or existing saves.
    if reason:
        print(f"\n{reason}")
        pause()
        return

    # We leave the current values unchanged if the player does not confirm.
    if not ask_yes_no("\nDelete this enemy permanently? (Y/N): "):
        print("\nNothing was deleted.")
        pause()
        return

    # We copy nested data so changing the new state will not also change our backup.
    prior_accounts = copy.deepcopy(account_records)
    mob_index = mob_list.index(mob)
    mob_list.remove(mob)

    # Removes the enemy from every saved queue
    # We check each related saved record so this result uses actual game data.
    for data in account_records.values():
        data["lineup"] = [e for e in data["lineup"] if e != mob["id"]]

    updates = {
        ENEMY_FILE: save_enemies(content_only=True),
        ACCOUNT_FILE: save_all_accounts(content_only=True)
    }
    # We save the linked records as one group so partial changes do not get left behind.
    if not atomic_record_updates(updates):
        mob_list.insert(mob_index, mob)
        account_records.clear()
        account_records.update(prior_accounts)
        print("Enemy was not deleted because saving failed.")
        pause()
        return

    print(f"\nEnemy {mob['id']} deleted.")
    pause()


# ----- Items -----

# Prints consumable-item stats and purchase limits.
def print_item_table(items):
    # We format the saved item attributes into a readable table.
    print_table(
        ["ID", "Name", "Effect", "Power", "Price", "Carry", "Description"],
        [
            [item["id"], item["name"], item["effect"], item["power"],
             item["price"], item["max_carry"], describe_item_effect(item)]
            for item in items
        ],
        max_width=30,
        numbered=True
    )


# Selects the item that will be viewed or edited.
def find_item_record():
    # We locate the selected item by its record ID.
    print("EXISTING ITEMS")
    items = list(item_records.values())
    print_item_table(items)
    print()
    key = input("Enter Item ID or number: ").strip().upper()
    if key.isdigit() and 1 <= int(key) <= len(items):
        return items[int(key)-1]
    item = item_records.get(key)
    if item is None:
        print("\nItem record not found.")
    return item


# Shows the instruction for keeping a saved value during editing.
def keep_hint(value):
    # Shows the current value in update prompts, e.g. "Name [Potion]: "
    # We tell the admin that Enter keeps the existing field value.
    return f" [{value}]" if value is not None else ""


# Collects and validates the item effect, power, price, and carry limit.
def ask_item_fields(item=None):
    # We collect an item's name, effect, power, cost, and carrying limit.
    item = item or {}

    name = ask_text(f"Name{keep_hint(item.get('name'))}: ", item.get("name"))
    effect = ask_option("Effect:", list(ITEM_EFFECTS), item.get("effect"))

    hints = {
        "heal": "percent of Max HP healed",
        "boost": "percent extra damage",
        "stun": "enemy turns skipped",
        "damage": "average damage dealt"
    }
    power = ask_int(f"Power ({hints[effect]}){keep_hint(item.get('power'))}: ",
                    0, default=item.get("power"))
    price = ask_int(f"Price{keep_hint(item.get('price'))}: ",
                    0, default=item.get("price"))
    carry = ask_int(f"Max Carry{keep_hint(item.get('max_carry'))}: ",
                    1, default=item.get("max_carry"))
    description = ask_text(
        f"Description{keep_hint(item.get('description'))}: ",
        item.get("description")
    )

    return {"name": name, "effect": effect, "power": power, "price": price,
            "max_carry": carry, "description": description}


# Creates a usable item profile and saves it with a new item ID.
def add_item_record():
    # We create an item and save it after validating the new fields.
    header("Add Item")

    item_id = next_record_id("ITM", list(item_records))
    print(f"New Item ID: {item_id}")

    fields = ask_item_fields()
    item_records[item_id] = {"id": item_id, **fields}
    if not save_items():
        item_records.pop(item_id, None)
        print("The item could not be saved. No record was added.")
        pause()
        return

    print(f"\nItem {item_id} {fields['name']} added successfully.")
    pause()


# Lists the items that can be used by the game and shops.
def view_item_records():
    # We list all currently available consumable items.
    header("All Items")

    print_item_table(item_records.values())

    print(f"\nTotal records: {len(item_records)}")
    pause()


# Filters consumable records based on the entered keyword.
def search_item_record():
    # We find items by their ID, name, or effect.
    header("Search Item")

    key = ask_text("Enter part of an Item ID, name or effect: ").lower()
    matches = [
        i for i in item_records.values()
        if key in i["id"].lower() or key in i["name"].lower()
        or key in i["effect"]
    ]

    if not matches:
        print("\nItem record not found.")

    if matches:
        print_item_table(matches)

    pause()


# Edits an existing item without changing unrelated inventory entries.
def update_item_record():
    # We edit an item safely and keep the old values if the save fails.
    header("Update Item")

    item = find_item_record()

    if item is None:
        pause()
        return

    print("Press Enter to keep the current value.\n")
    # We copy nested data so changing the new state will not also change our backup.
    prior_item = copy.deepcopy(item)
    prior_accounts = copy.deepcopy(account_records)
    item.update(ask_item_fields(item))

    # Adjust stored item quantities to the allowed carrying limit
    # We check each related saved record so this result uses actual game data.
    for data in account_records.values():
        if data["inventory"].get(item["id"], 0) > item["max_carry"]:
            data["inventory"][item["id"]] = item["max_carry"]

    if not atomic_record_updates({
            ITEM_FILE: save_items(content_only=True),
            ACCOUNT_FILE: save_all_accounts(content_only=True)}):
        item.clear()
        item.update(prior_item)
        account_records.clear()
        account_records.update(prior_accounts)
        print("Item was not updated because saving failed.")
        pause()
        return

    print(f"\nItem {item['id']} updated successfully.")
    pause()


# Checks whether an item can be safely removed from the item catalog.
def delete_item_record():
    # We check whether a saved inventory still uses an item before removal.
    header("Delete Item")

    item = find_item_record()

    if item is None:
        pause()
        return

    print_item_table([item])

    # We leave the current values unchanged if the player does not confirm.
    if not ask_yes_no("\nDelete this item? It is removed from every "
                      "inventory. (Y/N): "):
        print("\nNothing was deleted.")
        pause()
        return

    # We copy nested data so changing the new state will not also change our backup.
    prior_accounts = copy.deepcopy(account_records)
    del item_records[item["id"]]

    # We check each related saved record so this result uses actual game data.
    for data in account_records.values():
        data["inventory"].pop(item["id"], None)

    if not atomic_record_updates({
            ITEM_FILE: save_items(content_only=True),
            ACCOUNT_FILE: save_all_accounts(content_only=True)}):
        item_records[item["id"]] = item
        account_records.clear()
        account_records.update(prior_accounts)
        print("Item was not deleted because saving failed.")
        pause()
        return

    print(f"\nItem {item['id']} deleted.")
    pause()


# ----- Equipment -----

# Formats equipment records for the admin list.
def print_equipment_table(items):
    # We show the equipment slot, tier, bonus, price, and speed.
    print_table(
        ["ID", "Name", "Slot", "Tier", "Effect", "Price", "Description"],
        [
            [e["id"], e["name"], e["slot"], e["tier"], describe_equipment(e),
             e["price"], e["description"]]
            for e in ordered_equipment_records(items)
        ],
        max_width=30,
        numbered=True
    )


# Gets the selected piece of equipment by ID.
def find_equipment_record():
    # We look up the equipment ID selected by the admin.
    print("EXISTING EQUIPMENT")
    items = ordered_equipment_records(equipment_records.values())
    print_equipment_table(items)
    print()
    key = input("Enter Equipment ID or number: ").strip().upper()
    if key.isdigit() and 1 <= int(key) <= len(items):
        return items[int(key)-1]
    eq = equipment_records.get(key)
    if eq is None:
        print("\nEquipment record not found.")
    return eq


# Asks for equipment stats while validating slot, tier, and price.
def ask_equipment_fields(eq=None):
    # We collect the required equipment attributes and validate them.
    eq = eq or {}

    name = ask_text(f"Name{keep_hint(eq.get('name'))}: ", eq.get("name"))
    slot = ask_option("Slot:", EQUIPMENT_SLOTS, eq.get("slot"))
    tier = ask_option("Tier:", list(TIER_UNLOCK_REQUIREMENT), eq.get("tier"))
    hint = {"sword": "attack bonus", "shield": "percent blocked (max 75)",
            "armor": "damage removed per hit"}[slot]
    bonus = ask_int(f"Bonus ({hint}){keep_hint(eq.get('bonus'))}: ", 1,
                    75 if slot == "shield" else None, eq.get("bonus"))
    speed = (ask_int(f"Speed bonus (%) {keep_hint(eq.get('speed', 0))}: ",
                     0, 25, eq.get('speed', 0)) if slot == "sword" else 0)
    price = ask_int(f"Price{keep_hint(eq.get('price'))}: ", 0,
                    default=eq.get("price"))
    description = ask_text(
        f"Description{keep_hint(eq.get('description'))}: ",
        eq.get("description")
    )

    return {"name": name, "slot": slot, "tier": tier, "bonus": bonus,
            "price": price, "description": description, "speed": speed}


# Creates a new equipment entry using the selected slot and tier.
def add_equipment_record():
    # We add a new piece of shop equipment with a unique ID.
    header("Add Equipment")

    eid = next_record_id("EQP", list(equipment_records))
    print(f"New Equipment ID: {eid}")

    fields = ask_equipment_fields()
    equipment_records[eid] = {"id": eid, **fields}
    if not save_equipment():
        equipment_records.pop(eid, None)
        print("Equipment could not be saved. No record was added.")
        pause()
        return

    print(f"\nEquipment {eid} {fields['name']} added successfully.")
    pause()


# Displays current equipment profiles from saved data.
def view_equipment_records():
    # We list the saved swords, shields, and armor choices.
    header("All Equipment")

    print_equipment_table(equipment_records.values())

    print(f"\nTotal records: {len(equipment_records)}")
    pause()


# Finds equipment by its ID, name, or assigned category.
def search_equipment_record():
    # We find matching gear by its ID, name, slot, or tier.
    header("Search Equipment")

    key = ask_text("Enter part of an ID, name, slot or tier: ").lower()
    matches = [
        e for e in equipment_records.values()
        if key in e["id"].lower() or key in e["name"].lower()
        or key in e["slot"] or key in e["tier"].lower()
    ]

    if not matches:
        print("\nEquipment record not found.")
    else:
        print_equipment_table(matches)

    pause()


# Edits equipment values while checking affected player ownership.
def update_equipment_record():
    # We save equipment edits while protecting currently owned references.
    header("Update Equipment")

    eq = find_equipment_record()

    if eq is None:
        pause()
        return

    print("Press Enter to keep the current value.\n")
    # We copy nested data so changing the new state will not also change our backup.
    prior_eq = copy.deepcopy(eq)
    prior_accounts = copy.deepcopy(account_records)
    old_slot = eq["slot"]
    eq.update(ask_equipment_fields(eq))

    # A changed slot would break equipped pieces, so they are unequipped
    if eq["slot"] != old_slot:
        # We check each related saved record so this result uses actual game data.
        for data in account_records.values():
            data["equipped"] = {
                s: e for s, e in data["equipped"].items() if e != eq["id"]
            }

    if not atomic_record_updates({
            EQUIPMENT_FILE: save_equipment(content_only=True),
            ACCOUNT_FILE: save_all_accounts(content_only=True)}):
        eq.clear()
        eq.update(prior_eq)
        account_records.clear()
        account_records.update(prior_accounts)
        print("Equipment was not updated because saving failed.")
        pause()
        return

    print(f"\nEquipment {eq['id']} updated successfully.")
    pause()


# Prevents deletion of equipment still needed by saved player records.
def delete_equipment_record():
    # We stop deletion when removing a piece would leave broken player equipment references.
    header("Delete Equipment")

    eq = find_equipment_record()

    if eq is None:
        pause()
        return

    print_equipment_table([eq])

    # We leave the current values unchanged if the player does not confirm.
    if not ask_yes_no("\nDelete this equipment? It is removed from every "
                      "player. (Y/N): "):
        print("\nNothing was deleted.")
        pause()
        return

    # We copy nested data so changing the new state will not also change our backup.
    prior_accounts = copy.deepcopy(account_records)
    del equipment_records[eq["id"]]

    # We check each related saved record so this result uses actual game data.
    for data in account_records.values():
        data["owned_equipment"] = [
            e for e in data["owned_equipment"] if e != eq["id"]
        ]
        data["equipped"] = {
            s: e for s, e in data["equipped"].items() if e != eq["id"]
        }

    if not atomic_record_updates({
            EQUIPMENT_FILE: save_equipment(content_only=True),
            ACCOUNT_FILE: save_all_accounts(content_only=True)}):
        equipment_records[eq["id"]] = eq
        account_records.clear()
        account_records.update(prior_accounts)
        print("Equipment was not deleted because saving failed.")
        pause()
        return

    print(f"\nEquipment {eq['id']} deleted.")
    pause()


# ----- Rooms and passages -----

# Displays each room vertex with its current saved name and description.
def print_room_table(rooms):
    # We format saved room names and descriptions for the admin.
    rows = []

    for room in rooms:
        enemies = "\n".join(m["name"] for m in get_room_enemies(room["id"]))
        # We read neighbors from stored passages rather than assuming every room is connected.
        links = "\n".join(n for n, _ in get_neighbors(room["id"]))
        rows.append([room["id"], room["name"], room["description"],
                     enemies or "None", links or "None"])

    print_table(["ID", "Name", "Description", "Enemies", "Links"],
                rows, numbered=True)


# Gets an existing room by ID before changing its details.
def find_room_record():
    # We locate the selected room by its fixed room ID.
    print("EXISTING ROOMS")
    print_room_table(room_records.values())
    print()
    room_id = choose_room()
    return room_records[room_id] if room_id else None




# Displays the six required room records.
def view_room_records():
    # We display all six dungeon rooms from their saved records.
    header("All Rooms")

    print_room_table(room_records.values())

    print(f"\nTotal records: {len(room_records)}")
    pause()


# Searches room IDs, names, and descriptions.
def search_room_record():
    # We search rooms by ID, name, or description.
    header("Search Room")

    key = ask_text("Enter part of a Room ID or name: ").lower()
    matches = [
        r for r in room_records.values()
        if key in r["id"].lower() or key in r["name"].lower()
    ]

    if not matches:
        print("\nRoom record not found.")

    if matches:
        print_room_table(matches)

    pause()


# Changes a room's text without changing its fixed ID or route position.
def update_room_record():
    # We let the admin rename or describe an existing room without changing its ID.
    header("Update Room")

    room = find_room_record()

    if room is None:
        pause()
        return

    print("Press Enter to keep the current value.\n")
    # We copy nested data so changing the new state will not also change our backup.
    prior_room = copy.deepcopy(room)
    room["name"] = ask_text(f"Name [{room['name']}]: ", room["name"])
    room["description"] = ask_text(
        f"Description{keep_hint(room['description'])}: ", room["description"]
    )

    if not save_rooms():
        room.clear()
        room.update(prior_room)
        print("Room was not updated because saving failed.")
        pause()
        return
    print(f"\nRoom {room['id']} updated successfully.")
    pause()




# Rejects invalid room IDs, duplicate passages, and disallowed graph links.
def validate_connection(room_a, room_b):
    # We make sure a proposed graph passage joins permitted existing rooms.
    if room_a not in room_records or room_b not in room_records:
        return "Room record not found."
    if room_a == room_b:
        return "A room cannot be connected to itself."
    if any({c["a"], c["b"]} == {room_a, room_b} for c in room_connections):
        return "These rooms are already connected."
    return None


# Creates a labeled passage only when the graph rules allow it.
def add_connection_record():
    # We add a valid passage between two rooms and save the updated graph.
    header("Add Passage")
    print_table(["Room ID", "Name"],
                [[room_id, room_name(room_id)] for room_id in room_records],
                numbered=True)
    print("\nFirst room:")
    room_a = choose_room()
    if room_a is None:
        pause()
        return
    print("Second room:")
    room_b = choose_room()
    if room_b is None:
        pause()
        return
    error = validate_connection(room_a, room_b)
    if error:
        print(f"\n{error}")
        pause()
        return
    label = ask_text("Passage name: ")
    room_connections.append({"a": room_a, "b": room_b, "label": label})
    if not save_connections():
        room_connections.pop()
        print("The passage could not be saved. No connection was added.")
        pause()
        return
    print(f"\nPassage added: {room_name(room_a)} <-> {room_name(room_b)} via {label}")
    pause()


# Checks connectivity and progression before deleting a passage.
def remove_connection_record():
    # We refuse passage removal when it would break required dungeon progression.
    header("Remove Passage")
    if not room_connections:
        print("There are no passages.")
        pause()
        return
    print_table(["From", "To", "Passage"],
                [[f"{link['a']} {room_name(link['a'])}",
                  f"{link['b']} {room_name(link['b'])}", link["label"]]
                 for link in room_connections], numbered=True)
    number = ask_int(f"\nPassage to remove [1-{len(room_connections)}]: ",
                     1, len(room_connections))
    link = room_connections[number - 1]
    # We leave the current values unchanged if the player does not confirm.
    if not ask_yes_no(f"Remove the {link['label']}? (Y/N): "):
        print("\nNothing was removed.")
        pause()
        return
    room_connections.pop(number - 1)
    unreachable = [r for r in room_records
                   # We visit rooms in DFS order using saved connections.
                   if r not in depth_first_traversal(ENTRANCE_ROOM_ID)]
    for target in ROOM_ORDER[1:]:
        allowed = set(ROOM_ORDER[:ROOM_ORDER.index(target) + 1])
        reached = {ENTRANCE_ROOM_ID}
        pending = [ENTRANCE_ROOM_ID]
        # We keep going while this condition is still true.
        while pending:
            room_id = pending.pop(0)
            # We read neighbors from stored passages rather than assuming every room is connected.
            for neighbor, _ in get_neighbors(room_id):
                if neighbor in allowed and neighbor not in reached:
                    reached.add(neighbor)
                    pending.append(neighbor)
        if target not in reached and target not in unreachable:
            unreachable.append(target)
    if unreachable:
        room_connections.insert(number - 1, link)
        print("\nCannot remove this passage. The dungeon must stay accessible in progression order.")
    else:
        if save_connections():
            print("\nPassage removed.")
        else:
            room_connections.insert(number - 1, link)
            print("Passage was not removed because saving failed.")
    pause()


# Shows the same graph information used by the player, with admin details.
def admin_view_map():
    # We let the admin inspect the same live graph the player uses.
    header("Dungeon Map (Graph)")

    for line in dungeon_drawing_lines([]):
        print(line)

    print()

    for line in dungeon_map_lines([]):
        print(line)

    pause()


# ----- Questions -----

# Formats the challenge question profiles.
def print_question_table(questions):
    # We format challenge questions and answer details for maintenance.
    rows = []
    for question in questions:
        choices = "\n".join(
            f"[{number}] {choice}" + (" *" if number == question["answer"] else "")
            for number, choice in enumerate(question["choices"], 1)
        )
        rows.append([question["id"], question["difficulty"],
                     question["question"], choices, f"+{question['bonus']}"])
    print_table(["ID", "Difficulty", "Question", "Choices (* = correct)",
                 "ATK Bonus"], rows, max_width=26, numbered=True)


# Locates an existing question by ID before an admin action.
def find_question_record():
    # We locate the saved question selected by the admin.
    print("EXISTING QUESTIONS")
    print_question_table(question_records)
    print()
    key = input("Enter Question ID or number: ").strip().upper()
    if key.isdigit() and 1 <= int(key) <= len(question_records):
        return question_records[int(key)-1]
    # We check each related saved record so this result uses actual game data.
    for question in question_records:
        if question["id"] == key:
            return question
    print("\nQuestion record not found.")
    return None


# Validates the question choices, answer number, enemy link, and bonus.
def ask_question_fields(question=None, difficulty=None):
    # We collect the question, choices, answer number, and bonus value.
    question = question or {"choices": []}
    old_choices = question["choices"] + [None] * (4 - len(question["choices"]))
    level = (difficulty if difficulty is not None else
             ask_option("Difficulty:", ["Weak", "Intermediate", "Strong"],
                        question.get("difficulty")))
    prompt = ask_text(f"Question{keep_hint(question.get('question'))}: ",
                      question.get("question"))
    choices = [ask_text(f"Choice {n}{keep_hint(old)}: ", old, "|;")
               for n, old in enumerate(old_choices[:4], 1)]
    answer = ask_int(
        f"Correct choice number [1-4]{keep_hint(question.get('answer'))}: ",
        1, 4, question.get("answer")
    )
    bonus = ask_int(f"Bonus damage{keep_hint(question.get('bonus'))}: ",
                    0, default=question.get("bonus"))
    return {"question": prompt, "choices": choices, "answer": answer,
            "bonus": bonus, "difficulty": level}


# Adds a challenge question associated with an existing enemy.
def add_question_record():
    # We create a new challenge question after checking its enemy assignment.
    header("Add Question")
    qid = next_record_id("QST", [q["id"] for q in question_records])
    print(f"New Question ID: {qid}")
    question_records.append({"id": qid, **ask_question_fields()})
    if not save_questions():
        question_records.pop()
        print("The question could not be saved. No record was added.")
        pause()
        return
    print(f"\nQuestion {qid} added successfully.")
    pause()


# Lists all challenge questions available in the game.
def view_question_records():
    # We display all quiz challenges for review.
    header("All Questions")

    print_question_table(question_records)

    print(f"\nTotal records: {len(question_records)}")
    pause()


# Searches questions by ID or question text.
def search_question_record():
    # We find question records by their IDs or content.
    header("Search Question")

    key = ask_text("Enter part of a Question ID or text: ").lower()
    matches = [
        q for q in question_records
        if key in q["id"].lower() or key in q["question"].lower()
    ]

    if not matches:
        print("\nQuestion record not found.")

    if matches:
        print_question_table(matches)

    pause()


# Updates a saved question while checking its enemy and correct answer.
def update_question_record():
    # We update a question and restore it if writing the file fails.
    header("Update Question")

    question = find_question_record()

    if question is None:
        pause()
        return

    if question["id"] == BOSS_CHALLENGE_ID:
        print("The final Boss question is reserved and cannot be changed.")
        pause()
        return

    print("Press Enter to keep the current value.\n")
    values = ask_question_fields(question)
    if (values["difficulty"] != question["difficulty"]
            and sum(q["difficulty"] == question["difficulty"]
                    for q in question_records) <= 1):
        print("At least one question must remain for each difficulty.")
        pause()
        return
    earlier = dict(question)
    question.update(values)
    if not save_questions():
        question.clear()
        question.update(earlier)
        print("The question was not updated because saving failed.")
        pause()
        return

    print(f"\nQuestion {question['id']} updated successfully.")
    pause()


# Checks whether the selected question can be removed safely.
def delete_question_record():
    # We check dependencies before removing a question used in combat.
    header("Delete Question")
    question = find_question_record()
    if question is None:
        pause()
        return
    if question["id"] == BOSS_CHALLENGE_ID:
        print("The final Boss question is required and cannot be deleted.")
        pause()
        return
    if sum(q["difficulty"] == question["difficulty"] for q in question_records) <= 1:
        print("At least one question must remain for each difficulty.")
        pause()
        return
    print_question_table([question])
    # We leave the current values unchanged if the player does not confirm.
    if not ask_yes_no("\nDelete this question? (Y/N): "):
        print("\nNothing was deleted.")
        pause()
        return
    position = question_records.index(question)
    question_records.remove(question)
    if not save_questions():
        question_records.insert(position, question)
        print("The question was not deleted because saving failed.")
        pause()
        return
    print(f"\nQuestion {question['id']} deleted.")
    pause()


# ---------------------------------------------------------------
# ADMIN: TRANSACTIONS (GAME SETUP AND MANAGEMENT)
# ---------------------------------------------------------------

# Lets the admin select a saved player for transactions and inspection.
def choose_player_account():
    # We select a valid player profile for an admin transaction.
    accounts = list(player_accounts().items())
    print_account_table(accounts)
    key = input("\nEnter Username, Player ID, or No.: ").strip()
    if key.isdigit() and 1 <= int(key) <= len(accounts):
        return accounts[int(key) - 1][0]
    for username, data in accounts:
        if key.lower() == username.lower() or key.upper() == data["id"].upper():
            return username
    print("\nPlayer record not found.")
    return None


# Shows the player's progress using real wins, rank, and completed levels.
def view_player_progress():
    # We show a selected player's saved rank, enemies, Gold, and unlocked rooms.
    header("View Player Progress")

    username = choose_player_account()

    if username is None:
        pause()
        return

    data = account_records[username]
    # We check the tier-specific victory counts to decide the currently unlocked difficulty.
    rank = get_rank_info(data["wins"], data["defeated_ids"])

    print()
    print_account_table([(username, data)])
    print(f"Rank            : {rank['rank']} ({rank['next_unlock']})")
    print(f"Location        : {room_name(data['location'])}")
    print(f"Completed Levels: {', '.join(data['completed_levels']) or 'None'}")
    print(f"Defeated Enemies: {len(data['defeated_ids'])}/{len(mob_list)}")
    print(f"Saved Queue     : {', '.join(data['lineup']) or 'Empty'}")
    print("Equipment       : " + (", ".join(
        f"{equipment_records[e]['name']}"
        f"{' (worn)' if data['equipped'].get(equipment_records[e]['slot']) == e else ''}"
        for e in data["owned_equipment"] if e in equipment_records
    ) or "None"))
    print(f"Treasure Opened : {len(data['treasures'])}/{len(TREASURES)}")
    print(f"Boss Defeated   : "
          f"{'Yes' if all_bosses_defeated(data['defeated_ids']) else 'No'}")

    section("Dungeon Map For This Player")

    for line in dungeon_map_lines(data["defeated_ids"], data["lineup"]):
        print(line)

    pause()


# Resets the selected player's game progress after confirmation.
def reset_player_game_data():
    # We reset chosen game progress while keeping the account itself.
    header("Reset Player Game Data")

    username = choose_player_account()

    if username is None:
        pause()
        return

    # We leave the current values unchanged if the player does not confirm.
    if not ask_yes_no(f"\nReset all progress of {username}? (Y/N): "):
        print("\nNothing was changed.")
        pause()
        return

    data = account_records[username]
    # We copy nested data so changing the new state will not also change our backup.
    prior_account = copy.deepcopy(data)
    prior_session = copy.deepcopy(session_archive["players"].get(username))
    fresh = new_account_data(data["id"], data["password"])
    account_records[username] = fresh
    session_archive["players"].pop(username, None)
    if not atomic_record_updates({
            ACCOUNT_FILE: save_all_accounts(content_only=True),
            # We turn the session archive into JSON while keeping its nested battle data.
            BATTLE_SESSION_FILE: json.dumps(session_archive, ensure_ascii=False, indent=2)}):
        account_records[username] = prior_account
        if prior_session is not None:
            # We store each player's session separately so accounts do not share histories.
            session_archive["players"][username] = prior_session
        print("Player progress was not reset because saving failed.")
        pause()
        return

    print(f"\n{username} has been reset to the starting stats.")
    pause()


# Updates the starter supplies for the chosen player account.
def assign_starting_items():
    # We give eligible starting supplies to the chosen player and save the updated inventory.
    header("Assign Items to Player")

    username = choose_player_account()

    if username is None:
        pause()
        return

    data = account_records[username]
    items = list(item_records.values())

    print()

    print_table(["Item ID", "Name", "Owned/Max"],
                [[item["id"], item["name"],
                  f"{data['inventory'].get(item['id'], 0)}/{item['max_carry']}"]
                 for item in items], numbered=True)

    number = ask_int(f"Choose item [1-{len(items)}]: ", 1, len(items))
    item = items[number - 1]

    qty = ask_int(f"New quantity for {item['name']} "
                  f"[0-{item['max_carry']}]: ", 0, item["max_carry"])

    # We copy nested data so changing the new state will not also change our backup.
    prior_inventory = copy.deepcopy(data["inventory"])
    if qty > 0:
        data["inventory"][item["id"]] = qty
    else:
        data["inventory"].pop(item["id"], None)

    # We keep the existing accounts if the save cannot finish.
    if not save_all_accounts():
        data["inventory"] = prior_inventory
        print("Items were not assigned because saving failed.")
        pause()
        return
    print(f"\n{username} now has {qty} {item['name']}.")
    pause()


# Changes enemy difficulty only if the new record still follows dungeon rules.
def set_enemy_difficulty():
    # We update an enemy's difficulty only when the change will not break progression or saved fights.
    header("Set Enemy Difficulty")

    print_enemy_table(mob_list)

    print()
    mob = find_enemy_record(show_list=False)

    # We stop here if the enemy ID does not match an existing enemy.
    if mob is None:
        pause()
        return

    if enemy_has_active_player_state(mob):
        print("This enemy is in a saved queue, battle or undo state. "
              "Finish the encounter before changing its difficulty.")
        pause()
        return

    # We copy nested data so changing the new state will not also change our backup.
    prior_mob = copy.deepcopy(mob)
    allowed = ["Boss"] if mob["id"] == "BS-001" else ["Weak", "Intermediate", "Strong"]
    chosen_type = ask_option("New difficulty:", allowed, mob["type"])
    if chosen_type != mob["type"]:
        reason = enemy_change_block_reason(mob, chosen_type)
        if reason:
            print(f"\n{reason}")
            pause()
            return
    mob["type"] = chosen_type
    mob["room"] = ROOM_FOR_DIFFICULTY[mob["type"]]
    percent = ask_int("Scale HP and Attack by percent (100 = unchanged): ",
                      10, 500, 100)

    mob["max_hp"] = max(1, mob["max_hp"] * percent // 100)
    mob["atk"] = max(1, mob["atk"] * percent // 100)
    # We restore this enemy to its full HP so a future attempt starts fairly.
    mob["hp"] = mob["max_hp"]

    # We keep the old enemy records if writing the update failed.
    if not save_enemies():
        mob.clear()
        mob.update(prior_mob)
        print("Enemy difficulty was not updated because saving failed.")
        pause()
        return

    print("\nEnemy updated (it moved to the room of its new difficulty):")
    print_enemy_table([mob])
    pause()


# Turns saved battle history entries into readable report rows.
def battle_history_lines(username=None):
    # We format battle results so administrators can review what happened in each encounter.
    results = load_battle_results()

    if username:
        # A recreated username has a different permanent ID and must not
        # inherit the former account's battle history.
        if username in account_records:
            account_id = account_records[username]["id"]
            results = [r for r in results if r["player_id"] == account_id]
        else:
            results = [r for r in results if r["username"] == username]

    if not results:
        return ["No battle results have been recorded."]

    lines = table_lines(
        ["Date/Time", "Player", "Enemy", "Result", "Turns", "Gold", "Score"],
        [
            [r["date_time"], r["username"], r["enemy_name"], r["result"],
             r["turns"], r["gold"], r["score"]]
            for r in results
        ]
    )

    lines.append(f"\nTotal battles: {len(results)}")
    return lines


# Displays fight results recorded for the players.
def view_battle_history():
    # We display completed battle records from the saved history file.
    header("View Battle History")

    username = input("Filter by username (Enter for all): ").strip()

    print()

    # We check each related saved record so this result uses actual game data.
    for line in battle_history_lines(username or None):
        print(line)

    pause()


# Reads the permanent battle action log rather than only the current undo stack.
def read_full_activity_log(username=None):
    # We load the full activity text with its permanent action IDs.
    owners = {data["id"]: name for name, data in account_records.items()}
    entries = []
    for parts in read_record_rows(BATTLE_LOG_FILE):
        if len(parts) != 6 or not parts[0].startswith("ACT-"):
            continue
        if not parts[3].startswith("Player "):
            continue
        player_id = parts[3][7:]
        owner = owners.get(player_id, player_id)
        if username and owner != username:
            continue
        entries.append({"id": parts[0], "time": parts[1],
                        "action": parts[2], "username": owner,
                        "enemy": parts[4].removeprefix("Enemy "),
                        "details": parts[5]})
    return entries


# Lets the admin inspect detailed actions from the saved activity records.
def admin_view_full_activity_history():
    # We let admins inspect recorded player actions without editing them.
    header("Complete Player Activity History")
    print("[1] All Players")
    print("[2] Select Player")
    print("[0] Back")
    choice = input("\nEnter choice [0-2]: ").strip()
    if choice == "0":
        return
    if choice == "1":
        selected = None
    elif choice == "2":
        selected = choose_player_account()
        if selected is None:
            pause()
            return
    else:
        invalid_choice()
        return
    entries = read_full_activity_log(selected)
    offset = 0
    # We repeat this menu or action until the player gives a valid choice or leaves.
    while True:
        header("Complete Player Activity History")
        print(f"Player: {selected or 'All'} | Total recorded events: {len(entries)}")
        if not entries:
            print("No recorded activities.")
            pause()
            return
        batch = list(reversed(entries))[offset:offset + 10]
        print_table(["Action ID", "Time", "Player", "Activity", "Details"],
                    [[entry['id'], entry['time'], entry['username'],
                      entry['action'], entry['details']] for entry in batch],
                    max_width=50, numbered=True)
        print(f"Showing {offset + 1}-{offset + len(batch)} of {len(entries)}")
        older = offset + 10 < len(entries)
        newer = offset > 0
        if older:
            print("[1] Older Events")
        if newer:
            print("[2] Newer Events")
        print("[0] Back")
        choice = input("\nEnter choice: ").strip()
        if choice == "0":
            return
        if choice == "1" and older:
            offset += 10
        elif choice == "2" and newer:
            offset = max(0, offset - 10)
        else:
            invalid_choice()


# Uses the stored undo states to restore available reversible player actions.
def admin_undo_all_pending():
    # We safely apply all currently eligible Undo snapshots for a selected player.
    # We only restore the snapshots that are still safe to undo for the selected player.
    header("Undo All Available Player Actions")
    username = choose_player_account()
    if username is None:
        pause()
        return False
    saved = session_archive['players'].get(username, {})
    states = saved.get('undo', [])
    record = account_records[username]
    if not states:
        print("Undo Stack is EMPTY. There are no actions to restore.")
        pause()
        return False
    active_enemy = saved.get('current_enemy_id')
    in_battle = record['status'] == 'In Battle'
    if in_battle:
        mob = get_enemy_by_id(active_enemy) if active_enemy else None
        # We stop here if the enemy ID does not match an existing enemy.
        if (mob is None or active_enemy in record['defeated_ids']
                or not record['lineup'] or record['lineup'][0] != active_enemy
                or mob['room'] != record['location']
                or any(s.get('enemy_id') != active_enemy for s in states)):
            print("The current battle cannot be restored safely. Nothing changed.")
            pause()
            return False
    elif active_enemy or any(s.get('enemy_id') is not None for s in states):
        print("These Undo states belong to a different battle. Nothing changed.")
        pause()
        return False
    oldest = states[0]
    target_room = oldest.get('location', record['location'])
    target_queue = list(oldest.get('lineup', []))
    if (in_battle and
            (oldest.get('enemy_hp') is None
             or not 0 < oldest['enemy_hp'] <= mob['max_hp']
             or len(oldest.get('effects', [])) != 7
             or oldest.get('status') != 'In Battle')):
        print("Saved battle data is incomplete. Nothing changed.")
        pause()
        return False
    if target_room not in room_records or any(
            get_enemy_by_id(eid) is None
            or get_enemy_by_id(eid)['room'] != target_room
            or eid in record['defeated_ids']
            for eid in target_queue):
        print("Old saved location or Queue is no longer valid. Nothing changed.")
        pause()
        return False
    print(f"Player: {username} ({record['id']})")
    print(f"Actions to restore: {len(states)}")
    print(f"Gold: {record['gold']} -> {oldest['gold']}")
    print(f"HP: {record['hp']} -> {oldest['hp']}")
    print(f"Location: {room_name(record['location'])} -> {room_name(target_room)}")
    if in_battle:
        print(f"Enemy HP will return to {oldest['enemy_hp']}/{mob['max_hp']}.")
    print("Completed battles and permanent rewards are NOT part of this Undo.")
    # We leave the current values unchanged if the player does not confirm.
    if not ask_yes_no("Undo all available actions? (Y/N): "):
        print("Nothing was changed.")
        pause()
        return False
    import copy
    # We copy nested data so changing the new state will not also change our backup.
    previous_record = copy.deepcopy(record)
    previous_session = copy.deepcopy(saved)
    for key in ('hp', 'gold', 'score', 'inventory', 'owned_equipment',
                'equipped', 'status'):
        if key in oldest:
            record[key] = copy.deepcopy(oldest[key])
    record['location'] = target_room
    record['lineup'] = target_queue
    if in_battle:
        record.setdefault('wounds', {})[active_enemy] = oldest['enemy_hp']
        saved['effects'] = list(oldest['effects'])
    saved['undo'] = []
    session_archive['next_action_number'] += 1
    act_id = f"ACT-{session_archive['next_action_number'] - 1:06d}"
    event = {"action_id": act_id, "date_time": now_text(),
             "action_type": "Admin Undo", "player_id": record['id'],
             "enemy_id": "N/A",
             "description": (f"Admin restored {len(states)} available action(s) "
                             f"for {username}."),
             "player_hp_before": previous_record['hp'],
             "player_hp_after": record['hp'], "enemy_hp_before": None,
             "enemy_hp_after": None}
    saved.setdefault('history', []).append(event)
    # We handle reading, conversion, or save errors here instead of letting one problem crash the program.
    try:
        prior_log = Path(BATTLE_LOG_FILE).read_text(encoding="utf-8") if Path(BATTLE_LOG_FILE).exists() else ""
    except OSError as error:
        account_records[username] = previous_record
        session_archive['players'][username] = previous_session
        session_archive['next_action_number'] -= 1
        print(f"Unable to read activity log: {error}")
        pause()
        return False
    log_entry = (f"{event['action_id']} | {event['date_time']} | "
                 f"{event['action_type']} | Player {event['player_id']} | "
                 f"Enemy {event['enemy_id']} | {event['description']}\n"
                 f"    Player HP: {event['player_hp_before']} -> "
                 f"{event['player_hp_after']} | "
                 f"Enemy HP: None -> None\n")
    updates = {
        ACCOUNT_FILE: save_all_accounts(content_only=True),
        # We turn the session archive into JSON while keeping its nested battle data.
        BATTLE_SESSION_FILE: json.dumps(session_archive, ensure_ascii=False, indent=2),
        BATTLE_LOG_FILE: prior_log + log_entry
    }
    # We save the linked records as one group so partial changes do not get left behind.
    if not atomic_record_updates(updates):
        account_records[username] = previous_record
        session_archive['players'][username] = previous_session
        session_archive['next_action_number'] -= 1
        print("Undo could not be saved. No record was changed.")
        pause()
        return False
    print(f"Restored {len(states)} saved action(s). Undo Stack is now EMPTY.")
    print("Player account and session saved. The audit history is retained.")
    pause()
    return True


# Groups admin game-management actions that use the saved player records.
def game_setup_menu():
    # We group the admin's player progress and battle-management transactions.
    # We repeat this menu or action until the player gives a valid choice or leaves.
    while True:
        header("Transactions (Game Setup and Management)")
        print("[1] View Player Progress")
        print("[2] Reset Player Game Data")
        print("[3] Assign Starting Items")
        print("[4] Set Enemy Difficulty")
        print("[5] View Battle History")
        print("[6] View Complete Activity History")
        print("[7] Undo All Available Player Actions")
        print("\n[0] Back")
        choice = input("\nEnter choice [0-7]: ").strip()
        if choice == "1":
            view_player_progress()
        elif choice == "2":
            reset_player_game_data()
        elif choice == "3":
            assign_starting_items()
        elif choice == "4":
            set_enemy_difficulty()
        elif choice == "5":
            view_battle_history()
        elif choice == "6":
            admin_view_full_activity_history()
        elif choice == "7":
            admin_undo_all_pending()
        elif choice == "0":
            break
        else:
            invalid_choice()


# ---------------------------------------------------------------
# ADMIN: REPORT GENERATION
# Every report is built from the live records, displayed, and can be
# exported to a text file inside the reports folder.
# ---------------------------------------------------------------

# Generates current player statistics from account records.
def report_player_statistics():
    # We build the player statistics report from current saved accounts.
    lines = table_lines(
        ["ID", "Username", "HP", "ATK", "Gold", "Score", "Rank", "Room",
         "Status"],
        [
            [d["id"], username, f"{d['hp']}/{d['max_hp']}", d["atk"],
             # We check the tier-specific victory counts to decide the currently unlocked difficulty.
             d["gold"], d["score"], get_rank_info(d["wins"], d["defeated_ids"])["rank"],
             room_name(d["location"]), d["status"]]
            for username, d in player_accounts().items()
        ]
    )

    lines.append(f"\nTotal players: {len(player_accounts())}")
    return lines


# Counts victories, losses, and retreats using the saved battle records.
def report_wins_losses():
    """Count every recorded battle attempt, including retreats.

    This is an all-time report from battle history. Current account W/L
    counters may differ after an admin explicitly resets player progress.
    """
    # Read the saved battle history so reloads do not reset report totals.
    # We calculate victory, defeat, and retreat totals from actual battle results.
    records = load_battle_results()
    counts = {}
    for entry in records:
        outcome = entry["result"]
        # Only completed battle outcomes count in this report.
        if outcome not in ("Victory", "Defeat", "Retreated"):
            continue  # Dungeon exit is not a battle attempt.
        stats = counts.setdefault(entry["player_id"],
                                  {"Victory": 0, "Defeat": 0, "Retreated": 0})
        stats[outcome] += 1

    rows = []
    total_w = total_l = total_r = 0
    for username, data in player_accounts().items():
        result = counts.get(data["id"], {})
        wins = result.get("Victory", 0)
        losses = result.get("Defeat", 0)
        retreats = result.get("Retreated", 0)
        battles = wins + losses + retreats
        rate = f"{wins * 100 / battles:.0f}%" if battles else "-"
        rows.append([username, wins, losses, retreats, battles, rate])
        total_w += wins
        total_l += losses
        total_r += retreats

    lines = ["RECORDED BATTLE RESULTS FOR CURRENT ACCOUNTS "
             "(includes retreats; excludes dungeon exits)."]
    lines += table_lines(
        ["Username", "Wins", "Losses", "Retreats", "Battles", "Win Rate"], rows
    )
    lines.append(f"\nTotal wins: {total_w} | Total losses: {total_l} | "
                 f"Total retreats: {total_r} | "
                 f"Total battles: {total_w + total_l + total_r}")
    lines.append("Note: Historical results remain after a player-progress reset; "
                 "the Player Statistics Report shows current progress.")
    return lines


# Counts defeated enemies from each player's recorded progress.
def report_enemies_defeated():
    # We list defeated enemies using recorded player progress.
    players = player_accounts()
    rows = []

    # We check each related saved record so this result uses actual game data.
    for mob in mob_list:
        who = [u for u, d in players.items() if mob["id"] in d["defeated_ids"]]
        rows.append([mob["id"], mob["name"], mob["type"], len(who),
                     ", ".join(who) or "none"])

    lines = table_lines(
        ["ID", "Enemy", "Difficulty", "Times", "Defeated By"], rows,
        max_width=30
    )
    lines.append("")
    lines += table_lines(
        ["Username", "Enemies Defeated"],
        [
            [username, f"{len(d['defeated_ids'])}/{len(mob_list)}"]
            for username, d in players.items()
        ]
    )
    return lines


# Sorts players by their actual scores to build the ranking.
def report_score_ranking():
    # We sort player scores to find the current ranking.
    ranked = sorted(player_accounts().items(),
                    key=lambda pair: pair[1]["score"], reverse=True)

    return table_lines(
        ["Place", "Username", "Score", "Wins", "Rank"],
        [
            [place, username, d["score"], d["wins"],
             # We check the tier-specific victory counts to decide the currently unlocked difficulty.
             get_rank_info(d["wins"], d["defeated_ids"])["rank"]]
            for place, (username, d) in enumerate(ranked, 1)
        ]
    )


# Reports whether each player has completed the boss requirement.
def report_boss_status():
    # We report who has defeated the final boss and who still has not.
    bosses = [m for m in mob_list if m["type"] == "Boss"]
    lines = ["Bosses: " + (", ".join(m["name"] for m in bosses) or "None"), ""]

    lines += table_lines(
        ["Username", "Boss Defeated", "Dungeon Escaped"],
        [
            [username,
             "Yes" if all_bosses_defeated(d["defeated_ids"]) else "No",
             "Yes" if d["status"] == "Victorious" else "No"]
            for username, d in player_accounts().items()
        ]
    )
    return lines


# Lists item stock and item details from the saved item catalog.
def report_available_items():
    # We list current item records with their prices and effects.
    rows = []

    # We check each related saved record so this result uses actual game data.
    for item in item_records.values():
        owned = sum(
            d["inventory"].get(item["id"], 0)
            for d in player_accounts().values()
        )
        rows.append([item["id"], item["name"], item["effect"], item["price"],
                     item["max_carry"], owned, describe_item_effect(item)])

    return table_lines(
        ["ID", "Name", "Effect", "Price", "Carry", "Owned", "Description"],
        rows,
        max_width=30
    )


# Reports the owned/equipped gear from the actual equipment records.
def report_equipment():
    # We show owned or available equipment using the actual saved gear records.
    rows = []

    # We check each related saved record so this result uses actual game data.
    for eq in equipment_records.values():
        owners = [
            u for u, d in player_accounts().items()
            if eq["id"] in d["owned_equipment"]
        ]
        rows.append([eq["id"], eq["name"], eq["slot"], eq["tier"],
                     describe_equipment(eq), eq["price"],
                     ", ".join(owners) or "none"])

    lines = ["OPTIONAL SHOP EQUIPMENT (costs Gold)"]
    lines += table_lines(
        ["ID", "Name", "Slot", "Tier", "Effect", "Price", "Owned By"],
        rows,
        max_width=30
    )

    lines += ["", "STANDARD-ISSUE EQUIPMENT (free, upgrades per cleared level)"]
    lines += table_lines(
        ["Level", "Unlocked By", "Sword", "Shield", "Armor"],
        [
            [f"Lv.{level + 1}",
             "Start" if level == 0 else
             f"Clear {STANDARD_UPGRADE_LEVELS[level - 1]} level",
             *[f"{STANDARD_EQUIPMENT[slot][level][0]} "
               f"({describe_piece(standard_piece(slot, level))})"
               for slot in EQUIPMENT_SLOTS]]
            for level in range(len(STANDARD_UPGRADE_LEVELS) + 1)
        ],
        max_width=34
    )
    return lines


# Shows Gold earned and spent using the recorded game transactions.
def report_gold_economy():
    # Challenge answers grant attack damage only, never Gold.
    # This report includes only the game's real Gold sources.
    # We calculate Gold rewards and losses from battle history instead of guessing totals.
    # We add recorded rewards and deductions to explain where Gold was earned or lost.
    shop_cost = {
        tier: sum(e["price"] for e in equipment_records.values()
                  if e["tier"] == tier)
        for tier in TIER_UNLOCK_REQUIREMENT
    }

    rows = []
    running = STARTING_STATS["gold"]
    earned_at_start_of = {}
    total_enemy = total_level = total_treasure = 0

    for tier in LEVEL_ORDER:
        mobs = [m for m in mob_list if m["type"] == tier]
        room = ROOM_FOR_DIFFICULTY[tier]
        enemy_gold = sum(m["gold_reward"] for m in mobs)
        level_gold = LEVEL_COMPLETION_GOLD.get(tier, 0)
        treasure = TREASURES.get(room, ("", "", 0))[2]
        stage = enemy_gold + level_gold + treasure

        earned_at_start_of[tier] = running
        running += stage
        total_enemy += enemy_gold
        total_level += level_gold
        total_treasure += treasure
        rows.append([tier, len(mobs), enemy_gold, level_gold, treasure,
                     stage, running])

    lines = [
        "GOLD INCOME BY LEVEL (including optional enemies and chests)",
        f"Starting Gold: {STARTING_STATS['gold']} | "
        "Challenge questions grant bonus attack damage, not Gold."
    ]
    lines += table_lines(
        ["Level", "Enemies", "Enemy Gold", "Level Bonus", "Treasure",
         "Level Total", "Running Total"],
        rows
    )

    lines += ["", "OPTIONAL EQUIPMENT COST BY SHOP TIER"]
    cumulative = 0
    cost_rows = []

    for tier in TIER_UNLOCK_REQUIREMENT:
        cumulative += shop_cost[tier]
        required = TIER_UNLOCK_REQUIREMENT[tier]
        opens_with = earned_at_start_of.get(tier, 0)
        cost_rows.append([
            tier, "Start" if required is None else f"Clear {required} level",
            shop_cost[tier], cumulative, opens_with
        ])

    lines += table_lines(
        ["Shop Tier", "Opens", "Tier Cost", "Cost So Far",
         "Gold Earned Before Tier Opens*"],
        cost_rows
    )
    lines.append("*Gold earned up to the moment the tier opens, before any "
                 "spending, rest or potions. Tier N opens when the previous "
                 "level is cleared, so it is shown at the start of the level "
                 "being fought.")

    total_income = running
    total_gear = sum(shop_cost.values())
    potion = item_records.get("ITM-001", {}).get("price", 0)

    lines += ["", "SUMMARY"]
    lines += table_lines(
        ["Measure", "Gold"],
        [
            ["Total income (whole playthrough)", total_income],
            ["  from enemies", total_enemy],
            ["  from level-clear bonuses", total_level],
            ["  from treasure chests", total_treasure],
            ["  starting Gold", STARTING_STATS["gold"]],
            ["Every optional equipment piece", total_gear],
            ["Left for potions, supplies and rest if everything is bought",
             total_income - total_gear],
            ["Income before the Boss (levels up to Strong)",
             total_income - rows[-1][5] if rows else 0],
            [f"Health Potions that income could buy ({potion} Gold each)",
             (total_income // potion) if potion else 0]
        ],
        max_width=60
    )
    return lines


# Groups enemy records by difficulty for the admin report.
def report_enemy_difficulty():
    # We group recorded enemies by their saved difficulty.
    lines = []

    for tier in LEVEL_ORDER:
        mobs = [m for m in mob_list if m["type"] == tier]
        lines.append(f"{tier.upper()} ({len(mobs)} enemies)")

        if mobs:
            lines += table_lines(
                ["ID", "Name", "HP", "ATK", "Gold", "Score", "Room"],
                [
                    [mob["id"], mob["name"], mob["max_hp"], mob["atk"],
                     mob["gold_reward"], mob["score_reward"],
                     room_name(mob["room"])]
                    for mob in mobs
                ]
            )

            avg_hp = sum(m["max_hp"] for m in mobs) // len(mobs)
            avg_atk = sum(m["atk"] for m in mobs) // len(mobs)
            lines.append(f"Average HP {avg_hp}, average ATK {avg_atk}")

        lines.append("")

    return lines


# Builds a graph report from the current rooms and passage connections.
def report_dungeon_map():
    # We generate a graph report using the current rooms and passages.
    lines = ["MAP DRAWING"]
    lines += dungeon_drawing_lines([])
    lines.append("")
    lines.append("ROOMS AND PASSAGES")
    lines += dungeon_map_lines([])
    lines.append("")
    lines.append("EXPLORATION ORDER FROM THE ENTRANCE (DFS)")
    lines += [f"  {n}. {room_name(r)}" for n, r in
              # We visit rooms in DFS order using saved connections.
              enumerate(depth_first_traversal(ENTRANCE_ROOM_ID), 1)]
    return lines


REPORTS = [
    ("Player Statistics Report", report_player_statistics),
    ("Battle Wins and Losses Report", report_wins_losses),
    ("Enemies Defeated Report", report_enemies_defeated),
    ("Player Score Ranking Report", report_score_ranking),
    ("Boss Defeat Status Report", report_boss_status),
    ("Battle History Report", battle_history_lines),
    ("Available Items Report", report_available_items),
    ("Equipment Report", report_equipment),
    ("Gold Economy Report", report_gold_economy),
    ("Enemy Difficulty Report", report_enemy_difficulty),
    ("Dungeon Map Report", report_dungeon_map)
]


# Displays a generated report and offers to save its text output.
def show_report(title, lines):
    # We print a generated report and optionally export its exact text.
    header(title)
    print(f"Generated: {now_text()}\n")

    for line in lines:
        print(line)

    if ask_yes_no("\nExport this report to a text file? (Y/N): "):
        # We handle reading, conversion, or save errors here instead of letting one problem crash the program.
        try:
            Path(REPORT_FOLDER).mkdir(exist_ok=True)
            file_name = title.lower().replace(" ", "_") + ".txt"
            path = Path(REPORT_FOLDER) / file_name

            # We use a file context here so the file is properly closed after reading or writing.
            with open(path, "w", encoding="utf-8") as file:
                file.write(f"{title.upper()}\nGenerated: {now_text()}\n\n")
                file.write("\n".join(lines) + "\n")

            print(f"\nReport saved to {path}")
        except OSError as error:
            print(f"\nThe report could not be saved: {error}")

    pause()


# Opens the available reports without using hard-coded result tables.
def report_menu():
    # We let the admin choose which current report to generate.
    # We repeat this menu or action until the player gives a valid choice or leaves.
    while True:
        header("Report Generation")

        for number, (title, _) in enumerate(REPORTS, 1):
            print(f"[{number}] {title}")

        print("\n[0] Back")

        choice = input(f"\nEnter choice [0-{len(REPORTS)}]: ").strip()

        if choice.isdigit() and 1 <= int(choice) <= len(REPORTS):
            title, builder = REPORTS[int(choice) - 1]
            show_report(title, builder())
        elif choice == "0":
            break
        else:
            invalid_choice()


# Opens the four required admin sections and handles menu navigation.
def admin_menu():
    # Main menu for administrators
    # We give admins four main sections: Dashboard, Profiling, Transactions, and Reports.
    # We repeat this menu or action until the player gives a valid choice or leaves.
    while True:
        header("Admin Menu")

        print(f"Logged in as: {player['name']} | Role: Admin")

        print("\n[1] Dashboard")
        print("[2] Profiling (File Maintenance)")
        print("[3] Transactions (Game Setup and Management)")
        print("[4] Report Generation")
        print("\n[0] Logout")

        choice = input("\nEnter choice [0-4]: ").strip()

        if choice == "1":
            admin_dashboard()
        elif choice == "2":
            profiling_menu()
        elif choice == "3":
            game_setup_menu()
        elif choice == "4":
            report_menu()
        elif choice == "0":
            reset_session_state()
            print("\nLogging out...")
            break
        else:
            invalid_choice()


if __name__ == "__main__":
    # Load game records before opening the login menu
    load_all_records()
    login_screen()