import os
import json
import time
from confluent_kafka import Consumer, KafkaError
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
import asyncio
from bson import ObjectId
import io
from resume_parser import extract_text_from_pdf, extract_entities, calculate_score
from ai_evaluation import generate_ai_summary
from email_utils import send_shortlisted_email, send_rejected_email
from notifications import notify_shortlisted, notify_rejected, notify_selected

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")

client = AsyncIOMotorClient(MONGODB_URL)
db = client.recruitment_db
fs = AsyncIOMotorGridFSBucket(db)

async def check_and_shortlist(job_id, db):
    try:
        job_oid = ObjectId(job_id)
    except:
        print(f"❌ Invalid job_id format: {job_id}")
        return

    job = await db["jobs"].find_one({"_id": job_oid})
    if not job:
        return

    # Check if all applications for this job have been processed (Scored or Error)
    pending_count = await db["applications"].count_documents({
        "job_id": job_id,
        "status": {"$in": ["Applied", "AI_Shortlisting"]}
    })
    
    if pending_count == 0:
        print(f"All applications for job {job_id} processed. Running shortlisting...")
        try:
            vacancies = int(job.get("vacancies", 1))
        except:
            vacancies = 1
        shortlist_count = vacancies * 2
        
        # We only shortlist from those successfully scored
        all_scored_apps = await db["applications"].find({
            "job_id": job_id, 
            "status": "AI_Scored"
        }).sort("ai_score", -1).to_list(1000)
        
        for app in all_scored_apps[:shortlist_count]:
            await db["applications"].update_one(
                {"_id": app["_id"]},
                {"$set": {"status": "Shortlisted"}}
            )
            print(f"Candidate {app.get('candidate_email')} marked as Shortlisted")
            send_shortlisted_email(
                app.get('candidate_email'), 
                app.get('candidate_name', 'Candidate'), 
                job.get('title', 'Position')
            )
            
        for app in all_scored_apps[shortlist_count:]:
            await db["applications"].update_one(
                {"_id": app["_id"]},
                {"$set": {"status": "Rejected"}}
            )
            print(f"Candidate {app.get('candidate_email')} marked as Rejected")
            send_rejected_email(
                app.get('candidate_email'), 
                app.get('candidate_name', 'Candidate'), 
                job.get('title', 'Position')
            )
        
        # Optionally mark failed ones as Rejected as well
        failed_apps = await db["applications"].find({"job_id": job_id, "status": "AI_Error"}).to_list(1000)
        for app in failed_apps:
            await db["applications"].update_one(
                {"_id": app["_id"]},
                {"$set": {"status": "Rejected"}}
            )
            send_rejected_email(
                app.get('candidate_email'), 
                app.get('candidate_name', 'Candidate'), 
                job.get('title', 'Position')
            )

