
from flask import Flask,render_template,request
import re
import openai
import os
import numpy as np
import textblob
import sqlite3
from datetime import datetime
import joblib

# Set OpenAI API key
#openai.api_key = "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"

app = Flask(__name__)
user_name = ""
flag = 1

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # Create the user_cc table
    c.execute('''CREATE TABLE IF NOT EXISTS user_cc (
        id INTEGER PRIMARY KEY,
        name TEXT,
        type_cc TEXT,
        bank_cc TEXT,
        cc_name TEXT,
        datestamp TEXT
    )''')
    
    # Create the user table with name and timestamp columns
    c.execute('''CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY,
        name TEXT,
        timestamp TEXT
    )''')
    
    conn.commit()
    conn.close()

@app.route("/",methods=["GET","POST"])
def index():
    global flag
    flag = 1
    return render_template("index.html", flag=flag)

@app.route("/main",methods=["GET","POST"])
def main():
    global flag,user_name
    if flag==1:
        user_name = request.form.get("q")
        flag = 0
        currentDateTime = datetime.now()
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('INSERT INTO user (name,timestamp) VALUES(?,?)',(user_name,currentDateTime))
        conn.commit()
        c.close()
        conn.close()
    return(render_template("main.html",r=user_name))

@app.route("/gpt",methods=["GET","POST"])
def gpt():
    return(render_template("gpt.html"))
  
@app.route("/retrieve_userlog",methods=["GET","POST"])
def retrieve_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''SELECT * FROM user WHERE name = ?''', (user_name,))
    r = c.fetchall()  # Fetch all rows as a list of tuples
    c.close()
    conn.close()
    return(render_template("retrieve_db.html",r=r))

@app.route("/delete_userlog",methods=["GET","POST"])
def delete_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''DELETE FROM user WHERE name = ?''', (user_name,))
    conn.commit()
    c.close()
    conn.close()
    return(render_template("delete_db.html"))

@app.route("/linkcc",methods=["GET","POST"])
def linkcc():
    message = ""
    credit_card_added = ""

    if request.method == "POST":
        card_type = request.form.get('cardType')
        bank_name = request.form.get('bank')
        cc_name = request.form.get('creditCard')
        
        if card_type and bank_name and cc_name:
            # Check if the credit card from this bank already exists for the user
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute('''SELECT * FROM user_cc WHERE name = ? AND bank_cc = ? AND cc_name = ?''', (user_name, bank_name, cc_name))
            existing_card = c.fetchone()
            
            if existing_card:
                message = f"The credit card '{cc_name}' from {bank_name} has already been added."
            else:
                # Insert the data into the user_cc table
                datestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                c.execute('''INSERT INTO user_cc (name, type_cc, bank_cc, cc_name, datestamp)
                            VALUES (?, ?, ?, ?, ?)''', (user_name, card_type, bank_name, cc_name, datestamp))
                conn.commit()
                message = f"Credit card '{cc_name}' added! Do you want to proceed add another 1?"

            # Fetch the updated list of credit cards for this user
            user_cards = get_user_all_credit_cards(user_name)

            conn.close()
            return render_template('linkcc.html', user_name=user_name, message=message, user_cards=user_cards)

    user_cards = get_user_all_credit_cards(user_name)
    

    return render_template('linkcc.html', user_name=user_name, user_cards=user_cards)

@app.route("/removecc", methods=["POST"])
def removecc():
    message = ""
    
    cc_name = request.form.get('cc_name')
    
    print (cc_name)
    if cc_name:
        try:
            # Connect to the database and remove the selected credit card
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            
            # Delete the credit card with the given card_name
            c.execute('''DELETE FROM user_cc WHERE cc_name = ? AND name = ?''', (cc_name, user_name))
            conn.commit()
            
            message = "Credit card removed successfully."
            
            # Fetch the updated list of credit cards for this user
            user_cards = get_user_all_credit_cards(user_name)
            
            conn.close()
            return render_template('linkcc.html', user_name=user_name, message=message, user_cards=user_cards)
        except Exception as e:
            message = f"Error: {e}"
    
    # If no card was selected for removal, simply render the page
    user_cards = get_user_all_credit_cards(user_name)
    return render_template('linkcc.html', user_name=user_name, message=message, user_cards=user_cards)


def generate_gpt_response(prompt):
    # Request the GPT model for a response
    r = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Extract the response content
    response_text = r["choices"][0]["message"]["content"]

    # Formatting the response text
    response_text = response_text.replace("### ", "<h3>").replace("\n", "</h3>\n")
    response_text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", response_text)
    response_text = response_text.replace("\n- ", "<ul><li>").replace("\n", "</li></ul>\n")
    response_text = "<p>" + response_text.replace("\n", "</p><p>") + "</p>"
    
    return response_text

@app.route("/faq",methods=["GET","POST"])
def faq():
    return(render_template("faq.html"))

@app.route("/faq_reply",methods=["GET","POST"]) 
def faq_reply():
    q = request.form.get("q")
    response_text = generate_gpt_response(q)

    return render_template("faq_reply.html", r=response_text)

