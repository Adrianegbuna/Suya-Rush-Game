"""
SUYA RUSH - A Nigerian Street-Food Restaurant Simulation Game
A fast-paced cooking and time-management game built with Pygame where players
manage a suya (grilled meat) stand, serving customers before their patience runs out.

Architecture Overview:
The game is organized into several cohesive modules that handle distinct responsibilities:

- main.py (this file): Contains the main entry point, the central Game class that
  orchestrates all systems, and all game constants, enums, utility functions, and
  supporting classes. This is the monolithic single-file implementation.

- customer.py (conceptual): The Customer class manages individual customer behavior
  including their visual appearance, patience timer, order quantity, entrance/exit
  animations, speech bubbles for orders, and satisfaction feedback.

- grill.py (conceptual): The Grill and SuyaStick classes handle the cooking mechanics,
  tracking cook progress, burn states, slot management, and visual representation of
  meat on the grill with progress indicators.

- order.py (conceptual): The OrderManager class controls customer spawning logic,
  queue management, level-based difficulty scaling, and the serving interaction that
  validates correct order quantities against available cooked suya.

- ui_manager.py (conceptual): The UIManager class renders all screen states including
  the main menu, instructions, shop/upgrades, in-game HUD, pause overlay, and game
  over screen. It also handles button creation, hover states, and click detection.

- assets/ (placeholder directory): Reserved for external image and audio resources.
  The game is fully functional using only programmatically drawn shapes and colors,
  so no external assets are strictly required.
"""

import pygame
import random
import json
import os
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen settings
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Colors (Nigerian street-food vibrant theme)
COLORS = {
    'bg_dark': (30, 20, 10),
    'bg_market': (45, 35, 20),
    'wood': (139, 90, 43),
    'wood_light': (160, 110, 60),
    'grill_metal': (80, 80, 80),
    'grill_hot': (200, 80, 30),
    'fire_orange': (255, 140, 0),
    'fire_yellow': (255, 215, 0),
    'suya_raw': (180, 130, 90),
    'suya_cooked': (139, 69, 19),
    'suya_burned': (40, 20, 10),
    'customer_skin': [ (210, 180, 140), (180, 140, 100), (240, 200, 160), (160, 120, 80) ],
    'shirt_colors': [ (255, 50, 50), (50, 150, 255), (50, 200, 50), (255, 200, 50), (200, 50, 200) ],
    'text_white': (255, 255, 255),
    'text_gold': (255, 215, 0),
    'text_green': (50, 255, 100),
    'text_red': (255, 80, 80),
    'patience_green': (50, 255, 100),
    'patience_yellow': (255, 255, 0),
    'patience_red': (255, 50, 50),
    'bubble_white': (255, 255, 255),
    'ui_panel': (60, 45, 30, 220),
    'button_normal': (180, 120, 50),
    'button_hover': (220, 160, 70),
    'button_pressed': (140, 90, 30),
    'combo_glow': (255, 215, 0, 100),
}

# Game balance constants
INITIAL_PATIENCE = 15.0  # seconds
MIN_PATIENCE = 5.0
COOK_TIME = 4.0  # seconds to cook suya
BURN_TIME = 8.0  # seconds until burned
CUSTOMER_SPAWN_BASE = 4.0  # base spawn interval
MONEY_PER_SUYA = 50
COMBO_BONUS = [0, 0, 20, 50, 100, 200]  # bonus at combo levels
SPECIAL_CUSTOMER_CHANCE = 0.15
SPECIAL_MULTIPLIER = 2.0


class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    INSTRUCTIONS = "instructions"
    SHOP = "shop"

class SuyaState(Enum):
    RAW = "raw"
    COOKING = "cooking"
    COOKED = "cooked"
    BURNED = "burned"

class CustomerState(Enum):
    WAITING = "waiting"
    SERVED = "served"
    ANGRY = "angry"
    LEAVING = "leaving"

# UTILITY FUNCTIONS
#
# Standalone helper functions that are used across multiple classes.
# These handle common rendering tasks (rounded rectangles, shadowed text),
# and persistent data operations (loading and saving high-score records
# to a local JSON file). Keeping these as module-level functions avoids
# code duplication and keeps class definitions focused on their primary responsibilities.
#

def draw_rounded_rect(surface, color, rect, radius=10):
    """Render a rectangle with rounded corners on the given surface.
    
    Wraps pygame.draw.rect with the border_radius parameter to provide a
    consistent visual style for UI panels, buttons, and game objects throughout
    the interface. The radius parameter controls the curvature of the corners.
    """
    pygame.draw.rect(surface, color, rect, border_radius=radius)

def draw_text(surface, text, font, color, pos, center=True, shadow=True):
    """Render text onto a surface with an optional drop shadow for readability.
    
    When shadow is enabled, a black offset copy of the text is drawn first,
    creating depth that helps text stand out against busy backgrounds. The
    center flag determines whether pos is treated as the center point or the
    top-left corner of the text bounding box. Returns the text's Rect for
    potential collision or positioning calculations by the caller.
    """
    if shadow:
        shadow_surf = font.render(text, True, (0, 0, 0))
        offset = 2
        if center:
            shadow_rect = shadow_surf.get_rect(center=(pos[0] + offset, pos[1] + offset))
        else:
            shadow_rect = shadow_surf.get_rect(topleft=(pos[0] + offset, pos[1] + offset))
        surface.blit(shadow_surf, shadow_rect)

    text_surf = font.render(text, True, color)
    if center:
        text_rect = text_surf.get_rect(center=pos)
    else:
        text_rect = text_surf.get_rect(topleft=pos)
    surface.blit(text_surf, text_rect)
    return text_rect

def load_high_scores() -> List[Dict]:
    """Retrieve the persisted high-score leaderboard from local disk.
    
    Attempts to open and parse high_scores.json. If the file does not exist,
    is empty, or contains malformed JSON, returns an empty list rather than
    crashing, ensuring the game can always present a fresh leaderboard.
    """
    try:
        with open('high_scores.json', 'r') as f:
            return json.load(f)
    except:
        return []

def save_high_scores(scores: List[Dict]):
    """Persist the current high-score leaderboard to local disk.
    
    Serializes the provided list of score dictionaries into JSON format and
    writes them to high_scores.json. This is called whenever a game ends and
    the player's result needs to be recorded for future sessions.
    """
    with open('high_scores.json', 'w') as f:
        json.dump(scores, f)

# SUYA STICK CLASS
#
# Represents a single piece of suya meat mounted on a skewer stick and placed
# on a specific grill slot. Each instance independently tracks its own cooking
# state (raw -> cooking -> cooked -> burned), elapsed cook and burn timers,
# visual position on screen, and whether it is currently selected by the player.
# The class encapsulates all per-stick logic including state transitions,
# color interpolation during cooking, and self-rendering.
#

