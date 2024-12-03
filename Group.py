import tkinter as tk
from tkinter import messagebox
from collections import deque


class MazeProblem:
    def __init__(self, maze, initial, goal):
        self.maze = maze
        self.initial = initial
        self.goal = goal
        self.rows = len(maze)
        self.cols = len(maze[0])

    def goal_test(self, state):
        """Check if the state is the goal state."""
        return state == self.goal

    def step_cost(self, current_state, action, next_state):
        """Returns the cost of moving from current_state to next_state."""
        return 1  # Each move has a uniform cost of 1 in this maze

    def successor(self, state):
        """Generate successors for a given cell in the maze."""
        successors = []
        row, col = state
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]

        for drow, dcol in directions:
            new_row, new_col = row + drow, col + dcol
            if 0 <= new_row < self.rows and 0 <= new_col < self.cols and self.maze[new_row][new_col] == 0:
                successors.append((None, (new_row, new_col)))

        return successors


class Node_Depth:
    def __init__(self, state, parent=None, action=None, path_cost=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost  # Initialize with the cost to reach this node

    def expand(self, problem):
        """Return a list of child nodes generated from this node."""
        return [
            Node_Depth(next_state, self, action, self.path_cost + problem.step_cost(self.state, action, next_state))
            for action, next_state in problem.successor(self.state)
        ]

    def path(self):
        """Return the path from the root to this node."""
        node, path_back = self, []
        while node:
            path_back.append(node.state)
            node = node.parent
        return list(reversed(path_back))


def depth_limited_search(problem, limit=50):
    """
    Depth-Limited Search (DLS) with correct cost calculation.
    Counts all unique nodes explored during the search.
    """
    explored_nodes = set()  # Set to store all unique nodes visited

    def recursive_dls(node, problem, limit):
        nonlocal explored_nodes

        if node.state not in explored_nodes:
            explored_nodes.add(node.state)

        if problem.goal_test(node.state):
            return node
        elif limit == 0:
            return 'cutoff'
        else:
            cutoff_occurred = False
            for child in node.expand(problem):
                if child.state not in explored_nodes:  # Avoid revisiting nodes in the recursion
                    result = recursive_dls(child, problem, limit - 1)
                    if result == 'cutoff':
                        cutoff_occurred = True
                    elif result is not None:
                        return result
            return 'cutoff' if cutoff_occurred else None

    start_node = Node_Depth(problem.initial)
    result = recursive_dls(start_node, problem, limit)
    return result, len(explored_nodes)  # Return the result and total explored cost


def bfs(maze, start, end):
    """
    Breadth-First Search (BFS) with correct cost calculation.
    Counts all unique nodes explored during the search.
    """
    directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    rows, cols = len(maze), len(maze[0])

    queue = deque([start])
    visited = set([start])  # Set to store all unique nodes visited
    parent = {start: None}

    while queue:
        current = queue.popleft()

        if current == end:
            break

        for direction in directions:
            new_row, new_col = current[0] + direction[0], current[1] + direction[1]
            new_node = (new_row, new_col)

            if (0 <= new_row < rows and 0 <= new_col < cols and
                    maze[new_row][new_col] == 0 and new_node not in visited):
                queue.append(new_node)
                visited.add(new_node)  # Mark as visited
                parent[new_node] = current

    # Reconstruct the path from start to end
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = parent.get(current)

    return path[::-1], len(visited)  # Return path and total explored cost


class MazeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Maze Solver")

        # Initialize main container and variables
        self.rows = 0
        self.cols = 0
        self.blocked_cells = set()
        self.start = None
        self.end = None
        self.cell_labels = []

        # Create frames for each page
        self.page1 = tk.Frame(root)
        self.page2 = tk.Frame(root)
        self.grid_frame = None
        self.result_grid_frame = None

        self.create_page1()  # Display the first page initially

    def create_page1(self):
        """Page 1: Input rows, columns, and define blocked cells"""
        self.page1.grid(row=0, column=0, sticky="nsew")

        # Input for number of rows and columns
        tk.Label(self.page1, text="Number of Rows:").grid(row=0, column=0, padx=10, pady=5)
        self.rows_entry = tk.Entry(self.page1, width=5)
        self.rows_entry.grid(row=0, column=1)

        tk.Label(self.page1, text="Number of Columns:").grid(row=0, column=2, padx=10, pady=5)
        self.cols_entry = tk.Entry(self.page1, width=5)
        self.cols_entry.grid(row=0, column=3)

        # Button to create the grid
        create_grid_button = tk.Button(self.page1, text="Create Grid", command=self.create_grid)
        create_grid_button.grid(row=1, column=0, columnspan=4, pady=10)

        # Button to proceed to the next page
        next_page_button = tk.Button(self.page1, text="Next", command=self.show_page2, state="disabled")
        next_page_button.grid(row=2, column=0, columnspan=4, pady=10)
        self.next_page_button = next_page_button

    def create_grid(self):
        """Creates a grid of labels to mark blocked cells based on rows and columns."""
        try:
            self.rows = int(self.rows_entry.get())
            self.cols = int(self.cols_entry.get())

            if self.grid_frame:
                self.grid_frame.destroy()
            self.grid_frame = tk.Frame(self.page1)
            self.grid_frame.grid(row=3, column=0, columnspan=4, pady=(10, 0))

            self.cell_labels = []
            self.blocked_cells = set()

            for r in range(self.rows):
                row_labels = []
                for c in range(self.cols):
                    label_text = f"({r},{c})"
                    label = tk.Label(self.grid_frame, text=label_text, width=5, height=2, relief="solid", bg="lightblue")
                    label.grid(row=r, column=c)
                    label.bind("<Button-1>", lambda e, r=r, c=c: self.toggle_block(r, c))
                    row_labels.append(label)
                self.cell_labels.append(row_labels)

            self.next_page_button.config(state="normal")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid integers for rows and columns.")

    def toggle_block(self, row, col):
        """Toggle blocked cells by changing the label color."""
        if (row, col) not in self.blocked_cells:
            self.cell_labels[row][col].config(bg="red")
            self.blocked_cells.add((row, col))
        else:
            self.cell_labels[row][col].config(bg="lightblue")
            self.blocked_cells.remove((row, col))

    def show_page2(self):
        """Switch to Page 2 for start/goal input and path finding."""
        self.page1.grid_forget()
        self.create_page2()
        self.page2.tkraise()

    def create_page2(self):
        """Page 2: Input start/goal positions, choose algorithm, and show result"""
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

        tk.Label(self.page2, text="Select Search Algorithm:").grid(row=2, column=0, padx=10, pady=5)
        self.search_algo = tk.StringVar(value="Depth-Limited Search")
        tk.Radiobutton(self.page2, text="Depth-Limited Search", variable=self.search_algo, value="Depth-Limited Search").grid(row=2, column=1)
        tk.Radiobutton(self.page2, text="Breadth-First Search", variable=self.search_algo, value="Breadth-First Search").grid(row=2, column=2)

        find_path_button = tk.Button(self.page2, text="Find Path", command=self.find_path)
        find_path_button.grid(row=3, column=0, columnspan=4, pady=10)

        self.result_text = tk.Text(self.page2, height=10, width=40)
        self.result_text.grid(row=5, column=0, columnspan=4, padx=10, pady=10)

        self.cost_label = tk.Label(self.page2, text="", font=("Arial", 12))
        self.cost_label.grid(row=6, column=0, columnspan=4, pady=5)

    def find_path(self):
        """Finds the path and visually displays it on the grid on Page 2."""
        try:
            start_x, start_y = int(self.start_x_entry.get()), int(self.start_y_entry.get())
            end_x, end_y = int(self.end_x_entry.get()), int(self.end_y_entry.get())
            self.start, self.end = (start_x, start_y), (end_x, end_y)

            maze = [[0] * self.cols for _ in range(self.rows)]
            for r, c in self.blocked_cells:
                maze[r][c] = 1

            problem = MazeProblem(maze, self.start, self.end)

            path, total_cost = None, None
            if self.search_algo.get() == "Depth-Limited Search":
                path_node, total_cost = depth_limited_search(problem, limit=50)
                if path_node != 'cutoff':
                    path = path_node.path()
            elif self.search_algo.get() == "Breadth-First Search":
                path, total_cost = bfs(maze, self.start, self.end)

            self.result_text.delete(1.0, tk.END)
            if path:
                optimized_cost = len(path) - 1  # Optimized cost is the number of steps in the shortest path
                path_display = ['({},{})'.format(pos[0], pos[1]) for pos in path]
                self.result_text.insert(tk.END, '\n'.join(path_display))

                # Display both costs
                self.cost_label.config(
                    text=f"Total explored cost (unique nodes): {total_cost}\n"
                         f"Optimized path cost (shortest path length): {optimized_cost}"
                )
                self.display_path_on_grid(path)
            else:
                messagebox.showinfo("No Path", "No valid path found!")
                self.cost_label.config(text="")
                self.display_path_on_grid([])
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid integers for start and goal positions.")

    def display_path_on_grid(self, path):
        """Creates a grid to visually show the maze with the solution path."""
        if self.result_grid_frame:
            self.result_grid_frame.destroy()
        self.result_grid_frame = tk.Frame(self.page2)
        self.result_grid_frame.grid(row=7, column=0, columnspan=4, pady=(10, 0))

        for r in range(self.rows):
            for c in range(self.cols):
                color = "red" if (r, c) in self.blocked_cells else "green" if (r, c) in path else "lightblue"
                text = f"({r},{c})"
                if (r, c) == self.start:
                    color = "lightgreen"
                    text = "Start"
                elif (r, c) == self.end:
                    color = "lightblue"
                    text = "End"
                label = tk.Label(self.result_grid_frame, text=text, width=5, height=2, relief="solid", bg=color)
                label.grid(row=r, column=c)


# Initialize Tkinter and start the app
root = tk.Tk()
app = MazeApp(root)
root.mainloop()
