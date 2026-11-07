# DREADVEIL: THE LAST GATE

**Program Guide**  
**Main file:** `DS_FinalProject_MercadoRBanaybanayJBariteJDomingoJGonzalesA.py`

## 1. About the Program

**Dreadveil: The Last Gate** is a menu-driven dungeon adventure. Players explore connected rooms, battle enemies, manage equipment and supplies, earn rewards, and progress toward defeating **Vharok, the World Eater**. To complete the game, the player must defeat the boss, reach **The Last Gate**, and choose **Escape Dungeon**.

We use three data structures as part of the game's actual operations:

- **Queue (FIFO):** Controls the order in which waiting enemies enter battle.
- **Stack (LIFO):** Stores snapshots of actions that the player can undo.
- **Graph:** Connects dungeon rooms and supports routes, traversal, and travel checks.

The program also includes player accounts, administrator record maintenance, combat transactions, reports, and TXT/JSON file storage.


### Demonstration accounts

| Role | Username | Password |
|---|---|---|
| Administrator | `admin` | `admin123` |
| Player | `player` | `player123` |

These are local demonstration credentials. Passwords are stored in the account TXT file, so do not reuse personal passwords.

## 2. Project Files and Their Purposes

```text
DS-FINALPROJECT/
├── DS_FinalProject_MercadoRBanaybanayJBariteJDomingoJGonzalesA.py
├── README.md
├── 1_player_accounts.txt
├── 2_enemy_records.txt
├── 3_item_records.txt
├── 4_equipment_records.txt
├── 5_room_records.txt
├── 6_room_connections.txt
├── 7_question_records.txt
├── 8_battle_history_records.txt
├── 9_battle_activity_log.txt
├── 10_dungeon_game_records.txt
├── 11_reports/
└── 12_battle_session_records.json
```

| File | What it contains |
|---|---|
| `1_player_accounts.txt` | Login information, role, base stats, Gold, wins/losses, inventory, equipped items, defeated enemies, queue, and room location. |
| `2_enemy_records.txt` | Enemy IDs, names, difficulty levels, HP, ATK, rewards, and assigned rooms. |
| `3_item_records.txt` | Item IDs, effects, power, Gold prices, maximum carrying quantities, and descriptions. |
| `4_equipment_records.txt` | Sword, Shield, and Armor profiles, equipment levels, bonuses, speed, and prices. |
| `5_room_records.txt` | Room IDs, names, and descriptions (Graph vertices). |
| `6_room_connections.txt` | Connections between rooms and passage names (Graph edges). |
| `7_question_records.txt` | Challenge questions, choices, correct answers, attack bonuses, and difficulty levels. |
| `8_battle_history_records.txt` | Completed battle results such as Victory, Defeat, and Retreat. |
| `9_battle_activity_log.txt` | Chronological game actions identified by unique action IDs. |
| `10_dungeon_game_records.txt` | A readable snapshot of the current player's game state. |
| `11_reports/` | TXT reports exported by an administrator. |
| `12_battle_session_records.json` | Saved Undo snapshots, active battle state, temporary combat effects, and record counters. |

The reports folder and some history/session files are created when the related feature is used. Temporary and recovery files may also appear during safe-saving operations. They are part of the file-handling process and should not be deleted while the game is running.

## 3. Starting the Game

At the login screen, choose **Login**, **Create New Account**, or **Exit Game**. After signing in, the program opens the appropriate Player or Administrator menu.

### Player menu

| Option | Action |
|---|---|
| `[1]` | Enter Dungeon / View Completed Journey |
| `[2]` | View Player Statistics |
| `[3]` | Dungeon Map and Routes |
| `[4]` | Enemy Information |
| `[5]` | How to Play |
| `[0]` | Logout |

### Expedition Camp menu

| Option | Action | Option | Action |
|---|---|---|---|
| `[1]` | Start Battle | `[2]` | Add Enemy to Queue |
| `[3]` | View Queue | `[4]` | View Next Enemy |
| `[5]` | Travel to Room | `[6]` | Open Treasure Chest |
| `[7]` | Dungeon Shop | `[8]` | Equipment |
| `[9]` | Rest | `[10]` | Inventory |
| `[11]` | Dungeon Map | `[12]` | Player Stats |
| `[13]` | Player Action Stack | `[14]` | Undo Action |
| `[15]` | Save & Exit | `[16]` | Escape Dungeon |

### Battle menu

| Option | Action | Option | Action |
|---|---|---|---|
| `[1]` | Attack | `[2]` | Defend |
| `[3]` | Health Potion | `[4]` | Other Item |
| `[5]` | Challenge | `[6]` | Stats |
| `[7]` | View Queue | `[8]` | Player Action Stack |
| `[9]` | Undo Action | `[10]` | Retreat |

Battle options are available only while an enemy is being fought. Shopping, resting, and changing equipment are handled at camp.

## 4. Dungeon Map and Progression

The dungeon has six connected rooms:

