from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Discipline(db.Model):
    """Model for academic disciplines/subjects"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tests = db.relationship('Test', backref='discipline', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Test(db.Model):
    """Model for tests"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    discipline_id = db.Column(db.Integer, db.ForeignKey('discipline.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    questions = db.relationship('Question', backref='test', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, include_questions=False):
        result = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'discipline_id': self.discipline_id,
            'discipline_name': self.discipline.name if self.discipline else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'question_count': len(self.questions)
        }
        if include_questions:
            result['questions'] = [q.to_dict(include_options=True) for q in self.questions]
        return result

class Question(db.Model):
    """Model for test questions"""
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text)  # Explanation for the correct answer
    order = db.Column(db.Integer, default=0)
    options = db.relationship('Option', backref='question', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, include_options=False):
        result = {
            'id': self.id,
            'test_id': self.test_id,
            'question_text': self.question_text,
            'explanation': self.explanation,
            'order': self.order
        }
        if include_options:
            result['options'] = [o.to_dict() for o in sorted(self.options, key=lambda x: x.order)]
        return result

class Option(db.Model):
    """Model for question options (multiple choice)"""
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    option_text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False, nullable=False)
    order = db.Column(db.Integer, default=0)

    def to_dict(self, include_correct=False):
        result = {
            'id': self.id,
            'question_id': self.question_id,
            'option_text': self.option_text,
            'order': self.order
        }
        if include_correct:
            result['is_correct'] = self.is_correct
        return result

class TestResult(db.Model):
    """Model for storing test results"""
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
    student_name = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Float, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    correct_answers = db.Column(db.Integer, nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    answers = db.relationship('StudentAnswer', backref='test_result', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'test_id': self.test_id,
            'student_name': self.student_name,
            'score': self.score,
            'total_questions': self.total_questions,
            'correct_answers': self.correct_answers,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class StudentAnswer(db.Model):
    """Model for individual student answers"""
    id = db.Column(db.Integer, primary_key=True)
    test_result_id = db.Column(db.Integer, db.ForeignKey('test_result.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    selected_option_id = db.Column(db.Integer, db.ForeignKey('option.id'), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)

    question = db.relationship('Question', foreign_keys=[question_id])
    selected_option = db.relationship('Option', foreign_keys=[selected_option_id])

    def to_dict(self):
        return {
            'id': self.id,
            'question_id': self.question_id,
            'selected_option_id': self.selected_option_id,
            'is_correct': self.is_correct
        }
