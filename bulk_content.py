import os

report_path = 'documentation/Detailed_Project_Report.md'
with open(report_path, 'r', encoding='utf-8') as f:
    content = f.read()

code_appendix = '\n\n## CHAPTER 6.4: FULL SOURCE CODE LISTING\n'
dirs = ['backend', 'worker', 'frontend/src/app']

for d in dirs:
    if not os.path.exists(d):
        continue
    for root, _, files in os.walk(d):
        for file in files:
            if (file.endswith('.py') or file.endswith('.ts') or file.endswith('.html')) and '__' not in file and 'node_modules' not in root:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as code_f:
                        code_appendix += f'\n### FILE: {file_path}\n```text\n' + code_f.read() + '\n```\n'
                except:
                    pass

with open(report_path, 'w', encoding='utf-8') as f:
    f.write(content + code_appendix)

print("Bulk content added successfully.")
