# Session 1 – StudentList and SubjectList

## 🧪 Title
Connecting to MongoDB Atlas using Python (pymongo)
(MIT 261 – Parallel and Distributed Systems)

## 📝 Step-by-Step Flow

### 1. Install required libraries
- **pymongo** → for MongoDB connection
- **pandas** → to display tabular data
- **python-dotenv** → to load .env securely

### 2. Create .env file
- Store your MongoDB username and password
- Do not hardcode them in your script

### 3. Load environment variables
- Use `load_dotenv()` from `dotenv`
- Retrieve `MONGO_USER` and `MONGO_PASS` using `os.getenv()`
- Mask the password in terminal output
- Show ************ instead of real password

### 4. Connect to MongoDB Atlas
- Use `MongoClient` with secure URI
- Encode the password safely with `quote_plus()`
- Access your database (`mit261`)

### 5. Query the students collection
- Use `.find()` with projection to show:
  - `_id`, `Name`, `Course`, `YearLevel`
- Count total documents
- Convert results to `pandas.DataFrame`
- Display in terminal

### 6. Query the subjects collection
- Use `.find()` with projection to show:
  - `_id`, `Description`, `Units`, `Teacher`
- Convert to `DataFrame`
- Display in terminal

### 7. (Optional/Recommended)
- Save outputs to `.csv` for backup
- Limit display to first 10 rows (for readability)
- Take a screenshot of your output
  - Terminal output of both tables
  - Masked `.env` loading
  - Optional: screenshots of `.csv` files

### 8. Submit
- Your `.py` file
- Screenshots (or notebook file)

## ✅ Final Output Expected

### Terminal Display
- ✅ "Environment Loaded"
- ✅ Masked password
- ✅ "Documents in students: 500000"
- ✅ First 10 students in table format
- ✅ Subjects listed as table

### Files Created (optional)
- `students_list.csv`
- `subjects_list.csv`