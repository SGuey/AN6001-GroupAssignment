
from flask import Flask,render_template,request
import re
import openai
import os
import numpy as np
import textblob
import sqlite3
from datetime import datetime

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

@app.route("/cashback_reply",methods=["GET","POST"])
def cashback_reply():
    q = request.form.get("q")
    prompt = f"Please state the 4 digit Singapore Credit card MCC Code for {q} and return suggested Singapore Cashback Credit card together with cashback % for {q}. Order the credit card suggestion by higest cashback rate. Dont need to return conclusion."
    r = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    response_text = r["choices"][0]["message"]["content"]
    # Ensure proper formatting for headers (converting ### to <h3> with a line break)
    response_text = response_text.replace("### ", "<h3>").replace("\n", "</h3>\n")

    # Bold formatting using <b> tags
    response_text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", response_text)

    # List formatting (turning "- " into <ul><li> items)
    response_text = response_text.replace("\n- ", "<ul><li>").replace("\n", "</li></ul>\n")

    # Convert paragraphs into <p> tags for proper separation
    response_text = "<p>" + response_text.replace("\n", "</p><p>") + "</p>"

    # Stop the response after the list section
    # Find the index of the last </ul> tag (end of list) and truncate after it
    #end_of_list = response_text.find("</ul>")
    #if end_of_list != -1:
    #    response_text = response_text[:end_of_list + len("</ul>")]

    return render_template("gpt_reply.html", r=response_text)

@app.route("/miles_reply",methods=["GET","POST"]) 
def miles_reply():
    q = request.form.get("q")
    prompt = f"Please state the 4 digit Singapore Credit card MCC Code for {q} and return suggested Singapore Reward Miles Credit card together with the miles earn rate for {q}. Order the credit card suggestion by higest miles earn rate. Dont need to return conclusion."
    r = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    response_text = r["choices"][0]["message"]["content"]
    # Ensure proper formatting for headers (converting ### to <h3> with a line break)
    response_text = response_text.replace("### ", "<h3>").replace("\n", "</h3>\n")

    # Bold formatting using <b> tags
    response_text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", response_text)

    # List formatting (turning "- " into <ul><li> items)
    response_text = response_text.replace("\n- ", "<ul><li>").replace("\n", "</li></ul>\n")

    # Convert paragraphs into <p> tags for proper separation
    response_text = "<p>" + response_text.replace("\n", "</p><p>") + "</p>"

    # Stop the response after the list section
    # Find the index of the last </ul> tag (end of list) and truncate after it
    #end_of_list = response_text.find("</ul>")
    #if end_of_list != -1:
    #    response_text = response_text[:end_of_list + len("</ul>")]

    return render_template("gpt_reply.html", r=response_text)
   
    
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
            c.execute('''SELECT bank_cc, cc_name, datestamp FROM user_cc WHERE name = ? ORDER BY bank_cc,cc_name ''', (user_name,))
            user_cards = c.fetchall()

            conn.close()
            return render_template('linkcc.html', user_name=user_name, message=message, user_cards=user_cards)

    # If GET request, fetch user's existing credit cards
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''SELECT bank_cc, cc_name, datestamp FROM user_cc WHERE name = ? ORDER BY datestamp DESC''', (user_name,))
    user_cards = c.fetchall()
    conn.close()

    return render_template('linkcc.html', user_name=user_name, user_cards=user_cards)

@app.route("/faq",methods=["GET","POST"])
def faq():
    return(render_template("faq.html"))

@app.route("/faq_reply",methods=["GET","POST"]) 
def faq_reply():
    q = request.form.get("q")
    r = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": q}]
    )

    response_text = r["choices"][0]["message"]["content"]
    # Ensure proper formatting for headers (converting ### to <h3> with a line break)
    response_text = response_text.replace("### ", "<h3>").replace("\n", "</h3>\n")

    # Bold formatting using <b> tags
    response_text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", response_text)

    # List formatting (turning "- " into <ul><li> items)
    response_text = response_text.replace("\n- ", "<ul><li>").replace("\n", "</li></ul>\n")

    # Convert paragraphs into <p> tags for proper separation
    response_text = "<p>" + response_text.replace("\n", "</p><p>") + "</p>"

    return render_template("gpt_reply.html", r=response_text)

if __name__ == "__main__":
    init_db()
    app.run()

""" 
### Commented ###
@app.route("/prediction",methods=["GET","POST"])
def prediction():
    return(render_template("prediction.html"))

@app.route("/DBS",methods=["GET","POST"])
def DBS():
    return(render_template("DBS.html"))

@app.route("/DBS_prediction",methods=["GET","POST"])
def DBS_prediction():
    q = float(request.form.get("q"))
    return(render_template("DBS_prediction.html",r=90.2 + (-50.6*q)))

@app.route("/creditability",methods=["GET","POST"])
def creditability():
    return(render_template("creditability.html"))

@app.route("/creditability_prediction",methods=["GET","POST"])
def creditability_prediction():
    q = float(request.form.get("q"))
    r=1.22937616 + (-0.00011189*q)
    r = np.where(r >= 0.5, "yes","no")
    r = str(r)
    return(render_template("creditability_prediction.html",r=r))

@app.route("/text_sentiment",methods=["GET","POST"])
def text_sentiment():
    return(render_template("text_sentiment.html"))

@app.route("/text_sentiment_result",methods=["GET","POST"])
def text_sentiment_result():
    q = request.form.get("q")
    r = textblob.TextBlob(q).sentiment
    return(render_template("text_sentiment_result.html",r=r))

@app.route("/transfer_money",methods=["GET","POST"])
def transfer_money():
    return(render_template("transfer_money.html")) """