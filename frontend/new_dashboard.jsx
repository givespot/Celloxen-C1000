            return (
                <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8">
                    {/* Header with gradient text */}
                    <div className="mb-12">
                        <div style={{animation: 'fadeInDown 0.6s ease-out'}}>
                            <h1 className="text-5xl font-bold mb-2" style={{background: 'linear-gradient(to right, #60A5FA, #A78BFA, #F472B6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent'}}>
                                Clinic Dashboard
                            </h1>
                            <p className="text-xl text-slate-400">Aberdeen Wellness Centre • Your daily overview</p>
                        </div>
                    </div>

                    {/* Main Stats Grid - 4 columns */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                        {/* Total Patients Card */}
                        <div 
                            className="group relative overflow-hidden rounded-2xl p-6 bg-white/5 backdrop-blur-xl border border-white/20 shadow-xl hover:shadow-2xl transition-all duration-500 transform hover:-translate-y-2"
                            style={{animation: 'fadeInUp 0.6s ease-out'}}
                        >
                            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                            <div className="w-14 h-14 rounded-2xl flex items-center justify-center mb-4 bg-blue-500/20 group-hover:bg-blue-500/30 transition-all duration-300 transform group-hover:scale-110">
                                <i className="fas fa-users text-2xl text-blue-400"></i>
                            </div>
                            <div className="relative z-10">
                                <p className="text-slate-400 text-sm font-medium mb-1">Total Patients</p>
                                <div className="flex items-end justify-between">
                                    <p className="text-4xl font-bold text-white">{stats.total_patients || 0}</p>
                                    <div className="flex items-center gap-1 text-green-400 text-sm font-semibold">
                                        <i className="fas fa-arrow-up"></i> 12%
                                    </div>
                                </div>
                            </div>
                            <div className="absolute -top-10 -right-10 w-32 h-32 rounded-full opacity-5 group-hover:opacity-10 transition-all duration-500 bg-blue-500"></div>
                        </div>

                        {/* Today's Appointments Card */}
                        <div 
                            className="group relative overflow-hidden rounded-2xl p-6 bg-white/5 backdrop-blur-xl border border-white/20 shadow-xl hover:shadow-2xl transition-all duration-500 transform hover:-translate-y-2"
                            style={{animation: 'fadeInUp 0.6s ease-out 100ms'}}
                        >
                            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                            <div className="w-14 h-14 rounded-2xl flex items-center justify-center mb-4 bg-green-500/20 group-hover:bg-green-500/30 transition-all duration-300 transform group-hover:scale-110">
                                <i className="fas fa-calendar-check text-2xl text-green-400"></i>
                            </div>
                            <div className="relative z-10">
                                <p className="text-slate-400 text-sm font-medium mb-1">Today's Appointments</p>
                                <div className="flex items-end justify-between">
                                    <p className="text-4xl font-bold text-white">3</p>
                                    <div className="flex items-center gap-1 text-green-400 text-sm font-semibold">
                                        <i className="fas fa-arrow-up"></i> 8%
                                    </div>
                                </div>
                            </div>
                            <div className="absolute -top-10 -right-10 w-32 h-32 rounded-full opacity-5 group-hover:opacity-10 transition-all duration-500 bg-green-500"></div>
                        </div>

                        {/* Pending Assessments Card */}
                        <div 
                            className="group relative overflow-hidden rounded-2xl p-6 bg-white/5 backdrop-blur-xl border border-white/20 shadow-xl hover:shadow-2xl transition-all duration-500 transform hover:-translate-y-2"
                            style={{animation: 'fadeInUp 0.6s ease-out 200ms'}}
                        >
                            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                            <div className="w-14 h-14 rounded-2xl flex items-center justify-center mb-4 bg-amber-500/20 group-hover:bg-amber-500/30 transition-all duration-300 transform group-hover:scale-110">
                                <i className="fas fa-clipboard-list text-2xl text-amber-400"></i>
                            </div>
                            <div className="relative z-10">
                                <p className="text-slate-400 text-sm font-medium mb-1">Pending Assessments</p>
                                <div className="flex items-end justify-between">
                                    <p className="text-4xl font-bold text-white">{stats.pending_assessments || 2}</p>
                                </div>
                            </div>
                            <div className="absolute -top-10 -right-10 w-32 h-32 rounded-full opacity-5 group-hover:opacity-10 transition-all duration-500 bg-amber-500"></div>
                        </div>

                        {/* Active Therapy Plans Card */}
                        <div 
                            className="group relative overflow-hidden rounded-2xl p-6 bg-white/5 backdrop-blur-xl border border-white/20 shadow-xl hover:shadow-2xl transition-all duration-500 transform hover:-translate-y-2"
                            style={{animation: 'fadeInUp 0.6s ease-out 300ms'}}
                        >
                            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                            <div className="w-14 h-14 rounded-2xl flex items-center justify-center mb-4 bg-purple-500/20 group-hover:bg-purple-500/30 transition-all duration-300 transform group-hover:scale-110">
                                <i className="fas fa-heart-pulse text-2xl text-purple-400"></i>
                            </div>
                            <div className="relative z-10">
                                <p className="text-slate-400 text-sm font-medium mb-1">Active Plans</p>
                                <div className="flex items-end justify-between">
                                    <p className="text-4xl font-bold text-white">{stats.active_therapy_plans || 5}</p>
                                    <div className="flex items-center gap-1 text-green-400 text-sm font-semibold">
                                        <i className="fas fa-arrow-up"></i> 5%
                                    </div>
                                </div>
                            </div>
                            <div className="absolute -top-10 -right-10 w-32 h-32 rounded-full opacity-5 group-hover:opacity-10 transition-all duration-500 bg-purple-500"></div>
                        </div>
                    </div>

                    {/* Main content grid */}
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
                        {/* Quick Actions */}
                        <div className="lg:col-span-1 space-y-4">
                            <div style={{animation: 'fadeInLeft 0.6s ease-out'}}>
                                <h2 className="text-xl font-bold text-white mb-4">Quick Actions</h2>
                            </div>
                            
                            <button
                                onClick={() => window.setCurrentPage('patients')}
                                className="group relative w-full py-4 px-6 rounded-2xl font-semibold text-white transition-all duration-300 transform hover:scale-105 active:scale-95 shadow-lg hover:shadow-2xl overflow-hidden bg-gradient-to-r from-blue-600 to-blue-500"
                                style={{animation: 'fadeInUp 0.6s ease-out 400ms'}}
                            >
                                <div className="absolute inset-0 bg-white opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
                                <div className="relative z-10 flex items-center justify-center gap-3">
                                    <i className="fas fa-user-plus text-lg"></i>
                                    <span>Register Patient</span>
                                </div>
                            </button>

                            <button
                                onClick={() => window.setCurrentPage('assessments')}
                                className="group relative w-full py-4 px-6 rounded-2xl font-semibold text-white transition-all duration-300 transform hover:scale-105 active:scale-95 shadow-lg hover:shadow-2xl overflow-hidden bg-gradient-to-r from-green-600 to-green-500"
                                style={{animation: 'fadeInUp 0.6s ease-out 500ms'}}
                            >
                                <div className="absolute inset-0 bg-white opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
                                <div className="relative z-10 flex items-center justify-center gap-3">
                                    <i className="fas fa-clipboard-check text-lg"></i>
                                    <span>Start Assessment</span>
                                </div>
                            </button>

                            <button
                                onClick={() => window.setCurrentPage('appointments')}
                                className="group relative w-full py-4 px-6 rounded-2xl font-semibold text-white transition-all duration-300 transform hover:scale-105 active:scale-95 shadow-lg hover:shadow-2xl overflow-hidden bg-gradient-to-r from-purple-600 to-purple-500"
                                style={{animation: 'fadeInUp 0.6s ease-out 600ms'}}
                            >
                                <div className="absolute inset-0 bg-white opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
                                <div className="relative z-10 flex items-center justify-center gap-3">
                                    <i className="fas fa-calendar-plus text-lg"></i>
                                    <span>Schedule Appointment</span>
                                </div>
                            </button>

                            <button
                                onClick={() => window.setCurrentPage('therapy-plans')}
                                className="group relative w-full py-4 px-6 rounded-2xl font-semibold text-white transition-all duration-300 transform hover:scale-105 active:scale-95 shadow-lg hover:shadow-2xl overflow-hidden bg-gradient-to-r from-amber-600 to-amber-500"
                                style={{animation: 'fadeInUp 0.6s ease-out 700ms'}}
                            >
                                <div className="absolute inset-0 bg-white opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
                                <div className="relative z-10 flex items-center justify-center gap-3">
                                    <i className="fas fa-briefcase-medical text-lg"></i>
                                    <span>Create Plan</span>
                                </div>
                            </button>
                        </div>

                        {/* Today's Schedule */}
                        <div className="lg:col-span-2">
                            <div style={{animation: 'fadeInRight 0.6s ease-out'}}>
                                <h2 className="text-xl font-bold text-white mb-4">Today's Schedule</h2>
                            </div>
                            
                            <div className="space-y-3">
                                <div className="p-4 rounded-xl bg-blue-500/10 border-l-4 border-blue-500 hover:shadow-md transition-all duration-300 transform hover:translate-x-1" style={{animation: 'fadeInLeft 0.6s ease-out 400ms'}}>
                                    <div className="flex items-center gap-3">
                                        <div className="flex-shrink-0">
                                            <div className="flex items-center justify-center w-10 h-10 rounded-full bg-white shadow-sm">
                                                <i className="fas fa-clipboard-list text-blue-600"></i>
                                            </div>
                                        </div>
                                        <div className="flex-1">
                                            <p className="font-semibold text-white">09:00</p>
                                            <p className="text-sm font-medium text-slate-300">Health Assessment</p>
                                            <p className="text-xs text-slate-400">John Smith • Initial consultation</p>
                                        </div>
                                    </div>
                                </div>

                                <div className="p-4 rounded-xl bg-green-500/10 border-l-4 border-green-500 hover:shadow-md transition-all duration-300 transform hover:translate-x-1" style={{animation: 'fadeInLeft 0.6s ease-out 500ms'}}>
                                    <div className="flex items-center gap-3">
                                        <div className="flex-shrink-0">
                                            <div className="flex items-center justify-center w-10 h-10 rounded-full bg-white shadow-sm">
                                                <i className="fas fa-heart-pulse text-green-600"></i>
                                            </div>
                                        </div>
                                        <div className="flex-1">
                                            <p className="font-semibold text-white">11:30</p>
                                            <p className="text-sm font-medium text-slate-300">Therapy Session</p>
                                            <p className="text-xs text-slate-400">Session 5 • C-102 Metabolic Balance</p>
                                        </div>
                                    </div>
                                </div>

                                <div className="p-4 rounded-xl bg-amber-500/10 border-l-4 border-amber-500 hover:shadow-md transition-all duration-300 transform hover:translate-x-1" style={{animation: 'fadeInLeft 0.6s ease-out 600ms'}}>
                                    <div className="flex items-center gap-3">
                                        <div className="flex-shrink-0">
                                            <div className="flex items-center justify-center w-10 h-10 rounded-full bg-white shadow-sm">
                                                <i className="fas fa-check-circle text-amber-600"></i>
                                            </div>
                                        </div>
                                        <div className="flex-1">
                                            <p className="font-semibold text-white">14:00</p>
                                            <p className="text-sm font-medium text-slate-300">Follow-up Assessment</p>
                                            <p className="text-xs text-slate-400">Progress review appointment</p>
                                        </div>
                                    </div>
                                </div>

                                <div className="p-4 rounded-xl bg-purple-500/10 border-l-4 border-purple-500 hover:shadow-md transition-all duration-300 transform hover:translate-x-1" style={{animation: 'fadeInLeft 0.6s ease-out 700ms'}}>
                                    <div className="flex items-center gap-3">
                                        <div className="flex-shrink-0">
                                            <div className="flex items-center justify-center w-10 h-10 rounded-full bg-white shadow-sm">
                                                <i className="fas fa-user-check text-purple-600"></i>
                                            </div>
                                        </div>
                                        <div className="flex-1">
                                            <p className="font-semibold text-white">16:00</p>
                                            <p className="text-sm font-medium text-slate-300">Patient Consultation</p>
                                            <p className="text-xs text-slate-400">Sarah Johnson • Wellness check</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Recent Patients Activity */}
                    <div className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 backdrop-blur-xl border border-slate-700/50 rounded-3xl p-8" style={{animation: 'fadeInUp 0.6s ease-out 800ms'}}>
                        <h2 className="text-xl font-bold text-white mb-6">Recent Patient Activity</h2>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            <div className="p-4 bg-gradient-to-br from-slate-700/50 to-slate-600/50 border border-slate-600/50 rounded-xl hover:border-slate-500/50 transition-all duration-300 transform hover:scale-105">
                                <div className="flex items-center gap-3 mb-3">
                                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white font-bold">J</div>
                                    <div>
                                        <p className="text-white font-semibold">John Smith</p>
                                        <p className="text-xs text-slate-400">CLX-ABD-00001</p>
                                    </div>
                                </div>
                                <div className="text-xs text-slate-300 space-y-1">
                                    <p>📧 john@example.com</p>
                                    <p>📞 +44 123 456 7890</p>
                                </div>
                            </div>

                            <div className="p-4 bg-gradient-to-br from-slate-700/50 to-slate-600/50 border border-slate-600/50 rounded-xl hover:border-slate-500/50 transition-all duration-300 transform hover:scale-105">
                                <div className="flex items-center gap-3 mb-3">
                                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-green-400 to-blue-500 flex items-center justify-center text-white font-bold">S</div>
                                    <div>
                                        <p className="text-white font-semibold">Sarah Johnson</p>
                                        <p className="text-xs text-slate-400">CLX-ABD-00002</p>
                                    </div>
                                </div>
                                <div className="text-xs text-slate-300 space-y-1">
                                    <p>📧 sarah@example.com</p>
                                    <p>📞 +44 987 654 3210</p>
                                </div>
                            </div>

                            <div className="p-4 bg-gradient-to-br from-slate-700/50 to-slate-600/50 border border-slate-600/50 rounded-xl hover:border-slate-500/50 transition-all duration-300 transform hover:scale-105">
                                <div className="flex items-center gap-3 mb-3">
                                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-amber-400 to-red-500 flex items-center justify-center text-white font-bold">M</div>
                                    <div>
                                        <p className="text-white font-semibold">Mike Brown</p>
                                        <p className="text-xs text-slate-400">CLX-ABD-00003</p>
                                    </div>
                                </div>
                                <div className="text-xs text-slate-300 space-y-1">
                                    <p>📧 mike@example.com</p>
                                    <p>📞 +44 555 666 7777</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* CSS for animations */}
                    <style>{`
                        @keyframes fadeInDown {
                            from {
                                opacity: 0;
                                transform: translateY(-20px);
                            }
                            to {
                                opacity: 1;
                                transform: translateY(0);
                            }
                        }

                        @keyframes fadeInUp {
                            from {
                                opacity: 0;
                                transform: translateY(20px);
                            }
                            to {
                                opacity: 1;
                                transform: translateY(0);
                            }
                        }

                        @keyframes fadeInLeft {
                            from {
                                opacity: 0;
                                transform: translateX(-20px);
                            }
                            to {
                                opacity: 1;
                                transform: translateX(0);
                            }
                        }

                        @keyframes fadeInRight {
                            from {
                                opacity: 0;
                                transform: translateX(20px);
                            }
                            to {
                                opacity: 1;
                                transform: translateX(0);
                            }
                        }
                    `}</style>
                </div>
            );
