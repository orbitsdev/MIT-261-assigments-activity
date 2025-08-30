# Session 3 – Parallel vs Distributed Computing

## 🧪 Title
Comparing Parallel and Distributed Computing with MongoDB and Python
(MIT 261 – Parallel and Distributed Systems)

## ✅ EXPLANATION OF THE ACTIVITY
This lab activity demonstrates the difference between parallel and distributed computing approaches:
- **Parallel Computing**: Using multiple CPU cores on a single machine
- **Distributed Computing**: Simulating multiple nodes working together across a network

## 📝 Step-by-Step Flow

### 1. Environment Setup
- Install required libraries:
  - `pymongo` → for MongoDB connection
  - `pandas` → for data manipulation
  - `numpy` → for array operations
  - `multiprocessing` → for parallel computing
  - `python-dotenv` → for secure environment variable loading

### 2. Connect to MongoDB
- Load credentials from `.env` file
- Connect to MongoDB Atlas cluster
- Access the `mit261` database

### 3. Load and Process Data
- Fetch students and grades collections
- Convert to pandas DataFrames
- Merge data and explode arrays for analysis

### 4. Parallel Computing Implementation
- Use Python's `multiprocessing` library
- Split data into chunks based on CPU cores
- Process each chunk in parallel
- Measure execution time

### 5. Distributed Computing Simulation
- Simulate network nodes with separate functions
- Add artificial network delay
- Process data chunks across "nodes"
- Measure execution time

### 6. Compare Results
- Verify both approaches produce the same results
- Compare execution times
- Understand tradeoffs between approaches

## 💡 IMPORTANT TIPS FOR HANDLING LARGE COLLECTIONS

### Why Terminal Freezes
When working with MongoDB collections containing 500,000+ documents, your terminal may freeze if you try to display all data at once.

### Problem:
```python
# These can cause terminal to freeze with large datasets
print(df.to_string())
print(df)  # without limiting rows
df.head(100)  # too many rows
```

### Solutions:

#### 1. Limit Output with `.head()` or `.sample()`
```python
# Show only first 10 rows
print(df.head(10).to_string(index=False))

# Or random sample
print(df.sample(10).to_string(index=False))
```

#### 2. Filter Before Display
```python
# Filter to specific criteria first
df_filtered = df[df["Course"] == "Information Technology"]
print(df_filtered.head(10))
```

#### 3. Use MongoDB Query Filters
```python
# Filter at database level before loading to Python
docs = list(collection.find({"Course": "Information Technology"}).limit(10))
df = pd.DataFrame(docs)
```

#### 4. Use Projections to Limit Fields
```python
# Only retrieve needed fields
docs = list(collection.find({}, {"_id": 1, "Name": 1, "Course": 1}))
```

## ✅ Final Output Expected

### Terminal Display
- ✅ "Environment Loaded" confirmation
- ✅ Connection to MongoDB established
- ✅ Data loaded from collections
- ✅ Sample of exploded data
- ✅ Parallel computation time
- ✅ Distributed computation time
- ✅ Sample average grades from both approaches

### Learning Outcomes
- Understanding the difference between parallel and distributed computing
- Implementing parallel processing with Python's multiprocessing
- Simulating distributed systems
- Handling large datasets efficiently
- Measuring and comparing performance
