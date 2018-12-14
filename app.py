from flask import Flask, render_template, request
import pymysql
from datetime import datetime
import dbact

app = Flask(__name__)

flag = {}
data = {}

@app.route("/")
def home():
    return render_template("index.html")



@app.route("/get")
def get_bot_response():
    #user booking responses
    userText = request.args.get('msg')
    userText = userText.lower()
    if(userText in dbact.greetings):
        return str("How can I help you")
    elif(userText in dbact.bookText):
        return str("Where do you want to travel")
    elif(userText in dbact.destination and not bool(flag)):
        data['destination'] = userText
        flag['x'] = 1
        return str("From where you are travelling")
    elif(userText in dbact.source):
        data['source'] = userText
        del flag['x']
        return str("On which date would you like to leave")
    elif(dbact.validate(userText)):
        data['date'] = userText
        alldata = dbact.store_data(data)
        if(len(alldata) != 0):
            for adata in alldata:
                string = "Here are the flight details: "
                return (string+"<br> Flight Number : {0}, <br>Airline : {1}, <br> From : {2}, <br> To : {3}, <br> Fare : {4}, <br> On : {5} <br/>".format(adata[0], adata[1], adata[2],adata[3], adata[4], adata[5])+" Should I book it?")
        else:
            return str("Sorry, No Flights available. Try another day.")
    elif(userText == "yes"):
        return ("Your flight has been booked. Have a safe journey.")
    elif(userText == "no"):
        return ("Thankyou for using travelbot.")
    else:
        return str("Sorry, I did not understand")





if __name__ == "__main__":
    app.run()
