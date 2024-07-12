import os
import unittest
import json

from flaskr import create_app
from models import setup_db, Question, Category
from dotenv import load_dotenv

load_dotenv()
database_username = os.getenv("test_database_username")
database_password = os.getenv("test_database_password")
database_name = os.getenv("test_database_name")


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        self.database_path = 'postgresql://{}:{}@{}/{}'.format(database_username, database_password, 'localhost:5432', database_name)
        self.app = create_app(self.database_path)
        self.client = self.app.test_client
        

    def tearDown(self):
        pass
    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    def test_fail_get_categories(self):
        response = self.client().get('/categories/200')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not Found')
    
    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))
    
    def test_fail_get_questions(self):
        res = self.client().get("/questions/1000")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "method not allowed")

    def test_add_question(self):
        new_question = {
            'question': 'quiz question',
            'answer': 'abc',
            'difficulty': 1,
            'category': 1
        }
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_search_questions(self):
        new_search = {'searchTerm': 'a'}
        res = self.client().post('/questions/search', json=new_search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])
        self.assertIsNotNone(data['total_questions'])

    def test_fail_search_questions(self):
        search_data = {
            'searchTerm': 'eafdadcaatea',
        }

        response = self.client().post('/questions/search', json=search_data)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not Found')

    def test_delete_question(self):
        res = self.client().delete('/questions/2')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], '2')
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_fail_delete_question(self):
        res = self.client().delete('/questions/9999')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_get_questions_by_category(self):
        res = self.client().get('categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])

    def test_fail_get_questions_by_category(self):
        res = self.client().get('categories/1000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
    
    def test_get_quiz(self):
        res = self.client().post('/quizzes',
                                 json={'previous_questions': [],
                                       'quiz_category':
                                       {'id': '1', 'type': 'Science'}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])
        self.assertEqual(data['question']['category'], 1)

    def test_fail_get_quiz(self):
        res = self.client().post('/quizzes',
                                 json={
                                     'previous_questions': []
                                 })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 500)
        self.assertEqual(data['success'], False)



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()