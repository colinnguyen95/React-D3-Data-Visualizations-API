from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse
import pandas as pd
import sqlite3

app = Flask(__name__)

conn = sqlite3.connect('OS_Employee.db')

df = pd.read_csv("SalesDataOrders.csv", index_col=0)
headers = list(df.columns.values)

date_headers = headers[1:3]

for head in headers[:16]:
    if head in date_headers:
        df[head] = pd.to_datetime(df[head])

@app.route("/")
def hello():        
    return 'Hello'

@app.route("/wat")
def wat():        
    ordersData = df.loc[df["Order Date"].dt.year == 2014]
    orders = ordersData.head(3).reset_index()
    return orders.to_json(orient='records')

@app.route('/top10', methods=['GET'])
def topprofit():
    orders_year = df.loc[df["Order Date"].dt.year == 2014] 
    prod_prof_col = orders_year[["Product Name", "Profit"]]
    prod_prof = prod_prof_col.groupby(by="Product Name").sum().sort_values(by="Profit", ascending=False).reset_index()
    top10 = prod_prof.head(15)
    return top10.to_json(orient='records')

@app.route('/profitByMonth', methods=['GET'])
def profitByMonth():
    dataByYear = df.loc[df['Order Date'].dt.year == 2017]
    dataByYear['Order Date'] = dataByYear['Order Date'].dt.month
    dataByYear['Sales'] = dataByYear['Sales'].round(decimals=2)
    sales_month_col = dataByYear[['Order Date', 'Sales']]
    salesByState = sales_month_col.groupby(['Order Date']).sum().sort_values(by=['Order Date'], ascending=True).reset_index()
    return salesByState.to_json(orient='records')
    
@app.route("/profitpersegment")
def ProfitPerSegment():
    df['Profit'] = df['Profit'].round(2)
    seg_pro_col = df[['Segment', 'Profit']]
    segment_profits = seg_pro_col.groupby(["Segment"]).sum().sort_values(by=['Profit']).reset_index()
    return segment_profits.to_json(orient='records')

@app.route('/signin', methods=['GET', 'POST'])
def SignIn():
    if request.method == 'POST':
        email = request.get_json().get('email')
        password = request.get_json().get('password')
        with sqlite3.connect("OS_Employee.db") as db:
            cursor = db.cursor()
        find_Employee = ("SELECT * FROM Employee WHERE Email = ? AND Password = ?")
        cursor.execute(find_Employee,[(email),(password)])
        results = cursor.fetchall()
        
        if results:
            return jsonify('success')  
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