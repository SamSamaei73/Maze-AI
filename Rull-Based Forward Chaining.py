import tkinter as tk
from tkinter import messagebox


class MazeProblem:
    def __init__(self, maze, initial, goal):
        self.maze = maze
        self.initial = initial
        self.goal = goal
        self.rows = len(maze)
        self.cols = len(maze[0])
        self.facts = set()
        self.explored_cost = 0

        self.rules = [
            self.move_up,
            self.move_down,
            self.move_left,
            self.move_right
        ]

    def is_goal(self, position):
        return position == self.goal

    def within_bounds(self, row, col):
        return 0 <= row < self.rows and 0 <= col < self.cols and self.maze[row][col] == 0

    def add_fact(self, fact, path):
        path_tuple = tuple(path)
        if fact not in {pos for pos, _ in self.facts}:
            self.facts.add((fact, path_tuple))
            self.explored_cost += 1

    def move_up(self, position, path):
        row, col = position
        new_pos = (row - 1, col)
        if self.within_bounds(*new_pos):
            self.add_fact(new_pos, path + [new_pos])

    def move_down(self, position, path):
        row, col = position
        new_pos = (row + 1, col)
        if self.within_bounds(*new_pos):
            self.add_fact(new_pos, path + [new_pos])

    def move_left(self, position, path):
        row, col = position
        new_pos = (row, col - 1)
        if self.within_bounds(*new_pos):
            self.add_fact(new_pos, path + [new_pos])

    def move_right(self, position, path):
        row, col = position
        new_pos = (row, col + 1)
        if self.within_bounds(*new_pos):
            self.add_fact(new_pos, path + [new_pos])

    def apply_rules(self):
        self.add_fact(self.initial, [self.initial])

        while True:
            for position, path in self.facts.copy():
                if self.is_goal(position):
                    return list(path), self.explored_cost

                for rule in self.rules:
                    rule(position, list(path))

            if not self.facts:
                return None, self.explored_cost


class MazeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Maze Solver (Forward Chaining)")

        self.rows = 0
        self.cols = 0
        self.blocked_cells = set()
        self.start = None
        self.end = None

        self.page1 = tk.Frame(root)
        self.page2 = tk.Frame(root)
        self.grid_frame = None
        self.result_grid_frame = None
        self.create_page1()

    def create_page1(self):
        self.page1.grid(row=0, column=0, sticky="nsew")

        tk.Label(self.page1, text="Number of Rows:").grid(row=0, column=0, padx=10, pady=5)
        self.rows_entry = tk.Entry(self.page1, width=5)
        self.rows_entry.grid(row=0, column=1)

        tk.Label(self.page1, text="Number of Columns:").grid(row=0, column=2, padx=10, pady=5)
        self.cols_entry = tk.Entry(self.page1, width=5)
        self.cols_entry.grid(row=0, column=3)

        create_grid_button = tk.Button(self.page1, text="Create Grid", command=self.create_grid)
        create_grid_button.grid(row=1, column=0, columnspan=4, pady=10)

        next_page_button = tk.Button(self.page1, text="Next", command=self.show_page2, state="disabled")
        next_page_button.grid(row=2, column=0, columnspan=4, pady=10)
        self.next_page_button = next_page_button

    def create_grid(self):
        try:
            self.rows = int(self.rows_entry.get())
            self.cols = int(self.cols_entry.get())

            if self.grid_frame:
                self.grid_frame.destroy()
            self.grid_frame = tk.Frame(self.page1)
            self.grid_frame.grid(row=3, column=0, columnspan=4, pady=(10, 0))

            self.blocked_cells = set()
            for r in range(self.rows):
                for c in range(self.cols):
                    label_text = f"({r},{c})"
                    label = tk.Label(self.grid_frame, text=label_text, width=5, height=2, relief="solid", bg="lightblue")
                    label.grid(row=r, column=c)
                    label.bind("<Button-1>", lambda e, r=r, c=c: self.toggle_block(r, c))

            self.next_page_button.config(state="normal")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid integers for rows and columns.")

    def toggle_block(self, row, col):
        label = self.grid_frame.grid_slaves(row=row, column=col)[0]
        if (row, col) not in self.blocked_cells:
            label.config(bg="red")
            self.blocked_cells.add((row, col))
        else:
            label.config(bg="lightblue")
            self.blocked_cells.remove((row, col))

    def show_page2(self):
        self.page1.grid_forget()
        self.create_page2()
        self.page2.tkraise()

    def create_page2(self):
        self.page2.grid(row=0, column=0, sticky="nsew")

        tk.Label(self.page2, text="Start Position (x, y):").grid(row=0, column=0, padx=10, pady=5)
        self.start_x_entry = tk.Entry(self.page2, width=5)
        self.start_y_entry = tk.Entry(self.page2, width=5)
        self.start_x_entry.grid(row=0, column=1)
        self.start_y_entry.grid(row=0, column=2)

        tk.Label(self.page2, text="Goal Position (x, y):").grid(row=1, column=0, padx=10, pady=5)
        self.end_x_entry = tk.Entry(self.page2, width=5)
        self.end_y_entry = tk.Entry(self.page2, width=5)
        self.end_x_entry.grid(row=1, column=1)
        self.end_y_entry.grid(row=1, column=2)

        find_path_button = tk.Button(self.page2, text="Find Path", command=self.find_path)
        find_path_button.grid(row=2, column=0, columnspan=4, pady=10)

        self.result_text = tk.Text(self.page2, height=10, width=40)
        self.result_text.grid(row=3, column=0, columnspan=4, padx=10, pady=10)

        self.cost_label = tk.Label(self.page2, text="", font=("Arial", 12))
        self.cost_label.grid(row=4, column=0, columnspan=4, pady=5)

        # Frame for dynamic grid (second page visualization)
        self.result_grid_frame = tk.Frame(self.page2)
        self.result_grid_frame.grid(row=5, column=0, columnspan=4, pady=10)

    def generate_maze(self):
        maze = [[0] * self.cols for _ in range(self.rows)]
        for r, c in self.blocked_cells:
            maze[r][c] = 1
        return maze

    def find_path(self):
        try:
            start_x = int(self.start_x_entry.get())
            start_y = int(self.start_y_entry.get())
            end_x = int(self.end_x_entry.get())
            end_y = int(self.end_y_entry.get())

            self.start = (start_x, start_y)
            self.end = (end_x, end_y)

            maze = self.generate_maze()
            problem = MazeProblem(maze, self.start, self.end)

            solution_path, total_cost = problem.apply_rules()

            self.result_text.delete(1.0, tk.END)
            if solution_path:
                path_display = ['({},{})'.format(pos[0], pos[1]) for pos in solution_path]
                self.result_text.insert(tk.END, '\n'.join(path_display))

                # Calculate optimized cost (steps in the path minus 1)
                optimized_cost = len(solution_path) - 1
                self.cost_label.config(
                    text=f"Total explored cost: {total_cost}\nOptimized path cost: {optimized_cost}"
                )
                self.display_path_on_grid(solution_path)
            else:
                messagebox.showinfo("No Path", "No valid path found!")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid integers for start and goal positions.")

    def display_path_on_grid(self, path):
        """Display the path on the grid, styled like the first page."""
        if self.result_grid_frame:
            for widget in self.result_grid_frame.winfo_children():
                widget.destroy()

        for r in range(self.rows):
            for c in range(self.cols):
                color = "red" if (r, c) in self.blocked_cells else "green" if (r, c) in path else "lightblue"
                text = f"({r},{c})"
                if (r, c) == self.start:
                    color = "lightgreen"
                    text = "Start"
                elif (r, c) == self.end:
                    color = "yellow"
                    text = "End"
                label = tk.Label(self.result_grid_frame, text=text, width=5, height=2, relief="solid", bg=color)
                label.grid(row=r, column=c)


# Initialize the Tkinter root and application
root = tk.Tk()
app = MazeApp(root)
root.mainloop()
