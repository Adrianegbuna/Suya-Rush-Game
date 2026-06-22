"""
================================================================================
SUYA RUSH 3D - Nigerian Street-Food Simulator
================================================================================
"""

import pygame
import random
import json
import math
import time
import os
from enum import Enum
from typing import List, Optional, Dict, Tuple
from collections import deque

import numpy as np

from OpenGL.GL import *

# ============================================================
# INITIALIZATION
# ============================================================

pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# ============================================================
# COLOR PALETTE
# ============================================================

COLORS = {
    'bg_dark': (0.04, 0.025, 0.015),
    'bg_market': (0.10, 0.06, 0.03),
    'wood': (0.55, 0.35, 0.17),
    'wood_light': (0.65, 0.42, 0.22),
    'wood_dark': (0.30, 0.18, 0.08),
    'terracotta': (0.78, 0.38, 0.18),

    'grill_metal': (0.30, 0.30, 0.33),
    'grill_hot': (0.85, 0.35, 0.12),
    'fire_orange': (1.0, 0.55, 0.0),
    'fire_yellow': (1.0, 0.88, 0.0),
    'fire_red': (1.0, 0.2, 0.05),

    'suya_raw': (0.76, 0.56, 0.40),
    'suya_cooking': (0.65, 0.40, 0.20),
    'suya_cooked': (0.48, 0.22, 0.06),
    'suya_burned': (0.15, 0.07, 0.03),

    'text_white': (1.0, 1.0, 1.0),
    'text_gold': (1.0, 0.85, 0.15),
    'text_green': (0.25, 1.0, 0.45),
    'text_red': (1.0, 0.35, 0.35),
    'text_black': (0.05, 0.05, 0.05),

    'patience_green': (0.2, 1.0, 0.4),
    'patience_yellow': (1.0, 0.9, 0.0),
    'patience_red': (1.0, 0.2, 0.2),

    'skin_1': (0.82, 0.71, 0.55),
    'skin_2': (0.71, 0.55, 0.39),
    'skin_3': (0.94, 0.78, 0.63),
    'skin_4': (0.63, 0.47, 0.31),
    'shirt_red': (0.92, 0.22, 0.22),
    'shirt_blue': (0.22, 0.55, 0.95),
    'shirt_green': (0.22, 0.78, 0.22),
    'shirt_yellow': (0.95, 0.78, 0.15),
    'shirt_purple': (0.72, 0.25, 0.72),

    'concrete': (0.42, 0.38, 0.33),
    'concrete_dark': (0.28, 0.25, 0.22),
    'sky_top': (0.04, 0.06, 0.16),
    'sky_bottom': (0.22, 0.12, 0.05),
    'neon_glow': (1.0, 0.65, 0.15),

    'bubble_white': (0.98, 0.96, 0.92),
    'btn_primary': (0.75, 0.50, 0.18),
    'btn_primary_hover': (0.90, 0.65, 0.28),
    'btn_primary_press': (0.58, 0.38, 0.12),
    'btn_danger': (0.75, 0.20, 0.15),
    'btn_danger_hover': (0.90, 0.30, 0.20),
    'btn_action': (0.20, 0.60, 0.35),
    'btn_action_hover': (0.30, 0.75, 0.45),
    'panel_bg': (0.08, 0.06, 0.04),
    'panel_border': (0.55, 0.35, 0.12),
}

# ============================================================
# GAME BALANCE CONSTANTS
# ============================================================

INITIAL_PATIENCE = 18.0
MIN_PATIENCE = 6.0
COOK_TIME = 4.0
BURN_TIME = 8.0
CUSTOMER_SPAWN_MIN = 5.0
CUSTOMER_SPAWN_MAX = 15.0
MONEY_PER_SUYA = 50
COMBO_BONUS = [0, 0, 25, 60, 120, 250]
SPECIAL_CUSTOMER_CHANCE = 0.15
SPECIAL_MULTIPLIER = 2.0

# ============================================================
# ENUMS
# ============================================================

class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    INSTRUCTIONS = "instructions"
    SHOP = "shop"
    SETTINGS = "settings"

class SuyaState(Enum):
    RAW = "raw"
    COOKING = "cooking"
    COOKED = "cooked"

class CustomerState(Enum):
    WAITING = "waiting"
    SERVED = "served"
    ANGRY = "angry"
    LEAVING = "leaving"


# ============================================================
# 3D RENDERING UTILITIES
# ============================================================

def gl_set_color(r, g, b, a=1.0):
    glColor4f(r, g, b, a)


def draw_cube(x, y, z, w, h, d, color, alpha=1.0):
    gl_set_color(*color[:3], alpha)
    hw, hh, hd = w / 2, h / 2, d / 2
    glBegin(GL_QUADS)
    glNormal3f(0, 0, 1)
    glVertex3f(x - hw, y - hh, z + hd)
    glVertex3f(x + hw, y - hh, z + hd)
    glVertex3f(x + hw, y + hh, z + hd)
    glVertex3f(x - hw, y + hh, z + hd)
    glNormal3f(0, 0, -1)
    glVertex3f(x - hw, y - hh, z - hd)
    glVertex3f(x - hw, y + hh, z - hd)
    glVertex3f(x + hw, y + hh, z - hd)
    glVertex3f(x + hw, y - hh, z - hd)
    glNormal3f(0, 1, 0)
    glVertex3f(x - hw, y + hh, z - hd)
    glVertex3f(x - hw, y + hh, z + hd)
    glVertex3f(x + hw, y + hh, z + hd)
    glVertex3f(x + hw, y + hh, z - hd)
    glNormal3f(0, -1, 0)
    glVertex3f(x - hw, y - hh, z - hd)
    glVertex3f(x + hw, y - hh, z - hd)
    glVertex3f(x + hw, y - hh, z + hd)
    glVertex3f(x - hw, y - hh, z + hd)
    glNormal3f(1, 0, 0)
    glVertex3f(x + hw, y - hh, z - hd)
    glVertex3f(x + hw, y + hh, z - hd)
    glVertex3f(x + hw, y + hh, z + hd)
    glVertex3f(x + hw, y - hh, z + hd)
    glNormal3f(-1, 0, 0)
    glVertex3f(x - hw, y - hh, z - hd)
    glVertex3f(x - hw, y - hh, z + hd)
    glVertex3f(x - hw, y + hh, z + hd)
    glVertex3f(x - hw, y + hh, z - hd)
    glEnd()


def draw_cylinder(x, y, z, radius, height, color, alpha=1.0, segments=16):
    gl_set_color(*color[:3], alpha)
    h2 = height / 2
    glBegin(GL_TRIANGLE_FAN)
    glNormal3f(0, 1, 0)
    glVertex3f(x, y + h2, z)
    for i in range(segments + 1):
        angle = 2 * math.pi * i / segments
        cx = x + radius * math.cos(angle)
        cz = z + radius * math.sin(angle)
        glVertex3f(cx, y + h2, cz)
    glEnd()
    glBegin(GL_TRIANGLE_FAN)
    glNormal3f(0, -1, 0)
    glVertex3f(x, y - h2, z)
    for i in range(segments + 1):
        angle = 2 * math.pi * i / segments
        cx = x + radius * math.cos(angle)
        cz = z + radius * math.sin(angle)
        glVertex3f(cx, y - h2, cz)
    glEnd()
    glBegin(GL_QUAD_STRIP)
    for i in range(segments + 1):
        angle = 2 * math.pi * i / segments
        nx = math.cos(angle)
        nz = math.sin(angle)
        cx = x + radius * nx
        cz = z + radius * nz
        glNormal3f(nx, 0, nz)
        glVertex3f(cx, y + h2, cz)
        glVertex3f(cx, y - h2, cz)
    glEnd()


def draw_sphere(x, y, z, radius, color, alpha=1.0, segments=12):
    gl_set_color(*color[:3], alpha)
    for i in range(segments):
        lat0 = math.pi * (-0.5 + i / segments)
        lat1 = math.pi * (-0.5 + (i + 1) / segments)
        glBegin(GL_QUAD_STRIP)
        for j in range(segments + 1):
            lon = 2 * math.pi * j / segments
            for lat in [lat0, lat1]:
                nx = math.cos(lat) * math.cos(lon)
                ny = math.sin(lat)
                nz = math.cos(lat) * math.sin(lon)
                glNormal3f(nx, ny, nz)
                glVertex3f(x + radius * nx, y + radius * ny, z + radius * nz)
        glEnd()


def draw_rounded_box(x, y, z, w, h, d, color, radius=0.1, alpha=1.0):
    draw_cube(x, y, z, w - radius * 2, h, d - radius * 2, color, alpha)
    draw_cube(x, y, z, w, h - radius * 2, d, color, alpha)
    hw, hd = w / 2 - radius, d / 2 - radius
    corners = [(hw, hd), (-hw, hd), (hw, -hd), (-hw, -hd)]
    for cx, cz in corners:
        draw_cylinder(x + cx, y, z + cz, radius, h - radius * 2, color, alpha)


def draw_text_2d(surface, text, font, color, pos, center=True, shadow=True, shadow_color=(0, 0, 0, 180)):
    if shadow:
        shadow_surf = font.render(text, True, shadow_color[:3])
        if len(shadow_color) > 3:
            shadow_surf.set_alpha(shadow_color[3])
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


