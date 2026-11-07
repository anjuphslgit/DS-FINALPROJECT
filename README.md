# DREADVEIL: THE LAST GATE

### Game README and User Guide

**Game type:** Text-based dungeon role-playing game (RPG) 
**Last updated:** November 7, 2026  
**Main program:** `DS_FinalProject_MercadoRBanaybanayJBariteJDomingoJGonzalesA.py`  


This README explains how to set up the game, how to play it, and how its main systems work.

---
## 1. Project Overview

**Dreadveil: The Last Gate** is a text-based dungeon adventure. The player starts at Dreadveil Entrance, fights enemies of different difficulties, earns Gold and equipment, and works toward defeating **Vharok, the World Eater**. Once Vharok is defeated, the player can travel to **The Last Gate** and escape.

The game uses three main data structures:

- **Queue (FIFO):** Controls the order of enemies waiting for battle.
- **Stack (LIFO):** Stores reversible action snapshots so the latest eligible action can be undone first.
- **Graph:** Represents the dungeon's connected rooms and supports travel validation, route search, and traversal.

The program also has account management, enemy and item maintenance, battle transactions, saved records, reports, and input validation. It uses local TXT and JSON files rather than a database or online service.

### Project objectives

1. Let players select and fight real enemy records maintained in the program.
2. Show enqueue, dequeue, front, and rear operations in a working battle queue.
3. Show stack push, peek, and pop through reversible player actions.
4. Use connected dungeon rooms as a real graph with valid routes and locked progression.
5. Save player progress, transactions, action history, and related records.
6. Generate reports from actual gameplay information.
7. Handle invalid inputs and restricted actions without intentionally changing valid records.

---

## 2. Requirements and Installation

**Requirements**

- Python 3.10 or newer is recommended.
- Windows, macOS, or Linux terminal; a terminal at least around 105 characters wide is easier to read.
- No third-party Python packages are needed. The program uses Python's standard library.
- Permission to read and write files in the project folder.

### Suggested project folder

```text
Dreadveil_Final_Project/
├── README.md
├── DS_FinalProject_MercadoRBanaybanayJBariteJDomingoJGonzalesA.py
├── 1_player_accounts.txt
├── 2_enemy_records.txt
├── 3_item_records.txt
├── 4_equipment_records.txt
├── 5_room_records.txt
├── 6_room_connections.txt
├── 7_question_records.txt
├── 8_battle_history_records.txt       # created when applicable
├── 9_battle_activity_log.txt          # created when applicable
├── 10_dungeon_game_records.txt        # created when applicable
├── 12_reports/                        # created when a report is exported thru admin portal
└── 11_battle_session_records.json     # created when applicable

```

The program generates the initial seven profiling files on a clean first run. Some history, snapshot, session, and report files appear only after a related game or save operation. You do not need to create empty files manually.


### Starter demo accounts

| Role | Username | Password |
|---|---|---|
| Administrator | `admin` | `admin123` |
| Player | `player` | `player123` |

These are sample accounts created on a fresh installation. Existing account files keep their saved credentials. The project currently stores passwords in plain text; **do not use real or sensitive passwords**.

---

## 3. Story and Main Goal

While playing, the character discovers a mysterious chest surrounded by black mist. A voice challenges the player to find and defeat it. The character is pulled into Dreadveil and must pass through its rooms to discover that the voice belongs to **Vharok**.

To finish the adventure, the player must:

1. Defeat **three Weak enemies** to unlock Intermediate.
2. Defeat **three Intermediate enemies** to unlock Strong.
3. Defeat **three Strong enemies** to unlock the Boss room.
4. Defeat **Vharok** in Throne of Ruin.
5. Travel to **The Last Gate** and select **Escape Dungeon**.

Players can defeat extra enemies for additional enemy rewards, but those enemies are **optional** after the three-victory requirement for their difficulty has been reached.

---

## 4. Dungeon Rooms and Passage Names

The game has **six fixed base rooms**. These are the current built-in names, with only the original entrance name changed to match the game's messages.

| Room ID | Room name | Purpose |
|---|---|---|
| `ROOM-000` | **Dreadveil Entrance** | Starting point and respawn location after defeat |
| `ROOM-001` | Rotting Sewers | Weak enemies |
| `ROOM-002` | Bloodstone Hall | Intermediate enemies |
| `ROOM-003` | War-Torn Catacombs | Strong enemies |
| `ROOM-004` | Throne of Ruin | Boss encounter |
| `ROOM-005` | The Last Gate | Final escape |

**Original passage names are kept:**

