// CELLOXEN IRIDOLOGY REPORT DISPLAY FIX
console.log('🔧 Iridology Report Fix Loaded - v1.1 (Security Update)');

// XSS Prevention: HTML entity escaping function
function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
}

// Safely escape object values recursively
function sanitizeObject(obj) {
    if (typeof obj === 'string') return escapeHtml(obj);
    if (typeof obj !== 'object' || obj === null) return obj;
    if (Array.isArray(obj)) return obj.map(item => sanitizeObject(item));
    const sanitized = {};
    for (const [key, value] of Object.entries(obj)) {
        sanitized[key] = sanitizeObject(value);
    }
    return sanitized;
}

// Fixed report display function
async function displayIridologyReport(assessmentId) {
    console.log('📋 Loading iridology report for assessment:', assessmentId);
    
    const loadingElement = document.getElementById('loading-message') || 
                          document.querySelector('.loading') || 
                          document.querySelector('[class*="loading"]') ||
                          document.querySelector('div:contains("Loading")');
    
    const contentElement = document.getElementById('report-content') || 
                          document.querySelector('.report-content') || 
                          document.querySelector('[class*="report"]');
    
    try {
        // Show loading state
        if (loadingElement) {
            loadingElement.innerHTML = '<div class="text-blue-600 text-center p-4"><i class="fas fa-spinner fa-spin mr-2"></i>Loading report data...</div>';
            loadingElement.style.display = 'block';
        }
        
        // Fetch report data from API
        const response = await fetch(`/api/v1/iridology/${assessmentId}/report`);
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status} - ${response.statusText}`);
        }
        
        const rawReportData = await response.json();
        console.log('✅ Report data received:', rawReportData);

        if (!rawReportData.success) {
            throw new Error(rawReportData.error || 'Report generation failed');
        }

        // Sanitize all user-provided data to prevent XSS
        const reportData = sanitizeObject(rawReportData);
        const safeAssessmentId = escapeHtml(String(assessmentId));

        // Create comprehensive report HTML with sanitized data
        const reportHTML = `
            <div class="iridology-report max-w-5xl mx-auto p-6 bg-white">
                <div class="report-header mb-8 text-center border-b pb-6">
                    <h1 class="text-4xl font-bold text-gray-800 mb-3">🔬 Iridology Analysis Report</h1>
                    <div class="text-sm text-gray-500 mb-4">
                        <span class="mr-4">📅 Generated: ${escapeHtml(new Date().toLocaleDateString('en-GB'))}</span>
                        <span class="mr-4">⏰ Time: ${escapeHtml(new Date().toLocaleTimeString('en-GB'))}</span>
                        <span>🏥 Celloxen Health Portal</span>
                    </div>
                </div>

                <div class="patient-info bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
                    <h2 class="text-2xl font-bold mb-4 text-blue-800">👤 Patient Information</h2>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div class="space-y-3">
                            <div><span class="font-semibold">Name:</span> ${reportData.patient.first_name} ${reportData.patient.last_name}</div>
                            <div><span class="font-semibold">Patient ID:</span> ${reportData.patient.patient_number}</div>
                            <div><span class="font-semibold">Date of Birth:</span> ${reportData.patient.date_of_birth || 'Not provided'}</div>
                        </div>
                        <div class="space-y-3">
                            <div><span class="font-semibold">Assessment Date:</span> ${escapeHtml(new Date().toLocaleDateString('en-GB'))}</div>
                            <div><span class="font-semibold">Practitioner:</span> ${reportData.practitioner || 'Dr. Smith'}</div>
                            <div><span class="font-semibold">Report ID:</span> ${safeAssessmentId}</div>
                        </div>
                    </div>
                </div>
                
                <div class="constitutional-analysis bg-green-50 border border-green-200 rounded-lg p-6 mb-8">
                    <h2 class="text-2xl font-bold mb-4 text-green-800">🧬 Constitutional Analysis</h2>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div class="bg-white p-4 rounded border-l-4 border-green-500">
                            <h3 class="font-semibold text-lg mb-2">Constitutional Type</h3>
                            <p class="text-xl text-green-700">${reportData.analysis.constitutional_type || 'Mixed Constitution'}</p>
                            <p class="text-sm text-gray-600 mt-2">Primary inherited characteristics and predispositions</p>
                        </div>
                        <div class="bg-white p-4 rounded border-l-4 border-green-500">
                            <h3 class="font-semibold text-lg mb-2">Constitutional Strength</h3>
                            <p class="text-xl text-green-700">${reportData.analysis.constitutional_strength || 'Moderate Resilience'}</p>
                            <p class="text-sm text-gray-600 mt-2">Overall vitality and recovery capacity</p>
                        </div>
                    </div>
                </div>
                
                <div class="systems-analysis bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-8">
                    <h2 class="text-2xl font-bold mb-4 text-yellow-800">⚙️ System Conditions</h2>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        ${reportData.analysis.systems ? 
                            Object.entries(reportData.analysis.systems).map(([system, condition]) => `
                                <div class="bg-white p-4 rounded border-l-4 border-yellow-500">
                                    <h4 class="font-semibold capitalize text-lg">${system.replace('_', ' ')}</h4>
                                    <p class="text-gray-700 mt-1">${condition}</p>
                                </div>
                            `).join('') : 
                            `<div class="col-span-2 text-center py-8">
                                <p class="text-gray-500">System analysis data will be available after AI processing completes.</p>
                            </div>`
                        }
                    </div>
                </div>
                
                <div class="primary-concerns bg-orange-50 border border-orange-200 rounded-lg p-6 mb-8">
                    <h2 class="text-2xl font-bold mb-4 text-orange-800">⚠️ Areas of Focus</h2>
                    <div class="space-y-3">
                        ${reportData.analysis.primary_concerns ? 
                            reportData.analysis.primary_concerns.map(concern => `
                                <div class="flex items-start bg-white p-4 rounded border-l-4 border-orange-500">
                                    <i class="fas fa-exclamation-triangle text-orange-500 mr-3 mt-1"></i>
                                    <p class="text-gray-700">${concern}</p>
                                </div>
                            `).join('') : 
                            `<div class="text-center py-8">
                                <p class="text-gray-500">No specific concerns identified in current analysis.</p>
                            </div>`
                        }
                    </div>
                </div>
                
                <div class="recommendations bg-purple-50 border border-purple-200 rounded-lg p-6 mb-8">
                    <h2 class="text-2xl font-bold mb-4 text-purple-800">💡 Wellness Recommendations</h2>
                    <div class="space-y-3">
                        ${reportData.analysis.wellness_priorities ? 
                            reportData.analysis.wellness_priorities.map(rec => `
                                <div class="flex items-start bg-white p-4 rounded border-l-4 border-purple-500">
                                    <i class="fas fa-check-circle text-green-500 mr-3 mt-1"></i>
                                    <p class="text-gray-700">${rec}</p>
                                </div>
                            `).join('') : 
                            `<div class="text-center py-8">
                                <p class="text-gray-500">Personalized recommendations will be generated based on your analysis.</p>
                            </div>`
                        }
                    </div>
                </div>
                
                <div class="report-actions text-center mb-8">
                    <div class="space-x-4">
                        <button onclick="window.print()" class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition duration-200">
                            <i class="fas fa-print mr-2"></i>Print Report
                        </button>
                        <button onclick="downloadReportPDF(${assessmentId})" class="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition duration-200">
                            <i class="fas fa-download mr-2"></i>Download PDF
                        </button>
                        <button onclick="history.back()" class="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition duration-200">
                            <i class="fas fa-arrow-left mr-2"></i>Back to Assessments
                        </button>
                    </div>
                </div>
                
                <div class="report-footer text-center pt-6 border-t border-gray-200">
                    <div class="bg-gray-50 p-4 rounded-lg">
                        <p class="text-sm text-gray-600 mb-2">
                            <strong>Medical Disclaimer:</strong> This iridology report is for wellness and educational purposes only.
                        </p>
                        <p class="text-sm text-gray-600">
                            It does not constitute medical diagnosis or treatment advice. Please consult with a qualified healthcare professional for medical concerns.
                        </p>
                        <div class="mt-4 text-xs text-gray-500">
                            <span class="mr-4">🔒 Confidential Medical Information</span>
                            <span class="mr-4">📧 Generated by Celloxen Health Portal</span>
                            <span>🌐 https://celloxen.com</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Hide loading and show report
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }
        
        if (contentElement) {
            contentElement.innerHTML = reportHTML;
            contentElement.style.display = 'block';
        } else {
            // Create content element if it doesn't exist
            const newContentElement = document.createElement('div');
            newContentElement.id = 'report-content';
            newContentElement.innerHTML = reportHTML;
            document.body.appendChild(newContentElement);
        }
        
        console.log('✅ Iridology report displayed successfully');
        
    } catch (error) {
        console.error('❌ Failed to load report:', error);

        // Sanitize error message and assessmentId
        const safeErrorMessage = escapeHtml(error.message);
        const safeAssessmentId = escapeHtml(String(assessmentId));
        const safeTimestamp = escapeHtml(new Date().toLocaleString());

        const errorHTML = `
            <div class="error-message text-center p-8">
                <div class="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md mx-auto">
                    <div class="text-red-600 mb-4">
                        <i class="fas fa-exclamation-triangle text-3xl mb-3"></i>
                        <h3 class="text-lg font-bold">Error Loading Report</h3>
                    </div>
                    <p class="text-red-700 mb-4">${safeErrorMessage}</p>
                    <div class="space-x-3">
                        <button onclick="displayIridologyReport(${safeAssessmentId})" class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700">
                            <i class="fas fa-redo mr-2"></i>Try Again
                        </button>
                        <button onclick="history.back()" class="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700">
                            <i class="fas fa-arrow-left mr-2"></i>Go Back
                        </button>
                    </div>
                    <div class="mt-4 text-xs text-gray-500">
                        <p>Report ID: ${safeAssessmentId}</p>
                        <p>Error Time: ${safeTimestamp}</p>
                    </div>
                </div>
            </div>
        `;
        
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }
        
        if (contentElement) {
            contentElement.innerHTML = errorHTML;
        } else {
            document.body.innerHTML = errorHTML;
        }
    }
}

