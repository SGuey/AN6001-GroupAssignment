import sqlite3
import pandas as pd
username = "asd"  # Example username

# Connect to SQLite database
conn = sqlite3.connect('database.db')

# Read data into a Pandas DataFrame
#query = "SELECT * FROM user_cc WHERE name = ?"
#df = pd.read_sql_query(query, conn, params=(username,))

# Close the connection
conn.close()

# Display as a table
#print(df)

conn = sqlite3.connect('database.db')

# Read data into a Pandas DataFrame
query = "SELECT * FROM user_cc LIMIT 3"
df = pd.read_sql_query(query, conn, params=())

# Close the connection
conn.close()

# Display as a table
print(df)

conn = sqlite3.connect('database.db')

# Read data into a Pandas DataFrame
query = "SELECT * FROM user LIMIT 3"
df = pd.read_sql_query(query, conn, params=())

# Close the connection
conn.close()

# Display as a table
print(df)