def load_high_scores():
    try:
        with open('suya_rush_scores.json', 'r') as f:
            return json.load(f)
    except:
        return []


def save_high_scores(scores):
    with open('suya_rush_scores.json', 'w') as f:
        json.dump(scores, f, indent=2)


# ============================================================
# 3D SUYA STICK
# ============================================================

class SuyaStick3D:
    def __init__(self, slot_index, num_slots):
        self.slot_index = slot_index
        self.state = SuyaState.RAW
        self.cook_timer = 0.0
        self.selected = False
        spacing = 5.0 / max(num_slots, 1)
        self.x = -2.5 + slot_index * spacing + spacing / 2
        self.y = 1.35
        self.z = 0.0
        self.float_offset = random.uniform(0, 6.28)
        self.smoke_timer = 0

    def update(self, dt, cook_speed=1.0):
        self.float_offset += dt * 2
        if self.state == SuyaState.COOKING:
            self.cook_timer += dt * cook_speed
            if self.cook_timer >= COOK_TIME:
                self.state = SuyaState.COOKED
                self.cook_timer = COOK_TIME
        self.smoke_timer += dt

    def start_cooking(self):
        if self.state == SuyaState.RAW:
            self.state = SuyaState.COOKING

    def is_ready(self):
        return self.state == SuyaState.COOKED

    def discard(self):
        self.state = SuyaState.RAW
        self.cook_timer = 0.0
        self.selected = False

    def get_color(self):
        if self.state == SuyaState.RAW:
            return COLORS['suya_raw']
        elif self.state == SuyaState.COOKING:
            progress = self.cook_timer / COOK_TIME
            r = COLORS['suya_raw'][0] + (COLORS['suya_cooked'][0] - COLORS['suya_raw'][0]) * progress
            g = COLORS['suya_raw'][1] + (COLORS['suya_cooked'][1] - COLORS['suya_raw'][1]) * progress
            b = COLORS['suya_raw'][2] + (COLORS['suya_cooked'][2] - COLORS['suya_raw'][2]) * progress
            return (r, g, b)
        else:
            return COLORS['suya_cooked']

    def draw(self):
        color = self.get_color()
        float_y = self.y + math.sin(self.float_offset) * 0.03
        if self.selected:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE)
            draw_sphere(self.x, float_y, self.z, 0.28, COLORS['text_gold'], 0.2)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glDisable(GL_BLEND)
        gl_set_color(0.7, 0.7, 0.72)
        draw_cylinder(self.x, float_y, self.z, 0.022, 0.5, (0.7, 0.7, 0.72))
        chunk_offsets = [-0.18, -0.06, 0.06, 0.18]
        for i, cx in enumerate(chunk_offsets):
            chunk_color = list(color)
            if self.state == SuyaState.COOKING:
                variation = 0.05 * math.sin(self.cook_timer * 3 + i)
                chunk_color = [
                    max(0, min(1, color[0] + variation)),
                    max(0, min(1, color[1] + variation)),
                    max(0, min(1, color[2] + variation))
                ]
            gl_set_color(*chunk_color)
            glPushMatrix()
            glTranslatef(self.x + cx, float_y + 0.06, self.z)
            glScalef(1.0, 0.8, 0.9)
            draw_sphere(0, 0, 0, 0.07, chunk_color)
            glPopMatrix()
        if self.state == SuyaState.COOKING:
            progress = self.cook_timer / COOK_TIME
            bar_w = 0.28
            bar_h = 0.04
            bar_y = float_y + 0.28
            draw_cube(self.x, bar_y, self.z + 0.02, bar_w, bar_h, 0.015, (0.15, 0.15, 0.15))
            bar_color = COLORS['patience_yellow'] if progress < 0.7 else COLORS['patience_green']
            draw_cube(self.x - bar_w / 2 + (bar_w * progress) / 2, bar_y, self.z + 0.03,
                     bar_w * progress, bar_h, 0.02, bar_color)


# ============================================================
# 3D GRILL
# ============================================================

class Grill3D:
    def __init__(self, num_slots=6):
        self.num_slots = num_slots
        self.slots = [None] * num_slots
        self.cook_speed = 1.0
        self.max_slots = num_slots
        self.flame_time = 0.0

    def add_suya(self):
        for i in range(self.num_slots):
            if self.slots[i] is None:
                self.slots[i] = SuyaStick3D(i, self.num_slots)
                self.slots[i].start_cooking()
                return True
        return False

    def get_ready_suya(self):
        return sum(1 for s in self.slots if s is not None and s.is_ready())

    def take_suya(self, quantity):
        taken = 0
        for i in range(self.num_slots):
            if taken >= quantity:
                break
            if self.slots[i] is not None and self.slots[i].is_ready():
                self.slots[i] = None
                taken += 1
        return taken

    def update(self, dt):
        self.flame_time += dt * 10
        for slot in self.slots:
            if slot is not None:
                slot.update(dt, self.cook_speed)

    def draw(self):
        draw_rounded_box(0, 1.0, 0, 5.5, 0.35, 1.8, COLORS['grill_metal'], 0.05)
        draw_cube(0, 1.2, 0, 5.3, 0.06, 1.6, (0.15, 0.15, 0.18))
        gl_set_color(0.4, 0.4, 0.42)
        spacing = 5.0 / max(self.num_slots, 1)
        for i in range(self.num_slots + 1):
            x = -2.5 + i * spacing
            draw_cylinder(x, 1.24, 0, 0.015, 1.5, (0.4, 0.4, 0.42))
        for z in [-0.5, 0, 0.5]:
            draw_cylinder(0, 1.24, z, 0.012, 5.0, (0.4, 0.4, 0.42))
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        for i in range(10):
            fx = -2.2 + i * 0.5
            flicker = math.sin(self.flame_time + i * 1.3) * 0.3 + 0.7
            flicker *= math.sin(self.flame_time * 2 + i * 0.7) * 0.3 + 0.7
            flame_h = 0.35 * flicker
            draw_cylinder(fx, 0.85, 0, 0.05, flame_h * 0.5, COLORS['fire_yellow'], 0.85)
            f_x = fx + math.sin(self.flame_time + i) * 0.02
            f_z = math.cos(self.flame_time + i) * 0.02
            draw_cylinder(f_x, 0.78, f_z, 0.09, flame_h, COLORS['fire_orange'], 0.55)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_BLEND)
        leg_color = (0.2, 0.2, 0.22)
        for lx, lz in [(-2.4, -0.6), (2.4, -0.6), (-2.4, 0.6), (2.4, 0.6)]:
            draw_cylinder(lx, 0.5, lz, 0.05, 0.6, leg_color)
        for slot in self.slots:
            if slot is not None:
                slot.draw()


# ============================================================
# 3D CHEF - PUSHED BACK BEHIND GRILL
# ============================================================

class Chef3D:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        # PUSHED BACK: z=3.5 so chef is clearly behind the grill (grill is at z=0)
        self.z = 9.5
        self.skin_color = COLORS['skin_2']
        self.height = 1.08
        self.breath_offset = random.uniform(0, 6.28)
        self.arm_sway = 0.0
        self.head_turn = 0.0
        self.busy_timer = 0.0

    def update(self, dt):
        self.breath_offset += dt * 2
        self.arm_sway += dt * 1.5
        self.busy_timer += dt
        self.head_turn = math.sin(self.busy_timer * 0.7) * 0.08

    def draw(self):
        h = self.height
        breath = math.sin(self.breath_offset) * 0.02
        arm_angle = math.sin(self.arm_sway) * 0.06

        # Legs (dark trousers)
        gl_set_color(0.15, 0.12, 0.08)
        draw_cylinder(self.x - 0.12, 0.35 * h, self.z, 0.07, 0.7 * h, (0.15, 0.12, 0.08))
        draw_cylinder(self.x + 0.12, 0.35 * h, self.z, 0.07, 0.7 * h, (0.15, 0.12, 0.08))

        # Torso (white chef coat)
        torso_y = 0.9 * h + breath
        draw_rounded_box(self.x, torso_y, self.z, 0.50, 0.68 * h, 0.32, (0.95, 0.95, 0.98), 0.04)

        # White apron
        gl_set_color(0.98, 0.98, 0.98)
        draw_cube(self.x, torso_y - 0.08, self.z + 0.17, 0.40, 0.48 * h, 0.02, (0.98, 0.98, 0.98))
        draw_cube(self.x, torso_y + 0.22 * h, self.z + 0.17, 0.42, 0.025, 0.025, (0.98, 0.98, 0.98))

        # Arms (skin tone, slight sway)
        gl_set_color(*self.skin_color)
        glPushMatrix()
        glTranslatef(self.x - 0.30, torso_y + 0.18 * h, self.z)
        glRotatef(arm_angle * 20, 0, 0, 1)
        draw_cylinder(0, -0.1, 0, 0.055, 0.45 * h, self.skin_color)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(self.x + 0.30, torso_y + 0.18 * h, self.z)
        glRotatef(-arm_angle * 20, 0, 0, 1)
        draw_cylinder(0, -0.1, 0, 0.055, 0.45 * h, self.skin_color)
        glPopMatrix()

        # Head
        head_y = 1.48 * h + breath
        gl_set_color(*self.skin_color)
        draw_sphere(self.x, head_y, self.z, 0.21 * h, self.skin_color)

        # Eyes (looking slightly toward customers)
        eye_y = head_y + 0.04 * h
        eye_z = self.z + 0.17 * h
        gl_set_color(0.1, 0.08, 0.05)
        draw_sphere(self.x - 0.07 + self.head_turn * 0.5, eye_y, eye_z, 0.025, (0.1, 0.08, 0.05))
        draw_sphere(self.x + 0.07 + self.head_turn * 0.5, eye_y, eye_z, 0.025, (0.1, 0.08, 0.05))

        # Chef's Hat (Toque)
        hat_base_y = head_y + 0.18 * h
        gl_set_color(0.96, 0.96, 0.99)
        draw_cylinder(self.x, hat_base_y, self.z, 0.22 * h, 0.05, (0.96, 0.96, 0.99))
        hat_mid_y = hat_base_y + 0.16
        draw_cylinder(self.x, hat_mid_y, self.z, 0.26 * h, 0.28, (0.98, 0.98, 1.0))
        hat_top_y = hat_mid_y + 0.16
        draw_cylinder(self.x, hat_top_y, self.z, 0.28 * h, 0.06, (0.98, 0.98, 1.0))
        draw_cylinder(self.x, hat_top_y + 0.035, self.z, 0.28 * h, 0.015, (1.0, 1.0, 1.0))


