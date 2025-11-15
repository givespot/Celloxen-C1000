// NEW ASSESSMENT MODULE - CLEAN FRONTEND
// One question at a time, no skipping, clear scoring

const { useState, useEffect } = React;

function NewAssessmentModule() {
    const [step, setStep] = useState('start');
    const [patients, setPatients] = useState([]);
    const [selectedPatient, setSelectedPatient] = useState(null);
    const [assessmentId, setAssessmentId] = useState(null);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [allQuestions, setAllQuestions] = useState([]);
    const [selectedAnswer, setSelectedAnswer] = useState(null);
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState(null);
    const [iridologyResults, setIridologyResults] = useState(null);

    useEffect(() => {
        loadPatients();
        loadQuestions();
    }, []);

    const loadPatients = async () => {
        try {
            const response = await fetch('/api/v1/clinic/patients');
            const data = await response.json();
            // Handle both array and object formats
            setPatients(Array.isArray(data) ? data : (data.patients || []));
        } catch (error) {
            console.error('Error loading patients:', error);
        }
    };

    const loadQuestions = async () => {
        try {
            const response = await fetch('/api/v1/new-assessment/questions');
            const data = await response.json();
            
            const questionArray = [];
            Object.entries(data.domains).forEach(([domainKey, domainData]) => {
                domainData.questions.forEach(q => {
                    questionArray.push({
                        ...q,
                        domain: domainKey,
                        domain_name: domainData.domain_name,
                        therapy_code: domainData.therapy_code
                    });
                });
            });
            
            setAllQuestions(questionArray);
        } catch (error) {
            console.error('Error loading questions:', error);
        }
    };

    const startAssessment = async () => {
        if (!selectedPatient) {
            alert('Please select a patient');
            return;
        }

        setLoading(true);
        try {
            const response = await fetch('/api/v1/new-assessment/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    patient_id: selectedPatient.id,
                    clinic_id: 1
                })
            });

            const data = await response.json();
            setAssessmentId(data.assessment_id);
            setStep('questions');
        } catch (error) {
            alert('Error starting assessment: ' + error.message);
        } finally {
            setLoading(false);
        }
    };

    const submitAnswer = async () => {
        if (selectedAnswer === null) {
            alert('Please select an answer');
            return;
        }

        const currentQuestion = allQuestions[currentQuestionIndex];
        setLoading(true);

        try {
            await fetch('/api/v1/new-assessment/answer', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    assessment_id: assessmentId,
                    question_id: currentQuestion.id,
                    answer_text: currentQuestion.options[selectedAnswer],
                    answer_score: currentQuestion.scores[selectedAnswer]
                })
            });

            if (currentQuestionIndex < allQuestions.length - 1) {
                setCurrentQuestionIndex(currentQuestionIndex + 1);
                setSelectedAnswer(null);
            } else {
                // All questions answered, move to iridology
                setStep('iridology');
            }
        } catch (error) {
            alert('Error submitting answer: ' + error.message);
        } finally {
            setLoading(false);
        }
    };

    const completeAssessment = async () => {
        setLoading(true);
        try {
            const response = await fetch(`/api/v1/new-assessment/complete?assessment_id=${assessmentId}`, {
                method: 'POST'
            });

            const data = await response.json();
            setResults(data);
            setStep('results');
        } catch (error) {
            alert('Error completing assessment: ' + error.message);
        } finally {
            setLoading(false);
        }
    };
    
    const handleIridologyComplete = (iridologyData) => {
        setIridologyResults(iridologyData);
        // After iridology, complete the assessment
        completeAssessment();
    };
    
    const skipIridology = () => {
        // Skip iridology and go straight to results
        completeAssessment();
    };

    const currentQuestion = allQuestions[currentQuestionIndex];
    const progress = ((currentQuestionIndex + 1) / allQuestions.length) * 100;

    if (step === 'start') {
        return React.createElement('div', { className: 'max-w-4xl mx-auto p-6' },
            React.createElement('div', { className: 'bg-white rounded-lg shadow-lg p-8' },
                React.createElement('h1', { className: 'text-3xl font-bold text-gray-800 mb-2' }, 'New Health Assessment'),
                React.createElement('p', { className: 'text-gray-600 mb-8' }, '35 questions across 5 wellness domains'),
                
                React.createElement('div', { className: 'mb-6' },
                    React.createElement('label', { className: 'block text-sm font-medium text-gray-700 mb-2' }, 'Select Patient'),
                    React.createElement('select', {
                        className: 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500',
                        value: selectedPatient?.id || '',
                        onChange: (e) => {
                            const patient = patients.find(p => p.id === parseInt(e.target.value));
                            setSelectedPatient(patient);
                        }
                    },
                        React.createElement('option', { value: '' }, 'Choose a patient...'),
                        patients.map(patient =>
                            React.createElement('option', { key: patient.id, value: patient.id },
                                `${patient.first_name} ${patient.last_name} - ${patient.patient_number}`
                            )
                        )
                    )
                ),
                
                selectedPatient && React.createElement('div', { className: 'bg-purple-50 border border-purple-200 rounded-lg p-4 mb-6' },
                    React.createElement('h3', { className: 'font-semibold text-purple-900 mb-2' }, 'Selected Patient:'),
                    React.createElement('p', { className: 'text-purple-800' }, `${selectedPatient.first_name} ${selectedPatient.last_name}`),
                    React.createElement('p', { className: 'text-sm text-purple-600' }, `${selectedPatient.patient_number} • ${selectedPatient.email}`)
                ),
                
                React.createElement('button', {
                    onClick: startAssessment,
                    disabled: !selectedPatient || loading,
                    className: 'w-full bg-purple-600 text-white py-4 rounded-lg font-semibold hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors'
                }, loading ? 'Starting...' : 'Start Assessment')
            )
        );
    }

    if (step === 'iridology') {
        return React.createElement('div', { className: 'min-h-screen bg-gray-50 py-8' },
            React.createElement('div', { className: 'max-w-6xl mx-auto' },
                React.createElement(window.IridologyCaptureComponent, {
                    assessmentId: assessmentId,
                    onComplete: handleIridologyComplete
                }),
                
                // Skip button
                React.createElement('div', { className: 'text-center mt-6' },
                    React.createElement('button', {
                        onClick: skipIridology,
                        className: 'px-6 py-3 text-gray-600 hover:text-gray-800 hover:underline'
                    }, 'Skip Iridology Analysis and View Results →')
                )
            )
        );
    }
    
    if (step === 'questions' && currentQuestion) {
        return React.createElement('div', { className: 'max-w-4xl mx-auto p-6' },
            React.createElement('div', { className: 'bg-white rounded-lg shadow-lg p-8' },
                React.createElement('div', { className: 'mb-6' },
                    React.createElement('div', { className: 'flex justify-between text-sm text-gray-600 mb-2' },
                        React.createElement('span', null, `Question ${currentQuestionIndex + 1} of ${allQuestions.length}`),
                        React.createElement('span', null, `${Math.round(progress)}% Complete`)
                    ),
                    React.createElement('div', { className: 'w-full bg-gray-200 rounded-full h-3' },
                        React.createElement('div', {
                            className: 'bg-purple-600 h-3 rounded-full transition-all duration-300',
                            style: { width: `${progress}%` }
                        })
                    )
                ),
                
                React.createElement('div', { className: 'inline-block bg-purple-100 text-purple-700 px-4 py-2 rounded-full text-sm font-medium mb-4' },
                    `${currentQuestion.domain_name} (${currentQuestion.therapy_code})`
                ),
                
                React.createElement('h2', { className: 'text-2xl font-bold text-gray-800 mb-8' }, currentQuestion.text),
                
                React.createElement('div', { className: 'space-y-3 mb-8' },
                    currentQuestion.options.map((option, index) =>
                        React.createElement('button', {
                            key: index,
                            onClick: () => setSelectedAnswer(index),
                            className: `w-full text-left px-6 py-4 rounded-lg border-2 transition-all ${
                                selectedAnswer === index
                                    ? 'border-purple-600 bg-purple-50 text-purple-900 font-semibold'
                                    : 'border-gray-300 hover:border-purple-400 hover:bg-gray-50'
                            }`
                        },
                            React.createElement('div', { className: 'flex items-center' },
                                React.createElement('div', {
                                    className: `w-5 h-5 rounded-full border-2 mr-4 flex items-center justify-center ${
                                        selectedAnswer === index ? 'border-purple-600 bg-purple-600' : 'border-gray-400'
                                    }`
                                },
                                    selectedAnswer === index && React.createElement('div', { className: 'w-2 h-2 bg-white rounded-full' })
                                ),
                                React.createElement('span', { className: 'text-lg' }, option)
                            )
                        )
                    )
                ),
                
                React.createElement('div', { className: 'flex gap-4' },
                    currentQuestionIndex > 0 && React.createElement('button', {
                        onClick: () => {
                            setCurrentQuestionIndex(currentQuestionIndex - 1);
                            setSelectedAnswer(null);
                        },
                        className: 'px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors'
                    }, '← Previous'),
                    
                    React.createElement('button', {
                        onClick: submitAnswer,
                        disabled: selectedAnswer === null || loading,
                        className: 'flex-1 bg-purple-600 text-white py-3 rounded-lg font-semibold hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors'
                    }, loading ? 'Saving...' : currentQuestionIndex === allQuestions.length - 1 ? 'Complete Assessment' : 'Next Question →')
                )
            )
        );
    }

    if (step === 'results' && results) {
        return React.createElement('div', { className: 'max-w-6xl mx-auto p-6' },
            React.createElement('div', { className: 'bg-white rounded-lg shadow-lg p-8' },
                React.createElement('div', { className: 'text-center mb-8' },
                    React.createElement('h1', { className: 'text-3xl font-bold text-gray-800 mb-2' }, 'Assessment Complete!'),
                    React.createElement('p', { className: 'text-gray-600' }, `${selectedPatient?.first_name} ${selectedPatient?.last_name}`)
                ),
                
                React.createElement('div', { className: 'bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-lg p-8 mb-8 text-center' },
                    React.createElement('h2', { className: 'text-xl font-semibold mb-2' }, 'Overall Wellness Score'),
                    React.createElement('div', { className: 'text-6xl font-bold' }, `${results.overall_wellness_score}%`)
                ),
                
                // Iridology Results (if available)
                iridologyResults && React.createElement('div', { className: 'bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 mb-8 border-2 border-blue-200' },
                    React.createElement('h3', { className: 'text-2xl font-bold text-gray-800 mb-4' }, '🔬 Iridology Analysis'),
                    React.createElement('div', { className: 'grid grid-cols-1 md:grid-cols-2 gap-4' },
                        React.createElement('div', { className: 'bg-white rounded-lg p-4' },
                            React.createElement('p', { className: 'text-sm text-gray-600 mb-1' }, 'Constitutional Type'),
                            React.createElement('p', { className: 'text-xl font-bold text-blue-600' }, iridologyResults.constitutional_type)
                        ),
                        React.createElement('div', { className: 'bg-white rounded-lg p-4' },
                            React.createElement('p', { className: 'text-sm text-gray-600 mb-1' }, 'Constitutional Strength'),
                            React.createElement('p', { className: 'text-xl font-bold text-blue-600' }, iridologyResults.constitutional_strength)
                        )
                    ),
                    iridologyResults.recommendations && React.createElement('div', { className: 'mt-4' },
                        React.createElement('p', { className: 'font-semibold mb-2' }, 'AI Recommendations:'),
                        React.createElement('ul', { className: 'list-disc list-inside space-y-1 text-gray-700' },
                            iridologyResults.recommendations.map((rec, idx) =>
                                React.createElement('li', { key: idx }, rec)
                            )
                        )
                    )
                ),
                
                React.createElement('h3', { className: 'text-2xl font-bold text-gray-800 mb-4' }, 'Domain Scores'),
                React.createElement('div', { className: 'grid grid-cols-1 md:grid-cols-2 gap-6 mb-8' },
                    Object.entries(results.domain_scores).map(([key, domain]) =>
                        React.createElement('div', { key: key, className: 'border rounded-lg p-6' },
                            React.createElement('div', { className: 'flex justify-between items-start mb-3' },
                                React.createElement('div', null,
                                    React.createElement('h4', { className: 'font-semibold text-lg' }, domain.domain_name),
                                    React.createElement('p', { className: 'text-sm text-gray-600' }, domain.therapy_code)
                                ),
                                React.createElement('span', { className: 'text-3xl font-bold text-purple-600' }, `${domain.score}%`)
                            ),
                            React.createElement('div', { className: 'w-full bg-gray-200 rounded-full h-2' },
                                React.createElement('div', {
                                    className: 'bg-purple-600 h-2 rounded-full',
                                    style: { width: `${domain.score}%` }
                                })
                            ),
                            React.createElement('p', { className: 'text-sm text-gray-600 mt-2' },
                                `${domain.questions_answered} of ${domain.total_questions} questions answered`
                            )
                        )
                    )
                ),
                
                React.createElement('div', { className: 'flex gap-4' },
                    React.createElement('button', {
                        onClick: () => window.location.reload(),
                        className: 'flex-1 bg-purple-600 text-white py-3 rounded-lg font-semibold hover:bg-purple-700'
                    React.createElement('button', {                        onClick: async () => {                            const btn = event.target;                            btn.disabled = true;                            btn.textContent = 'Generating...';                            try {                                const response = await fetch(`/api/v1/reports/generate/${assessmentId}`, { method: 'POST' });                                const data = await response.json();                                if (data.success) {                                    window.open(`https://celloxen.com${data.download_url}`, '_blank');                                    btn.textContent = '📄 Download PDF Report';                                } else {                                    alert('Failed to generate report');                                }                            } catch (error) {                                console.error('Error:', error);                                alert('Error generating report');                            } finally {                                btn.disabled = false;                                btn.textContent = '📄 Download PDF Report';                            }                        },                        className: 'flex-1 bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700'                    }, '📄 Download PDF Report'),
                    }, 'New Assessment'),
                    React.createElement('button', {
                        onClick: () => window.location.href = '/assessments',
                        className: 'flex-1 border border-purple-600 text-purple-600 py-3 rounded-lg font-semibold hover:bg-purple-50'
                    }, 'View All Assessments')
                )
            )
        );
    }

    return React.createElement('div', null, 'Loading...');
}

const root = ReactDOM.createRoot(document.getElementById('assessment-root'));
root.render(React.createElement(NewAssessmentModule));
