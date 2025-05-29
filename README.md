# Pylium

**AI-native metadata framework** for modular, self-describing Python systems — built for the next generation of AI: from generative to agentic to emergent.

> 🧠 Structured intelligence.
> 🛠️ Designed for systems that think — and evolve.

Pylium provides structured metadata for Python systems, enabling AI agents and toolchains to reason about code, enforce access control, and dynamically adapt modules. It's designed for environments where modularity, traceability, and self-awareness of code components are essential.

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

## 🧼 Emergent AI: The Next Evolution

Pylium is more than a framework — it's a **building block for emergent AI systems**. In a world where AI not only generates code but writes, tests, optimizes, and uses it autonomously, Pylium provides the structure and control needed.

### Why Pylium for Emergent AI?

* **Self-Describing Modules**: Every component knows its purpose, dependencies, and license.
* **Dynamic Adaptability**: Enables AI systems to autonomously adapt to new requirements.
* **Secure Self-Development**: Clear licensing and access rules ensure that self-developing AI operates within defined boundaries.

---

## 📀 Manifest Example

```python
__manifest__ = Manifest(
    location=Manifest.Location(__name__, __qualname__),
    description="My impressive AI module",
    authors=[
        Manifest.Author(tag="rr", name="Rouven Raudzus", email="raudzus@autiwire.de", company="AutiWire GmbH")
    ],
    changelog=[
        Manifest.Changelog(version="0.1.0", date=Manifest.Date(2025, 5, 29))
    ],
    license=Manifest.licenses.Apache_2_0,
    status=Manifest.Status.Development,
    thread_safety=Manifest.ThreadSafety.ThreadSafe,
    access_mode=Manifest.AccessMode.Hybrid,
    frontend=Manifest.Frontend.API,
    backend=Manifest.Backend.SQLite | Manifest.Backend.File,
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

Pylium is licensed under the Apache License 2.0 — see `LICENSE`.
Individual modules or classes may define stricter licenses via their manifest headers.

⚠️ For commercial use of proprietary components or for consulting, please contact:
📧 [licensing@autiwire.de](mailto:licensing@autiwire.de)
🌐 [https://autiwire.de/pylium](https://autiwire.de/pylium)

---

## 🤝 Contributing

Pull requests, discussions, and feedback are welcome.
Please review our contribution guidelines (coming soon).

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

Rouven Raudzus — [autiwire.de](https://autiwire.de) / [@raudzus](https://github.com/raudzus)

> "Make every module self-aware."
