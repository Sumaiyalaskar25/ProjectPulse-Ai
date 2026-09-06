import type { ReactNode } from 'react'
import Image from 'next/image'
import { Bot } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ChatMessageProps {
  role: 'user' | 'ai'
  author: string
  timestamp: string
  avatar?: string
  children: ReactNode
}

export function ChatMessage({
  role,
  author,
  timestamp,
  avatar,
  children,
}: ChatMessageProps) {
  const isUser = role === 'user'

  return (
    <div
      className={cn(
        'flex flex-col gap-2',
        isUser ? 'items-end' : 'items-start',
      )}
    >
      <div
        className={cn(
          'flex items-center gap-2',
          isUser ? 'flex-row-reverse' : 'flex-row',
        )}
      >
        {isUser && avatar ? (
          <Image
            src={avatar}
            alt={author}
            width={30}
            height={30}
            unoptimized
            className="h-8 w-8 rounded-full object-cover"
          />
        ) : (
          <span className="flex h-8 w-8 items-center justify-center rounded-full bg-status-info/15">
            <Bot className="h-4 w-4 text-status-info" />
          </span>
        )}
        <span className="text-xs font-semibold text-text-primary">{author}</span>
        <span className="font-mono text-xs text-text-muted">{timestamp}</span>
      </div>
      <div
        className={cn(
          isUser
            ? 'max-w-[75%] rounded-2xl rounded-br-sm bg-slate-200 px-4 py-3 text-sm leading-relaxed text-slate-900'
            : 'max-w-[85%] rounded-2xl rounded-bl-sm bg-background-card px-4 py-3 text-sm leading-relaxed text-text-primary',
        )}
      >
        {children}
      </div>
    </div>
  )
}