const { useState, useEffect } = React;

// Sidebar Component
const Sidebar = ({ activeItem = 'assessments' }) => {
    const menuItems = [
        { id: 'dashboard', icon: 'fa-th-large', label: 'Dashboard', href: '/enhanced_dashboard.html' },
        { id: 'patients', icon: 'fa-users', label: 'Patients', href: '/patients.html' },
        { id: 'assessments', icon: 'fa-clipboard-list', label: 'Assessments', href: '/assessments.html' },
        { id: 'iridology', icon: 'fa-eye', label: 'Iridology', href: '/iridology.html' },
        { id: 'appointments', icon: 'fa-calendar-alt', label: 'Appointments', href: '/appointments.html' },
        { id: 'therapies', icon: 'fa-hand-holding-medical', label: 'Therapies', href: '/therapies.html' },
        { id: 'invoices', icon: 'fa-file-invoice-dollar', label: 'Patient Invoices', href: '/clinic_invoices.html' },
        { id: 'settings', icon: 'fa-cog', label: 'Settings', href: '/settings.html' }
    ];

    return (
        <div className="w-56 bg-white h-screen fixed left-0 top-0 shadow-lg flex flex-col">
            <div className="p-5 border-b border-gray-100">
                <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
                        <i className="fas fa-heartbeat text-white text-sm"></i>
                    </div>
                    <span className="text-lg font-bold text-gray-800">Celloxen</span>
                </div>
            </div>
            <nav className="flex-1 py-4 overflow-y-auto">
                {menuItems.map(item => (
                    <a
                        key={item.id}
                        href={item.href}
                        className={`flex items-center px-5 py-3 mx-2 rounded-lg transition-all duration-200 ${
                            activeItem === item.id
                                ? 'bg-indigo-50 text-indigo-600 font-medium'
                                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                        }`}
                    >
                        <i className={`fas ${item.icon} w-5 text-center mr-3 ${
                            activeItem === item.id ? 'text-indigo-600' : 'text-gray-400'
                        }`}></i>
                        <span className="text-sm">{item.label}</span>
                    </a>
                ))}
            </nav>
            <div className="p-4 border-t border-gray-100">
                <a href="/" className="flex items-center px-3 py-2 text-gray-600 hover:text-red-600 transition-colors rounded-lg hover:bg-red-50">
                    <i className="fas fa-sign-out-alt w-5 text-center mr-3"></i>
                    <span className="text-sm">Logout</span>
                </a>
            </div>
        </div>
    );
};

