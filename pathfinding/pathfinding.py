import tkinter as tk
from tkinter import ttk
from collections import deque
import random
import time

ROWS = 28
COLS = 55
CELL = 25

grid = []
start = None
goal = None
mode = "wall"

mouse_down = False


# ===============================
# NEIGHBORS WITH DIRECTIONS
# ===============================

def neighbors(r,c):

    dirs = [
        (1,0,"DOWN"),
        (-1,0,"UP"),
        (0,1,"RIGHT"),
        (0,-1,"LEFT")
    ]

    for dr,dc,d in dirs:

        nr=r+dr
        nc=c+dc

        if 0<=nr<ROWS and 0<=nc<COLS and grid[nr][nc]==0:
            yield nr,nc,d


# ===============================
# DRAWING
# ===============================

def draw_cell(r,c,color):

    x1=c*CELL
    y1=r*CELL
    x2=x1+CELL
    y2=y1+CELL

    canvas.create_rectangle(x1,y1,x2,y2,fill=color,outline="#222")


def draw_grid():

    canvas.delete("all")

    for r in range(ROWS):
        for c in range(COLS):

            color="#1e1e1e"

            if grid[r][c]==1:
                color="#444"

            if (r,c)==start:
                color="#51cf66"

            if (r,c)==goal:
                color="#ff6b6b"

            draw_cell(r,c,color)


# ===============================
# RECONSTRUCT PATH
# ===============================

def reconstruct(parent):

    path=[]
    cur=goal

    while cur:
        path.append(cur)
        cur=parent[cur][0]

    path.reverse()

    steps_box.delete("1.0",tk.END)

    for i,node in enumerate(path):

        r,c=node

        if node!=start and node!=goal:

            draw_cell(r,c,"#FFD43B")

        if parent[node][1]!="START":

            steps_box.insert(tk.END,f"Step {i}: Move {parent[node][1]}\n")

        root.update()
        time.sleep(speed.get()/1000)


# ===============================
# BFS
# ===============================

def bfs():

    queue=deque([start])
    parent={start:(None,"START")}

    while queue:

        node=queue.popleft()

        if node==goal:
            reconstruct(parent)
            return

        for nr,nc,d in neighbors(*node):

            nxt=(nr,nc)

            if nxt not in parent:

                parent[nxt]=(node,d)

                queue.append(nxt)

                if nxt!=goal:
                    draw_cell(nr,nc,"#4dabf7")

                root.update()
                time.sleep(speed.get()/1000)


# ===============================
# DFS
# ===============================

def dfs():

    stack=[start]
    parent={start:(None,"START")}

    while stack:

        node=stack.pop()

        if node==goal:
            reconstruct(parent)
            return

        for nr,nc,d in neighbors(*node):

            nxt=(nr,nc)

            if nxt not in parent:

                parent[nxt]=(node,d)

                stack.append(nxt)

                if nxt!=goal:
                    draw_cell(nr,nc,"#9775fa")

                root.update()
                time.sleep(speed.get()/1000)


# ===============================
# RUN
# ===============================

def run():

    if start is None or goal is None:
        return

    draw_grid()

    if algo.get()=="BFS":
        bfs()
    else:
        dfs()


# ===============================
# MAZE GENERATOR
# ===============================

def generate_maze():

    global grid

    grid=[[1]*COLS for _ in range(ROWS)]

    for r in range(1,ROWS-1,2):
        for c in range(1,COLS-1,2):

            grid[r][c]=0

            direction=random.choice([(2,0),(0,2)])

            nr=r+direction[0]
            nc=c+direction[1]

            if 0<nr<ROWS and 0<nc<COLS:

                grid[nr][nc]=0
                grid[r+direction[0]//2][c+direction[1]//2]=0

    draw_grid()


# ===============================
# RESET
# ===============================

def reset():

    global grid,start,goal

    grid=[[0]*COLS for _ in range(ROWS)]

    start=None
    goal=None

    steps_box.delete("1.0",tk.END)

    draw_grid()


# ===============================
# MOUSE EVENTS
# ===============================

def click(event):

    global start,goal

    c=event.x//CELL
    r=event.y//CELL

    if mode=="start":
        start=(r,c)

    elif mode=="goal":
        goal=(r,c)

    draw_grid()


def drag(event):

    if mode!="wall":
        return

    c=event.x//CELL
    r=event.y//CELL

    if 0<=r<ROWS and 0<=c<COLS:

        grid[r][c]=1
        draw_cell(r,c,"#444")


# ===============================
# MODE
# ===============================

def set_mode(m):
    global mode
    mode=m


# ===============================
# GUI
# ===============================

root=tk.Tk()
root.title("AI Pathfinding Visualizer")

root.state("zoomed")

root.configure(bg="#121212")

main=tk.Frame(root,bg="#121212")
main.pack(fill="both",expand=True)

# LEFT PANEL

panel=tk.Frame(main,bg="#121212",width=260)
panel.pack(side="left",fill="y",padx=15,pady=15)

title=tk.Label(panel,text="Pathfinding",font=("Segoe UI",26,"bold"),fg="white",bg="#121212")
title.pack(pady=10)

ttk.Button(panel,text="Start Node",command=lambda:set_mode("start")).pack(fill="x",pady=4)
ttk.Button(panel,text="Goal Node",command=lambda:set_mode("goal")).pack(fill="x",pady=4)
ttk.Button(panel,text="Draw Walls",command=lambda:set_mode("wall")).pack(fill="x",pady=4)

tk.Label(panel,text="Algorithm",fg="white",bg="#121212").pack(pady=5)

algo=tk.StringVar()
algo.set("BFS")

ttk.Combobox(panel,textvariable=algo,values=["BFS","DFS"]).pack(fill="x")

tk.Label(panel,text="Speed",fg="white",bg="#121212").pack(pady=5)

speed=tk.IntVar()
speed.set(15)

ttk.Scale(panel,from_=1,to=50,variable=speed,orient="horizontal").pack(fill="x")

ttk.Button(panel,text="Run",command=run).pack(fill="x",pady=8)
ttk.Button(panel,text="Reset",command=reset).pack(fill="x")
ttk.Button(panel,text="Generate Maze",command=generate_maze).pack(fill="x",pady=5)

# STEPS BOX

steps_box=tk.Text(panel,height=15,width=30,bg="#1e1e1e",fg="white")
steps_box.pack(pady=10)

# CREDITS

credit=tk.Label(
    panel,
    text="Made By\nARHAN ASHRAF RA2411030010039\nALLAN ROY RA2411030010028\nARJUN ANIL RA2411030010020\nELIJAH AJITH RA2411030010001\nPETER JIJO MANAVANAM RA2411030010045",
    fg="#FFD43B",
    bg="#121212",
    font=("Segoe UI",9)
)

credit.pack(pady=15)

# GRID

canvas=tk.Canvas(main,bg="#181818",highlightthickness=0)
canvas.pack(side="left",fill="both",expand=True,padx=10,pady=10)

canvas.bind("<Button-1>",click)
canvas.bind("<B1-Motion>",drag)

grid=[[0]*COLS for _ in range(ROWS)]

draw_grid()

root.mainloop()