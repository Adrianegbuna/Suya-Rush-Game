# 🍢 SUYA RUSH - Nigerian Street-Food Simulator

A complete, fast-paced restaurant simulation game built with Python and Pygame.

## 🎮 How to Run

```bash
# Install Pygame (if not already installed)
pip install pygame

# Run the game
python suya_rush.py
```

## 📁 Project Structure

```
suya_rush/
├── suya_rush.py      # Complete game (all classes in one file)
└── high_scores.json  # Auto-generated high scores file
```

## 🎯 Gameplay

You run a **Suya Stand** — a traditional Nigerian street-food grill serving spiced meat skewers!

### Controls

| Key/Button | Action |
|-----------|--------|
| **Mouse** | Click buttons to interact |
| **1-4** | Serve that many suya sticks to the first customer |
| **SPACE** | Add new suya to the grill |
| **D** | Discard burned suya |
| **P** | Pause/Resume game |

### Game Flow

1. **Customers arrive** with orders (1-4 sticks of suya)
2. **Add suya** to the grill and wait for it to cook
3. **Watch the green progress bar** — don't let it burn!
4. **Serve the correct quantity** before patience runs out
5. **Build combos** for consecutive correct orders
6. **Earn money** to buy upgrades in the shop

## 🏗️ Architecture

### Classes

| Class | Description |
|-------|-------------|
| `Game` | Main game loop, state management, scoring |
| `Customer` | Customer AI with patience, orders, animations |
| `Grill` | Multi-slot cooking system with burn mechanics |
| `SuyaStick` | Individual suya with cooking state machine |
| `OrderManager` | Customer queue and order fulfillment |
| `UIManager` | All UI rendering (menus, HUD, shop) |
| `ParticleSystem` | Visual effects (smoke, success/fail particles) |

### Enums

- `GameState` — MENU, PLAYING, PAUSED, GAME_OVER, INSTRUCTIONS, SHOP
- `SuyaState` — RAW, COOKING, COOKED, BURNED
- `CustomerState` — WAITING, SERVED, ANGRY, LEAVING

## ✨ Features

### Core Gameplay
- ✅ Customer queue system with random orders
- ✅ Patience meter that decreases over time
- ✅ Multi-slot grill with cooking progress bars
- ✅ Burn mechanics (suya turns black if overcooked)
- ✅ Correct/incorrect order feedback
- ✅ Angry customers who leave if waited too long

### Progression
- ✅ **Level system** — customers arrive faster, orders get larger
- ✅ **Combo system** — consecutive correct orders give bonus points
- ✅ **Special customers** (★) who pay double
- ✅ **Lives/Satisfaction** system — 5 chances before game over

### Shop & Upgrades
- ✅ **Faster Grill** — Cook 25% faster per level
- ✅ **More Patience** — Customers wait 2s longer per level
- ✅ **Extra Grill Slot** — Cook one more suya at once
- ✅ **Higher Profits** — Earn 20% more money per level

### UI & Visuals
- ✅ Main menu with high scores display
- ✅ Instructions screen
- ✅ In-game HUD (score, money, level, combo, lives)
- ✅ Speech bubbles with orders
- ✅ Patience bars above customers
- ✅ Particle effects (smoke, success stars, failure sparks)
- ✅ Animated customers (bounce while waiting, leave when angry)
- ✅ Fire effects under grill
- ✅ Nigerian market background with stalls

### Data Persistence
- ✅ Local high score leaderboard (JSON file)
- ✅ Upgrade purchases persist between games
- ✅ Daily objectives tracking

### Input
- ✅ Full mouse control
- ✅ Keyboard shortcuts (1-4, SPACE, D, P)
- ✅ Button hover effects

## 🎨 Visual Design

The game uses a **vibrant Nigerian street-food theme**:
- Warm wood tones for the stand
- Fiery orange/yellow grill flames
- Rich brown suya meat that darkens as it cooks
- Colorful customer shirts
- Gold accents for score and special customers

All graphics are **procedurally drawn with Pygame** — no external image files needed!

## 🔊 Sound (Placeholder System)

The game includes a sound system placeholder. To add sounds:
1. Place `.wav` or `.ogg` files in an `assets/sounds/` folder
2. Update the sound loading code in the `Game` class

Suggested sounds:
- Grill sizzling
- Customer arrival bell
- Success "cha-ching"
- Failure buzzer
- Background market ambience

## 🏆 Scoring

| Action | Points |
|--------|--------|
| Serve correct order | 100 × quantity |
| Patience bonus | Up to +50 |
| Special customer | 2× multiplier |
| Combo x2 | +20 bonus |
| Combo x3 | +50 bonus |
| Combo x4 | +100 bonus |
| Combo x5+ | +200 bonus |
| Wrong order | -50 |

## 📜 License

Created as a complete Pygame project example. Feel free to modify and expand!

---
**Enjoy your Suya Rush! 🇳🇬🔥**