# ============================================================
# 3D CUSTOMER (with facing direction and speech bubble text)
# ============================================================

class Customer3D:
    def __init__(self, customer_id, level=1, queue_index=0):
        self.id = customer_id
        self.state = CustomerState.WAITING
        self.queue_index = queue_index

        skin_colors = [COLORS['skin_1'], COLORS['skin_2'], COLORS['skin_3'], COLORS['skin_4']]
        self.skin_color = random.choice(skin_colors)
        shirt_colors = [COLORS['shirt_red'], COLORS['shirt_blue'], COLORS['shirt_green'],
                       COLORS['shirt_yellow'], COLORS['shirt_purple']]
        self.shirt_color = random.choice(shirt_colors)
        self.hair_style = random.randint(0, 2)
        self.height_var = random.uniform(0.9, 1.1)

        self.x = -14.0
        self.target_x = -3.5 - queue_index * 1.6
        self.z = random.uniform(-0.15, 0.15)
        self.y = 0.0

        max_order = min(4, 1 + level // 3)
        self.order_quantity = random.randint(1, max_order)
        self.remaining_order = self.order_quantity
        self.is_special = random.random() < SPECIAL_CUSTOMER_CHANCE

        patience_reduction = level * 0.5
        self.max_patience = max(INITIAL_PATIENCE - patience_reduction, MIN_PATIENCE)
        self.patience = self.max_patience

        self.arrived = False
        self.leave_speed = 5.0
        self.bounce_timer = 0
        self.breath_offset = random.uniform(0, 6.28)

        # Walking animation
        self.walk_cycle = 0.0
        self.walk_speed = 2.8

        # FACING: 0 = facing right (walking toward grill), 1 = facing forward (at grill)
        self.facing = 0

        self.feedback_text = ""
        self.feedback_timer = 0
        self.feedback_color = COLORS['text_white']
        self.speech_bob = 0

    def update(self, dt):
        new_target = -3.5 - self.queue_index * 1.6
        if abs(new_target - self.target_x) > 0.1:
            self.target_x = new_target
            self.arrived = False

        if self.state in [CustomerState.SERVED, CustomerState.ANGRY]:
            self.x -= self.leave_speed * dt
            self.y = 0.0
            self.facing = 0  # face left when leaving
        elif not self.arrived:
            dx = self.target_x - self.x
            if dx > 0.05:
                self.x += self.walk_speed * dt
                self.walk_cycle += dt * 6.0
                self.y = abs(math.sin(self.walk_cycle)) * 0.06
                self.facing = 0  # facing right while walking toward grill
            else:
                self.x = self.target_x
                self.arrived = True
                self.y = 0.0
                self.walk_cycle = 0.0
                self.facing = 1  # face forward (toward chef) when at grill
        else:
            self.y = 0.0
            self.facing = 1

        if self.state == CustomerState.WAITING and self.arrived:
            self.patience -= dt
            if self.patience <= 0:
                self.patience = 0
                self.state = CustomerState.ANGRY

        self.breath_offset += dt * 2
        self.bounce_timer += dt * 3
        self.speech_bob += dt * 4

        if self.feedback_timer > 0:
            self.feedback_timer -= dt

    def serve(self, quantity=1):
        self.remaining_order -= quantity
        if self.remaining_order <= 0:
            self.remaining_order = 0
            self.state = CustomerState.SERVED
            self.feedback_text = "YUM!"
            self.feedback_color = COLORS['text_green']
            self.feedback_timer = 1.5
            return True
        else:
            self.feedback_text = f"{self.remaining_order}x more!"
            self.feedback_color = COLORS['text_gold']
            self.feedback_timer = 1.0
            return False

    def get_money(self):
        base = self.order_quantity * MONEY_PER_SUYA
        if self.is_special:
            base = int(base * SPECIAL_MULTIPLIER)
        return base

    def get_score(self):
        base = self.order_quantity * 100
        if self.is_special:
            base = int(base * SPECIAL_MULTIPLIER)
        patience_bonus = int((self.patience / self.max_patience) * 50)
        return base + patience_bonus

    def is_off_screen(self):
        return self.x < -16

    def draw_body(self):
        breath = math.sin(self.breath_offset) * 0.02
        h = self.height_var

        walk_bob = 0.0
        leg_swing = 0.0
        arm_swing = 0.0
        if not self.arrived and self.state == CustomerState.WAITING:
            walk_bob = abs(math.sin(self.walk_cycle)) * 0.06
            leg_swing = math.sin(self.walk_cycle) * 0.25
            arm_swing = math.sin(self.walk_cycle + math.pi) * 0.15

        if self.facing == 0:
            # Walking right: rotate body 90 degrees so front faces +X
            glPushMatrix()
            glTranslatef(self.x, 0, self.z)
            glRotatef(-90, 0, 1, 0)
            self._draw_body_local(h, breath, walk_bob, leg_swing, arm_swing)
            glPopMatrix()
        else:
            # At grill: standard forward-facing toward +Z
            glPushMatrix()
            glTranslatef(self.x, 0, self.z)
            self._draw_body_local(h, breath, walk_bob, leg_swing, arm_swing)
            glPopMatrix()

    def _draw_body_local(self, h, breath, walk_bob, leg_swing, arm_swing):
        """Draw body at local origin (0,0,0)."""
        gl_set_color(0.2, 0.15, 0.1)
        glPushMatrix()
        glTranslatef(-0.12, 0.7 * h + walk_bob, 0)
        glRotatef(leg_swing * 30, 0, 0, 1)
        draw_cylinder(0, -0.35 * h, 0, 0.07, 0.7 * h, (0.2, 0.15, 0.1))
        glPopMatrix()
        glPushMatrix()
        glTranslatef(0.12, 0.7 * h + walk_bob, 0)
        glRotatef(-leg_swing * 30, 0, 0, 1)
        draw_cylinder(0, -0.35 * h, 0, 0.07, 0.7 * h, (0.2, 0.15, 0.1))
        glPopMatrix()

        gl_set_color(*self.shirt_color)
        torso_y = 0.9 * h + breath + walk_bob
        draw_rounded_box(0, torso_y, 0, 0.45, 0.65 * h, 0.28, self.shirt_color, 0.04)

        base_arm_angle = 0
        if self.state == CustomerState.WAITING and self.arrived:
            base_arm_angle = math.sin(self.bounce_timer) * 0.08
        elif self.state == CustomerState.ANGRY:
            base_arm_angle = -0.6

        gl_set_color(*self.skin_color)
        glPushMatrix()
        glTranslatef(-0.28, torso_y + 0.15 * h, 0)
        glRotatef((base_arm_angle + arm_swing) * 25, 0, 0, 1)
        draw_cylinder(0, -0.1, 0, 0.055, 0.45 * h, self.skin_color)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(0.28, torso_y + 0.15 * h, 0)
        glRotatef((-base_arm_angle - arm_swing) * 25, 0, 0, 1)
        draw_cylinder(0, -0.1, 0, 0.055, 0.45 * h, self.skin_color)
        glPopMatrix()

        head_y = 1.45 * h + breath + walk_bob
        gl_set_color(*self.skin_color)
        draw_sphere(0, head_y, 0, 0.2 * h, self.skin_color)

        eye_y = head_y + 0.04 * h
        eye_z = 0.16 * h
        gl_set_color(0.1, 0.08, 0.05)
        if self.state == CustomerState.ANGRY:
            draw_cube(-0.07, eye_y, eye_z, 0.05, 0.015, 0.015, (0.1, 0.08, 0.05))
            draw_cube(0.07, eye_y, eye_z, 0.05, 0.015, 0.015, (0.1, 0.08, 0.05))
        else:
            draw_sphere(-0.07, eye_y, eye_z, 0.025, (0.1, 0.08, 0.05))
            draw_sphere(0.07, eye_y, eye_z, 0.025, (0.1, 0.08, 0.05))

        if self.hair_style == 0:
            gl_set_color(0.08, 0.04, 0.02)
            draw_sphere(0, head_y + 0.08 * h, 0, 0.22 * h, (0.08, 0.04, 0.02))
        elif self.hair_style == 1:
            gl_set_color(*self.shirt_color)
            draw_cylinder(0, head_y + 0.12 * h, 0, 0.22 * h, 0.07, self.shirt_color)
            draw_cube(0, head_y + 0.08 * h, 0.08, 0.25 * h, 0.035, 0.12, self.shirt_color)
        else:
            gl_set_color(0.4, 0.3, 0.2)
            draw_cylinder(0, head_y + 0.1 * h, 0, 0.21 * h, 0.1, (0.4, 0.3, 0.2))

    def draw(self):
        self.draw_body()

        if self.state == CustomerState.WAITING and self.arrived:
            bob = math.sin(self.speech_bob) * 0.05
            self._draw_speech_bubble_with_text(bob)

        if self.state == CustomerState.WAITING and self.arrived:
            self._draw_patience_bar()

        if self.is_special and self.state == CustomerState.WAITING:
            star_y = 1.85 * self.height_var + math.sin(self.speech_bob * 2) * 0.05
            gl_set_color(*COLORS['text_gold'])
            draw_sphere(self.x, star_y, self.z, 0.07, COLORS['text_gold'])

    def _draw_speech_bubble_with_text(self, bob):
        """Draw speech bubble with the order quantity as visible black text."""
        bx = self.x + 0.55
        by = 1.85 * self.height_var + bob
        bz = self.z + 0.2

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        draw_rounded_box(bx, by, bz, 0.75, 0.5, 0.12, COLORS['bubble_white'], 0.04, 0.9)
        gl_set_color(*COLORS['bubble_white'][:3], 0.9)
        glBegin(GL_TRIANGLES)
        glVertex3f(self.x + 0.22, 1.65 * self.height_var, bz)
        glVertex3f(bx - 0.28, by - 0.1, bz)
        glVertex3f(bx - 0.28, by + 0.08, bz)
        glEnd()
        glDisable(GL_BLEND)

        # === RENDER ORDER TEXT IN BUBBLE ===
        text_str = f"{self.order_quantity}x SUYA"
        if self.is_special:
            text_str = f"{self.order_quantity}x SUYA!"

        text_surf = pygame.font.SysFont('Arial', 20, bold=True).render(text_str, True, (20, 20, 20))
        text_data = pygame.image.tostring(text_surf, 'RGBA', True)
        tw, th = text_surf.get_width(), text_surf.get_height()

        glPushMatrix()
        glDisable(GL_LIGHTING)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, tw, th, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)

        text_x = bx
        text_y = by + 0.02
        text_z = bz + 0.07
        text_w = 0.55
        text_h = 0.20

        glColor4f(1, 1, 1, 1)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0)
        glVertex3f(text_x - text_w/2, text_y + text_h/2, text_z)
        glTexCoord2f(1, 0)
        glVertex3f(text_x + text_w/2, text_y + text_h/2, text_z)
        glTexCoord2f(1, 1)
        glVertex3f(text_x + text_w/2, text_y - text_h/2, text_z)
        glTexCoord2f(0, 1)
        glVertex3f(text_x - text_w/2, text_y - text_h/2, text_z)
        glEnd()

        glDeleteTextures(1, [tex_id])
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)
        glPopMatrix()

    def _draw_patience_bar(self):
        bar_x = self.x
        bar_y = 1.78 * self.height_var
        bar_z = self.z
        bar_w = 0.45
        bar_h = 0.05
        ratio = self.patience / self.max_patience
        if ratio > 0.5:
            color = COLORS['patience_green']
        elif ratio > 0.25:
            color = COLORS['patience_yellow']
        else:
            color = COLORS['patience_red']
        draw_cube(bar_x, bar_y, bar_z, bar_w, bar_h, 0.015, (0.15, 0.15, 0.15))
        if ratio > 0:
            draw_cube(bar_x - bar_w / 2 + (bar_w * ratio) / 2, bar_y, bar_z + 0.01,
                     bar_w * ratio, bar_h, 0.02, color)


