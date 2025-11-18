const { useState, useEffect } = React;

function NewAssessmentModule() {
    const [step, setStep] = useState('start');
    const [patients, setPatients] = useState([]);
    const [selectedPatient, setSelectedPatient] = useState(null);
    const [assessmentId, setAssessmentId] = useState(null);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [questions, setQuestions] = useState([]);
    const [selectedAnswer, setSelectedAnswer] = useState(null);
    const [answers, setAnswers] = useState({});
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        console.log('Component mounted, loading data...');
        loadPatients();
        loadQuestions();
    }, []);

    const loadPatients = async () => {
        console.log('Loading patients...');
        try {
            const token = localStorage.getItem('token');
            console.log('Token exists:', !!token);
            
            if (!token) {
                setError('Not authenticated. Please login first.');
                window.location.href = '/';
                return;
            }

            const response = await fetch('/api/v1/clinic/patients', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            console.log('Patients API response status:', response.status);

            if (!response.ok) {
                if (response.status === 401) {
                    setError('Session expired. Please login again.');
                    setTimeout(() => window.location.href = '/', 2000);
                    return;
                }
                throw new Error(`Failed to load patients: ${response.status}`);
            }

            const data = await response.json();
            console.log('Patients data received:', data);
            
            const patientList = data.patients || data || [];
            console.log('Patient list:', patientList);
            
            if (Array.isArray(patientList)) {
                setPatients(patientList);
                console.log(`Loaded ${patientList.length} patients`);
            } else {
                console.error('Patients data is not an array:', patientList);
                setError('Invalid patient data received');
            }
        } catch (error) {
            console.error('Error loading patients:', error);
            setError(`Failed to load patients: ${error.message}`);
        }
    };

    const loadQuestions = async () => {
        console.log('Loading questions...');
        try {
            const response = await fetch('/api/v1/new-assessment/questions');
            console.log('Questions API response status:', response.status);

            if (!response.ok) {
                throw new Error(`Failed to load questions: ${response.status}`);
            }

            const data = await response.json();
            console.log('Questions data received:', data);
            
            const questionList = data.questions || [];
            setQuestions(questionList);
            console.log(`Loaded ${questionList.length} questions`);
        } catch (error) {
            console.error('Error loading questions:', error);
            setError(`Failed to load questions: ${error.message}`);
        }
    };

    const startAssessment = async () => {
        if (!selectedPatient) {
            alert('Please select a patient');
            return;
        }

        setLoading(true);
        setError(null);
        try {
            const token = localStorage.getItem('token');
            const userStr = localStorage.getItem('user');
            
            if (!token || !userStr) {
                setError('Not authenticated.');
                setTimeout(() => window.location.href = '/', 2000);
                return;
            }

            const user = JSON.parse(userStr);
            const response = await fetch('/api/v1/new-assessment/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    patient_id: selectedPatient.id,
                    practitioner_id: user.user_id,
                    clinic_id: user.clinic_id
                })
            });

            if (!response.ok) throw new Error('Failed to start');
            const data = await response.json();
            
            setAssessmentId(data.assessment_id);
            setStep('questions');
            setCurrentQuestionIndex(0);
            setSelectedAnswer(null);
        } catch (error) {
            alert(`Error: ${error.message}`);
        } finally {
            setLoading(false);
        }
    };

    const submitAnswer = async () => {
        if (selectedAnswer === null) {
            alert('Please select an answer');
            return;
        }

        const question = questions[currentQuestionIndex];
        const answerText = question.options[selectedAnswer];
        const answerScore = question.scores[selectedAnswer];

        setLoading(true);
        try {
            const token = localStorage.getItem('token');
            await fetch('/api/v1/new-assessment/answer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    assessment_id: assessmentId,
                    question_id: question.id,
                    answer_text: answerText,
                    answer_score: answerScore
                })
            });

            setAnswers(prev => ({
                ...prev,
                [question.id]: { text: answerText, score: answerScore }
            }));

            if (currentQuestionIndex < questions.length - 1) {
                setCurrentQuestionIndex(currentQuestionIndex + 1);
                setSelectedAnswer(null);
            } else {
                completeAssessment();
            }
        } catch (error) {
            alert(`Error: ${error.message}`);
        } finally {
            setLoading(false);
        }
    };

    const completeAssessment = async () => {
        setLoading(true);
        try {
            const token = localStorage.getItem('token');
            const response = await fetch('/api/v1/new-assessment/complete', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ assessment_id: assessmentId })
            });

            const data = await response.json();
            setResults(data);
            setStep('results');
        } catch (error) {
            alert(`Error: ${error.message}`);
        } finally {
            setLoading(false);
        }
    };

    const getDomainName = (d) => {
        const n = {
            'vitality_energy': 'Vitality & Energy',
            'comfort_mobility': 'Comfort & Mobility',
            'circulation_heart': 'Circulation & Heart',
            'stress_relaxation': 'Stress & Relaxation',
            'immune_digestive': 'Immune & Digestive'
        };
        return n[d] || d;
    };

    const getScoreColor = (s) => s >= 75 ? 'text-green-600' : s >= 50 ? 'text-yellow-600' : 'text-red-600';
    const getProgressColor = (s) => s >= 75 ? 'bg-green-500' : s >= 50 ? 'bg-yellow-500' : 'bg-red-500';

    if (step === 'start') {
        return React.createElement('div', { className: 'max-w-2xl mx-auto p-6' },
            React.createElement('div', { className: 'bg-white rounded-lg shadow-lg p-8' },
                React.createElement('h1', { className: 'text-3xl font-bold mb-6' }, 'New Wellness Assessment'),
                React.createElement('p', { className: 'text-gray-600 mb-6' }, 'Complete a 35-question wellness assessment'),
                error && React.createElement('div', { className: 'mb-4 p-4 bg-red-50 border border-red-200 rounded text-red-700' }, error),
                React.createElement('div', { className: 'mb-6' },
                    React.createElement('label', { className: 'block text-sm font-medium mb-2' }, 'Select Patient'),
                    patients.length === 0 ? 
                        React.createElement('div', { className: 'p-4 bg-blue-50 border rounded' },
                            React.createElement('p', null, 'Loading patients...')
                        ) :
                        React.createElement('select', {
                            value: selectedPatient?.id || '',
                            onChange: (e) => setSelectedPatient(patients.find(p => p.id === parseInt(e.target.value))),
                            className: 'w-full px-4 py-2 border rounded focus:ring-2 focus:ring-purple-500'
                        },
                            React.createElement('option', { value: '' }, 'Choose a patient...'),
                            patients.map(p => 
                                React.createElement('option', { key: p.id, value: p.id }, 
                                    `${p.first_name} ${p.last_name} - ${p.patient_number}`
                                )
                            )
                        ),
                    React.createElement('p', { className: 'mt-2 text-sm text-gray-500' }, 
                        `${patients.length} patient${patients.length !== 1 ? 's' : ''} available`
                    )
                ),
                React.createElement('button', {
                    onClick: startAssessment,
                    disabled: !selectedPatient || loading,
                    className: 'w-full bg-purple-600 text-white py-3 rounded hover:bg-purple-700 disabled:opacity-50'
                }, loading ? 'Starting...' : 'Start Assessment')
            )
        );
    }

    if (step === 'questions' && questions.length > 0) {
        const q = questions[currentQuestionIndex];
        const prog = ((currentQuestionIndex + 1) / questions.length) * 100;

        return React.createElement('div', { className: 'max-w-3xl mx-auto p-6' },
            React.createElement('div', { className: 'bg-white rounded-lg shadow-lg p-8' },
                React.createElement('div', { className: 'mb-6' },
                    React.createElement('div', { className: 'flex justify-between text-sm mb-2' },
                        React.createElement('span', null, `Question ${currentQuestionIndex + 1} of ${questions.length}`),
                        React.createElement('span', null, `${Math.round(prog)}% Complete`)
                    ),
                    React.createElement('div', { className: 'w-full bg-gray-200 rounded-full h-2' },
                        React.createElement('div', {
                            className: 'bg-purple-600 h-2 rounded-full',
                            style: { width: `${prog}%` }
                        })
                    )
                ),
                React.createElement('span', { className: 'inline-block bg-purple-100 text-purple-800 text-xs px-3 py-1 rounded-full mb-4' },
                    getDomainName(q.domain)
                ),
                React.createElement('h2', { className: 'text-2xl font-bold mb-6' }, q.text),
                React.createElement('div', { className: 'space-y-3 mb-8' },
                    q.options.map((opt, idx) =>
                        React.createElement('button', {
                            key: idx,
                            onClick: () => setSelectedAnswer(idx),
                            className: `w-full text-left p-4 rounded border-2 ${selectedAnswer === idx ? 'border-purple-600 bg-purple-50' : 'border-gray-200'}`
                        },
                            React.createElement('div', { className: 'flex items-center' },
                                React.createElement('div', {
                                    className: `w-6 h-6 rounded-full border-2 mr-3 flex items-center justify-center ${selectedAnswer === idx ? 'border-purple-600 bg-purple-600' : 'border-gray-300'}`
                                },
                                    selectedAnswer === idx && React.createElement('div', { className: 'w-2 h-2 bg-white rounded-full' })
                                ),
                                React.createElement('span', null, opt)
                            )
                        )
                    )
                ),
                React.createElement('div', { className: 'flex justify-between' },
                    React.createElement('button', {
                        onClick: () => { setCurrentQuestionIndex(currentQuestionIndex - 1); setSelectedAnswer(null); },
                        disabled: currentQuestionIndex === 0,
                        className: 'px-6 py-2 border rounded disabled:opacity-50'
                    }, 'Previous'),
                    React.createElement('button', {
                        onClick: submitAnswer,
                        disabled: selectedAnswer === null || loading,
                        className: 'px-8 py-2 bg-purple-600 text-white rounded disabled:opacity-50'
                    }, loading ? 'Saving...' : (currentQuestionIndex === questions.length - 1 ? 'Complete' : 'Next'))
                )
            )
        );
    }

    if (step === 'results' && results) {
        return React.createElement('div', { className: 'max-w-4xl mx-auto p-6' },
            React.createElement('div', { className: 'bg-white rounded-lg shadow-lg p-8' },
                React.createElement('h1', { className: 'text-3xl font-bold mb-2' }, 'Assessment Complete!'),
                React.createElement('p', { className: 'text-gray-600 mb-8' }, 
                    `Assessment for ${selectedPatient?.first_name} ${selectedPatient?.last_name}`
                ),
                React.createElement('div', { className: 'bg-gradient-to-r from-purple-500 to-purple-700 text-white rounded p-8 mb-8 text-center' },
                    React.createElement('h2', { className: 'text-lg mb-2' }, 'Overall Wellness Score'),
                    React.createElement('div', { className: 'text-6xl font-bold' }, `${results.overall_score}%`)
                ),
                React.createElement('h3', { className: 'text-xl font-bold mb-4' }, 'Domain Scores'),
                React.createElement('div', { className: 'space-y-4' },
                    Object.entries(results.domain_scores).map(([d, s]) =>
                        React.createElement('div', { key: d, className: 'border rounded p-4' },
                            React.createElement('div', { className: 'flex justify-between mb-2' },
                                React.createElement('span', { className: 'font-semibold' }, getDomainName(d)),
                                React.createElement('span', { className: `text-2xl font-bold ${getScoreColor(s)}` }, `${s}%`)
                            ),
                            React.createElement('div', { className: 'w-full bg-gray-200 rounded-full h-3' },
                                React.createElement('div', {
                                    className: `h-3 rounded-full ${getProgressColor(s)}`,
                                    style: { width: `${s}%` }
                                })
                            )
                        )
                    )
                ),
                React.createElement('div', { className: 'mt-8 flex gap-4' },
                    React.createElement('button', {
                        onClick: () => {
                            setStep('start');
                            setSelectedPatient(null);
                            setAssessmentId(null);
                            setResults(null);
                        },
                        className: 'flex-1 bg-purple-600 text-white py-3 rounded'
                    }, 'New Assessment'),
                    React.createElement('button', {
                        onClick: () => window.location.href = '/',
                        className: 'flex-1 border border-purple-600 text-purple-600 py-3 rounded'
                    }, 'Back to Portal')
                )
            )
        );
    }

    return React.createElement('div', { className: 'flex items-center justify-center h-screen' },
        React.createElement('div', { className: 'text-center' },
            React.createElement('div', { className: 'animate-spin rounded-full h-16 w-16 border-b-2 border-purple-600 mx-auto mb-4' }),
            React.createElement('p', null, 'Loading...')
        )
    );
}

ReactDOM.render(React.createElement(NewAssessmentModule), document.getElementById('assessment-root'));
