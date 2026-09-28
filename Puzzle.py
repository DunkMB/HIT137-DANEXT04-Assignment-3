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

#Map coordinates to grid position

    c = event.x // self.tile w
    r = event.y // self.tile h
    if r>=self.grid_size or c>=self.grid_size:
        return

#Position of tile and left click horizontal flip
    if event.state & 0x0001:
        self.grid[r][c].flip_horizontal()
        self.register_move()
        return

#Tile slection and swapping
    if self.selected_tile_pos is None:
        self.selected_tile_pos = (r, c)
        self.highlight_selected_tile(r, c)
        self.render_displays()
    else:
        sr, sc = self.selected_tile_pos
    if (sr, sc) == (r, c):
        self.selected_tile_pos = None
        self.render_displays()

#Duncan section



#Jonathan section