# ============================================================
# ORDER MANAGER
# ============================================================

class OrderManager:
    def __init__(self):
        self.customers = []
        self.next_customer_id = 1
        self.spawn_timer = 0.0
        self.spawn_interval = random.uniform(CUSTOMER_SPAWN_MIN, CUSTOMER_SPAWN_MAX)
        self.max_customers = 5

    def update(self, dt, level):
        for customer in self.customers:
            customer.update(dt)

        self.customers = [c for c in self.customers if not c.is_off_screen()]

        waiting = self.get_waiting_customers()
        for i, customer in enumerate(waiting):
            customer.queue_index = i

        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval and len(self.customers) < self.max_customers:
            self.spawn_timer = 0.0
            new_customer = Customer3D(self.next_customer_id, level, queue_index=len(waiting))
            self.next_customer_id += 1
            self.customers.append(new_customer)
            self.spawn_interval = random.uniform(CUSTOMER_SPAWN_MIN, CUSTOMER_SPAWN_MAX)

    def get_waiting_customers(self):
        return [c for c in self.customers if c.state == CustomerState.WAITING]

    def get_first_waiting(self):
        waiting = self.get_waiting_customers()
        return waiting[0] if waiting else None

    def serve_customer(self, quantity):
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

    def get_angry_customers(self):
        return sum(1 for c in self.customers if c.state == CustomerState.ANGRY and c.x > -8)

    def draw(self):
        for customer in self.customers:
            customer.draw()


# ============================================================
# 3D PARTICLE SYSTEM
# ============================================================

class Particle3D:
    def __init__(self, x, y, z, vx, vy, vz, color, size, lifetime):
        self.x, self.y, self.z = x, y, z
        self.vx, self.vy, self.vz = vx, vy, vz
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.rotation = random.uniform(0, 360)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.z += self.vz * dt
        self.vy -= 1.5 * dt
        self.lifetime -= dt
        self.rotation += 90 * dt

    def draw(self):
        alpha = max(0, self.lifetime / self.max_lifetime)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.rotation, 1, 1, 0)
        s = self.size * alpha
        draw_cube(0, 0, 0, s, s, s, self.color[:3], alpha * (self.color[3] if len(self.color) > 3 else 1.0))
        glPopMatrix()
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_BLEND)

    def is_dead(self):
        return self.lifetime <= 0


class ParticleSystem3D:
    def __init__(self):
        self.particles = []

    def spawn(self, x, y, z, color, count=10, speed=2.0):
        for _ in range(count):
            angle = random.uniform(0, 6.28)
            elevation = random.uniform(0.3, 1.2)
            vel = random.uniform(speed * 0.5, speed)
            vx = vel * math.cos(angle) * math.cos(elevation)
            vy = vel * math.sin(elevation)
            vz = vel * math.sin(angle) * math.cos(elevation)
            lifetime = random.uniform(0.5, 1.5)
            size = random.uniform(0.03, 0.08)
            self.particles.append(Particle3D(x, y, z, vx, vy, vz, color, size, lifetime))

    def spawn_success(self, x, y, z):
        self.spawn(x, y, z, (*COLORS['patience_green'], 0.8), 20, 3.0)
        self.spawn(x, y, z, (*COLORS['text_gold'], 0.9), 12, 2.0)

    def spawn_fail(self, x, y, z):
        self.spawn(x, y, z, (*COLORS['text_red'], 0.8), 15, 2.5)

    def spawn_smoke(self, x, y, z):
        self.particles.append(Particle3D(
            x + random.uniform(-0.3, 0.3), y, z + random.uniform(-0.3, 0.3),
            random.uniform(-0.2, 0.2), random.uniform(0.5, 1.5), random.uniform(-0.2, 0.2),
            (0.5, 0.45, 0.4, 0.5), random.uniform(0.05, 0.14), random.uniform(1.5, 3.0)
        ))

    def spawn_spark(self, x, y, z):
        self.particles.append(Particle3D(
            x, y, z,
            random.uniform(-0.5, 0.5), random.uniform(0.5, 2.5), random.uniform(-0.5, 0.5),
            (*COLORS['fire_yellow'], 0.9), random.uniform(0.02, 0.05), random.uniform(0.2, 0.6)
        ))

    def update(self, dt):
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if not p.is_dead()]

    def draw(self):
        for p in self.particles:
            p.draw()


# ============================================================
# 3D SCENE
# ============================================================

