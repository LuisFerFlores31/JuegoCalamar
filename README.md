# JuegoCalamar

JuegoCalamar is a multi-technology university project inspired by Pac-Man and Squid Game mechanics.
It combines agent-based simulation, real-time web visualization, and a 3D OpenGL scene to show autonomous characters competing over a grid map.

## Project Summary

The project simulates two teams of agents:

- Squids (Pacman-like agents) that try to paint and control walkable cells.
- Ghosts (hunter agents) that chase squids, capture them, and manage limited energy.

The simulation runs on a matrix loaded from CSV and exposes the state through an API. That state is consumed by:

- A web dashboard that renders the matrix and agents in real time.
- A Python OpenGL visualization with 3D models, animations, and environment assets.

## Why This Project Is Relevant

This project showcases practical software engineering across multiple domains:

- Multi-language development (Julia + JavaScript + Python).
- Simulation and autonomous agent logic.
- API design and real-time data synchronization.
- Interactive UI rendering with React.
- 3D graphics programming with OpenGL and custom OBJ/MTL assets.

## Architecture

1. Julia backend computes simulation steps and game rules.
2. Genie.jl exposes API endpoints (for example `/run`) with JSON snapshots.
3. React frontend polls the API and renders the board, agents, and energy indicators.
4. OpenGL Python app can consume/update positions and display a 3D world with animated characters and machines.

## Technologies Used

### Backend (Simulation + API)

- Julia
- Agents.jl and Agents.Pathfinding
- Genie.jl (web server + JSON responses)
- HTTP.jl
- DelimitedFiles (CSV matrix loading)

### Frontend (Web Visualizer)

- React 19
- Vite
- JavaScript (ES modules)
- SVG-based rendering for grid and entities
- ESLint

### 3D Visualization

- Python
- Pygame
- PyOpenGL (OpenGL, GLU, GLUT)
- OBJ/MTL custom loader
- Cubemap skybox rendering

### Assets and Data

- CSV matrix map (`backend/Matriz.csv`)
- 3D models and materials (`OPENGL/Player_Squid`, `OPENGL/WheelLoader`, `OPENGL/Envirioment`, etc.)
- Skybox textures (`OPENGL/sky_10_2k/...`)

## Core Features

- Agent-based autonomous movement and pursuit logic.
- Quadrant-based map strategy and divider/crossing behavior.
- Capture mechanics and win conditions (squids vs ghosts).
- Ghost energy system with recharge stations.
- Continuous state updates for visualization clients.
- Real-time board painting progress tracking.

## Repository Structure

- `backend/`: Julia simulation and API (`pacman.jl`, `webapi.jl`).
- `backend/frontend/`: React + Vite real-time visualizer.
- `OPENGL/`: Python OpenGL 3D renderer and assets.

## How To Run (Quick Start)

### 1) Start Julia API

From `backend/`, run the API file:

```julia
julia webapi.jl
```

Default endpoint used by the frontend: `http://localhost:8000/run`

### 2) Start Web Frontend

From `backend/frontend/`:

```bash
npm install
npm run dev
```

### 3) Run OpenGL Visualization (optional)

From `OPENGL/`, run:

```bash
python main.py
```

Install required Python dependencies before running (for example: `pygame`, `PyOpenGL`).

## Learning Outcomes

This project demonstrates:

- Designing simulation systems and game rules.
- Integrating backend logic with real-time frontends.
- Building interactive 3D visualization pipelines.
- Coordinating a full-stack workflow with modular components.
