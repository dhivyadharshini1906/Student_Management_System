import psycopg
import logging
import sys

# ---------------- CONFIGURATION ----------------

DB_CONFIG = {
    "dbname": "student_db",
    "user": "postgres",
    "password": "xxxxx",
    "host": "localhost",
    "port": "5432"
}

# ---------------- LOGGING ----------------

logging.basicConfig(
    filename="student_management.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# ---------------- DATABASE CONNECTION ----------------

def connect_database():
    try:
        conn = psycopg.connect(**DB_CONFIG)
        print("Database connected successfully!")
        return conn

    except psycopg.Error:
        logging.exception("Database connection failed.")
        print("Error: Could not connect to the database.")
        print("Check your database settings and PostgreSQL service.")
        return None


# ---------------- CREATE TABLE ----------------

def create_table(conn):
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id TEXT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    course VARCHAR(100) NOT NULL
                )
            """)
        conn.commit()
        print("Students table is ready!")

    except psycopg.Error:
        conn.rollback()
        logging.exception("Table creation failed.")
        print("Error: Could not prepare the students table.")
        sys.exit(1)


# ---------------- INPUT VALIDATION ----------------

def get_non_empty_input(message):
    while True:
        value = input(message).strip()

        if value:
            return value

        print("Error: Input cannot be empty!")


# ---------------- ADD STUDENT ----------------

def add_student(conn):
    student_id = get_non_empty_input("Enter student ID: ")
    name = get_non_empty_input("Enter student name: ")
    course = get_non_empty_input("Enter course: ")

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO students (id, name, course)
                VALUES (%s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (student_id, name, course))

            inserted = cursor.rowcount == 1

        conn.commit()

        if inserted:
            print("Student added successfully!")
        else:
            print("Error: This student ID already exists!")

    except psycopg.Error:
        conn.rollback()
        logging.exception("Adding student failed.")
        print("Error: Could not add the student.")


# ---------------- VIEW STUDENTS ----------------

def view_students(conn):
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, name, course
                FROM students
                ORDER BY id
            """)
            students = cursor.fetchall()

        if not students:
            print("No student records found.")
            return

        print("\n--- Student Records ---")

        for student in students:
            print(
                f"ID: {student[0]} \n"
                f"Name: {student[1]} \n"
                f"Course: {student[2]}\n"
                f"-------------------"
            )

        print(f"Total displayed: {len(students)}")

    except psycopg.Error:
        conn.rollback()
        logging.exception("Viewing students failed.")
        print("Error: Could not retrieve student records.")


# ---------------- SEARCH BY ID ----------------

def search_student(conn):
    student_id = get_non_empty_input("Enter student ID: ")

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, name, course
                FROM students
                WHERE id = %s
            """, (student_id,))

            student = cursor.fetchone()

        if student is None:
            print("Student not found!")
        else:
            print("\nStudent found:")
            print(f"ID: {student[0]}")
            print(f"Name: {student[1]}")
            print(f"Course: {student[2]}")

    except psycopg.Error:
        conn.rollback()
        logging.exception("Searching student by ID failed.")
        print("Error: Could not search for the student.")


# ---------------- UPDATE STUDENT ----------------

def update_student(conn):
    student_id = get_non_empty_input(
        "Enter student ID to update: "
    )

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM students WHERE id = %s",
                (student_id,)
            )

            student = cursor.fetchone()

            if student is None:
                print("Student not found!")
                return

            name = get_non_empty_input("Enter new name: ")
            course = get_non_empty_input("Enter new course: ")

            cursor.execute("""
                UPDATE students
                SET name = %s, course = %s
                WHERE id = %s
            """, (name, course, student_id))

        conn.commit()
        print("Student updated successfully!")

    except psycopg.Error:
        conn.rollback()
        logging.exception("Updating student failed.")
        print("Error: Could not update the student.")


# ---------------- DELETE STUDENT ----------------

def delete_student(conn):
    student_id = get_non_empty_input(
        "Enter student ID to delete: "
    )

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, name FROM students WHERE id = %s",
                (student_id,)
            )

            student = cursor.fetchone()

            if student is None:
                print("Student not found!")
                return

            print(f"Student: {student[1]} (ID: {student[0]})")
            confirm = input(
                "Are you sure you want to delete? (yes/no): "
            ).strip().lower()

            if confirm != "yes":
                print("Deletion cancelled.")
                return

            cursor.execute(
                "DELETE FROM students WHERE id = %s",
                (student_id,)
            )

        conn.commit()
        print("Student deleted successfully!")

    except psycopg.Error:
        conn.rollback()
        logging.exception("Deleting student failed.")
        print("Error: Could not delete the student.")


# ---------------- SEARCH BY NAME ----------------

def search_by_name(conn):
    name = get_non_empty_input(
        "Enter name or part of the name: "
    )

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, name, course
                FROM students
                WHERE name ILIKE %s
                ORDER BY name
            """, (f"%{name}%",))

            students = cursor.fetchall()

        if not students:
            print("No matching students found.")
            return

        for student in students:
            print(
                f"ID: {student[0]} | "
                f"Name: {student[1]} | "
                f"Course: {student[2]}"
            )

    except psycopg.Error:
        conn.rollback()
        logging.exception("Searching students by name failed.")
        print("Error: Could not search by name.")