async def process_resume(application_id, job_id, resume_file_id, candidate_email):
    print(f"Processing resume for application {application_id} (GridFS ID: {resume_file_id})")
    
    try:
        job_oid = ObjectId(job_id)
    except:
        print(f"❌ Invalid job_id format: {job_id}")
        return

    await db["applications"].update_one(
        {"_id": ObjectId(application_id)},
        {"$set": {"status": "AI_Shortlisting"}}
    )
    
    job = await db["jobs"].find_one({"_id": job_oid})
    required_skills = job.get("required_skills", []) if job else []
    
    # Download from GridFS
    grid_out = await fs.open_download_stream(ObjectId(resume_file_id))
    resume_data = await grid_out.read()
    
    # pdfminer.six can work with file-like objects
    resume_io = io.BytesIO(resume_data)
    text = extract_text_from_pdf(resume_io)
    
    print(f"\n--- Starting AI Processing for Application {application_id} ---")
    print(f"1. Extracting text from PDF (GridFS ID: {resume_file_id})...")
    if not text:
        print(f"❌ Failed to extract text from resume {resume_file_id}")
        await db["applications"].update_one(
            {"_id": ObjectId(application_id)},
            {"$set": {"status": "AI_Error"}}
        )
        await check_and_shortlist(job_id, db)
        return
    print(f"✅ Text extracted successfully. Extracted length: {len(text)} characters.")
    print(f"--- Extracted Text Snippet ---\n{text[:200]}...\n-----------------------------")

    print(f"2. Extracting entities (potential skills, contact info) from text...")
    extracted_data = extract_entities(text)
    print(f"✅ Extracted Skills: {extracted_data.get('potential_skills', [])}")
    print(f"✅ Extracted Info: Name: {extracted_data.get('candidate_name')}, Email: {extracted_data.get('candidate_email')}, Mobile: {extracted_data.get('candidate_mobile')}")
    
    print(f"3. Calculating score against required skills: {required_skills}")
    score = calculate_score(extracted_data["potential_skills"], required_skills)
    print(f"✅ Calculated Match Score: {score}%")
    
    print(f"4. Generating AI summary/feedback for {candidate_email}...")
    ai_feedback = generate_ai_summary(text, job.get("description", ""))
    print(f"✅ Generated Feedback: {ai_feedback}")
    print(f"--- Finished AI Processing for Application {application_id} ---\n")
    
    # Update application with score and feedback only
    # We DO NOT override candidate_name, candidate_mobile, or candidate_email from the PDF.
    # The application will strictly use the credentials provided at login.
    update_fields = {
        "status": "AI_Scored", 
        "ai_score": score,
        "ai_feedback": ai_feedback
    }

    # 1. Update the application document
    await db["applications"].update_one(
        {"_id": ObjectId(application_id)},
        {"$set": update_fields} 
    )

    # 2. Check if we should trigger shortlisting
    await check_and_shortlist(job_id, db)

async def handle_status_update(data):
    status = data.get("new_status")
    email = data.get("candidate_email")
    name = data.get("candidate_name", "Candidate")
    job_title = data.get("job_title", "Position")

    print(f"Processing status update for {email}: {status}")

    if status in ["Rejected", "Technical Rejected"]:
        notify_rejected(email, job_title)
        print(f"✅ Rejection email sent to {email} for {job_title}")
    elif status == "Shortlisted":
        notify_shortlisted(email, job_title)
        print(f"✅ Shortlist email sent to {email} for {job_title}")
    elif status == "Selected":
        notify_selected(email, job_title)
        print(f"✅ Selection email sent to {email} for {job_title}")
    # You can add more status triggers here (e.g., Selected, Interview Scheduled)

def create_consumer_with_retry(broker, max_retries=15, delay=5):
    """Create a Kafka consumer, retrying until Kafka is ready."""
    for attempt in range(1, max_retries + 1):
        try:
            consumer = Consumer({
                'bootstrap.servers': broker,
                'group.id': 'resume-processing-group',
                'auto.offset.reset': 'earliest',
                'socket.timeout.ms': 6000,
                'session.timeout.ms': 10000,
            })
            # Test connectivity by listing topics (raises if Kafka not ready)
            consumer.list_topics(timeout=5)
            print(f"✅ Kafka connected on attempt {attempt}.")
            return consumer
        except Exception as e:
            print(f"⏳ Kafka not ready (attempt {attempt}/{max_retries}): {e}. Retrying in {delay}s...")
            time.sleep(delay)
    raise RuntimeError("❌ Could not connect to Kafka after multiple retries.")

def start_worker():
    print(f"Starting AI Resume Screening Worker on broker {KAFKA_BROKER}...")
    
    consumer = create_consumer_with_retry(KAFKA_BROKER)
    consumer.subscribe(['resume-processing', 'application_status'])
    loop = asyncio.get_event_loop()

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(msg.error())
                    time.sleep(2)
                    continue
            
            topic = msg.topic()
            value = json.loads(msg.value().decode('utf-8'))
            print(f"Received message on {topic}: {value}")
            
            if topic == 'resume-processing':
                loop.run_until_complete(
                    process_resume(
                        value['application_id'],
                        value['job_id'],
                        value['resume_file_id'],
                        value['candidate_email']
                    )
                )
            elif topic == 'application_status':
                loop.run_until_complete(handle_status_update(value))
            
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Worker Error: {e}")
    finally:
        consumer.close()

if __name__ == "__main__":
    start_worker()

