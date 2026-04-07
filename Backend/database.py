import sqlite3
conn=sqlite3.connect('db.sqlite3')
cursor=conn.cursor()

departments = [
    ("Cardiology",),
    ("Neurology",),
    ("Orthopedics",),
    ("Dermatology",),
    ("General Medicine",)
]

cursor.executemany(
    "INSERT INTO Backend_department (name) VALUES (?)",
    departments
)

# Insert Doctors
doctors = [
    ("Dr. Arjun", "Cardiology"),
    ("Dr. Meena", "Neurology"),
    ("Dr. Ravi", "Orthopedics"),
    ("Dr. Divya", "Dermatology"),
    ("Dr. Karthik", "General Medicine")
]

cursor.executemany(
    "INSERT INTO Backend_doctor (name, department) VALUES (?, ?)",
    doctors
)
conn.commit()
conn.close()
