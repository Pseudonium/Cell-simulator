import tkinter as tk
#import pdb

class Cell:
	
	#ref_dict allows the coords to act as a pointer to the cell.
	ref_dict = {}
	"""active_cells allows the grid to determine sim_cells.
	Thus, it reduces the number of cells the grid needs to simulate.
	"""
	active_cells = set()
	
	def __init__(
			self, coords, size, grid_size, conditions = {},
			active_color = "black", inactive_color = "white", state = False,
			empty = False):
		"""Create a new cell.
		
		Positional arguments:
			
			coords ---------- Coordinates of the cell within the grid.
			Tuple (x, y)
			
			size ------------ Side length of the cell in pixels.
			Integer.
			
			grid_size ------- Side length of the grid, in squares.
			Integer.
		
		Keyword arguments:
		
			conditions ------ Dict of conditions the cell has.
			Used for complex simulations.
			Keys as names, values as floats.
			E.g. 'temperature': 50.4
			Dictionary.
			
			active_color ---- Color of the cell when alive.
			String or color reference.
			
			inactive_color -- Color of the cell when dead.
			String or color reference.
			
			state ----------- Whether the cell is alive or dead.
			Boolean.
			
			empty ----------- Whether the cell is 'empty',
			and thus is disregarded from the simulation.
		
		This object simulates a cell, which evolves over time.
		Here, the rules for evolution are from 'Conway's game of life'.
		"""
		self.coords = coords
		self.size = size
		self.grid_size = grid_size
		self.conditions = conditions
		self.active_color = active_color
		self.inactive_color = inactive_color
		self.state = state
		self.empty = empty
		"""The cell won't update it's state straight away.
		Otherwise, it could cause a knock-on effect,
		changing the number of neighbors for other cells.
		To avoid this, the cell will calculate its new_state first.
		Then, it can set self.state = self.new_state after all updates.
		"""
		self.new_state = False
		self.neighbor_coords = ()
		self.get_neighbor_coords()
		self.alive_neighbors = 0
		"""This allows instantiation without variable assignment,
		by letting the coordinates act as a pointer.
		"""
		Cell.ref_dict[self.coords] = self
	
	def valid_coord(self, coord):
		"""Determine whether a given coordinate is within the grid.
		
		x coordinates are measured from the origin.
		Hence, they should not be >= to the grid_size.
		This would indicate it was referring to a column right of the
		rightmost column, due to everything being 0-indexed.
		Similar rules apply for the y coordinate.
		"""
		(x, y) = coord
		return (0 <= x < self.grid_size) and (0 <= y < self.grid_size)
		
		
	def get_neighbor_coords(self):
		"""Construct neighbor_coords."""
		(x, y) = self.coords
		if self.empty:
			self.neighbor_coords = tuple()
		else:
			self.neighbor_coords = tuple(filter(self.valid_coord,
			[
				(x + a, y + b)
				for a in range(-1, 2) for b in range(-1, 2)
				if (a != 0 or b != 0)
			]))
		return self

	def update_neighbor_coords(self):
		"""Update neighbor_coords based on empty cells"""
		self.neighbor_coords = tuple([
			coord for coord in self.neighbor_coords
			if not Cell.ref_dict[coord].empty])

	def get_alive_neighbors(self):
		"""Determine alive_neighbors."""
		self.alive_neighbors = 0
		for n in self.neighbor_coords:
			if Cell.ref_dict[n].state:
				self.alive_neighbors += 1
		return self
	
	def get_new_state(self):
		"""Determine what the new state of the cell should be.
		
		Here is where any different rules can be configured.
		"""
		if self.empty:
			self.new_state = False
			self.state = False
		else:
			if not self.neighbor_coords:
				self.get_neighbor_coords().get_alive_neighbors()
			else:
				self.get_alive_neighbors()
			if self.state:
				if not 2 <= self.alive_neighbors <= 3:
					self.new_state = False
				else:
					self.new_state = True
			else:
				if self.alive_neighbors == 3:
					self.new_state = True
				else:
					self.new_state = False
		return self
	
	def update_state(self):
		"""Set self.state to self.new_state; reset self.new_state.
		
		Also will add/remove the cell from active_cells.
		"""
		self.state = self.new_state
		
		if self.state and self.coords not in Cell.active_cells:
			Cell.active_cells.add(self.coords)
		elif not self.state and self.coords in Cell.active_cells:
			Cell.active_cells.remove(self.coords)
		
		self.new_state = False
		return self

