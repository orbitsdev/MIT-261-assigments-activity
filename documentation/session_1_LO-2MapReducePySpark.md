# Session 2 – MapReduce with PySpark and MongoDB

## 🧪 Title
Implementing MapReduce with PySpark and MongoDB
(MIT 261 – Parallel and Distributed Systems)

## ✅ EXPLANATION OF THE ACTIVITY
This lab activity asks students to apply the MapReduce programming paradigm using:
- **MongoDB**: for loading a collection (students)
- **PySpark**: for distributed processing
- **MapReduce Logic**: using `.select()` (Map) and `.groupBy().count()` (Reduce)

## 📝 Step-by-Step Flow

### 1. Environment Setup
- Install required libraries:
  - `pyspark` → for distributed data processing
  - `pymongo` → for MongoDB connection
  - `pandas` → for data manipulation and display
  - `python-dotenv` → for secure environment variable loading

### 2. Create/Update .env file
- Store MongoDB credentials securely:
  ```
  MONGO_USER=your_username
  MONGO_PASS=your_password
  MONGO_HOST=your_cluster_hostname
  ```

### 3. Load Environment Variables
- Use `load_dotenv()` to load credentials
- Retrieve and mask sensitive information

### 4. Connect to MongoDB
- Build secure connection URI with encoded password
- Configure SparkSession with MongoDB connector

### 5. MAP Phase
- Load data from MongoDB collection
- Select specific fields using `.select()`:
  - `_id`, `Name`, `Course`, `YearLevel`
- Display preview of mapped data

### 6. REDUCE Phase
- Group data by `Course` field
- Count students in each course using `.count()`
- Display aggregated results

### 7. Output Formats
- Show results in tabular format
- Convert to dictionary for JSON representation
- (Optional) Convert to Pandas DataFrame

### 8. Clean Exit
- Stop SparkSession properly

## ✅ WHAT YOUR SCRIPT IS DOING

| Phase | Description |
|-------|-------------|
| Setup | Loads MongoDB credentials from .env |
| Spark Init | Initializes a SparkSession with Mongo connector |
| Map Phase | Selects only needed fields from students (`_id`, `Name`, `Course`, `YearLevel`) |
| Reduce Phase | Groups by `Course` and performs `count()` to simulate MapReduce aggregation |
| Pandas Output | Optionally converts a preview into Pandas dataframe for screenshots or CSV |
| Dict Output | Converts Spark result into Python dictionary (`{Course: count}`) |
| Clean Exit | Gracefully stops the Spark session |

## ✅ Final Output Expected

### Terminal Display
- ✅ "Environment Loaded" confirmation
- ✅ Masked password for security
- ✅ "SparkSession started" confirmation
- ✅ Student data preview (MAP phase)
- ✅ Course counts (REDUCE phase)
- ✅ Dictionary representation of results

### Screenshots to Submit
- Terminal output showing both MAP and REDUCE results
- Dictionary output showing course distribution

## 📚 Learning Outcomes
- Understanding MapReduce programming paradigm
- Implementing distributed data processing with PySpark
- Connecting PySpark to MongoDB for big data operations
- Performing basic data aggregation operations
