
from flask import Flask,render_template,request
import openai
import os
import numpy as np
import textblob
import sqlite3
import datetime

# Set OpenAI API key
openai.api_key = "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"

#GPTapi = os.getenv("GPT_API_TOKEN")
#model = genai.GenerativeModel("gemini-1.5-flash")
#genai.configure(api_key="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")

app = Flask(__name__)
user_name = ""
flag = 1

@app.route("/",methods=["GET","POST"])
def index():
    global flag
    flag = 1
    return(render_template("index.html"))

@app.route("/main",methods=["GET","POST"])
def main():
    global flag,user_name
    if flag==1:
        user_name = request.form.get("q")
        flag = 0
        currentDateTime = datetime.datetime.now()
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('INSERT INTO user (name,timestamp) VALUES(?,?)',(user_name,currentDateTime))
        conn.commit()
        c.close()
        conn.close()
    return(render_template("main.html",r=user_name))

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
    return(render_template("transfer_money.html"))

@app.route("/makersuite",methods=["GET","POST"])
def makersuite():
    return(render_template("makersuite.html"))

@app.route("/makersuite_1",methods=["GET","POST"])
def makersuite_1():
    q = "Can you help me prepare my tax return?"
    r = model.generate_content(q)
    return(render_template("makersuite_1_reply.html",r=r.text))

@app.route("/makersuite_gen",methods=["GET","POST"])
def makersuite_gen():
    q = request.form.get("q")
    prompt = f"Please return Singapore Credit card MCC Code for {q}"
    r = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    response_text = r["choices"][0]["message"]["content"].split(".")[0] + "."
    return render_template("makersuite_gen_reply.html", r=response_text)

@app.route("/retrieve_db",methods=["GET","POST"])
def retrieve_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''select * from user''')
    r=""
    for row in c:
        print(row)
        r = r + str(row)
    c.close()
    conn.close()
    return(render_template("retrieve_db.html",r=r))

@app.route("/delete_db",methods=["GET","POST"])
def delete_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''DELETE FROM user''')
    conn.commit()
    c.close()
    conn.close()
    return(render_template("delete_db.html"))

if __name__ == "__main__":
    app.run()
