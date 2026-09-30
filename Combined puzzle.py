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

import cv2
import numpy as np
import random
import copy
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageOps, ImageDraw


# JONATHAN SECTION: IMAGE TRANSFORMATION & PROCESSING 
class ImageSplit:
    def split_image(image, grid_size):
        """Splits an image into a list of tiles based on grid_size (rows, cols)."""
        rows, cols = grid_size
        tile_height = image.shape[0] // rows
        tile_width = image.shape[1] // cols
        tiles = []

        for r in range(rows):
            for c in range(cols):
                tile = image[r * tile_height:(r + 1) * tile_height, c * tile_width:(c + 1) * tile_width]
                tiles.append(tile)

        return tiles

    
    def rotation_sequence(tile, angle):
        """Rotates a single image tile by a given angle."""
        (h, w) = tile.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(tile, M, (w, h))
        return rotated

    
    def flip_sequence(tile, flip_axis):
        """Flips a single tile image along horizontal or vertical axis."""
        return cv2.flip(tile, flip_axis)

    
    def swap_sequence(tiles, pos1, pos2, columns):
        """Swaps two tiles given 2D coordinates."""
        index1 = pos1[0] * columns + pos1[1]
        index2 = pos2[0] * columns + pos2[1]
        tiles[index1], tiles[index2] = tiles[index2], tiles[index1]
        return tiles

    
    def apply_transformations(tiles):
        """Applies random transformations (rotate, flip, swap) to a list of tiles."""
        transformed_tiles = list(tiles)
        operations = ('rotate', 'flip', 'swap')

        for index in range(len(transformed_tiles)):
            operation = random.choice(operations)

            if operation == 'rotate':
                angle = random.choice((90, 180, 270))
                transformed_tiles[index] = ImageSplit.rotation_sequence(transformed_tiles[index], angle)

            elif operation == 'flip':
                flip_axis = random.choice((0, 1))
                transformed_tiles[index] = ImageSplit.flip_sequence(transformed_tiles[index], flip_axis)

            else:
                second_index = random.choice([u for u in range(len(transformed_tiles)) if u != index])
                transformed_tiles[index], transformed_tiles[second_index] = (
                    transformed_tiles[second_index], transformed_tiles[index]
                )

        return transformed_tiles


#  PUZZLE CORE LOGIC 
class PuzzleTile:
    def __init__(self, tile_id, cv_img):
        self.tile_id = tile_id
        self.original_cv_img = cv_img
        self.current_cv_img = cv_img.copy()
        self.rotation = 0  # 0, 90, 180, 270
        self.flipped = False

    def rotate_90_clockwise(self):
        self.rotation = (self.rotation + 90) % 360
        self.current_cv_img = cv2.rotate(self.current_cv_img, cv2.ROTATE_90_CLOCKWISE)

    def shift(self):
        """Flips the tile horizontally (mirroring action)."""
        self.flipped = not self.flipped
        self.current_cv_img = cv2.flip(self.current_cv_img, 1)


class Puzzle:
    def __init__(self, resized_img, grid_size):
        self.grid_size = grid_size
        self.tiles_list = []
        
        # Split image using Jonathan's helper
        raw_tiles = ImageSplit.split_image(resized_img, (grid_size, grid_size))
        for idx, t in enumerate(raw_tiles):
            self.tiles_list.append(PuzzleTile(idx + 1, t))

        # Store solved grid
        self.solved_grid = []
        for r in range(grid_size):
            row = []
            for c in range(grid_size):
                row.append(self.tiles_list[r * grid_size + c])
            self.solved_grid.append(row)

        # Build initial working grid
        self.grid = copy.deepcopy(self.solved_grid)

    def scramble(self):
        """Scrambles grid positions, rotations, and flips."""
        flat_grid = [tile for row in self.grid for tile in row]
        random.shuffle(flat_grid)
        
        for tile in flat_grid:
            # Apply random rotation
            rot_times = random.choice([0, 1, 2, 3])
            for _ in range(rot_times):
                tile.rotate_90_clockwise()
            
            # Apply random flip
            if random.choice([True, False]):
                tile.shift()

        # Reconstruct grid
        self.grid = []
        for r in range(self.grid_size):
            row = []
            for c in range(self.grid_size):
                row.append(flat_grid[r * self.grid_size + c])
            self.grid.append(row)


