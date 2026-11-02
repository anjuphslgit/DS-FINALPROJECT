# Dreadveil: The Last Gate

**A text-based fantasy dungeon adventure**  
**Data Structures Laboratory | Python Console Game**

> **Enter the darkness. Conquer the guardians. Break the curse. Reach the Last Gate.**

## About the Game

**Dreadveil: The Last Gate** is a single-player, story-driven dungeon adventure played in a Python terminal. The player explores connected rooms, battles enemies, earns rewards, manages equipment, and works toward a final confrontation with **Vharok, the World Eater**.

The adventure is built around three data structures used during gameplay:

- **Queue (FIFO):** Organizes enemies waiting to be fought.
- **Stack (LIFO):** Tracks battle actions and supports undoing eligible actions.
- **Graph:** Connects dungeon rooms and supports route search and traversal.

The game also includes player accounts, persistent save files, an administrator interface, and reports based on stored game records.

## Contents

1. [The Story](#1-the-story)
2. [Requirements and Installation](#2-requirements-and-installation)
3. [Starting the Game](#3-starting-the-game)
4. [Game Menus and Controls](#4-game-menus-and-controls)
5. [Dungeon Map and Progression](#5-dungeon-map-and-progression)
6. [Combat and Challenge Questions](#6-combat-and-challenge-questions)
7. [Player Statistics, Items, and Equipment](#7-player-statistics-items-and-equipment)
8. [Victory, Defeat, and Saved Progress](#8-victory-defeat-and-saved-progress)
9. [Data Structures in the Game](#9-data-structures-in-the-game)
10. [Administrator Guide](#10-administrator-guide)
11. [Game Files and Data Storage](#11-game-files-and-data-storage)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. The Story

While playing **Dreadveil: The Last Gate**, you discover a mysterious treasure chest glowing beneath a veil of black mist. A voice calls from within:

> *“Can you find and kill me?”*

You accept the challenge. Suddenly, the screen goes dark and the world around you disappears. When you awaken, you are no longer sitting in front of your computer. You are trapped inside **Dreadveil**, a cursed dungeon where monsters guard every passage.

At the heart of the dungeon waits **Vharok, the World Eater**—the source of the voice and the power holding the **Last Gate** shut. To return home, you must defeat the dungeon's guardians, grow stronger, confront Vharok at the **Throne of Ruin**, and finally cross the Last Gate.

### Your Mission

1. Explore the dungeon's connected rooms in order.
2. Defeat the guardians in the **Weak**, **Intermediate**, and **Strong** areas.
3. Collect Gold, recover HP, and improve your equipment.
4. Defeat **Vharok, the World Eater**, in the Boss Room.
5. Reach **The Last Gate** and escape to complete the story.

Defeating the final boss opens the way out, but the adventure is completed only when the player **steps through the Last Gate**.

---

## 2. Requirements and Installation

### System Requirements

- **Python 3**
- A terminal such as **Command Prompt**, **PowerShell**, or **Terminal**
- The main `.py` game file and its numbered `.txt` record files

The game uses Python's standard library; **no third-party packages are required**.

### Run the Program

Place the Python file and record files in the same folder. Open a terminal in that folder and run:

**Windows:**

```powershell
python Dreadveil_The_Last_Gate_Final_Escape_Outro.py
```

**macOS / Linux:**

```bash
python3 Dreadveil_The_Last_Gate_Final_Escape_Outro.py
```

If your Python file has a different filename, replace the filename in the command with the actual name of your file.

**Important:** Start the program from its project folder. The record files are read and saved using relative file paths. Keep a backup of the `.txt` files when moving the project or testing with existing progress.

---

## 3. Starting the Game

### Main Login Screen

| Option | Description |
|---|---|
| `[1] Login` | Sign in using an existing account. |
| `[2] Create New Account` | Register a new player account. |
| `[0] Exit Game` | Close the application. |

### Demonstration Accounts

The program can create these initial accounts when no account records are available:

| Role | Username | Password |
|---|---|---|
| Administrator | `admin` | `admin123` |
| Player | `player` | `player123` |

These are demonstration credentials for a local classroom project. Passwords are kept in the text-based account records; do not reuse personal passwords.

When logging in, the game loads the player's saved statistics, equipment, completed levels, room location, and encounter queue.

### Player Menu

| Option | Description |
|---|---|
| `[1] Enter Dungeon` | Begin or continue an unfinished adventure. |
| `[2] View Player Statistics` | View current stats, rank, inventory, and progress. |
| `[3] Dungeon Map and Routes` | Inspect the map, passages, BFS routes, and DFS traversal. |
| `[4] Enemy Information` | View enemy records and their availability. |
| `[5] How to Play` | Open the built-in gameplay instructions. |
| `[0] Logout` | Save player progress and return to the login screen. |

Once the adventure is completed, option `[1]` becomes **View Completed Journey**, allowing the player to revisit the ending and final score.

---

## 4. Game Menus and Controls

### Dungeon Menu

The dungeon interface displays your current room, **HP**, **ATK**, **SPD**, **DEF**, **BLOCK**, **Gold**, rank, encounter queue, and action history.

```text
EXPLORE AND BATTLE
[1]  Add Enemy to Queue    [2]  View Queue           [3]  View Next Enemy
[4]  Start Battle          [5]  Open Treasure Chest  [6]  Travel to Room

CAMP
[7]  Dungeon Shop         [8]  Equipment            [9]  Rest (40 Gold)
[10] Inventory            [11] Dungeon Map

RECORDS
[12] Player Stats         [13] Action History Stack [14] Undo Last Action
[15] Save Game            [16] Save & Exit           [17] Escape Dungeon
```

**Key actions**

- **`[16] Save & Exit`** — saves your current player data and encounter queue, then returns to the Player Menu.
- **`[17] Escape Dungeon`** — completes the adventure only after Vharok has been defeated and the player is standing at **The Last Gate**.
- **`[15] Save Game`** — writes a readable snapshot of the current game in addition to saving the player record.

### Battle Menu

| Option | Action | Option | Action |
|---|---|---|---|
| `[1]` | Attack | `[2]` | Defend |
| `[3]` | Health Potion | `[4]` | Other Item |
| `[5]` | Challenge | `[6]` | Stats |
| `[7]` | View Queue | `[8]` | Action Stack |
| `[9]` | Undo Last Action | `[10]` | Save |
| `[11]` | Retreat | | |

### Dungeon Map Menu

| Option | Description |
|---|---|
| `[1] View Dungeon Map` | View the connected dungeon rooms. |
| `[2] Room Details and Passages` | Inspect rooms and labeled connections. |
| `[3] Find Route to a Room (BFS)` | Search for a route through the graph. |
| `[4] Exploration Order (DFS Traversal)` | Display the depth-first exploration order. |
| `[0] Back` | Return to the previous screen. |

---

## 5. Dungeon Map and Progression

### Dungeon Route

The dungeon contains **six connected rooms**, arranged as a journey from the entrance to the exit.

```text
            [ROOM-000] DUNGEON ENTRANCE
                        |
                    Rusted Grate
                        |
            [ROOM-001] ROTTING SEWERS
                   Weak enemies
                        |
                    Crimson Gate
                        |
            [ROOM-002] BLOODSTONE HALL
               Intermediate enemies
                        |
                   Iron Drawbridge
                        |
           [ROOM-003] WAR-TORN CATACOMBS
                   Strong enemies
                        |
                     Throne Gate
                        |
             [ROOM-004] THRONE OF RUIN
              Vharok, the World Eater
                        |
                  Sealed Exit Door
                        |
             [ROOM-005] THE LAST GATE
                    Final escape
```

Passages connect neighboring rooms, but access to later areas depends on completing the required battles. The final exit remains sealed until Vharok is defeated.

### Enemies and Difficulty Levels

| Level | Room | Enemies |
|---|---|---|
| **Weak** | Rotting Sewers | Gravefang Rat, Hollowbone Goblin, Ashen Ghoul |
| **Intermediate** | Bloodstone Hall | Ironjaw Reaver, Boneguard Executioner, Hellchain Marauder |
| **Strong** | War-Torn Catacombs | Dreadfang Berserker, Abyssal Death Knight, Soulreaper Wraith |
| **Boss** | Throne of Ruin | Vharok, the World Eater |

There are **10 enemies** in the default adventure. Enemies become progressively stronger as the player advances.

### Player Ranks

| Rank | Total Victories | Enemy Access |
|---|---:|---|
| Beginner | 0–2 | Weak |
| Adventurer | 3–5 | Weak and Intermediate |
| Elite | 6–8 | Weak, Intermediate, and Strong |
| Master | 9 or more | All levels, including Boss |

Clearing a complete difficulty level grants **+5 base ATK** and **+20 maximum HP**, together with a completion Gold reward. Unlocking the next level also provides a new standard equipment set.

### How to Progress

1. Travel to the next accessible room.
2. Add undefeated enemies from that room to your **Encounter Queue**.
3. Fight enemies in queue order until the room is cleared.
4. Open the room's treasure chest if one is available.
5. Purchase supplies, upgrade equipment, or rest when necessary.
6. Continue to the next room until you reach the boss and the final exit.

---

## 6. Combat and Challenge Questions

### Combat Basics

- **Attack:** Deals damage; normal attacks may miss or land critical hits.
- **Defend:** Reduces incoming damage and strengthens the next attack.
- **Health Potion:** Restores HP up to the player's maximum.
- **Other Item:** Uses a Strength Tonic, Paralysis Bomb, or Poison Dagger, if available.
- **Retreat:** Leaves the current fight without defeating the enemy. The enemy recovers its full HP and stays in the queue.

The boss becomes more dangerous when its HP falls below half.

### Challenge Questions

Each default enemy has **one assigned Data Structures question**. During battle, the player may attempt that enemy's Challenge.

- **Correct answer:** A guaranteed hit with additional damage for that attack.
- **Wrong answer:** No Challenge damage bonus; the turn is used.
- **Question bonuses:** Increase across the difficulty levels.
- **Gold:** Challenge questions do **not** award Gold.

Each Challenge can be used once per encounter. The boss has its own final Challenge question.

---

## 7. Player Statistics, Items, and Equipment

### Starting Player Statistics

A new player begins with:

| Attribute | Starting Value |
|---|---:|
| HP / Max HP | 100 / 100 |
| Base ATK | 14 |
| Gold | 60 |
| Health Potions | 1 |
| Rank | Beginner |

The player's equipment also affects combat statistics:

| Statistic | Meaning |
|---|---|
| **HP** | Current health points. |
| **ATK** | Attack power, including applicable weapon bonuses. |
| **SPD** | Weapon speed bonus affecting attack accuracy and critical-hit chance. |
| **DEF** | Armor-based reduction of incoming damage. |
| **BLOCK** | Shield-based percentage of damage blocked. |
| **Gold** | Currency for items, equipment, and resting. |
| **Score** | Points gained through victories, treasure, and completion. |

### Usable Items

| Item | Default Effect | Price |
|---|---|---:|
| Health Potion | Restores 35% of Max HP | 30 Gold |
| Strength Tonic | +50% damage for the next 3 attacks | 70 Gold |
| Paralysis Bomb | 75% chance to prevent enemy action for 2 turns | 110 Gold |
| Poison Dagger | A direct attack that does not miss | 120 Gold |

Available items, prices, and effects can be inspected in the game and are stored in the item records.

### Equipment by Level

Each unlocked level has a free sword, shield, and armor set. The shop offers optional upgrades suitable for the active level.

| Level | Sword | Shield | Armor |
|---|---|---|---|
| Weak | Rusty Sword | Wooden Shield | Cloth Armor |
| Intermediate | Bloodstone Sword | Iron Shield | Chainmail Armor |
| Strong | Steel Sword | Steel Shield | Steel Armor |
| Boss | Darksteel Sword | Darksteel Shield | Darksteel Armor |

Previously purchased gear remains owned, even after progressing to a stronger equipment tier.

### Camp, Treasure, and Rewards

- **Rest at Camp:** Costs **40 Gold** and restores HP based on **50% of Max HP**, without exceeding maximum health.
- **Treasure Chests:** Become available after clearing their corresponding fighting room. Each chest can be opened once per player.
- **Enemy Rewards:** Victories award Gold and Score according to each enemy's records.
- **Level Rewards:** Clearing a level improves the player's stats and awards additional Gold.

---

## 8. Victory, Defeat, and Saved Progress

### Winning the Adventure

Defeating Vharok breaks the curse sealing the Last Gate, but **the victory sequence is not finished until the player reaches the exit**.

To complete the game:

1. Defeat **Vharok, the World Eater**, in the **Throne of Ruin**.
2. Select **Travel to Room** and move to **The Last Gate**.
3. Accept the prompt to step through the exit, or select **`[17] Escape Dungeon`** while standing at the gate.
4. Read the final story scene and completion message.

The ending connects to the beginning of the adventure: the player returns to the world outside the game, the mysterious chest closes, and its voice falls silent.

> **YOU FOUND ME. YOU DEFEATED ME. YOU ARE FREE.**

Completing the escape awards **500 Score**, records the player's status as **Victorious**, saves the result, and returns the player to the **main login screen**.

### After Winning

When a victorious player signs in again, the game recognizes the completed journey. The Player Menu offers **View Completed Journey**, where the ending and final score can be viewed. It does not automatically restart the adventure.

### Losing a Battle

If HP reaches zero during combat:

- The battle ends in **Defeat**.
- The player loses **25% of their current Gold**.
- The player returns to the **Dungeon Entrance** with **50% of Max HP**.
- The **Encounter Queue is cleared**.
- The enemy regains some HP but may remain wounded.
- Completed levels, defeated enemies, owned equipment, and other saved progress remain available.

The player can recover, prepare, and continue the journey.

### Saving and Leaving

- **`[15] Save Game`:** Records the current game state and a readable game snapshot.
- **`[16] Save & Exit`:** Saves the player's progress and leaves the dungeon for the Player Menu.
- **`[0] Logout`** on the Player Menu: Saves progress and returns to the login screen.

---

## 9. Data Structures in the Game

The game demonstrates data structures using actual battles, actions, and rooms.

| Data Structure | In-Game Use | Operations |
|---|---|---|
| **Queue (FIFO)** | Enemy encounter lineup | Enqueue, view front/rear, dequeue, handle empty queue |
| **Action History Stack (LIFO)** | Chronological record of recent actions | Push, view top, display, remove latest log entry |
| **Undo Stack (LIFO)** | Snapshots of eligible player actions | Push before an action; pop to restore the previous state |
| **Graph** | Dungeon rooms and labeled passages | Represent connections, validate travel, find BFS routes, perform DFS traversal |

### Encounter Queue

Enemies are added in the order chosen by the player. The enemy at the **front** is fought first. After victory, that enemy is **dequeued**. Retreating leaves the enemy in the queue for another attempt.

### Action History and Undo

The **Action History Stack** records events with the newest entry at the top. The separate **Undo Stack** restores the latest reversible action, such as eligible combat, item, equipment, purchase, or rest actions. Completed victories, defeats, retreats, and travel cannot be undone.

Removing an entry from the action log is different from undoing the original gameplay action.

### Dungeon Graph

Rooms are **vertices**; passages are **edges**. The player can view connected rooms, search for a route using **Breadth-First Search (BFS)**, and display an exploration order using **Depth-First Search (DFS)**. The map and routes use the game's stored room and passage records.

---

## 10. Administrator Guide

An Administrator account opens the management interface instead of the adventure menu.

### Main Administrator Menu

| Option | Section | Purpose |
|---|---|---|
| `[1]` | Dashboard | View game and account summaries. |
| `[2]` | Profiling (File Maintenance) | Manage player, enemy, item, equipment, room, passage, and question records. |
| `[3]` | Transactions (Game Setup and Management) | View progress, manage selected game data, and review battle history. |
| `[4]` | Report Generation | Display and export reports built from game records. |
| `[0]` | Logout | Return to the login screen. |

### Profiling

The Profiling section supports maintaining the game's records, including adding, viewing, searching, updating, and deleting records where permitted. Record IDs and relationships must be valid.

### Transactions

| Option | Operation |
|---|---|
| `[1]` | View Player Progress |
| `[2]` | Reset Player Game Data |
| `[3]` | Assign Starting Items |
| `[4]` | Set Enemy Difficulty |
| `[5]` | View Battle History |
| `[0]` | Back |

### Available Reports

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

Reports are generated from actual stored records. After viewing a report, the administrator may export it to a text file in the **`reports/`** folder.

---

## 11. Game Files and Data Storage

### Project File Structure

```text
Dreadveil-Project/
├── Dreadveil_The_Last_Gate_Final_Escape_Outro.py
├── README.md
├── 1player_accounts.txt
├── 2enemy_records.txt
├── 3item_records.txt
├── 4equipment_records.txt
├── 5room_records.txt
├── 6room_connections.txt
├── 7question_records.txt
├── 8battle_history_records.txt
├── 9battle_activity_log.txt
├── 10dungeon_game_records.txt
└── reports/                     (created when reports are exported)
```

### Record File Reference

| Filename | Purpose |
|---|---|
| `1player_accounts.txt` | Account credentials, status, health, Gold, score, victories, inventory, equipment, queue, location, and saved progress. |
| `2enemy_records.txt` | Enemy names, difficulty, HP, ATK, rewards, and room assignments. |
| `3item_records.txt` | Item effects, power, prices, descriptions, and carry limits. |
| `4equipment_records.txt` | Equipment IDs, names, slots, tiers, bonuses, prices, and speed. |
| `5room_records.txt` | Room IDs, names, and descriptions. |
| `6room_connections.txt` | Labeled connections between dungeon rooms. |
| `7question_records.txt` | Battle Challenge questions and their enemy assignments. |
| `8battle_history_records.txt` | Saved results of battles, retreats, defeats, and dungeon escape. |
| `9battle_activity_log.txt` | Readable action-history snapshot. |
| `10dungeon_game_records.txt` | Readable snapshot of the active player's saved-game information. |

### Saving Data Safely

- Keep the program and its numbered record files together.
- Back up the record files before testing record maintenance or reset operations.
- Avoid renaming the numbered files; the filenames are referenced by the program.
- Some missing files may be recreated using default records, so do not remove save files when trying to resume an existing game.

---

## 12. Troubleshooting

| Problem | What to Do |
|---|---|
| Python cannot find the game file. | Open the terminal in the correct project folder and check the `.py` filename. |
| Saved progress seems missing. | Verify that the program is using the correct `1player_accounts.txt` in the current working folder. |
| An enemy cannot be added to the queue. | Check that the enemy is undefeated, belongs to the current room, and is available at your progress level. |
| The next room is sealed. | Defeat the required enemies in the current area before traveling forward. |
| The queue is empty. | Add an eligible enemy before selecting **Start Battle**. |
| An item or upgrade cannot be purchased. | Check the Gold cost, inventory carrying limit, and equipment tier. |
| A treasure chest will not open. | Clear every enemy in its room; each chest can only be opened once. |
| Undo is unavailable. | Check that a reversible action exists on the Undo Stack. Major battle outcomes and travel cannot be undone. |
| `[17] Escape Dungeon` does not finish the game. | Defeat Vharok first, then travel to **The Last Gate** and select the escape action. |
| An already victorious account cannot enter a new run. | The completed account displays **View Completed Journey** instead of starting another adventure. |
| The tables look crowded. | Widen the terminal window or reduce the console font size. |

---

**Dreadveil: The Last Gate**  
*Enter the darkness. Conquer the depths. Reclaim your freedom.*
