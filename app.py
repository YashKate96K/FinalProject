import os
from flask import Flask, request, render_template
from google.cloud import firestore
from google.cloud import language_v1

app = Flask(__name__)
db = firestore.Client()
nlp_client = language_v1.LanguageServiceClient()

@app.route('/', methods=['GET', 'POST'])
def index():
    feedback_list = []
    if request.method == 'POST':
        feedback = request.form['feedback']
        doc_ref = db.collection('feedback').add({'text': feedback})
        document = language_v1.Document(content=feedback, type_=language_v1.Document.Type.PLAIN_TEXT)
        sentiment = nlp_client.analyze_sentiment(request={'document': document}).document_sentiment
        score = sentiment.score
        magnitude = sentiment.magnitude
        db.collection('feedback').document(doc_ref[1].id).update({'sentiment_score': score, 'magnitude': magnitude})

    feedbacks = db.collection('feedback').stream()
    for fb in feedbacks:
        feedback_list.append(fb.to_dict())

    return render_template('index.html', feedbacks=feedback_list)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))