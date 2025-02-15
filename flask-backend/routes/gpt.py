from openai import OpenAI
from dotenv import load_dotenv
from flask import Flask, request, jsonify, Blueprint
import os

# Load environment variables from the .env file
load_dotenv()

gpt_bp = Blueprint('gpt', __name__)

# Access the OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

@gpt_bp.route("/generate", methods=["POST"])
def generate_response(prompt, input):
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "developer", "content": prompt},
            {
                "role": "user",
                "content": input
            }
        ]
    )

    return (completion.choices[0].message.content)

@gpt_bp.route("/generate_json", methods=["POST"])
def generate_response_json(prompt, input):
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "developer", "content": prompt},
            {
                "role": "user",
                "content": input
            }
        ]
    )

    return (completion.choices[0].message.content)