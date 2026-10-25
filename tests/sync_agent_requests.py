import time

import requests

CHATBOT_URL = "http://localhost:8000/hospital-rag-agent"

questions = [
    "What is the current wait time at wallace-hamilton hospital?",
    "Which hospital has the shortest wait time?",
    "At which hospitals are patients complaining about billing and insurance issues?",  # E501
    "What is the average duration in days for emergency visits?",
    "What are patients saying about the nursing staff at Castaneda-Hardy?",
    "What was the total billing amount charged to each payer for 2023?",
    "What is the average billing amount for medicaid visits?",
    "How many patients has Dr. Ryan Brown treated?",
    "Which physician has the lowest average visit duration in days?",
    "How many visits are open and what is their average duration in days?",
    "Have any patients complained about noise?",
    "How much was billed for patient 789's stay?",
    "Which physician has billed the most to cigna?",
    "Which state had the largest percent increase in medicaid visits from 2022 to 2023?",  # E501
]

request_bodies = [{"text": q} for q in questions]

start_time = time.perf_counter()
outputs = []

for question in questions:
    response = requests.post(
        CHATBOT_URL,
        json={"text": question},
        timeout=300,
    )

    print(f"\nQuestion: {question}")
    print(f"HTTP status: {response.status_code}")
    print(f"Response: {response.text[:1000]}")

    outputs.append(response)

end_time = time.perf_counter()
print(f"\nRun time: {end_time - start_time:.2f} seconds")
print(f"Successful responses: {sum(r.is_success for r in outputs)}/{len(outputs)}")
