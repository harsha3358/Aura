import { create } from 'zustand'

export interface User {
  id: string
  email: string
  display_name: string
  timezone: string
  onboarding_completed: boolean
}

export interface FactItem {
  id: string
  entity: string
  value: string
  confidence: number
  category?: string
  context_id?: string
  project_id?: string
  created_at: string
}

export interface DecisionItem {
  id: string
  chosen_option: string
  confidence: number
  context_id?: string
  project_id?: string
  created_at: string
}

export interface TaskItem {
  id: string
  task: string
  status: string
  priority: number
  context_id?: string
  project_id?: string
  created_at: string
}

export interface DeadlineItem {
  id: string
  title: string
  due_at: string
  confidence: number
  context_id?: string
  project_id?: string
  created_at: string
}

export interface ContextItem {
  id: string
  name: string
  description: string
  confidence: number
  is_active: boolean
  created_at: string
}

export interface StructuredBrief {
  active_projects: string[]
  current_contexts: string[]
  top_priorities: string[]
  open_tasks: string[]
  upcoming_deadlines: string[]
  recent_decisions: string[]
  suggested_next_actions: string[]
}

export interface ExecutiveBrief {
  id: string
  brief_date: string
  structured_brief: StructuredBrief
  rendered_brief: string
  created_at: string
}

interface AuraState {
  isAuthenticated: boolean
  token: string | null
  user: User | null
  brief: ExecutiveBrief | null
  facts: FactItem[]
  decisions: DecisionItem[]
  tasks: TaskItem[]
  deadlines: DeadlineItem[]
  contexts: ContextItem[]
  loading: boolean
  error: string | null
  
  // Actions
  login: (email: string, password: string) => Promise<boolean>
  logout: () => void
  fetchBriefToday: () => Promise<void>
  fetchKnowledge: () => Promise<void>
  toggleTaskStatus: (taskId: string) => Promise<void>
  createContext: (name: string, description?: string) => Promise<void>
  submitBriefFeedback: (briefId: string, rating: string, comment?: string) => Promise<boolean>
}

// Pre-populated mock data for UI-first design
const mockUser: User = {
  id: "11111111-1111-1111-1111-111111111111",
  email: "harsha@aura.run",
  display_name: "Harsha",
  timezone: "Asia/Kolkata",
  onboarding_completed: true
}

const mockBrief: ExecutiveBrief = {
  id: "brief-123",
  brief_date: new Date().toISOString().split('T')[0],
  structured_brief: {
    active_projects: ["AURA"],
    current_contexts: ["Startup Building"],
    top_priorities: ["Frontend Dashboard", "Benchmark Review"],
    open_tasks: ["Finish Knowledge Explorer", "Conduct 7-day Founder Dogfooding"],
    upcoming_deadlines: ["Benchmark Review (due in 2 days)"],
    recent_decisions: ["Skip Embeddings in Sprint 3"],
    suggested_next_actions: ["Finish Knowledge Explorer screen first"]
  },
  rendered_brief: `GOOD MORNING HARSHA\n\nActive Project:\n- AURA\n\nCurrent Context:\n- Startup Building\n\nTop Priorities:\n- Frontend Dashboard\n- Benchmark Review\n\nOpen Tasks:\n- Finish Knowledge Explorer\n- Conduct 7-day Founder Dogfooding\n\nUpcoming Deadlines:\n- Benchmark Review (due in 2 days)\n\nRecent Decisions:\n- Skip Embeddings in Sprint 3\n\nSuggested Next Action:\n- Finish Knowledge Explorer screen first`,
  created_at: new Date().toISOString()
}

const mockFacts: FactItem[] = [
  { id: "f-1", entity: "project", value: "AURA is a personal cognitive operating system", confidence: 1.0, category: "project_detail", context_id: "ctx-1", created_at: "2026-06-24T12:00:00Z" },
  { id: "f-2", entity: "frontend", value: "React 19, Vite, Tailwind v4 and Zustand are used for the frontend", confidence: 0.95, category: "tech_stack", context_id: "ctx-1", created_at: "2026-06-24T12:05:00Z" },
  { id: "f-3", entity: "database", value: "PostgreSQL is used as the primary database", confidence: 1.0, category: "tech_stack", context_id: "ctx-1", created_at: "2026-06-24T12:10:00Z" },
  { id: "f-4", entity: "metric", value: "The founder dogfood metric is tracked daily", confidence: 1.0, category: "business_rule", context_id: "ctx-1", created_at: "2026-06-24T12:15:00Z" },
  { id: "f-5", entity: "LLM", value: "Local-first Ollama is the default LLM provider", confidence: 0.9, category: "tech_stack", context_id: "ctx-2", created_at: "2026-06-24T12:20:00Z" }
]