# ---------------- FILTER BY COURSE ----------------

def filter_by_course(conn):
    course = get_non_empty_input("Enter course name: ")

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, name, course
                FROM students
                WHERE course ILIKE %s
                ORDER BY name
            """, (course,))

            students = cursor.fetchall()

        if not students:
            print("No students found for this course.")
            return

        print(f"\nStudents in {course}:")

        for student in students:
            print(
                f"ID: {student[0]} | "
                f"Name: {student[1]} | "
                f"Course: {student[2]}"
            )

    except psycopg.Error:
        conn.rollback()
        logging.exception("Filtering students by course failed.")
        print("Error: Could not filter students.")


# ---------------- COUNT STUDENTS ----------------

def count_students(conn):
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM students")
            total = cursor.fetchone()[0]

        print(f"Total number of students: {total}")

    except psycopg.Error:
        conn.rollback()
        logging.exception("Counting students failed.")
        print("Error: Could not count students.")


# ---------------- SORT STUDENTS ----------------

def sort_students(conn):
    print("\nSort students by:")
    print("1. Student ID")
    print("2. Student Name")

    choice = input("Enter your choice: ").strip()

    if choice == "1":
        order_column = "id"
    elif choice == "2":
        order_column = "name"
    else:
        print("Invalid choice!")
        return

    try:
        # Column name comes only from the fixed choices above.
        query = f"""
            SELECT id, name, course
            FROM students
            ORDER BY {order_column}
        """

        with conn.cursor() as cursor:
            cursor.execute(query)
            students = cursor.fetchall()

        if not students:
            print("No student records found.")
            return

        for student in students:
            print(
                f"ID: {student[0]} | "
                f"Name: {student[1]} | "
                f"Course: {student[2]}"
            )

    except psycopg.Error:
        conn.rollback()
        logging.exception("Sorting students failed.")
        print("Error: Could not sort students.")


# ---------------- MAIN MENU ----------------

def main():
    conn = connect_database()

    if conn is None:
        sys.exit(1)

    try:
        create_table(conn)

        while True:
            print("\n===== STUDENT MANAGEMENT SYSTEM =====")
            print("1. Add Student")
            print("2. View Students")
            print("3. Search Student by ID")
            print("4. Update Student")
            print("5. Delete Student")
            print("6. Search Student by Name")
            print("7. Filter Students by Course")
            print("8. Count Total Students")
            print("9. Sort Students")
            print("10. Exit")

            choice = input("Enter your choice: ").strip()

            if choice == "1":
                add_student(conn)

            elif choice == "2":
                view_students(conn)

            elif choice == "3":
                search_student(conn)

            elif choice == "4":
                update_student(conn)

            elif choice == "5":
                delete_student(conn)

            elif choice == "6":
                search_by_name(conn)

            elif choice == "7":
                filter_by_course(conn)

            elif choice == "8":
                count_students(conn)

            elif choice == "9":
                sort_students(conn)

            elif choice == "10":
                print("Thank you for using the system!")
                break

            else:
                print("Invalid choice! Enter a number from 1 to 10.")

    except (KeyboardInterrupt, EOFError):
        print("\nProgram interrupted safely.")

    finally:
        conn.close()
        print("Database connection closed.")


# ---------------- PROGRAM ENTRY POINT ----------------

if __name__ == "__main__":
    main()