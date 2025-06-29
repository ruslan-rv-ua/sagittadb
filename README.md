# 🏹 SagittaDB

<div align="center">

![SagittaDB Logo](https://img.shields.io/badge/SagittaDB-🏹-blue?style=for-the-badge)
[![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-orange?style=for-the-badge)](pyproject.toml)
[![Python](https://img.shields.io/badge/python-3.13+-blue?style=for-the-badge)](https://python.org)

*A lightweight, document-oriented database using SQLite*

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Contributing](#-contributing)

</div>

---

## ✨ Features

- 🎯 **Document-Oriented**: Store and query JSON documents with ease
- ⚡ **SQLite Backend**: Built on reliable SQLite for performance and ACID compliance
- � **Flexible Querying**: Search by exact match, patterns, or multiple values
- � **Indexing Support**: Create custom indexes for optimized queries
- 🧵 **Thread-Safe**: Built-in locking for concurrent access
- � **Zero Dependencies**: Pure Python with optional orjson for better performance

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/sagitta.git

# Navigate to project directory
cd sagitta

# Install in development mode
pip install -e .

# Optional: Install with orjson for better performance
pip install -e ".[orjson]"
```

## 📦 Installation

### Prerequisites

- Python 3.13 or higher
- pip

### Install via pip

```bash
pip install sagittadb
```

### Install from source

```bash
git clone https://github.com/yourusername/sagitta.git
cd sagitta
pip install -e .
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
```

### Advanced Usage

```python
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

For detailed documentation, visit our [Wiki](https://github.com/yourusername/sagitta/wiki) or check out the [API Reference](docs/api.md).

### Key Components

| Component | Description | Status |
|-----------|-------------|--------|
| Core Engine | Main database operations | ✅ Complete |
| Query System | Document search and filtering | ✅ Complete |
| Indexing | Performance optimization | ✅ Complete |
| Concurrency | Thread-safe operations | ✅ Complete |

## 🛠️ Development

### Setup Development Environment

```bash
# Clone and setup
git clone https://github.com/yourusername/sagitta.git
cd sagitta

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Run tests
python -m pytest

# Run tests with coverage
python -m pytest --cov=sagittadb
```

### Project Structure

```
sagitta/
├── src/sagittadb/    # Source code
├── tests/            # Test files
├── docs/             # Documentation
├── examples/         # Example implementations
└── pyproject.toml    # Project configuration
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=sagittadb

# Run specific test module
python -m pytest tests/test_sagittadb.py
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### How to Contribute

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📊 Roadmap

- [x] Core functionality
- [x] Basic documentation
- [ ] Advanced analytics
- [ ] Plugin system
- [ ] Mobile optimization
- [ ] Cloud integration

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Acknowledgments

- Thanks to all contributors who have helped shape Sagitta
- Inspired by the constellation Sagitta (The Arrow)
- Built with ❤️ by the development team

## 📞 Support

- 📧 Email: support@sagitta.dev
- 💬 Discord: [Join our community](https://discord.gg/sagitta)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/sagitta/issues)

---

<div align="center">

**Made with 🏹 and ❤️**

[⬆ back to top](#-sagittadb)

</div>