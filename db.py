from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["AgriExportDB"]

products_col = db["products"]
markets_col = db["markets"]
logistics_col = db["logistics"]