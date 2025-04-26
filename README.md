# pylium

A modern Python monorepo using implicit namespace packages (PEP 420).

## Project Structure

```
pylium/
├── src/
│   └── pylium/           # PEP 420 namespace package
│       └── core/         # Core functionality
│           └── __init__.py
├── plugins/              # Git submodules for plugins
└── pyproject.toml        # Build configuration
```

## Setup

1. Clone the repository with submodules:
   ```bash
   git clone --recursive git@github.com:your-org/pylium.git
   ```

2. Initialize submodules (if not done during clone):
   ```bash
   git submodule update --init --recursive
   ```

3. Install the main package in development mode:
   ```bash
   pip install -e .
   ```

4. Install plugins in development mode:
   ```bash
   cd plugins/plugin_name
   pip install -e .
   ```

## Development

- Core functionality is in `src/pylium/core/`
- Plugins are managed as Git submodules in `plugins/`
- Each plugin should follow the same structure with its own `src/pylium/plugin_name/` directory
- The namespace `pylium` is shared between core and all plugins

## Running the Application

```bash
python -m pylium
```