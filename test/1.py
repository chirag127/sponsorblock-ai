# https://api-inference.huggingface.co/models/bigscience/bloom
# payload {"inputs":"This tool converts irregular verbs to past tense.\nArise - Arose\nBecome - Became\nForget - Forgot\nFreeze -","parameters":{"seed":74,"early_stopping":false,"length_penalty":0,"max_new_tokens":20,"do_sample":true,"top_p":0.9}}

import requests

api = "https://api-inference.huggingface.co/models/bigscience/bloom"

payload = {
    "inputs": """write Python code to Make a function to Parse the list of expenses and return the list of triples (date, value, currency).
    Ignore lines starting with #.
    Parse the date using datetime.
""",
    "parameters": {
        "seed": 74,
        "early_stopping": False,
        "length_penalty": 0,
        "max_new_tokens": 200,
        "do_sample": True,
        "top_p": 0,
    },
}
response = requests.post(api, json=payload)

print(response.text)
