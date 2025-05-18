# Pylium Module

A module in Pylium is represented by a set of Python files that work together to provide functionality. The module system follows a clear structure to separate concerns and maintain clean code organization.

## File Structure

### Module

- `project/package/module.py` - Module initialization and exports
- `project/package/module.h.py` - Module header defining the public interface
- `project/package/module.impl.py` - Implementation of the module's functionality

### Package

- `project/package/__init__.py` - Package initialization and export
- `project/package/__header__.py` - Package header defining the public interface
- `project/package/__impl__.py` - Package implementation
- `project/package/__main__.py` - Package CLI and main entry point

### Project

- `project/__init__.py` - Project initialization and exports
- `project/__header__.py` - Project header defining the public interface
- `project/__impl__.py` - Project implementation
- `project/__main__.py` - Project CLI and main entry point
- `project/../pyproject.toml` - Project definitions

### File Tree example

```
project_a/                  # Project
├── __init__.py
├── __header__.py          # Header section
├── __impl__.py           # Implementation section
├── module1.py            # Module under project
├── module1_h.py          # Module header section
├── module1_impl.py       # Module implementation section
│
├── package_x/            # Package under project
│   ├── __init__.py
│   ├── __header__.py     # Header section
│   ├── __impl__.py      # Implementation section
│   ├── module2.py       # Module under package
│   ├── module2_h.py     # Module header section
│   └── module2_impl.py  # Module implementation section
│
└── project_b/           # Project under project
    ├── __init__.py
    ├── __header__.py    # Header section
    ├── __impl__.py     # Implementation section
    │
    └── package_y/      # Package under sub-project
        ├── __init__.py
        ├── __header__.py
        ├── __impl__.py
        └── project_c/  # Project under package
            ├── __init__.py
            ├── __header__.py
            └── __impl__.py
```







