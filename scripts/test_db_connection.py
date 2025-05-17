import psycopg2
from psycopg2 import OperationalError
import sys

def test_connection():
    print("Testing database connection...")
    try:
        print("Attempting to connect to PostgreSQL...")
        connection = psycopg2.connect(
            database="E_commerce_chatbot",
            user="E_commerce_chatbot",
            password="E_commerce_chatbot",
            host="localhost",
            port="5432"
        )
        sys.stdout.flush()
        print("Successfully connected to the PostgreSQL database!")
        
        # Test querying the shops table
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM shops LIMIT 1;")
        result = cursor.fetchone()
        print("Successfully queried shops table!")
        if result:
            print("Found existing shop record:", result)
        else:
            print("No shop records found - table is empty")
            
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.stdout.flush()
        
if __name__ == "__main__":
    print("Starting database connection test...")
    sys.stdout.flush()
    test_connection()
    print("Test completed.")
    sys.stdout.flush()