class SuyaStick:
    """Represents a single stick of suya on the grill."""

    def __init__(self, slot_index: int):
        self.slot_index = slot_index
        self.state = SuyaState.RAW
        self.cook_timer = 0.0
        self.burn_timer = 0.0
        self.x = 300 + slot_index * 90
        self.y = 450
        self.width = 70
        self.height = 20
        self.selected = False

    def update(self, dt: float, cook_speed: float = 1.0):
        """Advance the cooking simulation for this suya stick by one frame.
        
        If the stick is in the COOKING state, increments the cook_timer by the
        elapsed delta time scaled by cook_speed. Once cook_timer reaches COOK_TIME,
        the state transitions to COOKED. Independently, the burn_timer increments
        whenever the stick is COOKING or COOKED; reaching BURN_TIME transitions
        the state to BURNED, making the stick inedible until discarded.
        """
        if self.state == SuyaState.COOKING:
            self.cook_timer += dt * cook_speed
            if self.cook_timer >= COOK_TIME:
                self.state = SuyaState.COOKED
                self.cook_timer = COOK_TIME

        if self.state in [SuyaState.COOKING, SuyaState.COOKED]:
            self.burn_timer += dt * cook_speed
            if self.burn_timer >= BURN_TIME:
                self.state = SuyaState.BURNED

    def start_cooking(self):
        """Initiate the cooking process for this suya stick.
        
        Only has an effect when the stick is in the RAW state, transitioning
        it to COOKING. This is typically called immediately after the stick is
        placed on the grill so that it begins progressing toward the cooked state.
        """
        if self.state == SuyaState.RAW:
            self.state = SuyaState.COOKING

    def is_ready(self) -> bool:
        """Determine whether this suya stick has reached the perfectly cooked state.
        
        Returns True only if the internal state equals COOKED, indicating the stick
        is safe to remove from the grill and serve to a customer.
        """
        return self.state == SuyaState.COOKED

    def is_burned(self) -> bool:
        """Determine whether this suya stick has been left on the grill too long.
        
        Returns True only if the internal state equals BURNED, meaning the stick
        is ruined, cannot be served, and should be discarded to free the grill slot.
        """
        return self.state == SuyaState.BURNED

    def discard(self):
        """Clear this grill slot by resetting the suya stick to its initial RAW state.
        
        Zeros out all timers and clears the selection flag, effectively making the
        slot empty and ready to receive a new piece of suya. Called when the player
        manually discards burned meat or when the game auto-clears burned sticks.
        """
        self.state = SuyaState.RAW
        self.cook_timer = 0.0
        self.burn_timer = 0.0
        self.selected = False

    def draw(self, surface):
        """Render this suya stick and all its associated visual indicators.
        
        Draws the meat rectangle with color interpolated between raw and cooked
        during the cooking phase, the metal skewer line through the center, a gold
        selection border if selected, a green progress bar above the stick while
        cooking, and a red BURNED label when overcooked.
        """
        # Draw stick
        stick_color = COLORS['suya_raw']
        if self.state == SuyaState.COOKING:
            # Interpolate color based on cook progress
            progress = self.cook_timer / COOK_TIME
            r = int(COLORS['suya_raw'][0] + (COLORS['suya_cooked'][0] - COLORS['suya_raw'][0]) * progress)
            g = int(COLORS['suya_raw'][1] + (COLORS['suya_cooked'][1] - COLORS['suya_raw'][1]) * progress)
            b = int(COLORS['suya_raw'][2] + (COLORS['suya_cooked'][2] - COLORS['suya_raw'][2]) * progress)
            stick_color = (r, g, b)
        elif self.state == SuyaState.COOKED:
            stick_color = COLORS['suya_cooked']
        elif self.state == SuyaState.BURNED:
            stick_color = COLORS['suya_burned']

        # Draw meat on stick
        meat_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        draw_rounded_rect(surface, stick_color, meat_rect, 5)

        # Draw skewer stick
        pygame.draw.line(surface, (200, 200, 200), 
                        (self.x + 5, self.y + self.height//2),
                        (self.x + self.width - 5, self.y + self.height//2), 3)

        # Draw selection highlight
        if self.selected:
            pygame.draw.rect(surface, COLORS['text_gold'], 
                           (self.x - 3, self.y - 3, self.width + 6, self.height + 6), 2, border_radius=5)

        # Draw progress bar for cooking
        if self.state == SuyaState.COOKING:
            bar_width = self.width
            progress = self.cook_timer / COOK_TIME
            fill_width = int(bar_width * progress)
            pygame.draw.rect(surface, (100, 100, 100), (self.x, self.y - 10, bar_width, 6))
            pygame.draw.rect(surface, COLORS['patience_green'], (self.x, self.y - 10, fill_width, 6))

        # Draw burned indicator
        if self.state == SuyaState.BURNED:
            draw_text(surface, "BURNED", pygame.font.SysFont('Arial', 14), 
                     COLORS['text_red'], (self.x + self.width//2, self.y - 15))

# GRILL CLASS
#
# Manages the entire cooking station as a collection of discrete slots, each
# capable of holding one SuyaStick. The Grill class is responsible for adding
# new suya to empty slots, querying how many sticks are ready to serve,
# removing cooked sticks when orders are fulfilled, clearing burned sticks,
# and applying global cook-speed modifiers from upgrades. It also renders the
# grill chassis, animated flame effects beneath the grates, and delegates
# drawing of individual suya sticks to their respective instances.
#

class Grill:
    """Manages the suya grill with multiple cooking slots."""

    def __init__(self, num_slots: int = 6):
        self.num_slots = num_slots
        self.slots: List[Optional[SuyaStick]] = [None] * num_slots
        self.cook_speed = 1.0
        self.max_slots = num_slots

        # Grill visual properties
        self.x = 250
        self.y = 420
        self.width = num_slots * 90 + 40
        self.height = 120

    def add_suya(self) -> bool:
        """Place a new raw suya stick onto the first available grill slot.
        
        Iterates through all slots in order; upon finding an empty one, instantiates
        a new SuyaStick, immediately starts its cooking timer, and returns True.
        If every slot is occupied, returns False so the caller knows the action failed.
        """
        for i in range(self.num_slots):
            if self.slots[i] is None:
                self.slots[i] = SuyaStick(i)
                self.slots[i].start_cooking()
                return True
        return False

    def get_ready_suya(self) -> int:
        """Count the number of suya sticks currently in the COOKED state.
        
        This value is displayed in the HUD and is checked before allowing the
        player to serve an order, ensuring they cannot promise more suya than
        is actually available on the grill.
        """
        return sum(1 for s in self.slots if s is not None and s.is_ready())

    def take_suya(self, quantity: int) -> int:
        """Remove up to the requested number of cooked suya sticks from the grill.
        
        Scans slots left-to-right, removing COOKED sticks until either the requested
        quantity is met or no more cooked sticks remain. Returns the actual count
        removed, which the caller compares against the requested quantity to verify
        sufficient supply before completing a serve action.
        """
        taken = 0
        for i in range(self.num_slots):
            if taken >= quantity:
                break
            if self.slots[i] is not None and self.slots[i].is_ready():
                self.slots[i] = None
                taken += 1
        return taken

    def discard_burned(self):
        """Clear every grill slot that contains a burned suya stick.
        
        Iterates through all slots and sets any BURNED stick to None, freeing
        those slots for new meat. This is triggered by the player clicking the
        DISCARD button or pressing the D key.
        """
        for i in range(self.num_slots):
            if self.slots[i] is not None and self.slots[i].is_burned():
                self.slots[i] = None

    def update(self, dt: float):
        """Advance the cooking simulation for every occupied grill slot.
        
        Delegates to each SuyaStick's own update method, passing the frame delta
        time and the global cook_speed multiplier so that upgrade effects apply
        uniformly across all sticks currently on the grill.
        """
        for slot in self.slots:
            if slot is not None:
                slot.update(dt, self.cook_speed)

    def draw(self, surface):
        """Render the complete grill assembly including base, grates, flames, and suya.
        
        Draws the metal grill body with rounded corners, vertical grate lines,
        animated flickering fire ellipses beneath the cooking surface, delegates
        individual suya rendering to each SuyaStick, and finally draws the GRILL label.
        """
        # Draw grill base
        grill_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        draw_rounded_rect(surface, COLORS['grill_metal'], grill_rect, 10)

        # Draw grill grates
        for i in range(self.num_slots + 1):
            x_pos = self.x + 20 + i * 90
            pygame.draw.line(surface, (60, 60, 60), 
                           (x_pos, self.y + 10), (x_pos, self.y + self.height - 10), 3)

        # Draw fire/glow effect under grill
        for i in range(5):
            offset = random.randint(-3, 3)
            flame_height = random.randint(15, 35)
            flame_color = random.choice([COLORS['fire_orange'], COLORS['fire_yellow']])
            pygame.draw.ellipse(surface, flame_color,
                              (self.x + 50 + i * 100 + offset, self.y + self.height - 5, 30, flame_height))

        # Draw suya sticks
        for slot in self.slots:
            if slot is not None:
                slot.draw(surface)

        # Draw grill label
        font = pygame.font.SysFont('Arial', 20, bold=True)
        draw_text(surface, "GRILL", font, COLORS['text_white'], 
                 (self.x + self.width//2, self.y - 20))

# CUSTOMER CLASS
#
# Models an individual customer who enters from the left, waits in queue,
# displays an order via a speech bubble, and eventually leaves either satisfied
# or angry. Each customer has randomized visual attributes (skin tone, shirt color,
# hairstyle), a procedurally generated order size that scales with game level,
# a patience timer that drains while waiting, and a special-customer flag that
# doubles rewards. The class handles all its own animation (entrance sliding,
# idle bouncing, angry arm raising, exit sliding), rendering, and feedback text.
#

class Customer:
    """Represents a customer with order and patience."""

    def __init__(self, customer_id: int, level: int = 1):
        self.id = customer_id
        self.state = CustomerState.WAITING

        # Random appearance
        self.skin_color = random.choice(COLORS['customer_skin'])
        self.shirt_color = random.choice(COLORS['shirt_colors'])
        self.hair_style = random.randint(0, 2)

        # Position
        self.x = -100
        self.target_x = 200
        self.y = 250
        self.width = 80
        self.height = 120

        # Order
        max_order = min(4, 1 + level // 3)
        self.order_quantity = random.randint(1, max_order)
        self.is_special = random.random() < SPECIAL_CUSTOMER_CHANCE

        # Patience
        patience_reduction = level * 0.5
        self.max_patience = max(INITIAL_PATIENCE - patience_reduction, MIN_PATIENCE)
        self.patience = self.max_patience

        # Animation
        self.arrived = False
        self.leave_speed = 200
        self.bounce_offset = 0
        self.bounce_timer = 0

        # Feedback
        self.feedback_text = ""
        self.feedback_timer = 0
        self.feedback_color = COLORS['text_white']

    def update(self, dt: float):
        """Advance this customer's animation, patience, and state machine by one frame.
        
        Handles four concurrent behaviors: (1) entrance sliding from off-screen left
        to the target queue position, (2) patience depletion while WAITING that
        transitions to ANGRY at zero, (3) exit sliding when SERVED or ANGRY,
        (4) a subtle bounce animation while idle in queue, and (5) feedback text fade-out.
        """
        # Entrance animation
        if not self.arrived:
            self.x += 300 * dt
            if self.x >= self.target_x:
                self.x = self.target_x
                self.arrived = True

        # Patience drain
        if self.state == CustomerState.WAITING and self.arrived:
            self.patience -= dt
            if self.patience <= 0:
                self.patience = 0
                self.state = CustomerState.ANGRY

        # Leaving animation
        if self.state in [CustomerState.SERVED, CustomerState.ANGRY]:
            self.x -= self.leave_speed * dt

        # Bounce animation while waiting
        if self.state == CustomerState.WAITING and self.arrived:
            self.bounce_timer += dt * 5
            self.bounce_offset = abs(int(5 * (1 if int(self.bounce_timer) % 2 == 0 else -1)))

        # Feedback timer
        if self.feedback_timer > 0:
            self.feedback_timer -= dt

    def serve(self, quantity: int) -> bool:
        """Validate a serving attempt against this customer's order.
        
        Compares the provided quantity with the customer's requested order_quantity.
        On a match, transitions the customer to SERVED, displays a positive YUM!
        feedback, and returns True. On a mismatch, displays a negative WRONG! feedback,
        applies a 3-second patience penalty, and returns False so the main game loop
        can handle the mistake consequences (combo break, life loss).
        """
        if quantity == self.order_quantity:
            self.state = CustomerState.SERVED
            self.feedback_text = "YUM!"
            self.feedback_color = COLORS['text_green']
            self.feedback_timer = 1.5
            return True
        else:
            self.feedback_text = "WRONG!"
            self.feedback_color = COLORS['text_red']
            self.feedback_timer = 1.5
            self.patience -= 3  # Penalty for wrong order
            return False

    def get_money(self) -> int:
        """Compute the monetary reward for successfully serving this customer.
        
        Base earnings equal order_quantity multiplied by MONEY_PER_SUYA.
        If this customer is a special customer (marked with a gold star), the
        base amount is doubled via SPECIAL_MULTIPLIER before returning.
        """
        base = self.order_quantity * MONEY_PER_SUYA
        if self.is_special:
            base = int(base * SPECIAL_MULTIPLIER)
        return base

    def get_score(self) -> int:
        """Compute the total score contribution for successfully serving this customer.
        
        Base score is order_quantity times 100, doubled for special customers.
        An additional patience bonus of up to 50 points is awarded based on
        the ratio of remaining patience to maximum patience, incentivizing quick service.
        """
        base = self.order_quantity * 100
        if self.is_special:
            base = int(base * SPECIAL_MULTIPLIER)
        # Bonus for remaining patience
        patience_bonus = int((self.patience / self.max_patience) * 50)
        return base + patience_bonus

    def is_off_screen(self) -> bool:
        """Determine whether this customer has animated fully off the visible screen area.
        
        Returns True if the customer's x position is beyond the left or right
        boundaries (with a 150-pixel buffer), signaling the OrderManager to remove
        this instance from the active customer list and free up queue space.
        """
        return self.x < -150 or self.x > SCREEN_WIDTH + 150

    def draw(self, surface):
        """Render the complete customer avatar and all associated UI overlays.
        
        Composes the character from primitive shapes: rounded shirt body, skin-toned
        head with animated eyes (angry slant when upset), mouth expression (smile,
        frown, or neutral), hairstyle variation (short hair, cap, or turban), arms
        positioned by emotional state, speech bubble with order details, patience
        meter, special-customer star, and floating feedback text.
        """
        y_pos = self.y + self.bounce_offset

        # Body (shirt)
        body_rect = pygame.Rect(self.x + 10, y_pos + 40, 60, 50)
        draw_rounded_rect(surface, self.shirt_color, body_rect, 5)

        # Head
        head_rect = pygame.Rect(self.x + 15, y_pos, 50, 50)
        draw_rounded_rect(surface, self.skin_color, head_rect, 15)

        # Eyes
        eye_color = (30, 20, 10)
        if self.state == CustomerState.ANGRY:
            # Angry eyes (slanted)
            pygame.draw.line(surface, eye_color, (self.x + 25, y_pos + 20), (self.x + 35, y_pos + 25), 3)
            pygame.draw.line(surface, eye_color, (self.x + 45, y_pos + 20), (self.x + 55, y_pos + 25), 3)
        else:
            pygame.draw.circle(surface, eye_color, (self.x + 30, y_pos + 25), 4)
            pygame.draw.circle(surface, eye_color, (self.x + 50, y_pos + 25), 4)

        # Mouth
        if self.state == CustomerState.SERVED:
            # Happy smile
            pygame.draw.arc(surface, (100, 50, 50), 
                          (self.x + 30, y_pos + 30, 20, 15), 0, 3.14, 2)
        elif self.state == CustomerState.ANGRY:
            # Frown
            pygame.draw.arc(surface, (100, 50, 50), 
                          (self.x + 30, y_pos + 35, 20, 15), 3.14, 0, 2)
        else:
            # Neutral
            pygame.draw.line(surface, (100, 50, 50), 
                           (self.x + 32, y_pos + 38), (self.x + 48, y_pos + 38), 2)

        # Hair
        if self.hair_style == 0:
            # Short hair
            pygame.draw.ellipse(surface, (20, 10, 5), 
                              (self.x + 10, y_pos - 10, 60, 25))
        elif self.hair_style == 1:
            # Cap
            pygame.draw.ellipse(surface, self.shirt_color, 
                              (self.x + 10, y_pos - 5, 60, 20))
            pygame.draw.rect(surface, self.shirt_color, 
                           (self.x + 10, y_pos + 5, 60, 10))
        else:
            # Turban/head wrap
            pygame.draw.ellipse(surface, (100, 80, 60), 
                              (self.x + 5, y_pos - 5, 70, 25))

        # Arms
        if self.state == CustomerState.WAITING:
            # Arms down/waiting
            pygame.draw.line(surface, self.skin_color, 
                           (self.x + 10, y_pos + 50), (self.x - 5, y_pos + 80), 6)
            pygame.draw.line(surface, self.skin_color, 
                           (self.x + 70, y_pos + 50), (self.x + 85, y_pos + 80), 6)
        elif self.state == CustomerState.ANGRY:
            # Arms raised in anger
            pygame.draw.line(surface, self.skin_color, 
                           (self.x + 10, y_pos + 50), (self.x - 10, y_pos + 20), 6)
            pygame.draw.line(surface, self.skin_color, 
                           (self.x + 70, y_pos + 50), (self.x + 90, y_pos + 20), 6)

        # Speech bubble with order
        if self.state == CustomerState.WAITING and self.arrived:
            self._draw_speech_bubble(surface, y_pos)

        # Patience bar
        if self.state == CustomerState.WAITING and self.arrived:
            self._draw_patience_bar(surface, y_pos)

        # Special customer indicator
        if self.is_special and self.state == CustomerState.WAITING:
            star_font = pygame.font.SysFont('Arial', 24, bold=True)
            draw_text(surface, "★", star_font, COLORS['text_gold'], 
                     (self.x + 40, y_pos - 30))

        # Feedback text
        if self.feedback_timer > 0:
            feedback_font = pygame.font.SysFont('Arial', 28, bold=True)
            draw_text(surface, self.feedback_text, feedback_font, self.feedback_color,
                     (self.x + 40, y_pos - 60))

    def _draw_speech_bubble(self, surface, y_pos):
        """Render a speech bubble to the right of the customer displaying their order.
        
        Draws a white rounded rectangle with a triangular tail pointing at the customer,
        a black border, the order text (e.g., "Suya x2"), and a SPECIAL! label in gold
        if this customer carries the special-customer flag. The y_pos parameter accounts
        for the idle bounce animation so the bubble tracks the customer vertically.
        """
        bubble_x = self.x + 90
        bubble_y = y_pos - 20
        bubble_w = 100
        bubble_h = 70

        # Bubble background
        bubble_rect = pygame.Rect(bubble_x, bubble_y, bubble_w, bubble_h)
        draw_rounded_rect(surface, COLORS['bubble_white'], bubble_rect, 10)
        pygame.draw.polygon(surface, COLORS['bubble_white'], 
                          [(bubble_x, bubble_y + 40), (bubble_x - 15, bubble_y + 50), (bubble_x, bubble_y + 55)])

        # Border
        pygame.draw.rect(surface, (0, 0, 0), bubble_rect, 2, border_radius=10)

        # Order text
        font = pygame.font.SysFont('Arial', 18, bold=True)
        draw_text(surface, f"Suya x{self.order_quantity}", font, (0, 0, 0), 
                 (bubble_x + bubble_w//2, bubble_y + 25))

        if self.is_special:
            special_font = pygame.font.SysFont('Arial', 14, bold=True)
            draw_text(surface, "SPECIAL!", special_font, COLORS['text_gold'], 
                     (bubble_x + bubble_w//2, bubble_y + 50))

    def _draw_patience_bar(self, surface, y_pos):
        """Render a horizontal patience gauge above the customer's head.
        
        Displays a gray background bar and a colored fill bar whose width shrinks
        as patience decreases. Color transitions from green (above 50%) to yellow
        (25-50%) to red (below 25%), giving the player an immediate visual warning
        of impending customer anger.
        """
        bar_x = self.x + 10
        bar_y = y_pos - 15
        bar_w = 60
        bar_h = 8

        # Background
        pygame.draw.rect(surface, (80, 80, 80), (bar_x, bar_y, bar_w, bar_h))

        # Fill
        patience_ratio = self.patience / self.max_patience
        fill_w = int(bar_w * patience_ratio)

        if patience_ratio > 0.5:
            color = COLORS['patience_green']
        elif patience_ratio > 0.25:
            color = COLORS['patience_yellow']
        else:
            color = COLORS['patience_red']

        if fill_w > 0:
            pygame.draw.rect(surface, color, (bar_x, bar_y, fill_w, bar_h))

# ORDER MANAGER
#
# Acts as the central queue and spawning controller for all customers.
# It maintains the live list of Customer instances, periodically spawns new
# customers based on a level-adjusted interval (faster spawns at higher levels),
# cleans up customers who have moved off-screen, and mediates the serving
# interaction between the player and the first waiting customer in line.
# It also aggregates statistics such as counting angry customers for life-loss calculations.
#

class OrderManager:
    """Manages customer queue and orders."""

    def __init__(self):
        self.customers: List[Customer] = []
        self.next_customer_id = 1
        self.spawn_timer = 0
        self.spawn_interval = CUSTOMER_SPAWN_BASE
        self.max_customers = 5

    def update(self, dt: float, level: int):
        """Advance the entire customer ecosystem by one frame.
        
        Updates all existing customers (animations, patience, state changes), removes
        any that have fully exited the screen, and spawns a new customer if the spawn
        timer exceeds the level-adjusted interval and the queue is not at max capacity.
        Higher levels reduce the spawn interval, increasing pressure on the player.
        """
        # Update existing customers
        for customer in self.customers:
            customer.update(dt)

        # Remove customers that have left
        self.customers = [c for c in self.customers if not c.is_off_screen()]

        # Spawn new customers
        self.spawn_timer += dt
        adjusted_interval = max(1.5, self.spawn_interval - level * 0.3)

        if self.spawn_timer >= adjusted_interval and len(self.customers) < self.max_customers:
            self.spawn_timer = 0
            new_customer = Customer(self.next_customer_id, level)
            self.next_customer_id += 1
            self.customers.append(new_customer)

    def get_waiting_customers(self) -> List[Customer]:
        """Filter the customer list to return only those currently in the WAITING state.
        
        A customer must have both state WAITING and arrived True (finished entrance
        animation) to be considered truly waiting. This list drives the serving logic
        and determines which customer receives the next order fulfillment.
        """
        return [c for c in self.customers if c.state == CustomerState.WAITING and c.arrived]

    def get_first_waiting(self) -> Optional[Customer]:
        """Retrieve the next customer eligible to receive a served order.
        
        Returns the first element from get_waiting_customers(), which respects
        spawn order (left-to-right queue). Returns None if no customers are currently
        waiting, preventing invalid serve actions when the queue is empty.
        """
        waiting = self.get_waiting_customers()
        return waiting[0] if waiting else None

    def serve_customer(self, quantity: int) -> Tuple[bool, int, int, bool]:
        """Attempt to fulfill the first waiting customer's order with the given quantity.
        
        Delegates validation to the Customer's serve() method. On success, extracts
        and returns the score, money, and special-customer flag from that customer.
        On failure (wrong quantity), returns a -50 score penalty, zero money, and False.
        This tuple is unpacked by the main Game.serve_order() method to apply results.
        """
        customer = self.get_first_waiting()
        if customer is None:
            return False, 0, 0, False

        success = customer.serve(quantity)
        if success:
            score = customer.get_score()
            money = customer.get_money()
            is_special = customer.is_special
            return True, score, money, is_special
        else:
            return False, -50, 0, False

    def get_angry_customers(self) -> int:
        """Count how many customers are currently in the ANGRY state and still visible.
        
        Only counts angry customers whose x position is still within the screen bounds,
        ensuring each angry departure is processed exactly once for life-loss calculation
        before the customer is cleaned up by the off-screen removal logic.
        """
        return sum(1 for c in self.customers if c.state == CustomerState.ANGRY and c.x > -150)

    def draw(self, surface):
        """Render every active customer in the queue.
        
        Simply iterates over the customer list and delegates to each Customer's
        own draw method, preserving their relative layering in spawn order.
        """
        for customer in self.customers:
            customer.draw(surface)

# PARTICLE SYSTEM
#
# Provides lightweight visual feedback through programmatically generated particles.
# Individual Particle instances track position, velocity, color, size, and remaining lifetime,
# applying simple gravity and fade-out for a polished effect. The ParticleSystem
# container manages spawning batches for different events (success, failure, grill smoke),
# updates all active particles each frame, and culls dead ones to maintain performance.
#

class Particle:
    """Simple particle for visual effects."""

    def __init__(self, x: float, y: float, color: Tuple[int, int, int], 
                 velocity: Tuple[float, float], lifetime: float, size: int = 4):
        self.x = x
        self.y = y
        self.color = color
        self.vx, self.vy = velocity
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size

    def update(self, dt: float):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt
        self.vy += 50 * dt  # gravity

    def draw(self, surface):
        alpha = max(0, int(255 * (self.lifetime / self.max_lifetime)))
        color = (*self.color[:3], alpha)
        size = max(1, int(self.size * (self.lifetime / self.max_lifetime)))
        pygame.draw.circle(surface, self.color[:3], (int(self.x), int(self.y)), size)

    def is_dead(self) -> bool:
        return self.lifetime <= 0

class ParticleSystem:
    """Manages visual particle effects."""

    def __init__(self):
        self.particles: List[Particle] = []

    def spawn(self, x: float, y: float, color: Tuple[int, int, int], 
              count: int = 10, speed: float = 100):
        """Generate a burst of particles at the specified screen coordinates.
        
        Creates count particles with randomized velocities radiating outward from
        the spawn point. Horizontal velocity is bidirectional and varied; vertical
        velocity is always upward (negative) with random magnitude. Each particle
        gets a random lifetime for natural variation in the burst pattern.
        """
        for _ in range(count):
            angle = random.uniform(0, 6.28)
            vel = random.uniform(speed * 0.5, speed)
            vx = vel * (1 if random.random() > 0.5 else -1) * random.uniform(0.5, 1.5)
            vy = -random.uniform(speed * 0.5, speed)
            lifetime = random.uniform(0.5, 1.5)
            self.particles.append(Particle(x, y, color, (vx, vy), lifetime))

    def spawn_success(self, x: float, y: float):
        """Create a celebratory particle burst for a correct order serve.
        
        Emits green particles (patience color) and gold particles (score color)
        at the specified location with slightly different speeds for a layered,
        festive explosion that rewards the player visually.
        """
        self.spawn(x, y, COLORS['patience_green'], 15, 150)
        self.spawn(x, y, COLORS['text_gold'], 8, 100)

    def spawn_fail(self, x: float, y: float):
        """Create a punitive particle burst for a wrong order or missed serve.
        
        Emits red particles at the specified location to give immediate visual
        feedback that the player made an error, reinforcing the negative outcome
        alongside the score penalty and combo break.
        """
        self.spawn(x, y, COLORS['text_red'], 12, 120)

    def spawn_smoke(self, x: float, y: float):
        """Create a single drifting smoke particle from the grill area.
        
        Generates a gray particle with slight horizontal drift and upward velocity,
        simulating the aromatic smoke rising from a real suya grill. Randomized
        position offset and size variation make the effect look organic rather than mechanical.
        """
        self.particles.append(Particle(
            x + random.randint(-20, 20), y,
            (100, 100, 100),
            (random.uniform(-20, 20), -random.uniform(30, 60)),
            random.uniform(1, 2),
            random.randint(3, 6)
        ))

    def update(self, dt: float):
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if not p.is_dead()]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)

# UI MANAGER
#
# Centralizes every aspect of the user interface that does not belong to a specific
# gameplay object. This includes initializing a font registry for consistent typography,
# defining reusable button structures with hover and pressed visual states, and
# implementing dedicated draw methods for every screen in the game: main menu,
# instructions, upgrade shop, in-game HUD, pause overlay, and game-over screen.
# It also handles dynamic button lists that change based on the current game state.
#

class UIManager:
    """Handles all UI rendering and input."""

    def __init__(self):
        self.fonts = {
            'title': pygame.font.SysFont('Arial', 72, bold=True),
            'subtitle': pygame.font.SysFont('Arial', 36, bold=True),
            'large': pygame.font.SysFont('Arial', 48, bold=True),
            'medium': pygame.font.SysFont('Arial', 28, bold=True),
            'small': pygame.font.SysFont('Arial', 20),
            'tiny': pygame.font.SysFont('Arial', 16),
        }
        self.buttons: List[Dict] = []
        self.hovered_button = None

    def create_button(self, rect: pygame.Rect, text: str, action: str, 
                     color_key: str = 'button_normal') -> Dict:
        """Construct a dictionary representing an interactive UI button.
        
        Packages the button's screen rectangle, display text, action identifier
        (used by the event handler to determine what happens when clicked), and
        three color states (normal, hover, pressed) into a single structure.
        This dictionary is appended to self.buttons and consumed by draw_button().
        """
        button = {
            'rect': rect,
            'text': text,
            'action': action,
            'color': COLORS[color_key],
            'hover_color': COLORS['button_hover'],
            'pressed_color': COLORS['button_pressed']
        }
        return button

    def draw_button(self, surface, button, is_hovered=False, is_pressed=False):
        """Render one button with appropriate visual state onto the surface.
        
        Selects the background color based on interaction state (pressed takes
        precedence over hover over normal), draws a rounded rectangle, adds a
        black outline for definition, and centers the button text within the rect.
        """
        if is_pressed:
            color = button['pressed_color']
        elif is_hovered:
            color = button['hover_color']
        else:
            color = button['color']

        draw_rounded_rect(surface, color, button['rect'], 15)
        pygame.draw.rect(surface, (0, 0, 0), button['rect'], 2, border_radius=15)

        font = self.fonts['medium']
        draw_text(surface, button['text'], font, COLORS['text_white'], 
                 button['rect'].center)

    def draw_main_menu(self, surface, high_scores: List[Dict]):
        """Render the game's title screen with navigation and leaderboard.
        
        Fills the background with the dark theme color, draws the game title
        and subtitle, adds decorative orange circles, creates and positions
        four interactive buttons (START GAME, INSTRUCTIONS, SHOP / UPGRADES, EXIT),
        and displays the top 5 high scores with player names and score values.
        """
        # Background
        surface.fill(COLORS['bg_dark'])

        # Title
        draw_text(surface, "SUYA RUSH", self.fonts['title'], COLORS['text_gold'],
                 (SCREEN_WIDTH//2, 120))
        draw_text(surface, "Nigerian Street-Food Simulator", self.fonts['subtitle'], 
                 COLORS['text_white'], (SCREEN_WIDTH//2, 180))

        # Decorative elements
        for i in range(3):
            pygame.draw.circle(surface, COLORS['fire_orange'], 
                             (200 + i * 400, 300), 30 + i * 5)

        # Buttons
        self.buttons = []
        button_y = 320
        for text, action in [("START GAME", "start"), ("INSTRUCTIONS", "instructions"), 
                            ("SHOP / UPGRADES", "shop"), ("EXIT", "exit")]:
            rect = pygame.Rect(SCREEN_WIDTH//2 - 150, button_y, 300, 60)
            self.buttons.append(self.create_button(rect, text, action))
            button_y += 80

        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            is_hovered = button['rect'].collidepoint(mouse_pos)
            self.draw_button(surface, button, is_hovered)

        # High scores
        if high_scores:
            draw_text(surface, "HIGH SCORES", self.fonts['medium'], COLORS['text_gold'],
                     (SCREEN_WIDTH//2, 650))
            y = 690
            for i, score in enumerate(high_scores[:5]):
                text = f"{i+1}. {score.get('name', 'Player')} - {score.get('score', 0)}"
                draw_text(surface, text, self.fonts['small'], COLORS['text_white'],
                         (SCREEN_WIDTH//2, y))
                y += 25

    def draw_instructions(self, surface):
        """Render the tutorial screen explaining game mechanics and controls.
        
        Displays a dark background with the HOW TO PLAY header, followed by
        numbered gameplay steps, a KEYBOARD SHORTCUTS section highlighting
        hotkeys for efficient play, and notes on special customers and combos.
        A BACK button at the bottom returns the player to the main menu.
        """
        surface.fill(COLORS['bg_dark'])

        draw_text(surface, "HOW TO PLAY", self.fonts['title'], COLORS['text_gold'],
                 (SCREEN_WIDTH//2, 60))

        instructions = [
            "",
            "You run a Suya (grilled meat) stand in Nigeria!",
            "",
            "1. Customers arrive and order 1-4 sticks of suya",
            "2. Click 'ADD SUYA' to place meat on the grill",
            "3. Wait for suya to cook (watch the green bar)",
            "4. Don't let suya burn! Remove burned suya with 'DISCARD'",
            "5. Click the number buttons (1-4) to serve customers",
            "6. Serve before their patience runs out!",
            "",
            "KEYBOARD SHORTCUTS:",
            "[1-4] Serve that many suya to the first customer",
            "[SPACE] Add suya to grill",
            "[D] Discard burned suya",
            "[P] Pause game",
            "",
            "SPECIAL CUSTOMERS (★) pay DOUBLE!",
            "Build COMBOs by serving consecutive correct orders!",
        ]

        y = 120
        for line in instructions:
            if line.startswith("KEYBOARD") or line.startswith("SPECIAL"):
                draw_text(surface, line, self.fonts['medium'], COLORS['text_gold'],
                         (SCREEN_WIDTH//2, y))
            else:
                draw_text(surface, line, self.fonts['small'], COLORS['text_white'],
                         (SCREEN_WIDTH//2, y))
            y += 30

        # Back button
        self.buttons = []
        back_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 100, 200, 50)
        self.buttons.append(self.create_button(back_rect, "BACK", "menu"))

        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            is_hovered = button['rect'].collidepoint(mouse_pos)
            self.draw_button(surface, button, is_hovered)

    def draw_shop(self, surface, money: int, upgrades: Dict):
        """Render the upgrade shop where players spend earned money on permanent improvements.
        
        Shows the player's current money balance and lists four upgrade categories:
        Faster Grill, More Patience, Extra Grill Slot, and Higher Profits. Each item
        displays its name, description, current level, and purchase cost. Buttons
        are visually disabled (grayed out) when the player cannot afford the upgrade.
        """
        surface.fill(COLORS['bg_dark'])

        draw_text(surface, "SUYA STAND UPGRADES", self.fonts['title'], COLORS['text_gold'],
                 (SCREEN_WIDTH//2, 60))
        draw_text(surface, f"Money: ₦{money}", self.fonts['large'], COLORS['text_green'],
                 (SCREEN_WIDTH//2, 130))

        self.buttons = []

        # Upgrade items
        upgrades_list = [
            ("Faster Grill", "cook_speed", 500, "Cook suya 25% faster"),
            ("More Patience", "patience", 400, "Customers wait 2s longer"),
            ("Extra Grill Slot", "grill_slots", 800, "Cook one more suya at once"),
            ("Higher Profits", "profits", 600, "Earn 20% more money"),
        ]

        y = 200
        for name, key, cost, desc in upgrades_list:
            # Upgrade box
            box_rect = pygame.Rect(200, y, 800, 80)
            draw_rounded_rect(surface, COLORS['wood'], box_rect, 10)

            draw_text(surface, name, self.fonts['medium'], COLORS['text_gold'],
                     (300, y + 25), center=False)
            draw_text(surface, desc, self.fonts['small'], COLORS['text_white'],
                     (300, y + 55), center=False)

            level = upgrades.get(key, 0)
            draw_text(surface, f"Lvl {level}", self.fonts['small'], COLORS['text_gold'],
                     (650, y + 40))

            # Buy button
            buy_rect = pygame.Rect(750, y + 15, 200, 50)
            can_afford = money >= cost
            buy_btn = self.create_button(buy_rect, f"₦{cost}", f"buy_{key}")
            buy_btn['cost'] = cost
            buy_btn['can_afford'] = can_afford
            self.buttons.append(buy_btn)

            color = COLORS['button_normal'] if can_afford else (80, 80, 80)
            draw_rounded_rect(surface, color, buy_rect, 10)
            pygame.draw.rect(surface, (0, 0, 0), buy_rect, 2, border_radius=10)

            text_color = COLORS['text_white'] if can_afford else (150, 150, 150)
            draw_text(surface, f"₦{cost}", self.fonts['medium'], text_color, buy_rect.center)

            y += 100

        # Back button
        back_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 80, 200, 50)
        self.buttons.append(self.create_button(back_rect, "BACK", "menu"))

        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            if button['action'] != "menu":
                continue
            is_hovered = button['rect'].collidepoint(mouse_pos)
            self.draw_button(surface, button, is_hovered)

    def draw_game_hud(self, surface, score: int, money: int, combo: int, 
                     level: int, lives: int):
        """Render the persistent heads-up display overlaid during gameplay.
        
        Draws a semi-transparent top panel containing the current score in gold,
        money balance in green with the Nigerian Naira symbol, current level,
        satisfaction lives as five circles (filled red for remaining, gray for lost),
        and a prominent combo counter with bonus point annotations when active.
        """
        # Top panel
        panel_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 70)
        s = pygame.Surface((SCREEN_WIDTH, 70), pygame.SRCALPHA)
        s.fill(COLORS['ui_panel'])
        surface.blit(s, (0, 0))

        # Score
        draw_text(surface, f"Score: {score}", self.fonts['medium'], 
                 COLORS['text_gold'], (100, 35))

        # Money
        draw_text(surface, f"₦{money}", self.fonts['medium'], 
                 COLORS['text_green'], (300, 35))

        # Level
        draw_text(surface, f"Level {level}", self.fonts['medium'], 
                 COLORS['text_white'], (500, 35))

        # Lives (satisfaction)
        draw_text(surface, "Satisfaction: ", self.fonts['medium'], 
                 COLORS['text_white'], (700, 35))
        for i in range(5):
            color = COLORS['text_red'] if i < lives else (80, 80, 80)
            pygame.draw.circle(surface, color, (820 + i * 30, 35), 10)

        # Combo
        if combo > 1:
            combo_text = f"COMBO x{combo}!"
            draw_text(surface, combo_text, self.fonts['large'], 
                     COLORS['text_gold'], (SCREEN_WIDTH//2, 110))
            if combo >= 3:
                bonus = COMBO_BONUS[min(combo, len(COMBO_BONUS)-1)]
                draw_text(surface, f"+{bonus} pts", self.fonts['medium'], 
                         COLORS['patience_green'], (SCREEN_WIDTH//2, 150))

    def draw_game_controls(self, surface, grill: Grill):
        """Render the interactive control panel for cooking and serving actions.
        
        Creates the ADD SUYA and DISCARD buttons on the left, serve-quantity
        buttons (1-4) on the right, and displays a real-time count of how many
        suya sticks are cooked and ready out of the total available grill slots.
        All buttons support mouse hover highlighting.
        """
        self.buttons = []

        # Add Suya button
        add_rect = pygame.Rect(50, 580, 180, 60)
        self.buttons.append(self.create_button(add_rect, "ADD SUYA", "add_suya"))

        # Discard burned button
        discard_rect = pygame.Rect(50, 660, 180, 60)
        self.buttons.append(self.create_button(discard_rect, "DISCARD", "discard"))

        # Serve quantity buttons
        for i in range(1, 5):
            btn_rect = pygame.Rect(900 + (i-1) * 70, 580, 60, 60)
            self.buttons.append(self.create_button(btn_rect, str(i), f"serve_{i}"))

        # Grill status
        ready = grill.get_ready_suya()
        status_text = f"Ready: {ready}/{grill.num_slots}"
        draw_text(surface, status_text, self.fonts['medium'], 
                 COLORS['text_gold'], (140, 540))

        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            is_hovered = button['rect'].collidepoint(mouse_pos)
            self.draw_button(surface, button, is_hovered)

    def draw_pause(self, surface):
        """Render a dimming overlay and pause message when the game is paused.
        
        Covers the entire screen with a semi-transparent black rectangle to mute
        background visuals, then displays PAUSED in large white text and a
        reminder to press P to resume in smaller gold text.
        """
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        draw_text(surface, "PAUSED", self.fonts['title'], COLORS['text_white'],
                 (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        draw_text(surface, "Press P to resume", self.fonts['medium'], COLORS['text_gold'],
                 (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30))

    def draw_game_over(self, surface, score: int, high_score: bool, 
                      high_scores: List[Dict]):
        """Render the end-of-game summary screen with final statistics.
        
        Dims the screen with a dark overlay, shows the final score, highlights
        NEW HIGH SCORE! if applicable, lists the top 5 scores from the leaderboard
        (with the top entry in gold), and provides PLAY AGAIN and MAIN MENU buttons
        for navigation.
        """
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        draw_text(surface, "GAME OVER", self.fonts['title'], COLORS['text_red'],
                 (SCREEN_WIDTH//2, 150))

        draw_text(surface, f"Final Score: {score}", self.fonts['large'], 
                 COLORS['text_gold'], (SCREEN_WIDTH//2, 250))

        if high_score:
            draw_text(surface, "NEW HIGH SCORE!", self.fonts['large'], 
                     COLORS['patience_green'], (SCREEN_WIDTH//2, 320))

        # High scores
        draw_text(surface, "TOP SCORES", self.fonts['medium'], COLORS['text_white'],
                 (SCREEN_WIDTH//2, 380))
        y = 420
        for i, hs in enumerate(high_scores[:5]):
            text = f"{i+1}. {hs.get('name', 'Player')} - {hs.get('score', 0)}"
            color = COLORS['text_gold'] if i == 0 else COLORS['text_white']
            draw_text(surface, text, self.fonts['small'], color,
                     (SCREEN_WIDTH//2, y))
            y += 30

        # Buttons
        self.buttons = []
        restart_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 600, 300, 60)
        self.buttons.append(self.create_button(restart_rect, "PLAY AGAIN", "restart"))

        menu_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 680, 300, 60)
        self.buttons.append(self.create_button(menu_rect, "MAIN MENU", "menu"))

        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            is_hovered = button['rect'].collidepoint(mouse_pos)
            self.draw_button(surface, button, is_hovered)

    def draw_background(self, surface):
        """Render the static environmental backdrop for the gameplay scene.
        
        Composes a Nigerian street-market atmosphere with a dark brown sky,
        five background market stalls with triangular roofs and rectangular bodies,
        a ground plane, the main suya stand counter made of wood tones, a lighter
        counter-top edge, and a centered SUYA STAND sign in gold lettering.
        """
        # Sky/background
        surface.fill(COLORS['bg_market'])

        # Market stalls in background
        for i in range(5):
            x = i * 250
            # Stall roof
            pygame.draw.polygon(surface, (100, 60, 30), 
                              [(x, 150), (x + 125, 100), (x + 250, 150)])
            # Stall body
            pygame.draw.rect(surface, (80, 50, 25), (x + 20, 150, 210, 200))

        # Ground
        pygame.draw.rect(surface, (60, 50, 30), (0, 600, SCREEN_WIDTH, 200))

        # Suya stand structure
        # Counter
        counter_rect = pygame.Rect(0, 350, SCREEN_WIDTH, 250)
        draw_rounded_rect(surface, COLORS['wood'], counter_rect, 0)

        # Counter top edge
        pygame.draw.rect(surface, COLORS['wood_light'], (0, 350, SCREEN_WIDTH, 20))

        # Stand sign
        sign_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 50, 300, 80)
        draw_rounded_rect(surface, COLORS['wood'], sign_rect, 10)
        pygame.draw.rect(surface, (0, 0, 0), sign_rect, 3, border_radius=10)

        font = pygame.font.SysFont('Arial', 40, bold=True)
        draw_text(surface, "SUYA STAND", font, COLORS['text_gold'], 
                 (SCREEN_WIDTH//2, 90))

# MAIN GAME CLASS
#
# The core orchestrator that ties every subsystem together. It initializes Pygame,
# creates the display window and game clock, instantiates the Grill, OrderManager,
# ParticleSystem, and UIManager, and maintains the authoritative game state variables
# (score, money, combo, level, lives). The Game class defines the main event loop,
# processes all player input (keyboard shortcuts and mouse clicks), applies upgrade
# effects to gameplay constants, enforces level progression, validates serving actions,
# tracks daily objectives, and transitions between menu, playing, paused, and game-over states.
# It also persists high scores to disk and handles end-of-game bookkeeping.
#

class Game:
    """Main game class that manages all game states and systems."""

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Suya Rush - Nigerian Street-Food Simulator")
        self.clock = pygame.time.Clock()
        self.running = True

        # Game systems
        self.grill = Grill()
        self.order_manager = OrderManager()
        self.particles = ParticleSystem()
        self.ui = UIManager()

        # Game state
        self.state = GameState.MENU
        self.score = 0
        self.money = 0
        self.combo = 0
        self.level = 1
        self.lives = 5
        self.total_served = 0
        self.total_angry = 0

        # Upgrades
        self.upgrades = {
            'cook_speed': 0,
            'patience': 0,
            'grill_slots': 0,
            'profits': 0,
        }

        # High scores
        self.high_scores = load_high_scores()

        # Sound placeholders (visual feedback used when sounds unavailable)
        self.sounds_enabled = False

        # Daily objectives
        self.objectives = {
            'serve_10': {'target': 10, 'current': 0, 'reward': 200, 'completed': False},
            'serve_special': {'target': 3, 'current': 0, 'reward': 300, 'completed': False},
            'no_burn': {'target': 1, 'current': 0, 'reward': 500, 'completed': False},
        }
        self.burned_count = 0

    def apply_upgrades(self):
        """Translate the player's purchased upgrade levels into modified gameplay constants.
        
        Each upgrade key maps to a specific mechanical change: cook_speed increases
        the global cooking rate, patience extends customer wait times (applied during
        Customer initialization), grill_slots expands the Grill's slot count, and
        profits boosts money rewards at serve time. This method must be called after
        any upgrade purchase and during game reset to ensure values are current.
        """
        # Faster grill
        speed_bonus = 1.0 + self.upgrades['cook_speed'] * 0.25
        self.grill.cook_speed = speed_bonus

        # More patience
        patience_bonus = self.upgrades['patience'] * 2.0

        # Extra grill slots
        extra_slots = self.upgrades['grill_slots']
        self.grill.num_slots = self.grill.max_slots + extra_slots

        # Higher profits applied in serve logic

    def reset_game(self):
        """Reinitialize all runtime game state to begin a fresh play session.
        
        Creates new instances of Grill (with upgrade-adjusted slot count), OrderManager,
        and ParticleSystem; resets score, money, combo, level, lives, and counters;
        reapplies all purchased upgrades; and clears objective progress. Preserves
        the upgrade dictionary and high-score list across sessions.
        """
        self.grill = Grill(self.grill.max_slots + self.upgrades['grill_slots'])
        self.apply_upgrades()
        self.order_manager = OrderManager()
        self.particles = ParticleSystem()
        self.score = 0
        self.money = 0
        self.combo = 0
        self.level = 1
        self.lives = 5
        self.total_served = 0
        self.total_angry = 0
        self.burned_count = 0
        self.objectives = {
            'serve_10': {'target': 10, 'current': 0, 'reward': 200, 'completed': False},
            'serve_special': {'target': 3, 'current': 0, 'reward': 300, 'completed': False},
            'no_burn': {'target': 1, 'current': 0, 'reward': 500, 'completed': False},
        }

    def check_level_up(self):
        """Evaluate whether the player has met the threshold to advance to the next level.
        
        The requirement is total_served >= level * 8 (e.g., 8 serves for level 1,
        16 for level 2, etc.). Upon leveling up, increments the level counter and
        spawns a success particle burst at the screen center to celebrate the milestone.
        Higher levels increase spawn frequency and order complexity.
        """
        if self.total_served >= self.level * 8:
            self.level += 1
            # Level up effect
            self.particles.spawn_success(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)

    def serve_order(self, quantity: int):
        """Process a player-initiated serving action for the specified quantity.
        
        Validates that enough cooked suya is available on the grill; if not,
        spawns a fail effect and aborts. Otherwise delegates to OrderManager to
        serve the first waiting customer. On success, removes the consumed suya,
        applies profit upgrades, increments combo and score (with combo bonus),
        awards money, updates objectives, checks for level-up, and spawns success
        particles. On failure, breaks combo, decrements lives, spawns fail particles,
        and triggers game over if lives reach zero.
        """
        ready = self.grill.get_ready_suya()
        if ready < quantity:
            # Not enough suya ready
            self.particles.spawn_fail(200, 300)
            return

        success, points, earned, is_special = self.order_manager.serve_customer(quantity)

        if success:
            # Take suya from grill
            self.grill.take_suya(quantity)

            # Apply profit upgrade
            profit_mult = 1.0 + self.upgrades['profits'] * 0.2
            earned = int(earned * profit_mult)

            # Combo system
            self.combo += 1
            combo_bonus = COMBO_BONUS[min(self.combo, len(COMBO_BONUS)-1)]
            points += combo_bonus

            self.score += points
            self.money += earned
            self.total_served += 1

            # Particle effect
            first_customer = self.order_manager.get_waiting_customers()
            if first_customer:
                self.particles.spawn_success(first_customer[0].x, first_customer[0].y)

            # Objectives
            self.objectives['serve_10']['current'] += 1
            if is_special:
                self.objectives['serve_special']['current'] += 1

            self.check_level_up()
            self.check_objectives()
        else:
            self.combo = 0
            self.lives -= 1
            self.particles.spawn_fail(200, 300)
            if self.lives <= 0:
                self.game_over()

    def check_objectives(self):
        """Evaluate all active daily objectives and grant rewards for completed ones.
        
        Iterates through the objectives dictionary; for any objective whose current
        progress meets or exceeds its target and is not yet marked completed,
        flags it complete, adds the monetary reward to the player's balance,
        and awards half the reward value as bonus score points.
        """
        for key, obj in self.objectives.items():
            if not obj['completed'] and obj['current'] >= obj['target']:
                obj['completed'] = True
                self.money += obj['reward']
                self.score += obj['reward'] // 2

    def game_over(self):
        """Transition the game to the GAME_OVER state and persist the final score.
        
        Compares the current score against the existing high-score list to determine
        if this run qualifies as a new high score. Appends the result, sorts descending,
        trims to the top 10 entries, and writes the updated leaderboard back to disk
        via save_high_scores(). The UI will read these values when rendering the
        game-over screen.
        """
        self.state = GameState.GAME_OVER

        # Check high score
        is_high = False
        if not self.high_scores or self.score > self.high_scores[0].get('score', 0):
            is_high = True

        # Save score
        self.high_scores.append({'name': 'Player', 'score': self.score, 'level': self.level})
        self.high_scores.sort(key=lambda x: x['score'], reverse=True)
        self.high_scores = self.high_scores[:10]
        save_high_scores(self.high_scores)

    def handle_events(self):
        """Poll and respond to all Pygame events for the current frame.
        
        Handles the QUIT event to stop the game loop. Processes keyboard input
        for pause toggling (P key) and gameplay shortcuts (SPACE to add suya,
        D to discard burned, 1-4 to serve quantities). Processes mouse clicks
        on UI buttons across all game states, routing actions like start, restart,
        menu navigation, cooking commands, serving commands, and upgrade purchases
        to their respective handler logic.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p and self.state == GameState.PLAYING:
                    self.state = GameState.PAUSED
                elif event.key == pygame.K_p and self.state == GameState.PAUSED:
                    self.state = GameState.PLAYING

                if self.state == GameState.PLAYING:
                    if event.key == pygame.K_SPACE:
                        self.grill.add_suya()
                    elif event.key == pygame.K_d:
                        self.grill.discard_burned()
                    elif event.key == pygame.K_1:
                        self.serve_order(1)
                    elif event.key == pygame.K_2:
                        self.serve_order(2)
                    elif event.key == pygame.K_3:
                        self.serve_order(3)
                    elif event.key == pygame.K_4:
                        self.serve_order(4)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()

                for button in self.ui.buttons:
                    if button['rect'].collidepoint(mouse_pos):
                        action = button['action']

                        if action == "start":
                            self.reset_game()
                            self.state = GameState.PLAYING
                        elif action == "instructions":
                            self.state = GameState.INSTRUCTIONS
                        elif action == "shop":
                            self.state = GameState.SHOP
                        elif action == "exit":
                            self.running = False
                        elif action == "menu":
                            self.state = GameState.MENU
                        elif action == "restart":
                            self.reset_game()
                            self.state = GameState.PLAYING
                        elif action == "add_suya":
                            self.grill.add_suya()
                        elif action == "discard":
                            self.grill.discard_burned()
                        elif action.startswith("serve_"):
                            qty = int(action.split("_")[1])
                            self.serve_order(qty)
                        elif action.startswith("buy_"):
                            key = action.split("_", 1)[1]
                            cost = button.get('cost', 0)
                            if button.get('can_afford', False) and self.money >= cost:
                                self.money -= cost
                                self.upgrades[key] += 1
                                self.apply_upgrades()

    def update(self, dt: float):
        """Advance all gameplay systems by one frame when in the PLAYING state.
        
        Updates the grill cooking simulation, customer queue and spawning, and
        particle effects. Detects newly angry customers since the last frame,
        deducts lives accordingly, breaks combo, and triggers game over if lives
        deplete. Spawns ambient grill smoke randomly. Monitors for burned suya
        to auto-discard them and reset the no-burn objective progress.
        """
        if self.state != GameState.PLAYING:
            return

        # Update systems
        self.grill.update(dt)
        self.order_manager.update(dt, self.level)
        self.particles.update(dt)

        # Check for angry customers
        angry_count = self.order_manager.get_angry_customers()
        if angry_count > self.total_angry:
            new_angry = angry_count - self.total_angry
            self.total_angry = angry_count
            self.lives -= new_angry
            self.combo = 0
            if self.lives <= 0:
                self.game_over()

        # Random smoke particles from grill
        if random.random() < 0.1:
            self.particles.spawn_smoke(400, 420)

        # Check no-burn objective
        for slot in self.grill.slots:
            if slot is not None and slot.is_burned():
                self.burned_count += 1
                self.objectives['no_burn']['current'] = 0  # Reset
                slot.discard()

    def draw(self):
        """Execute the complete rendering pipeline for the current game state.
        
        Clears the screen and delegates to the appropriate UI drawing method
        based on state (MENU, INSTRUCTIONS, SHOP, PLAYING, PAUSED, GAME_OVER).
        For gameplay states, renders the background scene first, then overlays
        game objects (grill, customers, particles), the HUD, control buttons,
        active objectives, and finally any state-specific overlays (pause dimming
        or game-over screen). Flips the display buffer to present the frame.
        """
        self.screen.fill(COLORS['bg_dark'])

        if self.state == GameState.MENU:
            self.ui.draw_main_menu(self.screen, self.high_scores)

        elif self.state == GameState.INSTRUCTIONS:
            self.ui.draw_instructions(self.screen)

        elif self.state == GameState.SHOP:
            self.ui.draw_shop(self.screen, self.money, self.upgrades)

        elif self.state in [GameState.PLAYING, GameState.PAUSED, GameState.GAME_OVER]:
            # Background
            self.ui.draw_background(self.screen)

            # Game objects
            self.grill.draw(self.screen)
            self.order_manager.draw(self.screen)
            self.particles.draw(self.screen)

            # HUD
            self.ui.draw_game_hud(self.screen, self.score, self.money, 
                                 self.combo, self.level, self.lives)
            self.ui.draw_game_controls(self.screen, self.grill)

            # Objectives display
            y = 200
            for key, obj in self.objectives.items():
                if not obj['completed']:
                    status = f"{obj['current']}/{obj['target']}"
                    text = f"Obj: {status} - ₦{obj['reward']}"
                    draw_text(self.screen, text, self.ui.fonts['tiny'], 
                             COLORS['text_gold'], (1100, y), center=False)
                    y += 20

            # Overlays
            if self.state == GameState.PAUSED:
                self.ui.draw_pause(self.screen)
            elif self.state == GameState.GAME_OVER:
                is_high = self.score > (self.high_scores[1].get('score', 0) if len(self.high_scores) > 1 else 0)
                self.ui.draw_game_over(self.screen, self.score, is_high, self.high_scores)

        pygame.display.flip()

    def run(self):
        """Execute the primary game loop until the player exits.
        
        Continuously calculates delta time, processes input events, updates game
        logic, and renders the frame at the target FPS. This method blocks until
        self.running becomes False (via the exit button or window close), after
        which it cleanly shuts down Pygame.
        """
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()