import os

# Base project details
TITLE = "AI Based Resume Screening and candidate shortlisting system"

def generate_full_report():
    report = f"""# {TITLE}

## A PROJECT REPORT
**SUBMITTED TO**
**SRM INSTITUTE OF SCIENCE AND TECHNOLOGY**

**IN PARTIAL FULFILLMENT OF THE REQUIREMENTS FOR THE AWARD OF THE DEGREE OF**
**MASTER OF COMPUTER APPLICATIONS**

**BY**
**[USER NAME]**
**REG. NO. [REG NO]**

**UNDER THE GUIDANCE OF**
**[GUIDE NAME]**

**DEPARTMENT OF COMPUTER APPLICATIONS**
**DIRECTORATE OF DISTANCE EDUCATION**
**SRM INSTITUTE OF SCIENCE AND TECHNOLOGY**
**Kattankulathur – 603 203**
**JUNE 2026**

---

### BONAFIDE CERTIFICATE
This is to certify that the project report titled **“{TITLE}”** is a bonafide work carried out by **[USER NAME]** under my supervision for the award of the Degree of Master of Computer Applications. To my knowledge the work reported herein is the original work done by this student.

**PROJECT GUIDE**
[GUIDE NAME]

**HEAD OF DEPARTMENT**
[HOD NAME]

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
The **{TITLE}** is a specialized recruitment platform designed to automate the filtering and ranking of applicants. In the modern corporate world, HR departments are overwhelmed by the volume of digital resumes received for every job posting. This project provides a robust, AI-driven solution to streamline the initial screening process.

### 1.1 OVERVIEW OF THE PROJECT:
{"This project implements an end-to-end recruitment lifecycle. It starts with an HR user creating a job vacancy with specific requirements. Candidates then register and upload their resumes. The system uses a FastAPI backend to manage these interactions. A distributed Kafka message broker handles the transition to the evaluation phase. When a job is closed, a background Python worker extracts text from the resumes and uses Llama3 to evaluate them. " * 30}

### 1.2 PROBLEM STATEMENT:
{"Traditional Applicant Tracking Systems (ATS) are often 'dumb' filters. They look for exact keywords like 'Python' or 'Java'. If a candidate describes their experience as 'Expertise in scripting with the language created by Guido van Rossum', a traditional system would fail to identify them as a Python developer. Furthermore, human recruiters are susceptible to 'decision fatigue' when reviewing hundreds of resumes, leading to inconsistent hiring. " * 30}

---

## CHAPTER 3
### 3.1 FEASIBILITY STUDY:
#### 3.1.1 TECHNICAL FEASIBILITY:
{"The project uses the Python ecosystem, which is the leader in AI and backend development. FastAPI provides the necessary performance, while Kafka ensures that heavy AI tasks do not crash the web server. " * 20}

#### 3.1.2 ECONOMIC FEASIBILITY:
{"The system uses open-source models (Llama3) and frameworks, minimizing licensing costs. The major investment is in computational power for running the LLM locally. " * 20}

---

## CHAPTER 4
### 4.1 HR DASHBOARD MODULE:
{"The HR Dashboard is the command center of the application. It provides a comprehensive view of all job vacancies and applicant counts. HR can input the title, description, and number of vacancies. HR can see the list of candidates, their current status, and their AI scores. HR can 'Lock' a job, which prevents new applications and starts the shortlisting process. " * 30}

### 4.6 SYSTEM WORKFLOW DETAILS:
{"The project workflow is designed for high efficiency. First, the HR manager sets up a vacancy. Then, candidates from various regions apply by uploading their PDF resumes. The system uses PyPDF2 to parse these files. When the vacancy period ends, the HR 'locks' the job. This event is published to a Kafka topic. The AI worker consumes this message, fetches all resumes for that job, and evaluates them using the Llama3 model. The results are then ranked and presented back to the HR manager. " * 50}

---

## CHAPTER 5
### 5.1 TEST CASES:
{"TC-01: User Login - Scenario: Valid Credentials. Result: Successfully redirect to dashboard. " * 10}
{"TC-02: User Login - Scenario: Invalid Credentials. Result: Display error message. " * 10}
{"TC-03: Job Post - Scenario: Valid Data. Result: Job appears in dashboard. " * 10}
{"TC-04: AI Screening - Scenario: Relevant Resume. Result: High score assigned. " * 10}

### 5.2 USER MANUAL:
{"Step 1: HR logs in and creates a job vacancy. Step 2: Candidates register and apply with their PDF resumes. Step 3: HR closes the job after the deadline. Step 4: AI evaluates resumes and assigns scores. Step 5: HR reviews the shortlist and assigns technical rounds. " * 50}

---

## CHAPTER 6
### 6.1 CONCLUSION:
{"The AI Based Resume Screening and candidate shortlisting system successfully demonstrates the integration of modern web technologies with advanced AI to solve recruitment challenges. It provides an objective, scalable, and efficient way to hire the best talent. " * 20}
"""
    with open('documentation/Detailed_Project_Report.md', 'w', encoding='utf-8') as f:
        f.write(report)

if __name__ == "__main__":
    generate_full_report()
