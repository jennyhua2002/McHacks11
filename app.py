import pandas as pd
from flask import Flask, request, jsonify, render_template
from fuzzywuzzy import process

app = Flask(__name__)

def load_excel_data(file_path):
    data = pd.read_excel(file_path, engine='openpyxl')
    diseases_to_symptoms = {}
    for index, row in data.iterrows():
        disease = row['Disease']
        symptoms = row[1:].dropna().values.tolist()
        for symptom in symptoms:
            symptom_lower = symptom.lower()
            if symptom_lower not in diseases_to_symptoms:
                diseases_to_symptoms[symptom_lower] = set()
            diseases_to_symptoms[symptom_lower].add(disease)
    diseases_to_symptoms = {symptom: list(diseases) for symptom, diseases in diseases_to_symptoms.items()}
    return diseases_to_symptoms

diseases_db = load_excel_data('very_clean.xlsx')


def find_diseases(input_symptom):

    closest_match,score = process.extractOne(input_symptom.lower(), diseases_db.keys())
    if score > 80:
        return diseases_db[closest_match]
    else:
        return ["No disease found"]


@app.route('/search', methods=['GET'])
def search():
    symptom = request.args.get('symptom', '').strip()
    if not symptom:
        return jsonify({"error": "No symptom provided"}), 400
    possible_diseases = find_diseases(symptom)
    return jsonify(possible_diseases)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)