```text
Dreadveil Entrance --[Rusted Grate]------> Rotting Sewers
Rotting Sewers ----[Crimson Gate]-------> Bloodstone Hall
Bloodstone Hall ---[Iron Drawbridge]----> War-Torn Catacombs
War-Torn Catacombs [Throne Gate]--------> Throne of Ruin
Throne of Ruin ----[Sealed Exit Door]---> The Last Gate
```

The graph stores passages as **two-way connections**; the arrows above show the main story progression, not one-way graph edges. Travel still requires an existing connection and the appropriate unlock conditions.

An administrator can update room names and descriptions and manage valid passage connections. 
Creating or deleting the six base room IDs is not a supported operation in the current fixed-route design. 
Certain old built-in names are corrected when saved data is loaded, while administrator-customized names are intended to be preserved.

---

## 5. Player Progression and Rank System

Progression counts **distinct defeated enemy IDs belonging to the required difficulty**, not simply the overall Wins number. This prevents extra victories in an easy room from skipping a harder required level.

| Rank earned | Required victories | Highest difficulty available |
|---|---|---|
| Beginner | Fewer than 3 Weak victories | Weak |
| Adventurer | At least 3 Weak | Intermediate |
| Elite | At least 3 Weak **and** 3 Intermediate | Strong |
| Master | At least 3 Weak, 3 Intermediate **and** 3 Strong | Boss |

For example, if an admin adds a fourth Weak enemy, defeating any three distinct Weak enemies is enough to unlock Bloodstone Hall. 
The fourth Weak enemy remains available. 
The player may return to Rotting Sewers later and defeat it, but that extra Weak victory cannot replace a required Intermediate victory.

### Level-completion rewards

Reaching the required three victories for a regular difficulty provides:

- **+5 Base ATK**.
- **+20 Max HP**, with HP increased as part of the reward.
- A one-time level Gold bonus: **Weak +40**, **Intermediate +80**, or **Strong +150**.
- The next free standard Sword, Shield, and Armor set, when a new equipment tier is unlocked.

Rewards are granted **once per completed level**. Extra enemies do not trigger the same completion reward again. The level reward screen displays real **Before**, **After**, and **Gained** values, including the actual Gold balance before and after the level bonus. The regular enemy's Gold reward is added before the level-completion Gold bonus is displayed.

Defeating the Boss opens the final exit. The final escape also awards **500 Score**.

### Optional treasure chests

A room's treasure chest is separate from its level-unlock requirement. The player must defeat **every enemy currently in that room** to open its chest. Chests give one-time Gold and Score rewards. Therefore, a player can advance after three required victories and come back later to clear remaining enemies for treasure.

---

## 6. Player Controls and Main Features

After logging in, the player can enter the adventure, view statistics, open the dungeon map, inspect enemy information, and read **How to Play**.

At the Expedition Camp, the main options include:

- Start Battle; Add Enemy to Queue; View Queue; View Next Enemy.
- Travel to Room; Open Treasure Chest.
- Dungeon Shop; Equipment; Rest; Inventory.
- Dungeon Map; Player Stats; Player Action Stack; Undo Action.
- Save & Exit; Escape Dungeon.

During an active battle, the player can **Attack, Defend, use a Potion, use another Item, answer a Challenge, view Stats or Queue, open the Player Action Stack, Undo an eligible action, or Retreat**.

### Battle mechanics

- **Attack:** Damage uses the player's stats and equipment, with chances of misses and critical hits.
- **Defend:** Reduces incoming damage and can prepare a counterattack bonus.
- **Potion:** Restores health without exceeding Max HP, provided an applicable item is available.
- **Other items:** Strength Tonic, Paralysis Bomb, and Poison Dagger provide their defined combat effects.
- **Challenge:** Uses a question from the current enemy's difficulty; a correct answer grants attack bonus damage, not Gold.
- **Boss:** Vharok becomes enraged below half HP.
- **Shop and Equipment:** Players can buy optional equipment, equip owned pieces, and receive free standard equipment as they progress.
- **Rest:** Costs **40 Gold** and restores up to **50% of Max HP**, without exceeding Max HP.

The starting player stats are **100 HP, 100 Max HP, 14 Base ATK, and 60 Gold**, plus one Health Potion. The initial catalog contains **four consumable-item profiles** and **24 purchasable equipment profiles**.

---

## 7. What Happens After Victory, Retreat, or Defeat

