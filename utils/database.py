from pymongo import MongoClient

from utils.config import MONGODB_URI, DATABASE, REQUESTS_COLLECTION


client = MongoClient(MONGODB_URI)
database = client[DATABASE]

requests_collection = database[REQUESTS_COLLECTION]
