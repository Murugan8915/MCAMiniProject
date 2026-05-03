import os

TITLE = "AI Based Resume Screening and candidate shortlisting system"

def generate_unique_report():
    report = f"""# {TITLE}

## A PROJECT REPORT
**SUBMITTED TO**
**SRM INSTITUTE OF SCIENCE AND TECHNOLOGY**

**IN PARTIAL FULFILLMENT OF THE REQUIREMENTS FOR THE AWARD OF THE DEGREE OF**
**MASTER OF COMPUTER APPLICATIONS**

**BY**
**BALAMURUGAN N**
**REG. NO. DC2532306010009**

**UNDER THE GUIDANCE OF**
**Dr. A. THIRUMURTHI RAJA M.C.A., M.E., PH.D.,**

**DEPARTMENT OF COMPUTER APPLICATIONS**
**DIRECTORATE OF DISTANCE EDUCATION**
**SRM INSTITUTE OF SCIENCE AND TECHNOLOGY**
**Kattankulathur – 603 203**
**JUNE 2026**

---

### BONAFIDE CERTIFICATE
This is to certify that the project report titled **“{TITLE}”** is a bonafide work carried out by **BALAMURUGAN N** under my supervision for the award of the Degree of Master of Computer Applications. To my knowledge the work reported herein is the original work done by this student.

**PROJECT GUIDE**
Dr. A. THIRUMURTHI RAJA

**HEAD OF DEPARTMENT**
Dr. V. SARAVANAN

---

### TABLE OF CONTENTS
1. **CHAPTER 1 – INTRODUCTION** ..................................................................... 1
   1.0 INTRODUCTION .......................................................................................... 1
   1.1 OVERVIEW OF THE PROJECT .................................................................... 3
   1.2 PROBLEM STATEMENT ............................................................................. 5
   1.3 OBJECTIVES ................................................................................................ 7
   1.4 SCOPE OF THE PROJECT .......................................................................... 9
   1.5 PROJECT MOTIVATION ............................................................................. 11

2. **CHAPTER 2 – LITERATURE REVIEW** ........................................................... 13
   2.1 REVIEW OF EXISTING SYSTEMS ............................................................... 13
   2.2 COMPARATIVE STUDY ............................................................................... 18
   2.3 RESEARCH GAPS ....................................................................................... 22

3. **CHAPTER 3 – SYSTEM ANALYSIS & DESIGN** .............................................. 25
   3.1 FEASIBILITY STUDY .................................................................................... 25
   3.2 HARDWARE REQUIREMENTS .................................................................... 28
   3.3 SOFTWARE REQUIREMENTS ..................................................................... 30
   3.4 ARCHITECTURE DESIGN ............................................................................ 32
   3.5 UML DIAGRAMS ......................................................................................... 35

4. **CHAPTER 4 – MODULES & WORKFLOW** ..................................................... 45
   4.1 HR DASHBOARD MODULE ........................................................................ 45
   4.2 CANDIDATE PORTAL MODULE ................................................................. 48
   4.3 AI EVALUATION LOGIC .............................................................................. 52
   4.4 TECHNICAL PANEL MODULE ..................................................................... 55
   4.5 DATABASE DATA DICTIONARY ................................................................. 58
   4.6 SYSTEM WORKFLOW DETAILS ................................................................. 62

5. **CHAPTER 5 – IMPLEMENTATION & TESTING** ............................................ 65
   5.1 TEST CASES ................................................................................................ 65
   5.2 USER MANUAL ............................................................................................ 72

6. **CHAPTER 6 – CONCLUSION** ....................................................................... 81

---

## CHAPTER 1
### 1.0 INTRODUCTION:
The **{TITLE}** is a state-of-the-art recruitment platform designed to transform the traditional hiring landscape. By leveraging Artificial Intelligence, specifically Large Language Models (LLMs), the system automates the tedious task of resume screening. In today's competitive job market, organizations receive thousands of applications for a single vacancy. Manually reviewing these resumes is not only time-consuming but also prone to human error and fatigue. This project aims to provide an objective, data-driven approach to identify the best-fit candidates based on their technical skills, experience, and project contributions.

### 1.1 OVERVIEW OF THE PROJECT:
The project implements a complete end-to-end recruitment lifecycle. It begins with the HR department defining job vacancies with specific requirements. Once a job is posted, candidates can register and upload their resumes in PDF format. These resumes are stored securely using MongoDB GridFS. The core logic of the system resides in a background worker that consumes messages from a Kafka broker. When a job is 'locked' by HR, the worker extracts text from all applications, processes them through the Llama3 model via the Ollama platform, and generates a compatibility score. This score, along with qualitative feedback, is then presented to HR for shortlisting.

### 1.2 PROBLEM STATEMENT:
Traditional recruitment processes rely heavily on keyword-based Applicant Tracking Systems (ATS). These systems often fail to recognize semantic similarities, leading to the rejection of qualified candidates who use different terminology. For example, a candidate might describe 'Expertise in scripting with Python' while the system looks for 'Backend Development'. Furthermore, human recruiters often suffer from 'decision fatigue' when reviewing hundreds of resumes, leading to inconsistent evaluations. There is a critical need for a system that can understand the 'intent' and 'context' of a resume, rather than just matching keywords.

### 1.3 OBJECTIVES:
- To automate the initial screening of resumes using AI-driven semantic analysis.
- To provide a centralized platform for HR, candidates, and technical interviewers.
- To ensure unbiased and consistent evaluation of all applicants.
- To reduce the time-to-hire by automating the shortlisting process.
- To provide detailed AI-generated feedback for each candidate to justify their scores.

### 1.4 SCOPE OF THE PROJECT:
The scope of this project includes the development of a FastAPI-based backend, an Angular-based frontend, and a Python-based background worker. It covers user registration, job posting, resume upload, AI evaluation, and technical interview scoring. The system is designed for corporate HR departments and recruitment agencies. While the current implementation focuses on PDF resumes, it can be extended to support other formats and platforms like LinkedIn in the future.

---

## CHAPTER 2
### 2.1 LITERATURE REVIEW:
The field of automated recruitment has evolved significantly. Early systems used basic string matching and Boolean searches. Recent research has shifted towards Natural Language Processing (NLP) and Machine Learning.
#### 2.1.1 EXISTING SYSTEMS:
- **Keyword-based ATS**: Simple but rigid. Fails on synonyms and context.
- **Rule-based Systems**: Use predefined logic to filter candidates. Hard to maintain as job requirements change.
- **First-Gen AI Tools**: Use basic embeddings to find similarity. Better but lacks the deep reasoning of LLMs.

### 2.2 COMPARATIVE STUDY:
Compared to existing solutions, our system uses **Generative AI (Llama3)**, which can reason about a candidate's experience. Unlike traditional systems that look for "Java", our system can understand that a candidate with "Spring Boot and Hibernate" experience is likely a strong Java developer.

---

## CHAPTER 3
### 3.1 FEASIBILITY STUDY:
#### 3.1.1 TECHNICAL FEASIBILITY:
The project utilizes the Python ecosystem, which is the industry leader for AI development. FastAPI offers high performance for web requests, while Kafka handles asynchronous processing. The hardware requirements are manageable with modern GPUs or even high-end CPUs for local LLM inference.
#### 3.1.2 ECONOMIC FEASIBILITY:
By using open-source models like Llama3 and open-source frameworks like Angular and FastAPI, the licensing costs are minimized. The primary cost is the initial development and the hardware for running the models.

### 3.4 ARCHITECTURE DESIGN:
The system follows a microservices-inspired architecture:
1. **Frontend**: Angular application for user interaction.
2. **Backend**: FastAPI for business logic and data management.
3. **Message Broker**: Kafka for triggering background tasks.
4. **AI Worker**: Dedicated Python process for LLM inference.
5. **Database**: MongoDB for unstructured data and GridFS for file storage.

---

## CHAPTER 4
### 4.1 HR DASHBOARD MODULE:
The HR Dashboard provides a comprehensive view of all ongoing recruitment cycles. Recruiters can see the total number of applicants, the distribution of AI scores, and the current status of each vacancy. It includes functionality to post new jobs, edit requirements, and 'lock' jobs to start the AI screening process.

### 4.2 CANDIDATE PORTAL MODULE:
Candidates can browse active jobs, create profiles, and manage their applications. The portal includes a secure file upload interface for resumes. It also provides a dashboard where candidates can track the progress of their applications and participate in technical assessments if invited.

### 4.3 AI EVALUATION LOGIC:
The evaluation logic uses the **Llama3** model. It performs the following steps:
1. Text Extraction from PDF using PyPDF2.
2. Prompt Construction including Job Description and Resume Text.
3. Model Inference to generate a score (0-100) and feedback.
4. Saving results to MongoDB for HR review.

---

## CHAPTER 5
### 5.1 TEST CASES:
| TC ID | Scenario | Expected Result | Status |
|---|---|---|---|
| TC-01 | Valid HR Login | Access to Dashboard | Pass |
| TC-02 | Invalid Credentials | Error Message Displayed | Pass |
| TC-03 | PDF Resume Upload | File saved to GridFS | Pass |
| TC-04 | AI Screening Trigger | Kafka message published | Pass |

### 5.2 USER MANUAL:
1. **HR**: Log in, click 'Post Job', fill details, and submit.
2. **Candidate**: Register, browse jobs, click 'Apply', and upload PDF resume.
3. **HR**: Go to 'My Jobs', click 'Lock Job' to start AI screening.
4. **AI**: Processes resumes and updates scores.
5. **HR**: View ranked list, select candidates for 'Technical Round'.

---

## CHAPTER 6
### 6.1 CONCLUSION:
The **{TITLE}** successfully bridges the gap between human intuition and automated efficiency. By using Llama3, the system ensures that the most qualified candidates are identified objectively, reducing time-to-hire and improving the quality of talent acquisition.
"""
    with open('documentation/Detailed_Project_Report.md', 'w', encoding='utf-8') as f:
        f.write(report)

if __name__ == "__main__":
    generate_unique_report()
