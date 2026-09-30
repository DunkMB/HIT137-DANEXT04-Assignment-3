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
import random, copy, time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageOps, ImageDraw
from abc import ABC, abstractmethod

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
# Jonathan section

class ImageSplit:
   class ImageSplit:

    def split_image(image, grid_size):
        rows, cols = grid_size
        tile_height = image.shape[0] // rows
        tile_width = image.shape[1] // cols
        tiles = []

        for r in range(rows):
            for c in range(cols):
                tile = image[r * tile_height:(r + 1) * tile_height, c * tile_width:(c + 1) * tile_width]
                tiles.append(tile)

        return tiles

    grid_map = {
        '3x3': (3, 3),
        '4x4': (4, 4),
        '5x5': (5, 5)
    }

    im = cv2.imread('image.jpg')
    im = cv2.resize(im, (400, 400))
    grid_size = random.choice(list(grid_map.values()))

    tiles = []
    for r in range(grid_size[0]):
        for c in range(grid_size[1]):
            tile = im[r * (400 // grid_size[0]):(r + 1) * (400 // grid_size[0]), c * (400 // grid_size[1]):(c + 1) * (400 // grid_size[1])]
            tiles.append(tile)

    def angle():
        angle_options = {90: "90°", 180: "180°", 270: "270°"}
        rotation_angle = random.choice(list(angle_options.keys()))
        return rotation_angle

    def rotation_sequence(tiles, angle):
        (h,w) =tiles.shape[:2]
        center = (w // 2, h // 2)
        M =cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(tiles, M, (w,h))
        return rotated

    def flip_sequence(grid):
        flip_options = [1, 0]
        flip = random.choice(flip_options)
        flipped = cv2.flip(grid, flip)
        return flipped

    def swap_sequence(tiles, pos1, pos2, columns):
        index1 = pos1[0] * columns + pos1[1]
        index2 = pos2[0] * columns + pos2[1]
        tiles[index1], tiles[index2] = tiles[index2], tiles[index1]
        return tiles

    def apply_transformations(tiles):
        transformed_tiles = list(tiles)
        operations = ('rotate', 'flip', 'swap')

        for index in range(len(transformed_tiles)):
            operation = random.choice(operations)

            if operation == 'rotate':
                angle = random.choice((90, 180, 270))
                transformed_tiles [index] = ImageSplit.rotation_sequence(transformed_tiles[index], angle)

            elif operation == 'flip':
                flip_axis = random.choice((0, 1))
                transformed_tiles[index] = ImageSplit.flip_sequence(transformed_tiles[index], flip_axis)

            else:
                second_index = random.choice([u for u in range(len(transformed_tiles)) if u != index])
                transformed_tiles[index], transformed_tiles[second_index] = (transformed_tiles[second_index], transformed_tiles[index])


        return transformed_tiles

#Amber section

class ImageTilePuzzle:
    def __init__(self, root, image_path, size=3):
        self.root = root
        self.root.title("DAN/EXT04 - Puzzle Game")
        self.size = size
        self.tile_width = 100
        self.tile_height = 100
        self.selected_tile = None
        self.hints_used = 0
        self.max_hints = 3
        self.moves = 0
        self.start_time = None
        self.running = False

       # Resize window to fit puzzle + reference board
        self.root.geometry(
            f"{self.tile_width * self.size * 2 + 100}x{self.tile_height * self.size + 150}"
        ) 
        
        # Load and slice image
        self.original_image = Image.open(image_path).resize(
            (self.tile_width * size, self.tile_height * size)
        )
        self.tiles = []
        tile_id = 1
        for row in range(size):
            for col in range(size):
                tile_img = self.original_image.crop(
                    (col * self.tile_width, row * self.tile_height,
                     (col + 1) * self.tile_width, (row + 1) * self.tile_height)
                )
                self.tiles.append({
                    "id": tile_id,
                    "pil_image": tile_img,
                    "image": None,
                    "rotation": 0,
                    "flipped": False
                })
                tile_id += 1

        # Reference board
        self.solved_tiles = copy.deepcopy(sorted(self.tiles, key=lambda t: t["id"]))

        # Layout
        boards_frame = tk.Frame(self.root)
        boards_frame.grid(row=0, column=0, columnspan=2, pady=10)

        self.buttons = []
        puzzle_frame = tk.Frame(boards_frame)
        puzzle_frame.grid(row=0, column=0, padx=10)
        for i in range(len(self.tiles)):
            btn = tk.Button(puzzle_frame, width=100, height=100)
            btn.grid(row=i // size, column=i % size)
            btn.bind("<Button-1>", lambda e, idx=i: self.select_tile(idx))
            btn.bind("<Button-3>", lambda e, idx=i: self.rotate_tile(idx))
            btn.bind("<Button-2>", lambda e, idx=i: self.flip_tile(idx))
            self.buttons.append(btn)

        # Create solved board buttons with correct images
        self.solved_buttons = []
        solved_frame = tk.Frame(boards_frame)
        solved_frame.grid(row=0, column=1, padx=10)

        for i, tile in enumerate(self.solved_tiles):
            # Ensure solved tile image matches puzzle tile size
            resized_img = tile["pil_image"].resize((self.tile_width, self.tile_height))
            photo = ImageTk.PhotoImage(resized_img)
            tile["image"] = photo  # store reference
            btn = tk.Button(solved_frame, image=photo)  # no width/height in text units
            btn.grid(row=i // self.size, column=i % self.size)
            self.solved_buttons.append(btn) 

        # Info label
        self.info_label = tk.Label(self.root, text="Moves: 0 | Time: 0s | Incorrect: 0 | Hints: 0/3", font=("Arial", 14))
        self.info_label.grid(row=1, column=0, columnspan=2, pady=5)

        # Controls
        controls_frame = tk.Frame(self.root)
        controls_frame.grid(row=2, column=0, columnspan=2, pady=5)
        tk.Button(controls_frame, text="Hint", command=self.show_hint).pack(side="left", padx=5)
        tk.Button(controls_frame, text="Solve", command=self.solve_puzzle).pack(side="left", padx=5)

        # Shuffle automatically
        self.shuffle_tiles()
        self.update_board()
        self.update_info()
        self.update_timer()

    def shuffle_tiles(self):
        random.shuffle(self.tiles)
        for tile in self.tiles:
            tile["rotation"] = random.choice([0, 90, 180, 270])
            tile["flipped"] = random.choice([True, False])

    def update_board(self):
        for i, tile in enumerate(self.tiles):
            img = tile["pil_image"]
            if tile["flipped"]:
                img = ImageOps.mirror(img)
            if tile["rotation"] != 0:
                img = img.rotate(tile["rotation"], expand=True)
            img = ImageTk.PhotoImage(img)
            tile["image"] = img
            self.buttons[i].config(image=img, highlightthickness=0, bg="SystemButtonFace")

        for i, tile in enumerate(self.solved_tiles):
            img = ImageTk.PhotoImage(tile["pil_image"])
            tile["image"] = img
            self.solved_buttons[i].config(image=img, highlightthickness=0, bg="SystemButtonFace")

    def update_info(self):
        incorrect_count = sum(
            1 for i, tile in enumerate(self.tiles)
            if tile["id"] != self.solved_tiles[i]["id"] or tile["rotation"] != 0 or tile["flipped"]
        )
        elapsed = int(time.time() - self.start_time) if self.running else 0
        self.info_label.config(
            text=f"Moves: {self.moves} | Time: {elapsed}s | Incorrect: {incorrect_count} | Hints: {self.hints_used}/{self.max_hints}"
        )

    def update_timer(self):
        if self.running:
            self.update_info()
        self.root.after(500, self.update_timer)

    def check_progress(self):
            correct = sum(1 for i, tile in enumerate(self.tiles)
                          if tile["id"] == i+1 and tile["rotation"] == 0 and not tile["flipped"])
            remaining = int(self.size**2 - correct) if self.size**2 > 0 else 0
            elapsed = int(time.time() - self.start_time) if self.running else 0
            self.info_label.config(text=f"Moves: {self.moves} | Time: {elapsed}s | Incorrect: {remaining} | Hints: {self.hints_used}/{self.max_hints}")
    
            if remaining == 0:
                self.running = False
                messagebox.showinfo("Puzzle Solved",
                                    f"Congratulations!\nMoves: {self.moves}\nTime: {elapsed}s\nHints Used: {self.hints_used}/{self.max_hints}")    

    def select_tile(self, idx):
        if not self.running:
            self.start_time = time.time()
            self.running = True

        if self.selected_tile is None:
            self.selected_tile = idx
            self.buttons[idx].config(bg="yellow")
        else:
            self.swap_tiles(self.selected_tile, idx)
            self.buttons[self.selected_tile].config(bg="SystemButtonFace")
            self.selected_tile = None
            self.moves += 1
            self.update_board()
            self.update_info()
            self.check_progress()

    def swap_tiles(self, idx1, idx2):
        self.tiles[idx1], self.tiles[idx2] = self.tiles[idx2], self.tiles[idx1]

    def rotate_tile(self, idx):
        self.tiles[idx]["rotation"] = (self.tiles[idx]["rotation"] + 90) % 360
        self.moves += 1
        self.update_board()
        self.update_info()
        self.check_progress()

    def flip_tile(self, idx):
        self.tiles[idx]["flipped"] = not self.tiles[idx]["flipped"]
        self.moves += 1
        self.update_board()
        self.update_info()
        self.check_progress()

    def show_hint(self):
        if self.hints_used >= self.max_hints:
            messagebox.showinfo("No Hints Left", "You have used all available hints!")
            return

        self.hints_used += 1
        self.update_info()

        # Find first incorrect tile
        for puzzle_idx, tile in enumerate(self.tiles):
            correct_tile = self.solved_tiles[puzzle_idx]
            if tile["id"] != correct_tile["id"] or tile["rotation"] != 0 or tile["flipped"]:
                # Find where this tile belongs in the solved board
                correct_position_idx = next(
                    idx for idx, t in enumerate(self.solved_tiles) if t["id"] == tile["id"]
                )
                self.mark_hint(puzzle_idx, correct_position_idx)
                break

    from PIL import ImageDraw

    from PIL import ImageDraw

    def mark_hint(self, puzzle_idx, correct_position_idx):
        """Highlight incorrect tile in puzzle board and its correct position in reference board with a filled blue circle."""
        # Puzzle tile image with current transformations
        tile_img = self.tiles[puzzle_idx]["pil_image"]
        if self.tiles[puzzle_idx]["flipped"]:
            tile_img = ImageOps.mirror(tile_img)
        if self.tiles[puzzle_idx]["rotation"] != 0:
            tile_img = tile_img.rotate(self.tiles[puzzle_idx]["rotation"], expand=True)

        # Draw outlined blue circle
        img_with_circle = tile_img.copy()
        draw = ImageDraw.Draw(img_with_circle)
        center_x = img_with_circle.width // 2
        center_y = img_with_circle.height // 2
        radius = min(center_x, center_y) // 1.2  # adjust size here
        draw.ellipse(
            (center_x - radius, center_y - radius, center_x + radius, center_y + radius),
            outline="blue",
            width=5  # thickness of the outline
        )
 
        # Convert to PhotoImage and store reference
        photo = ImageTk.PhotoImage(img_with_circle)
        self.tiles[puzzle_idx]["image"] = photo
        self.buttons[puzzle_idx].config(image=photo)

        # Correct tile image in reference board
        correct_img = self.solved_tiles[correct_position_idx]["pil_image"].copy()
        draw_ref = ImageDraw.Draw(correct_img)
        center_x = correct_img.width // 2
        center_y = correct_img.height // 2
        radius = min(center_x, center_y) // 1.2
        draw_ref.ellipse(
            (center_x - radius, center_y - radius, center_x + radius, center_y + radius),
            outline="blue",
            width=5  # thickness of the outline
        )

        # Convert to PhotoImage and store reference
        photo_ref = ImageTk.PhotoImage(correct_img)
        self.solved_tiles[correct_position_idx]["image"] = photo_ref
        self.solved_buttons[correct_position_idx].config(image=photo_ref)

    def solve_puzzle(self):
        """Set puzzle tiles to solved state and refresh display."""
        self.tiles = [tile.copy() for tile in self.solved_tiles]  # deep copy
        self.update_board()
        

if __name__ == "__main__":
    root = tk.Tk()
    game = ImageTilePuzzle(root, "image.jpg", size=3)
    root.mainloop()