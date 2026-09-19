# Assignments for CS146S: The Modern Software Developer

This is an independent, educational repository for working through assignments inspired by [CS146S: The Modern Software Developer](https://themodernsoftware.dev), taught at Stanford University in Fall 2025.

It is a personal learning project and is not an official Stanford University or CS146S repository. It is not affiliated with or endorsed by Stanford University or the course staff.

## Repo Setup
These steps work with Python 3.12.

1. Install Anaconda
   - Download and install: [Anaconda Individual Edition](https://www.anaconda.com/download)
   - Open a new terminal so `conda` is on your `PATH`.

2. Create and activate a Conda environment (Python 3.12)
   ```bash
   conda create -n cs146s python=3.12 -y
   conda activate cs146s
   ```

3. Install Poetry
   ```bash
   curl -sSL https://install.python-poetry.org | python -
   ```

4. Install project dependencies with Poetry (inside the activated Conda env)
   From the repository root:
   ```bash
   poetry install --no-interaction
   ```