| Result | Player | Enemy | Encounter Queue | Progress |
|---|---|---|---|---|
| **Victory** | Receives enemy Gold/Score and a win; may unlock a level | Marked defeated | Winning enemy is removed from the front | Saved |
| **Retreat** | Leaves the fight without earning victory rewards | Returns to full HP | Enemy stays in the queue | Earlier progress kept |
| **Defeat** | Loses 25% of current Gold and respawns at **Dreadveil Entrance** with 50% Max HP | The enemy that won returns to full HP | Queue is cleared | Earlier victories and unlocked rooms kept |
| **Final Escape** | Gains the final Score bonus and finishes the journey | Boss already defeated | No further battle needed | Final result saved |

**Example:** If a player has 120 Max HP and loses a battle, the player returns to Dreadveil Entrance with **60/120 HP**. The enemy that defeated the player is fully healed for the next encounter. 
Players may revisit already unlocked rooms to fight optional enemies.

---

## 8. Queue Implementation — FIFO

The **Encounter Queue** is a Python list named `encounter_lineup` containing enemy IDs from actual enemy profiles.

- **Enqueue:** Adds the chosen eligible enemy to the rear using `append()`.
- **Front/Peek:** Shows the next enemy without removing it.
- **Dequeue:** Removes the front using `pop(0)` after a victory; the View Queue menu also has a manual front-dequeue option.
- **Display:** Shows the full waiting lineup with FRONT and REAR labels.
- **Validation:** Rejects duplicate queued enemies, defeated enemies, invalid IDs, and invalid locations.

Example:

```text
FRONT [Gravefang Rat -> Hollowbone Goblin -> Ashen Ghoul] REAR
```

The first enemy entered is the first to be processed. 
The queue belongs to the player's current-room encounter workflow. 
If the player selects **Start Battle** with an empty queue, the game automatically queues the first eligible enemy in the current room. 
If there is no eligible enemy in that room, the game does not start a battle.

---

## 9. Stack Implementation — LIFO

The game maintains two related forms of action information:

1. **Battle activity history:** A chronological record of meaningful game actions, with saved action IDs and the relevant player/enemy details. Administrators can inspect the complete activity history.
2. **Player Undo Stack:** A list named `undo_stack` of snapshots saved **before** reversible actions. The latest eligible snapshot is on top.

### Undo process

1. The program saves the state before an eligible action (**push**).
2. The player performs the action (such as Attack, Defend, Item, Purchase, Equip, Rest, or eligible Travel).
3. **View Player Actions (Undoable)** shows the current snapshots; **View Latest Undoable Action** peeks at the top.
4. **Undo Latest Action** removes the newest snapshot (**pop**) and restores the corresponding saved state.
5. If the stack is empty, the program shows an appropriate message instead of removing anything.

PERMANENT results such as victory, defeat, retreat, and final escape are not undoable. This prevents duplicated rewards and inconsistent game outcomes.

**How the two records differ:** 
The Player Action Stack screen displays undoable snapshots. 
The permanent battle-action history is a separate saved record that administrators can view. 
Removing an undo snapshot restores eligible game state, but it does not erase completed battle results from the permanent history.

---

## 10. Graph Implementation — Dungeon Map

The six rooms are **vertices** in `room_records`. The labeled, two-way passages in `room_connections` are **edges**.

Main graph operations include:

- Listing rooms and their stored passage connections.
- Adding/removing a permitted passage, with relationship validation.
- Using **Breadth-First Search (BFS)** to find a route.
- Using **Depth-First Search (DFS)** to show an exploration order.
- Showing room details, the dungeon map, current location, and locked/unlocked status.
- Rejecting travel to an unconnected or locked destination.

A player may travel backward through connected passages to revisit earlier rooms. The map and traversal use stored room/connection data, not just a prewritten demonstration diagram. The six base room IDs remain fixed for this version of the game's story.

---

## 11. Administrator Features

Administrators have four main sections for managing game records and viewing game activity:

| Main section | What it does |
|---|---|
| **Dashboard** | Displays live player and game summaries |
| **Profiling (File Maintenance)** | Maintains Player Accounts, Enemies, Items, Equipment, Rooms/Passages, and Questions |
| **Transactions (Game Setup and Management)** | Shows player progress, resets player game data, assigns starting items, sets enemy difficulty, views battle/activity history, and handles available admin Undo actions |
| **Report Generation** | Creates reports based on actual saved records and current system information |

Admin validation protects required enemy counts. At least **three Weak, three Intermediate, three Strong, and one Boss** enemy must remain available in the program's difficulty catalog. The program also restricts editing/deleting enemies involved in saved player queues, battles, or undo states.

### Available reports

1. Player Statistics Report
2. Battle Wins and Losses Report
3. Enemies Defeated Report
4. Player Score Ranking Report
5. Boss Defeat Status Report
6. Battle History Report
7. Available Items Report
8. Equipment Report
9. Gold Economy Report
10. Enemy Difficulty Report
11. Dungeon Map Report

