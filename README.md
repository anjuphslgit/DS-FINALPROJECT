# DREADVEIL: THE LAST GATE

**Program Guide**  
**Main program:** `DS_FinalProject_MercadoRBanaybanayJBariteJDomingoJGonzalesA.py`  
**Language:** Python 3  
**Type:** Menu-driven dungeon adventure

## 1. About the Program

**Dreadveil: The Last Gate** is a console-based dungeon adventure where players explore connected rooms, defeat enemies, earn rewards, and face **Vharok, the World Eater**. The goal is to clear every enemy room, reach **The Last Gate**, and escape the dungeon.

The program uses three data structures during gameplay:

- **Queue (FIFO):** Holds enemies selected by the player. The first enemy added is the first enemy fought.
- **Stack (LIFO):** Stores game-state snapshots so the most recent action can be undone first.
- **Graph:** Represents the dungeon rooms and passages used for travel and route searches.

Player accounts, administrator tools, battle history, progress records, and reports are stored in TXT and JSON files.

### Demo accounts

| Role | Username | Password |
|---|---|---|
| Administrator | `admin` | `admin123` |
| Player | `player` | `player123` |

These accounts are for local demonstration. The program stores account passwords in a TXT file, so personal passwords should not be used.

## 2. Project Files

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

| File | Purpose |
|---|---|
| `1_player_accounts.txt` | Accounts, player statistics, inventory, queue, room location, and progress. |
| `2_enemy_records.txt` | Enemies, difficulty, HP, ATK, rewards, and assigned rooms. |
| `3_item_records.txt` | Consumable items, effects, prices, and carrying limits. |
| `4_equipment_records.txt` | Swords, shields, armor, bonuses, and prices. |
| `5_room_records.txt` | Room names and descriptions (graph vertices). |
| `6_room_connections.txt` | Connected rooms and passage names (graph edges). |
| `7_question_records.txt` | Challenge questions, answers, and damage bonuses. |
| `8_battle_history_records.txt` | Saved battle results and the final escape record. |
| `9_battle_activity_log.txt` | Recorded player and battle actions. |
| `10_dungeon_game_records.txt` | Readable game progress snapshot. |
| `11_reports/` | Administrator-generated TXT reports. |
| `12_battle_session_records.json` | Active battle details, queue-related session data, Undo snapshots, and counters. |

The game creates supported record files and the reports folder as needed. Keep the TXT and JSON records together with the program when continuing saved progress.

## 3. Player Menus

### Main player menu

| Choice | Action |
|---|---|
| `[1]` | Enter Dungeon |
| `[2]` | View Player Statistics |
| `[3]` | Dungeon Map and Routes |
| `[4]` | Enemy Information |
| `[5]` | How to Play |
| `[0]` | Logout |

### Expedition Camp

| Choice | Action | Choice | Action |
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

| Choice | Action | Choice | Action |
|---|---|---|---|
| `[1]` | Attack | `[2]` | Defend |
| `[3]` | Health Potion | `[4]` | Other Item |
| `[5]` | Challenge | `[6]` | Stats |
| `[7]` | View Queue | `[8]` | Player Action Stack |
| `[9]` | Undo Action | `[10]` | Retreat |

The **How to Play** screen inside the game shows a short guide. The **OBJECTIVE** in the player status panel shows the current room goal and updates with enemy progress.

## 4. Dungeon Map and Room Progression

The dungeon contains six rooms connected in this order:

```text
Dreadveil Entrance (ROOM-000)
        |
        v
Rotting Sewers (ROOM-001)        - Weak
        |
        v
Bloodstone Hall (ROOM-002)       - Intermediate
        |
        v
War-Torn Catacombs (ROOM-003)    - Strong
        |
        v
Throne of Ruin (ROOM-004)        - Boss
        |
        v
The Last Gate (ROOM-005)         - Exit
```

Passages connect rooms in both directions, so players may revisit reachable rooms. Entry into a later room depends on clearing the required rooms.

**All enemies currently assigned to a room must be defeated before the next room unlocks.** The requirement is based on the saved enemy records, including enemies created by an administrator.

