from flask import Flask
from flask_restful import Resource, Api
import pandas as pd

app = Flask(__name__)
# api = Api(app)

df = pd.read_csv("SalesDataOrders.csv", index_col=0)
headers = list(df.columns.values)

date_headers = headers[1:3]

for head in headers[:16]:
    if head in date_headers:
        df[head] = pd.to_datetime(df[head])

@app.route("/")
def hello():        
    ordersData = df.loc[df["Order Date"].dt.year == 2014]
    orders = ordersData.head(3).reset_index()
    #return ordersData.head(3).to_html()
    return orders.to_json(orient='records')

@app.route("/top10")
def topprofit():
    orders_year = df.loc[df["Order Date"].dt.year == 2016] 
    
    # orders_month = orders_year.loc[orders_year["Order Date"].dt.month == 2]
    
    # prod_prof_col = orders_month[["Product Name", "Profit"]]
    prod_prof_col = orders_year[["Product Name", "Profit"]]
    
    prod_prof = prod_prof_col.groupby(by="Product Name").sum().sort_values(by="Profit", ascending=False).reset_index()
    
    #top10 = prod_prof.head(10)

    return prod_prof.to_json(orient='records')
    
    #print(prod_prof.tail(10))

@app.route("/profitpersegment")
def ProfitPerSegment():
    seg_pro_col = df[['Segment', 'Profit']]
    
    segment_profits = seg_pro_col.groupby(["Segment"]).sum().sort_values(by=['Profit']).reset_index()

    return segment_profits.to_json(orient='records')

# class Student(Resource):
#     def get(self, name):
#         return {'student': name}

# api.add_resource(Student, '/student/<string:name>')

#app.run(port=5000)

if __name__ == "__main__":
    app.run()