```text
ROOM-000  Dreadveil Entrance
    |
    | Rusted Grate
    v
ROOM-001  Rotting Sewers       (Weak)
    |
    | Crimson Gate
    v
ROOM-002  Bloodstone Hall      (Intermediate)
    |
    | Iron Drawbridge
    v
ROOM-003  War-Torn Catacombs   (Strong)
    |
    | Throne Gate
    v
ROOM-004  Throne of Ruin       (Boss)
    |
    | Sealed Exit Door
    v
ROOM-005  The Last Gate        (Exit)
```

The passages are stored as **two-way Graph connections**. The arrows show the main route through the story; players can return to an accessible earlier room.

To unlock each stage, defeat **three different enemies** of the current difficulty:

| Completed victories | Rank | Next difficulty |
|---|---|---|
| Fewer than 3 Weak | Beginner | Weak |
| 3 Weak | Adventurer | Intermediate |
| 3 Weak and 3 Intermediate | Elite | Strong |
| 3 Weak, 3 Intermediate, and 3 Strong | Master | Boss |

Completing a regular difficulty grants **+5 Base ATK**, **+20 Max HP**, and a one-time Gold bonus: Weak **40**, Intermediate **80**, or Strong **150**. Each newly unlocked equipment tier also provides free standard gear. Extra enemies can be fought for rewards, but they do not replace victories required in the next difficulty.

Treasure chests become available after **all enemies in the applicable room** have been defeated. To win the game, defeat Vharok, travel to The Last Gate, and select **Escape Dungeon**. Completing the escape adds **500 Score**.

## 5. Combat, Items, and Equipment

A new player starts with **100/100 HP**, **14 Base ATK**, **60 Gold**, and **one Health Potion**.

- **Attack:** Deals damage using the player's attack power, equipment, random damage variation, hit chance, and critical-hit chance.
- **Defend:** Reduces incoming damage and prepares a counterattack bonus.
- **Challenge:** Answers a difficulty-matched question for bonus attack damage when correct.
- **Rest:** Costs **40 Gold** and restores up to **50% of Max HP**, without exceeding the HP limit.

**Displayed ATK includes the worn Sword bonus.** The account TXT stores Base ATK; for example, 14 Base ATK plus 2 from a standard Rusty Sword displays as 16 Total ATK.

### Consumable items

| Item ID | Item | Price | Max carry | Effect |
|---|---|---:|---:|---|
| `ITM-001` | Health Potion | 30 | 10 | Restores 35% of Max HP. |
| `ITM-002` | Strength Tonic | 70 | 5 | Adds 50% damage for the next three attacks. |
| `ITM-003` | Paralysis Bomb | 110 | 5 | Has a 75% chance to paralyze the enemy for two turns. |
| `ITM-004` | Poison Dagger | 120 | 5 | Deals immediate direct damage, based on a power of 35. |
| `ITM-005` | Dice of Fate | 100 | 5 | Rolls one of six possible combat effects. |

**Dice of Fate outcomes:**

| Roll | Name | Effect |
|---|---|---|
| 1 | Cursed Roll | Lose up to 15 HP; this roll cannot reduce HP below 1. |
| 2 | Dark Shield | Block up to 30 damage from the next enemy hit. |
| 3 | Life Blessing | Recover up to 25 HP. |
| 4 | Soul Surge | Add 30% damage to the next sword attack. |
| 5 | Shadow Shield | Negate the next enemy hit. |
| 6 | Jackpot | Add 100% damage to the next sword attack. |

To use Dice of Fate, purchase it from **Dungeon Shop → Supplies**, enter battle, and choose **Other Item**. A use consumes one die and a combat turn. The program saves pending Fate shields and attack bonuses, including when a battle is resumed. Another die cannot be rolled while its prior shield or attack bonus is still pending.

### Equipment

Players wear **one Sword, one Shield, and one Armor**. They may switch between available gear, including the free standard gear for their unlocked tier, but cannot leave an equipment slot empty. Purchased equipment remains associated with the player's account.

Equipment is grouped into **Weak, Intermediate, Strong, and Boss** tiers. Each tier has two purchasable choices for each equipment type (**24 equipment records** in total). Equipment IDs run from `EQP-001` to `EQP-024`.

## 6. Queue, Stack, and Graph in the Code

### Encounter Queue — FIFO

We store waiting enemy IDs in the `encounter_lineup` list.

- **Enqueue:** Add an eligible enemy to the rear using `append()`.
- **Front / Peek:** View the next enemy without removing it.
- **Dequeue:** Remove the front enemy with `pop(0)` when the applicable operation is performed.
- **Display:** Show the enemy order with FRONT and REAR labels.

If the player selects **Start Battle** with no queued enemies, the game queues the first eligible enemy in the current room. If none remain, it prevents the battle from starting. Queue operations also check for invalid and unavailable enemy records.

### Player Action Stack — LIFO

We use `undo_stack` to keep game-state snapshots before eligible actions. The newest snapshot is the TOP of the stack.

```text
PLAYER ACTION STACK
[1] View Player Actions (Undoable)
[2] View Latest Undoable Action
[3] Undo Latest Action
[0] Back
```

