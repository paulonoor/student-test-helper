from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from models import db, Discipline, Test, Question, Option, TestResult, StudentAnswer
import os

app = Flask(__name__)
CORS(app)

# Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', f'sqlite:///{os.path.join(basedir, "test_helper.db")}')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Routes for serving HTML pages
@app.route('/')
def index():
    """Main page - shows both teacher and student interfaces"""
    return render_template('index.html')

@app.route('/teacher')
def teacher():
    """Teacher interface for creating tests"""
    return render_template('teacher.html')

@app.route('/student')
def student():
    """Student interface for taking tests"""
    return render_template('student.html')

# API Routes for Disciplines
@app.route('/api/disciplines', methods=['GET', 'POST'])
def disciplines():
    """Get all disciplines or create a new one"""
    if request.method == 'GET':
        disciplines = Discipline.query.all()
        return jsonify([d.to_dict() for d in disciplines])
    
    elif request.method == 'POST':
        data = request.json
        discipline = Discipline(
            name=data['name'],
            description=data.get('description', '')
        )
        db.session.add(discipline)
        db.session.commit()
        return jsonify(discipline.to_dict()), 201

@app.route('/api/disciplines/<int:discipline_id>', methods=['GET', 'DELETE'])
def discipline_detail(discipline_id):
    """Get or delete a specific discipline"""
    discipline = Discipline.query.get_or_404(discipline_id)
    
    if request.method == 'GET':
        return jsonify(discipline.to_dict())
    
    elif request.method == 'DELETE':
        db.session.delete(discipline)
        db.session.commit()
        return '', 204

# API Routes for Tests
@app.route('/api/tests', methods=['GET', 'POST'])
def tests():
    """Get all tests or create a new one"""
    if request.method == 'GET':
        discipline_id = request.args.get('discipline_id', type=int)
        if discipline_id:
            tests = Test.query.filter_by(discipline_id=discipline_id).all()
        else:
            tests = Test.query.all()
        return jsonify([t.to_dict() for t in tests])
    
    elif request.method == 'POST':
        data = request.json
        test = Test(
            title=data['title'],
            description=data.get('description', ''),
            discipline_id=data['discipline_id']
        )
        db.session.add(test)
        db.session.commit()
        return jsonify(test.to_dict()), 201

@app.route('/api/tests/<int:test_id>', methods=['GET', 'DELETE'])
def test_detail(test_id):
    """Get or delete a specific test"""
    test = Test.query.get_or_404(test_id)
    
    if request.method == 'GET':
        include_questions = request.args.get('include_questions', 'false').lower() == 'true'
        return jsonify(test.to_dict(include_questions=include_questions))
    
    elif request.method == 'DELETE':
        db.session.delete(test)
        db.session.commit()
        return '', 204

# API Routes for Questions
@app.route('/api/tests/<int:test_id>/questions', methods=['POST'])
def create_question(test_id):
    """Create a new question for a test"""
    test = Test.query.get_or_404(test_id)
    data = request.json
    
    question = Question(
        test_id=test_id,
        question_text=data['question_text'],
        explanation=data.get('explanation', ''),
        order=data.get('order', 0)
    )
    db.session.add(question)
    db.session.flush()  # Get the question ID
    
    # Add options
    for option_data in data.get('options', []):
        option = Option(
            question_id=question.id,
            option_text=option_data['option_text'],
            is_correct=option_data.get('is_correct', False),
            order=option_data.get('order', 0)
        )
        db.session.add(option)
    
    db.session.commit()
    return jsonify(question.to_dict(include_options=True)), 201

@app.route('/api/questions/<int:question_id>', methods=['DELETE'])
def delete_question(question_id):
    """Delete a question"""
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    return '', 204

# API Routes for Taking Tests
@app.route('/api/tests/<int:test_id>/take', methods=['GET'])
def take_test(test_id):
    """Get test with questions for student to take (without showing correct answers)"""
    test = Test.query.get_or_404(test_id)
    
    result = test.to_dict()
    result['questions'] = []
    
    for question in sorted(test.questions, key=lambda q: q.order):
        q_dict = question.to_dict()
        q_dict['options'] = [o.to_dict(include_correct=False) for o in sorted(question.options, key=lambda x: x.order)]
        result['questions'].append(q_dict)
    
    return jsonify(result)

@app.route('/api/tests/<int:test_id>/submit', methods=['POST'])
def submit_test(test_id):
    """Submit test answers and get results with explanations"""
    test = Test.query.get_or_404(test_id)
    data = request.json
    
    student_name = data.get('student_name', 'Anonymous')
    answers = data.get('answers', {})  # {question_id: option_id}
    
    # Calculate score
    total_questions = len(test.questions)
    correct_count = 0
    detailed_results = []
    
    # Create test result
    test_result = TestResult(
        test_id=test_id,
        student_name=student_name,
        total_questions=total_questions,
        correct_answers=0,  # Will update after checking
        score=0.0  # Will update after checking
    )
    db.session.add(test_result)
    db.session.flush()
    
    for question in test.questions:
        selected_option_id = answers.get(str(question.id))
        
        if selected_option_id is None:
            continue
            
        selected_option = Option.query.get(selected_option_id)
        if not selected_option:
            continue
            
        is_correct = selected_option.is_correct
        if is_correct:
            correct_count += 1
        
        # Store student answer
        student_answer = StudentAnswer(
            test_result_id=test_result.id,
            question_id=question.id,
            selected_option_id=selected_option_id,
            is_correct=is_correct
        )
        db.session.add(student_answer)
        
        # Prepare detailed result
        correct_option = next((o for o in question.options if o.is_correct), None)
        question_result = {
            'question_id': question.id,
            'question_text': question.question_text,
            'selected_option_id': selected_option_id,
            'selected_option_text': selected_option.option_text,
            'is_correct': is_correct,
            'correct_option_id': correct_option.id if correct_option else None,
            'correct_option_text': correct_option.option_text if correct_option else None,
            'explanation': question.explanation if not is_correct else None
        }
        detailed_results.append(question_result)
    
    # Update test result with final score
    score = (correct_count / total_questions * 100) if total_questions > 0 else 0
    test_result.correct_answers = correct_count
    test_result.score = score
    
    db.session.commit()
    
    return jsonify({
        'test_result_id': test_result.id,
        'score': score,
        'correct_answers': correct_count,
        'total_questions': total_questions,
        'detailed_results': detailed_results
    })

# API Routes for Results
@app.route('/api/results', methods=['GET'])
def results():
    """Get all test results"""
    results = TestResult.query.order_by(TestResult.completed_at.desc()).all()
    return jsonify([r.to_dict() for r in results])

@app.route('/api/results/<int:result_id>', methods=['GET'])
def result_detail(result_id):
    """Get detailed result"""
    result = TestResult.query.get_or_404(result_id)
    return jsonify(result.to_dict())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
