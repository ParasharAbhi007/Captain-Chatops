from flask import Flask, render_template, request, jsonify
from session import Session
import requests
import json
from chat import get_response

app = Flask(__name__)
session = Session()

@app.get("/")

def index_get():
    return render_template("base.html")

def saveResponses(session: Session):
    url = "localhost:8080/twilio/incoming"

    payload = json.dumps({
        "deploymentType:": session.deploymentType
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': ''
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)

@app.post("/predict")
def predict():
    
    text = request.get_json().get("message")
    #check if the text is valid
    tag, response = get_response(text)
    print(tag,response)
    if session.step is None and tag == 'deployment':
        session.step = "deployment"
    elif session.step == "deployment" and tag == 'deployment_type':
        session.step = "deployment_type"
        session.deploymentType = text
    elif session.step == "deployment_type" and tag == 'pipeline_name':
        session.step = "pipeline_name"
        session.pipelineName = text
        print("session.pipelineName:", session.pipelineName)
    elif session.step == "pipeline_name" and tag == 'service':
        session.step = "service"
        session.service = text
        #response = "Please select the infrastructure for the pipeline: 1. infra1, 2. infra2"
    elif session.step == "service" and tag == 'infra':
        session.step = "infra"
        session.infra = text
        #response = "Please select the connector for the pipeline: 1. connector1, 2. connector2"
    elif session.step == "infra" and tag == 'connector':
        session.step = "connector"
        session.connector = text
        #response = "Great! Please confirm that you want to deploy your pipeline with the following options: deployment type - {}, pipeline name - {}, service - {}, infrastructure - {}, connector - {}. Type 'Yes' to confirm or 'No' to start over.".format(session.deploymentType, session.pipelineName, session.service, session.infra, session.connector)
    elif session.step == "connector" and tag == 'confirm':
        session.step = "end"
        # API call
        saveResponses(session)
        #response = "Great! I've made the API call for you. Is there anything else I can help you with?"
    
    
    message = {"answer": response}
    return jsonify(message)



if __name__ == "__main__":
    app.run(debug=True)