class Grid:

	def __init__(
			self, size, cell_size, active_color = "black",
			inactive_color = "white", condition_dict = {},
			initial_active_cells = [],
			initial_empty_cells = []):
		"""Create a new grid.
		
		Positional arguments:
		
			size ----------------- Size of the grid in cells.
			Integer.
			
			cell_size ------------ Size of a cell in pixels.
			Integer.
		
		Keyword arguments:
		
			active_color --------- Color of a cell when alive.
			String or color reference.
			
			inactive_color ------- Color of a cell when dead.
			String or color reference.
			
			condition_dict ------- Nested dictionary.
			Coordinates as keys, dicts of conditions as values.
			Dictionary.
			
			initial_active_cells - List of cells that start alive.
			List.
		
		"""
		self.size = size
		self.cell_size = cell_size
		self.active_color = active_color
		self.inactive_color = inactive_color
		self.condition_dict = condition_dict
		self.initial_active_cells = initial_active_cells
		self.initial_empty_cells = initial_empty_cells
		"""Only active cells and neighbors are simulated.
		Coords in self.sim_cells. This attempts to reduce CPU usage.
		"""
		self.sim_cells = set()
		self.create_cells().set_active_cells().set_empty_cells()

	def create_cells(self):
		"""Instantiate all new cells with required parameters."""
		
		"""Conditions may not be specified.
		The if statement thus avoids KeyErrors.
		"""
		if self.condition_dict:
			for x in range(0, self.size):
				for y in range(0, self.size):
					Cell(
						(x, y), self.cell_size, self.size,
						conditions = self.condition_dict[(x, y)],
						active_color = self.active_color,
						inactive_color = self.inactive_color)
		else:
			for x in range(0, self.size):
				for y in range(0, self.size):
					Cell(
						(x, y), self.cell_size, self.size,
						active_color = self.active_color,
						inactive_color = self.inactive_color)
		return self
	
	def set_active_cells(self):
		"""Set states of cells specified by a list to True."""
		for coord in self.initial_active_cells:
			Cell.ref_dict[coord].new_state = True
			Cell.ref_dict[coord].update_state()
		return self
	
	def set_empty_cells(self):
		"""Set certain cells to be empty"""
		for coord in self.initial_empty_cells:
			Cell.ref_dict[coord].empty = True
		for cell in Cell.ref_dict.values():
			cell.update_neighbor_coords()
		return self
	
	def get_sim_cells(self):
		"""Get all cells that need to be simulated."""
		self.sim_cells = set()
		for coord in Cell.active_cells:
			self.sim_cells.add(coord)
		"""This finds all neighbors of active cells,
		to determine which cells need to be simulated."""
		self.sim_cells.update(
			[(x + a, y + b)
			for a in range(-1,2) for b in range(-1,2)
			for (x,y) in self.sim_cells
			if Cell.valid_coord(Cell.ref_dict[(x,y)], (x + a, y + b))
			and not Cell.ref_dict[(x,y)].empty])
		return self
	
	def update_grid(self):
		"""Update simulated cells, and update the set of sim_cells."""
		self.get_sim_cells()
		"""Two loops are used to stop early death or birth of cells.
		The grid is meant to evolve as a whole each tick,
		and not cell-by-cell.
		"""
		for coord in self.sim_cells:
			Cell.ref_dict[coord].get_new_state()
		for coord in self.sim_cells:
			Cell.ref_dict[coord].update_state()
		return self