| Room completed | Rank reached | Unlocked stage |
|---|---|---|
| Rotting Sewers (all Weak enemies) | Adventurer | Intermediate |
| Bloodstone Hall (all Intermediate enemies) | Elite | Strong |
| War-Torn Catacombs (all Strong enemies) | Master | Boss |
| Throne of Ruin (all bosses) | Master | The Last Gate |

For example, if a room has four enemies and three are defeated, progress is **3/4**. The remaining enemy must also be defeated to clear the room. If the administrator adds new enemy, the progress total updates and forward access follows the current clearance requirement. Rewards already earned from a room are not granted twice.

The on-screen objective changes depending on the player's location, such as:

```text
Defeat 1 more Intermediate enemy to unlock the next room (2/3).
Travel to Bloodstone Hall and defeat 1 Intermediate enemy (2/3).
```

Clearing a regular room grants a one-time **+5 Base ATK**, **+20 Max HP**, and Gold bonus: **40** for Weak, **80** for Intermediate, and **150** for Strong. Free standard equipment becomes available with the corresponding tier. A cleared fighting room also has a one-time treasure chest that can be opened while in that room.

## 5. Encounter Queue (FIFO)

The **Encounter Queue** is a player-controlled list of enemies waiting for battle. It uses **First In, First Out (FIFO)**.

1. Travel to an accessible enemy room.
2. Select **`[2] Add Enemy to Queue`** and choose an available enemy.
3. Select **`[1] Start Battle`** to fight the enemy at the **FRONT**.
4. After victory, that enemy is removed from the front. Other queued enemies keep their order.

**Start Battle does not automatically add an enemy.** If the queue is empty, the game asks the player to add one first. An enemy must be undefeated, accessible, and eligible for the room where it is selected. The same enemy cannot be queued twice.

The queue is saved when the player **travels, retreats, loses a battle, saves, or logs back in**. If the front enemy is in another room, the player must return to that room before fighting it. **View Queue** shows each enemy's position and room. Outside battle, the player may also choose **Dequeue Front Enemy**, which removes the first queued enemy without fighting.

## 6. Player Action Stack (LIFO)

The **Undo Stack** saves snapshots of reversible actions using **Last In, First Out (LIFO)**:

- **Push:** Store a snapshot before an action.
- **Peek:** View the latest action that can be undone.
- **Pop / Undo:** Restore the most recent snapshot first.

Undo can restore battle actions, queue changes, travel, equipment and item changes, and battle outcomes such as **victory, defeat, or retreat**. Restoring a snapshot can also restore HP, Gold, Score, inventory, enemy states, earned rewards, room progress, and room unlocks. An undone victory may return the player to the active battle.

The **Player Action Stack** menu lets players view undoable actions, inspect the latest action, or undo it. The activity history is saved separately from the Undo Stack.

**Final Escape cannot be undone.** Once the player confirms the ending and it is saved successfully, gameplay and the Undo Stack are permanently locked for that character.

## 7. Combat, Camp, and Rewards

A newly registered player starts with **100 HP**, **100 Max HP**, **14 Base ATK**, **60 Gold**, and **one Health Potion**.

- **Attack:** Uses attack power, equipped sword, hit chance, critical chance, and damage variation.
- **Defend:** Reduces damage and prepares a stronger next attack.
- **Items:** Restore HP, boost damage, stun enemies, deal damage, or trigger Dice of Fate effects.
- **Challenge:** A correct answer gives an attack bonus; a wrong answer uses the turn.
- **Retreat:** Ends the encounter; the enemy heals and stays in the queue.
- **Defeat:** Deducts **25% of current Gold**, revives the player with **50% of Max HP**, and returns them to Dreadveil Entrance. The queue and completed victories remain saved.
- **Rest:** Costs **40 Gold** and heals **50% of Max HP**, without exceeding the HP limit.

Players equip **one Sword, one Shield, and one Armor**. The shop offers consumables and optional upgrades for accessible equipment tiers. The displayed attack value includes the equipped sword's bonus.

### Saved battle results

| Result | Saved effect |
|---|---|
| Victory | Defeated enemy recorded; Gold and Score added; enemy removed from the queue. |
| Retreat | Battle ends; enemy returns to full HP; queue order remains. |
| Defeat | Gold penalty and revival recorded; enemy heals; queue and prior progress remain. |
| Escape | Final score bonus recorded; the completed journey becomes read-only. |

