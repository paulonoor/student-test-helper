// Global variables
let currentTestId = null;

// API Base URL
const API_BASE = '/api';

// Load initial data
document.addEventListener('DOMContentLoaded', () => {
    loadDisciplines();
    loadTests();
});

// Disciplines
async function loadDisciplines() {
    try {
        const response = await fetch(`${API_BASE}/disciplines`);
        const disciplines = await response.json();
        
        // Update disciplines list
        const list = document.getElementById('disciplinesList');
        list.innerHTML = disciplines.map(d => `
            <div class="list-item">
                <div class="list-item-content">
                    <h3>${d.name}</h3>
                    <p>${d.description || 'No description'}</p>
                </div>
                <div class="list-item-actions">
                    <button onclick="deleteDiscipline(${d.id})" class="btn btn-danger">Delete</button>
                </div>
            </div>
        `).join('');
        
        // Update discipline dropdown
        const select = document.getElementById('testDiscipline');
        select.innerHTML = '<option value="">Select Discipline</option>' +
            disciplines.map(d => `<option value="${d.id}">${d.name}</option>`).join('');
            
    } catch (error) {
        console.error('Error loading disciplines:', error);
        alert('Failed to load disciplines');
    }
}

async function createDiscipline() {
    const name = document.getElementById('disciplineName').value.trim();
    const description = document.getElementById('disciplineDescription').value.trim();
    
    if (!name) {
        alert('Please enter a discipline name');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/disciplines`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, description })
        });
        
        if (response.ok) {
            document.getElementById('disciplineName').value = '';
            document.getElementById('disciplineDescription').value = '';
            loadDisciplines();
        } else {
            alert('Failed to create discipline');
        }
    } catch (error) {
        console.error('Error creating discipline:', error);
        alert('Failed to create discipline');
    }
}

async function deleteDiscipline(id) {
    if (!confirm('Are you sure you want to delete this discipline? All associated tests will be deleted.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/disciplines/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            loadDisciplines();
            loadTests();
        } else {
            alert('Failed to delete discipline');
        }
    } catch (error) {
        console.error('Error deleting discipline:', error);
        alert('Failed to delete discipline');
    }
}

// Tests
async function loadTests() {
    try {
        const response = await fetch(`${API_BASE}/tests`);
        const tests = await response.json();
        
        const list = document.getElementById('testsList');
        list.innerHTML = tests.map(t => `
            <div class="list-item">
                <div class="list-item-content">
                    <h3>${t.title}</h3>
                    <p>${t.description || 'No description'}</p>
                    <p><strong>Discipline:</strong> ${t.discipline_name} | <strong>Questions:</strong> ${t.question_count}</p>
                </div>
                <div class="list-item-actions">
                    <button onclick="manageQuestions(${t.id}, '${t.title}')" class="btn btn-primary">Manage Questions</button>
                    <button onclick="deleteTest(${t.id})" class="btn btn-danger">Delete</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading tests:', error);
        alert('Failed to load tests');
    }
}

async function createTest() {
    const title = document.getElementById('testTitle').value.trim();
    const description = document.getElementById('testDescription').value.trim();
    const disciplineId = document.getElementById('testDiscipline').value;
    
    if (!title || !disciplineId) {
        alert('Please enter a test title and select a discipline');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/tests`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                title, 
                description, 
                discipline_id: parseInt(disciplineId) 
            })
        });
        
        if (response.ok) {
            document.getElementById('testTitle').value = '';
            document.getElementById('testDescription').value = '';
            document.getElementById('testDiscipline').value = '';
            loadTests();
        } else {
            alert('Failed to create test');
        }
    } catch (error) {
        console.error('Error creating test:', error);
        alert('Failed to create test');
    }
}

async function deleteTest(id) {
    if (!confirm('Are you sure you want to delete this test?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/tests/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            loadTests();
        } else {
            alert('Failed to delete test');
        }
    } catch (error) {
        console.error('Error deleting test:', error);
        alert('Failed to delete test');
    }
}

// Questions Management
function manageQuestions(testId, testTitle) {
    currentTestId = testId;
    document.getElementById('currentTestTitle').textContent = testTitle;
    document.getElementById('questionsSection').style.display = 'block';
    document.getElementById('disciplinesSection').style.display = 'none';
    document.getElementById('testsSection').style.display = 'none';
    loadQuestions();
}

function hideQuestionsSection() {
    document.getElementById('questionsSection').style.display = 'none';
    document.getElementById('disciplinesSection').style.display = 'block';
    document.getElementById('testsSection').style.display = 'block';
    currentTestId = null;
}

async function loadQuestions() {
    if (!currentTestId) return;
    
    try {
        const response = await fetch(`${API_BASE}/tests/${currentTestId}?include_questions=true`);
        const test = await response.json();
        
        const list = document.getElementById('questionsList');
        if (test.questions.length === 0) {
            list.innerHTML = '<p>No questions yet. Add your first question above.</p>';
        } else {
            list.innerHTML = test.questions.map((q, index) => `
                <div class="question-card">
                    <h3>Question ${index + 1}: ${q.question_text}</h3>
                    <div class="question-options">
                        ${q.options.map(o => `
                            <div class="option-label" style="${o.is_correct ? 'background: #d4edda; font-weight: bold;' : ''}">
                                ${o.is_correct ? '✓' : '•'} ${o.option_text}
                            </div>
                        `).join('')}
                    </div>
                    ${q.explanation ? `<p><strong>Explanation:</strong> ${q.explanation}</p>` : ''}
                    <button onclick="deleteQuestion(${q.id})" class="btn btn-danger" style="margin-top: 10px;">Delete Question</button>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading questions:', error);
        alert('Failed to load questions');
    }
}

async function addQuestion() {
    if (!currentTestId) return;
    
    const questionText = document.getElementById('questionText').value.trim();
    const explanation = document.getElementById('questionExplanation').value.trim();
    
    if (!questionText) {
        alert('Please enter a question');
        return;
    }
    
    // Get options
    const optionTexts = Array.from(document.querySelectorAll('.option-text')).map(input => input.value.trim());
    const correctIndex = parseInt(document.querySelector('input[name="correctOption"]:checked').value);
    
    if (optionTexts.some(text => !text)) {
        alert('Please fill in all options');
        return;
    }
    
    const options = optionTexts.map((text, index) => ({
        option_text: text,
        is_correct: index === correctIndex,
        order: index
    }));
    
    try {
        const response = await fetch(`${API_BASE}/tests/${currentTestId}/questions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question_text: questionText,
                explanation: explanation,
                options: options
            })
        });
        
        if (response.ok) {
            // Clear form
            document.getElementById('questionText').value = '';
            document.getElementById('questionExplanation').value = '';
            document.querySelectorAll('.option-text').forEach(input => input.value = '');
            document.querySelector('input[name="correctOption"][value="0"]').checked = true;
            
            loadQuestions();
        } else {
            alert('Failed to add question');
        }
    } catch (error) {
        console.error('Error adding question:', error);
        alert('Failed to add question');
    }
}

async function deleteQuestion(id) {
    if (!confirm('Are you sure you want to delete this question?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/questions/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            loadQuestions();
        } else {
            alert('Failed to delete question');
        }
    } catch (error) {
        console.error('Error deleting question:', error);
        alert('Failed to delete question');
    }
}
