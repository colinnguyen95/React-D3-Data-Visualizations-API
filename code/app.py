"""
Team Project: Web Application --> Data Dashbord 

Libraries Used: Pandas (data manipulation), SQlite (database), CSV (read data), 
                Flask (python web framework)

Team Functions: We all used pandas for data manipulation
    Colin Nguyen: Sign In / Register functions using SQL queries+ frontend 
    Finn Pardon: Top 5 and Lowest 5 Profitable Products 
    Antoinette Loya: Profit by Month / Profit by Segment
    Richard De La Rosa: Sales by State / Helped with and learned from everyone's functions

Note: There might be trouble running these functions without 
        installing required dependencies of the project. A video explaining how 
        this app works will be included.

source venv/bin/activate
"""

from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse
import pandas as pd
#import numpy as np
import sqlite3

app = Flask(__name__)

df = pd.read_csv("SalesDataOrders.csv", index_col=0)
headers = list(df.columns.values)

date_headers = headers[1:3]

for head in headers[:16]:
    if head in date_headers:
        df[head] = pd.to_datetime(df[head])

@app.route("/")
def hello():        
    return 'Hello'

@app.route('/top5', methods=['GET', 'POST'])
def topprofit():
    # firstName = request.get_json().get('firstName')
    # D3Year = request.get_json().get('D3Year')
    orders_year = df.loc[df["Order Date"].dt.year == 2017] 
    # orders_year = df.loc[df["Order Date"].dt.year == D3Year] 
    prod_prof_col = orders_year[["Product Name", "Profit"]]
    prod_prof = prod_prof_col.groupby(by="Product Name").sum().sort_values(by="Profit", ascending=False).reset_index()
    prod_prof['Profit'] = prod_prof['Profit'].round(2)
    top10 = prod_prof.head(5)
    return top10.to_json(orient='records')

@app.route('/lowest5', methods=['GET'])
def lowestprofit():
    orders_year = df.loc[df["Order Date"].dt.year == 2017] 
    prod_prof_col = orders_year[["Product Name", "Profit"]]
    prod_prof = prod_prof_col.groupby(by="Product Name").sum().sort_values(by="Profit", ascending=False).reset_index()
    prod_prof['Profit'] = prod_prof['Profit'].round(2)
    lowest10 = prod_prof.tail(5)
    return lowest10.to_json(orient='records')

@app.route('/salesByMonth', methods=['GET'])
def salesByMonth():
    dataByYear = df.loc[df['Order Date'].dt.year == 2017]
    dataByYear['Order Date'] = dataByYear['Order Date'].dt.month
    dataByYear['Sales'] = dataByYear['Sales'].round(decimals=2)
    sales_month_col = dataByYear[['Order Date', 'Sales']]
    salesByState = sales_month_col.groupby(['Order Date']).sum().sort_values(by=['Order Date'], ascending=True).reset_index()
    return salesByState.to_json(orient='records')
    
@app.route("/profitpercategory", methods=['GET'])
def ProfitPerCategory():
    df['Profit'] = df['Profit'].round(2)
    seg_pro_col = df[['Segment', 'Profit']]
    segment_profits = seg_pro_col.groupby(["Segment"]).sum().sort_values(by=['Profit']).reset_index()
    segment_profits['Profit'] = segment_profits['Profit'].round(2)
    return segment_profits.to_json(orient='records')

@app.route("/salesByState", methods=['GET'])
def SalesByState():
    df['Sales'] = df['Sales'].round(decimals=2)
    state_sal_col = df[['State', 'Sales']]
    salesByState = state_sal_col.groupby(['State']).sum().sort_values(by=['Sales'], ascending=False)
    return salesByState.reset_index().to_json(orient='records')


@app.route('/signin', methods=['GET', 'POST'])
def SignIn():
    if request.method == 'POST':
        email = request.get_json().get('email')
        password = request.get_json().get('password')
        with sqlite3.connect("OS_Employee.db") as db:
            cursor = db.cursor()
        find_Employee = ("SELECT * FROM Employee WHERE Email = ? AND Password = ?")
        cursor.execute(find_Employee,[(email),(password)])
        results = cursor.fetchone()
        
        if results:
            find_EmployeeName = ("SELECT FirstName FROM Employee WHERE Email = ? AND Password = ?")
            cursor.execute(find_EmployeeName,[(email),(password)])
            firstName = cursor.fetchone()
            return jsonify(name=firstName[0]), 200
        else:
            return jsonify('error logging in'), 400

@app.route('/register', methods=['GET', 'POST'])
def Register():
    if request.method == 'POST':
        firstName = request.get_json().get('firstName')
        lastName = request.get_json().get('lastName')
        employeeID = request.get_json().get('employeeID')
        email = request.get_json().get('email')
        password = request.get_json().get('password')
        
        insertData = '''INSERT INTO Employee(EmployeeID, FirstName, LastName, Email, Password) VALUES 
        (?,?,?,?,?)'''
        with sqlite3.connect("OS_Employee.db") as db:
            cursor = db.cursor()
        cursor.execute(insertData,[(employeeID),(firstName),(lastName),(email),(password)])
        db.commit()

if __name__ == "__main__":
    app.run(debug=True)