// PDF Download function
async function downloadReportPDF(assessmentId) {
    try {
        console.log('📥 Downloading PDF for assessment:', assessmentId);
        
        const response = await fetch(`/api/v1/iridology/${assessmentId}/download-pdf`);
        
        if (!response.ok) {
            throw new Error(`PDF Download failed: ${response.status}`);
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `iridology_report_${assessmentId}_${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        console.log('✅ PDF download completed');
        
    } catch (error) {
        console.error('❌ PDF download failed:', error);
        alert('PDF download failed: ' + error.message);
    }
}

// Auto-initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔍 Iridology Report Fix - Page loaded');
    
    // Look for assessment ID in URL
    const urlParams = new URLSearchParams(window.location.search);
    const pathMatch = window.location.pathname.match(/\/(\d+)$/);
    const hashMatch = window.location.hash.match(/assessment_id=(\d+)/);
    
    let assessmentId = null;
    
    if (urlParams.has('assessment_id')) {
        assessmentId = urlParams.get('assessment_id');
    } else if (pathMatch) {
        assessmentId = pathMatch[1];
    } else if (hashMatch) {
        assessmentId = hashMatch[1];
    }
    
    if (assessmentId) {
        console.log(`📋 Auto-loading report for assessment ${assessmentId}`);
        setTimeout(() => {
            displayIridologyReport(assessmentId);
        }, 500);
    } else {
        console.log('ℹ️ No assessment ID found in URL - waiting for manual trigger');
    }
});

// Make functions available globally
window.displayIridologyReport = displayIridologyReport;
window.downloadReportPDF = downloadReportPDF;

console.log('✅ Iridology Report Fix loaded successfully');
