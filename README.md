# Dungeon Conquest (TDC)

**User Guide and Program Documentation**  
Data Structures Laboratory | Python Console Application

Dungeon Conquest is a text-based dungeon adventure in which players travel through connected rooms, battle enemies, collect treasure, improve equipment, and defeat the final boss. The game features separate Player and Administrator accounts and saves game information in text files.


## Contents

1. [Getting Started](#1-getting-started)
2. [Logging In and Main Menus](#2-logging-in-and-main-menus)
3. [How to Play](#3-how-to-play)
4. [Dungeon Map and Progression](#4-dungeon-map-and-progression)
5. [Battle Guide](#5-battle-guide)
6. [Items, Equipment, and Rewards](#6-items-equipment-and-rewards)
7. [Data Structures Used](#7-data-structures-used)
8. [Administrator Guide](#8-administrator-guide)
9. [Record Files and Saving](#9-record-files-and-saving)
10. [Troubleshooting](#10-troubleshooting)

## 1. Getting Started
### Requirements

```bash
python3 DS_FinalProject_MercadoRBanaybanayJBariteJDomingoJGonzalesA.py
```

> **Important:** Run the program from the folder containing the `.txt` record files. The game reads and writes those files using relative paths. Keep a backup of the record files before testing or making changes.

## 2. Logging In and Main Menus

### Login screen

| Option | Action |
|---|---|
| `[1] Login` | Enter an existing username and password. |
| `[2] Create New Account` | Register a player account. |
| `[0] Exit Game` | Close the program. |

The project includes these standard accounts:

| Account type | Username | Password |
|---|---|---|
| Administrator | `admin` | `admin123` |
| Player | `player` | `player123` |

Additional accounts can be created through the login screen or maintained by an administrator. For security, use these demonstration passwords only within the project environment; the educational program stores credentials in plain text.

### Player main menu

After signing in as a player, the menu provides the following options:

| Option | Purpose |
|---|---|
| `[1] Enter Dungeon` | Open the dungeon and continue the adventure. |
| `[2] View Player Statistics` | Review HP, attack, equipment, score, and progress. |
| `[3] Dungeon Map and Routes` | View connected rooms and use route-finding features. |
| `[4] Enemy Information` | Check enemy attributes and availability. |
| `[5] How to Play` | Read gameplay instructions inside the program. |
| `[0] Logout` | Save account progress and return to the login screen. |

### Dungeon menu

The main dungeon screen shows the player's HP, attack, speed, defense, block, Gold, room, encounter queue, and recent actions.

```text
EXPLORE AND BATTLE
[1]  Add Enemy to Queue    [2]  View Queue          [3]  View Next Enemy
[4]  Start Battle          [5]  Open Treasure Chest [6]  Travel to Room

CAMP
[7]  Dungeon Shop         [8]  Equipment           [9]  Rest (40 Gold)
[10] Inventory            [11] Dungeon Map

RECORDS
[12] Player Stats         [13] Action History Stack [14] Undo Last Action
[15] Save Game            [16] Save & Exit        [17] Escape Dungeon
```

**Save & Exit** stores the player's current progress and returns to the player menu. **Escape Dungeon** is the final winning action and is available only after the necessary objectives are completed.

## 3. How to Play

Follow this basic gameplay sequence:

1. Sign in as a player and select **Enter Dungeon**.
2. Use **Travel to Room** to enter an available connected room.
3. Choose **Add Enemy to Queue** to select an enemy from that room.
4. Check **View Queue** or **View Next Enemy** to see the upcoming battle.
5. Select **Start Battle** to fight the enemy at the front of the queue.
6. Defeat all enemies in the room to unlock the next area.
7. Open the room's treasure chest, visit the shop, or rest when needed.
8. Continue through each difficulty level until the final boss is defeated.
9. Travel to **The Last Gate** and choose **Escape Dungeon** to finish the game.

The Encounter Queue processes enemies in the order they were added. A defeated enemy is removed from the queue. If a player retreats, the enemy stays in the queue so the encounter can be attempted again.

## 4. Dungeon Map and Progression

### Room order

```text
Dungeon Entrance
       |
       v
Rotting Sewers (Weak)
       |
       v
Bloodstone Hall (Intermediate)
       |
       v
War-Torn Catacombs (Strong)
       |
       v
Throne of Ruin (Boss)
       |
       v
The Last Gate (Exit)
```

The dungeon has six connected rooms and ten enemies. Players must clear the appropriate enemies to advance. The final exit is locked until **Vharok, the World Eater** is defeated.

### Player ranks

| Rank | Victories | Available difficulty |
|---|---:|---|
| Beginner | 0–2 | Weak |
| Adventurer | 3–5 | Intermediate and earlier levels |
| Elite | 6–8 | Strong and earlier levels |
| Master | 9 or more | Boss and earlier levels |

Completing a difficulty level grants additional base attack, maximum HP, and a Gold reward. The next level also provides a new set of free equipment.

### Dungeon Map and Routes

The Dungeon Map submenu provides:

| Option | Feature |
|---|---|
| `[1] View Dungeon Map` | Display rooms and available passages. |
| `[2] Room Details and Passages` | Inspect room information and connections. |
| `[3] Find Route to a Room (BFS)` | Find a route through the dungeon graph. |
| `[4] Exploration Order (DFS Traversal)` | Display depth-first room traversal. |
| `[0] Back` | Return to the previous menu. |

## 5. Battle Guide

### Battle menu

| Option | Action | Option | Action |
|---|---|---|---|
| `[1]` | Attack | `[2]` | Defend |
| `[3]` | Health Potion | `[4]` | Other Item |
| `[5]` | Challenge | `[6]` | Stats |
| `[7]` | View Queue | `[8]` | Action Stack |
| `[9]` | Undo Last Action | `[10]` | Save |
| `[11]` | Retreat | | |

**Attack** damages the enemy, although attacks may miss or land critical hits. **Defend** reduces incoming damage during that turn and strengthens the following attack. Potions and other battle items use a turn.

### Challenge questions

Each enemy has a corresponding question about data structures. The player can attempt one Challenge question during each battle.

- A **correct answer** performs a guaranteed hit with additional damage for that attack.
- A **wrong answer** does not give bonus damage and uses the player's turn.
- Stronger enemies have questions with higher attack bonuses.
- Answer choices are shuffled on screen.

The final boss has a separate Challenge question. The Challenge feature awards bonus **attack damage**, not Gold.

### Retreat and defeat

**Retreat** ends the current battle. The enemy returns to full HP and remains at the front of the queue; no victory reward is given.

If the player's HP reaches zero, the game records a defeat. The player loses 25% of their current Gold, returns to the entrance with 50% of maximum HP, and the encounter queue is cleared. Previously completed levels, defeated-enemy records, and owned equipment are retained. The enemy recovers part of its HP before the next attempt.

### Action History and Undo

The **Action History Stack** displays recorded actions, with the latest action on top. **Undo Last Action** restores the most recent reversible game state, such as an attack, item use, purchase, equipment change, or camp rest. Completed battles, retreats, and room travel cannot be undone.

## 6. Items, Equipment, and Rewards

### Shop items

| Item | Use |
|---|---|
| Health Potion | Restores a percentage of the player's maximum HP. |
| Strength Tonic | Boosts damage for the next three attacks. |
| Paralysis Bomb | Has a chance to prevent the enemy from acting for multiple turns. |
| Poison Dagger | Deals direct damage that does not miss. |

Select **Dungeon Shop** to purchase supplies or equipment. Items require sufficient Gold and are subject to carrying limits.

### Equipment progression

The player uses a sword, shield, and armor. Each newly unlocked difficulty has its own free equipment set, and the shop offers optional upgrades for that level.

| Level | Sword | Shield | Armor |
|---|---|---|---|
| Weak | Rusty Sword | Wooden Shield | Cloth Armor |
| Intermediate | Bloodstone Sword | Iron Shield | Chainmail Armor |
| Strong | Steel Sword | Steel Shield | Steel Armor |
| Boss | Darksteel Sword | Darksteel Shield | Darksteel Armor |

- **Sword:** Adds attack power; speed improves hit accuracy and critical-hit chance.
- **Shield:** Blocks a percentage of incoming damage.
- **Armor:** Reduces damage received per hit.

Purchased equipment stays in the inventory, but only equipment appropriate to the current level can be equipped. Use **Equipment** in the dungeon menu to choose available gear.

### Rest and treasure

**Rest at Camp** costs 40 Gold and restores up to 50% of maximum HP. A treasure chest becomes available after all enemies in its room are defeated. Each chest can be opened only once per player and awards Gold and score.

Gold can also be earned from enemy victories and completing difficulty levels. Gold is spent on supplies, equipment, and resting.

## 7. Data Structures Used

Dungeon Conquest demonstrates data structures through gameplay rather than separate examples.

| Data structure | Purpose in the game | Common operations |
|---|---|---|
| **Queue (FIFO)** | Stores upcoming enemies in encounter order. | Enqueue, dequeue, peek/front, display. |
| **Action History Stack (LIFO)** | Records the sequence of player and battle actions. | Push, view top, display. |
| **Undo Stack (LIFO)** | Stores reversible action snapshots. | Push and pop to restore a previous state. |
| **Graph** | Represents dungeon rooms and connected passages. | View connections, search, BFS routes, DFS traversal. |

These structures are integrated with the player, enemy, room, and battle records. The game displays their contents while the corresponding operations take place.

## 8. Administrator Guide

Administrator accounts open the management menu rather than the player adventure menu.

| Option | Section | Main purpose |
|---|---|---|
| `[1]` | Dashboard | View summaries of players, enemies, and game progress. |
| `[2]` | Profiling (File Maintenance) | Add, view, search, update, and delete records. |
| `[3]` | Transactions (Game Setup and Management) | Review or manage player progress, items, enemy difficulty, and battle history. |
| `[4]` | Report Generation | View reports and optionally export them to text files. |
| `[0]` | Logout | Return to the login screen. |

**Profiling** includes player accounts, enemies, items, equipment, rooms/passages, and Challenge questions. **Transactions** includes viewing player progress, resetting a selected player's game data, assigning starting items, changing enemy difficulty, and viewing battle history.

### Available reports

1. Player Statistics
2. Battle Wins and Losses
3. Enemies Defeated
4. Player Score Ranking
5. Boss Defeat Status
6. Battle History
7. Available Items
8. Equipment
9. Gold Economy
10. Enemy Difficulty
11. Dungeon Map

After opening a report, choose whether to export it. Exported reports are written into the `reports/` folder.

## 9. Record Files and Saving

The game uses text files to keep information between sessions.

| File | Stored information |
|---|---|
| `1player_accounts.txt` | Player and administrator accounts, stats, inventory, equipment, queue, and progress. |
| `2enemy_records.txt` | Enemy details, difficulty, combat stats, rewards, and assigned room. |
| `3item_records.txt` | Item information, effects, prices, and carry limits. |
| `4equipment_records.txt` | Equipment names, types, bonuses, prices, and tiers. |
| `5room_records.txt` | Dungeon rooms. |
| `6room_connections.txt` | Connections between dungeon rooms. |
| `7question_records.txt` | Challenge questions, answer choices, attack bonuses, and enemy assignments. |
| `8battle_history_records.txt` | Saved battle results. |
| `9battle_activity_log.txt` | Saved action-history output for the current session. |
| `10dungeon_game_records.txt` | Readable saved-game information for the current session. |

The main program is `DS_FinalProject_MercadoRBanaybanayJBariteJDomingoJGonzalesA.py`.

### Saving progress

Use **Save Game** from the dungeon menu, or **Save** during battle, to write game information. Player-account progress is also saved during gameplay and on logout. **Save & Exit** leaves the dungeon while retaining the player's saved progress and encounter queue.

> Keep the Python file and numbered record files together. A missing record file may be recreated with default information, so do not delete or replace saved data without making a backup.

## 10. Troubleshooting

| Problem | What to check |
|---|---|
| An account or saved progress is missing. | Run the game from the folder containing the correct `1player_accounts.txt` file. |
| An enemy cannot be added to the queue. | Confirm that the enemy is undefeated, belongs to the current room, and is unlocked. |
| The next room is locked. | Defeat all required enemies in the preceding room. |
| There is not enough Gold for an item. | Earn more Gold through battles, level rewards, or treasure chests. |
| Equipment is not available to wear. | Check the current difficulty tier and the owned equipment list. |
| The treasure chest cannot be opened. | Clear every enemy in the room first; each chest opens only once. |
| Undo does not work. | Only reversible actions can be undone; major battle and travel outcomes cannot. |
| Escape Dungeon is unavailable. | Defeat the boss and travel to **The Last Gate** before choosing the final escape action. |
| Tables do not fit the screen. | Widen the terminal window or reduce the terminal font size. |

---

**Dungeon Conquest — Data Structures Laboratory**  
Python console game with Queue, Stack, and Graph operations.
