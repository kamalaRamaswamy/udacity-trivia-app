import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, data):
    page = request.args.get('page', 1, type=int)
    start = (page -1 ) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    data = [item.format() for item in data]
    return data[start:end]

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    if test_config is None:
        setup_db(app)
    else:
        database_path = test_config.get('SQLALCHEMY_DATABASE_URI')
        setup_db(app, database_path=database_path)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def get_categories():
        try:
            allCategories = Category.query.all()
            if len(allCategories) == 0:
                abort(404)

            return jsonify({
                'success': True,
                'categories': {category.id: category.type for category in allCategories}
            })
        except Exception as e:
            print(e)


    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def get_questions():
        page = request.args.get('page', 1, type=int)
        try:
            questions = Question.query.all().paginate(page, 10)
            allCategories = Category.query.all()

            if len(questions) == 0:
                abort(404)
            if len(allCategories) == 0:
                abort(404)

            return jsonify({
                'questions': questions,
                'total_questions': len(questions),
                'categories': {category.id: category.type for category in allCategories},
                'current_category': None,
                'success': True,
            })

        except Exception as e:
            print(e)
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<question_id>", methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)
            if question:
                question.delete()
                return jsonify({
                    'success': True,
                    'deleted': question_id
                })
            abort(404)

        except Exception as e:
            print(e)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        try:
            body = request.get_json()
            search_term = body.get('searchTerm', None)

            if search_term:
                search_results = Question.query.filter(
                    Question.question.ilike(f'%{search_term}%')).all()

                return jsonify({
                    'success': True,
                    'questions': [question.format() for question in search_results],
                    'total_questions': len(search_results),
                    'current_category': None
                })
            abort(404)

        except Exception as e:
            print(e)

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
    def post_question():
        try:
            body = request.get_json()
            question = body.get('question')
            answer = body.get('answer')
            difficulty = body.get('difficulty')
            category = body.get('category')

            try:
                question = Question(question=question, answer=answer,
                                    difficulty=difficulty, category=category)
                print('question', question)
                if question.question:
                    question.insert()

                return jsonify({
                    'success': True,
                    'created': question.id,
                })

            except:
                abort(422)

        except Exception as e:
            print(e)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions',methods=['GET'])
    def get_questions_by_category(category_id):
        try:
            category = Category.query.get(category_id)
            if category is None :
                abort(404)
            
            questions = Question.query.filter(Question.category == category_id).all()

            return jsonify({
                    'success':True,
                    'questions':paginate_questions(request, selection),
                    'total_questions' : len(questions),
                    'current_category' : category_id
                    })

        except Exception as e:
            print(e)

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
    def get_quizzes():
        try:
            body = request.get_json()
            prev_questions = body.get('previous_questions', None)
            quiz_category = body.get('quiz_category', None)
            questions = []
            quiz_question = {}
            selected_category = Category.query.filter(
                Category.type == str(quiz_category['type'])).one_or_none()
            category_id = selected_category.id
            questions = Question.query.filter(
                    Question.id.notin_(prev_questions),
                    Question.category == category_id).all()
            for i in range(len(questions)):
                question = random.choice(questions)
                quiz_question = question.format()
            return jsonify({
                'question': quiz_question,
                'success': True})
        except Exception as e:
            print(e)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource Not Found"
        }), 404

    @app.errorhandler(422)
    def not_processable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Not Processable"
        }), 422

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal Server Error"
        }), 500


    return app

