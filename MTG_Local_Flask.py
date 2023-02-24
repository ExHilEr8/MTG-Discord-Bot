from flask import Flask, request
import json

ADD_CARDS_PATH = 'MTG Discord Bot\\addcards.json'

lands = ['Plains', 'Island', 'Swamp', 'Mountain', 'Forest']

app = Flask(__name__)

@app.route('/')
def home():
    return 'Default page'

@app.route('/addcards', methods = ['POST'])
def addcards():
    if(request.method == 'POST'):
        with open(ADD_CARDS_PATH, "w") as f:
            json.dump(request.form, f, indent=4)
        
        carddict = list(request.form.values())
        
        print(carddict)
        return 'Response successful'

def run():
    app.run(debug=True)
    
run()