class App:
	
	#Matches cell coordinates to the canvas squares.
	canvas_dict = {}
	
	def __init__(
			self, grid_size, cell_size,
			active_color = "black", inactive_color = "white",
			condition_dict = {}, initial_active_cells = [],
			initial_empty_cells = []):
		"""Start a new game.
		
		Positional arguments:
		
			grid_size ------------ Size of grid, in cells.
			Integer.
		
			cell_size ------------ Size of a cell, in pixels.
			Integer.
		
		Keyword arguments:
		
			active_color --------- Color of a cell when alive.
			String or color reference.
			
			inactive_color ------- Color of a cell when dead.
			String or color reference.
			
			condition_dict ------- Nested dictionary.
			Coordinates as keys, dicts of conditions as values.
			Dictionary.
			
			initial_active_cells - List of cells that start alive.
			List.
		"""
		self.grid_size = grid_size
		self.cell_size = cell_size
		self.active_color = active_color
		self.inactive_color = inactive_color
		self.condition_dict = condition_dict
		self.initial_active_cells = initial_active_cells
		self.initial_empty_cells = initial_empty_cells
		
		self.size = grid_size * cell_size
		self.grid = Grid(
			self.grid_size, self.cell_size,
			active_color = self.active_color,
			inactive_color = self.inactive_color,
			condition_dict = self.condition_dict,
			initial_active_cells = self.initial_active_cells,
			initial_empty_cells = self.initial_empty_cells)
		self.root = tk.Tk()
		self.canvas = tk.Canvas(
			self.root, bg = "white",
			height = self.size, width = self.size)
		self.canvas.pack()
		self.render_canvas(canvas_created = False)
		
		self.root.after(1000, self.refresh_display)
		self.root.mainloop()
	
	def refresh_display(self):
		"""Update both grid and canvas."""
		self.grid.update_grid()
		self.render_canvas(canvas_created = True)
		self.root.after(50, self.refresh_display)
	
	def render_canvas(self, canvas_created = False):
		if not canvas_created:
			for x in range(0, self.grid_size):
				for y in range(0, self.grid_size):
					if (x, y) in self.initial_active_cells:
						#This specifies the corners of the polygon.
						App.canvas_dict[(x, y)] = self.canvas.create_polygon(
							x * self.cell_size, y * self.cell_size,
							(x+1) * self.cell_size, y * self.cell_size,
							(x+1) * self.cell_size, (y+1) * self.cell_size,
							x * self.cell_size, (y+1) * self.cell_size,
							fill = self.active_color, outline = "black")
					elif (x, y) in self.initial_empty_cells:
						App.canvas_dict[(x, y)] = self.canvas.create_polygon(
							x * self.cell_size, y * self.cell_size,
							(x+1) * self.cell_size, y * self.cell_size,
							(x+1) * self.cell_size, (y+1) * self.cell_size,
							x * self.cell_size, (y+1) * self.cell_size,
							fill = self.inactive_color, outline = "white")
					else:
						App.canvas_dict[(x, y)] = self.canvas.create_polygon(
							x * self.cell_size, y * self.cell_size,
							(x+1) * self.cell_size, y * self.cell_size,
							(x+1) * self.cell_size, (y+1) * self.cell_size,
							x * self.cell_size, (y+1) * self.cell_size,
							fill = self.inactive_color, outline = "black")
		else:
			for coord in self.grid.sim_cells:
				if Cell.ref_dict[coord].state:
					self.canvas.itemconfig(
						App.canvas_dict[coord], fill = self.active_color)
				else:
					self.canvas.itemconfig(
						App.canvas_dict[coord], fill = self.inactive_color)

if __name__ == "__main__":
	#This gives the default pattern of a Gosper glider gun.
	app = App(60, 5, initial_active_cells = [
		(25,1), (23,2), (25,2), (13,3),
		(14,3), (21,3), (22,3), (35,3),
		(36,3), (12,4), (16,4), (21,4),
		(22,4), (35,4), (36,4), (1,5),
		(2,5), (11,5), (17,5), (21,5),
		(22,5), (1,6), (2,6), (11,6),
		(15,6), (17,6), (18,6), (23,6),
		(25,6), (11,7), (17,7), (25,7),
		(12,8), (16,8), (13,9), (14,9)])
