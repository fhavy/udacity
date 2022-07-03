from functools import total_ordering
import os
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def Paginating_questions(request, selection):
    page= request.args.get('page', 1, type=int)
    start = (page-1)*QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format()for question in selection]
    currenting_questions =questions[start:end]
    return currenting_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)



    #set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs	
  
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
      
 
    #use the after_request decorator to set Access-Control-Allow 
    @app.after_request
    def after_request(response):
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true' )
                response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS,DELETE')
                return response
            
   #create an endpoint to handle Get requests for all availabe categories
    @app.route("/categories")
    def categories():
          categories = Category.query.all()
          categoriesdictionary = {}
          for category in categories:
              categoriesdictionary[category.id] = category.type
              
              return jsonify({'success': True, 'categories': categoriesdictionary})


    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.
    """
    
    @app.route('/questions')
    def questions():
        try:
          #(lol this is for getting all the questions i guess )
            selection = Question.query.order_by(Question.id).all()
          #(lol this definitely gets total number of questions)
            totalQuestions = len(selection)
          #(lol this is to get current question and the next cocde after it is for if the page number is not found)
            currentingQuestions = Paginating_questions(request, selection)           
            if (len(currentingQuestions) == 0):
                abort(404)
          #(lol we are getting all categories here)
            categories = Category.query.all()
            categoriesdictionary = {}
            for category in categories:
                categoriesdictionary[category.id] = category.type

            return jsonify({
                'success': True,
                'questions': currentingQuestions,
                'total_questions': totalQuestions,
                'categories': categoriesdictionary
            })
        except Exception as e:
            print(e)
            abort(400)

    
    """
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
     
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.
    
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
     
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete(id):
        try:
            question = Question.query.filter_by(id=id).one_or_none()
            # (lol when you cant find the question )
            if question is None:
                abort(404)

            question.delete()
            # (lol i am sending back the current books and to update front end)
            selection = Question.query.order_by(Question.id).all()
            currentquestions = Paginating_questions(request, selection)

            return jsonify({
                'success': True,
                 'questions': currentquestions,
                 'deleted': id,
                 'total_questions': len(selection)
            })

        except Exception as e:
            print(e)
            abort(404)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.
    
    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    
    @app.route("/questions", methods=['POST'])
    def plus_question():
        #(lol as you can see it gets the body from request)
        body = request.get_json()
        # (lol this is to a get new data and also for none if not enterd)
        ThenewQuestion = body.get('question', None)
        Thenewanswer = body.get('answer', None)
        AnewCategory = body.get('category', None)
        Anewdifficulty = body.get('difficulty', None)

        try:
            #(lol just  add )
            question = Question(question=ThenewQuestion, answer=Thenewanswer,
                                category=AnewCategory, difficulty=Anewdifficulty)
            question.insert()

            # (lol am sendint  back the current questions yeah and alsso to update front end)
            selection = Question.query.order_by(Question.id).all()
            currenquestions = Paginating_questions(request, selection)

            return jsonify({
                'success': True,
                'created': question.id,
                'questions': currenquestions,
                'total_questions': len(selection)
            })

        except Exception as e:
            print(e)
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
     
     
    @app.route("/search", methods=['POST'])
    def post_search():
        body = request.get_json()
        search = body.get('searchTerm')
        questions = Question.query.filter(
            Question.question.ilike('%'+search+'%')).all()

        if questions:
            currentquestions = Paginating_questions(request, questions)
            return jsonify({
                'success': True,
                'questions': currentquestions,
                'total_questions': len(questions)
            })
        else:
            abort(404)
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:id>/questions")
    def questions_based_on_categories(id):
        #(lol this baby retrives the category by given id)
        category = Category.query.filter_by(id=id).one_or_none()
        if category:
            # (lol this baby also retrives all questions in a category)
            questionsInCat = Question.query.filter_by(category=str(id)).all()
            currentquestions = Paginating_questions(request, questionsInCat)

            return jsonify({
                'success': True,
                'questions': currentquestions,
                'total_questions': len(questionsInCat),
                'current_category': category.type
            })
        # (lol this baby handles  category not founs)
        else:
            abort(404)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def get_category_to_play_the_quiz():
        # (lol this bad boy gets the qestions category and the previous question)
        body = request.get_json()
        quizCategory = body.get('quiz_category')
        previousQuestion = body.get('previous_questions')

        try:
            if (quizCategory['id'] == 0):
                questionsQuery = Question.query.all()
            else:
                questionsQuery = Question.query.filter_by(
                    category=quizCategory['id']).all()

            randomIndex = random.randint(0, len(questionsQuery)-1)
            nextquest = questionsQuery[randomIndex]

            stillQuestions = True
            while nextquest.id not in previousQuestion:
                nextquest = questionsQuery[randomIndex]
                return jsonify({
                    'success': True,
                    'question': {
                        "answer": nextquest.answer,
                        "category": nextquest.category,
                        "difficulty": nextquest.difficulty,
                        "id": nextquest.id,
                        "question": nextquest.question
                    },
                    'previousQuestion': previousQuestion
                })

        except Exception as e:
            print(e)
            abort(404)
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    # (lol this is for 404 errors)
    @app.errorhandler(404)
    def page_is_not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "page is not found",
        }), 404
        
         # (lol this is for 422 errors)   
    @app.errorhandler(422)
    def Error_is_unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Error_is_unprocessable",
        }), 422
        
        
                 # (lol this is for 405 errors)   
    @app.errorhandler(405)
    def the_method_is_not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "the method is not allowed ",
        }), 400
        # (lol this is for 500 errors)    
    @app.errorhandler(500)
    def the_internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "the internal server error",
        }), 500
        
         # (lol this is for 400 errors)   
    @app.errorhandler(400)
    def the_request_is_bad(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "the_request_is_bad ",
        }), 400
        
        
    return app

