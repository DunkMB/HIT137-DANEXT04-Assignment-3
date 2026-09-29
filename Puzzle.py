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



#Jonathan section