const mockDecisions: DecisionItem[] = [
  { id: "d-1", chosen_option: "PostgreSQL selected over Neo4j", confidence: 1.0, context_id: "ctx-1", created_at: "2026-06-24T10:00:00Z" },
  { id: "d-2", chosen_option: "Skip Embeddings in Sprint 3 to focus on cognition first", confidence: 0.95, context_id: "ctx-1", created_at: "2026-06-24T11:00:00Z" },
  { id: "d-3", chosen_option: "Focus on Daily Brief MVP first", confidence: 0.9, context_id: "ctx-1", created_at: "2026-06-24T11:30:00Z" }
]

const mockTasks: TaskItem[] = [
  { id: "t-1", task: "Finish Knowledge Explorer", status: "pending", priority: 1, context_id: "ctx-1", created_at: "2026-06-24T09:00:00Z" },
  { id: "t-2", task: "Build Executive Brief UI", status: "completed", priority: 1, context_id: "ctx-1", created_at: "2026-06-24T08:00:00Z" },
  { id: "t-3", task: "Setup Database Migrations", status: "completed", priority: 2, context_id: "ctx-1", created_at: "2026-06-24T07:00:00Z" },
  { id: "t-4", task: "Conduct 7-day Founder Dogfooding", status: "pending", priority: 1, context_id: "ctx-1", created_at: "2026-06-24T09:15:00Z" }
]

const mockDeadlines: DeadlineItem[] = [
  { id: "dl-1", title: "Benchmark Review", due_at: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(), confidence: 1.0, context_id: "ctx-1", created_at: "2026-06-24T09:30:00Z" },
  { id: "dl-2", title: "Sprint 4 Launch", due_at: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toISOString(), confidence: 0.95, context_id: "ctx-1", created_at: "2026-06-24T09:40:00Z" }
]

const mockContexts: ContextItem[] = [
  { id: "ctx-1", name: "Startup Building", description: "Developing AURA and tracking metrics", confidence: 1.0, is_active: true, created_at: "2026-06-24T06:00:00Z" },
  { id: "ctx-2", name: "Learning", description: "React 19 & Tailwind v4 experimental features", confidence: 0.9, is_active: false, created_at: "2026-06-24T06:30:00Z" }
]

const API_PREFIX = '/api/v1'

const apiFetch = async (url: string, options: RequestInit = {}): Promise<Response> => {
  const token = localStorage.getItem('aura_token')
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...options.headers,
  }
  return fetch(url, { ...options, headers })
}

const initialToken = localStorage.getItem('aura_token')