#  MAIN APPLICATION CLASS (COMBINING DARREN, DUNCAN & AMBER) 
class ImagePuzzleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DAN/EXT04 - Combined Puzzle Game")
        
        self.grid_size_var = tk.IntVar(value=3)
        self.original_cv_image = None
        self.puzzle = None
        
        self.tile_width = 100
        self.tile_height = 100
        self.grid_size = 3
        
        self.selected_tile_pos = None
        self.move_count = 0
        self.hints_used = 0
        self.max_hints = 3
        self.start_time = None
        self.running = False
        self.is_solved = False
        self.active_hint = None

        self._build_ui()

    def _build_ui(self):
        # Duncan's control frame
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(fill=tk.X)

        ttk.Button(control_frame, text="Load Image", command=self.load_image).pack(side=tk.LEFT, padx=5)
        ttk.Label(control_frame, text="Grid Size:").pack(side=tk.LEFT, padx=5)
        grid_combobox = ttk.Combobox(control_frame, textvariable=self.grid_size_var, values=[3, 4, 5], state="readonly", width=5)
        grid_combobox.pack(side=tk.LEFT, padx=5)

        self.hint_button = ttk.Button(control_frame, text=f"Hint ({self.max_hints} left)", command=self.show_hint, state=tk.DISABLED)
        self.hint_button.pack(side=tk.LEFT, padx=5)

        self.solve_button = ttk.Button(control_frame, text="Solve", command=self.solve_puzzle, state=tk.DISABLED)
        self.solve_button.pack(side=tk.LEFT, padx=5)

        # Info & Timer Label (Amber)
        self.info_label = tk.Label(self.root, text="Moves: 0 | Time: 0s | Incorrect: 0 | Hints: 0/3", font=("Arial", 12))
        self.info_label.pack(pady=5)

        # Boards frame
        self.boards_frame = tk.Frame(self.root)
        self.boards_frame.pack(pady=10)

        # SWAPPED: Solved reference frame on LEFT (column 0)
        self.solved_frame = tk.Frame(self.boards_frame, bd=2, relief=tk.SUNKEN)
        self.solved_frame.grid(row=0, column=0, padx=10)

        # SWAPPED: Puzzle frame on RIGHT (column 1)
        self.puzzle_frame = tk.Frame(self.boards_frame, bd=2, relief=tk.SUNKEN)
        self.puzzle_frame.grid(row=0, column=1, padx=10)

        self.buttons_grid = []
        self.solved_buttons_grid = []

        self.update_timer()

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

        self.original_cv_image = usr_img
        target_dim = 400
        grid_size = self.grid_size_var.get()
        self.grid_size = grid_size

        h, w, _ = usr_img.shape
        min_dim = min(h, w)
        crop_h = (min_dim // grid_size) * grid_size
        crop_w = (min_dim // grid_size) * grid_size

        start_y = (h - crop_h) // 2
        start_x = (w - crop_w) // 2
        cropped = usr_img[start_y:start_y + crop_h, start_x:start_x + crop_w]

        final_dim = (target_dim // grid_size) * grid_size
        resized_img = cv2.resize(cropped, (final_dim, final_dim))
        
        self.tile_width = final_dim // grid_size
        self.tile_height = final_dim // grid_size

        self.puzzle = Puzzle(resized_img, grid_size)
        self.puzzle.scramble()
        
        self.selected_tile_pos = None
        self.move_count = 0
        self.hints_used = 0
        self.active_hint = None
        self.is_solved = False
        self.start_time = time.time()
        self.running = True

        self.hint_button.config(state=tk.NORMAL, text=f"Hint ({self.max_hints - self.hints_used} left)")
        self.solve_button.config(state=tk.NORMAL)

        self._create_board_buttons()
        self.render_displays()

    def _create_board_buttons(self):
        # Clear existing buttons
        for widget in self.puzzle_frame.winfo_children():
            widget.destroy()
        for widget in self.solved_frame.winfo_children():
            widget.destroy()

        self.buttons_grid = []
        self.solved_buttons_grid = []

        for r in range(self.grid_size):
            row_btns = []
            solved_row_btns = []
            for c in range(self.grid_size):
                # Interactive puzzle button
                btn = tk.Button(self.puzzle_frame, width=self.tile_width, height=self.tile_height)
                btn.grid(row=r, column=c)
                btn.bind("<Button-1>", lambda event, arg_r=r, arg_c=c: self.handle_left_click_event(event, arg_r, arg_c))
                btn.bind("<Button-3>", lambda event, arg_r=r, arg_c=c: self.handle_right_click_event(event, arg_r, arg_c))
                row_btns.append(btn)

                # Solved reference button
                s_btn = tk.Button(self.solved_frame, width=self.tile_width, height=self.tile_height)
                s_btn.grid(row=r, column=c)
                solved_row_btns.append(s_btn)

            self.buttons_grid.append(row_btns)
            self.solved_buttons_grid.append(solved_row_btns)

    #  DARREN SECTION & INTEGRATION: USER INPUT LOGIC 
    def handle_left_click_event(self, event, r, c):
        if self.original_cv_image is None or self.is_solved:
            return

        # Shift + Left click flips (Darren)
        if event.state & 0x0001:
            self.puzzle.grid[r][c].shift()
            self.register_move()
            return

        # Tile selection & swapping
        if self.selected_tile_pos is None:
            self.selected_tile_pos = (r, c)
            self.render_displays()
            return

        sr, sc = self.selected_tile_pos
        if (sr, sc) == (r, c):
            self.selected_tile_pos = None
            self.render_displays()
        else:
            # Swap tiles
            self.puzzle.grid[sr][sc], self.puzzle.grid[r][c] = self.puzzle.grid[r][c], self.puzzle.grid[sr][sc]
            self.selected_tile_pos = None
            self.register_move()

    def handle_right_click_event(self, event, r, c):
        if self.original_cv_image is None or self.is_solved:
            return

        # Right-click 90 degrees clockwise rotation (Darren)
        self.puzzle.grid[r][c].rotate_90_clockwise()
        self.register_move()

    def register_move(self):
        self.move_count += 1
        self.active_hint = None  # Reset active hint on move
        self.render_displays()
        self.check_if_solved()

    #  DISPLAY & RENDER LOGIC 
    def render_displays(self):
        if not self.puzzle:
            return

        # Render current puzzle grid
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                tile = self.puzzle.grid[r][c]
                cv_img = cv2.cvtColor(tile.current_cv_img, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(cv_img)

                # Draw hint if active
                if self.active_hint and self.active_hint['puzzle_pos'] == (r, c):
                    pil_img = self._draw_hint_overlay(pil_img)

                photo = ImageTk.PhotoImage(pil_img)
                btn = self.buttons_grid[r][c]
                btn.config(image=photo)
                btn.image = photo  # keep reference

                # Highlight selected tile
                if self.selected_tile_pos == (r, c):
                    btn.config(highlightbackground="yellow", highlightcolor="yellow", highlightthickness=3)
                else:
                    btn.config(highlightthickness=0)

        # Render solved reference grid
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                tile = self.puzzle.solved_grid[r][c]
                cv_img = cv2.cvtColor(tile.original_cv_img, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(cv_img)

                if self.active_hint and self.active_hint['solved_pos'] == (r, c):
                    pil_img = self._draw_hint_overlay(pil_img)

                photo = ImageTk.PhotoImage(pil_img)
                s_btn = self.solved_buttons_grid[r][c]
                s_btn.config(image=photo)
                s_btn.image = photo

        self.update_move_count_display()

    def _draw_hint_overlay(self, pil_img):
        """Draws Amber's blue circle hint overlay onto a PIL Image."""
        img_copy = pil_img.copy()
        draw = ImageDraw.Draw(img_copy)
        center_x = img_copy.width // 2
        center_y = img_copy.height // 2
        radius = min(center_x, center_y) // 1.2
        draw.ellipse(
            (center_x - radius, center_y - radius, center_x + radius, center_y + radius),
            outline="blue",
            width=5
        )
        return img_copy

    def update_move_count_display(self):
        incorrect = 0
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                current = self.puzzle.grid[r][c]
                target = self.puzzle.solved_grid[r][c]
                if current.tile_id != target.tile_id or current.rotation != 0 or current.flipped:
                    incorrect += 1

        elapsed = int(time.time() - self.start_time) if self.running else 0
        self.info_label.config(
            text=f"Moves: {self.move_count} | Time: {elapsed}s | Incorrect: {incorrect} | Hints: {self.hints_used}/{self.max_hints}"
        )

    def update_timer(self):
        if self.running and not self.is_solved:
            self.update_move_count_display()
        self.root.after(500, self.update_timer)

    def show_hint(self):
        if self.hints_used >= self.max_hints:
            messagebox.showinfo("No Hints Left", "You have used all available hints!")
            return

        # Find ALL incorrect tiles first
        incorrect_tiles = []
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                curr_tile = self.puzzle.grid[r][c]
                target_tile = self.puzzle.solved_grid[r][c]

                if curr_tile.tile_id != target_tile.tile_id or curr_tile.rotation != 0 or curr_tile.flipped:
                    incorrect_tiles.append((r, c, curr_tile))

        if incorrect_tiles:
            # Pick a random incorrect tile from the list
            r, c, curr_tile = random.choice(incorrect_tiles)

            # Locate target solved coordinates for this tile
            for sr in range(self.grid_size):
                for sc in range(self.grid_size):
                    if self.puzzle.solved_grid[sr][sc].tile_id == curr_tile.tile_id:
                        self.active_hint = {
                            'puzzle_pos': (r, c),
                            'solved_pos': (sr, sc)
                        }
                        break

            self.hints_used += 1
            self.hint_button.config(text=f"Hint ({self.max_hints - self.hints_used} left)")
            self.render_displays()

    def solve_puzzle(self):
        """Restores grid to the solved state directly (Amber)."""
        self.puzzle.grid = copy.deepcopy(self.puzzle.solved_grid)
        self.active_hint = None
        self.render_displays()
        self.check_if_solved()

    def check_if_solved(self):
        solved = True
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                current = self.puzzle.grid[r][c]
                target = self.puzzle.solved_grid[r][c]
                if current.tile_id != target.tile_id or current.rotation != 0 or current.flipped:
                    solved = False
                    break
            if not solved:
                break

        if solved:
            self.is_solved = True
            self.running = False
            elapsed = int(time.time() - self.start_time)
            messagebox.showinfo(
                "Puzzle Solved",
                f"Congratulations!\nMoves: {self.move_count}\nTime: {elapsed}s\nHints Used: {self.hints_used}/{self.max_hints}"
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = ImagePuzzleApp(root)
    root.mainloop()