## 8. Final Escape and Completed Journey

The player must clear the fighting rooms, defeat **Vharok**, and travel to **The Last Gate**. Selecting **Escape Dungeon** opens a final confirmation:

- **No:** Cancel the escape and continue playing.
- **Yes:** Save the completed story, earn **+500 Score**, clear the Undo Stack, and permanently lock gameplay.

The completed state remains locked after logout and login. The player can view these records:

```text
JOURNEY COMPLETE - RECORDS

[1] Player Statistics
[2] Battle History
[3] Activity History
[4] Dungeon Map and Routes
[5] Inventory and Equipment

[0] Logout
```

These options are **read-only**. Enemies cannot be queued or fought, rooms cannot be explored, and the final escape cannot be reversed. **Enemy Records is not an option in the completed-journey menu.**

## 9. Graph and Administrator Features

### Graph operations

Dungeon rooms are stored as vertices in `room_records`, and the passages are stored as edges in `room_connections`. The map supports:

- Displaying room connections and passage information.
- Checking whether travel between connected rooms is allowed.
- Finding a route with **Breadth-First Search (BFS)**.
- Showing exploration order with **Depth-First Search (DFS)**.

### Administrator menu

| Option | Section | Purpose |
|---|---|---|
| `[1]` | Dashboard | Display player, battle, enemy, and progress summaries. |
| `[2]` | Profiling (File Maintenance) | Maintain players, enemies, items, equipment, questions, rooms, and connections. |
| `[3]` | Transactions (Game Setup and Management) | View progress, reset player data, assign items, inspect history, and manage undoable actions. |
| `[4]` | Report Generation | Display and export reports based on saved game data. |
| `[0]` | Logout | Exit the administrator menu. |

Reports include player statistics, wins and losses, defeated enemies, score rankings, boss status, battle history, available items, equipment, Gold economy, enemy difficulty, and dungeon map.

Administrator enemy changes affect room-clear requirements. A room becomes complete only when every enemy currently assigned to that room has been defeated. A completed final escape remains locked.

## 10. Main Python Functions

| Area | Main functions | Purpose |
|---|---|---|
| Startup | `load_all_records()`, `login_screen()` | Load saved records and handle logins. |
| Player menus | `open_adventure_menu()`, `dungeon_menu()`, `show_instructions()` | Display player options, camp actions, and instructions. |
| Accounts | `register_new_account()`, `save_all_accounts()` | Create and store account records. |
| Queue | `add_enemy_to_lineup()`, `display_encounter_lineup()`, `dequeue_front_from_menu()` | Manage enemy order using FIFO. |
| Stack | `push_undo()`, `undo_latest_action()`, `battle_log_menu()` | Save and restore actions using LIFO. |
| Progression | `room_enemy_progress()`, `is_level_complete()`, `current_objective_text()` | Calculate live room goals and unlock conditions. |
| Combat | `start_battle_with_next_enemy()`, `resolve_enemy_victory()`, `resolve_player_defeat()` | Start battles and process results. |
| Map | `get_neighbors()`, `find_route()`, `depth_first_traversal()`, `travel_to_room()` | Work with graph connections and navigation. |
| Ending | `escape_dungeon()` | Confirm and save the final escape. |
| Storage | `atomic_record_updates()`, `save_session_archive()` | Save related records and session details. |
| Admin | `profiling_menu()`, `game_setup_menu()`, `report_menu()` | Maintain records and generate reports. |

## 11. Troubleshooting

**The game cannot find saved data.** Run the program in the folder that contains its TXT and JSON records. Check that the filenames are correct.

**Start Battle cannot begin.** Add an enemy to the queue first. The enemy at the front must be in the player's current room, and that room must be accessible.

**The next room is locked.** Check the objective and defeat every remaining enemy in the required room. The total includes enemies assigned by the administrator.

**Undo is empty or unavailable.** Check whether a reversible snapshot exists. Undo cannot be used after final escape.

**The terminal displays overlapping screens.** Run the game in a terminal that supports ANSI clearing and use a wide enough terminal for tables.

**Changes are not saved.** Confirm that the project folder is writable and there is enough available storage. Avoid editing record files while the game is running.