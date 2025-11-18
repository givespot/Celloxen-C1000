#!/bin/bash

# Create a hybrid version: Complete portal + Enhanced dashboard (no animations)
cp index.html.full_original index.html.hybrid

# Extract just the enhanced dashboard component (static version)
# We'll keep your original PatientManagement, AssessmentSystem, etc. and just upgrade the dashboard

echo "Creating hybrid version with full portal + enhanced dashboard..."

# Replace only the ClinicDashboard component while keeping everything else
sed -i '/\/\/ Enhanced Dashboard Component with Interactive Widgets/,/^        };$/c\
        \/\/ Enhanced Dashboard Component (Static Version)\
        const ClinicDashboard = () => {\
            const [stats, setStats] = useState({\
                total_patients: 0,\
                todays_appointments: 3,\
                pending_assessments: 2,\
                active_therapy_plans: 5,\
                monthly_revenue: 15420,\
                completion_rate: 87,\
                satisfaction_score: 94,\
                new_patients_this_week: 4\
            });\
            const [currentTime, setCurrentTime] = useState(new Date());\
            \
            useEffect(() => {\
                const timer = setInterval(() => setCurrentTime(new Date()), 1000);\
                return () => clearInterval(timer);\
            }, []);\
            \
            useEffect(() => {\
                fetch("/api/v1/patients/stats/overview")\
                    .then(res => res.json())\
                    .then(data => setStats(prevStats => ({ ...prevStats, ...data })))\
                    .catch(err => console.error(err));\
            }, []);\
            \
            const AnimatedCounter = ({ end, duration = 2000 }) => {\
                const [count, setCount] = useState(0);\
                useEffect(() => {\
                    let startTime;\
                    const animate = (timestamp) => {\
                        if (!startTime) startTime = timestamp;\
                        const progress = Math.min((timestamp - startTime) / duration, 1);\
                        setCount(Math.floor(progress * end));\
                        if (progress < 1) requestAnimationFrame(animate);\
                    };\
                    requestAnimationFrame(animate);\
                }, [end, duration]);\
                return React.createElement("span", null, count);\
            };\
            \
            return (\
                React.createElement("div", null,\
                    React.createElement("div", { className: "mb-8 flex justify-between items-start" },\
                        React.createElement("div", null,\
                            React.createElement("h1", { className: "text-4xl font-bold text-gray-900 mb-2" }, "Enhanced Clinic Dashboard"),\
                            React.createElement("p", { className: "text-xl text-gray-600" }, "Aberdeen Wellness Centre • Your comprehensive overview")\
                        ),\
                        React.createElement("div", { className: "bg-white rounded-xl shadow-md p-4 text-center border-l-4 border-indigo-500" },\
                            React.createElement("div", { className: "text-2xl font-bold text-gray-900" }, currentTime.toLocaleTimeString()),\
                            React.createElement("div", { className: "text-sm text-gray-500" }, currentTime.toLocaleDateString())\
                        )\
                    ),\
                    React.createElement("div", { className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8" },\
                        React.createElement("div", { className: "bg-white p-6 rounded-xl shadow-md hover:shadow-lg" },\
                            React.createElement("div", { className: "flex items-center" },\
                                React.createElement("div", { className: "p-3 rounded-lg bg-blue-100 mr-4" },\
                                    React.createElement("i", { className: "fas fa-users text-blue-600 text-xl" })\
                                ),\
                                React.createElement("div", { className: "flex-1" },\
                                    React.createElement("h3", { className: "text-gray-500 text-sm font-medium" }, "Total Patients"),\
                                    React.createElement("p", { className: "text-3xl font-bold text-gray-900" }, React.createElement(AnimatedCounter, { end: stats.total_patients || 0 })),\
                                    React.createElement("div", { className: "text-sm text-green-600" }, "+12% this month")\
                                )\
                            )\
                        ),\
                        React.createElement("div", { className: "bg-white p-6 rounded-xl shadow-md hover:shadow-lg" },\
                            React.createElement("div", { className: "flex items-center" },\
                                React.createElement("div", { className: "p-3 rounded-lg bg-green-100 mr-4" },\
                                    React.createElement("i", { className: "fas fa-calendar-check text-green-600 text-xl" })\
                                ),\
                                React.createElement("div", null,\
                                    React.createElement("h3", { className: "text-gray-500 text-sm font-medium" }, "Today\\'s Appointments"),\
                                    React.createElement("p", { className: "text-3xl font-bold text-gray-900" }, React.createElement(AnimatedCounter, { end: stats.todays_appointments || 3 })),\
                                    React.createElement("p", { className: "text-sm text-blue-600" }, "Scheduled today")\
                                )\
                            )\
                        ),\
                        React.createElement("div", { className: "bg-white p-6 rounded-xl shadow-md hover:shadow-lg" },\
                            React.createElement("div", { className: "flex items-center" },\
                                React.createElement("div", { className: "p-3 rounded-lg bg-purple-100 mr-4" },\
                                    React.createElement("i", { className: "fas fa-procedures text-purple-600 text-xl" })\
                                ),\
                                React.createElement("div", null,\
                                    React.createElement("h3", { className: "text-gray-500 text-sm font-medium" }, "Active Therapy Plans"),\
                                    React.createElement("p", { className: "text-3xl font-bold text-gray-900" }, React.createElement(AnimatedCounter, { end: stats.active_therapy_plans || 5 })),\
                                    React.createElement("p", { className: "text-sm text-purple-600" }, "In progress")\
                                )\
                            )\
                        ),\
                        React.createElement("div", { className: "bg-white p-6 rounded-xl shadow-md hover:shadow-lg" },\
                            React.createElement("div", { className: "flex items-center" },\
                                React.createElement("div", { className: "p-3 rounded-lg bg-orange-100 mr-4" },\
                                    React.createElement("i", { className: "fas fa-pound-sign text-orange-600 text-xl" })\
                                ),\
                                React.createElement("div", null,\
                                    React.createElement("h3", { className: "text-gray-500 text-sm font-medium" }, "Monthly Revenue"),\
                                    React.createElement("p", { className: "text-3xl font-bold text-gray-900" }, "£", React.createElement(AnimatedCounter, { end: stats.monthly_revenue || 15420 })),\
                                    React.createElement("p", { className: "text-sm text-green-600" }, "+8% vs last month")\
                                )\
                            )\
                        )\
                    ),\
                    React.createElement("div", { className: "grid grid-cols-1 lg:grid-cols-2 gap-6" },\
                        React.createElement("div", { className: "bg-white p-6 rounded-xl shadow-md" },\
                            React.createElement("h3", { className: "text-lg font-semibold text-gray-900 mb-4 flex items-center" },\
                                React.createElement("i", { className: "fas fa-clock mr-2 text-indigo-600" }),\
                                "Quick Actions"\
                            ),\
                            React.createElement("div", { className: "flex flex-col gap-3" },\
                                React.createElement("button", {\
                                    onClick: () => window.setCurrentPage("patients"),\
                                    className: "w-full bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white py-3 px-4 rounded-lg font-medium text-left"\
                                }, React.createElement("i", { className: "fas fa-user-plus mr-3" }), "Register New Patient"),\
                                React.createElement("button", {\
                                    onClick: () => window.setCurrentPage("assessments"),\
                                    className: "w-full bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white py-3 px-4 rounded-lg font-medium text-left"\
                                }, React.createElement("i", { className: "fas fa-clipboard-check mr-3" }), "Start Health Assessment"),\
                                React.createElement("button", {\
                                    onClick: () => window.setCurrentPage("appointments"),\
                                    className: "w-full bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 text-white py-3 px-4 rounded-lg font-medium text-left"\
                                }, React.createElement("i", { className: "fas fa-calendar-plus mr-3" }), "Schedule Appointment"),\
                                React.createElement("button", {\
                                    onClick: () => window.setCurrentPage("reports"),\
                                    className: "w-full bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white py-3 px-4 rounded-lg font-medium text-left"\
                                }, React.createElement("i", { className: "fas fa-chart-bar mr-3" }), "View Reports")\
                            )\
                        ),\
                        React.createElement("div", { className: "bg-white p-6 rounded-xl shadow-md" },\
                            React.createElement("h3", { className: "text-lg font-semibold text-gray-900 mb-4" }, "Today\\'s Schedule"),\
                            React.createElement("div", { className: "space-y-3" },\
                                React.createElement("div", { className: "flex items-center p-3 bg-blue-50 rounded-lg" },\
                                    React.createElement("div", { className: "w-3 h-3 bg-blue-500 rounded-full mr-3" }),\
                                    React.createElement("div", { className: "flex-1" },\
                                        React.createElement("p", { className: "text-sm font-medium" }, "09:00 - Health Assessment"),\
                                        React.createElement("p", { className: "text-xs text-gray-500" }, "John Smith - Initial consultation")\
                                    )\
                                ),\
                                React.createElement("div", { className: "flex items-center p-3 bg-green-50 rounded-lg" },\
                                    React.createElement("div", { className: "w-3 h-3 bg-green-500 rounded-full mr-3" }),\
                                    React.createElement("div", { className: "flex-1" },\
                                        React.createElement("p", { className: "text-sm font-medium" }, "11:30 - Therapy Session"),\
                                        React.createElement("p", { className: "text-xs text-gray-500" }, "Session 5 - C-102 Metabolic Balance")\
                                    )\
                                ),\
                                React.createElement("div", { className: "flex items-center p-3 bg-orange-50 rounded-lg" },\
                                    React.createElement("div", { className: "w-3 h-3 bg-orange-500 rounded-full mr-3" }),\
                                    React.createElement("div", { className: "flex-1" },\
                                        React.createElement("p", { className: "text-sm font-medium" }, "14:00 - Follow-up Assessment"),\
                                        React.createElement("p", { className: "text-xs text-gray-500" }, "Progress review appointment")\
                                    )\
                                )\
                            )\
                        )\
                    )\
                )\
            );\
        };' index.html.hybrid