def get_user_credit_cards(user_name,type):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''SELECT cc_name FROM user_cc WHERE name = ? and type_cc = ?''', (user_name,type))
    r = c.fetchall()  # Fetch all rows as a list of tuples
    c.close()
    conn.close()
    return(r)

def get_user_all_credit_cards(user_name):
    # If GET request, fetch user's existing credit cards
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''SELECT bank_cc, cc_name, datestamp FROM user_cc WHERE name = ? ORDER BY bank_cc,cc_name''', (user_name,))
    user_cards = c.fetchall()
    conn.close()
    return(user_cards)

def get_user_all_credit_cards_With_types(user_name,types):
    # If GET request, fetch user's existing credit cards
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''SELECT bank_cc, cc_name, datestamp FROM user_cc WHERE name = ? and type_cc = ? ORDER BY bank_cc,cc_name''', (user_name,types))
    user_cards = c.fetchall()
    conn.close()
    return(user_cards)


@app.route("/cashback_reply", methods=["GET", "POST"])
def cashback_reply():
    q = request.form.get("q")  # The Merchant Name input
    use_user_cc = 'optIn' in request.form  # Checks if the checkbox was checked
    user_cc = None

    if use_user_cc:
        user_cc = get_user_credit_cards(user_name,'Cashback')  # Fetch user's credit cards from DB
        
    # Building the prompt based on whether the user opted in to use their credit cards
    if user_cc:
        prompt = f"Please state the 4 digit Singapore Credit card MCC Code for {q} and Use the following credit cards for the suggestion: {user_cc}. Order the credit card suggestions by highest cashback rate and show the cashback %. Don't need to return a conclusion."
    else:
        prompt = f"Please state the 4 digit Singapore Credit card MCC Code for {q} and return suggested Singapore Cashback Credit card with cashback % for {q}. Order the credit card suggestions by highest cashback rate. Don't need to return a conclusion."

    response_text = generate_gpt_response(prompt)
    user_cards = get_user_all_credit_cards_With_types(user_name,'Cashback')

    return render_template("gpt_reply.html", r=response_text, user_cards=user_cards, type ='Cashback')

@app.route("/miles_reply", methods=["GET", "POST"])
def miles_reply():
    q = request.form.get("q")  # The Merchant Name input
    use_user_cc = 'optIn' in request.form  # Checks if the checkbox was checked
    user_cc = None

    if use_user_cc:
        user_cc = get_user_credit_cards(user_name,'Miles')  # Fetch user's credit cards from DB

    # Building the prompt based on whether the user opted in to use their credit cards
    if user_cc:
        prompt = f"Please state the 4 digit Singapore Credit card MCC Code for {q} and Use the following credit cards for the suggestion: {user_cc} and suggest miles earn rate for {q}. Order the credit card suggestions by highest miles earn rate. Don't need to return a conclusion."
    else:
        prompt = f"Please state the 4 digit Singapore Credit card MCC Code for {q} and return suggested Singapore Reward Miles Credit card with miles earn rate for {q}. Order the credit card suggestions by highest miles earn rate. Don't need to return a conclusion."

    response_text = generate_gpt_response(prompt)
    user_cards = get_user_all_credit_cards_With_types(user_name,'Miles')
    return render_template("gpt_reply.html", r=response_text, user_cards=user_cards, type = 'Miles')


def preprocess_input(data):
    """Preprocess input data to match training format."""
    data_array = np.array(data, dtype=float).reshape(1, -1)

    scaler = joblib.load("scaler.pkl")  # Ensure the scaler is also saved and loaded

    return scaler.transform(data_array)

@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    prediction = None
    user_inputs = {}

    if request.method == 'POST':
        if not request.form:  # Check if the form is empty
            prediction = "Please fill in the values"
        else:
            try:
                # Extract user inputs
                user_inputs = {
                    'Male': str(request.form['Male']),  # Assuming Male is 0 or 1 (int)
                    'Age': str(request.form['Age']),  # Assuming Age is an integer
                    'Debt': str(request.form['Debt']),  # Assuming Debt is an integer
                    'Married': str(request.form['Married']),  # Assuming Married is 0 or 1 (int)
                    'BankCustomer': str(request.form['BankCustomer']),  # Assuming BankCustomer is 0 or 1 (int)
                    'EducationLevel': str(request.form['EducationLevel']),  # Assuming EducationLevel is an integer
                    'YearsEmployed': str(request.form['YearsEmployed']),  # Assuming YearsEmployed is an integer
                    'PriorDefault': str(request.form['PriorDefault']),  # Assuming PriorDefault is 0 or 1 (int)
                    'Employed': str(request.form['Employed']),  # Assuming Employed is 0 or 1 (int)
                    'CreditScore': str(request.form['CreditScore']),  # Assuming CreditScore is an integer
                    'Citizen': str(request.form['Citizen']),  # Assuming Citizen is 0 or 1 (int)
                    'Income': str(request.form['Income'])  # Assuming Income is an integer
                }
                print(list(user_inputs.values()))
                processed_features = preprocess_input(list(user_inputs.values()))
                print(f"Processed features: {processed_features}")
                # Load the trained model
                model = joblib.load("model.pkl")

                result = model.predict(processed_features)
                print(result)
                prediction = "Approved" if result[0] == 1 else "Denied"
            except Exception as e:
                prediction = f"Error: {str(e)}"
                print(prediction)
    
    return render_template('prediction.html', prediction=prediction, user_inputs=user_inputs)



if __name__ == "__main__":
    init_db()
    app.run()

