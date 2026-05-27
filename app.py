from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
DATA_FILE = "exam_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    return []

def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/add-exam', methods=['POST'])
def add_exam():
    data = load_data()
    request_data = request.json
    
    try:
        marks = float(request_data['marks'])
        total_marks = float(request_data['total_marks'])
        subject = request_data['subject']
        
        if marks < 0 or total_marks <= 0 or marks > total_marks:
            return jsonify({'success': False, 'message': 'Invalid marks!'})
        
        percentage = (marks / total_marks) * 100
        
        record = {
            "subject": subject,
            "marks": marks,
            "total_marks": total_marks,
            "percentage": round(percentage, 2),
            "date": datetime.now().strftime("%d-%m-%Y %H:%M")
        }
        
        data.append(record)
        save_data(data)
        return jsonify({'success': True, 'message': f'{subject} added successfully!'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/get-records', methods=['GET'])
def get_records():
    data = load_data()
    return jsonify(data)

@app.route('/api/get-statistics', methods=['GET'])
def get_statistics():
    data = load_data()
    
    if not data:
        return jsonify({'success': False})
    
    percentages = [record['percentage'] for record in data]
    average = sum(percentages) / len(percentages)
    best = max(data, key=lambda x: x['percentage'])
    worst = min(data, key=lambda x: x['percentage'])
    
    if average >= 90:
        grade = "A+ (Outstanding!)"
    elif average >= 80:
        grade = "A (Very Good!)"
    elif average >= 70:
        grade = "B (Good!)"
    elif average >= 60:
        grade = "C (Average)"
    else:
        grade = "D (Need Improvement)"
    
    return jsonify({
        'success': True,
        'total_exams': len(data),
        'average': round(average, 2),
        'best_subject': best['subject'],
        'best_percentage': best['percentage'],
        'worst_subject': worst['subject'],
        'worst_percentage': worst['percentage'],
        'grade': grade,
        'highest': round(max(percentages), 2),
        'lowest': round(min(percentages), 2)
    })

@app.route('/api/delete-record/<int:index>', methods=['DELETE'])
def delete_record(index):
    data = load_data()
    
    if 0 <= index < len(data):
        data.pop(index)
        save_data(data)
        return jsonify({'success': True, 'message': 'Record deleted!'})
    
    return jsonify({'success': False, 'message': 'Invalid index!'})

if __name__ == '__main__':
    app.run(debug=True, port=5099)
