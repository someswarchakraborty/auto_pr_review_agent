"""Test module for PR review."""
import os
import sqlite3

def insecure_database_operation(user_input):
    """This function has some issues for the PR reviewer to find."""
    # Security issue: SQL injection vulnerability
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Intentional SQL injection vulnerability
    query = f"SELECT * FROM users WHERE username = '{user_input}'"
    cursor.execute(query)
    
    # Resource management issue: not closing connection
    return cursor.fetchall()

def complex_function(a, b, c, d, e, f):
    """This function has complexity issues."""
    # Too many parameters
    result = 0
    
    # Nested conditions for complexity
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        result = f
                    else:
                        result = e
                else:
                    result = d
            else:
                result = c
        else:
            result = b
    else:
        result = a
        
    return result

class UtilityClass:
    """Class with some issues."""
    
    @staticmethod
    def helper_method():
        """Static utility method that could be instance method."""
        return "helper"
    
    def process_data(self, data):
        """Method with debug flag."""
        debug = True  # Security issue: Debug flag enabled
        
        if debug:
            print(f"Processing data: {data}")
            
        # Architecture issue: Direct database access in wrong layer
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM data")
        
        return cursor.fetchall()