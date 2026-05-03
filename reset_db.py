from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client.recruitment_db

print("Resetting jobs to Active...")
db.jobs.update_many({}, {"$set": {"status": "Active"}})

print("Resetting applications to Applied and clearing AI scores...")
db.applications.update_many({}, {
    "$set": {"status": "Applied"},
    "$unset": {"ai_score": "", "ai_feedback": ""}
})

print("DB Reset complete.")
client.close()
