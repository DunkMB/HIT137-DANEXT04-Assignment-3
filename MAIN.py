import cv2
import numpy as np
import random
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
from abc import ABC, abstractmethod


# ==========================================
# 1. OOP: TRANSFORMATIONS (Polymorphism & Inheritance)
# ==========================================

class Transformation(ABC):
    """Abstract base class for tile transformations."""
    @abstractmethod
    def apply(self, puzzle):
        pass

    @abstractmethod
    def invert(self, puzzle):
        pass


class SwapTransformation(Transformation):
    """Swaps two tiles in the puzzle."""
    def __init__(self, pos1, pos2):
        self.pos1 = pos1  # (r1, c1)
        self.pos2 = pos2  # (r2, c2)

    def apply(self, puzzle):
        puzzle.grid[self.pos1[0]][self.pos1[1]], puzzle.grid[self.pos2[0]][self.pos2[1]] = \
            puzzle.grid[self.pos2[0]][self.pos2[1]], puzzle.grid[self.pos1[0]][self.pos1[1]]

    def invert(self, puzzle):
        # Swapping again undoes the swap
        self.apply(puzzle)


class RotateTransformation(Transformation):
    """Rotates a single tile by 90, 180, or 270 degrees clockwise."""
    def __init__(self, pos, angle):
        self.pos = pos  # (r, c)
        self.angle = angle  # 90, 180, 270

    def apply(self, puzzle):
        tile = puzzle.grid[self.pos[0]][self.pos[1]]
        tile.rotation = (tile.rotation + self.angle) % 360

    def invert(self, puzzle):
        tile = puzzle.grid[self.pos[0]][self.pos[1]]
        tile.rotation = (tile.rotation - self.angle) % 360


class FlipTransformation(Transformation):
    """Flips a single tile horizontally or vertically."""
    def __init__(self, pos, axis):
        self.pos = pos  # (r, c)
        self.axis = axis  # 'horizontal' or 'vertical'

    def apply(self, puzzle):
        tile = puzzle.grid[self.pos[0]][self.pos[1]]
        if self.axis == 'horizontal':
            tile.h_flipped = not tile.h_flipped
        else:
            tile.v_flipped = not tile.v_flipped

    def invert(self, puzzle):
        # Flipping again undoes the flip
        self.apply(puzzle)


# ==========================================
# 2. PUZZLE DATA STRUCTURES (Encapsulation)
# ==========================================

class Tile:
    """Represents a single tile piece in the grid."""
    def __init__(self, original_image, original_pos):
        self.original_image = original_image  # cv2 BGR image
        self.original_pos = original_pos      # (r, c) correct home position
        self.rotation = 0                       # 0, 90, 180, 270 degrees
        self.h_flipped = False
        self.v_flipped = False

    def is_correct(self, current_pos):
        """Checks if the tile is in its original position and orientation."""
        return (self.original_pos == current_pos and 
                self.rotation == 0 and 
                not self.h_flipped and 
                not self.v_flipped)

    def get_current_image(self):
        """Applies current rotations and flips using OpenCV."""
        img = self.original_image.copy()

        if self.h_flipped:
            img = cv2.flip(img, 1)
        if self.v_flipped:
            img = cv2.flip(img, 0)

        if self.rotation == 90:
            img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        elif self.rotation == 180:
            img = cv2.rotate(img, cv2.ROTATE_180)
        elif self.rotation == 270:
            img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)

        return img


