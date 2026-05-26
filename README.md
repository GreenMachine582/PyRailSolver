# PyRailSolver

> A Python-based Train Valley World map solver and editor.

![Status](https://img.shields.io/badge/status-pre--alpha-orange)
![Python](https://img.shields.io/badge/python-3.13%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

PyRailSolver is an open-source toolkit for analysing, designing, and solving [Train Valley World](https://store.steampowered.com/app/2244470/Train_Valley_World/) maps. It imports maps from CSV files or builds them through a local web-based editor, models the rail network as a directed graph, simulates train movements, and determines optimal track layouts and routing strategies to achieve map objectives.

The long-term goal is to provide both a practical solver and a visual planning tool that helps players understand *why* a solution works, rather than simply producing one.

---

## Table of Contents

- [Game Context](#game-context)
- [Features](#features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Core Concepts](#core-concepts)
- [Solver Strategy](#solver-strategy)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Example Workflow](#example-workflow)
- [Milestones](#milestones)
- [Objectives](#objectives)
- [Success Criteria](#success-criteria)
- [Contributing](#contributing)
- [License](#license)

---

## Game Context

Train Valley World is a puzzle game where players build railway networks to route trains between stations. Each map presents a fixed set of stations, terrain constraints, and a fleet of trains with defined origins, destinations, and schedules. Players lay track, place junctions, and assign routes to deliver all trains to their destinations without collisions, within budget and time limits.

PyRailSolver treats each map as a graph optimisation problem: given the terrain as a grid, the station positions as fixed nodes, and the trains as demand flows, what is the minimum-cost track layout that routes all trains successfully and maximises the score?

---

## Features

### Current

- [ ] CSV map import
- [ ] Internal graph representation
- [ ] Map validation
- [ ] Pathfinding algorithms
- [ ] Local web interface

### Planned

- [ ] Interactive map editor
- [ ] Multiple train simulation
- [ ] Track cost optimisation
- [ ] Junction conflict detection
- [ ] Throughput analysis
- [ ] Automatic solution generation
- [ ] Solution visualisation
- [ ] Save/load project files
- [ ] Scenario benchmarking
- [ ] Export solutions

### Future

- [ ] AI-assisted optimisation
- [ ] Genetic algorithm solver
- [ ] Community map sharing
- [ ] Replay generation
- [ ] Solver comparison framework
- [ ] WebAssembly deployment

---

## Architecture

```text
┌────────────────────┐     ┌────────────────────┐
│   CSV Importer     │     │   Web Map Editor   │
└─────────┬──────────┘     └─────────┬──────────┘
          │                          │
          └──────────┬───────────────┘
                     │
          ┌──────────▼──────────┐
          │      Map Model      │
          │   (Graph Structure) │
          └──────────┬──────────┘
                     │
          ┌──────────┴──────────┐
          │                     │
 ┌────────▼────────┐   ┌────────▼────────┐
 │  Pathfinding    │   │   Simulation    │
 │     Engine      │   │     Engine      │
 └────────┬────────┘   └────────┬────────┘
          │                     │
          └──────────┬──────────┘
                     │
          ┌──────────▼──────────┐
          │   Optimisation /    │
          │   Solver Engine     │
          └──────────┬──────────┘
                     │
          ┌──────────▼──────────┐
          │   Web UI / Editor   │
          │  (Results & Review) │
          └─────────────────────┘
```

**Data flow:** raw map data enters via CSV import or the web editor, is normalised into the graph model, processed by pathfinding and simulation independently, then fed into the solver which ranks candidate solutions and surfaces results through the UI.

---

## Technology Stack

### Backend

| Package | Purpose |
|---|---|
| Python 3.13+ | Core runtime |
| FastAPI | REST API and web server |
| Pydantic | Data validation and settings |
| NetworkX | Graph modelling and algorithms |
| NumPy | Numerical operations |

### Frontend

| Technology | Purpose |
|---|---|
| FastAPI Templates (Jinja2) | Server-side rendering |
| HTMX | Dynamic UI without a JS framework |
| Bootstrap 5 | Responsive layout and components |
| SVG | Map and route rendering |

### Tooling

| Tool | Purpose |
|---|---|
| Pytest | Unit and integration testing |
| Coverage | Test coverage reporting |
| Ruff | Linting and formatting |
| MyPy | Static type checking |

### Optional / Future

| Package | Purpose |
|---|---|
| PostgreSQL | Persistent map and solution storage |
| SQLModel | ORM layer over Pydantic and SQLAlchemy |
| Redis | Caching and background task queuing |

---

## Core Concepts

### Nodes

Each node in the graph represents a discrete location on the map:

| Type | Description |
|---|---|
| Station | Named origin or destination for trains |
| Platform | Berth within a station (capacity-constrained) |
| Junction | Track fork or merge point |
| Depot | Maintenance or holding area |
| Waypoint | Intermediate routing constraint |
| Track endpoint | Terminal node at a dead end |

### Edges

Each directed edge represents a section of track between two nodes:

| Attribute | Description |
|---|---|
| Construction cost | Gold spent to lay the track |
| Travel distance | Length in grid units |
| Max capacity | Simultaneous trains permitted |
| Direction | One-way or bidirectional |
| Speed limit | Maximum permitted train speed |

### Trains

Each train is defined by:

| Attribute | Description |
|---|---|
| Origin | Starting station |
| Destination | Target station |
| Cargo type | Affects which platforms are valid |
| Speed | Movement rate in simulation ticks |
| Spawn timing | Tick at which the train enters the network |
| Priority | Determines routing precedence in conflicts |

---

## Solver Strategy

The solver operates in sequential stages, each building on the previous:

### Stage 1 — Connectivity

Verify that all required origin-destination pairs are reachable given the current track layout. Maps that fail connectivity checks cannot be solved without additional track.

### Stage 2 — Route Discovery

Generate valid candidate routes using graph search algorithms:

- **Dijkstra** — optimal single-source shortest paths by cost or distance
- **A*** — heuristic-guided search for faster pathfinding on large grids
- **Yen's K-shortest paths** — enumerate *k* alternatives per train pair for solution diversity

### Stage 3 — Simulation

Run discrete-event train movement simulations to identify:

- Deadlocks (circular waiting)
- Track congestion hotspots
- Excess waiting time at junctions
- Signal and reservation conflicts

### Stage 4 — Optimisation

Score and improve candidate layouts against a chosen objective:

| Objective | Description |
|---|---|
| Lowest cost | Minimise total track construction spend |
| Highest throughput | Maximise trains delivered per unit time |
| Fastest completion | Minimise time to deliver all trains |
| Maximum score | Optimise the in-game scoring function |

### Stage 5 — Ranking

Evaluate all candidate solutions across all objectives, apply Pareto filtering, and present ranked results with explanations.

---

## Project Structure

```text
PyRailSolver/
│
├── app/
│   ├── api/          # FastAPI route handlers
│   ├── core/         # Configuration, logging, shared utilities
│   ├── graph/        # Graph model, node/edge types
│   ├── parser/       # CSV and map file importers
│   ├── simulation/   # Discrete-event train simulation
│   ├── solver/       # Route discovery and optimisation
│   ├── optimiser/    # Scoring and candidate ranking
│   ├── renderer/     # SVG generation
│   └── ui/           # Jinja2 templates and static assets
│
├── tests/            # Pytest suites mirroring app/ structure
├── examples/         # Sample maps and solved scenarios
├── docs/             # Extended documentation
├── maps/             # Map CSV files
├── scripts/          # Dev and data-prep utilities
└── README.md
```

---

## Getting Started

> The project has no runnable code yet. This section describes the intended setup once the foundation milestone is complete.

### Prerequisites

- Python 3.13 or later
- `pip` or `uv` (recommended)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/PyRailSolver.git
cd PyRailSolver

# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# Install dependencies
pip install -e ".[dev]"
```

### Running the development server

```bash
uvicorn app.main:app --reload
```

Open `http://localhost:8000` in your browser.

### Running tests

```bash
pytest
```

### Linting and type checking

```bash
ruff check .
mypy app/
```

---

## Example Workflow

1. Import a Train Valley World map from CSV.
2. Validate the map structure and check connectivity.
3. Build the internal graph model.
4. Calculate valid train routes using pathfinding.
5. Simulate train movement and identify conflicts.
6. Optimise the track layout against the chosen objective.
7. Review ranked solutions in the visual UI.
8. Export the winning solution.

---

## Milestones

### Milestone 1 — Foundation

**Goal:** Import and represent maps.

- [x] Project structure and packaging
- [x] Configuration system
- [x] CSV parser
- [ ] Graph model
- [ ] Validation framework
- [ ] Unit tests

**Deliverable:** Load a map and display graph statistics.

---

### Milestone 2 — Visualisation

**Goal:** View maps in a browser.

- [ ] FastAPI application skeleton
- [ ] SVG map renderer
- [ ] Pan and zoom controls
- [ ] Node and edge rendering with labels

**Deliverable:** Interactive read-only map viewer.

---

### Milestone 3 — Editor

**Goal:** Build maps locally without the game.

- [ ] Place and label stations
- [ ] Place junctions
- [ ] Draw track segments
- [ ] Delete objects
- [ ] Save/load map files

**Deliverable:** Fully functional local map editor.

---

### Milestone 4 — Pathfinding

**Goal:** Generate valid train routes.

- [ ] Dijkstra implementation
- [ ] A* implementation
- [ ] Yen's K-shortest paths
- [ ] Route visualisation overlay
- [ ] Route validity checks

**Deliverable:** Train routes displayed on the map.

---

### Milestone 5 — Simulation

**Goal:** Model train behaviour over time.

- [ ] Discrete-event train movement engine
- [ ] Signal and block reservation system
- [ ] Junction conflict detection
- [ ] Deadlock detection and prevention
- [ ] Performance metrics collection

**Deliverable:** Playable simulation mode with metrics.

---

### Milestone 6 — Optimisation

**Goal:** Produce automated solutions.

- [ ] Scoring engine matching in-game rules
- [ ] Candidate layout generation
- [ ] Search heuristics
- [ ] Optimisation algorithms (greedy, local search)
- [ ] Benchmark suite

**Deliverable:** Automatically generated map solutions.

---

### Milestone 7 — Advanced Solver

**Goal:** Find near-optimal solutions on hard maps.

- [ ] Genetic algorithm solver
- [ ] Simulated annealing
- [ ] Monte Carlo tree search
- [ ] Parallel execution via multiprocessing

**Deliverable:** High-performance optimisation engine.

---

## Objectives

The project aims to answer several key questions about any given map:

1. Can every train reach its destination given the current track layout?
2. What track layout minimises total construction cost?
3. What layout maximises train throughput?
4. Where are the bottlenecks and junction conflicts?
5. What route assignment achieves the highest in-game score?
6. How does a proposed solution compare to alternative layouts?

---

## Success Criteria

The project will be considered successful when it can:

- Import a complete map definition from CSV.
- Render maps visually in a browser with full pan/zoom support.
- Simulate train movement accurately against the game's rules.
- Detect congestion, deadlocks, and junction conflicts.
- Generate valid route solutions automatically.
- Rank solutions against defined objectives with clear explanations.
- Provide understandable visual feedback that teaches players *why* a solution works.

---

## Contributing

Contributions are welcome. The project does not yet have a formal contribution guide, but in the meantime:

1. Fork the repository and create a feature branch.
2. Follow the existing code style (enforced by Ruff and MyPy).
3. Write tests for any new logic.
4. Open a pull request with a clear description of the change and its motivation.

If you have ideas for solver strategies, map formats, or game mechanics that the current design does not cover, open an issue first to discuss.

---

## License

[MIT Licence](LICENSE)
