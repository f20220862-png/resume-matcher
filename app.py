import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Gemini API
api_key = os.getenv('GEMINI_API_KEY')
if api_key:
    genai.configure(api_key=api_key)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/tailor', methods=['POST'])
def tailor_resume():
    if not api_key:
        return jsonify({"error": "Gemini API Key is not set in the .env file."}), 500

    data = request.json
    jd = data.get('jd')
    resume = data.get('resume')

    if not jd or not resume:
        return jsonify({"error": "Job description and resume are required."}), 400

    system_prompt = """You are an expert LaTeX resume writer and career coach. Your job is to take a LaTeX resume and tailor it to a specific job description — WITHOUT fabricating any experience.

Rules:
- Return ONLY valid, compilable LaTeX code. No explanations, no markdown, no code fences.
- Start your response directly with \\documentclass or the first LaTeX command.
- Keep the exact same LaTeX document structure, packages, and formatting commands as the original.
- Reorder bullet points (\\item entries) to prioritise what's most relevant to this JD.
- Rephrase existing \\item bullets using keywords and language from the JD (do not invent new experience).
- Strengthen weak bullets that are relevant to the role.
- De-emphasise or condense experience clearly unrelated to this role.
- Update or add a Profile/Summary section at the top, targeted at this specific role.
- Be direct and specific. No filler phrases like "proven track record" or "results-oriented professional".
- The output must be 100% valid LaTeX that compiles without errors."""

    user_prompt = f"""JOB DESCRIPTION:
{jd}

ORIGINAL LATEX RESUME:
{resume}

Please tailor the LaTeX resume for this specific role. Output ONLY the complete, compilable LaTeX code."""

    try:
        # Use gemini-flash-latest as it's fast and perfect for this text task
        model = genai.GenerativeModel('gemini-flash-latest', system_instruction=system_prompt)
        response = model.generate_content(user_prompt)
        
        return jsonify({"content": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