// Domain badge colors
const getDomainStyle = (domain) => {
    const styles = {
        'vitality_energy': { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200', icon: 'fa-bolt' },
        'comfort_mobility': { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200', icon: 'fa-walking' },
        'circulation_heart': { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200', icon: 'fa-heart' },
        'stress_relaxation': { bg: 'bg-green-50', text: 'text-green-700', border: 'border-green-200', icon: 'fa-spa' },
        'immune_digestive': { bg: 'bg-purple-50', text: 'text-purple-700', border: 'border-purple-200', icon: 'fa-shield-alt' }
    };
    return styles[domain] || { bg: 'bg-gray-50', text: 'text-gray-700', border: 'border-gray-200', icon: 'fa-question' };
};

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
        loadPatients();
        loadQuestions();
    }, []);

    const loadPatients = async () => {
        try {
            const token = localStorage.getItem('token');
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

            if (!response.ok) {
                if (response.status === 401) {
                    setError('Session expired. Please login again.');
                    setTimeout(() => window.location.href = '/', 2000);
                    return;
                }
                throw new Error(`Failed to load patients: ${response.status}`);
            }

            const data = await response.json();
            const patientList = data.patients || data || [];
            if (Array.isArray(patientList)) {
                setPatients(patientList);
            } else {
                setError('Invalid patient data received');
            }
        } catch (error) {
            setError(`Failed to load patients: ${error.message}`);
        }
    };

    const loadQuestions = async () => {
        try {
            const response = await fetch('/api/v1/new-assessment/questions');
            if (!response.ok) {
                throw new Error(`Failed to load questions: ${response.status}`);
            }
            const data = await response.json();
            setQuestions(data.questions || []);
        } catch (error) {
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

    const getDomainCode = (d) => {
        const codes = {
            'vitality_energy': 'C-102',
            'comfort_mobility': 'C-103',
            'circulation_heart': 'C-104',
            'stress_relaxation': 'C-105',
            'immune_digestive': 'C-106'
        };
        return codes[d] || 'C-100';
    };

    const getScoreColor = (s) => s >= 75 ? 'text-green-600' : s >= 50 ? 'text-yellow-600' : 'text-red-600';
    const getProgressBgColor = (s) => s >= 75 ? 'bg-green-500' : s >= 50 ? 'bg-yellow-500' : 'bg-red-500';

    // Start screen - Patient selection
    if (step === 'start') {
        return (
            <div className="min-h-screen bg-gray-50 flex">
                <Sidebar activeItem="assessments" />
                <div className="ml-56 flex-1 p-8">
                    <div className="max-w-2xl mx-auto">
                        <div className="mb-8">
                            <h1 className="text-2xl font-bold text-gray-900">New Wellness Assessment</h1>
                            <p className="text-gray-500 mt-1">Complete a comprehensive 35-question wellness assessment</p>
                        </div>

                        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8">
                            <div className="flex items-center space-x-4 mb-6">
                                <div className="w-14 h-14 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center">
                                    <i className="fas fa-clipboard-list text-white text-2xl"></i>
                                </div>
                                <div>
                                    <h2 className="text-lg font-semibold text-gray-900">Wellness Assessment</h2>
                                    <p className="text-sm text-gray-500">35 questions • ~10 minutes</p>
                                </div>
                            </div>

                            {error && (
                                <div className="mb-6 p-4 bg-red-50 border border-red-100 rounded-lg flex items-center text-red-700">
                                    <i className="fas fa-exclamation-circle mr-3"></i>
                                    <span>{error}</span>
                                </div>
                            )}

                            <div className="mb-6">
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    <i className="fas fa-user mr-2 text-gray-400"></i>
                                    Select Patient
                                </label>
                                {patients.length === 0 ? (
                                    <div className="p-4 bg-gray-50 border border-gray-100 rounded-lg flex items-center">
                                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-indigo-600 mr-3"></div>
                                        <span className="text-gray-600">Loading patients...</span>
                                    </div>
                                ) : (
                                    <select
                                        value={selectedPatient?.id || ''}
                                        onChange={(e) => setSelectedPatient(patients.find(p => p.id === parseInt(e.target.value)))}
                                        className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white text-gray-900 transition-colors"
                                    >
                                        <option value="">Choose a patient...</option>
                                        {patients.map(p => (
                                            <option key={p.id} value={p.id}>
                                                {p.first_name} {p.last_name} - {p.patient_number}
                                            </option>
                                        ))}
                                    </select>
                                )}
                                <p className="mt-2 text-sm text-gray-500">
                                    <i className="fas fa-info-circle mr-1"></i>
                                    {patients.length} patient{patients.length !== 1 ? 's' : ''} available
                                </p>
                            </div>

                            <div className="bg-gray-50 rounded-lg p-4 mb-6">
                                <h3 className="text-sm font-medium text-gray-700 mb-3">Assessment covers:</h3>
                                <div className="grid grid-cols-2 gap-2">
                                    {[
                                        { icon: 'fa-bolt', label: 'Vitality & Energy', color: 'text-amber-600' },
                                        { icon: 'fa-walking', label: 'Comfort & Mobility', color: 'text-blue-600' },
                                        { icon: 'fa-heart', label: 'Circulation & Heart', color: 'text-red-600' },
                                        { icon: 'fa-spa', label: 'Stress & Relaxation', color: 'text-green-600' },
                                        { icon: 'fa-shield-alt', label: 'Immune & Digestive', color: 'text-purple-600' }
                                    ].map(item => (
                                        <div key={item.label} className="flex items-center text-sm text-gray-600">
                                            <i className={`fas ${item.icon} ${item.color} mr-2 w-4`}></i>
                                            {item.label}
                                        </div>
                                    ))}
                                </div>
                            </div>

                            <button
                                onClick={startAssessment}
                                disabled={!selectedPatient || loading}
                                className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-3 px-6 rounded-lg font-medium hover:from-indigo-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center"
                            >
                                {loading ? (
                                    <>
                                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                                        Starting Assessment...
                                    </>
                                ) : (
                                    <>
                                        <i className="fas fa-play mr-2"></i>
                                        Start Assessment
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    // Questions screen
    if (step === 'questions' && questions.length > 0) {
        const q = questions[currentQuestionIndex];
        const progress = ((currentQuestionIndex + 1) / questions.length) * 100;
        const domainStyle = getDomainStyle(q.domain);

        return (
            <div className="min-h-screen bg-gray-50 flex">
                <Sidebar activeItem="assessments" />
                <div className="ml-56 flex-1">
                    {/* Header */}
                    <div className="bg-white border-b border-gray-100 px-8 py-5">
                        <div className="flex justify-between items-start">
                            <div>
                                <h1 className="text-xl font-bold text-gray-900">
                                    Assessment for: {selectedPatient?.first_name} {selectedPatient?.last_name}
                                </h1>
                                <p className="text-sm text-gray-500 mt-1">Question {currentQuestionIndex + 1} of {questions.length}</p>
                            </div>
                            <div className={`flex items-center px-4 py-2 rounded-lg ${domainStyle.bg} ${domainStyle.text} border ${domainStyle.border}`}>
                                <i className={`fas ${domainStyle.icon} mr-2`}></i>
                                <span className="font-medium">{getDomainName(q.domain)}</span>
                                <span className="ml-2 text-xs opacity-75">({getDomainCode(q.domain)})</span>
                            </div>
                        </div>

                        {/* Progress bar */}
                        <div className="mt-4">
                            <div className="flex justify-between text-xs text-gray-500 mb-1">
                                <span>Progress</span>
                                <span>{Math.round(progress)}% Complete</span>
                            </div>
                            <div className="w-full bg-gray-100 rounded-full h-2">
                                <div
                                    className="bg-gradient-to-r from-indigo-500 to-purple-500 h-2 rounded-full transition-all duration-500"
                                    style={{ width: `${progress}%` }}
                                ></div>
                            </div>
                        </div>
                    </div>

                    {/* Question content */}
                    <div className="p-8">
                        <div className="max-w-3xl mx-auto">
                            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8">
                                <h2 className="text-xl font-semibold text-gray-900 mb-8 leading-relaxed">
                                    {q.text}
                                </h2>

                                <div className="space-y-3 mb-8">
                                    {q.options.map((opt, idx) => (
                                        <button
                                            key={idx}
                                            onClick={() => setSelectedAnswer(idx)}
                                            className={`w-full text-left p-4 rounded-xl border-2 transition-all duration-200 hover:shadow-md ${
                                                selectedAnswer === idx
                                                    ? 'border-indigo-500 bg-indigo-50 shadow-sm'
                                                    : 'border-gray-100 bg-white hover:border-gray-200 hover:bg-gray-50'
                                            }`}
                                        >
                                            <div className="flex items-center">
                                                <div className={`w-6 h-6 rounded-full border-2 mr-4 flex items-center justify-center transition-all ${
                                                    selectedAnswer === idx
                                                        ? 'border-indigo-500 bg-indigo-500'
                                                        : 'border-gray-300'
                                                }`}>
                                                    {selectedAnswer === idx && (
                                                        <div className="w-2 h-2 bg-white rounded-full"></div>
                                                    )}
                                                </div>
                                                <span className={`text-base ${
                                                    selectedAnswer === idx ? 'text-indigo-900 font-medium' : 'text-gray-700'
                                                }`}>{opt}</span>
                                            </div>
                                        </button>
                                    ))}
                                </div>

                                {/* Navigation buttons */}
                                <div className="flex justify-between items-center pt-4 border-t border-gray-100">
                                    <button
                                        onClick={() => {
                                            setCurrentQuestionIndex(currentQuestionIndex - 1);
                                            setSelectedAnswer(answers[questions[currentQuestionIndex - 1]?.id] ?
                                                questions[currentQuestionIndex - 1].options.indexOf(answers[questions[currentQuestionIndex - 1].id].text) : null
                                            );
                                        }}
                                        disabled={currentQuestionIndex === 0}
                                        className="flex items-center px-5 py-2.5 text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                                    >
                                        <i className="fas fa-chevron-left mr-2"></i>
                                        Previous
                                    </button>

                                    <div className="flex items-center space-x-1">
                                        {Array.from({ length: Math.min(5, questions.length) }, (_, i) => {
                                            const dotIndex = Math.max(0, Math.min(currentQuestionIndex - 2, questions.length - 5)) + i;
                                            return (
                                                <div
                                                    key={i}
                                                    className={`w-2 h-2 rounded-full transition-all ${
                                                        dotIndex === currentQuestionIndex
                                                            ? 'bg-indigo-500 w-4'
                                                            : dotIndex < currentQuestionIndex
                                                                ? 'bg-indigo-200'
                                                                : 'bg-gray-200'
                                                    }`}
                                                ></div>
                                            );
                                        })}
                                    </div>

                                    <button
                                        onClick={submitAnswer}
                                        disabled={selectedAnswer === null || loading}
                                        className="flex items-center px-6 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all font-medium"
                                    >
                                        {loading ? (
                                            <>
                                                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                                                Saving...
                                            </>
                                        ) : currentQuestionIndex === questions.length - 1 ? (
                                            <>
                                                Complete
                                                <i className="fas fa-check ml-2"></i>
                                            </>
                                        ) : (
                                            <>
                                                Next
                                                <i className="fas fa-chevron-right ml-2"></i>
                                            </>
                                        )}
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    // Results screen
    if (step === 'results' && results) {
        return (
            <div className="min-h-screen bg-gray-50 flex">
                <Sidebar activeItem="assessments" />
                <div className="ml-56 flex-1 p-8">
                    <div className="max-w-4xl mx-auto">
                        {/* Header */}
                        <div className="mb-8">
                            <div className="flex items-center mb-2">
                                <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center mr-3">
                                    <i className="fas fa-check text-green-600"></i>
                                </div>
                                <h1 className="text-2xl font-bold text-gray-900">Assessment Complete!</h1>
                            </div>
                            <p className="text-gray-500 ml-13">
                                Assessment for {selectedPatient?.first_name} {selectedPatient?.last_name}
                            </p>
                        </div>

                        {/* Overall Score Card */}
                        <div className="bg-gradient-to-br from-indigo-600 via-purple-600 to-indigo-700 rounded-2xl p-8 mb-8 text-white shadow-xl">
                            <div className="flex items-center justify-between">
                                <div>
                                    <h2 className="text-lg opacity-90 mb-2">Overall Wellness Score</h2>
                                    <div className="text-6xl font-bold">{results.overall_score}%</div>
                                    <p className="text-sm opacity-75 mt-2">
                                        {results.overall_score >= 75 ? 'Excellent wellness level' :
                                         results.overall_score >= 50 ? 'Moderate wellness level' :
                                         'Needs attention'}
                                    </p>
                                </div>
                                <div className="w-32 h-32 bg-white/10 rounded-full flex items-center justify-center">
                                    <i className={`fas ${
                                        results.overall_score >= 75 ? 'fa-smile-beam' :
                                        results.overall_score >= 50 ? 'fa-meh' :
                                        'fa-frown'
                                    } text-5xl opacity-90`}></i>
                                </div>
                            </div>
                        </div>

                        {/* Domain Scores */}
                        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-8">
                            <h3 className="text-lg font-semibold text-gray-900 mb-6">Domain Scores</h3>
                            <div className="space-y-5">
                                {Object.entries(results.domain_scores).map(([domain, score]) => {
                                    const style = getDomainStyle(domain);
                                    return (
                                        <div key={domain} className="group">
                                            <div className="flex items-center justify-between mb-2">
                                                <div className="flex items-center">
                                                    <div className={`w-8 h-8 ${style.bg} rounded-lg flex items-center justify-center mr-3`}>
                                                        <i className={`fas ${style.icon} ${style.text} text-sm`}></i>
                                                    </div>
                                                    <span className="font-medium text-gray-900">{getDomainName(domain)}</span>
                                                </div>
                                                <span className={`text-2xl font-bold ${getScoreColor(score)}`}>
                                                    {score}%
                                                </span>
                                            </div>
                                            <div className="w-full bg-gray-100 rounded-full h-3 overflow-hidden">
                                                <div
                                                    className={`h-3 rounded-full transition-all duration-1000 ${getProgressBgColor(score)}`}
                                                    style={{ width: `${score}%` }}
                                                ></div>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>

                        {/* Action Buttons */}
                        <div className="flex gap-4">
                            <button
                                onClick={() => {
                                    setStep('start');
                                    setSelectedPatient(null);
                                    setAssessmentId(null);
                                    setResults(null);
                                    setAnswers({});
                                    setCurrentQuestionIndex(0);
                                }}
                                className="flex-1 bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-3 px-6 rounded-lg font-medium hover:from-indigo-700 hover:to-purple-700 transition-all flex items-center justify-center"
                            >
                                <i className="fas fa-plus mr-2"></i>
                                New Assessment
                            </button>
                            <button
                                onClick={() => window.location.href = '/assessments.html'}
                                className="flex-1 border border-indigo-200 text-indigo-600 py-3 px-6 rounded-lg font-medium hover:bg-indigo-50 transition-colors flex items-center justify-center"
                            >
                                <i className="fas fa-list mr-2"></i>
                                View All Assessments
                            </button>
                            <button
                                onClick={() => window.location.href = '/'}
                                className="flex-1 border border-gray-200 text-gray-600 py-3 px-6 rounded-lg font-medium hover:bg-gray-50 transition-colors flex items-center justify-center"
                            >
                                <i className="fas fa-home mr-2"></i>
                                Back to Portal
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    // Loading state
    return (
        <div className="min-h-screen bg-gray-50 flex">
            <Sidebar activeItem="assessments" />
            <div className="ml-56 flex-1 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Loading assessment...</p>
                </div>
            </div>
        </div>
    );
}

ReactDOM.render(<NewAssessmentModule />, document.getElementById('assessment-root'));
