# Pylium

**AI-native metadata framework** for modular, self-describing Python systems — designed for the next generation of AI applications, from generative models to agentic and emergent systems.

> 🧠 Structured intelligence.
> 🛠️ Designed for systems that think — and evolve.

Pylium provides structured metadata for Python systems, enabling AI agents and toolchains to reason about code, enforce access control, and dynamically adapt modules. It's designed for environments where modularity, traceability, and self-awareness of code components are essential.

## Table of Contents
- [Pylium](#pylium)
  - [Table of Contents](#table-of-contents)
  - [✨ Features](#-features)
  - [🧬 Emergent AI: The Next Evolution](#-emergent-ai-the-next-evolution)
    - [Why Pylium for Emergent AI?](#why-pylium-for-emergent-ai)
  - [📀 Manifest Example](#-manifest-example)
  - [📦 Installation](#-installation)
  - [📄 Licensing](#-licensing)
  - [🤝 Contributing](#-contributing)
  - [🚀 Roadmap](#-roadmap)
  - [👤 Maintainer](#-maintainer)

---

## ✨ Features

* 📦 **Per-Class & Per-Module Metadata**
  Manifest-based headers define structure, purpose, licensing, access levels, and more.

* 🤖 **AI-Oriented Reflection**
  Enables structured code introspection, intelligent editing, module recognition and justification.

* 🔐 **Granular Licensing & Access Control**
  Globally licensed under Apache 2.0, with support for proprietary or commercial licenses per class or module.

* ↺ **Self-Contained & Lightweight**
  No runtime dependencies. Static metadata is interpreted at load or compile time.

* 🧠 **Toolchain-Compatible**
  Works with code generators, linters, packagers, and AI-driven IDEs.

---

## 🧬 Emergent AI: The Next Evolution

Pylium is more than a framework — it's a **building block for emergent AI systems**. In a world where AI not only generates code but writes, tests, optimizes, and uses it autonomously, Pylium provides the structure and control needed.

### Why Pylium for Emergent AI?

* **Self-Describing Modules**: Every component knows its purpose, dependencies, and license.
* **Dynamic Adaptability**: Enables AI systems to autonomously adapt to new requirements.
* **Secure Self-Development**: Clear licensing and access rules ensure that self-developing AI operates within defined boundaries.

---

## 📀 Manifest Example

```python

# Create an AuthorList instance
_project_authors = Manifest.AuthorList([Manifest.Author(tag="rr", name="Rouven Raudzus", email="raudzus@autiwire.de", company="AutiWire GmbH")])
_project_maintainers = _project_authors # might differ 

__manifest__ = Manifest(
    location=Manifest.Location(__name__, __qualname__), # For a class
    # location=Manifest.Location(__name__), # For a module
    description="My impressive AI module",
    authors=_project_authors,
    maintainers=_project_maintainers,
    copyright=Manifest.Copyright(date=Manifest.Date(2025, 1, 1), author=_project_authors.rr),
    license=Manifest.licenses.Apache2,
    status=Manifest.Status.Development,
    dependencies=[
        Manifest.Dependency(type=Manifest.Dependency.Type.PIP, name="fire", version=">=0.7.0"),
    ],
    changelog=[
        Manifest.Changelog(version="0.1.0", date=Manifest.Date(2025, 5, 29), author=_project_authors.rr, notes=["Initial release of my impressive AI module."])
    ],
    thread_safety=Manifest.ThreadSafety.ThreadSafe,
    access_mode=Manifest.AccessMode.Hybrid,
    frontend=Manifest.Frontend.API,
    backend=Manifest.Backend.SQLite | Manifest.Backend.File,
    ai_access_level=Manifest.AIAccessLevel.Read | Manifest.AIAccessLevel.SuggestOnly,
)
```

---

## 📦 Installation

Pylium is in its early phase — a stable API will soon be available via PyPI.

```bash
pip install pylium  # (coming soon)
```

Until then, you can install it locally:

```bash
git clone https://github.com/autiwire/pylium.git
cd pylium
pip install -e .
```

---

## 📄 Licensing

Pylium is licensed under the Apache License 2.0 — see [`LICENSE.md`](LICENSE.md).
Individual modules or classes may define stricter licenses via their manifest headers.

⚠️ For commercial use of proprietary components or for consulting, please contact:
📧 [info@autiwire.de](mailto:info@autiwire.de)
🌐 [https://autiwire.de](https://autiwire.de)

---

## 🤝 Contributing

Pull requests, discussions, and feedback are welcome.
Please review our [contribution guidelines](CONTRIBUTING.md).

---

## 🚀 Roadmap

* Manifest system with licensing / access / thread-safety metadata
* Structured enums for access, backend, frontend
* `pylium.cli` – manifest inspection & validation
* Integration with code generators (e.g. crowbar)
* VSCode / AI IDE support (autocompletion, documentation hints, restrictions)
* PyPI release

---

## 👤 Maintainer

Rouven Raudzus — [autiwire.de](https://autiwire.de) / [@rraudzus](https://github.com/Verlusti)

> "Make every module self-aware."
