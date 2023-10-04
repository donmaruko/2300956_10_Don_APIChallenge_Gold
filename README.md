# Data Analysis and Text Manipulation with Flask

This Flask application provides various data analysis and text manipulation functionalities through a RESTful API. It includes operations for cleansing text, performing statistical calculations, visualizing data, and more.

## Installation

1. Clone this repository to your local machine:
```shell
git clone https://github.com/donmaruko/Flask-Data-Analysis.git
```

2. Install the required Python packages listed in the `requirements.txt` file:
```shell
pip install -r requirements.txt
```

3. Start the Flask application
```shell
python API.py
```

4. The application will be accessible at `http://localhost:8000`.

## API Endpoints

The API endpoints provided by this application are documented using Swagger. You can access the Swagger documentation by visiting `http://localhost:8000/apidocs/` while the application is running.

### Text-Related Endpoints:

The application expects data files in CSV format for data analysis and text files for text manipulation. You can upload these files to the corresponding endpoints for processing.

- `/cleanse_text`: Cleanses text by removing non-alphanumeric characters.
- `/cleanse_text_file`: Cleanses text from an uploaded file.
- `/multiply_numbers`: Multiplies two numbers.
- `/reverse_text`: Reverses the order of characters in text.
- `/count_words`: Counts the number of words in text.

### Data-Visualization Endpoints:

- `/analyze_data`: Analyzes data from an uploaded CSV file.
- `/visualize_data`: Visualizes data distribution from an uploaded CSV file.
- `/generate_pie_chart`: Generates a pie chart for a specific column in a CSV file.
- `/generate_word_cloud`: Generates a word cloud from text data.
- `/frequency_word_cloud`: Generates a word cloud based on word frequencies.
- `/visualize_skewness`: Visualizes skewness for a specific column.
- `/visualize_kurtosis`: Visualizes kurtosis for a specific column.

### Git Endpoints:

- `/git_pull`: Performs a Git pull to update the repository.
- `/git_push`: Performs a Git push to push changes to the repository.

Please refer to the Swagger documentation for more details on how to use these endpoints.

## Contributing

Contributions are welcome! If you have any suggestions, bug reports, or feature requests, please create an issue or submit a pull request.
