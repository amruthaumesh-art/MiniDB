
from pathlib import Path
from minidb import Database

demo_file = Path("data/demo_students.log")
if demo_file.exists():
    demo_file.unlink()

db = Database(str(demo_file))
print("\n========== MINIDB DATABASE DEMO ==========\n")

# 1. INSERT RECORDS
print("1. INSERTING STUDENT RECORDS")

students = [
    {"name": "Ananya", "branch": "CSE IoT-AI", "semester": 5},
    {"name": "Rahul", "branch": "CSE", "semester": 6},
    {"name": "Priya", "branch": "ECE", "semester": 4},
    {"name": "Kiran", "branch": "CSE IoT-AI", "semester": 6},
]

for student in students:
    db.insert(student)

print("Student records inserted successfully.")

# 2. DISPLAY ALL RECORDS
print("\n2. ALL STUDENT RECORDS")
for record in db.all():
    print(record)

# 3. FILTER RECORDS
print("\n3. FILTER: STUDENTS IN SEMESTER 6")
result = db.execute(
    "SELECT * FROM students WHERE semester = 6"
)
for record in result:
    print(record)

# 4. SORTING
print("\n4. SORTING BY SEMESTER - ASCENDING")
print(db.execute(
    "SELECT * FROM students ORDER BY semester ASC"
))

print("\n5. SORTING BY SEMESTER - DESCENDING")
print(db.execute(
    "SELECT * FROM students ORDER BY semester DESC"
))

# 5. AGGREGATION
print("\n6. AGGREGATE QUERIES")
print("Total students:", db.execute(
    "SELECT COUNT(*) FROM students"
))
print("Semester sum:", db.execute(
    "SELECT SUM(semester) FROM students"
))
print("Average semester:", db.execute(
    "SELECT AVG(semester) FROM students"
))

# 6. INDEXING
print("\n7. INDEXING")
db.create_index("branch")

print("Students found using branch index:")
print(db.execute(
    "SELECT * FROM students WHERE branch = 'CSE IoT-AI'"
))

print("Query execution statistics:")
print(db.last_query_stats)

# 7. TRANSACTION COMMIT
print("\n8. TRANSACTION COMMIT")
db.execute("BEGIN")
db.insert({
    "name": "Meera",
    "branch": "ISE",
    "semester": 5,
})
db.execute("COMMIT")

print("Committed student record: Meera")

# 8. TRANSACTION ROLLBACK
print("\n9. TRANSACTION ROLLBACK")
db.execute("BEGIN")
db.insert({
    "name": "Temporary",
    "branch": "CSE",
    "semester": 3,
})
db.execute("ROLLBACK")

print("Temporary record rolled back.")
print("Final student count:", db.execute(
    "SELECT COUNT(*) FROM students"
))

print("\n========== DEMO COMPLETED ==========\n")
