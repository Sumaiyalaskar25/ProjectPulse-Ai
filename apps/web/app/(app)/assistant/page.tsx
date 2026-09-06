import { AppShell } from '@/components/layout/AppShell'
import { ChatPanel } from '@/components/assistant/ChatPanel'
import { QueryPanel } from '@/components/assistant/QueryPanel'

export default function AssistantPage() {
  return (
    <AppShell activeNav="AI Assistant">
      <div className="flex h-full gap-6">
        <QueryPanel />
        <ChatPanel />
      </div>
    </AppShell>
  )
}