class Puzzle:
    """Manages the grid state and transformation pipeline."""
    def __init__(self, image, grid_size):
        self.grid_size = grid_size
        self.original_image = image
        self.h, self.w, _ = image.shape
        self.tile_h = self.h // grid_size
        self.tile_w = self.w // grid_size

        # Slicer: Slice original image into pieces
        self.tiles = []
        self.grid = []  # 2D list grid[r][c]
        for r in range(grid_size):
            row = []
            for c in range(grid_size):
                y1, y2 = r * self.tile_h, (r + 1) * self.tile_h
                x1, x2 = c * self.tile_w, (c + 1) * self.tile_w
                tile_img = self.original_image[y1:y2, x1:x2]
                tile = Tile(tile_img, (r, c))
                row.append(tile)
                self.tiles.append(tile)
            self.grid.append(row)

        self.transformations = []

    def scramble(self):
        """Scrambles the puzzle with random transformations based on grid size."""
        # Scaling counts: 3x3 -> 6, 4x4 -> 12, 5x5 -> 20
        count_map = {3: 6, 4: 12, 5: 20}
        num_transforms = count_map.get(self.grid_size, 6)

        self.transformations = []
        for _ in range(num_transforms):
            t_type = random.choice(['swap', 'rotate', 'flip'])
            if t_type == 'swap':
                r1, r2 = random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1)
                c1, c2 = random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1)
                transform = SwapTransformation((r1, c1), (r2, c2))
            elif t_type == 'rotate':
                r, c = random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1)
                angle = random.choice([90, 180, 270])
                transform = RotateTransformation((r, c), angle)
            elif t_type == 'flip':
                r, c = random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1)
                axis = random.choice(['horizontal', 'vertical'])
                transform = FlipTransformation((r, c), axis)

            transform.apply(self)
            self.transformations.append(transform)

    def is_solved(self):
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if not self.grid[r][c].is_correct((r, c)):
                    return False
        return True

    def get_incorrect_count(self):
        count = 0
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if not self.grid[r][c].is_correct((r, c)):
                    count += 1
        return count


# ==========================================
# 3. TKINTER GUI APPLICATION
# ==========================================

class ImagePuzzleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Scrambled Image Puzzle")

        # Game state variables
        self.grid_size_var = tk.IntVar(value=3)
        self.puzzle = None
        self.selected_tile_pos = None
        self.moves_count = 0
        self.hints_used = 0
        self.max_hints = 3
        self.active_hint = None  # Stores (incorrect_pos, correct_pos)
        self.is_solved = False

        self._build_ui()

    def _build_ui(self):
        # Top Control Frame
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(fill=tk.X)

        ttk.Button(control_frame, text="Load Image", command=self.load_image).pack(side=tk.LEFT, padx=5)

        ttk.Label(control_frame, text="Grid Size:").pack(side=tk.LEFT, padx=5)
        grid_combobox = ttk.Combobox(control_frame, textvariable=self.grid_size_var, values=[3, 4, 5], state="readonly", width=5)
        grid_combobox.pack(side=tk.LEFT, padx=5)

        self.hint_button = ttk.Button(control_frame, text="Hint (3 left)", command=self.use_hint, state=tk.DISABLED)
        self.hint_button.pack(side=tk.LEFT, padx=5)

        self.solve_button = ttk.Button(control_frame, text="Solve", command=self.solve_puzzle, state=tk.DISABLED)
        self.solve_button.pack(side=tk.LEFT, padx=5)

        # Info Frame
        info_frame = ttk.Frame(self.root, padding=5)
        info_frame.pack(fill=tk.X)

        self.moves_label = ttk.Label(info_frame, text="Moves: 0", font=("Arial", 11, "bold"))
        self.moves_label.pack(side=tk.LEFT, padx=20)

        self.incorrect_label = ttk.Label(info_frame, text="Tiles Incorrect: -", font=("Arial", 11, "bold"))
        self.incorrect_label.pack(side=tk.LEFT, padx=20)

        # Image Display Frame
        self.display_frame = ttk.Frame(self.root, padding=10)
        self.display_frame.pack()

        # Canvas for Left (Original) and Right (Transformed)
        self.left_canvas = tk.Canvas(self.display_frame, width=400, height=400, bg="gray")
        self.left_canvas.pack(side=tk.LEFT, padx=10)

        self.right_canvas = tk.Canvas(self.display_frame, width=400, height=400, bg="gray")
        self.right_canvas.pack(side=tk.RIGHT, padx=10)

        # Bindings for right canvas (Interactive)
        self.right_canvas.bind("<Button-1>", self.on_left_click)
        self.right_canvas.bind("<Button-3>", self.on_right_click)

    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if not file_path:
            return

        # Read image using OpenCV
        raw_img = cv2.imread(file_path)
        if raw_img is None:
            messagebox.showerror("Error", "Failed to load image file.")
            return

        # Target canvas dimensions
        target_dim = 400
        grid_size = self.grid_size_var.get()

        # Resize & crop image so it's square and evenly divisible by grid_size
        h, w, _ = raw_img.shape
        min_dim = min(h, w)
        crop_h = (min_dim // grid_size) * grid_size
        crop_w = (min_dim // grid_size) * grid_size

        # Center crop
        start_y = (h - crop_h) // 2
        start_x = (w - crop_w) // 2
        cropped = raw_img[start_y:start_y + crop_h, start_x:start_x + crop_w]

        # Resize to fixed display size (400x400)
        final_dim = (target_dim // grid_size) * grid_size
        resized_img = cv2.resize(cropped, (final_dim, final_dim))

        # Reset Game State
        self.puzzle = Puzzle(resized_img, grid_size)
        self.puzzle.scramble()
        self.selected_tile_pos = None
        self.moves_count = 0
        self.hints_used = 0
        self.active_hint = None
        self.is_solved = False

        # Enable UI
        self.hint_button.config(state=tk.NORMAL, text=f"Hint ({self.max_hints} left)")
        self.solve_button.config(state=tk.NORMAL)

        self.update_display()

    def update_display(self):
        if not self.puzzle:
            return

        grid_size = self.puzzle.grid_size
        tile_w = self.puzzle.tile_w
        tile_h = self.puzzle.tile_h

        # 1. Display Reference Original Image (Left Canvas)
        orig_rgb = cv2.cvtColor(self.puzzle.original_image, cv2.COLOR_BGR2RGB)
        
        # Overlay blue circle on hint reference position if active
        if self.active_hint:
            _, (hr, hc) = self.active_hint
            center_x = hc * tile_w + tile_w // 2
            center_y = hr * tile_h + tile_h // 2
            cv2.circle(orig_rgb, (center_x, center_y), min(tile_w, tile_h) // 4, (0, 0, 255), 3)

        orig_pil = Image.fromarray(orig_rgb)
        self.left_img_tk = ImageTk.PhotoImage(orig_pil)
        self.left_canvas.config(width=self.puzzle.w, height=self.puzzle.h)
        self.left_canvas.create_image(0, 0, anchor=tk.NW, image=self.left_img_tk)

        # 2. Build Transformed Image (Right Canvas)
        canvas_bgr = np.zeros_like(self.puzzle.original_image)

        for r in range(grid_size):
            for c in range(grid_size):
                tile = self.puzzle.grid[r][c]
                t_img = tile.get_current_image()
                y1, y2 = r * tile_h, (r + 1) * tile_h
                x1, x2 = c * tile_w, (c + 1) * tile_w
                canvas_bgr[y1:y2, x1:x2] = t_img

        trans_rgb = cv2.cvtColor(canvas_bgr, cv2.COLOR_BGR2RGB)

        # Draw visual indicators (faint grid, green tick, highlights)
        for r in range(grid_size):
            for c in range(grid_size):
                x1, y1 = c * tile_w, r * tile_h
                x2, y2 = (c + 1) * tile_w, (r + 1) * tile_h

                # Faint grid lines
                cv2.rectangle(trans_rgb, (x1, y1), (x2, y2), (200, 200, 200), 1)

                # Small green tick if correctly positioned & oriented
                if self.puzzle.grid[r][c].is_correct((r, c)):
                    cv2.putText(trans_rgb, "v", (x1 + 8, y1 + 22), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)

        # Draw Hint Highlight (Blue Circle)
        if self.active_hint:
            (ir, ic), _ = self.active_hint
            center_x = ic * tile_w + tile_w // 2
            center_y = ir * tile_h + tile_h // 2
            cv2.circle(trans_rgb, (center_x, center_y), min(tile_w, tile_h) // 4, (255, 0, 0), 3)

        # Draw Selected Tile Highlight (Yellow Border)
        if self.selected_tile_pos:
            sr, sc = self.selected_tile_pos
            x1, y1 = sc * tile_w, sr * tile_h
            x2, y2 = (sc + 1) * tile_w, (sr + 1) * tile_h
            cv2.rectangle(trans_rgb, (x1, y1), (x2, y2), (255, 255, 0), 3)

        trans_pil = Image.fromarray(trans_rgb)
        self.right_img_tk = ImageTk.PhotoImage(trans_pil)
        self.right_canvas.config(width=self.puzzle.w, height=self.puzzle.h)
        self.right_canvas.create_image(0, 0, anchor=tk.NW, image=self.right_img_tk)

        # Update Info Stats
        self.moves_label.config(text=f"Moves: {self.moves_count}")
        self.incorrect_label.config(text=f"Tiles Incorrect: {self.puzzle.get_incorrect_count()}")

        # Check Win Condition
        if self.puzzle.is_solved() and not self.is_solved:
            self.is_solved = True
            self.hint_button.config(state=tk.DISABLED)
            messagebox.showinfo("Congratulations!", f"Puzzle Solved in {self.moves_count} moves!")

    def _get_click_pos(self, event):
        """Converts mouse click event coordinates to grid (row, col)."""
        col = event.x // self.puzzle.tile_w
        row = event.y // self.puzzle.tile_h
        if 0 <= row < self.puzzle.grid_size and 0 <= col < self.puzzle.grid_size:
            return (row, col)
        return None

    def register_move(self):
        """Increments move counter and clears active hint."""
        self.moves_count += 1
        self.active_hint = None
        self.update_display()

    def on_left_click(self, event):
        if not self.puzzle or self.is_solved:
            return

        pos = self._get_click_pos(event)
        if not pos:
            return

        # Check Shift + Left Click (Horizontal Flip)
        if event.state & 0x0001:  # Shift modifier key active
            FlipTransformation(pos, 'horizontal').apply(self.puzzle)
            self.selected_tile_pos = None
            self.register_move()
            return

        # Normal Left Click (Select / Swap)
        if self.selected_tile_pos is None:
            self.selected_tile_pos = pos
            self.update_display()
        elif self.selected_tile_pos == pos:
            # Deselect if clicking the same tile
            self.selected_tile_pos = None
            self.update_display()
        else:
            # Swap tiles
            SwapTransformation(self.selected_tile_pos, pos).apply(self.puzzle)
            self.selected_tile_pos = None
            self.register_move()

    def on_right_click(self, event):
        """Right Click -> Rotate 90 Degrees Clockwise."""
        if not self.puzzle or self.is_solved:
            return

        pos = self._get_click_pos(event)
        if pos:
            RotateTransformation(pos, 90).apply(self.puzzle)
            self.selected_tile_pos = None
            self.register_move()

    def use_hint(self):
        if not self.puzzle or self.is_solved or self.hints_used >= self.max_hints:
            return

        # Find all incorrect tiles
        incorrect_tiles = []
        for r in range(self.puzzle.grid_size):
            for c in range(self.puzzle.grid_size):
                tile = self.puzzle.grid[r][c]
                if not tile.is_correct((r, c)):
                    incorrect_tiles.append(((r, c), tile.original_pos))

        if not incorrect_tiles:
            return

        # Pick one incorrect tile randomly
        self.active_hint = random.choice(incorrect_tiles)
        self.hints_used += 1

        if self.hints_used >= self.max_hints:
            self.hint_button.config(state=tk.DISABLED, text="Hint (0 left)")
        else:
            self.hint_button.config(text=f"Hint ({self.max_hints - self.hints_used} left)")

        self.update_display()

    def solve_puzzle(self):
        if not self.puzzle or self.is_solved:
            return

        # Solves by placing original tiles directly back into standard order
        for r in range(self.puzzle.grid_size):
            for c in range(self.puzzle.grid_size):
                # Find the tile that originally belongs at (r, c)
                for tr in range(self.puzzle.grid_size):
                    for tc in range(self.puzzle.grid_size):
                        if self.puzzle.grid[tr][tc].original_pos == (r, c):
                            # Swap into place
                            self.puzzle.grid[tr][tc], self.puzzle.grid[r][c] = \
                                self.puzzle.grid[r][c], self.puzzle.grid[tr][tc]
                            break

                # Reset orientation
                tile = self.puzzle.grid[r][c]
                tile.rotation = 0
                tile.h_flipped = False
                tile.v_flipped = False

        self.moves_count = 0
        self.selected_tile_pos = None
        self.active_hint = None
        self.update_display()


# ==========================================
# ENTRY POINT
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    app = ImagePuzzleApp(root)
    root.mainloop()