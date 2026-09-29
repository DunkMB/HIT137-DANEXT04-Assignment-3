print("=" * 50)
print("HIT137 - Software Now - Assignment 3")
print("Group Name: DAN/EXT04")
print("=" * 50)
print("Group Members:")
print("_" * 50)
print(f"{'Amber Francis':<20} {'s403747':>20}")
print(f"{'Darren Bragg':<20} {'s406821':>20}")
print(f"{'Duncan Brown':<20} {'s407728':>20}")
print(f"{'Jonathan Falkner':<20} {'s400817':>20}")
print("_" * 50)
print(" " * 50)
print(" " * 50)

import cv2
import numpy as np
import random
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
from abc import ABC, abstractmethod

#Amber section




#Darren section


#Solving the puzzle (tile interactions)

def handle_left_click(self, event):
    if self.original_cv_image is None or self.is_solved:
        return

    # Map coordinates to grid position
    c = event.x // self.tile_width
    r = event.y // self.tile_height
    if r >= self.grid_size or c >= self.grid_size:
        return

    # Shift + left click flips the tile; ordinary left click selects/swaps tiles
    if event.state & 0x0001 and event.num == 1:
        self.grid[r][c].shift()
        return

    # Tile selection and swapping
    if self.selected_tile_pos is None:
        self.selected_tile_pos = (r, c)
        self.highlight_selected_tile(r, c)
        self.render_displays()
        return

    sr, sc = self.selected_tile_pos
    if (sr, sc) == (r, c):
        # Deselect tile if same tile clicked again
        self.selected_tile_pos = None
        self.render_displays()
    else:
        # Different tile chosen, swap
        self.grid[sr][sc], self.grid[r][c] = self.grid[r][c], self.grid[sr][sc]
        self.selected_tile_pos = None
        self.register_move()

def handle_right_click(self, event):
    if self.original_cv_image is None or self.is_solved:
        return

    c = event.x // self.tile_width
    r = event.y // self.tile_height
    if r >= self.grid_size or c >= self.grid_size:
        return

#Right click 90 degrees clockwise rotation
    self.grid[r][c].rotate_90_clockwise()
    self.register_move()

def register_move(self):
    self.move_count += 1
    self.update_move_count_display()
    self.check_if_solved() 


#Duncan section
class ImagePuzzleApp:
    def _build_ui(self):
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(fill=tk.X)
# Image insert button
        ttk.Button(control_frame, text="Load Image", command=self.load_image).pack(side=tk.LEFT, padx=5)

        ttk.Label(control_frame, text="Grid Size:").pack(side=tk.LEFT, padx=5)
        grid_combobox = ttk.Combobox(control_frame, textvariable=self.grid_size_var, values=[3, 4, 5], state="readonly", width=5)
        grid_combobox.pack(side=tk.LEFT, padx=5)
# Load the image and size/crop it.
    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if not file_path:
            return

        usr_img = cv2.imread(file_path)
        if usr_img is None:
            messagebox.showerror("Error", "Failed to load image file.")
            return

        target_dim = 400
        grid_size = self.grid_size_var.get()

        h, w, _ = usr_img.shape
        min_dim = min(h, w)
        crop_h = (min_dim // grid_size) * grid_size
        crop_w = (min_dim // grid_size) * grid_size

        start_y = (h - crop_h) // 2
        start_x = (w - crop_w) // 2
        cropped = usr_img[start_y:start_y + crop_h, start_x:start_x + crop_w]

        final_dim = (target_dim // grid_size) * grid_size
        resized_img = cv2.resize(cropped, (final_dim, final_dim))
        self.puzzle = Puzzle(resized_img, grid_size)
        self.puzzle.scramble()
        self.selected_tile_pos = None
        self.moves_count = 0
        self.hints_used = 0
        self.active_hint = None
        self.is_solved = False
# Add these in later
        # self.hint_button.config(state=tk.NORMAL, text=f"Hint ({self.max_hints} left)")
        # self.solve_button.config(state=tk.NORMAL)

        self.update_display()

# This line gets added to the whole code in its proper place. Activate later.
        # self.puzzle = Puzzle(resized_img, grid_size)

