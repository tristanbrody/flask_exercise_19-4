from flask import Flask, request, render_template, url_for, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys, SurveyResponse

app = Flask(__name__)

app.config['SECRET_KEY'] = "fake"
debug = DebugToolbarExtension(app)

@app.route('/')
def home_page():
    #clear out some session variables
    session.pop("current_survey", None)
    session.pop("current_survey_length", None)
    session.pop("current_survey_question", None)
    return render_template('home_page.html', surveys=surveys)

@app.route('/start/survey', methods={"POST"})
def init_survey():
    session["current_survey"] = request.form["survey_name"]
    #check if selected survey is already completed
    try:
        if session[f"{session['current_survey']}_complete"]:
            return survey_completed(session["current_survey"], True)
        # elif session["current_survey_question"] > 1:
        #     survey_name = session['current_survey']
        #     current_survey_question = session['current_survey_question']
        #     return redirect(f'/{survey_name}/{current_survey_question}')
    except KeyError:
        #since selected survey isn't completed, initialize some session variables
        session[f"{session['current_survey']}_complete"] = False
        survey_name = session['current_survey']
        
        session["current_survey_question"] = 1
        session["current_survey_length"] = surveys[session["current_survey"]].survey_length
        session[f"{session['current_survey']}_responses"] = []

        return redirect(f'/{survey_name}/1')

@app.route('/answer', methods={"POST"})
def redirect_to_continue_survey():
    #runs when a survey question is answered
    survey_name = session["current_survey"]
    session["current_survey_question"] +=1
    question_number = session["current_survey_question"]

    #check if question number in URL was last question in survey
    if question_number == session["current_survey_length"]+1:
        session[f"{survey_name}_responses"].append({
        surveys[session["current_survey"]].questions[session['current_survey_question']-2].question: request.form["choice"]})
        return survey_completed(session["current_survey"])
    elif question_number > session["current_survey_length"]+1:
        return survey_completed(session["current_survey"])

    elif "choice" in request.form:
        session[f"{survey_name}_responses"].append({
            surveys[session["current_survey"]].questions[session['current_survey_question']-2].question: request.form["choice"]})

    return redirect(f'/{survey_name}/{question_number}')

@app.route('/thanks-dude')
def thank_you_page(survey=""):
    #set session variable marking current survey as complete
    session[f"{session['current_survey']}_complete"] = True
    current_survey = session['current_survey']
    responses = session[f'{current_survey}_responses'] 
    return render_template('thank_you.html', responses=responses)

@app.route('/<survey>/<int:question_number>', methods={"POST", "GET"})
def continue_survey(survey, question_number):

    if session[f"{survey}_complete"]:
        return survey_completed(survey)

    elif question_number > session["current_survey_question"]:
        survey_name = session["current_survey"]
        current_question = session["current_survey_question"]
        return redirect(f'/{survey_name}/{current_question}')

    else:
        return render_template('survey_questions.html', surveys=surveys)

def survey_completed(survey, already_completed=False):
    if already_completed:
        flash("You've already completed this survey")
    return redirect('/thanks-dude')