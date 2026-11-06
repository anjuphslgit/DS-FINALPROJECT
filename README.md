# Dreadveil: The Last Gate

**A text-based fantasy dungeon adventure**  
**Data Structures Laboratory | Python Console Game | Final Project**

> **Enter the darkness. Conquer the guardians. Break the curse. Reach the Last Gate.**

## About the Game

**Dreadveil: The Last Gate** is a single-player, menu-driven Python dungeon RPG. The player explores connected rooms, battles guardians, manages Gold, health, consumables and equipment, and escapes after defeating **Vharok, the World Eater**.

It integrates three required data structures into actual game operations:

- **Queue (FIFO)** — the Encounter Queue decides which eligible enemy is fought first.
- **Stack (LIFO)** — the Player Action Stack saves reversible snapshots and supports TOP/PEEK and POP/Undo.
- **Graph** — the dungeon consists of room vertices and labeled, two-way passage edges, with BFS and DFS traversal.

The same application includes player accounts, an Administrator interface with the professor's **four required functional sections**, transaction history, record files and **11 reports**.

---

## 1. The Story

You accept the challenge. Suddenly, the screen goes dark and the world around you disappears. When you awaken, you are no longer sitting in front of your computer. You are trapped inside **Dreadveil**, a cursed dungeon where monsters guard every passage.

At the heart of the dungeon waits **Vharok, the World Eater**—the source of the voice and the power holding the **Last Gate** shut. To return home, you must defeat the dungeon's guardians, grow stronger, confront Vharok at the **Throne of Ruin**, and finally cross the Last Gate.


### Your Mission

1. Explore the dungeon and unlock new rooms.
2. Put eligible enemies in the Encounter Queue and fight them in FIFO order.
3. Survive battles using attacks, defenses, potions, items and challenge questions.
4. Earn Gold, improve gear and collect one-time treasures.
5. Defeat Vharok, walk through the final gate, and return home.

Defeating the final boss opens the way out, but the adventure is completed only when the player **steps through the Last Gate**.

---

## Requirements and Installation


### Run the Program

Extract the project files together, then open a terminal **inside that folder**:

```bash
python DS_FinalProject_MercadoRBanaybanayJBariteJDomingoJGonzalesA.py
```


---

## Starting the Game

### Main Login Screen

```text
[1] Login
[2] Create New Account
[0] Exit Game
```

### Demonstration Accounts

| Role | Username | Password |
|---|---|---|
| Administrator | `admin` | `admin123` |
| Player | `player` | `player123` |

Use these for local demonstrations only. Passwords are stored in readable local records for this class prototype, not a production authentication system.

### Player Menu

```text
[1] Enter Dungeon / View Completed Journey
[2] View Player Statistics
[3] Dungeon Map and Routes
[4] Enemy Information
[5] How to Play
[0] Logout
```

The completed-journey label depends on whether the account has already achieved victory. Logging in loads the saved character, inventory, equipped choices, room, Queue and eligible Undo state.

---

## Game Menus and Controls

### Dungeon / Expedition Camp Menu

```text
EXPLORE AND BATTLE
[1] Start Battle          [2] Add Enemy to Queue    [3] View Queue
[4] View Next Enemy       [5] Travel to Room        [6] Open Treasure Chest

CAMP
[7] Dungeon Shop          [8] Equipment             [9] Rest
[10] Inventory            [11] Dungeon Map

RECORDS
[12] Player Stats         [13] Player Action Stack  [14] Undo Action
[15] Save & Exit          [16] Escape Dungeon
```

The program displays the player's HP, total ATK, speed, defense, block, Gold, location, objective, Queue, Undo Stack and autosave feedback. Values are calculated from real player state.

### Battle Menu

```text
[1] Attack                [2] Defend                 [3] Health Potion
[4] Other Item            [5] Challenge              [6] Stats
[7] View Queue            [8] Player Action Stack    [9] Undo Action
[10] Retreat
```

### Player Action Stack Menu

```text
PLAYER ACTION STACK
Available Undo Actions:

[1] View Battle Actions
[2] View Latest Action
[3] Undo Latest Action

[0] Back
```

There is **no option [4]**. Option [1] displays eligible Undo snapshots, option [2] shows TOP/PEEK, and option [3] POPs the most recent eligible state after confirmation. The complete permanent activity audit is available through the Administrator's Transactions menu, not through this player Stack menu.

---

## Dungeon Map and Progression

### The Six-Room Dungeon

