from pymongo import MongoClient


class ConnectMongo:
    def __init__(self, db_name):
        try:
            self.conn = MongoClient()
            print("Connected successfully!!!")
        except ConnectionAbortedError:
            print("Could not connect to MongoDB")

        self.db = self.conn[db_name]

    def insert_data(self, collection_name, data_list):
        collection = self.db[collection_name]
        try:
            x = collection.insert_many(data_list)
            print("inserted into collection {} - {} documents".format(collection_name, len(x.inserted_ids)))
        except BrokenPipeError:
            print("insert_many into collection {} - failed".format(collection_name))

    def delete_data(self, collection_name, data_list):
        collection = self.db[collection_name]
        delete_count = 0
        for data in data_list:
            try:
                collection.delete_one(data)
            except BrokenPipeError:
                print("delete on collection {} - failed for {}".format(collection_name, data))
                print("collection {} - deleted {} documents".format(collection_name, delete_count))
            delete_count += 1
        print("collection {} - deleted {} documents".format(collection_name, delete_count))

    def delete_all_data(self, collection_name):
        collection = self.db[collection_name]
        try:
            x = collection.delete_many({})
            print("collection {} - deleted {} documents".format(collection_name, x.deleted_count))
        except BrokenPipeError:
            print("delete_many into collection {} - failed".format(collection_name))


if __name__ == "__main__":
    connect_db = ConnectMongo(db_name='cricketDB')
    mylist = [
        {"name": "Amy", "address": "Apple st 652"},
        {"name": "Hannah", "address": "Mountain 21"},
        {"name": "Michael", "address": "Valley 345"},
        {"name": "Sandy", "address": "Ocean blvd 2"},
        {"name": "Betty", "address": "Green Grass 1"},
        {"name": "Richard", "address": "Sky st 331"},
        {"name": "Susan", "address": "One way 98"},
        {"name": "Vicky", "address": "Yellow Garden 2"},
        {"name": "Ben", "address": "Park Lane 38"},
        {"name": "William", "address": "Central st 954"},
        {"name": "Chuck", "address": "Main Road 989"},
        {"name": "Viola", "address": "Sideway 1633"}
    ]
    connect_db.insert_data('tournament', mylist)
    connect_db.delete_data('tournament', mylist)
    connect_db.insert_data('tournament', mylist)
    connect_db.delete_all_data('tournament')