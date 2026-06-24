import React, { useState, useEffect } from 'react'
import { useAuraStore } from './store/auraStore'

function App() {
  const { 
    brief, 
    facts, 
    decisions, 
    tasks, 
    deadlines, 
    contexts, 
    login, 
    logout,
    isAuthenticated,
    user,
    toggleTaskStatus,
    createContext,
    fetchBriefToday,
    fetchKnowledge,
    submitBriefFeedback
  } = useAuraStore()

  const [currentView, setCurrentView] = useState<'dashboard' | 'explorer'>('dashboard')
  const [showRawBrief, setShowRawBrief] = useState(false)
  
  // Founder Feedback State
  const [feedbackRating, setFeedbackRating] = useState<'useful' | 'neutral' | 'not_useful' | null>(null)
  const [feedbackComment, setFeedbackComment] = useState('')
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false)
  const [isSubmittingFeedback, setIsSubmittingFeedback] = useState(false)

  // Reset feedback state when brief changes
  useEffect(() => {
    setFeedbackRating(null)
    setFeedbackComment('')
    setFeedbackSubmitted(false)
  }, [brief?.id])

  // Knowledge Explorer State
  const [explorerTab, setExplorerTab] = useState<'facts' | 'decisions' | 'tasks' | 'deadlines' | 'contexts'>('facts')
  const [searchQuery, setSearchQuery] = useState('')
  const [contextFilter, setContextFilter] = useState('all')
  const [dateSort, setDateSort] = useState<'newest' | 'oldest'>('newest')

  // Login Form State
  const [loginEmail, setLoginEmail] = useState('harsha@aura.run')
  const [loginPassword, setLoginPassword] = useState('password123')
  const [loginError, setLoginError] = useState<string | null>(null)
  const [isLoggingIn, setIsLoggingIn] = useState(false)

  // Load initial data on mount/auth change
  useEffect(() => {
    if (isAuthenticated) {
      fetchBriefToday()
      fetchKnowledge()
    }
  }, [isAuthenticated, fetchBriefToday, fetchKnowledge])

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoginError(null)
    setIsLoggingIn(true)
    const success = await login(loginEmail, loginPassword)
    setIsLoggingIn(false)
    if (success) {
      setCurrentView('dashboard')
    } else {
      setLoginError('Invalid email or password')
    }
  }

  const handleLogout = () => {
    logout()
  }

  // Knowledge Explorer Helpers
  const matchesSearch = (text: string) => 
    text.toLowerCase().includes(searchQuery.toLowerCase())

  const matchesContext = (itemContextId?: string) => 
    contextFilter === 'all' || itemContextId === contextFilter

  const sortByDate = <T extends { created_at: string }>(items: T[]) => {
    return [...items].sort((a, b) => {
      const timeA = new Date(a.created_at).getTime()
      const timeB = new Date(b.created_at).getTime()
      return dateSort === 'newest' ? timeB - timeA : timeA - timeB
    })
  }

  // Filtered and Sorted Data for Explorer
  const filteredFacts = sortByDate(
    facts.filter(f => matchesContext(f.context_id) && (matchesSearch(f.entity) || matchesSearch(f.value) || (f.category && matchesSearch(f.category))))
  )

  const filteredDecisions = sortByDate(
    decisions.filter(d => matchesContext(d.context_id) && matchesSearch(d.chosen_option))
  )

  const filteredTasks = sortByDate(
    tasks.filter(t => matchesContext(t.context_id) && matchesSearch(t.task))
  )

  const filteredDeadlines = sortByDate(
    deadlines.filter(dl => matchesContext(dl.context_id) && matchesSearch(dl.title))
  )

  const filteredContexts = sortByDate(
    contexts.filter(c => (contextFilter === 'all' || c.id === contextFilter) && (matchesSearch(c.name) || matchesSearch(c.description)))
  )

  // Navigation Items
  const navItems = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'explorer', label: 'Knowledge Explorer' }
  ]

  // KPI Calculations
  const activeProjectsCount = brief?.structured_brief.active_projects.length || 0
  const openTasksCount = tasks.filter(t => t.status === "pending").length
  const upcomingDeadlinesCount = deadlines.length
  const recentDecisionsCount = decisions.length

  const activeContext = contexts.find(c => c.is_active) || contexts[0]

  // If not authenticated, render Login Screen
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-[#09090b] text-[#f4f4f5] flex items-center justify-center p-6 select-none font-sans">
        <div className="w-full max-w-sm bg-[#0c0c0e] border border-[#1e1e24] rounded-xl p-8 space-y-6 shadow-2xl relative overflow-hidden">
          {/* Top aesthetic color bar */}
          <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-[#a78bfa] to-transparent opacity-60"></div>
          
          <div className="text-center space-y-2">
            <h1 className="text-3xl font-extrabold tracking-widest text-white m-0">AURA</h1>
            <p className="text-xs text-[#71717a]">Your personal cognitive OS</p>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            {loginError && (
              <div className="bg-[rgba(239,68,68,0.1)] border border-red-500/20 text-red-400 text-xs px-3 py-2 rounded-md">
                {loginError}
              </div>
            )}
            
            <div className="space-y-1.5">
              <label htmlFor="email" className="text-xs font-semibold text-[#a1a1aa] uppercase tracking-wider">Email</label>
              <input
                id="email"
                type="email"
                required
                value={loginEmail}
                onChange={(e) => setLoginEmail(e.target.value)}
                className="w-full px-3.5 py-2 bg-[#060608] border border-[#1e1e24] rounded-lg text-sm text-white focus:outline-none focus:border-[#a78bfa] focus:ring-1 focus:ring-[#a78bfa] placeholder-[#71717a] transition-all"
                placeholder="email@example.com"
              />
            </div>

            <div className="space-y-1.5">
              <label htmlFor="password" className="text-xs font-semibold text-[#a1a1aa] uppercase tracking-wider">Password</label>
              <input
                id="password"
                type="password"
                required
                value={loginPassword}
                onChange={(e) => setLoginPassword(e.target.value)}
                className="w-full px-3.5 py-2 bg-[#060608] border border-[#1e1e24] rounded-lg text-sm text-white focus:outline-none focus:border-[#a78bfa] focus:ring-1 focus:ring-[#a78bfa] placeholder-[#71717a] transition-all"
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              disabled={isLoggingIn}
              className="w-full mt-2 bg-white hover:bg-zinc-100 text-zinc-950 font-medium py-2 rounded-lg text-sm transition-all focus:outline-none focus:ring-2 focus:ring-[#a78bfa] focus:ring-offset-2 focus:ring-offset-zinc-950 disabled:opacity-55 flex items-center justify-center cursor-pointer"
            >
              {isLoggingIn ? "Authenticating..." : "Continue"}
            </button>
          </form>

          <div className="text-center">
            <span className="text-[10px] text-[#52525b]">
              Secured by Supabase Auth Flow
            </span>
          </div>
        </div>
      </div>
    )
  }

  // Authenticated Dashboard & Explorer layout
  return (
    <div className="min-h-screen bg-[#09090b] text-[#f4f4f5] flex flex-col md:flex-row font-sans">
      {/* Sidebar Navigation */}
      <aside className="w-full md:w-64 bg-[#0c0c0e] border-b md:border-b-0 md:border-r border-[#1e1e24] p-6 flex flex-col justify-between shrink-0">
        <div>
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-2xl font-extrabold tracking-widest text-white m-0">AURA</h1>
            {activeContext && (
              <span className="text-xs bg-[#1f1f23] text-[#a78bfa] px-2.5 py-1 rounded-full border border-[#2e2e33]">
                {activeContext.name}
              </span>
            )}
          </div>

          {/* Navigation Links */}
          <nav className="space-y-1.5">
            {navItems.map(item => (
              <button
                key={item.id}
                onClick={() => setCurrentView(item.id as any)}
                className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium transition-colors cursor-pointer ${
                  currentView === item.id 
                    ? 'bg-[#18181b] text-white border border-[#27272a]' 
                    : 'text-[#a1a1aa] hover:bg-[#121214] hover:text-[#e4e4e7]'
                }`}
              >
                {item.label}
              </button>
            ))}
          </nav>
        </div>

        {/* User Session Profile */}
        <div className="mt-8 pt-6 border-t border-[#1e1e24] flex items-center justify-between">
          <div className="flex flex-col">
            <span className="text-xs font-semibold text-white">{user?.display_name || "Harsha"}</span>
            <span className="text-[11px] text-[#71717a]">{user?.email || "harsha@aura.run"}</span>
          </div>
          <button 
            onClick={handleLogout}
            className="text-xs text-[#a1a1aa] hover:text-white transition-colors cursor-pointer"
          >
            Logout
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-grow p-6 md:p-10 max-w-5xl mx-auto w-full">
        {currentView === 'dashboard' && (
          <div className="space-y-8 animate-fade-in">
            {/* Greeting Header */}
            <div>
              <h2 className="text-3xl font-semibold tracking-tight text-white">Good Morning Harsha</h2>
              <p className="text-sm text-[#71717a] mt-1">Here is your daily cognitive digest.</p>
            </div>

            {/* KPI Cards Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-[#0c0c0e] border border-[#1e1e24] p-5 rounded-lg flex flex-col justify-between">
                <span className="text-xs font-semibold text-[#71717a] uppercase tracking-wider">Projects</span>
                <span className="text-3xl font-bold text-white mt-2">{activeProjectsCount}</span>
              </div>
              <div className="bg-[#0c0c0e] border border-[#1e1e24] p-5 rounded-lg flex flex-col justify-between">
                <span className="text-xs font-semibold text-[#71717a] uppercase tracking-wider">Tasks</span>
                <span className="text-3xl font-bold text-white mt-2">{openTasksCount}</span>
              </div>
              <div className="bg-[#0c0c0e] border border-[#1e1e24] p-5 rounded-lg flex flex-col justify-between">
                <span className="text-xs font-semibold text-[#71717a] uppercase tracking-wider">Deadlines</span>
                <span className="text-3xl font-bold text-white mt-2">{upcomingDeadlinesCount}</span>
              </div>
              <div className="bg-[#0c0c0e] border border-[#1e1e24] p-5 rounded-lg flex flex-col justify-between">
                <span className="text-xs font-semibold text-[#71717a] uppercase tracking-wider">Decisions</span>
                <span className="text-3xl font-bold text-white mt-2">{recentDecisionsCount}</span>
              </div>
            </div>

            {/* Structured Brief Dashboard */}
            <div className="bg-[#0c0c0e] border border-[#1e1e24] rounded-lg overflow-hidden">
              {/* Header Tab Toggles */}
              <div className="border-b border-[#1e1e24] bg-[#0e0e11] px-6 py-4 flex items-center justify-between">
                <span className="text-sm font-semibold tracking-tight text-white uppercase tracking-wider">Executive Brief</span>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setShowRawBrief(false)}
                    className={`text-xs px-3 py-1.5 rounded transition-all cursor-pointer ${
                      !showRawBrief 
                        ? 'bg-[#18181b] text-white border border-[#27272a]' 
                        : 'text-[#a1a1aa] hover:text-white'
                    }`}
                  >
                    Structured
                  </button>
                  <button
                    onClick={() => setShowRawBrief(true)}
                    className={`text-xs px-3 py-1.5 rounded transition-all cursor-pointer ${
                      showRawBrief 
                        ? 'bg-[#18181b] text-white border border-[#27272a]' 
                        : 'text-[#a1a1aa] hover:text-white'
                    }`}
                  >
                    Raw View
                  </button>
                </div>
              </div>

              {/* Brief Content */}
              <div className="p-6">
                {showRawBrief ? (
                  <pre className="text-sm text-[#d4d4d8] font-mono whitespace-pre-wrap leading-relaxed bg-[#060608] p-4 rounded border border-[#1e1e24]">
                    {brief?.rendered_brief}
                  </pre>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Active Context */}
                    <div className="space-y-2 border-b md:border-b-0 md:border-r border-[#1e1e24] pb-6 md:pb-0 md:pr-6">
                      <h4 className="text-xs font-semibold text-[#71717a] uppercase tracking-wider">Current Context</h4>
                      <p className="text-sm font-medium text-white">{activeContext?.name || "No Active Context"}</p>
                      <p className="text-xs text-[#a1a1aa]">{activeContext?.description}</p>
                    </div>

                    {/* Active Projects */}
                    <div className="space-y-2">
                      <h4 className="text-xs font-semibold text-[#71717a] uppercase tracking-wider">Active Projects</h4>
                      {brief?.structured_brief.active_projects.length ? (
                        <ul className="space-y-1.5 list-none p-0 m-0">
                          {brief.structured_brief.active_projects.map((proj, idx) => (
                            <li key={idx} className="text-sm text-white flex items-center">
                              <span className="h-1.5 w-1.5 rounded-full bg-[#a78bfa] mr-2"></span>
                              {proj}
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="text-xs text-[#71717a]">No active projects.</p>
                      )}
                    </div>

                    <div className="md:col-span-2 border-t border-[#1e1e24] pt-6"></div>

                    {/* Top Priorities */}
                    <div className="space-y-2">
                      <h4 className="text-xs font-semibold text-[#71717a] uppercase tracking-wider">Top Priorities</h4>
                      {brief?.structured_brief.top_priorities.length ? (
                        <ul className="space-y-2 list-none p-0 m-0">
                          {brief.structured_brief.top_priorities.map((item, idx) => (
                            <li key={idx} className="text-sm text-[#e4e4e7] flex items-start">
                              <span className="text-[#a78bfa] mr-2">⚡</span>
                              {item}
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="text-xs text-[#71717a]">No direct priorities.</p>
                      )}
                    </div>

                    {/* Open Tasks */}
                    <div className="space-y-2">
                      <h4 className="text-xs font-semibold text-[#71717a] uppercase tracking-wider">Open Tasks</h4>
                      {tasks.filter(t => t.status === "pending").length ? (
                        <ul className="space-y-2 list-none p-0 m-0">
                          {tasks.filter(t => t.status === "pending").map((task) => (
                            <li key={task.id} className="text-sm text-[#e4e4e7] flex items-center">
                              <input 
                                type="checkbox" 
                                checked={false}
                                onChange={() => toggleTaskStatus(task.id)}
                                className="mr-2 h-4 w-4 rounded border-zinc-700 bg-zinc-950 text-[#8b5cf6] focus:ring-0 focus:ring-offset-0 cursor-pointer"
                              />
                              {task.task}
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="text-xs text-[#71717a]">No pending tasks.</p>
                      )}
                    </div>

                    <div className="md:col-span-2 border-t border-[#1e1e24] pt-6"></div>

                    {/* Upcoming Deadlines */}
                    <div className="space-y-2">
                      <h4 className="text-xs font-semibold text-[#71717a] uppercase tracking-wider">Upcoming Deadlines</h4>
                      {deadlines.length ? (
                        <ul className="space-y-2 list-none p-0 m-0">
                          {deadlines.map((dl) => (
                            <li key={dl.id} className="text-sm text-[#e4e4e7] flex items-center">
                              <span className="text-red-400 mr-2">📅</span>
                              {dl.title} (due {new Date(dl.due_at).toLocaleDateString()})
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="text-xs text-[#71717a]">No upcoming deadlines.</p>
                      )}
                    </div>

                    {/* Recent Decisions */}
                    <div className="space-y-2">
                      <h4 className="text-xs font-semibold text-[#71717a] uppercase tracking-wider">Recent Decisions</h4>
                      {decisions.length ? (
                        <ul className="space-y-2 list-none p-0 m-0">
                          {decisions.map((dec) => (
                            <li key={dec.id} className="text-sm text-[#e4e4e7] flex items-start">
                              <span className="text-[#a78bfa] mr-2">✓</span>
                              {dec.chosen_option}
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="text-xs text-[#71717a]">No decisions logged recently.</p>
                      )}
                    </div>

                    <div className="md:col-span-2 border-t border-[#1e1e24] pt-6"></div>

                    {/* Suggested Next Action */}
                    <div className="md:col-span-2 space-y-2 bg-[#121215] border border-[#27272a] p-4 rounded-lg">
                      <h4 className="text-xs font-semibold text-[#a78bfa] uppercase tracking-wider">Suggested Next Action</h4>
                      {brief?.structured_brief.suggested_next_actions.map((act, idx) => (
                        <div key={idx} className="flex flex-col md:flex-row md:items-center justify-between gap-4 mt-2">
                          <p className="text-sm font-medium text-white">{act}</p>
                          <button className="bg-[#1c1917] hover:bg-[#292524] text-xs font-medium text-white px-3.5 py-1.5 rounded border border-[#44403c] transition-colors self-start md:self-auto cursor-pointer">
                            Action Completed
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Founder Feedback Widget */}
                {brief && (
                  <div className="mt-8 pt-6 border-t border-[#1e1e24] space-y-4">
                    <div className="flex flex-col space-y-1">
                      <h4 className="text-xs font-semibold text-[#71717a] uppercase tracking-wider">Daily Brief Evaluation</h4>
                      <p className="text-[11px] text-[#a1a1aa]">Help AURA learn what information makes your morning better.</p>
                    </div>

                    {feedbackSubmitted ? (
                      <div className="bg-[rgba(16,185,129,0.06)] border border-[#10b981]/20 text-[#10b981] text-xs px-4 py-3 rounded-lg flex items-center justify-between">
                        <span>✓ Feedback recorded in database. Thank you for dogfooding AURA!</span>
                        <button 
                          type="button"
                          onClick={() => setFeedbackSubmitted(false)}
                          className="text-[#a78bfa] hover:text-white underline text-[10px] cursor-pointer bg-transparent border-0 outline-none"
                        >
                          Change rating
                        </button>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        <div className="flex items-center space-x-3">
                          <button
                            type="button"
                            onClick={() => setFeedbackRating('useful')}
                            className={`flex items-center space-x-2 px-3 py-2 rounded-lg border transition-all cursor-pointer text-xs font-medium ${
                              feedbackRating === 'useful'
                                ? 'bg-[rgba(16,185,129,0.1)] border-[#10b981] text-white font-semibold'
                                : 'bg-[#121215] border-[#1e1e24] text-[#a1a1aa] hover:border-[#10b981]/40 hover:text-white'
                            }`}
                          >
                            <span>👍</span>
                            <span>Useful</span>
                          </button>
                          <button
                            type="button"
                            onClick={() => setFeedbackRating('neutral')}
                            className={`flex items-center space-x-2 px-3 py-2 rounded-lg border transition-all cursor-pointer text-xs font-medium ${
                              feedbackRating === 'neutral'
                                ? 'bg-[rgba(245,158,11,0.1)] border-[#f59e0b] text-white font-semibold'
                                : 'bg-[#121215] border-[#1e1e24] text-[#a1a1aa] hover:border-[#f59e0b]/40 hover:text-white'
                            }`}
                          >
                            <span>😐</span>
                            <span>Neutral</span>
                          </button>
                          <button
                            type="button"
                            onClick={() => setFeedbackRating('not_useful')}
                            className={`flex items-center space-x-2 px-3 py-2 rounded-lg border transition-all cursor-pointer text-xs font-medium ${
                              feedbackRating === 'not_useful'
                                ? 'bg-[rgba(239,68,68,0.1)] border-[#ef4444] text-white font-semibold'
                                : 'bg-[#121215] border-[#1e1e24] text-[#a1a1aa] hover:border-[#ef4444]/40 hover:text-white'
                            }`}
                          >
                            <span>👎</span>
                            <span>Not Useful</span>
                          </button>
                        </div>

                        {feedbackRating && (
                          <div className="space-y-3 animate-fade-in">
                            <textarea
                              rows={2}
                              value={feedbackComment}
                              onChange={(e) => setFeedbackComment(e.target.value)}
                              placeholder="Add optional notes (e.g. what was useful or annoying)..."
                              className="w-full px-3 py-2 bg-[#060608] border border-[#1e1e24] rounded-lg text-xs text-white focus:outline-none focus:border-[#a78bfa] focus:ring-1 focus:ring-[#a78bfa] placeholder-[#71717a] transition-all resize-none"
                            />
                            <button
                              type="button"
                              onClick={async () => {
                                setIsSubmittingFeedback(true)
                                const success = await submitBriefFeedback(brief.id, feedbackRating, feedbackComment)
                                setIsSubmittingFeedback(false)
                                if (success) {
                                  setFeedbackSubmitted(true)
                                }
                              }}
                              disabled={isSubmittingFeedback}
                              className="bg-white hover:bg-zinc-100 text-zinc-950 font-semibold px-4 py-1.5 rounded-lg text-xs transition-all disabled:opacity-55 cursor-pointer"
                            >
                              {isSubmittingFeedback ? "Submitting..." : "Submit Feedback"}
                            </button>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Footer info */}
              <div className="bg-[#0e0e11] border-t border-[#1e1e24] px-6 py-4 flex items-center justify-between text-xs text-[#71717a]">
                <span>Last Updated: {brief ? new Date(brief.created_at).toLocaleString() : "Never"}</span>
                <span>Deterministic pipeline V1.0</span>
              </div>
            </div>
          </div>
        )}

        {/* Knowledge Explorer View */}
        {currentView === 'explorer' && (
          <div className="space-y-6 animate-fade-in">
            {/* Page Header */}
            <div>
              <h2 className="text-2xl font-bold tracking-tight text-white m-0">Knowledge Explorer</h2>
              <p className="text-sm text-[#71717a] mt-1">Browse, filter, and search extracted cognitive entities.</p>
            </div>

            {/* Search & Filter Bar */}
            <div className="flex flex-col md:flex-row md:items-center gap-4 bg-[#0c0c0e] border border-[#1e1e24] p-4 rounded-lg">
              {/* Search Bar */}
              <div className="relative flex-grow">
                <span className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-[#71717a]">
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </span>
                <input
                  type="text"
                  placeholder="Search facts, decisions, tasks..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-9 pr-4 py-1.5 bg-[#060608] border border-[#1e1e24] rounded-lg text-sm text-white focus:outline-none focus:border-[#a78bfa] focus:ring-1 focus:ring-[#a78bfa] placeholder-[#71717a] transition-all"
                />
              </div>

              {/* Dropdown Filters */}
              <div className="flex flex-wrap items-center gap-3">
                <div className="flex items-center space-x-1.5">
                  <span className="text-xs font-semibold text-[#71717a] uppercase tracking-wider">Context:</span>
                  <select
                    value={contextFilter}
                    onChange={(e) => setContextFilter(e.target.value)}
                    className="bg-[#060608] border border-[#1e1e24] rounded-lg text-xs text-white px-3 py-1.5 focus:outline-none focus:border-[#a78bfa] cursor-pointer"
                  >
                    <option value="all">All Contexts</option>
                    {contexts.map(ctx => (
                      <option key={ctx.id} value={ctx.id}>{ctx.name}</option>
                    ))}
                  </select>
                </div>
                
                <div className="flex items-center space-x-1.5">
                  <span className="text-xs font-semibold text-[#71717a] uppercase tracking-wider">Sort Date:</span>
                  <select
                    value={dateSort}
                    onChange={(e) => setDateSort(e.target.value as any)}
                    className="bg-[#060608] border border-[#1e1e24] rounded-lg text-xs text-white px-3 py-1.5 focus:outline-none focus:border-[#a78bfa] cursor-pointer"
                  >
                    <option value="newest">Newest First</option>
                    <option value="oldest">Oldest First</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Tabs Row */}
            <div className="border-b border-[#1e1e24] flex space-x-6 text-sm overflow-x-auto scrollbar-none">
              {(['facts', 'decisions', 'tasks', 'deadlines', 'contexts'] as const).map(tab => {
                const getCount = () => {
                  if (tab === 'facts') return filteredFacts.length
                  if (tab === 'decisions') return filteredDecisions.length
                  if (tab === 'tasks') return filteredTasks.length
                  if (tab === 'deadlines') return filteredDeadlines.length
                  return filteredContexts.length
                }
                const label = tab.charAt(0).toUpperCase() + tab.slice(1)
                return (
                  <button
                    key={tab}
                    onClick={() => setExplorerTab(tab)}
                    className={`pb-3 font-medium transition-all border-b-2 relative shrink-0 cursor-pointer ${
                      explorerTab === tab 
                        ? 'border-[#a78bfa] text-white' 
                        : 'border-transparent text-[#71717a] hover:text-[#e4e4e7]'
                    }`}
                  >
                    <span>{label}</span>
                    <span className="ml-1.5 text-xs px-1.5 py-0.5 rounded bg-[#18181b] border border-[#27272a] text-[#a1a1aa]">
                      {getCount()}
                    </span>
                  </button>
                )
              })}
            </div>

            {/* Tab Contents */}
            <div className="mt-4">
              {/* FACTS TAB */}
              {explorerTab === 'facts' && (
                <div className="space-y-4">
                  {filteredFacts.length === 0 ? (
                    <div className="text-center py-12 border border-[#1e1e24] border-dashed rounded-lg text-[#71717a] text-sm bg-[#0c0c0e]">
                      No facts match your filters.
                    </div>
                  ) : (
                    <div className="bg-[#0c0c0e] border border-[#1e1e24] rounded-lg overflow-hidden">
                      <div className="overflow-x-auto">
                        <table className="w-full text-left text-sm border-collapse">
                          <thead>
                            <tr className="border-b border-[#1e1e24] bg-[#0e0e11] text-[#71717a] text-xs font-semibold uppercase tracking-wider">
                              <th className="py-3.5 px-6">Entity</th>
                              <th className="py-3.5 px-6">Fact Value</th>
                              <th className="py-3.5 px-6">Confidence</th>
                              <th className="py-3.5 px-6">Logged</th>
                            </tr>
                          </thead>
                          <tbody>
                            {filteredFacts.map(fact => (
                              <tr key={fact.id} className="border-b border-[#0e0e11] last:border-b-0 hover:bg-[#09090b] transition-colors">
                                <td className="py-4 px-6 font-medium text-white">
                                  <span className="bg-[#18181b] text-[#a78bfa] border border-[#27272a] px-2.5 py-0.5 rounded text-xs">
                                    {fact.entity}
                                  </span>
                                </td>
                                <td className="py-4 px-6 text-[#e4e4e7] max-w-md">{fact.value}</td>
                                <td className="py-4 px-6">
                                  <span className={`text-xs px-2.5 py-0.5 rounded-full border ${
                                    fact.confidence >= 0.9 
                                      ? 'bg-[rgba(16,185,129,0.06)] text-[#10b981] border-[#10b981]/20' 
                                      : 'bg-[rgba(245,158,11,0.06)] text-[#f59e0b] border-[#f59e0b]/20'
                                  }`}>
                                    {Math.round(fact.confidence * 100)}%
                                  </span>
                                </td>
                                <td className="py-4 px-6 text-xs text-[#71717a]">
                                  {new Date(fact.created_at).toLocaleDateString()}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* DECISIONS TAB */}
              {explorerTab === 'decisions' && (
                <div className="space-y-4">
                  {filteredDecisions.length === 0 ? (
                    <div className="text-center py-12 border border-[#1e1e24] border-dashed rounded-lg text-[#71717a] text-sm bg-[#0c0c0e]">
                      No decisions match your filters.
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 gap-4">
                      {filteredDecisions.map(dec => (
                        <div key={dec.id} className="bg-[#0c0c0e] border border-[#1e1e24] p-5 rounded-lg space-y-3 hover:border-zinc-700 transition-colors">
                          <div className="flex items-start justify-between">
                            <p className="text-sm font-medium text-white leading-relaxed">{dec.chosen_option}</p>
                            <span className="text-xs px-2.5 py-0.5 rounded-full border bg-[rgba(16,185,129,0.06)] text-[#10b981] border-[#10b981]/20 shrink-0 ml-4 font-mono">
                              {Math.round(dec.confidence * 100)}% confidence
                            </span>
                          </div>
                          <div className="flex items-center justify-between text-xs text-[#71717a] pt-2 border-t border-[#1e1e24]">
                            <span>Context: {contexts.find(c => c.id === dec.context_id)?.name || "General"}</span>
                            <span>Logged {new Date(dec.created_at).toLocaleDateString()}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* TASKS TAB */}
              {explorerTab === 'tasks' && (
                <div className="space-y-4">
                  {filteredTasks.length === 0 ? (
                    <div className="text-center py-12 border border-[#1e1e24] border-dashed rounded-lg text-[#71717a] text-sm bg-[#0c0c0e]">
                      No tasks match your filters.
                    </div>
                  ) : (
                    <div className="bg-[#0c0c0e] border border-[#1e1e24] rounded-lg overflow-hidden">
                      {filteredTasks.map(task => (
                        <div key={task.id} className="border-b border-[#1e1e24] last:border-b-0 p-4 flex items-center justify-between hover:bg-[#09090b] transition-colors">
                          <div className="flex items-center space-x-3">
                            <input
                              type="checkbox"
                              checked={task.status === "completed"}
                              onChange={() => toggleTaskStatus(task.id)}
                              className="h-4 w-4 rounded border-zinc-700 bg-zinc-950 text-[#8b5cf6] focus:ring-0 focus:ring-offset-0 cursor-pointer"
                            />
                            <span className={`text-sm ${task.status === "completed" ? 'line-through text-[#71717a]' : 'text-[#e4e4e7]'}`}>
                              {task.task}
                            </span>
                          </div>
                          <div className="flex items-center space-x-3 text-xs">
                            <span className={`px-2.5 py-0.5 rounded border text-[10px] font-semibold uppercase tracking-wider ${
                              task.status === "completed" 
                                ? 'bg-zinc-900 text-[#71717a] border-zinc-800' 
                                : 'bg-[#18181b] text-[#a78bfa] border-[#27272a]'
                            }`}>
                              {task.status}
                            </span>
                            <span className="text-[#71717a] font-mono">
                              Priority {task.priority}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* DEADLINES TAB */}
              {explorerTab === 'deadlines' && (
                <div className="space-y-4">
                  {filteredDeadlines.length === 0 ? (
                    <div className="text-center py-12 border border-[#1e1e24] border-dashed rounded-lg text-[#71717a] text-sm bg-[#0c0c0e]">
                      No deadlines match your filters.
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {filteredDeadlines.map(dl => {
                        const isOverdue = new Date(dl.due_at).getTime() < Date.now()
                        return (
                          <div key={dl.id} className="bg-[#0c0c0e] border border-[#1e1e24] p-5 rounded-lg flex flex-col justify-between hover:border-zinc-700 transition-colors">
                            <div>
                              <h4 className="text-sm font-semibold text-white leading-relaxed">{dl.title}</h4>
                              <div className="flex items-center space-x-2 mt-2">
                                <span className="text-xs">📅</span>
                                <span className={`text-xs ${isOverdue ? 'text-red-400 font-medium' : 'text-[#a1a1aa]'}`}>
                                  {isOverdue ? 'Overdue: ' : 'Due: '} {new Date(dl.due_at).toLocaleString()}
                                </span>
                              </div>
                            </div>
                            <div className="flex items-center justify-between text-xs text-[#71717a] pt-4 mt-4 border-t border-[#1e1e24]">
                              <span>Confidence: {Math.round(dl.confidence * 100)}%</span>
                              <span>Logged {new Date(dl.created_at).toLocaleDateString()}</span>
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  )}
                </div>
              )}

              {/* CONTEXTS TAB */}
              {explorerTab === 'contexts' && (
                <div className="space-y-4">
                  {filteredContexts.length === 0 ? (
                    <div className="text-center py-12 border border-[#1e1e24] border-dashed rounded-lg text-[#71717a] text-sm bg-[#0c0c0e]">
                      No contexts match your filters.
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {filteredContexts.map(ctx => (
                        <div key={ctx.id} className={`p-5 rounded-lg border flex flex-col justify-between hover:border-zinc-700 transition-colors ${
                          ctx.is_active 
                            ? 'bg-[#0e0e11] border-[#a78bfa]' 
                            : 'bg-[#0c0c0e] border-[#1e1e24]'
                        }`}>
                          <div>
                            <div className="flex items-center justify-between">
                              <h4 className="text-sm font-semibold text-white">{ctx.name}</h4>
                              {ctx.is_active && (
                                <span className="text-[10px] bg-[rgba(167,139,250,0.15)] text-[#a78bfa] border border-[#a78bfa]/20 px-2.5 py-0.5 rounded-full uppercase tracking-wider font-semibold">
                                  Active Context
                                </span>
                              )}
                            </div>
                            <p className="text-xs text-[#a1a1aa] mt-2 line-clamp-2 leading-relaxed">{ctx.description}</p>
                          </div>
                          <div className="flex items-center justify-between text-xs text-[#71717a] pt-4 mt-4 border-t border-[#1e1e24]">
                            <span>Confidence: {Math.round(ctx.confidence * 100)}%</span>
                            <span>Created {new Date(ctx.created_at).toLocaleDateString()}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