class Scene3D:
    def __init__(self):
        self.time = 0
        self.lantern_sway = 0

    def update(self, dt):
        self.time += dt
        self.lantern_sway += dt * 1.5

    def draw_ground(self):
        gl_set_color(*COLORS['concrete'])
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)
        size = 15
        for i in range(-size, size, 2):
            for j in range(-size, size, 2):
                shade = 0.88 + 0.12 * ((i + j) % 4) / 3
                c = (COLORS['concrete'][0] * shade,
                     COLORS['concrete'][1] * shade,
                     COLORS['concrete'][2] * shade)
                gl_set_color(*c)
                glVertex3f(i, 0, j)
                glVertex3f(i + 2, 0, j)
                glVertex3f(i + 2, 0, j + 2)
                glVertex3f(i, 0, j + 2)
        glEnd()
        draw_cube(0, -0.02, -7, 20, 0.08, 0.4, COLORS['concrete_dark'])

    def draw_market_stalls(self):
        for i in range(-3, 4):
            if i == 0:
                continue
            x = i * 4.5
            z = -5.0
            draw_cube(x, 1.0, z, 2.0, 2.0, 1.5, (0.4, 0.25, 0.15))
            draw_cube(x, 2.35, z, 2.2, 0.1, 1.7, (0.5, 0.2, 0.1))
            draw_cube(x, 2.55, z, 1.6, 0.1, 1.5, (0.55, 0.22, 0.08))
            draw_cube(x, 0.6, z + 0.8, 1.8, 0.1, 0.4, (0.6, 0.4, 0.2))
            goods_colors = [
                (0.85, 0.2, 0.2), (0.2, 0.7, 0.3), (0.9, 0.85, 0.15),
                (0.2, 0.5, 0.9), (0.8, 0.35, 0.75), (0.95, 0.6, 0.15)
            ]
            for j in range(4):
                gx = x - 0.6 + j * 0.4
                gc = goods_colors[j % len(goods_colors)]
                draw_cube(gx, 0.85, z + 0.8, 0.22, 0.22, 0.22, gc)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            draw_cube(x, 2.15, z + 0.9, 1.8, 0.02, 0.5, (0.9, 0.5, 0.15), 0.5)
            glDisable(GL_BLEND)

    def draw_suya_stand(self):
        draw_rounded_box(0, 0.9, 2.0, 5.0, 1.0, 1.2, COLORS['wood'], 0.1)
        draw_cube(0, 1.45, 2.0, 5.2, 0.08, 1.4, COLORS['wood_light'])
        draw_cube(0, 0.9, 2.65, 4.8, 0.8, 0.05, COLORS['wood_dark'])
        gl_set_color(0.85, 0.55, 0.15)
        draw_cube(0, 1.25, 2.68, 4.6, 0.04, 0.02, (0.85, 0.55, 0.15))
        draw_cube(0, 0.55, 2.68, 4.6, 0.04, 0.02, (0.85, 0.55, 0.15))
        draw_cylinder(-1.8, 3.0, 2.7, 0.05, 3.0, COLORS['wood_dark'])
        draw_cylinder(1.8, 3.0, 2.7, 0.05, 3.0, COLORS['wood_dark'])
        draw_rounded_box(0, 4.2, 2.7, 4.2, 0.6, 0.12, COLORS['wood'], 0.08)
        draw_cube(0, 4.2, 2.76, 4.3, 0.7, 0.02, (0.1, 0.08, 0.05))
        draw_cube(0, 4.2, 2.78, 4.0, 0.5, 0.02, (0.85, 0.55, 0.15))
        for lx in [-1.5, 0, 1.5]:
            lantern_y = 3.8 + math.sin(self.lantern_sway + lx) * 0.05
            gl_set_color(0.3, 0.3, 0.3)
            draw_cylinder(lx, 4.0, 2.75, 0.008, 0.3, (0.3, 0.3, 0.3))
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE)
            draw_sphere(lx, lantern_y, 2.75, 0.1, COLORS['neon_glow'], 0.5)
            glDisable(GL_BLEND)

    def draw(self):
        self.draw_ground()
        self.draw_market_stalls()
        self.draw_suya_stand()


# ============================================================
# UI MANAGER
# ============================================================

