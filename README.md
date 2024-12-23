# Installation Guide

Follow the steps below to install and run this project on your machine.

## Prerequisites

Ensure you have the following installed on your system:

- [Python 3.12.x](https://www.python.org/downloads/release/python-3120/)
- [Poetry](https://python-poetry.org/docs/#installation) (package manager for Python)

## Installation Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/just-better-code/awaken.git
   cd awaken
   ```

2**Install dependencies**:
   ```bash
   poetry install
   ```

## Running the Project

To run the project, use the following command:
```bash
poetry run python -m awaken.main
```

## Troubleshooting

If you encounter any issues:
- Verify the Python version using:
  ```bash
  python --version
  ```
- Ensure Poetry is installed and correctly configured:
  ```bash
  poetry --version
  ```
- Ensure you are using Python 3.12.x for this project.
   ```bash
   poetry env use 3.12
   ```
- Reinstall dependencies if needed:
  ```bash
  poetry install
  