The admin may export a report to a TXT file in `11_reports/`. Reports are produced from program records rather than manually typed sample totals.

---

## 12. Data Files and Persistence

| File/folder | Stored information |
|---|---|
| `1_player_accounts.txt` | Account credentials, role, player stats, inventory, progress, location, and other saved account fields |
| `2_enemy_records.txt` | Enemy IDs, names, difficulties, stats, rewards, and room IDs |
| `3_item_records.txt` | Consumable-item profiles and effects |
| `4_equipment_records.txt` | Equipment IDs, slots, tiers, bonuses, and prices |
| `5_room_records.txt` | Graph room vertices and room descriptions |
| `6_room_connections.txt` | Graph passage edges and labels |
| `7_question_records.txt` | Challenge questions and assigned enemies |
| `8_battle_history_records.txt` | Saved battle outcomes and related values |
| `9_battle_activity_log.txt` | Saved action-history records |
| `10_dungeon_game_records.txt` | Readable game snapshot |
| `11_reports/` | Exported TXT reports |
| `12_battle_session_records.json` | Active battle/queue/undo session state and persisted counters |

The program attempts to write related records safely using temporary files and rollback handling. It also restores previously saved player sessions when supported saved data exists. The JSON session archive stores counters used to avoid recycling player/admin IDs and restarting recorded action IDs after a reload.

**Data-handling reminders:** Always back up saved TXT/JSON files before switching versions. Do not rename individual data files unless the names inside the Python code are updated too. Local file storage is not equivalent to a database with guaranteed crash recovery.

---


## 13. How the Python Code Is Organized

The current source uses named functions for records, game rules, structure operations, battles, and reports. These functions are useful when exploring how the program works:

| Feature | Main functions |
|---|---|
| Starting and loading | `load_all_records()`, `login_screen()` |
| Account registration | `register_new_account()`, `create_account_with_unique_id()` |
| Progression | `defeated_count_for_difficulty()`, `get_rank_info()`, `process_level_completion()` |
| Rewards table | `show_level_completion_rewards()` |
| Queue | `add_enemy_to_lineup()`, `dequeue_front_from_menu()`, `remove_front_enemy()` |
| Undo Stack | `push_undo()`, `undo_latest_action()`, `display_undo_stack()` |
| Battle outcomes | `resolve_enemy_victory()`, `resolve_player_defeat()`, `resolve_retreat()` |
| Graph | `get_neighbors()`, `get_accessible_rooms()`, `find_route()`, `depth_first_traversal()` |
| Travel and map | `travel_to_room()`, `dungeon_map_lines()` |
| Persistence | `atomic_record_updates()`, `save_session_archive()`, `restore_battle_state()` |
| Reports | `report_menu()`, `show_report()` |

Code comments explain why checks and updates are made. The tests are in a separate Python file and are **not required to launch the game itself**.

---

## 14. Technical Notes and Current Limitations

- **Six base rooms:** The story uses six fixed room IDs. Admins can rename rooms, edit descriptions, and manage valid passages, but cannot freely add or remove base rooms.
- **Local files:** Data is saved in TXT and JSON files inside the game folder. The game is intended for local use and does not use an online database.
- **Demo account passwords:** Passwords are saved as plain text in this version. Use sample credentials only, not passwords from your real accounts.
- **Undo behavior:** Only actions with a saved reversible snapshot can be undone. Completed victories, defeats, retreats, and the final escape are permanent results.
- **Game records:** A fresh installation starts with the sample accounts and item catalog. Administrators can add more compatible records from the profiling menus.
- **Interface:** This is a console game, so gameplay is controlled using text menus and keyboard input instead of a graphical window.

---

## 15. A Typical Play Session

1. Open the program, then log in with an existing player account or register a new one.
2. Read the opening story and travel from **Dreadveil Entrance** to **Rotting Sewers**.
3. Add enemies to the Encounter Queue and start a battle. During combat, use attacks, defense, consumable items, and challenges.
4. Defeat three different Weak enemies to unlock **Bloodstone Hall**. Remaining Weak enemies become optional.
5. Defeat three Intermediate enemies and three Strong enemies to unlock the **Throne of Ruin**. You may revisit earlier rooms along valid connected passages.
6. Defeat **Vharok, the World Eater**, travel to **The Last Gate**, and select **Escape Dungeon** to complete the adventure.
7. Use **Save & Exit** when you want to stop playing. The game will load supported saved progress when you return.

You can also use the shop, equip weapons and armor, rest, collect available treasure chests, or inspect the map while exploring. Every run can be different because player choices, available enemy records, and combat outcomes affect the journey.