import os
from flask import Flask, render_template, jsonify

app = Flask(__name__)

def load_cereals():
    """Load cereal names from the cereal.txt file."""
    cereals = []
    data_file = os.path.join(os.path.dirname(__file__), 'Data', 'cereal.txt')
    
    with open(data_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        # Skip header and empty lines
        for line in lines[1:]:
            line = line.strip()
            if line:
                # Split by whitespace and get the brand name (first column)
                parts = line.split('"')
                if len(parts) >= 2:
                    brand_name = parts[1]
                    cereals.append(brand_name)
    
    return cereals

@app.route('/')
def index():
    """Serve the main page."""
    cereals = load_cereals()
    return render_template('index.html', cereals=cereals)

@app.route('/api/cereals')
def get_cereals():
    """API endpoint to get cereal list."""
    cereals = load_cereals()
    return jsonify(cereals)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)