class UIManager:
    def __init__(self):
        self.fonts = self._load_fonts()
        self.buttons = []
        self.title_pulse = 0
        self.bg_particles = []
        self.init_bg_particles()

    def _load_fonts(self):
        fonts = {}
        font_names = [
            'Segoe UI', 'Arial', 'Helvetica', 'DejaVu Sans',
            'Liberation Sans', 'FreeSans', 'Noto Sans'
        ]
        def find_font(size, bold=False):
            for name in font_names:
                try:
                    font = pygame.font.SysFont(name, size, bold=bold)
                    test = font.render("Test", True, (255, 255, 255))
                    if test.get_width() > 0:
                        return font
                except:
                    continue
            return pygame.font.Font(None, size)
        fonts['title'] = find_font(68, bold=True)
        fonts['subtitle'] = find_font(32, bold=True)
        fonts['large'] = find_font(44, bold=True)
        fonts['medium'] = find_font(26, bold=True)
        fonts['small'] = find_font(20)
        fonts['tiny'] = find_font(15)
        return fonts

    def init_bg_particles(self):
        for _ in range(30):
            self.bg_particles.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT),
                'size': random.randint(2, 5),
                'speed': random.uniform(0.3, 1.2),
                'alpha': random.randint(30, 80),
                'color': random.choice([
                    (255, 200, 50), (255, 140, 0), (255, 100, 0),
                    (200, 150, 50), (255, 220, 100)
                ])
            })

    def update_bg_particles(self, dt):
        for p in self.bg_particles:
            p['y'] -= p['speed'] * dt * 30
            if p['y'] < -10:
                p['y'] = SCREEN_HEIGHT + 10
                p['x'] = random.randint(0, SCREEN_WIDTH)

    def draw_bg_particles(self, surface):
        for p in self.bg_particles:
            s = pygame.Surface((p['size'] * 2, p['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*p['color'], p['alpha']), (p['size'], p['size']), p['size'])
            surface.blit(s, (int(p['x'] - p['size']), int(p['y'] - p['size'])))

    def create_button(self, rect, text, action, style='primary'):
        color_map = {
            'primary': {
                'base': COLORS['btn_primary'],
                'hover': COLORS['btn_primary_hover'],
                'press': COLORS['btn_primary_press'],
            },
            'danger': {
                'base': COLORS['btn_danger'],
                'hover': COLORS['btn_danger_hover'],
                'press': (0.60, 0.15, 0.10),
            },
            'action': {
                'base': COLORS['btn_action'],
                'hover': COLORS['btn_action_hover'],
                'press': (0.15, 0.45, 0.28),
            },
        }
        c = color_map.get(style, color_map['primary'])
        base = c['base']
        hover = c['hover']
        press = c['press']
        return {
            'rect': pygame.Rect(rect) if isinstance(rect, (tuple, list)) else rect,
            'text': text,
            'action': action,
            'style': style,
            'color': (int(base[0]*255), int(base[1]*255), int(base[2]*255)),
            'hover_color': (int(hover[0]*255), int(hover[1]*255), int(hover[2]*255)),
            'press_color': (int(press[0]*255), int(press[1]*255), int(press[2]*255)),
        }

    def draw_modern_button(self, surface, button, is_hovered=False, is_pressed=False):
        rect = button['rect']
        if is_pressed:
            color = button['press_color']
            y_offset = 2
        elif is_hovered:
            color = button['hover_color']
            y_offset = 0
        else:
            color = button['color']
            y_offset = 0
        shadow_rect = rect.copy()
        shadow_rect.move_ip(0, 4)
        shadow_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 80), shadow_surf.get_rect(), border_radius=14)
        surface.blit(shadow_surf, shadow_rect)
        btn_rect = rect.copy()
        btn_rect.move_ip(0, y_offset)
        pygame.draw.rect(surface, color, btn_rect, border_radius=14)
        highlight = pygame.Surface((btn_rect.width, btn_rect.height // 2), pygame.SRCALPHA)
        pygame.draw.rect(highlight, (255, 255, 255, 25), highlight.get_rect(), border_radius=14)
        surface.blit(highlight, (btn_rect.x, btn_rect.y))
        bottom = pygame.Surface((btn_rect.width, btn_rect.height // 3), pygame.SRCALPHA)
        pygame.draw.rect(bottom, (0, 0, 0, 30), bottom.get_rect(), border_radius=14)
        surface.blit(bottom, (btn_rect.x, btn_rect.y + btn_rect.height * 2 // 3))
        pygame.draw.rect(surface, (255, 255, 255, 50), btn_rect, 2, border_radius=14)
        draw_text_2d(surface, button['text'], self.fonts['medium'],
                    (255, 255, 255), btn_rect.center)

    def draw_main_menu(self, surface, high_scores, dt, has_save=False):
        self.title_pulse += dt * 3
        surface.fill((12, 7, 4))
        self.update_bg_particles(dt)
        self.draw_bg_particles(surface)
        banner = pygame.Surface((SCREEN_WIDTH, 180), pygame.SRCALPHA)
        for i in range(180):
            alpha = max(0, 40 - i // 5)
            pygame.draw.line(banner, (180, 100, 20, alpha), (0, i), (SCREEN_WIDTH, i))
        surface.blit(banner, (0, 0))
        pulse = abs(math.sin(self.title_pulse)) * 0.3 + 0.7
        glow_size = int(30 * pulse)
        title_surf = self.fonts['title'].render("SUYA RUSH", True, (255, 215, 0))
        glow_surf = pygame.Surface((title_surf.get_width() + glow_size * 2, 
                                    title_surf.get_height() + glow_size * 2), pygame.SRCALPHA)
        for r in range(glow_size, 0, -2):
            alpha = int(40 * (1 - r / glow_size) * pulse)
            glow_rect = title_surf.get_rect(center=(glow_surf.get_width()//2, glow_surf.get_height()//2))
            glow_rect.inflate_ip(r * 2, r * 2)
            pygame.draw.ellipse(glow_surf, (255, 180, 0, alpha), glow_rect)
        surface.blit(glow_surf, (SCREEN_WIDTH//2 - glow_surf.get_width()//2, 55 - glow_size))
        surface.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH//2, 100)))
        draw_text_2d(surface, "3D", self.fonts['large'], (255, 140, 0), 
                    (SCREEN_WIDTH//2 + 210, 100))
        draw_text_2d(surface, "Nigerian Street-Food Simulator", self.fonts['subtitle'],
                    (220, 200, 180), (SCREEN_WIDTH//2, 160))
        pygame.draw.line(surface, (200, 140, 40),
                        (SCREEN_WIDTH//2 - 220, 195),
                        (SCREEN_WIDTH//2 + 220, 195), 2)

        self.buttons = []
        button_configs = [("START GAME", "start", 'action')]
        if has_save:
            button_configs.append(("CONTINUE", "continue", 'action'))
        button_configs.extend([
            ("HOW TO PLAY", "instructions", 'primary'),
            ("UPGRADES", "shop", 'primary'),
            ("EXIT", "exit", 'danger'),
        ])

        button_y = 260
        for text, action, style in button_configs:
            rect = pygame.Rect(SCREEN_WIDTH//2 - 170, button_y, 340, 58)
            self.buttons.append(self.create_button(rect, text, action, style))
            button_y += 78

        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        for button in self.buttons:
            is_hovered = button['rect'].collidepoint(mouse_pos)
            is_pressed = is_hovered and mouse_pressed
            self.draw_modern_button(surface, button, is_hovered, is_pressed)

        panel = pygame.Surface((400, 100), pygame.SRCALPHA)
        pygame.draw.rect(panel, (25, 18, 12, 230), panel.get_rect(), border_radius=14)
        pygame.draw.rect(panel, (180, 130, 40, 100), panel.get_rect(), 2, border_radius=14)
        surface.blit(panel, (SCREEN_WIDTH//2 - 200, 590))
        draw_text_2d(surface, "HIGH SCORES", self.fonts['medium'],
                    (255, 215, 0), (SCREEN_WIDTH//2, 615))
        if high_scores:
            y = 645
            for i, score in enumerate(high_scores[:3]):
                medal_colors = [(255, 215, 0), (200, 200, 200), (205, 127, 50)]
                mc = medal_colors[i] if i < 3 else (255, 255, 255)
                text = f"{i+1}. {score.get('name', 'Player')} - {score.get('score', 0):,}"
                draw_text_2d(surface, text, self.fonts['small'], mc, (SCREEN_WIDTH//2, y))
                y += 24
        else:
            draw_text_2d(surface, "No scores yet - be the first!", self.fonts['small'],
                        (180, 180, 180), (SCREEN_WIDTH//2, 650))

    def draw_instructions(self, surface):
        surface.fill((12, 7, 4))
        self.draw_bg_particles(surface)
        draw_text_2d(surface, "HOW TO PLAY", self.fonts['title'],
                    (255, 215, 0), (SCREEN_WIDTH//2, 50))
        pygame.draw.line(surface, (200, 140, 40),
                        (SCREEN_WIDTH//2 - 180, 90),
                        (SCREEN_WIDTH//2 + 180, 90), 2)
        panel = pygame.Surface((900, 420), pygame.SRCALPHA)
        pygame.draw.rect(panel, (20, 14, 8, 240), panel.get_rect(), border_radius=16)
        pygame.draw.rect(panel, (180, 130, 40, 80), panel.get_rect(), 2, border_radius=16)
        surface.blit(panel, (SCREEN_WIDTH//2 - 450, 110))
        instructions = [
            ("You run a Suya (grilled meat) stand in a bustling Nigerian market!", (255, 220, 180), 'small'),
            ("", (255, 255, 255), 'small'),
            ("1. Customers arrive and order 1-4 sticks of suya", (230, 230, 230), 'small'),
            ("2. Click 'ADD SUYA' to place raw meat on the 3D grill", (230, 230, 230), 'small'),
            ("3. Watch the meat cook - green bar shows progress", (230, 230, 230), 'small'),
            ("4. Serve PERFECTLY cooked suya for maximum points!", (230, 230, 230), 'small'),
            ("5. Don't let it burn - burned suya wastes a slot", (255, 180, 180), 'small'),
            ("6. Click number buttons (1-4) to serve the first customer", (230, 230, 230), 'small'),
            ("7. Serve before their patience runs out!", (230, 230, 230), 'small'),
            ("", (255, 255, 255), 'small'),
            ("KEYBOARD SHORTCUTS:", (255, 215, 0), 'medium'),
            ("[SPACE] Add suya  |  [1-4] Serve customer  |  [D] Discard burned  |  [P] Pause", 
             (200, 230, 200), 'small'),
            ("", (255, 255, 255), 'small'),
            ("SPECIAL CUSTOMERS pay DOUBLE! Build COMBOs for bonus points!", (100, 255, 150), 'medium'),
        ]
        y = 135
        for line, color, font_key in instructions:
            draw_text_2d(surface, line, self.fonts[font_key], color, (SCREEN_WIDTH//2, y))
            y += 26 if font_key == 'small' else 32
        self.buttons = []
        back_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 80, 200, 52)
        self.buttons.append(self.create_button(back_rect, "BACK", "menu", 'primary'))
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            is_hovered = button['rect'].collidepoint(mouse_pos)
            self.draw_modern_button(surface, button, is_hovered)

    def draw_shop(self, surface, money, upgrades):
        surface.fill((12, 7, 4))
        self.draw_bg_particles(surface)
        draw_text_2d(surface, "SUYA STAND UPGRADES", self.fonts['title'],
                    (255, 215, 0), (SCREEN_WIDTH//2, 50))
        money_surf = self.fonts['large'].render(f"N{money:,}", True, (50, 255, 100))
        glow = pygame.Surface((money_surf.get_width() + 40, money_surf.get_height() + 20), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (50, 255, 100, 30), glow.get_rect())
        surface.blit(glow, (SCREEN_WIDTH//2 - glow.get_width()//2, 108))
        surface.blit(money_surf, money_surf.get_rect(center=(SCREEN_WIDTH//2, 125)))
        self.buttons = []
        upgrades_list = [
            ("Faster Grill", "cook_speed", 500, "Cook suya 25% faster per level", "Time is money!"),
            ("Patient Customers", "patience", 400, "Customers wait 2s longer per level", "Keep them happy!"),
            ("Extra Grill Slot", "grill_slots", 800, "Cook one more suya at once", "More capacity!"),
            ("Higher Profits", "profits", 600, "Earn 20% more Naira per level", "Cha-ching!"),
        ]
        y = 185
        for name, key, cost, desc, tagline in upgrades_list:
            card = pygame.Surface((940, 95), pygame.SRCALPHA)
            pygame.draw.rect(card, (30, 22, 14, 240), card.get_rect(), border_radius=14)
            pygame.draw.rect(card, (180, 130, 40, 80), card.get_rect(), 2, border_radius=14)
            surface.blit(card, (170, y))
            draw_text_2d(surface, name, self.fonts['medium'],
                        (255, 215, 0), (310, y + 25), center=False)
            draw_text_2d(surface, desc, self.fonts['small'],
                        (200, 200, 200), (310, y + 52), center=False)
            draw_text_2d(surface, tagline, self.fonts['tiny'],
                        (180, 160, 100), (310, y + 72), center=False)
            level = upgrades.get(key, 0)
            draw_text_2d(surface, f"Lv.{level}", self.fonts['small'],
                        (255, 200, 100), (720, y + 45))
            buy_rect = pygame.Rect(800, y + 22, 180, 52)
            can_afford = money >= cost
            buy_btn = self.create_button(buy_rect, f"N{cost}", f"buy_{key}", 
                                        'action' if can_afford else 'primary')
            buy_btn['cost'] = cost
            buy_btn['can_afford'] = can_afford
            self.buttons.append(buy_btn)
            if can_afford:
                mouse_pos = pygame.mouse.get_pos()
                is_hovered = buy_btn['rect'].collidepoint(mouse_pos)
                self.draw_modern_button(surface, buy_btn, is_hovered)
            else:
                pygame.draw.rect(surface, (50, 40, 35), buy_rect, border_radius=14)
                draw_text_2d(surface, f"N{cost}", self.fonts['medium'],
                            (120, 120, 120), buy_rect.center)
            y += 115
        back_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 70, 200, 52)
        self.buttons.append(self.create_button(back_rect, "BACK", "menu", 'primary'))
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            if button['action'] == "menu":
                is_hovered = button['rect'].collidepoint(mouse_pos)
                self.draw_modern_button(surface, button, is_hovered)

    def draw_game_hud(self, surface, score, money, combo, level, lives):
        hud = pygame.Surface((SCREEN_WIDTH, 70), pygame.SRCALPHA)
        for i in range(70):
            alpha = min(240, 180 + i)
            pygame.draw.line(hud, (10, 7, 5, alpha), (0, i), (SCREEN_WIDTH, i))
        surface.blit(hud, (0, 0))
        pygame.draw.line(surface, (200, 140, 40), (0, 70), (SCREEN_WIDTH, 70), 2)
        draw_text_2d(surface, f"Score: {score:,}", self.fonts['medium'],
                    (255, 215, 0), (100, 35))
        draw_text_2d(surface, f"N{money:,}", self.fonts['medium'],
                    (50, 255, 100), (320, 35))
        draw_text_2d(surface, f"Level {level}", self.fonts['medium'],
                    (255, 255, 255), (520, 35))
        draw_text_2d(surface, "Lives:", self.fonts['small'],
                    (220, 220, 220), (660, 35))
        for i in range(5):
            heart_color = (255, 60, 60) if i < lives else (50, 45, 40)
            hx = 730 + i * 28
            hy = 35
            pygame.draw.circle(surface, heart_color, (hx - 5, hy - 3), 6)
            pygame.draw.circle(surface, heart_color, (hx + 5, hy - 3), 6)
            points = [(hx, hy + 6), (hx - 10, hy - 2), (hx + 10, hy - 2)]
            pygame.draw.polygon(surface, heart_color, points)
        if combo > 1:
            combo_text = f"COMBO x{combo}!"
            combo_surf = self.fonts['large'].render(combo_text, True, (255, 215, 0))
            glow_w = combo_surf.get_width() + 40
            glow_h = combo_surf.get_height() + 20
            glow = pygame.Surface((glow_w, glow_h), pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (255, 180, 0, 45), glow.get_rect())
            surface.blit(glow, (SCREEN_WIDTH//2 - glow_w//2, 88))
            surface.blit(combo_surf, combo_surf.get_rect(center=(SCREEN_WIDTH//2, 105)))
            if combo >= 3:
                bonus = COMBO_BONUS[min(combo, len(COMBO_BONUS) - 1)]
                draw_text_2d(surface, f"+{bonus} pts", self.fonts['medium'],
                            (100, 255, 150), (SCREEN_WIDTH//2, 140))

    def draw_game_controls(self, surface, grill):
        self.buttons = []
        panel = pygame.Surface((SCREEN_WIDTH, 110), pygame.SRCALPHA)
        for i in range(110):
            alpha = min(230, 160 + i // 2)
            pygame.draw.line(panel, (10, 7, 5, alpha), (0, i), (SCREEN_WIDTH, i))
        surface.blit(panel, (0, SCREEN_HEIGHT - 110))
        pygame.draw.line(surface, (200, 140, 40), (0, SCREEN_HEIGHT - 110), 
                        (SCREEN_WIDTH, SCREEN_HEIGHT - 110), 2)
        add_rect = pygame.Rect(50, SCREEN_HEIGHT - 90, 170, 58)
        self.buttons.append(self.create_button(add_rect, "+ ADD SUYA", "add_suya", 'action'))
        serve_rect = pygame.Rect(240, SCREEN_HEIGHT - 90, 150, 58)
        can_serve = grill.get_ready_suya() > 0
        serve_style = 'action' if can_serve else 'primary'
        self.buttons.append(self.create_button(serve_rect, "SERVE", "serve", serve_style))
        ready = grill.get_ready_suya()
        status_color = (255, 215, 0) if ready > 0 else (180, 180, 180)
        draw_text_2d(surface, f"Ready: {ready}/{grill.num_slots}  |  Click SERVE to give suya to first customer!", self.fonts['medium'],
                    status_color, (SCREEN_WIDTH//2, SCREEN_HEIGHT - 62))
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        for button in self.buttons:
            is_hovered = button['rect'].collidepoint(mouse_pos)
            is_pressed = is_hovered and mouse_pressed
            self.draw_modern_button(surface, button, is_hovered, is_pressed)

    def draw_pause(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))
        panel = pygame.Surface((500, 380), pygame.SRCALPHA)
        pygame.draw.rect(panel, (20, 14, 8, 250), panel.get_rect(), border_radius=20)
        pygame.draw.rect(panel, (200, 140, 40, 100), panel.get_rect(), 3, border_radius=20)
        surface.blit(panel, (SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2 - 190))
        draw_text_2d(surface, "PAUSED", self.fonts['title'],
                    (255, 255, 255), (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 130))
        self.buttons = []
        resume_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 60, 300, 52)
        self.buttons.append(self.create_button(resume_rect, "RESUME", "resume", 'action'))
        save_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 5, 300, 52)
        self.buttons.append(self.create_button(save_rect, "SAVE & QUIT", "save_quit", 'primary'))
        menu_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 70, 300, 52)
        self.buttons.append(self.create_button(menu_rect, "QUIT TO MENU", "menu", 'danger'))
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        for button in self.buttons:
            is_hovered = button['rect'].collidepoint(mouse_pos)
            is_pressed = is_hovered and mouse_pressed
            self.draw_modern_button(surface, button, is_hovered, is_pressed)

    def draw_game_over(self, surface, score, high_score, high_scores):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        panel = pygame.Surface((600, 520), pygame.SRCALPHA)
        pygame.draw.rect(panel, (18, 12, 8, 250), panel.get_rect(), border_radius=24)
        pygame.draw.rect(panel, (200, 100, 30, 120), panel.get_rect(), 3, border_radius=24)
        surface.blit(panel, (SCREEN_WIDTH//2 - 300, 80))
        draw_text_2d(surface, "GAME OVER", self.fonts['title'],
                    (255, 80, 80), (SCREEN_WIDTH//2, 140))
        draw_text_2d(surface, f"Final Score: {score:,}", self.fonts['large'],
                    (255, 215, 0), (SCREEN_WIDTH//2, 210))
        if high_score:
            draw_text_2d(surface, "NEW HIGH SCORE!", self.fonts['large'],
                        (50, 255, 100), (SCREEN_WIDTH//2, 270))
        draw_text_2d(surface, "TOP SCORES", self.fonts['medium'],
                    (255, 255, 255), (SCREEN_WIDTH//2, 320))
        y = 355
        for i, hs in enumerate(high_scores[:5]):
            text = f"{i+1}. {hs.get('name', 'Player')} - {hs.get('score', 0):,}"
            colors = [(255, 215, 0), (220, 220, 220), (205, 170, 120), (255, 255, 255), (255, 255, 255)]
            color = colors[i] if i < len(colors) else (255, 255, 255)
            draw_text_2d(surface, text, self.fonts['small'], color,
                        (SCREEN_WIDTH//2, y))
            y += 30
        self.buttons = []
        restart_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 580, 300, 58)
        self.buttons.append(self.create_button(restart_rect, "PLAY AGAIN", "restart", 'action'))
        menu_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 650, 300, 58)
        self.buttons.append(self.create_button(menu_rect, "MAIN MENU", "menu", 'primary'))
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        for button in self.buttons:
            is_hovered = button['rect'].collidepoint(mouse_pos)
            is_pressed = is_hovered and mouse_pressed
            self.draw_modern_button(surface, button, is_hovered, is_pressed)


# ============================================================
# MAIN GAME CLASS
# ============================================================

class Game:
    def __init__(self):
        pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            pygame.DOUBLEBUF | pygame.OPENGL
        )
        pygame.display.set_caption("Suya Rush 3D - Nigerian Street-Food Simulator")
        pygame.mouse.set_visible(True)
        self.clock = pygame.time.Clock()
        self.running = True
        self.setup_opengl()
        self.scene = Scene3D()
        self.chef = Chef3D()
        self.grill = Grill3D()
        self.order_manager = OrderManager()
        self.particles = ParticleSystem3D()
        self.ui = UIManager()
        self.state = GameState.MENU
        self.score = 0
        self.money = 0
        self.combo = 0
        self.level = 1
        self.lives = 5
        self.total_served = 0
        self.total_angry = 0
        self.upgrades = {
            'cook_speed': 0,
            'patience': 0,
            'grill_slots': 0,
            'profits': 0,
        }
        self.high_scores = load_high_scores()
        self.camera_angle = 0.0
        self.camera_height = 3.0
        self.camera_distance = 7.5
        self.target_camera_angle = 0.0

    def setup_opengl(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glLightfv(GL_LIGHT0, GL_POSITION, [4.0, 10.0, 6.0, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.4, 0.3, 0.25, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 0.92, 0.78, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [0.5, 0.45, 0.35, 1.0])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [0.3, 0.3, 0.3, 1.0])
        glMaterialf(GL_FRONT, GL_SHININESS, 30.0)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(0.04, 0.03, 0.06, 1.0)

    def _perspective(self, fovy, aspect, near, far):
        f = 1.0 / math.tan(math.radians(fovy) / 2.0)
        nf = 1.0 / (near - far)
        m = [
            f / aspect, 0.0, 0.0, 0.0,
            0.0, f, 0.0, 0.0,
            0.0, 0.0, (far + near) * nf, -1.0,
            0.0, 0.0, 2.0 * far * near * nf, 0.0
        ]
        glMultMatrixf(m)

    def _look_at(self, eye_x, eye_y, eye_z, center_x, center_y, center_z, up_x, up_y, up_z):
        fx = center_x - eye_x
        fy = center_y - eye_y
        fz = center_z - eye_z
        flen = math.sqrt(fx*fx + fy*fy + fz*fz)
        if flen > 0:
            fx, fy, fz = fx/flen, fy/flen, fz/flen
        sx = fy * up_z - fz * up_y
        sy = fz * up_x - fx * up_z
        sz = fx * up_y - fy * up_x
        slen = math.sqrt(sx*sx + sy*sy + sz*sz)
        if slen > 0:
            sx, sy, sz = sx/slen, sy/slen, sz/slen
        ux = sy * fz - sz * fy
        uy = sz * fx - sx * fz
        uz = sx * fy - sy * fx
        m = [
            sx, ux, -fx, 0.0,
            sy, uy, -fy, 0.0,
            sz, uz, -fz, 0.0,
            0.0, 0.0, 0.0, 1.0
        ]
        glMultMatrixf(m)
        glTranslatef(-eye_x, -eye_y, -eye_z)

    def setup_camera(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        self._perspective(50, SCREEN_WIDTH / SCREEN_HEIGHT, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.camera_angle += (self.target_camera_angle - self.camera_angle) * 0.05
        eye_x = math.sin(self.camera_angle) * 1.5
        eye_y = self.camera_height
        eye_z = self.camera_distance
        self._look_at(
            eye_x, eye_y, eye_z,
            0.0, 1.2, 0.0,
            0.0, 1.0, 0.0
        )

    def apply_upgrades(self):
        speed_bonus = 1.0 + self.upgrades['cook_speed'] * 0.25
        self.grill.cook_speed = speed_bonus
        extra_slots = self.upgrades['grill_slots']
        self.grill.num_slots = self.grill.max_slots + extra_slots

    def has_save_game(self):
        return os.path.exists('suya_rush_save.json')

    def save_game(self):
        save_data = {
            'score': self.score,
            'money': self.money,
            'combo': self.combo,
            'level': self.level,
            'lives': self.lives,
            'total_served': self.total_served,
            'total_angry': self.total_angry,
            'upgrades': self.upgrades,
            'grill_max_slots': self.grill.max_slots,
            'date': time.strftime('%Y-%m-%d %H:%M:%S'),
        }
        try:
            with open('suya_rush_save.json', 'w') as f:
                json.dump(save_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Save failed: {e}")
            return False

    def load_game(self):
        try:
            with open('suya_rush_save.json', 'r') as f:
                save_data = json.load(f)
            self.score = save_data.get('score', 0)
            self.money = save_data.get('money', 0)
            self.combo = save_data.get('combo', 0)
            self.level = save_data.get('level', 1)
            self.lives = save_data.get('lives', 5)
            self.total_served = save_data.get('total_served', 0)
            self.total_angry = save_data.get('total_angry', 0)
            self.upgrades = save_data.get('upgrades', {
                'cook_speed': 0, 'patience': 0, 'grill_slots': 0, 'profits': 0
            })
            base_slots = save_data.get('grill_max_slots', 6)
            self.grill = Grill3D(base_slots)
            self.apply_upgrades()
            self.order_manager = OrderManager()
            self.particles = ParticleSystem3D()
            return True
        except Exception as e:
            print(f"Load failed: {e}")
            return False

    def reset_game(self):
        self.grill = Grill3D(self.grill.max_slots + self.upgrades.get('grill_slots', 0))
        self.apply_upgrades()
        self.order_manager = OrderManager()
        self.particles = ParticleSystem3D()
        self.score = 0
        self.money = 0
        self.combo = 0
        self.level = 1
        self.lives = 5
        self.total_served = 0
        self.total_angry = 0
        if os.path.exists('suya_rush_save.json'):
            os.remove('suya_rush_save.json')

    def check_level_up(self):
        if self.total_served >= self.level * 8:
            self.level += 1
            self.particles.spawn_success(0, 3, 0)

    def serve_one_suya(self):
        """Serve 1 cooked suya to the first waiting customer."""
        ready = self.grill.get_ready_suya()
        if ready < 1:
            self.particles.spawn_fail(-3, 1.5, 0)
            return
        customer = self.order_manager.get_first_waiting()
        if customer is None:
            self.particles.spawn_fail(-3, 1.5, 0)
            return
        # Take 1 suya from grill
        self.grill.take_suya(1)
        # Serve customer (partial or full)
        fully_served = customer.serve(1)
        if fully_served:
            profit_mult = 1.0 + self.upgrades['profits'] * 0.2
            earned = int(customer.get_money() * profit_mult)
            points = customer.get_score()
            self.combo += 1
            combo_bonus = COMBO_BONUS[min(self.combo, len(COMBO_BONUS) - 1)]
            points += combo_bonus
            self.score += points
            self.money += earned
            self.total_served += 1
            self.particles.spawn_success(customer.x, 2.0, customer.z)
            self.check_level_up()
        else:
            # Partial serve - customer wants more
            self.particles.spawn_success(customer.x, 2.0, customer.z)

    def game_over(self):
        self.state = GameState.GAME_OVER
        is_high = False
        if not self.high_scores or self.score > self.high_scores[0].get('score', 0):
            is_high = True
        self.high_scores.append({
            'name': 'Player',
            'score': self.score,
            'level': self.level,
            'date': time.strftime('%Y-%m-%d')
        })
        self.high_scores.sort(key=lambda x: x['score'], reverse=True)
        self.high_scores = self.high_scores[:10]
        save_high_scores(self.high_scores)
        if os.path.exists('suya_rush_save.json'):
            os.remove('suya_rush_save.json')

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                    elif self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING
                    elif self.state in [GameState.INSTRUCTIONS, GameState.SHOP]:
                        self.state = GameState.MENU
                if event.key == pygame.K_p:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                    elif self.state == GameState.PAUSED:
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
                        elif action == "continue":
                            if self.load_game():
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
                        elif action == "resume":
                            self.state = GameState.PLAYING
                        elif action == "save_quit":
                            self.save_game()
                            self.state = GameState.MENU
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

    def update(self, dt):
        if self.state == GameState.MENU:
            return
        if self.state != GameState.PLAYING:
            return
        self.scene.update(dt)
        self.chef.update(dt)
        self.grill.update(dt)
        self.order_manager.update(dt, self.level)
        self.particles.update(dt)
        angry_count = self.order_manager.get_angry_customers()
        if angry_count > self.total_angry:
            new_angry = angry_count - self.total_angry
            self.total_angry = angry_count
            self.lives -= new_angry
            self.combo = 0
            if self.lives <= 0:
                self.game_over()
        if random.random() < 0.08:
            self.particles.spawn_smoke(0, 1.3, 0)
        if random.random() < 0.04:
            self.particles.spawn_spark(
                random.uniform(-2, 2), 0.9, random.uniform(-0.3, 0.3)
            )


    def render_3d(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.setup_camera()
        self.scene.draw()
        self.chef.draw()
        self.grill.draw()
        self.order_manager.draw()
        self.particles.draw()

    def render_ui(self):
        ui_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        ui_surface.fill((0, 0, 0, 0))
        dt = self.clock.get_time() / 1000.0
        if self.state == GameState.MENU:
            self.ui.draw_main_menu(ui_surface, self.high_scores, dt, self.has_save_game())
        elif self.state == GameState.INSTRUCTIONS:
            self.ui.draw_instructions(ui_surface)
        elif self.state == GameState.SHOP:
            self.ui.draw_shop(ui_surface, self.money, self.upgrades)
        elif self.state in [GameState.PLAYING, GameState.PAUSED, GameState.GAME_OVER]:
            self.ui.draw_game_hud(ui_surface, self.score, self.money,
                                 self.combo, self.level, self.lives)
            self.ui.draw_game_controls(ui_surface, self.grill)
            if self.state == GameState.PAUSED:
                self.ui.draw_pause(ui_surface)
            elif self.state == GameState.GAME_OVER:
                is_high = (self.score > (self.high_scores[1].get('score', 0) 
                           if len(self.high_scores) > 1 else 0))
                self.ui.draw_game_over(ui_surface, self.score, is_high, self.high_scores)
        ui_data = pygame.image.tostring(ui_surface, 'RGBA', True)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        tex_id = glGenTextures(1)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA,
            SCREEN_WIDTH, SCREEN_HEIGHT,
            0, GL_RGBA, GL_UNSIGNED_BYTE, ui_data
        )
        glColor4f(1, 1, 1, 1)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0)
        glVertex2f(0, 0)
        glTexCoord2f(1, 0)
        glVertex2f(SCREEN_WIDTH, 0)
        glTexCoord2f(1, 1)
        glVertex2f(SCREEN_WIDTH, SCREEN_HEIGHT)
        glTexCoord2f(0, 1)
        glVertex2f(0, SCREEN_HEIGHT)
        glEnd()
        glDeleteTextures(1, [tex_id])
        glDisable(GL_TEXTURE_2D)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

    def draw(self):
        self.render_3d()
        self.render_ui()
        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()


if __name__ == "__main__":
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()