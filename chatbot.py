import psycopg2
import re

# Establish connection to the PostgreSQL database
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="adi",
    host="localhost",
    port="5432"
)

# Function to extract CWE ID from user input using regular expressions
def extract_cwe_id(user_input):
    """
    Extracts CWE ID from user input using regex.

    Args:
        user_input (str): User input containing CWE ID.

    Returns:
        str: CWE ID if found, otherwise None.
    """
    # Use regex to find CWE ID in the format CWE-XXX
    match = re.search(r'CWE-\d+', user_input)
    if match:
        return match.group(0)
    else:
        return None

# Function to get vulnerability details based on CWE ID
def get_vulnerability_details(cwe_id):
    """
    Retrieves vulnerability details from the database based on CWE ID.

    Args:
        cwe_id (str): CWE ID to search for.

    Returns:
        str: Formatted vulnerability details if found, otherwise a message indicating no details found.
    """
    try:
        # Create a cursor object to execute SQL queries
        cur = conn.cursor()

        # Execute SQL query to retrieve vulnerability details based on CWE ID
        cur.execute("SELECT name, description, detection_methods, potential_mitigations FROM vulnerabilities WHERE cwe = %s", (cwe_id,))
        row = cur.fetchone()  # Fetch the first row

        if row:
            name, description, detection_methods, potential_mitigations = row

            # Format the response
            response = (
                f"Name: {name}\n"
                f"Description:\n{description}\n"
                f"Detection Methods:\n{detection_methods}\n"
                f"Potential Mitigations:\n{potential_mitigations}"
            )
            return response
        else:
            return "No details found for this CWE ID."
    except psycopg2.Error as e:
        print("Error retrieving data from the database:", e)
        return "An error occurred while retrieving data."

    finally:
        # Close the cursor
        if 'cur' in locals():
            cur.close()

# Function to generate a response based on user input
def chatbot_response(user_input):
    """
    Generates a response based on user input.

    Args:
        user_input (str): User input.

    Returns:
        str: Response generated by the chatbot.
    """
    if user_input.lower() == 'hello':
        return "Hello! How can I assist you today?"
    
    cwe_id = extract_cwe_id(user_input)  # Extract CWE ID from user input
    if cwe_id:
        details = get_vulnerability_details(cwe_id)  # Get vulnerability details based on CWE ID
        return details
    else:
        return "No CWE ID found in the input."

# Main loop for chatbot interaction
if __name__ == "__main__":
    try:
        while True:
            user_input = input("User: ")  # Prompt user for input
            if user_input.lower() == 'exit':  # Check if user wants to exit
                break
            response = chatbot_response(user_input)  # Get response from chatbot
            print("Bot:", response)  # Print response
    except KeyboardInterrupt:
        print("\nExiting...")

# Close the database connection
conn.close()