```text
[ROOM-000]              [ROOM-001]             [ROOM-002]
Dungeon Entrance  <-->  Rotting Sewers   <-->  Bloodstone Hall
       Rusted Grate                 Crimson Gate

[ROOM-002]               [ROOM-003]             [ROOM-004]             [ROOM-005]
Bloodstone Hall   <-->   War-Torn Catacombs <--> Throne of Ruin <--> The Last Gate
        Iron Drawbridge               Throne Gate            Sealed Exit Door
```

Passages are stored as graph edges, but room access still depends on gameplay progress. Additional valid Admin-created passages must not bypass progression rules.

| Room ID | Location | Purpose | Enemies |
|---|---|---|---:|
| `ROOM-000` | Dungeon Entrance | Starting point | 0 |
| `ROOM-001` | Rotting Sewers | Weak difficulty | 3 |
| `ROOM-002` | Bloodstone Hall | Intermediate difficulty | 3 |
| `ROOM-003` | War-Torn Catacombs | Strong difficulty | 3 |
| `ROOM-004` | Throne of Ruin | Boss confrontation | 1 |
| `ROOM-005` | The Last Gate | Final escape | 0 |

### Ranks and Access

| Rank | Wins | Progression |
|---|---:|---|
| Beginner | 0–2 | Weak |
| Adventurer | 3–5 | Intermediate |
| Elite | 6–8 | Strong |
| Master | 9+ | Boss |

Clearing all enemies of Weak, Intermediate or Strong difficulty awards **+5 Base ATK**, **+20 Max HP**, and a completion Gold bonus of **40 / 80 / 150**, respectively. The next free standard equipment tier becomes available. Boss defeat does not itself complete the game: the player must reach the exit.

---

## Combat and Challenge Questions

### Combat Actions

- **Attack:** uses total ATK, random damage spread and miss/critical-hit calculations.
- **Defend:** reduces incoming damage and can boost the next counterattack.
- **Health Potion:** restores health, limited by Max HP and owned quantity.
- **Other Item:** Strength Tonic, Paralysis Bomb or Poison Dagger, subject to stock and effects.
- **Challenge:** a correct answer adds bonus attack damage. Normal questions are drawn from the enemy's difficulty pool; Vharok uses fixed boss question `QST-010`.
- **Retreat:** ends an encounter without victory rewards and keeps its permanent outcome record.

**Normal damage:** the base calculation starts from Total ATK (Base ATK + currently equipped sword bonus), with a random spread of **±3** before relevant effects and any enemy mitigation. For example, Base ATK 14 + starter Rusty Sword 2 gives **16 displayed ATK**; an intentionally unequipped sword shows **14 ATK**.

Challenge answers do not directly grant Gold; they influence battle damage.

---

## Player Statistics, Items and Equipment

### Starting Player Statistics

| Stat | Starting value |
|---|---:|
| HP / Max HP | 100 / 100 |
| **Base ATK (saved in accounts TXT)** | 14 |
| Gold | 60 |
| Score | 0 |
| Wins / Losses | 0 / 0 |
| Starting Item | 1 Health Potion |
| Starting Room | Dungeon Entrance |

The player screen shows **Total ATK** after equipped sword bonuses; the accounts TXT stores **Base ATK** to avoid double-counting gear.

### Dungeon Shop — Items and Maximum Carry Quantity

| ID | Item | Price (Gold) | Maximum carried | Main effect |
|---|---|---:|---:|---|
| `ITM-001` | Health Potion | 30 | **10** | Restores 35% of Max HP |
| `ITM-002` | Strength Tonic | 70 | **5** | +50% damage for 3 attacks |
| `ITM-003` | Paralysis Bomb | 110 | **5** | Chance to stun an enemy |
| `ITM-004` | Poison Dagger | 120 | **5** | Direct damage that does not miss |

The shop's `Owned/Max` column combines **Owned** from the player's saved inventory in `1player_accounts.txt` and **Max** from item catalog `3item_records.txt`.

The program recognizes the **original unedited legacy item caps** (`5 / 3 / 2 / 2`) and upgrades them to **`10 / 5 / 5 / 5`** when loading that specific catalog. It does **not** overwrite custom Admin values. If the shop still shows old caps, check that you are running the latest Python source and that its `3item_records.txt` is writable.

**Professor requirement note:** These numbers are carrying limits, not different item profiles. There are **four** default consumable item records; the earlier Midterm handout asks for at least **five valid records in each applicable Profiling module**. The group must confirm the approved scope or add and test a genuine fifth item before claiming strict compliance.

