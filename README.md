# 🧩 Intelligent Tango Puzzle Solver

An interactive Python application that solves **Tango Logic Puzzles** using the **A\* Search Algorithm**. The project combines heuristic-guided state-space exploration with a Tkinter-based graphical interface, allowing users to visualize the solving process and analyze algorithm performance.

---

## 📌 Overview

Tango is a logic puzzle that requires placing symbols while satisfying predefined constraints.

This project models the puzzle as a state-space search problem and applies the **A\* Search Algorithm** to efficiently explore valid states and generate an optimal solution.

The application also provides an interactive GUI that visualizes the search process and displays useful execution statistics.

---

## ✨ Features

- Heuristic-guided A* Search implementation
- Efficient state-space exploration
- Automatic puzzle solving
- Interactive Tkinter graphical interface
- Real-time visualization of search progression
- Displays explored states and execution statistics
- Supports algorithm debugging and analysis

---

## 🛠 Technologies Used

- Python
- Tkinter
- A* Search Algorithm
- Heuristic Search
- State-Space Search

---

## 🧠 Algorithm

The solver uses the **A\* Search Algorithm**, which combines:

- Cost from the initial state *(g(n))*
- Heuristic estimate to the goal *(h(n))*

to evaluate

```
f(n) = g(n) + h(n)
```

This enables the solver to prioritize the most promising states while reducing unnecessary exploration.

---

## 📂 Project Structure

```
.
├──tango_animated_agent.py
└── README.md
```


---

## 🚀 How to Run

1. Clone the repository

```bash
git clone https://github.com/NityaPawar7/a-star-tango-solver.git
```

2. Navigate to the project directory

```bash
cd a-star-tango-solver
```

3. Run the application

```bash
python main.py
```

---

## 📊 Concepts Demonstrated

- Artificial Intelligence
- A* Search
- Heuristic Functions
- State-Space Search
- Graph Search
- Python GUI Development
- Algorithm Visualization

---

## 🎯 Learning Outcomes

This project strengthened my understanding of:

- Designing heuristic-based search algorithms
- State-space problem modeling
- Search optimization techniques
- GUI development using Tkinter
- Debugging and visualizing algorithm execution

---

## 📷 Screenshots

<img width="871" height="852" alt="Screenshot 2026-05-27 000706" src="https://github.com/user-attachments/assets/337790d5-4abf-47cb-866c-a9c9fe968743" />

<img width="861" height="853" alt="Screenshot 2026-05-27 000822" src="https://github.com/user-attachments/assets/a945f49c-186a-4cfc-96ec-2cada8a80354" />

<img width="860" height="856" alt="Screenshot 2026-05-27 001101" src="https://github.com/user-attachments/assets/a387e8e4-45ab-4651-8256-85571c09c63f" />

<img width="438" height="875" alt="Screenshot 2026-05-27 001348" src="https://github.com/user-attachments/assets/e530c926-edae-4f42-b206-4c8856dc61bf" />

---

## 👩‍💻 Author

**Nitya R Pawar**

B.E. Artificial Intelligence & Machine Learning  
BMS College of Engineering, Bengaluru

GitHub: https://github.com/NityaPawar7
