import sys
import psycopg

try:
    # 1. Connect to PostgreSQL
    conn = psycopg.connect(
        dbname="student_db",
        user="postgres",
        password="divya@6",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()
    # print("Database connected successfully!")

except psycopg.OperationalError:
    print("Error: Could not connect to the database.")
    print("Please check whether PostgreSQL is running.")
    sys.exit(1)

# 2. Create table if it does not exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id TEXT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        course VARCHAR(100) NOT NULL
    )
""")
conn.commit()
# print("Students table is ready!")

# 3. Main menu
try:
    while True:
        print("\n--- Student Management System ---")
        print("1. Add Student")
        print("2. View Students")
        print("3. Exit")
        print("4. Search Student")
        print("5. Update Student")
        print("6. Delete Student")

        choice = input("Enter your choice: ").strip()

        if choice not in ["1", "2", "3", "4", "5", "6"]:
            print("Invalid choice! Please enter a number from 1 to 6.")
            continue

        # Add Student
        if choice == "1":
            student_id = input("Enter student ID: ").strip()
            name = input("Enter student name: ").strip()
            course = input("Enter course: ").strip()
            if not student_id or not name or not course:
                print("All fields are required!")
                continue
            cursor.execute("""
                INSERT INTO students (id, name, course)
                VALUES (%s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (student_id, name, course))
            conn.commit()
            if cursor.rowcount == 1:
                print("Student added successfully!")
            else:
                print("This student ID already exists!")

        # View Students
        elif choice == "2":
            cursor.execute("SELECT * FROM students ORDER BY id")
            records = cursor.fetchall()
            if records:
                for student in records:
                    print(
                        f"ID: {student[0]} \n"
                        f"Name: {student[1]} \n"
                        f"Course: {student[2]} \n"
                        f"---------------------"
                    )
            else:
                print("No students found!")

        # Exit
        elif choice == "3":
            print("Thank you!")
            break

        # Search Student
        elif choice == "4":
            search_id = input("Enter student ID: ").strip()
            cursor.execute(
                "SELECT * FROM students WHERE id = %s",
                (search_id,)
            )
            student = cursor.fetchone()
            if student:
                print("Student found:", student)
            else:
                print("Student not found!")

        # Update Student
        elif choice == "5":
            update_id = input("Enter student ID to update: ").strip()
            cursor.execute(
                "SELECT * FROM students WHERE id = %s",
                (update_id,)
            )
            student = cursor.fetchone()
            if student:
                print("Current name:", student[1])
                print("Current course:", student[2])
                new_name = input("Enter new name: ").strip()
                new_course = input("Enter new course: ").strip()
                if not new_name or not new_course:
                    print("Name and course cannot be empty!")
                    continue
                cursor.execute("""
                    UPDATE students
                    SET name = %s, course = %s
                    WHERE id = %s
                """, (new_name, new_course, update_id))
                conn.commit()
                print("Student updated successfully!")
            else:
                print("Student not found!")

        # Delete Student
        elif choice == "6":
            delete_id = input("Enter student ID to delete: ").strip()
            cursor.execute(
                "SELECT * FROM students WHERE id = %s",
                (delete_id,)
            )
            student = cursor.fetchone()
            if student:
                print("Student found:", student)
                confirm = input(
                    "Confirm deletion? (yes/no): "
                ).strip().lower()
                if confirm == "yes":
                    cursor.execute(
                        "DELETE FROM students WHERE id = %s",
                        (delete_id,)
                    )
                    conn.commit()
                    print("Student deleted successfully!")
                else:
                    print("Deletion cancelled!")
            else:
                print("Student not found!")

        else:
            print("Invalid choice! Enter a number from 1 to 6.")

finally:
    cursor.close()
    conn.close()
    print("Database connection closed.")

