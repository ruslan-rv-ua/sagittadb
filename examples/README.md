# SagittaDB Examples

This directory contains comprehensive examples demonstrating various features and use cases of SagittaDB.

## 📁 Example Files

### 1. `basic_usage.py` - Getting Started
**Purpose**: Introduction to SagittaDB fundamentals  
**Topics Covered**:
- Database connection and setup
- Document insertion (single and batch)
- Basic querying and filtering
- Document updates and deletions
- Count operations

**Run with**:
```bash
cd examples
python basic_usage.py
```

**What you'll learn**:
- How to create and connect to a SagittaDB database
- Basic CRUD operations
- Simple search and filtering techniques

---

### 2. `advanced_querying.py` - Complex Queries
**Purpose**: Advanced search and query patterns  
**Topics Covered**:
- Complex filtering with multiple conditions
- Pattern matching with regular expressions
- Pagination (limit and offset)
- Index creation for performance optimization
- Search optimization techniques

**Run with**:
```bash
cd examples
python advanced_querying.py
```

**What you'll learn**:
- Advanced search patterns and techniques
- Performance optimization with indexes
- Handling large datasets with pagination
- Regular expression pattern matching

---

### 3. `ecommerce_demo.py` - Real-World Application
**Purpose**: Complete e-commerce system simulation  
**Topics Covered**:
- Product catalog management
- Order processing and tracking
- Customer analytics
- Inventory management
- Sales reporting

**Run with**:
```bash
cd examples
python ecommerce_demo.py
```

**What you'll learn**:
- Real-world application architecture
- Complex data relationships
- Business logic implementation
- Analytics and reporting

---

### 4. `performance_benchmark.py` - Performance Testing
**Purpose**: Performance analysis and benchmarking  
**Topics Covered**:
- Bulk insertion performance
- Query performance measurement
- Memory vs file-based database comparison
- Concurrent access patterns
- Performance optimization strategies

**Run with**:
```bash
cd examples
python performance_benchmark.py
```

**What you'll learn**:
- Performance characteristics of SagittaDB
- Benchmarking techniques
- Optimization strategies
- Concurrent access handling

---

### 5. `in_memory_usage.py` - In-Memory Database
**Purpose**: Using SagittaDB as an in-memory database  
**Topics Covered**:
- Session tracking
- Cache implementation
- Real-time analytics
- Data processing pipelines
- Temporary data storage

**Run with**:
```bash
cd examples
python in_memory_usage.py
```

**What you'll learn**:
- In-memory database benefits
- Cache-like operations
- Real-time data processing
- Session and temporary data management

---

### 6. `migration_backup.py` - Data Management
**Purpose**: Database migration and backup strategies  
**Topics Covered**:
- Schema migration between versions
- Data transformation during migration
- Backup creation (file copy and JSON export)
- Data restoration procedures
- Migration validation

**Run with**:
```bash
cd examples
python migration_backup.py
```

**What you'll learn**:
- Database migration strategies
- Backup and restore procedures
- Data validation techniques
- Schema evolution management

---

## 🚀 Quick Start

1. **Setup your environment**:
   ```bash
   # Make sure SagittaDB is installed
   pip install -e .
   
   # Navigate to examples
   cd examples
   ```

2. **Run basic example**:
   ```bash
   python basic_usage.py
   ```

3. **Explore other examples**:
   ```bash
   # Try the e-commerce demo
   python ecommerce_demo.py
   
   # Test performance
   python performance_benchmark.py
   
   # Explore in-memory usage
   python in_memory_usage.py
   ```

## 📊 Generated Files

Running the examples will create various database files:

- `example_basic.db` - Basic usage example data
- `example_advanced.db` - Advanced querying example data
- `ecommerce_products.db` - E-commerce product catalog
- `ecommerce_orders.db` - E-commerce order data
- `benchmark_file.db` - Performance benchmark data
- `legacy_system.db` - Migration example legacy data
- `new_system.db` - Migration example new schema
- Various backup files (`.db` and `.json` formats)

## 🛠️ Customization

Each example is designed to be educational and modifiable:

- **Modify data sizes**: Adjust `num_docs`, `num_queries`, etc. in examples
- **Change scenarios**: Modify the sample data to match your use case
- **Add new operations**: Extend examples with additional SagittaDB features
- **Performance testing**: Adjust benchmark parameters for your system

## 📚 Learning Path

**Recommended order for learning**:

1. **Start with basics**: `basic_usage.py`
2. **Learn advanced features**: `advanced_querying.py`
3. **See real-world usage**: `ecommerce_demo.py`
4. **Understand performance**: `performance_benchmark.py`
5. **Explore in-memory**: `in_memory_usage.py`
6. **Master data management**: `migration_backup.py`

## 🔧 Troubleshooting

**Common issues**:

- **Permission errors**: Ensure write permissions in the examples directory
- **Module not found**: Make sure SagittaDB is installed (`pip install -e .`)
- **Database locked**: Close any existing database connections
- **Performance issues**: Adjust example parameters for your system

## 💡 Tips

- **Clean up**: Remove generated `.db` files between runs if needed
- **Experimentation**: Modify examples to test different scenarios
- **Performance**: Use in-memory databases (`:memory:`) for temporary testing
- **Debugging**: Add print statements to trace execution flow

## 🤝 Contributing

Found an issue or want to add a new example?

1. Create a new example file following the naming pattern
2. Add comprehensive comments and documentation
3. Include it in this README with description
4. Test thoroughly before submitting

Happy coding with SagittaDB! 🏹