export const useAuraStore = create<AuraState>((set, get) => ({
  isAuthenticated: !!initialToken,
  token: initialToken,
  user: null,
  brief: null,
  facts: [],
  decisions: [],
  tasks: [],
  deadlines: [],
  contexts: [],
  loading: false,
  error: null,

  login: async (email, password) => {
    set({ loading: true, error: null })
    try {
      // Setup mock JWT token for local API authentication
      const token = "mock-supabase-jwt-token"
      localStorage.setItem('aura_token', token)
      set({ 
        isAuthenticated: true, 
        token: token,
      })

      // Fetch user profile from API to verify token/session
      try {
        const res = await apiFetch(`${API_PREFIX}/users/me`)
        if (res.ok) {
          const userData = await res.json()
          set({ user: userData })
        } else {
          set({ user: mockUser })
        }
      } catch (e) {
        set({ user: mockUser })
      }

      // Pre-fetch briefings and explorer data
      await get().fetchBriefToday()
      await get().fetchKnowledge()
      set({ loading: false })
      return true
    } catch (err: any) {
      set({ error: err.message || "Login failed", loading: false })
      return false
    }
  },

  logout: () => {
    localStorage.removeItem('aura_token')
    set({ 
      isAuthenticated: false, 
      token: null, 
      user: null, 
      brief: null,
      facts: [],
      decisions: [],
      tasks: [],
      deadlines: [],
      contexts: []
    })
  },

  fetchBriefToday: async () => {
    set({ loading: true, error: null })
    try {
      const res = await apiFetch(`${API_PREFIX}/brief/today`)
      if (res.ok) {
        const briefData = await res.json()
        set({ brief: briefData, loading: false })
      } else {
        set({ brief: mockBrief, loading: false })
      }
    } catch (err: any) {
      set({ brief: mockBrief, loading: false })
    }
  },

  fetchKnowledge: async () => {
    set({ loading: true, error: null })
    try {
      const [ctxRes, factsRes, decRes, tasksRes, dlRes] = await Promise.all([
        apiFetch(`${API_PREFIX}/contexts`),
        apiFetch(`${API_PREFIX}/facts`),
        apiFetch(`${API_PREFIX}/decisions`),
        apiFetch(`${API_PREFIX}/tasks`),
        apiFetch(`${API_PREFIX}/deadlines`),
      ])

      const contextsData = ctxRes.ok ? await ctxRes.json() : mockContexts
      const factsData = factsRes.ok ? await factsRes.json() : mockFacts
      const decisionsData = decRes.ok ? await decRes.json() : mockDecisions
      const tasksData = tasksRes.ok ? await tasksRes.json() : mockTasks
      const deadlinesData = dlRes.ok ? await dlRes.json() : mockDeadlines

      set({
        contexts: contextsData,
        facts: factsData,
        decisions: decisionsData,
        tasks: tasksData,
        deadlines: deadlinesData,
        loading: false
      })
    } catch (err: any) {
      set({
        contexts: mockContexts,
        facts: mockFacts,
        decisions: mockDecisions,
        tasks: mockTasks,
        deadlines: mockDeadlines,
        loading: false
      })
    }
  },

  toggleTaskStatus: async (taskId) => {
    const originalTasks = get().tasks
    const taskToToggle = originalTasks.find(t => t.id === taskId)
    if (!taskToToggle) return

    const newStatus = taskToToggle.status === "completed" ? "pending" : "completed"
    
    // Optimistic UI update
    set((state) => ({
      tasks: state.tasks.map(t => 
        t.id === taskId 
          ? { ...t, status: newStatus }
          : t
      )
    }))

    try {
      const res = await apiFetch(`${API_PREFIX}/tasks/${taskId}`, {
        method: 'PATCH',
        body: JSON.stringify({ status: newStatus })
      })
      if (!res.ok) {
        // Rollback on error
        set({ tasks: originalTasks })
      }
    } catch (err) {
      // Rollback on network error
      set({ tasks: originalTasks })
    }
  },

  createContext: async (name, description = "") => {
    try {
      const res = await apiFetch(`${API_PREFIX}/contexts`, {
        method: 'POST',
        body: JSON.stringify({ name, description })
      })
      if (res.ok) {
        const newCtx = await res.json()
        set((state) => ({
          contexts: [newCtx, ...state.contexts]
        }))
      } else {
        // Fallback local creation
        const localCtx: ContextItem = {
          id: `ctx-${Date.now()}`,
          name,
          description,
          confidence: 1.0,
          is_active: false,
          created_at: new Date().toISOString()
        }
        set((state) => ({
          contexts: [localCtx, ...state.contexts]
        }))
      }
    } catch (err) {
      // Fallback local creation
      const localCtx: ContextItem = {
        id: `ctx-${Date.now()}`,
        name,
        description,
        confidence: 1.0,
        is_active: false,
        created_at: new Date().toISOString()
      }
      set((state) => ({
        contexts: [localCtx, ...state.contexts]
      }))
    }
  },

  submitBriefFeedback: async (briefId: string, rating: string, comment = ""): Promise<boolean> => {
    try {
      const res = await apiFetch(`${API_PREFIX}/brief/${briefId}/feedback`, {
        method: 'POST',
        body: JSON.stringify({ rating, feedback: comment })
      })
      return res.ok
    } catch (err) {
      console.error("Failed to submit feedback to API", err)
      return false
    }
  }
}))
