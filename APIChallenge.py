from flask import Flask, jsonify, request, send_file
from io import BytesIO
from flasgger import Swagger, swag_from
from werkzeug.exceptions import MethodNotAllowed
from wordcloud import WordCloud
from collections import Counter
import re
import os
import sqlite3
import pandas as pd
import matplotlib, matplotlib.pyplot as plt
import seaborn as sns
import git

matplotlib.use('Agg')
app = Flask(__name__)
swagger = Swagger(app, template_file='swagger.yaml')

# read CSV file
def read_csv_file(file):
    df = pd.read_csv(file)
    return df

def calculate_numeric_columns(data_frame):
    global numeric_columns
    numeric_columns = data_frame.select_dtypes(include=['float', 'integer'])

def initialize_database():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS text_data (id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT)''')
    conn.commit()
    return conn, c

# for deleting data.db, use carefully!
def delete_db():
    db_file_path = 'data.db'
    if os.path.exists(db_file_path):
        # Remove the data.db file
        os.remove(db_file_path)
        print("data.db file has been successfully deleted.")
    else:
        print("data.db file does not exist.")

@app.route('/cleanse_text', methods=['POST'])
@swag_from('swagger.yaml')
def cleanse_text():
    if request.method == 'POST':
        text = request.form.get('text')
        if not text:
            return jsonify({'error': 'Invalid input'}), 400
        cleansed_text = re.sub(r'[^a-zA-Z0-9]', ' ', text)
        result = {'cleansed_text': cleansed_text}
        # Save cleansed text to SQLite database
        conn, c = initialize_database()
        c.execute("INSERT INTO text_data (text) VALUES (?)", (cleansed_text,))
        conn.commit()
        return jsonify(result)
    
@app.route('/cleanse_text_file', methods=['POST'])
@swag_from('swagger.yaml')
def cleanse_text_file():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400
    text = file.read().decode('utf-8')
    cleansed_text = re.sub(r'[^a-zA-Z0-9]', ' ', text)
    result = {'cleansed_text': cleansed_text}
    conn, c = initialize_database()
    c.execute("INSERT INTO text_data (text) VALUES (?)", (cleansed_text,))
    conn.commit()
    return jsonify(result)

@app.route('/view_cleansed_text', methods=['GET'])
def view_cleansed_text():
    conn, c = initialize_database()
    c.execute("SELECT * FROM text_data")
    data = c.fetchall()
    cleansed_text_list = [row[1] for row in data]
    return '\n'.join(cleansed_text_list)

@app.route('/multiply_numbers', methods=['POST'])
@swag_from('swagger.yaml')
def multiply_numbers():
    num1 = request.form.get('num1')
    num2 = request.form.get('num2')
    if not num1 or not num2:
        return jsonify({'error': 'Invalid input'}), 400
    try:
        num1 = float(num1)
        num2 = float(num2)
        result = {'result': num1 * num2}
        return jsonify(result)
    except ValueError:
        return jsonify({'error': 'Invalid input'}), 400

@app.route('/reverse_text', methods=['POST'])
@swag_from('swagger.yaml')
def reverse_text():
    text = request.form.get('text')
    if not text:
        return jsonify({'error': 'Invalid input'}), 400
    reversed_text = text[::-1]
    result = {'reversed_text': reversed_text}
    return jsonify(result)

@app.route('/count_words', methods=['POST'])
@swag_from('swagger.yaml')
def count_words():
    text = request.form.get('text')
    if not text:
        return jsonify({'error': 'Invalid input'}), 400
    word_count = len(text.split())
    result = {'word_count': word_count}
    return jsonify(result)

@app.route('/git_pull', methods=['POST'])
@swag_from('swagger.yaml')
def git_pull():
    try:
        repo = git.Repo('.')
        repo.remotes.origin.pull()
        return 'Git pull successful'
    except git.exc.GitCommandError:
        return jsonify({'error': 'Git pull failed'}), 500

@app.route('/git_push', methods=['POST'])
@swag_from('swagger.yaml')
def git_push():
    try:
        repo = git.Repo('.')
        repo.remotes.origin.push()
        return 'Git push successful'
    except git.exc.GitCommandError:
        return jsonify({'error': 'Git push failed'}), 500

@app.route('/analyze_data', methods=['POST'])
@swag_from('swagger.yaml')
def analyze_data():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400
    salary_filter = request.form.get('salary_filter')
    age_filter = request.form.get('age_filter')
    occupations_filter = request.form.getlist('occupations_filter')
    try:
        df = pd.read_csv(file)
        if salary_filter is not None:
            df = df[df['Salary'] > int(salary_filter)]
        if age_filter is not None:
            df = df[df['Age'] > int(age_filter)]
        if occupations_filter:
            occupations_filter = [occupation.lower() for occupation in occupations_filter]
            df = df[df['Occupation'].str.lower().isin([occupation.lower() for occupation in occupations_filter])]
        # Select all columns from the DataFrame
        selected_columns = df.columns.tolist()
        # Convert the result to a list of dictionaries
        output = df.to_dict(orient='records')
        return jsonify({'data_analysis_result': output, 'selected_columns': selected_columns})
    except pd.errors.ParserError:
        return jsonify({'error': 'Invalid CSV file format'}), 400

@app.route('/visualize_data', methods=['POST'])
@swag_from('swagger.yaml')
def visualize_data():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400
    try:
        df = pd.read_csv(file)
        column = request.form.get('column')
        if column not in df.columns:
            return jsonify({'error': 'Invalid column name'}), 400
        plt.figure(figsize=(8, 6))
        sns.histplot(data=df, x=column, bins=10, kde=True)
        plt.title(f'Histogram of {column}')
        plt.xlabel(column)
        plt.ylabel('Count')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        image_buffer = BytesIO()
        plt.savefig(image_buffer, format='png')
        plt.close()
        image_buffer.seek(0)
        return send_file(image_buffer, mimetype='image/png')
    except pd.errors.ParserError:
        return jsonify({'error': 'Invalid CSV file format'}), 400

@app.route('/generate_pie_chart', methods=['POST'])
@swag_from('swagger.yaml')
def generate_pie_chart():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400
    try:
        df = pd.read_csv(file)
        column = request.form.get('column')
        if column not in df.columns:
            return jsonify({'error': f'Column "{column}" does not exist in the CSV file'}), 400
        category_counts = df[column].value_counts()
        plt.figure(figsize=(8, 6))
        plt.pie(category_counts, labels=category_counts.index, autopct='%1.1f%%')
        plt.title(f'Distribution of {column.capitalize()}')
        plt.axis('equal')
        plt.legend()
        image_buffer = BytesIO()
        plt.savefig(image_buffer, format='png')
        plt.close()
        image_buffer.seek(0)
        return send_file(image_buffer, mimetype='image/png')
    except pd.errors.ParserError:
        return jsonify({'error': 'Invalid CSV file format'}), 400

@app.route('/generate_word_cloud', methods=['POST'])
@swag_from('swagger.yaml')
def generate_word_cloud():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400
    try:
        text = file.read().decode('utf-8')
        wordcloud = WordCloud().generate(text)
        plt.figure(figsize=(8, 6))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('Word Cloud')
        image_buffer = BytesIO()
        plt.savefig(image_buffer, format='png')
        plt.close()
        image_buffer.seek(0)
        return send_file(image_buffer, mimetype='image/png')
    except pd.errors.ParserError:
        return jsonify({'error': 'Invalid file format'}), 400

@app.route('/frequency_word_cloud', methods=['POST'])
@swag_from('swagger.yaml')
def frequency_word_cloud():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400
    try:
        text = file.read().decode('utf-8')
        word_counter = Counter(text.split())
        # Determine the maximum and minimum frequencies
        max_frequency = max(word_counter.values())
        min_frequency = min(word_counter.values())
        wordcloud = WordCloud(
            width=800,
            height=600,
            min_font_size=10,
            max_font_size=100,
            relative_scaling=0.5  # Adjust this value to control the size variation
        ).generate_from_frequencies(word_counter)
        plt.figure(figsize=(8, 6))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('Word Cloud')
        image_buffer = BytesIO()
        plt.savefig(image_buffer, format='png')
        plt.close()
        image_buffer.seek(0)
        return send_file(image_buffer, mimetype='image/png')
    except pd.errors.ParserError:
        return jsonify({'error': 'Invalid file format'}), 400

@app.route('/visualize_skewness', methods=['POST'])
@swag_from('swagger.yaml')
def visualize_skewness():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400
    column_name = request.form.get('column_name')
    if not column_name:
        return jsonify({'error': 'Invalid column name'}), 400
    df = read_csv_file(file)
    plt.figure(figsize=(8, 6))
    sns.histplot(df[column_name], kde=True)
    plt.title('Skewness - Distribution of ' + column_name)
    plt.xlabel(column_name)
    plt.ylabel('Count')
    image_buffer = BytesIO()
    plt.savefig(image_buffer, format='png')
    plt.close()
    image_buffer.seek(0)
    return send_file(image_buffer, mimetype='image/png')

@app.route('/visualize_kurtosis', methods=['POST'])
@swag_from('swagger.yaml')
def visualize_kurtosis():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400
    column_name = request.form.get('column_name')
    if not column_name:
        return jsonify({'error': 'Invalid column name'}), 400
    df = read_csv_file(file)
    plt.figure(figsize=(8, 6))
    sns.histplot(df[column_name], kde=True)
    plt.title('Kurtosis - Distribution of ' + column_name)
    plt.xlabel(column_name)
    plt.ylabel('Count')
    image_buffer = BytesIO()
    plt.savefig(image_buffer, format='png')
    plt.close()
    image_buffer.seek(0)
    return send_file(image_buffer, mimetype='image/png')

@app.errorhandler(MethodNotAllowed)
def handle_method_not_allowed(error):
    return jsonify({'error': 'Method not allowed'}), 405

if __name__ == '__main__':
    app.run(port=8000,debug=True)
