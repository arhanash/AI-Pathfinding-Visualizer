# AI Pathfinding Visualizer

A modern **Python-based Pathfinding Visualizer** that demonstrates how **Artificial Intelligence search algorithms** such as **Breadth-First Search (BFS)** and **Depth-First Search (DFS)** work on a grid-based environment.

This application allows users to interactively create walls, generate mazes, and visualize how algorithms explore the search space to find a path between two nodes.

---

## Project Overview

This project was developed as part of an **Artificial Intelligence course simulation assignment**.

The visualizer demonstrates:

* How search algorithms explore nodes
* How paths are constructed from start to goal
* How different algorithms behave in the same environment

The program provides a **visual simulation of AI search techniques** using a modern graphical interface built with **Python Tkinter**.

---

## Features

* Fullscreen modern interface
* BFS (Breadth-First Search) visualization
* DFS (Depth-First Search) visualization
* Drag and draw walls with mouse
* Random maze generator
* Adjustable animation speed
* Step-by-step movement directions (UP, DOWN, LEFT, RIGHT)
* Real-time node exploration visualization
* Reset and run controls
* Interactive grid system

---

## Algorithms Implemented

### Breadth-First Search (BFS)

Breadth-First Search explores nodes **level by level** and guarantees the **shortest path in an unweighted graph**.

**Characteristics**

* Uses a Queue (FIFO)
* Complete
* Optimal for unweighted graphs

Time Complexity:

```
O(b^d)
```

Where
`b` = branching factor
`d` = depth of solution

---

### Depth-First Search (DFS)

Depth-First Search explores nodes **deep into the tree before backtracking**.

**Characteristics**

* Uses a Stack (LIFO)
* May not return shortest path
* Lower memory usage

Time Complexity:

```
O(b^m)
```

Where
`m` = maximum depth

---

## How the Visualization Works

1. User selects **Start Node**
2. User selects **Goal Node**
3. User draws **Walls / Obstacles**
4. User selects algorithm (**BFS / DFS**)
5. Click **Run**
6. Algorithm explores nodes step-by-step
7. Final path is highlighted

The steps are displayed such as:

```
Step 1: RIGHT
Step 2: DOWN
Step 3: LEFT
Step 4: UP
```

---

## Controls

| Button        | Description                   |
| ------------- | ----------------------------- |
| Start Node    | Place the starting node       |
| Goal Node     | Place the target node         |
| Draw Walls    | Create obstacles              |
| Algorithm     | Choose BFS or DFS             |
| Speed         | Control animation speed       |
| Run           | Start algorithm visualization |
| Reset         | Clear grid                    |
| Generate Maze | Create random maze            |

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/arhanash/AI-Pathfinding-Visualizer
```

### 2. Navigate to the Project

```bash
cd AI-Pathfinding-Visualizer
```

### 3. Run the Application

```bash
python ai_pathfinding_visualizer.py
```

Python 3.x is required.

---

## Technologies Used

* Python
* Tkinter (GUI Framework)
* Graph Search Algorithms
* Artificial Intelligence Concepts

---

## Project Structure

```
AI-Pathfinding-Visualizer
│
├── ai_pathfinding_visualizer.py
├── README.md
```

---

## Team Members

**ARHAN ASHRAF**
RA2411030010039

**ALLAN ROY**
RA2411030010028

**ARJUN ANIL**
RA2411030010020

**ELIJAH AJITH**
RA2411030010001

**PETER JIJO MANAVANAM**
RA2411030010045

---

## Future Improvements

Possible enhancements include:

* A* Pathfinding Algorithm
* Bidirectional Search
* Weighted graphs
* Diagonal movement
* More advanced maze generation algorithms
* Export as standalone executable (.exe)

---

## License

This project is developed for **educational purposes** as part of an Artificial Intelligence coursework project.
