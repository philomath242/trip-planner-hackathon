from flask import Flask, render_template, request
import google.generativeai as genai
import os


app = Flask(__name__)

def read_from_file(file_path):
    try:
        with open(file_path, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return None

# Prioritize environment variable over file
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or read_from_file("gemini.key")

if not GEMINI_API_KEY:
    raise ValueError("Error: GEMINI_API_KEY must be set via environment variable or gemini.key file")

genai.configure(api_key=GEMINI_API_KEY)


try:
    # Ensure the API key is valid before trying to get the model
    if GEMINI_API_KEY:
        model = genai.GenerativeModel("models/gemini-pro")
    else:
        model = None
except Exception as e:
    print(f"Error initializing GenerativeModel: {e}")
    model = None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    print(request.form)

    if not model:
        print("Generative AI model is not configured. Please check API key.", "error")

    # Extract form data
    from_loc = request.form["from"]
    to_loc = request.form["to"]
    start_date = request.form["start_date"]
    end_date = request.form["end_date"]
    budget = request.form["budget"]
    travel_theme = request.form["traveltheme"]

    # Construct the prompt
    prompt = (
        f"Plan a trip from {from_loc} to {to_loc} "
        f"starting on {start_date} and ending on {end_date} "
        f"with a budget of {budget} and a travel theme of {travel_theme}. "
        f"Provide a detailed itinerary and suggestions."
    )

    try:
        response = model.generate_content(prompt)

        if response and response.parts:
            response_text = "".join(
                [part.text for part in response.parts if hasattr(part, "text")]
            )
            return response_text
        else:
            print("No content received from the AI model.", "warning")
            return render_template(
                "index.html", trip_plan="Could not generate trip plan."
            )
    except Exception as e:
        print(f"An unexpected error occurred: {e}", "error")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
