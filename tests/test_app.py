import pytest
from app import app, db
from models import Discipline, Test, Question, Option

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

@pytest.fixture
def sample_discipline(client):
    """Create a sample discipline"""
    with app.app_context():
        discipline = Discipline(name='Mathematics', description='Math courses')
        db.session.add(discipline)
        db.session.commit()
        return discipline.id

@pytest.fixture
def sample_test(client, sample_discipline):
    """Create a sample test"""
    with app.app_context():
        test = Test(
            title='Algebra Test',
            description='Basic algebra',
            discipline_id=sample_discipline
        )
        db.session.add(test)
        db.session.commit()
        return test.id

def test_index_page(client):
    """Test index page loads"""
    response = client.get('/')
    assert response.status_code == 200

def test_create_discipline(client):
    """Test creating a discipline"""
    response = client.post('/api/disciplines', json={
        'name': 'Science',
        'description': 'Science courses'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == 'Science'

def test_get_disciplines(client, sample_discipline):
    """Test getting all disciplines"""
    response = client.get('/api/disciplines')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) >= 1

def test_create_test(client, sample_discipline):
    """Test creating a test"""
    response = client.post('/api/tests', json={
        'title': 'Geometry Test',
        'description': 'Basic geometry',
        'discipline_id': sample_discipline
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['title'] == 'Geometry Test'

def test_get_tests(client, sample_test):
    """Test getting all tests"""
    response = client.get('/api/tests')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) >= 1

def test_create_question(client, sample_test):
    """Test creating a question with options"""
    response = client.post(f'/api/tests/{sample_test}/questions', json={
        'question_text': 'What is 2 + 2?',
        'explanation': 'Basic addition',
        'options': [
            {'option_text': '3', 'is_correct': False, 'order': 0},
            {'option_text': '4', 'is_correct': True, 'order': 1},
            {'option_text': '5', 'is_correct': False, 'order': 2},
            {'option_text': '6', 'is_correct': False, 'order': 3}
        ]
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['question_text'] == 'What is 2 + 2?'
    assert len(data['options']) == 4

def test_take_test(client, sample_test):
    """Test getting test for taking (without answers)"""
    # First create a question
    with app.app_context():
        question = Question(
            test_id=sample_test,
            question_text='Sample question?',
            explanation='Sample explanation'
        )
        db.session.add(question)
        db.session.flush()
        
        option1 = Option(question_id=question.id, option_text='A', is_correct=False)
        option2 = Option(question_id=question.id, option_text='B', is_correct=True)
        db.session.add_all([option1, option2])
        db.session.commit()
    
    response = client.get(f'/api/tests/{sample_test}/take')
    assert response.status_code == 200
    data = response.get_json()
    assert 'questions' in data
    # Verify correct answers are not exposed
    for question in data['questions']:
        for option in question['options']:
            assert 'is_correct' not in option

def test_submit_test(client, sample_test):
    """Test submitting test answers"""
    # Create a question with options
    with app.app_context():
        question = Question(
            test_id=sample_test,
            question_text='Sample question?',
            explanation='This is why B is correct'
        )
        db.session.add(question)
        db.session.flush()
        
        option1 = Option(question_id=question.id, option_text='A', is_correct=False, order=0)
        option2 = Option(question_id=question.id, option_text='B', is_correct=True, order=1)
        db.session.add_all([option1, option2])
        db.session.commit()
        
        question_id = question.id
        correct_option_id = option2.id
    
    # Submit correct answer
    response = client.post(f'/api/tests/{sample_test}/submit', json={
        'student_name': 'Test Student',
        'answers': {str(question_id): correct_option_id}
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['score'] == 100.0
    assert data['correct_answers'] == 1
    assert data['total_questions'] == 1
    assert 'detailed_results' in data
    assert len(data['detailed_results']) == 1

def test_submit_test_with_wrong_answer(client, sample_test):
    """Test submitting test with wrong answer shows explanation"""
    # Create a question with options
    with app.app_context():
        question = Question(
            test_id=sample_test,
            question_text='Sample question?',
            explanation='This is why B is correct'
        )
        db.session.add(question)
        db.session.flush()
        
        option1 = Option(question_id=question.id, option_text='A', is_correct=False, order=0)
        option2 = Option(question_id=question.id, option_text='B', is_correct=True, order=1)
        db.session.add_all([option1, option2])
        db.session.commit()
        
        question_id = question.id
        wrong_option_id = option1.id
    
    # Submit wrong answer
    response = client.post(f'/api/tests/{sample_test}/submit', json={
        'student_name': 'Test Student',
        'answers': {str(question_id): wrong_option_id}
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['score'] == 0.0
    assert data['correct_answers'] == 0
    
    # Check that explanation is provided for wrong answer
    result = data['detailed_results'][0]
    assert result['is_correct'] is False
    assert result['explanation'] == 'This is why B is correct'
    assert result['correct_option_text'] is not None
