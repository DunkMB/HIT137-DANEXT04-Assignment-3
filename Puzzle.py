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
print(" " * 50)
print("_" * 50)
print("Question 1")
print("_" * 50)


#Amber section
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageOps, ImageDraw
import copy, random, time

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


#Darren section



#Duncan section



#Jonathan section