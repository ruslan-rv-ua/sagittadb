# 🏹 SagittaDB

<div align="center">

[![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-orange?style=for-the-badge)](https://pypi.org/project/sagittadb/)
[![Python](https://img.shields.io/badge/python-3.13+-blue?style=for-the-badge)](https://python.org)

*A lightweight, document-oriented database using SQLite*

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Contributing](#-contributing)

</div>

---

## ✨ Features

- 🎯 **Document-Oriented**: Store and query JSON documents with ease
- ⚡ **SQLite Backend**: Built on reliable SQLite for performance and ACID compliance
- 🔍 **Flexible Querying**: Search by exact match, patterns, or multiple values
- 📊 **Indexing Support**: Create custom indexes for optimized queries
- 🧵 **Thread-Safe**: Built-in locking for concurrent access
- 📦 **Zero Dependencies**: Pure Python with optional orjson for better performance

## 📦 Installation

### Prerequisites

- Python 3.13 or higher
- (Optional) [uv](https://github.com/astral-sh/uv) — ultra-fast Python package manager

### Install via pip

```bash
pip install sagittadb
```

### Install via uv (recommended for fast installs)

```bash
uv add sagittadb

# Optional: Install with orjson for better performance
uv add sagittadb[orjson]
```

### Install from source

```bash
git clone https://github.com/ruslan-rv-ua/sagittadb.git
cd sagittadb
pip install .
```

## 🎯 Usage

### Basic Example

```python
from sagittadb import SagittaDB

# Initialize database
db = SagittaDB("my_database.db")  # or ":memory:" for in-memory database

# Insert documents
user_id = db.insert({"name": "Alice", "age": 30, "city": "New York"})
db.insert_many([
    {"name": "Bob", "age": 25, "city": "Los Angeles"},
    {"name": "Charlie", "age": 35, "city": "Chicago"}
])

# Search documents
for user in db.search({"city": "New York"}):
    print(user)

# Pattern matching
for user in db.search_pattern("name", r"^A"):
    print(f"Found user starting with A: {user}")

# Count documents
total_users = db.count()
ny_users = db.count({"city": "New York"})

# Create indexes for better performance
db.create_index("city")
db.create_index("age")

# Find multiple values
young_users = list(db.find_any("age", [20, 21, 22, 23, 24, 25]))

# Update documents
updated_count = db.update({"name": "Alice"}, {"age": 31})

# Remove documents
removed_count = db.remove({"city": "Chicago"})

# Get all documents with pagination
for user in db.all(limit=10, offset=20):
    print(user)

# Close database when done
db.close()
```

## 📚 Documentation

For examples of usage, check out the `examples/` directory in this repository.

## 🛠️ Development

### Setup Development Environment

```bash
# Clone and setup
git clone https://github.com/ruslan-rv-ua/sagittadb.git
cd sagittadb

# Create virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Unix/macOS:
# source .venv/bin/activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"


# Or use uv for faster setup
uv pip install -e ".[dev]"

# Run tests
uv run pytest
uv run pytest --cov=sagittadb
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### How to Contribute

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Made with 🏹 and ❤️**

[⬆ back to top](#-sagittadb)

</div>