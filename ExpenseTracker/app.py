from flask import Flask, request, jsonify     
from uuid import uuid1, uuid4          # to create unique identifier strings
import os, json, pytz                   # pytz provides timezone
from datetime import date, datetime
import pandas as pd

# create a json file => a give it a basic structures
db = {}
db_filename = "db.json"

# check whether db.json exists in the directory or not => for that use os package
if os.path.exists(db_filename): # if it exists then we load the json file
    print("DB Exists")
    with open(db_filename, 'r') as f:
        db = json.load(f)
else:
    print("DB Does Not Exists")
    accessKey = str(uuid1()) #generate a unique id and typecast to string
    secretKey = str(uuid4())

    item_types = [
        "Food", "beverages", "Clothing", "Stationaries", "Wearable", "Electronic Accessories"
    ]

    # create the db.json file to be stored
    db = {
        "accessKey" : accessKey,
        "secretKey" : secretKey,
        "item_type" : item_types,
        "users": []
    }

    # create the json file where db.json is to be dumped
    with open (db_filename, "w+") as f:
        json.dump(db, f, indent=4)

# whatever file operations we need to do => do it before calling the API object => increases the efficiency of the code
app = Flask(__name__)

# User sign up
@app.route('/signup', methods = ['POST']) # it's good practise to mention the method
#define a function without the same name
def signup():
    if request.method == 'POST':

        name = request.form['name'] # accessing the form data => and accessing "name" of form data as a key
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']

        userDict = {
            "name": name,
            "email": email,
            "password": password,
            "username": username,
            "purchases": {}
        }
        email_list = []
        for element in db["users"]:
            email_list.append(element["email"])


        if len(db["users"]) == 0 or userDict["email"] not in email_list:
            # then this is a new user
            db["users"].append(userDict)
            with open(db_filename, "r+") as f:
                f.seek(0)   
                json.dump(db, f, indent=4)
            
            return "User added successfully"
        else:
            return "user already exists"
    return "Error: Trying to access endpoint with wrong method"

@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    for user in db["users"]:
        if user["email"] == email and user ["password"] == password:
            user_idx = db ["users"].index(user)

            response = {
                "message": "logged in successfully",
                "user_index": user_idx
            }
            return response
        else:
            continue
    return "Wrong email or password!! Please try again"

#Add purchase
@app.route("/add_purchase", methods= ['POST'])
def add_purchase():
    if request.method == 'POST':
        user_idx = int (request.form["user_index"])
        item_name= request.form["item_name"]
        item_type= request.form["item_type"]
        item_price= request.form["item_price"]

        curr_date= str(date.today())
        curr_time= str(datetime.now(pytz.timezone("Asia/Kolkata")))

    itemDict={
        "item_name": item_name,
        "item_type": item_type,
        "item_price": item_price,
        "purchase_time": curr_time
    }

    existing_dates= list(db["users"][user_idx]["purchases"].keys())
    print(existing_dates)

    if len(db["users"][user_idx]["purchases"]) ==0:
        db["users"][user_idx]["purchases"][curr_date]=[]
        db["users"][user_idx]["purchases"][curr_date].append(itemDict)
        with open(db_filename, "r+") as f:
            f.seek(0)
            json.dump(db, f, indent=4)
        return "user added successfully"
    else:
        db["users"][user_idx]["purchases"][curr_date].append(itemDict)
        with open(db_filename, "r+") as f:
            f.seek(0)
            json.dump(db, f, indent=4)
        return "Item added successfully"
    #return "Some error uccured!! unable to add item"

    # purchase_dates= list(db["users"][user_idx]["purchases"].keys())

    # if curr_date in purchase_dates:
    #     db["users"][user_idx]["purchases"][curr_date].append(itemDict)
    #     return "Item added successfully"

@app.route("/get_all_purcheses_for_today", methods=["GET"])
def get_all_purcheses_for_today():
    user_idx = int(request.args["user_index"])
    print("user Index = ", user_idx)

    curr_date= str(date.today())

    list_of_purchases= db["users"][user_idx]["purchases"][curr_date]

    purchasedates= list(db["users"][user_idx]["purchases"].keys())
    if curr_date in purchasedates:
        return jsonify(purchases_for_today=list_of_purchases)
    else:
        return jsonify(message="Data Not found")

    #return jsonify(purchases_for_today=list_of_purchases)

@app.route("/get_purchases", methods=["GET"])
def get_purchases():
    data = request.json
    user_index= data["user_index"]
    start_date= data["start_date"]
    end_date= data["end_date"]

    dates= pd.date_range(start_date, end_date)

    dates_in_db= list(db["users"][user_index]["purchases"].keys())

    purchaseDict= {}
    for dt in dates_in_db:
        if dt in dates:
            purchaseDict[dt] = db["users"][user_index]["purchases"][dt]
        else:
            continue
    return purchaseDict

if __name__ == "__main__":
    app.run(host='0.0.0.0', port="5000", debug=True)