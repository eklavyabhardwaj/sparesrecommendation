from flask import Flask, request, render_template, redirect, url_for, session
import pickle
import os

app = Flask(__name__)

app.secret_key = os.urandom(24)

# Load the serialized model
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        tube_size = request.form['tube_size']
        flow_rate = float(request.form['flow_rate'])
        rpm = float(request.form['rpm'])

        # Convert tube size to our numeric format
        tube_size = float('.'.join(tube_size.split('x')))

        # Make a prediction
        prediction = model.predict([[rpm, tube_size, flow_rate]])

        # If model supports predict_proba, get the confidence. Else, adjust as necessary.
        confidence = model.predict_proba([[rpm, tube_size, flow_rate]])
        max_confidence = max(confidence[0])  # Get maximum confidence

        # Check if the confidence is 100%
        if max_confidence == 1.0:
            session['recommended_pump'] = prediction[0]
            return redirect(url_for('pump_details'))
        else:
            session['recommended_pump'] = prediction[0]
            return redirect(url_for('low_confidence_pump_details'))



    return render_template('index.html')

@app.route('/pump_details', methods=['GET'])
def pump_details():
    recommended_pump = session.get('recommended_pump', None)
    return render_template('pump_details.html', recommended_pump=recommended_pump)

@app.route('/low_confidence_pump_details', methods=['GET'])
def low_confidence_pump_details():
    recommended_pump = session.get('recommended_pump', None)
    return render_template('alternate_pump.html', recommended_pump=recommended_pump)


if __name__ == "__main__":
    app.run(debug=True)
