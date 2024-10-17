from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os
from textblob import TextBlob
from datetime import datetime

app = Flask(__name__)

# File path for storing scores during session
DATA_FILE = 'scores.csv'

# Ensure the data file exists at the start of the app
def ensure_data_file():
    if not os.path.exists(DATA_FILE):
        # Create a new DataFrame if the file doesn't exist
        df = pd.DataFrame(columns=['Name', 'Communication Skills', 'Problem Solving', 'Technical Knowledge', 'Teamwork', 'Adaptability', 'Comment'])
        df.to_csv(DATA_FILE, index=False)

# Call the function at the start
ensure_data_file()

@app.route('/')
def index():
    # Load existing data
    df = pd.read_csv(DATA_FILE)
    return render_template('index.html', scores=df.to_dict(orient='records'))

@app.route('/submit', methods=['POST'])
def submit_scores():
    # Get data from form
    name = request.form['name']
    comm_skills = int(request.form['communication'])
    problem_solving = int(request.form['problem_solving'])
    tech_knowledge = int(request.form['technical'])
    teamwork = int(request.form['teamwork'])
    adaptability = int(request.form['adaptability'])
    comment = request.form['comment']

    # Load existing data
    df = pd.read_csv(DATA_FILE)

    # Create a new DataFrame for the new entry
    new_entry = pd.DataFrame({
        'Name': [name],
        'Communication Skills': [comm_skills],
        'Problem Solving': [problem_solving],
        'Technical Knowledge': [tech_knowledge],
        'Teamwork': [teamwork],
        'Adaptability': [adaptability],
        'Comment': [comment]
    })

    # Append the new entry
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)  # Save the updated DataFrame

    return redirect(url_for('index'))

@app.route('/top_candidates')
def top_candidates():
    # Load existing data
    df = pd.read_csv(DATA_FILE)
    
    # Calculate total score
    df['Total Score'] = df[['Communication Skills', 'Problem Solving', 'Technical Knowledge', 'Teamwork', 'Adaptability']].sum(axis=1)

    # Analyze sentiment for each comment
    df['Sentiment'] = df['Comment'].apply(lambda x: TextBlob(x).sentiment.polarity)

    # Sort by Total Score and, in case of ties, by sentiment (higher sentiment first)
    df_sorted = df.sort_values(by=['Total Score', 'Sentiment'], ascending=[False, False])

    # Limit the results to top 20 or fewer
    top_candidates = df_sorted.head(20)[['Name', 'Total Score']]  # Sentiment is removed from the displayed columns

    return render_template('top_candidates.html', candidates=top_candidates.to_dict(orient='records'))

@app.route('/save_and_shutdown')
def save_and_shutdown():
    # Load existing data
    df = pd.read_csv(DATA_FILE)

    # Generate a filename with current date and time
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    new_filename = f'result_{timestamp}.csv'

    # Save the current data into the new file
    df.to_csv(new_filename, index=False)

    return "Data saved to {}. You can now close the website.".format(new_filename)

if __name__ == '__main__':
    app.run(debug=True)