### Equipment Tiers and Native IDs

Each tier provides a free standard Sword, Shield and Armor. The shop sells optional tier-appropriate upgrades, with `+1` and `+2` choices.

| Tier | Sword +1 / +2 | Shield +1 / +2 | Armor +1 / +2 |
|---|---|---|---|
| Weak | `EQP-001` / `EQP-002` | `EQP-003` / `EQP-004` | `EQP-005` / `EQP-006` |
| Intermediate | `EQP-007` / `EQP-008` | `EQP-009` / `EQP-010` | `EQP-011` / `EQP-012` |
| Strong | `EQP-013` / `EQP-014` | `EQP-015` / `EQP-016` | `EQP-017` / `EQP-018` |
| Boss | `EQP-019` / `EQP-020` | `EQP-021` / `EQP-022` | `EQP-023` / `EQP-024` |


### Equip, Unequip and Save

Players may choose the free standard piece, an owned available shop upgrade, or deliberately equip nothing in **each individual slot**:

```text
[No Sword]    -> Sword bonus = 0
[No Shield]   -> Shield block bonus = 0
[No Armor]    -> Armor defense bonus = 0
```

For deliberately empty slots, the saved account's `equipped` field uses the literal `NONE` (for example, `sword=NONE;shield=NONE;armor=NONE`). `NONE` is a slot state, **not** an additional Equipment catalog ID. Choices survive save/reload and are included in eligible Undo snapshots. Equipment changes are not allowed during an active battle.

To re-equip, select that slot again in the Equipment menu. Free gear remains free, and previously purchased equipment remains owned.

### Camp and Treasure

- **Rest:** costs 40 Gold, heals up to 50% of Max HP and never exceeds Max HP.
- **Treasure:** each eligible room has a once-per-player chest, unlocked after clearing the room.
- **Rewards:** defeated enemies award the Gold/Score from their profile, and level-clearing awards are separate.

---

## Victory, Defeat and Saved Progress

### Winning

1. Defeat Vharok in `ROOM-004`.
2. Travel to `ROOM-005` (The Last Gate).
3. Select **[16] Escape Dungeon**.
4. Receive the ending, the one-time **+500 Score** bonus, and a saved `Victorious` status.

### Losing a Battle

- The player receives a **25% Gold penalty**.
- The Losses count increases; the player revives with **50% of Max HP** at the Entrance.
- Existing completed levels, defeated-enemy progress and purchased equipment are preserved.

### Saving and Undo Limits

Progress is saved through the applicable game operations, not by an extra redundant Save Game menu item. **[15] Save & Exit** leaves the dungeon and preserves progress. An unsuccessful file write should be reported as such, not as a completed save.

Player Undo and Admin Undo All apply only to currently valid **pending reversible action snapshots**. Completed battles, recorded permanent rewards and a finished final escape are not arbitrarily rolled back.

---

## Data Structures in the Game

### Queue — First-In, First-Out (FIFO)

```text
FRONT -> [Enemy A] -> [Enemy B] -> [Enemy C] <- REAR
DEQUEUE removes Enemy A.
ENQUEUE adds a new eligible enemy at REAR.
```

The game supports Enqueue, Dequeue, FRONT, REAR, queue DISPLAY and EMPTY handling, with the waiting lineup saved under the player record.

### Stack — Last-In, First-Out (LIFO)

```text
        TOP -> [Action C: Attack]
               [Action B: Rest]
        BASE   [Action A: Shop Purchase]

POP (Undo) restores Action C's pre-action snapshot.
NEXT TOP becomes Action B.
```

Before an eligible action, the game **PUSHes** a reversible snapshot. The Player Action Stack displays eligible items, **PEEKs** at the top, and **POPs** on Undo. It also shows `EMPTY` when no actions are available. The full activity history is separately available to Admin.

### Graph — Vertices, Edges, BFS and DFS

- Six stored room vertices in `5room_records.txt`.
- Labeled, bidirectional passage edges in `6room_connections.txt`.
- **BFS** finds a shortest unweighted route using actual stored connections.
- **DFS** gives a traversal order.
- Admin can add or remove permitted passages, subject to connection/progression validation.


---

## Administrator Guide

### Main Administrator Menu

```text
[1] Dashboard
[2] Profiling (File Maintenance)
[3] Transactions (Game Setup and Management)
[4] Report Generation
[0] Logout
```

