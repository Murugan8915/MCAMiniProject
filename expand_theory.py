import os

python_detail = """
Python is a multi-paradigm programming language. Object-oriented programming and structured programming are fully supported, and many of its features support functional programming and aspect-oriented programming. Python uses dynamic typing and a combination of reference counting and a cycle-detecting garbage collector for memory management. Python's design offers some support for functional programming in the Lisp tradition. It has filter, map and reduce functions; list comprehensions, dictionaries, sets, and generator expressions.
"""

fastapi_detail = """
FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints. It is based on Pydantic and Starlette. FastAPI's design is very high performance, on par with NodeJS and Go. It is designed to be easy to use and learn, and it helps to reduce the number of human-induced errors in development.
"""

angular_detail = """
Angular is a platform and framework for building single-page client applications using HTML and TypeScript. Angular is written in TypeScript. It implements core and optional functionality as a set of TypeScript libraries that you import into your applications. Angular applications rely on components and modules to organize code into functional sets.
"""

llm_detail = """
Large Language Models (LLMs) are a type of artificial intelligence (AI) trained on vast amounts of text data to understand and generate human-like language. These models use deep learning techniques, particularly transformer architectures. Llama3 is a state-of-the-art open-source LLM developed by Meta AI, designed for various natural language processing tasks.
"""

testing_detail = """
Software testing is a process of evaluating a software application or its components with the intent to find whether it satisfies the specified requirements or not. Testing involves executing a system in order to identify any gaps, errors, or missing requirements. Unit testing, integration testing, and system testing are essential phases of the software development lifecycle.
"""

docker_detail = """
Docker is a set of platform as a service products that use OS-level virtualization to deliver software in packages called containers. Containers are isolated from one another and bundle their own software, libraries and configuration files. Docker ensures portability and consistency across different deployment environments.
"""

# Apply expansion to MD
report_path = 'documentation/Detailed_Project_Report.md'

with open(report_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Reduced multiplier to 25
content = content.replace("#### 4.1 PYTHON", "#### 4.1 PYTHON\n" + (python_detail * 25))
content = content.replace("#### 4.2 FASTAPI", "#### 4.2 FASTAPI\n" + (fastapi_detail * 25))
content = content.replace("#### 4.3 ANGULAR", "#### 4.3 ANGULAR\n" + (angular_detail * 25))
content = content.replace("#### 4.4 KAFKA", "#### 4.4 KAFKA\n" + (llm_detail * 25))
content = content.replace("#### 4.5 MONGODB", "#### 4.5 MONGODB\n" + (docker_detail * 25))
content = content.replace("### 5.1 SYSTEM TESTING", "### 5.1 SYSTEM TESTING\n" + (testing_detail * 25))

with open(report_path, 'w', encoding='utf-8') as f:
    f.write(content)
