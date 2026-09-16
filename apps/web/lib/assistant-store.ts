import { create } from 'zustand'
import { queryAssistant } from '@/lib/api-client'
import { mockQueryAssistant } from '@/lib/mock-data'
import { useToastStore } from './toast-store'

export interface ChatItem {
  id: string
  role: 'user' | 'ai'
  author: string
  timestamp: string
  text: string
  data?: Record<string, unknown>[]
  sources?: string[]
  sql_query?: string
}

interface AssistantStoreState {
  messages: ChatItem[]
  isLoading: boolean
  currentSessionId: string
  sendMessage: (query: string) => Promise<void>
  clearChat: () => void
  exportChat: () => void
}

const useMockData = process.env.NEXT_PUBLIC_USE_MOCK_DATA !== 'false'

const INITIAL_MESSAGES: ChatItem[] = [
  {
    id: 'msg-init-1',
    role: 'user',
    author: 'EXECUTIVE DIRECTOR',
    timestamp: '14:32:05',
    text: 'Identify the top 3 infrastructure projects currently exceeding budget by more than 15% and summarize their primary risk drivers.',
  },
  {
    id: 'msg-init-2',
    role: 'ai',
    author: 'INTELLIGENCE AGENT',
    timestamp: '14:32:06',
    text: 'Based on the latest data sync (Oct 27, 14:32 UTC), I have identified three critical projects with significant budget variances. The primary drivers include land acquisition litigation and unexpected soil instability during the monsoon period.',
    data: [
      {
        project: 'NH-44 Expressway Ext.',
        budget: '4.2B Cr',
        overrun: '+34.2%',
        status: 'CRITICAL',
      },
      {
        project: 'Mumbai Metro Line 3',
        budget: '12.8B Cr',
        overrun: '+18.5%',
        status: 'AT RISK',
      },
      {
        project: 'Chennai Smart Grid',
        budget: '1.5B Cr',
        overrun: '+22.1%',
        status: 'AT RISK',
      },
    ],
    sources: ['Q3 Financial Audit', 'Land Registry v.24', 'Sensor Node 442 Logs'],
  },
]

export const useAssistantStore = create<AssistantStoreState>()((set, get) => ({
  messages: INITIAL_MESSAGES,
  isLoading: false,
  currentSessionId: 'PULSE-' + Math.floor(1000 + Math.random() * 9000) + '-X',

  sendMessage: async (query: string) => {
    if (!query.trim()) return

    const now = new Date()
    const timeStr = now.toTimeString().split(' ')[0]

    const userMessage: ChatItem = {
      id: `usr-${Date.now()}`,
      role: 'user',
      author: 'OPERATOR',
      timestamp: timeStr,
      text: query.trim(),
    }

    set((state) => ({
      messages: [...state.messages, userMessage],
      isLoading: true,
    }))

    try {
      const response = useMockData
        ? await mockQueryAssistant(query)
        : await queryAssistant(query)

      const aiMessage: ChatItem = {
        id: `ai-${Date.now()}`,
        role: 'ai',
        author: 'INTELLIGENCE AGENT',
        timestamp: new Date().toTimeString().split(' ')[0],
        text: response.formatted_answer || 'Analysis complete.',
        data: response.data && response.data.length > 0 ? response.data : undefined,
        sources: response.sources && response.sources.length > 0 ? response.sources : ['National Data Warehouse'],
      }

      set((state) => ({
        messages: [...state.messages, aiMessage],
        isLoading: false,
      }))
    } catch (error: any) {
      const errorMessage: ChatItem = {
        id: `ai-err-${Date.now()}`,
        role: 'ai',
        author: 'INTELLIGENCE AGENT',
        timestamp: new Date().toTimeString().split(' ')[0],
        text: `Error processing query: ${error.message || 'Unable to reach backend service.'}`,
      }
      set((state) => ({
        messages: [...state.messages, errorMessage],
        isLoading: false,
      }))
    }
  },

  clearChat: () => {
    set({
      messages: [],
      currentSessionId: 'PULSE-' + Math.floor(1000 + Math.random() * 9000) + '-X',
    })
    useToastStore.getState().show('Started new intelligence query session.')
  },

  exportChat: () => {
    const { messages, currentSessionId } = get()
    const exportData = {
      sessionId: currentSessionId,
      exportedAt: new Date().toISOString(),
      messages,
    }
    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json',
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `assistant_session_${currentSessionId}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    useToastStore.getState().show('Session insights exported successfully.')
  },
}))
