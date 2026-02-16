// Global variables
let currentTest = null;

// API Base URL
const API_BASE = '/api';

// Constants
const SCORE_PRECISION = 1;

// Helper function to escape HTML and prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Load initial data
document.addEventListener('DOMContentLoaded', () => {
    loadDisciplines();
    loadTests();
});

// Load disciplines for filter
async function loadDisciplines() {
    try {
        const response = await fetch(`${API_BASE}/disciplines`);
        const disciplines = await response.json();
        
        const select = document.getElementById('filterDiscipline');
        select.innerHTML = '<option value="">All Disciplines</option>' +
            disciplines.map(d => `<option value="${d.id}">${escapeHtml(d.name)}</option>`).join('');
            
    } catch (error) {
        console.error('Error loading disciplines:', error);
    }
}

// Load available tests
async function loadTests() {
    try {
        const disciplineId = document.getElementById('filterDiscipline').value;
        let url = `${API_BASE}/tests`;
        if (disciplineId) {
            url += `?discipline_id=${disciplineId}`;
        }
        
        const response = await fetch(url);
        const tests = await response.json();
        
        const list = document.getElementById('availableTestsList');
        if (tests.length === 0) {
            list.innerHTML = '<p>No tests available</p>';
        } else {
            list.innerHTML = tests.map(t => `
                <div class="list-item">
                    <div class="list-item-content">
                        <h3>${escapeHtml(t.title)}</h3>
                        <p>${escapeHtml(t.description || 'No description')}</p>
                        <p><strong>Discipline:</strong> ${escapeHtml(t.discipline_name)} | <strong>Questions:</strong> ${t.question_count}</p>
                    </div>
                    <div class="list-item-actions">
                        <button class="btn btn-primary take-test-btn" data-test-id="${t.id}">Take Test</button>
                    </div>
                </div>
            `).join('');
            
            // Attach event listeners
            document.querySelectorAll('.take-test-btn').forEach(btn => {
                btn.addEventListener('click', function() {
                    startTest(parseInt(this.dataset.testId));
                });
            });
        }
    } catch (error) {
        console.error('Error loading tests:', error);
        alert('Failed to load tests');
    }
}

// Start taking a test
async function startTest(testId) {
    const studentName = document.getElementById('studentName').value.trim();
    
    if (!studentName) {
        alert('Please enter your name before taking a test');
        document.getElementById('studentName').focus();
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/tests/${testId}/take`);
        currentTest = await response.json();
        
        if (currentTest.questions.length === 0) {
            alert('This test has no questions yet');
            return;
        }
        
        // Hide tests list and show test form
        document.getElementById('testsListSection').style.display = 'none';
        document.getElementById('takeTestSection').style.display = 'block';
        
        // Populate test info
        document.getElementById('testTitle').textContent = currentTest.title;
        document.getElementById('testDescription').textContent = currentTest.description || '';
        
        // Populate questions
        const container = document.getElementById('questionsContainer');
        container.innerHTML = currentTest.questions.map((q, index) => `
            <div class="question-card">
                <h3>Question ${index + 1}</h3>
                <p>${escapeHtml(q.question_text)}</p>
                <div class="question-options">
                    ${q.options.map(o => `
                        <label class="option-label">
                            <input type="radio" name="question_${q.id}" value="${o.id}" required>
                            <span>${escapeHtml(o.option_text)}</span>
                        </label>
                    `).join('')}
                </div>
            </div>
        `).join('');
        
        // Setup form submission
        document.getElementById('testForm').onsubmit = submitTest;
        
    } catch (error) {
        console.error('Error starting test:', error);
        alert('Failed to load test');
    }
}

// Submit test
async function submitTest(event) {
    event.preventDefault();
    
    if (!currentTest) return;
    
    const studentName = document.getElementById('studentName').value.trim();
    
    // Collect answers
    const answers = {};
    currentTest.questions.forEach(q => {
        const selected = document.querySelector(`input[name="question_${q.id}"]:checked`);
        if (selected) {
            answers[q.id] = parseInt(selected.value);
        }
    });
    
    // Check if all questions are answered
    if (Object.keys(answers).length !== currentTest.questions.length) {
        alert('Please answer all questions before submitting');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/tests/${currentTest.id}/submit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                student_name: studentName,
                answers: answers
            })
        });
        
        const results = await response.json();
        
        // Hide test form and show results
        document.getElementById('takeTestSection').style.display = 'none';
        document.getElementById('resultsSection').style.display = 'block';
        
        // Display results
        displayResults(results);
        
    } catch (error) {
        console.error('Error submitting test:', error);
        alert('Failed to submit test');
    }
}

// Display test results
function displayResults(results) {
    // Display score
    document.getElementById('scoreDisplay').textContent = `${results.score.toFixed(SCORE_PRECISION)}%`;
    document.getElementById('correctCount').textContent = results.correct_answers;
    document.getElementById('totalCount').textContent = results.total_questions;
    
    // Display detailed results
    const container = document.getElementById('detailedResults');
    container.innerHTML = results.detailed_results.map((result, index) => {
        const isCorrect = result.is_correct;
        return `
            <div class="result-item ${isCorrect ? 'correct' : 'incorrect'}">
                <h4>Question ${index + 1}: ${escapeHtml(result.question_text)}</h4>
                <p><strong>Your answer:</strong> <span class="${isCorrect ? 'correct-answer' : 'incorrect-answer'}">${escapeHtml(result.selected_option_text)}</span></p>
                ${!isCorrect ? `
                    <p><strong>Correct answer:</strong> <span class="correct-answer">${escapeHtml(result.correct_option_text)}</span></p>
                    ${result.explanation ? `
                        <div class="explanation">
                            <strong>Explanation:</strong> ${escapeHtml(result.explanation)}
                        </div>
                    ` : ''}
                ` : '<p class="correct-answer">✓ Correct!</p>'}
            </div>
        `;
    }).join('');
}

// Back to tests list
function backToTestsList() {
    document.getElementById('testsListSection').style.display = 'block';
    document.getElementById('takeTestSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'none';
    currentTest = null;
    loadTests();
}
