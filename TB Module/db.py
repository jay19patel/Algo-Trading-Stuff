import pymongo

def DbEstabilation():
    try:
        db_client = pymongo.MongoClient("mongodb+srv://justj:justj@cluster0.fsgzjrl.mongodb.net/")
        db_folder = db_client["LearningTest"]
        profileCollection = db_folder.get_collection("Profile")
        testCollection = db_folder.get_collection("Test")
        print("Database connection established successfully")
        return db_folder
    except Exception as e:
        print(f"Failed to establish database connection: {e}")
        return None, None

