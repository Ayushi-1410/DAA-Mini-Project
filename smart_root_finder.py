import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from collections import deque
import heapq
import math


class SmartRouteFinder:

    def __init__(self, root):
        self.root = root
        self.root.title("Smart Route Finder")
        self.root.geometry("1100x750")
        self.root.resizable(False, False)

        # =====================================================
        # GRAPH DATA
        # =====================================================

        self.nodes = {}
        self.edges = {}

        self.node_counter = 0

        self.start_node = None
        self.end_node = None

        # For edge creation/deletion
        self.selected_node = None

        # Current operation
        self.mode = "add_node"

        self.running = False

        # =====================================================
        # GUI
        # =====================================================

        self.create_gui()

        # Load example graph
        self.create_example_graph()

    # =========================================================
    # CREATE GUI
    # =========================================================

    def create_gui(self):

        # -----------------------------------------------------
        # TITLE
        # -----------------------------------------------------

        title = tk.Label(
            self.root,
            text="SMART ROUTE FINDER",
            font=("Arial", 24, "bold")
        )

        title.pack(pady=(10, 0))

        subtitle = tk.Label(
            self.root,
            text="Graph Based Route Finding using Dijkstra, BFS and DFS",
            font=("Arial", 11)
        )

        subtitle.pack(pady=3)

        # -----------------------------------------------------
        # MAIN CONTROL FRAME
        # -----------------------------------------------------

        control_frame = tk.Frame(
            self.root,
            bd=1,
            relief="groove",
            padx=10,
            pady=8
        )

        control_frame.pack(pady=8)

        # Algorithm
        tk.Label(
            control_frame,
            text="Algorithm:",
            font=("Arial", 10, "bold")
        ).grid(row=0, column=0, padx=5)

        self.algorithm_box = ttk.Combobox(
            control_frame,
            values=["Dijkstra", "BFS", "DFS"],
            state="readonly",
            width=12
        )

        self.algorithm_box.current(0)

        self.algorithm_box.grid(
            row=0,
            column=1,
            padx=5
        )

        # Find Path
        self.find_button = tk.Button(
            control_frame,
            text="Find Best Path",
            width=15,
            command=self.find_path
        )

        self.find_button.grid(
            row=0,
            column=2,
            padx=5
        )

        # Example
        tk.Button(
            control_frame,
            text="Example Graph",
            width=14,
            command=self.create_example_graph
        ).grid(
            row=0,
            column=3,
            padx=5
        )

        # Clear
        tk.Button(
            control_frame,
            text="Clear Graph",
            width=14,
            command=self.clear_graph
        ).grid(
            row=0,
            column=4,
            padx=5
        )

        # Reset
        tk.Button(
            control_frame,
            text="Reset",
            width=14,
            command=self.create_example_graph
        ).grid(
            row=0,
            column=5,
            padx=5
        )

        # -----------------------------------------------------
        # GRAPH EDITING OPTIONS
        # -----------------------------------------------------

        edit_frame = tk.Frame(self.root)

        edit_frame.pack(pady=5)

        tk.Label(
            edit_frame,
            text="Graph Tools:",
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT, padx=5)

        # Add Node
        tk.Button(
            edit_frame,
            text="Add Node",
            width=12,
            command=lambda: self.set_mode("add_node")
        ).pack(side=tk.LEFT, padx=3)

        # Add Edge
        tk.Button(
            edit_frame,
            text="Add Edge",
            width=12,
            command=lambda: self.set_mode("add_edge")
        ).pack(side=tk.LEFT, padx=3)

        # Delete Node
        tk.Button(
            edit_frame,
            text="Delete Node",
            width=12,
            command=lambda: self.set_mode("delete_node")
        ).pack(side=tk.LEFT, padx=3)

        # Delete Edge
        tk.Button(
            edit_frame,
            text="Delete Edge",
            width=12,
            command=lambda: self.set_mode("delete_edge")
        ).pack(side=tk.LEFT, padx=3)

        # Start
        tk.Button(
            edit_frame,
            text="Set Start",
            width=12,
            command=lambda: self.set_mode("set_start")
        ).pack(side=tk.LEFT, padx=3)

        # Destination
        tk.Button(
            edit_frame,
            text="Set Destination",
            width=14,
            command=lambda: self.set_mode("set_end")
        ).pack(side=tk.LEFT, padx=3)

        # -----------------------------------------------------
        # CANVAS
        # -----------------------------------------------------

        self.canvas = tk.Canvas(
            self.root,
            width=1150,
            height=570,
            bg="white",
            highlightthickness=1,
            highlightbackground="gray"
        )

        self.canvas.pack(pady=8)

        self.canvas.bind(
            "<Button-1>",
            self.canvas_click
        )

        # -----------------------------------------------------
        # STATUS
        # -----------------------------------------------------

        self.status = tk.Label(
            self.root,
            text="Ready",
            font=("Arial", 11, "bold")
        )

        self.status.pack(pady=3)

        # -----------------------------------------------------
        # LEGEND
        # -----------------------------------------------------

        legend = tk.Label(
            self.root,
            text=(
                "Green = Start   |   Red = Destination   |   "
                "Blue = Visited   |   Yellow = Final Path   |   "
                "Black = Normal Node"
            ),
            font=("Arial", 9)
        )

        legend.pack()

    # =========================================================
    # SET MODE
    # =========================================================

    def set_mode(self, mode):

        if self.running:
            return

        self.mode = mode
        self.selected_node = None

        messages = {

            "add_node":
                "ADD NODE: Click anywhere on the canvas.",

            "add_edge":
                "ADD EDGE: Click two nodes. Then enter edge weight.",

            "delete_node":
                "DELETE NODE: Click a node to delete it.",

            "delete_edge":
                "DELETE EDGE: Click two connected nodes.",

            "set_start":
                "SET START: Click a node.",

            "set_end":
                "SET DESTINATION: Click a node."
        }

        self.status.config(
            text=messages[mode]
        )

        self.draw_graph()

    # =========================================================
    # CANVAS CLICK
    # =========================================================

    def canvas_click(self, event):

        if self.running:
            return

        x = event.x
        y = event.y

        node = self.get_node_at(x, y)

        # =====================================================
        # ADD NODE
        # =====================================================

        if self.mode == "add_node":

            if node is not None:
                return

            # Prevent nodes from being too close
            for data in self.nodes.values():

                distance = math.sqrt(
                    (data["x"] - x) ** 2 +
                    (data["y"] - y) ** 2
                )

                if distance < 50:
                    self.status.config(
                        text="Node is too close to another node."
                    )
                    return

            self.node_counter += 1

            name = self.generate_node_name()

            self.nodes[name] = {
                "x": x,
                "y": y
            }

            self.edges[name] = {}

            self.draw_graph()

            self.status.config(
                text=f"Node {name} added."
            )

        # =====================================================
        # ADD EDGE
        # =====================================================

        elif self.mode == "add_edge":

            if node is None:
                return

            # First node
            if self.selected_node is None:

                self.selected_node = node

                self.status.config(
                    text=(
                        f"First node: {node}. "
                        "Now click the second node."
                    )
                )

                self.draw_graph()

            # Second node
            else:

                first = self.selected_node
                second = node

                if first == second:
                    self.status.config(
                        text="Cannot connect a node to itself."
                    )
                    return

                # Check existing edge
                if second in self.edges[first]:

                    messagebox.showinfo(
                        "Edge Exists",
                        f"Edge {first} - {second} already exists."
                    )

                    self.selected_node = None
                    self.draw_graph()

                    return

                # Ask weight
                weight = simpledialog.askfloat(
                    "Edge Weight",
                    (
                        f"Enter weight / distance for\n"
                        f"{first} ↔ {second}"
                    ),
                    minvalue=0.1,
                    parent=self.root
                )

                if weight is not None:

                    self.add_edge(
                        first,
                        second,
                        weight
                    )

                    self.status.config(
                        text=(
                            f"Edge added: "
                            f"{first} ↔ {second} "
                            f"(Weight = {weight})"
                        )
                    )

                self.selected_node = None

                self.draw_graph()

        # =====================================================
        # DELETE NODE
        # =====================================================

        elif self.mode == "delete_node":

            if node is None:
                return

            confirm = messagebox.askyesno(
                "Delete Node",
                f"Delete node {node} and all its edges?"
            )

            if confirm:

                self.delete_node(node)

                self.draw_graph()

        # =====================================================
        # DELETE EDGE
        # =====================================================

        elif self.mode == "delete_edge":

            if node is None:
                return

            if self.selected_node is None:

                self.selected_node = node

                self.status.config(
                    text=(
                        f"Node {node} selected. "
                        "Now click the connected node."
                    )
                )

                self.draw_graph()

            else:

                first = self.selected_node
                second = node

                if second in self.edges[first]:

                    self.delete_edge(
                        first,
                        second
                    )

                    self.status.config(
                        text=f"Edge {first} ↔ {second} deleted."
                    )

                else:

                    self.status.config(
                        text=(
                            f"No edge exists between "
                            f"{first} and {second}."
                        )
                    )

                self.selected_node = None

                self.draw_graph()

        # =====================================================
        # SET START
        # =====================================================

        elif self.mode == "set_start":

            if node is not None:

                self.start_node = node

                self.status.config(
                    text=f"Start node = {node}"
                )

                self.draw_graph()

        # =====================================================
        # SET DESTINATION
        # =====================================================

        elif self.mode == "set_end":

            if node is not None:

                self.end_node = node

                self.status.config(
                    text=f"Destination = {node}"
                )

                self.draw_graph()

    # =========================================================
    # GENERATE NODE NAME
    # =========================================================

    def generate_node_name(self):

        # A-Z
        if self.node_counter <= 26:
            return chr(
                64 + self.node_counter
            )

        # After Z
        return f"N{self.node_counter}"

    # =========================================================
    # ADD EDGE
    # =========================================================

    def add_edge(
        self,
        node1,
        node2,
        weight
    ):

        # Undirected graph
        self.edges[node1][node2] = weight
        self.edges[node2][node1] = weight

    # =========================================================
    # DELETE NODE
    # =========================================================

    def delete_node(self, node):

        # Remove node from neighbors
        for neighbor in list(
            self.edges[node].keys()
        ):

            if neighbor in self.edges:
                self.edges[neighbor].pop(
                    node,
                    None
                )

        # Delete node data
        self.edges.pop(
            node,
            None
        )

        self.nodes.pop(
            node,
            None
        )

        # Update start/end
        if self.start_node == node:
            self.start_node = None

        if self.end_node == node:
            self.end_node = None

        self.selected_node = None

        self.status.config(
            text=f"Node {node} deleted."
        )

    # =========================================================
    # DELETE EDGE
    # =========================================================

    def delete_edge(
        self,
        node1,
        node2
    ):

        self.edges[node1].pop(
            node2,
            None
        )

        self.edges[node2].pop(
            node1,
            None
        )

    # =========================================================
    # FIND NODE
    # =========================================================

    def get_node_at(
        self,
        x,
        y
    ):

        for name, data in self.nodes.items():

            distance = math.sqrt(
                (data["x"] - x) ** 2 +
                (data["y"] - y) ** 2
            )

            if distance <= 24:
                return name

        return None

    # =========================================================
    # FIND EDGE CLICKED
    # =========================================================

    def distance_point_to_line(
        self,
        px,
        py,
        x1,
        y1,
        x2,
        y2
    ):

        dx = x2 - x1
        dy = y2 - y1

        if dx == 0 and dy == 0:
            return math.sqrt(
                (px - x1) ** 2 +
                (py - y1) ** 2
            )

        t = (
            ((px - x1) * dx +
             (py - y1) * dy)
            /
            (dx * dx + dy * dy)
        )

        t = max(
            0,
            min(1, t)
        )

        closest_x = x1 + t * dx
        closest_y = y1 + t * dy

        return math.sqrt(
            (px - closest_x) ** 2 +
            (py - closest_y) ** 2
        )

    # =========================================================
    # DRAW GRAPH
    # =========================================================

    def draw_graph(self):

        self.canvas.delete("all")

        # -----------------------------------------------------
        # EDGES
        # -----------------------------------------------------

        drawn_edges = set()

        for node1 in self.edges:

            for node2, weight in self.edges[node1].items():

                edge_id = tuple(
                    sorted(
                        [node1, node2]
                    )
                )

                if edge_id in drawn_edges:
                    continue

                drawn_edges.add(edge_id)

                x1 = self.nodes[node1]["x"]
                y1 = self.nodes[node1]["y"]

                x2 = self.nodes[node2]["x"]
                y2 = self.nodes[node2]["y"]

                # Edge
                self.canvas.create_line(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill="gray",
                    width=3
                )

                # Weight position
                mx = (x1 + x2) / 2
                my = (y1 + y2) / 2

                # Weight background
                self.canvas.create_oval(
                    mx - 16,
                    my - 11,
                    mx + 16,
                    my + 11,
                    fill="white",
                    outline="gray"
                )

                self.canvas.create_text(
                    mx,
                    my,
                    text=str(weight),
                    font=("Arial", 9, "bold")
                )

        # -----------------------------------------------------
        # NODES
        # -----------------------------------------------------

        for name, data in self.nodes.items():

            x = data["x"]
            y = data["y"]

            radius = 23

            if name == self.start_node:

                color = "green"

            elif name == self.end_node:

                color = "red"

            elif name == self.selected_node:

                color = "orange"

            else:

                color = "lightblue"

            self.canvas.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                fill=color,
                outline="black",
                width=2
            )

            self.canvas.create_text(
                x,
                y,
                text=name,
                font=("Arial", 11, "bold")
            )

    # =========================================================
    # DIJKSTRA
    # =========================================================

    def dijkstra(self):

        distances = {
            node: float("inf")
            for node in self.nodes
        }

        previous = {}

        distances[self.start_node] = 0

        priority_queue = [
            (0, self.start_node)
        ]

        visited = set()
        visited_order = []

        while priority_queue:

            current_distance, current = heapq.heappop(
                priority_queue
            )

            if current in visited:
                continue

            visited.add(current)

            visited_order.append(current)

            if current == self.end_node:
                break

            for neighbor, weight in self.edges[current].items():

                new_distance = (
                    current_distance + weight
                )

                if new_distance < distances[neighbor]:

                    distances[neighbor] = new_distance

                    previous[neighbor] = current

                    heapq.heappush(
                        priority_queue,
                        (
                            new_distance,
                            neighbor
                        )
                    )

        path = self.reconstruct_path(
            previous
        )

        return (
            visited_order,
            path,
            distances
        )

    # =========================================================
    # BFS
    # =========================================================

    def bfs(self):

        queue = deque(
            [self.start_node]
        )

        visited = {
            self.start_node
        }

        previous = {}

        visited_order = []

        while queue:

            current = queue.popleft()

            visited_order.append(current)

            if current == self.end_node:
                break

            for neighbor in self.edges[current]:

                if neighbor not in visited:

                    visited.add(
                        neighbor
                    )

                    previous[neighbor] = current

                    queue.append(
                        neighbor
                    )

        path = self.reconstruct_path(
            previous
        )

        return (
            visited_order,
            path,
            None
        )

    # =========================================================
    # DFS
    # =========================================================

    def dfs(self):

        stack = [
            self.start_node
        ]

        visited = set()

        previous = {}

        visited_order = []

        while stack:

            current = stack.pop()

            if current in visited:
                continue

            visited.add(current)

            visited_order.append(current)

            if current == self.end_node:
                break

            # Reverse only for predictable traversal
            neighbors = list(
                self.edges[current].keys()
            )

            for neighbor in reversed(
                neighbors
            ):

                if neighbor not in visited:

                    if neighbor not in previous:

                        previous[neighbor] = current

                    stack.append(
                        neighbor
                    )

        path = self.reconstruct_path(
            previous
        )

        return (
            visited_order,
            path,
            None
        )

    # =========================================================
    # RECONSTRUCT PATH
    # =========================================================

    def reconstruct_path(
        self,
        previous
    ):

        if self.start_node == self.end_node:

            return [
                self.start_node
            ]

        if self.end_node not in previous:

            return []

        path = []

        current = self.end_node

        while current != self.start_node:

            path.append(
                current
            )

            current = previous[current]

        path.append(
            self.start_node
        )

        path.reverse()

        return path

    # =========================================================
    # FIND PATH
    # =========================================================

    def find_path(self):

        if self.running:
            return

        if not self.nodes:

            messagebox.showwarning(
                "Graph Empty",
                "Please create a graph first."
            )

            return

        if self.start_node is None:

            messagebox.showwarning(
                "Start Missing",
                "Please select a start node."
            )

            return

        if self.end_node is None:

            messagebox.showwarning(
                "Destination Missing",
                "Please select a destination node."
            )

            return

        algorithm = self.algorithm_box.get()

        # -----------------------------------------------------
        # Run algorithm
        # -----------------------------------------------------

        if algorithm == "Dijkstra":

            visited, path, distances = (
                self.dijkstra()
            )

        elif algorithm == "BFS":

            visited, path, distances = (
                self.bfs()
            )

        else:

            visited, path, distances = (
                self.dfs()
            )

        # -----------------------------------------------------
        # No path
        # -----------------------------------------------------

        if not path:

            messagebox.showinfo(
                "No Path",
                (
                    f"{algorithm} could not find "
                    "a route between the selected nodes."
                )
            )

            return

        self.running = True

        self.find_button.config(
            state=tk.DISABLED
        )

        self.status.config(
            text=f"{algorithm} is searching..."
        )

        # Start animation
        self.animate_visited(
            visited,
            0,
            path,
            algorithm,
            distances
        )

    # =========================================================
    # VISITED ANIMATION
    # =========================================================

    def animate_visited(
        self,
        visited,
        index,
        path,
        algorithm,
        distances
    ):

        if index < len(visited):

            node = visited[index]

            # Draw current graph
            self.draw_graph()

            # Highlight visited node
            if (
                node != self.start_node
                and
                node != self.end_node
            ):

                x = self.nodes[node]["x"]
                y = self.nodes[node]["y"]

                self.canvas.create_oval(
                    x - 23,
                    y - 23,
                    x + 23,
                    y + 23,
                    fill="skyblue",
                    outline="black",
                    width=2
                )

                self.canvas.create_text(
                    x,
                    y,
                    text=node,
                    font=("Arial", 11, "bold")
                )

            self.root.after(
                350,
                lambda: self.animate_visited(
                    visited,
                    index + 1,
                    path,
                    algorithm,
                    distances
                )
            )

        else:

            # Search complete
            # Now highlight ONLY final path
            self.animate_final_path(
                path,
                0,
                algorithm,
                distances
            )

    # =========================================================
    # FINAL PATH HIGHLIGHT
    # =========================================================

    def animate_final_path(
        self,
        path,
        index,
        algorithm,
        distances
    ):

        if index == 0:

            # First redraw clean graph
            self.draw_graph()

        if index < len(path):

            node = path[index]

            # Highlight node
            if (
                node != self.start_node
                and
                node != self.end_node
            ):

                x = self.nodes[node]["x"]
                y = self.nodes[node]["y"]

                self.canvas.create_oval(
                    x - 25,
                    y - 25,
                    x + 25,
                    y + 25,
                    fill="yellow",
                    outline="orange",
                    width=3
                )

                self.canvas.create_text(
                    x,
                    y,
                    text=node,
                    font=("Arial", 11, "bold")
                )

            # Highlight edge
            if index > 0:

                previous = path[index - 1]

                self.draw_highlighted_edge(
                    previous,
                    node
                )

            self.root.after(
                400,
                lambda: self.animate_final_path(
                    path,
                    index + 1,
                    algorithm,
                    distances
                )
            )

        else:

            # -------------------------------------------------
            # COMPLETE
            # -------------------------------------------------

            self.running = False

            self.find_button.config(
                state=tk.NORMAL
            )

            path_text = " → ".join(path)

            if algorithm == "Dijkstra":

                total_distance = distances[
                    self.end_node
                ]

                self.status.config(
                    text=(
                        f"Best Path: {path_text}    |    "
                        f"Total Distance: {total_distance}"
                    )
                )

            else:

                self.status.config(
                    text=(
                        f"Path: {path_text}    |    "
                        f"Edges: {len(path) - 1}"
                    )
                )

    # =========================================================
    # HIGHLIGHT EDGE
    # =========================================================

    def draw_highlighted_edge(
        self,
        node1,
        node2
    ):

        x1 = self.nodes[node1]["x"]
        y1 = self.nodes[node1]["y"]

        x2 = self.nodes[node2]["x"]
        y2 = self.nodes[node2]["y"]

        self.canvas.create_line(
            x1,
            y1,
            x2,
            y2,
            fill="orange",
            width=6
        )

        # Weight
        weight = self.edges[node1][node2]

        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2

        self.canvas.create_oval(
            mx - 17,
            my - 12,
            mx + 17,
            my + 12,
            fill="yellow",
            outline="orange"
        )

        self.canvas.create_text(
            mx,
            my,
            text=str(weight),
            font=("Arial", 9, "bold")
        )

    # =========================================================
    # EXAMPLE GRAPH
    # =========================================================

    def create_example_graph(self):

        if self.running:
            return

        self.nodes = {}
        self.edges = {}

        self.node_counter = 11

        # -----------------------------------------------------
        # Node positions
        # -----------------------------------------------------

        positions = {

            "A": (100, 100),

            "B": (300, 70),

            "C": (500, 100),

            "D": (720, 70),

            "E": (950, 130),

            "F": (220, 260),

            "G": (450, 280),

            "H": (680, 250),

            "I": (900, 320),

            "J": (500, 450),

            "K": (760, 450)
        }

        self.nodes = {
            name: {
                "x": x,
                "y": y
            }
            for name, (x, y)
            in positions.items()
        }

        self.edges = {
            name: {}
            for name in self.nodes
        }

        # -----------------------------------------------------
        # Example weighted roads
        # -----------------------------------------------------

        roads = [

            ("A", "B", 4),

            ("A", "F", 3),

            ("B", "C", 2),

            ("B", "F", 5),

            ("C", "D", 3),

            ("C", "G", 4),

            ("D", "E", 5),

            ("D", "H", 2),

            ("E", "I", 3),

            ("F", "G", 2),

            ("F", "J", 6),

            ("G", "H", 3),

            ("G", "J", 4),

            ("H", "I", 2),

            ("H", "K", 5),

            ("I", "K", 3),

            ("J", "K", 2)
        ]

        for node1, node2, weight in roads:

            self.add_edge(
                node1,
                node2,
                weight
            )

        self.start_node = "A"

        self.end_node = "K"

        self.selected_node = None

        self.mode = "add_node"

        self.draw_graph()

        self.status.config(
            text=(
                "Example Graph loaded. "
                "Start = A, Destination = K"
            )
        )

    # =========================================================
    # CLEAR GRAPH
    # =========================================================

    def clear_graph(self):

        if self.running:
            return

        confirm = messagebox.askyesno(
            "Clear Graph",
            "Delete all nodes and edges?"
        )

        if not confirm:
            return

        self.nodes = {}

        self.edges = {}

        self.node_counter = 0

        self.start_node = None

        self.end_node = None

        self.selected_node = None

        self.draw_graph()

        self.status.config(
            text=(
                "Graph cleared. "
                "Use Add Node to create your graph."
            )
        )


# =============================================================
# MAIN
# =============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = SmartRouteFinder(root)

    root.mainloop()