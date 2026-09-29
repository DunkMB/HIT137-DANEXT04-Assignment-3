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
# Import and set up the necessary libraries
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random
import time

# Define the Puzzle Game as a class
class ImageTilePuzzle:
    def __init__(self, root, image_path):
        self.root = root
        self.root.title("DAN/EXT04 - Puzzle Game")

        # Game settings
        self.size = 3  # 3x3 grid
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        # Load the image first
        self.original_image = Image.open(image_path)

        # Use 80% of screen size for puzzle
        max_width = int(screen_w * 0.4)   # each grid takes ~40% of screen width
        max_height = int(screen_h * 0.8)  # height takes ~80% of screen height

        # Crop the image to a square and resize it to fit within the max dimensions
        img_w, img_h = self.original_image.size
        min_side = min(img_w, img_h)
        left = (img_w - min_side) // 2
        top = (img_h - min_side) // 2
        right = left + min_side
        bottom = top + min_side
        self.original_image = self.original_image.crop((left, top, right, bottom))

        img_w, img_h = self.original_image.size
        scale = min(max_width / img_w, max_height / img_h, 1.0)  # don't upscale too much
        new_w, new_h = int(img_w * scale), int(img_h * scale)
        self.original_image = self.original_image.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # Calculate tile size dynamically
        self.tile_width = self.original_image.width // self.size
        self.tile_height = self.original_image.height // self.size

        # Create tile data for puzzle
        self.tiles = []
        tile_id = 1
        for row in range(self.size):
            for col in range(self.size):
                tile_img = self.original_image.crop(
                    (col * self.tile_width, row * self.tile_height,
                     (col + 1) * self.tile_width, (row + 1) * self.tile_height)
                )
                self.tiles.append({
                     "id": tile_id,
                     "image": tile_img,
                     "rotation": 0,
                     "flipped": False
                })
                tile_id += 1

        # Keep a solved reference (sorted by id)
        import copy
        self.solved_tiles = copy.deepcopy(sorted(self.tiles, key=lambda t: t["id"]))

        # Shuffle puzzle tiles
        random.shuffle(self.tiles)

        # Randomly rotate and flip tiles
        for tile in self.tiles:
            # Random rotation: 0, 90, 180, or 270 degrees
            tile["rotation"] = random.choice([0, 90, 180, 270])
            # Random flip: True or False
            tile["flipped"] = random.choice([True, False])

        # Game state
        self.start_time = None
        self.moves = 0
        self.running = False
        self.selected_tile = None
        self.hints_used = 0
        self.max_hints = 3

        # Layout: Puzzle on left, solved reference on right
        main_frame = tk.Frame(self.root)
        main_frame.pack(pady=10)

        puzzle_frame = tk.Frame(main_frame)
        puzzle_frame.grid(row=0, column=0, padx=10)

        solved_frame = tk.Frame(main_frame)
        solved_frame.grid(row=0, column=1, padx=10)

        # Info label
        self.info_label = tk.Label(root, text="Moves: 0 | Time: 0s | Correct: 0% | Hints: 0/3", font=("Arial", 14))
        self.info_label.pack(pady=5)

        # Control buttons
        controls_frame = tk.Frame(self.root)
        controls_frame.pack(pady=5)

        self.hint_button = tk.Button(controls_frame, text="Hint", font=("Arial", 14), command=self.show_hint)
        self.hint_button.grid(row=0, column=0, padx=5)
       
        self.solve_button = tk.Button(controls_frame, text="Solve", font=("Arial", 14), command=self.solve_puzzle)
        self.solve_button.grid(row=0, column=1, padx=5)

        # Puzzle grid (interactive)
        self.buttons = []
        for i in range(self.size**2):
            btn = tk.Button(puzzle_frame, borderwidth=1, relief="solid")
            btn.grid(row=i // self.size, column=i % self.size)
            btn.bind("<Button-1>", lambda e, i=i: self.select_tile(i))  # Left click
            btn.bind("<Button-2>", lambda e, i=i: self.flip_tile(i))    # Middle click
            btn.bind("<Button-3>", lambda e, i=i: self.rotate_tile(i))  # Right click
            self.buttons.append(btn)

        # Solved grid (static reference)
        self.solved_buttons = []
        for i in range(self.size**2):
            lbl = tk.Label(solved_frame, borderwidth=1, relief="solid")
            lbl.grid(row=i // self.size, column=i % self.size)
            self.solved_buttons.append(lbl)

        self.update_board()
        self.update_timer()

# ---------------- Hint Feature ----------------
    def show_hint(self):
        """Highlight one incorrect tile and its correct location."""
        # Limit hints to 3 per game
        if self.hints_used >= self.max_hints:
            messagebox.showwarning("No Hints Left", "You have used all available hints.")
            return

        incorrect_indices = [i for i, val in enumerate(self.tiles) if val != self.goal_state[i] and val is not None]
        if not incorrect_indices:
            messagebox.showinfo("No Hint Needed", "All tiles are already in the correct position!")
            return
        
        # Reset all highlights first
        for btn in self.buttons:
            btn.config(bg="SystemButtonFace")
        for lbl in self.solved_buttons:
            lbl.config(bg="SystemButtonFace")

        # Pick one incorrect tile
        hint_index = random.choice(incorrect_indices)
        tile_value = self.tiles[hint_index]
        
        # Find where this tile belongs in the goal board
        correct_position = self.goal_state.index(tile_value)
        
        # Reset highlights first
        self.clear_highlights()
        
        # Highlight wrong tile in puzzle (blue outline)
        self.buttons[hint_index].config(highlightbackground="blue", highlightcolor="blue", highlightthickness=3)
        
        # Highlight correct location in goal board (blue outline)
        self.goal_labels[correct_position].config(highlightbackground="blue", highlightcolor="blue", highlightthickness=3)
        
        self.hints_used += 1
        self.update_info()

# ---------------- Solve Feature ----------------
    def solve_puzzle(self):
        """Instantly solve the puzzle."""
        import copy
        self.tiles = copy.deepcopy(self.solved_tiles)  # restore solved state
        self.moves += 1
        self.running = False
        self.update_board()
        self.check_progress()
        messagebox.showinfo("Solved", "The puzzle has been solved!")

    def update_board(self):
        # Puzzle grid
        for i, tile in enumerate(self.tiles):
            img_tk = self.get_transformed_image(tile)
            self.buttons[i].config(image=img_tk, bg="SystemButtonFace")
            self.buttons[i].image = img_tk  # keep reference

        # Solved grid
        for i, tile in enumerate(self.solved_tiles):
            img_tk = ImageTk.PhotoImage(tile["image"])
            self.solved_buttons[i].config(image=img_tk, bg="SystemButtonFace")
            self.solved_buttons[i].image = img_tk

    def select_tile(self, index):
        if self.selected_tile is None:
            self.selected_tile = index
            self.buttons[index].config(bg="blue")
        else:
            self.swap_tiles(self.selected_tile, index)
            self.selected_tile = None
            self.update_board()

    def swap_tiles(self, idx1, idx2):
        self.tiles[idx1], self.tiles[idx2] = self.tiles[idx2], self.tiles[idx1]
        self.moves += 1
        self.start_game()
        self.check_progress()

    def flip_tile(self, index):
        self.tiles[index]["flipped"] = not self.tiles[index]["flipped"]
        self.moves += 1
        self.start_game()
        self.update_board()
        self.check_progress()

    def rotate_tile(self, index):
        self.tiles[index]["rotation"] = (self.tiles[index]["rotation"] + 90) % 360
        self.moves += 1
        self.start_game()
        self.update_board()
        self.check_progress()

    def start_game(self):
        if not self.running:
            self.start_time = time.time()
            self.running = True

    def get_transformed_image(self, tile):
        img = tile["image"]
        if tile["flipped"]:
            img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        if tile["rotation"] != 0:
            img = img.rotate(tile["rotation"], expand=True)
        return ImageTk.PhotoImage(img)

    def check_progress(self):
        correct = sum(1 for i, tile in enumerate(self.tiles)
                      if tile["id"] == i+1 and tile["rotation"] == 0 and not tile["flipped"])
        progress = int((correct / len(self.tiles)) * 100)
        elapsed = int(time.time() - self.start_time) if self.running else 0
        self.info_label.config(text=f"Moves: {self.moves} | Time: {elapsed}s | Correct: {progress}% | Hints: {self.hints_used}/{self.max_hints}")

        if progress == 100:
            self.running = False
            messagebox.showinfo("Puzzle Solved",
                                f"Congratulations!\nMoves: {self.moves}\nTime: {elapsed}s")

    def update_timer(self):
        """Update timer periodically."""
        if self.running:
            self.check_progress()
        self.root.after(500, self.update_timer)


if __name__ == "__main__":
    root = tk.Tk()
    game = ImageTilePuzzle(root, "image.jpg")  
    root.mainloop()



#Darren section



#Duncan section



#Jonathan section