The required functional sections are **Dashboard, Profiling, Transactions and Report Generation**. Back and Logout controls are navigation only.

### Profiling (File Maintenance)

Manage Player accounts, Enemies, Items, Equipment, fixed Room details and passages, and Challenge Questions. Available operations include Add, View, Search, Update and Delete **where supported**. The six base rooms are fixed, but Admin can maintain valid passage connections.

### Transactions

```text
[1] View Player Progress
[2] Reset Player Game Data
[3] Assign Starting Items
[4] Set Enemy Difficulty
[5] View Battle History
[6] View Complete Activity History
[7] Undo All Available Player Actions
[0] Back
```

Admin Undo All restores valid **pending** Undo snapshots for a selected player. It is **not** an unrestricted historical rollback of victories or final escape.

### Reports (11)

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

Reports use loaded game records and can be exported to the `reports/` folder. 

---

## Game Files and Data Storage

### Project File Structure

```text
Dreadveil_The_Last_Gate_Project/
├── DS_FinalProject_MercadoRBanaybanayJBariteJDomingoJGonzalesA.py
├── README.md                     <- this code-style guide
├── BLUEPRINT.md                  <- full final blueprint / rubric checklist
├── TEST_RESULTS.md
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
├── 11battle_session_records.json <- generated during play
└── reports/                      <- generated on report export
```

### Record File Reference

| File | What it stores |
|---|---|
| `1player_accounts.txt` | Username, role, base stats, Gold, Score, Wins/Losses, HP, inventory, queue, equipment/`NONE` slots, room and progression |
| `2enemy_records.txt` | Ten default enemies, difficulty, HP/ATK, reward values and assigned room |
| `3item_records.txt` | Four consumable types, effects, prices and **10/5/5/5** carry limits |
| `4equipment_records.txt` | 24 native sequential Equipment IDs, type, tier, bonuses, costs and speed |
| `5room_records.txt` | Six named rooms / graph vertices |
| `6room_connections.txt` | Named graph connections / edges |
| `7question_records.txt` | Difficulty-pool challenges, choices, answer and bonus damage |
| `8battle_history_records.txt` | Permanent completed encounter outcomes |
| `9battle_activity_log.txt` | Saved chronological activity history |
| `10dungeon_game_records.txt` | Human-readable latest active-player state snapshot |
| `11battle_session_records.json` | Per-player active battle and Undo snapshot data, created at runtime |

The JSON session system can produce a `.recovery.json` file if the primary file cannot be replaced. Preserve both when backing up the project.

### Important File Relationships

```text
Player.inventory[item_id]       -> 3item_records.txt
Player.owned_equipment[EQP-ID]  -> 4equipment_records.txt
Player.equipped[slot]           -> EQP-ID, standard free gear, or NONE
Player.encounter_queue          -> 2enemy_records.txt IDs
Enemy.room                      -> 5room_records.txt
Room connections                -> 5room_records.txt valid IDs
Undo snapshots                  -> player account and session state
```

**Important:** The program uses multiple local TXT and JSON files, not an ACID database. Although it checks writes and attempts coordinated saves, abrupt power loss or disk/file-lock errors still require backup/recovery checks. Do not claim crash-proof transactions.


---

## Troubleshooting

| Problem | What to check |
|---|---|
| Can't start the game | Python version, source filename, terminal working folder |
| Player progress looks lost | Confirm `1player_accounts.txt` is in the active working folder; don't mix old-ID saves |
| Shop shows `1/5` for potions | You may have an old `3item_records.txt`; run updated code in a writable folder or use fresh item TXT |
| Can't buy more items | Gold balance and `Owned/Max` carry-cap check |
| Can't equip an item | It may be unowned, outside current tier, or in an active battle |
| ATK shows 16 but TXT says 14 | 14 is Base ATK; 16 includes the starter sword's +2 bonus |
| Want no equipped bonuses | Equipment menu -> select No Sword, No Shield and/or No Armor |
| Undo is unavailable | No currently reversible snapshot or a committed result cannot be undone |
| Can't enter next room | Defeat the required guardians and satisfy the room lock |
| Save fails | Check file permissions, disk space and antivirus/other processes locking files |
| Exit unavailable | Defeat Vharok, reach The Last Gate and choose Escape Dungeon |

---

**Dreadveil: The Last Gate**  
*Enter the darkness. Conquer the depths. Reclaim your freedom.*