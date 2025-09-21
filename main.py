from flask import Flask, render_template, request, redirect, url_for, flash
import google.generativeai as genai
import os
import secrets
import markdown

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)


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
    raise ValueError(
        "Error: GEMINI_API_KEY must be set via environment variable or gemini.key file"
    )

genai.configure(api_key=GEMINI_API_KEY)


# print("Available models:")
# for m in genai.list_models():
#     # Filter for models that support generateContent, as that's what you likely need
#     if "generateContent" in m.supported_generation_methods:
#         print(f"  Name: {m.name} with Description: {m.description}")
#         print(f"  Supported methods: {m.supported_generation_methods}")
#         print("-" * 20)


try:
    # Ensure the API key is valid before trying to get the model
    if GEMINI_API_KEY:
        model = genai.GenerativeModel("models/gemini-1.5-pro")
    else:
        model = None
except Exception as e:
    print(f"Error initializing GenerativeModel: {e}")
    model = None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/results")
def result():
    plan = request.args.get("plan")

    return render_template("result.html", plan=plan)


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
    no_of_people = request.form["travellers"]
    # Construct the prompt
    # prompt = (
    #     f"Plan a trip from {from_loc} to {to_loc} "
    #     f"starting on {start_date} and ending on {end_date} "
    #     f"with a budget of {budget} INR and a travel theme of {travel_theme}. "
    #     f"Provide a detailed itinerary and suggestions."
    # )

    prompt = (
        f"Create a detailed travel itinerary for a trip from {from_loc} to {to_loc}, "
        f"starting on {start_date} (YYYY-MM-DD) and ending on {end_date} (YYYY-MM-DD), "
        f"with a total budget of {budget} INR and a travel theme of {travel_theme} consisting {no_of_people} traveller(s). "
        f"Include the following in the response, formatted in Markdown for clarity:\n"
        f"- **Overview**: A brief summary of the trip, including the theme and key highlights.\n"
        f"- **Itinerary**: A day-by-day plan with specific activities, locations, and estimated times (e.g., morning, afternoon, evening).\n"
        f"- **Transportation**: Suggested modes of travel (e.g., flights, trains, buses) with estimated costs and booking tips.\n"
        f"- **Accommodation**: Recommended places to stay (e.g., hotels, hostels, or rentals) within the budget, including estimated costs.\n"
        f"- **Activities**: Specific activities aligned with the {travel_theme} theme (e.g., cultural visits, adventure, food tours), including estimated costs.\n"
        f"- **Dining**: Suggested dining options that reflect local cuisine or the travel theme, with approximate costs.\n"
        f"- **Budget Breakdown**: A clear table summarizing costs for transportation, accommodation, activities, dining, and any miscellaneous expenses, ensuring the total stays within {budget} INR.\n"
        f"- **Tips and Notes**: Practical advice (e.g., packing tips, local customs, safety considerations) and any budget-saving suggestions.\n"
        f"Constraints:\n"
        f"- Ensure all costs are in INR and do not exceed the {budget} INR budget.\n"
        f"- Use realistic and practical suggestions based on current travel conditions as of today.\n"
        f"- Prioritize activities and experiences that strongly align with the {travel_theme} theme.\n"
        f"- Provide specific names of places, restaurants, or services where possible, and avoid generic suggestions.\n"
        f"Return the response in well-structured Markdown format, with clear headings, bullet points, and a table for the budget breakdown."
    )

    print(f"Generated Prompt: {prompt}")

    try:
        response = model.generate_content(prompt)

        if response and response.parts:
            response_text = "".join(
                [part.text for part in response.parts if hasattr(part, "text")]
            )

            response_html = markdown.markdown(response_text)
            return redirect(url_for("result", plan=response_html))
        else:
            return redirect(url_for("index"))
    except Exception as e:
        flash(f"An unexpected error occurred: {e}", "error")
        return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