- **Push:** Save a snapshot before a reversible action.
- **Peek:** Display the most recent undoable action.
- **Pop / Undo:** Restore the latest snapshot and remove it from the Stack.
- **Empty handling:** Display feedback when no Undo actions remain.

Completed Victory, Defeat, Retreat, and Final Escape results are permanent and cannot be undone through this menu. The separate activity log records completed and in-progress actions for administrator review.

### Dungeon Graph

We store rooms as vertices in `room_records` and named passages as edges in `room_connections`. The program can display the connected dungeon, validate a player's next room, find a route using **Breadth-First Search (BFS)**, and show exploration order using **Depth-First Search (DFS)**. Travel is allowed only when a passage exists and progression rules permit entry.

## 7. Battle Results and Saved Progress

| Outcome | What happens |
|---|---|
| **Victory** | The player receives the enemy's Gold and Score, gains a win, and the defeated enemy is removed from the front of the Queue. |
| **Retreat** | The battle ends without victory rewards; the enemy remains available for a later fight. |
| **Defeat** | The player loses 25% of current Gold, returns to Dreadveil Entrance at 50% Max HP, and keeps previously earned progression. |
| **Final Escape** | The player's completed adventure and final bonus are saved. |

The program saves changes to the appropriate account, battle-history, activity-log, session, and snapshot files. Undo snapshots and temporary battle effects are stored in the session JSON. The readable game snapshot reflects the current player rather than replacing every player's account record.

**Save & Exit** saves the player's progress and leaves the dungeon menu. Keep backups of TXT/JSON records before moving or replacing project files. File saving includes failure checks, but local files do not provide the same crash recovery guarantees as a transactional database.

## 8. Administrator Controls

The Admin menu has four sections:

1. **Dashboard:** View live summaries of accounts, enemies, progression, battles, and scores.
2. **Profiling (File Maintenance):** Add, view, search, update, and delete supported Player, Enemy, Item, Equipment, and Question records; maintain rooms and passages.
3. **Transactions (Game Setup and Management):** View player progress, reset game data, assign starting items, set enemy difficulty, inspect battle history and full activity history, or undo a player's available pending actions.
4. **Report Generation:** Generate reports using the stored game records and optionally export them as TXT files.

The available reports are: Player Statistics, Battle Wins and Losses, Enemies Defeated, Player Score Ranking, Boss Defeat Status, Battle History, Available Items, Equipment, Gold Economy, Enemy Difficulty, and Dungeon Map.

The six core room IDs are fixed; the Admin can update room details and manage permitted connections. Admin Undo All applies only to available reversible states, not permanent completed battle outcomes.

## 9. Main Python Functions

The program is organized into functions for file handling, account and record maintenance, game logic, data structures, combat, and reports.

| Area | Main functions | Purpose |
|---|---|---|
| Startup | `load_all_records()`, `login_screen()` | Load stored records and open account access. |
| Accounts | `register_new_account()`, `save_all_accounts()` | Create accounts and save account data. |
| Player state | `save_current_player_account()`, `restore_battle_state()` | Save and restore progress and active battles. |
| Items | `load_items()`, `supplies_shop()`, `apply_item_effect()` | Load item definitions, sell supplies, and apply combat effects. |
| Equipment | `load_equipment()`, `equipment_menu()` | Load and switch available worn gear. |
| Queue | `add_enemy_to_lineup()`, `dequeue_front_from_menu()`, `display_encounter_lineup()` | Maintain and display waiting enemies in FIFO order. |
| Stack | `push_undo()`, `undo_latest_action()`, `battle_log_menu()` | Maintain saved reversible states and let players undo eligible actions. |
| Combat | `start_battle_with_next_enemy()`, `calculate_player_attack()`, `resolve_enemy_victory()`, `resolve_player_defeat()` | Handle battles, damage, and battle outcomes. |
| Graph | `get_neighbors()`, `find_route()`, `depth_first_traversal()`, `travel_to_room()` | Read connections, search routes, and control travel. |
| File storage | `atomic_record_updates()`, `save_session_archive()` | Coordinate record writing and session saving. |
| Admin | `profiling_menu()`, `game_setup_menu()`, `report_menu()` | Open maintenance, transactions, and reports. |

These functions use the same saved records that appear in the TXT/JSON files. Tables and menus present the current program data rather than relying on fixed demonstration results.

## 10. Troubleshooting

**The game cannot find saved records.** Run the Python file from the directory containing the TXT and JSON files. Confirm that the filenames match those used in the code.
**An item or equipment record does not appear.** Check that the row has the required fields, its ID is unique, and the effect or equipment slot is valid.
**A player cannot start a battle.** Confirm the current room has an eligible undefeated enemy and that the room is accessible.
**Undo is unavailable.** The player can undo only actions with an active saved snapshot. Permanent completed outcomes cannot be reversed.
**Changes are not saved.** Check folder permissions, available disk space, and whether another program is locking the records. Review the error shown by the program before continuing.
**The console layout looks crowded.** Use a wider terminal window so tables and the game HUD can be displayed properly.