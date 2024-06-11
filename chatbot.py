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

def extract_cwe_id(user_input):
    """
    Extracts CWE ID from user input using regex.

    Args:
        user_input (str): User input containing CWE ID.

    Returns:
        str: CWE ID if found, otherwise None.
    """
    match = re.search(r'CWE-\d+', user_input)
    if match:
        return match.group(0)
    return None

def get_vulnerability_details(cwe_id, detail_type=None):
    """
    Retrieves vulnerability details from the database based on CWE ID.

    Args:
        cwe_id (str): CWE ID to search for.
        detail_type (str): Specific detail type to retrieve (e.g., 'mitigations').

    Returns:
        dict: Formatted vulnerability details if found, otherwise a message indicating no details found.
    """
    try:
        cur = conn.cursor()
        query = "SELECT name, description, detection_methods, potential_mitigations FROM vulnerabilities WHERE cwe = %s"
        cur.execute(query, (cwe_id,))
        row = cur.fetchone()

        if row:
            name, description, detection_methods, potential_mitigations = row
            response = {
                "Name": name,
                "Description": description,
                "Detection Methods": detection_methods,
                "Potential Mitigations": potential_mitigations
            }
            if detail_type:
                return {detail_type: response.get(detail_type.replace(" ", "_"))}
            return response
        else:
            return {"error": "No details found for this CWE ID."}
    except psycopg2.Error as e:
        print("Error retrieving data from the database:", e)
        return {"error": "An error occurred while retrieving data."}
    finally:
        if 'cur' in locals():
            cur.close()

def extract_detail_type(user_input):
    """
    Extracts the detail type from the user input.

    Args:
        user_input (str): User input.

    Returns:
        str: Detail type if found, otherwise None.
    """
    detail_types = ['description', 'detection methods', 'potential mitigations']
    for detail_type in detail_types:
        if detail_type in user_input.lower():
            return detail_type.replace(" ", "_").capitalize()
    return None

def chatbot_response(user_input):
    """
    Generates a response based on user input.

    Args:
        user_input (str): User input.

    Returns:
        str: Response generated by the chatbot.
    """
    if user_input.lower() in ['hello', 'hi']:
        return "Hello! How can I assist you today?"
    if user_input.lower() == 'my name is adveith':
        return "Hello Adveith! How can I assist you today?"
    if user_input.lower() == 'lavdya':
        return "tera baap lavdya"

    cwe_id = extract_cwe_id(user_input)
    if cwe_id:
        detail_type = extract_detail_type(user_input)
        details = get_vulnerability_details(cwe_id, detail_type)
        if "error" in details:
            return details["error"]
        else:
            if detail_type:
                return f"{detail_type.capitalize()}: {details.get(detail_type)}"
            else:
                # Return all details if no specific detail type is requested
                response = (
                    f"Name: {details['Name']}\n"
                    f"Description: {details['Description']}\n"
                    f"Detection Methods: {details['Detection Methods']}\n"
                    f"Potential Mitigations: {details['Potential Mitigations']}"
                )
                return response
    else:
        return "No CWE ID found in the input. Can you please enter another CWE ID?"
