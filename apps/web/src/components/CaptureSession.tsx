import React, { useEffect, useState } from 'react';
import { useAuraStore } from '../store/auraStore';

/**
 * CaptureSession component implements the Capture Session workflow.
 * It provides a sidebar with a list of conversation sessions, a button to create a new session,
 * a message timeline for the active session, and an input box with a send button.
 *
 * Test IDs are added for automated UI testing.
 */
export const CaptureSession: React.FC = () => {
  const {
    conversations,
    activeConversationId,
    fetchConversations,
    createConversation,
    sendMessage,
    approveKnowledgeItem,
    rejectKnowledgeItem,
    updateKnowledgeItem,
  } = useAuraStore();

  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [message, setMessage] = useState('');
  const [editingItemId, setEditingItemId] = useState<string | null>(null);
  const [editingItemText, setEditingItemText] = useState('');
  const [rejectingItemId, setRejectingItemId] = useState<string | null>(null);

  // Load conversations on mount
  useEffect(() => {
    fetchConversations();
  }, [fetchConversations]);

  // When activeConversationId from store changes, reflect in local state
  useEffect(() => {
    if (activeConversationId) {
      setSelectedId(activeConversationId);
    }
  }, [activeConversationId]);

  const handleNewSession = async () => {
    const newId = await createConversation();
    if (newId) {
      setSelectedId(newId);
    }
  };

  const handleSend = async () => {
    if (!selectedId || !message.trim()) return;
    await sendMessage(selectedId, message.trim());
    setMessage('');
  };

  const activeConversation = conversations.find((c) => c.id === selectedId);

  const getChipStyle = (type: string, state: string) => {
    if (state === 'rejected') {
      return {
        bg: 'bg-zinc-900 border-zinc-800 text-[#71717a]',
        badge: 'bg-zinc-850 border-zinc-800 text-[#71717a]',
        label: 'REJECTED'
      }
    }
    switch (type) {
      case 'fact':
        return {
          bg: 'bg-[rgba(167,139,250,0.06)] border-[#a78bfa]/20 text-[#e4e4e7]',
          badge: 'bg-[rgba(167,139,250,0.15)] border-[#a78bfa]/30 text-[#a78bfa]',
          label: 'FACT'
        }
      case 'decision':
        return {
          bg: 'bg-[rgba(59,130,246,0.06)] border-[#60a5fa]/20 text-[#e4e4e7]',
          badge: 'bg-[rgba(59,130,246,0.15)] border-[#60a5fa]/30 text-[#60a5fa]',
          label: 'DECISION'
        }
      case 'task':
        return {
          bg: 'bg-[rgba(249,115,22,0.06)] border-[#fb923c]/20 text-[#e4e4e7]',
          badge: 'bg-[rgba(249,115,22,0.15)] border-[#fb923c]/30 text-[#fb923c]',
          label: 'TASK'
        }
      case 'deadline':
        return {
          bg: 'bg-[rgba(239,68,68,0.06)] border-[#f87171]/20 text-[#e4e4e7]',
          badge: 'bg-[rgba(239,68,68,0.15)] border-[#f87171]/30 text-[#f87171]',
          label: 'DEADLINE'
        }
      default:
        return {
          bg: 'bg-zinc-900 border-zinc-800 text-[#e4e4e7]',
          badge: 'bg-zinc-800 border-zinc-700 text-[#71717a]',
          label: 'UNKNOWN'
        }
    }
  }

  const renderReviewChip = (
    type: 'fact' | 'decision' | 'task' | 'deadline',
    item: any,
    messageId: string
  ) => {
    const style = getChipStyle(type, item.review_state)
    const isEditing = editingItemId === item.id
    const isRejecting = rejectingItemId === item.id

    const getPrimaryText = () => {
      if (type === 'fact') return `${item.entity}: ${item.value}`
      if (type === 'decision') return item.chosen_option
      if (type === 'task') return item.task
      return item.title
    }

    const getRawTextForEditing = () => {
      if (type === 'fact') return item.value
      if (type === 'decision') return item.chosen_option
      if (type === 'task') return item.task
      return item.title
    }

    return (
      <div 
        key={item.id}
        data-testid={`chip-${item.id}`}
        className={`flex flex-col md:flex-row items-start md:items-center gap-2 px-3 py-1.5 rounded-lg border text-xs transition-all max-w-full chip ${style.bg}`}
      >
        {isEditing ? (
          <div className="flex items-center gap-2 w-full" data-testid="edit-panel">
            <span className={`px-2 py-0.5 rounded text-[10px] font-bold tracking-wider shrink-0 ${style.badge}`}>
              EDITING
            </span>
            <input
              type="text"
              value={editingItemText}
              onChange={(e) => setEditingItemText(e.target.value)}
              className="flex-grow px-2 py-1 bg-[#060608] border border-[#1e1e24] rounded text-xs text-white focus:outline-none focus:border-[#a78bfa] min-w-[200px]"
              autoFocus
              data-testid="edit-input"
            />
            <button
              type="button"
              onClick={async () => {
                const payload: any = {}
                if (type === 'fact') payload.value = editingItemText
                else if (type === 'decision') payload.chosen_option = editingItemText
                else if (type === 'task') payload.task = editingItemText
                else payload.title = editingItemText

                await updateKnowledgeItem({ type, id: item.id, payload, messageId })
                setEditingItemId(null)
              }}
              className="px-2 py-1 bg-[#10b981] hover:bg-[#059669] text-white rounded text-[10px] font-semibold cursor-pointer"
              data-testid="save-button"
            >
              Save
            </button>
            <button
              type="button"
              onClick={() => setEditingItemId(null)}
              className="px-2 py-1 bg-zinc-800 hover:bg-zinc-700 text-[#a1a1aa] rounded text-[10px] font-semibold cursor-pointer"
              data-testid="cancel-edit-button"
            >
              Cancel
            </button>
          </div>
        ) : isRejecting ? (
          <div className="flex flex-col md:flex-row items-start md:items-center gap-2 w-full" data-testid="reject-panel">
            <span className="text-[10px] font-semibold text-[#a1a1aa] uppercase tracking-wider shrink-0">
              Why reject?
            </span>
            <div className="flex flex-wrap gap-1.5">
              {['Wrong Type', 'Wrong Value', 'Incomplete', 'Hallucinated', 'Duplicate'].map(reason => (
                <button
                  type="button"
                  key={reason}
                  onClick={async () => {
                    await rejectKnowledgeItem({ type, id: item.id, reason, messageId })
                    setRejectingItemId(null);
                  }}
                  className="px-2 py-0.5 bg-[#ef4444]/10 hover:bg-[#ef4444]/25 text-[#f87171] border border-[#ef4444]/20 rounded text-[10px] transition-all cursor-pointer font-medium"
                  data-testid={`reject-reason-${reason}`}
                >
                  {reason}
                </button>
              ))}
              <button
                type="button"
                onClick={() => setRejectingItemId(null)}
                className="px-2 py-0.5 bg-zinc-800 hover:bg-zinc-700 text-[#a1a1aa] rounded text-[10px] cursor-pointer font-medium"
                data-testid="cancel-reject-button"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <>
            <div className="flex items-center gap-1.5 min-w-0 max-w-full">
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold tracking-wider shrink-0 ${style.badge}`}>
                {style.label}
              </span>
              <span className={`truncate max-w-[280px] md:max-w-[400px] text-[#e4e4e7] ${item.review_state === 'rejected' ? 'line-through opacity-50' : ''}`}>
                {getPrimaryText()}
              </span>
              {type === 'deadline' && item.due_at && (
                <span className="text-[10px] text-[#71717a] shrink-0 font-mono">
                  (due {new Date(item.due_at).toLocaleDateString()})
                </span>
              )}
            </div>

            <div className="flex items-center gap-1.5 shrink-0 ml-auto md:ml-0 border-t md:border-t-0 border-[#1e1e24] pt-1.5 md:pt-0 w-full md:w-auto justify-end">
              {item.review_state === 'approved' && (
                <span className="text-[#10b981] font-semibold text-[10px] bg-[#10b981]/10 px-2 py-0.5 rounded border border-[#10b981]/20 flex items-center gap-1">
                  ✓ Approved
                </span>
              )}
              {item.review_state === 'edited' && (
                <span className="text-[#f59e0b] font-semibold text-[10px] bg-[#f59e0b]/10 px-2 py-0.5 rounded border border-[#f59e0b]/20">
                  Edited
                </span>
              )}
              {item.review_state === 'rejected' && (
                <span className="text-[#ef4444] font-semibold text-[10px] bg-[#ef4444]/10 px-2 py-0.5 rounded border border-[#ef4444]/20">
                  Rejected
                </span>
              )}

              {item.review_state !== 'rejected' && item.review_state !== 'approved' && (
                <div className="flex items-center gap-1">
                  <button
                    type="button"
                    onClick={async () => {
                      await approveKnowledgeItem({ type, id: item.id, messageId })
                    }}
                    className="p-1 bg-[#10b981]/10 hover:bg-[#10b981]/25 border border-[#10b981]/20 rounded text-[#10b981] text-[10px] transition-all cursor-pointer font-bold flex items-center justify-center h-5 w-5 animate-fade-in edit"
                    title="Approve"
                    data-testid="approve-button"
                  >
                    ✓
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setEditingItemId(item.id)
                      setEditingItemText(getRawTextForEditing())
                    }}
                    className="p-1 bg-[#f59e0b]/10 hover:bg-[#f59e0b]/25 border border-[#f59e0b]/20 rounded text-[#f59e0b] text-[10px] transition-all cursor-pointer font-bold flex items-center justify-center h-5 w-5 animate-fade-in edit"
                    title="Edit"
                    data-testid="edit-button"
                  >
                    ✎
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setRejectingItemId(item.id)
                    }}
                    className="p-1 bg-[#ef4444]/10 hover:bg-[#ef4444]/25 border border-[#ef4444]/20 rounded text-[#ef4444] text-[10px] transition-all cursor-pointer font-bold flex items-center justify-center h-5 w-5 animate-fade-in reject"
                    title="Reject"
                    data-testid="reject-button"
                  >
                    ✗
                  </button>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    )
  }

  return (
    <div className="flex h-full capture-modal" data-testid="capture-session">
      {/* Sidebar */}
      <aside className="w-64 border-r border-[#1e1e24] p-4 overflow-y-auto" data-testid="session-sidebar">
        <button
          className="w-full mb-4 px-3 py-2 bg-[#a78bfa] hover:bg-[#906ffa] text-white rounded"
          onClick={handleNewSession}
          data-testid="new-session-button"
        >
          New Session
        </button>
        <ul className="space-y-2">
          {conversations.map((conv) => (
            <li
              key={conv.id}
              className={`p-2 rounded cursor-pointer ${selectedId === conv.id ? 'bg-[#18181b] text-white' : 'text-[#a1a1aa] hover:bg-[#121214] hover:text-[#e4e4e7]'}`}
              onClick={() => setSelectedId(conv.id)}
              data-testid={`session-item-${conv.id}`}
            >
              {conv.title || 'Untitled Session'}
            </li>
          ))}
        </ul>
      </aside>

      {/* Main chat area */}
      <main className="flex-1 flex flex-col p-4 overflow-y-auto" data-testid="message-timeline">
        {activeConversation ? (
          <div className="flex-1 space-y-3 mb-4">
            {activeConversation.messages.map((msg: any, idx: number) => (
              <div
                key={idx}
                className="flex flex-col space-y-2 max-w-[85%] mr-auto items-start"
                data-testid={`message-${msg.id || idx}`}
              >
                <div
                  className={`p-2.5 rounded-xl border text-sm leading-relaxed ${msg.role === 'assistant' ? 'bg-[#0c0c0e] text-[#e4e4e7] border-[#1e1e24]/40' : 'bg-[#18181b] text-white border-[#1e1e24]'}`}
                >
                  {msg.content}
                </div>
                <span className="text-[10px] text-[#52525b] px-1">
                  {new Date(msg.created_at || Date.now()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
                
                {/* Render Review Chips for User Messages */}
                {msg.role === 'user' && (
                  <div className="flex flex-wrap gap-2 justify-start mt-1 max-w-full" data-testid="extraction-chips">
                    {msg.facts?.map((item: any) => renderReviewChip('fact', item, msg.id))}
                    {msg.decisions?.map((item: any) => renderReviewChip('decision', item, msg.id))}
                    {msg.tasks?.map((item: any) => renderReviewChip('task', item, msg.id))}
                    {msg.deadlines?.map((item: any) => renderReviewChip('deadline', item, msg.id))}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center text-[#71717a]" data-testid="no-session-placeholder">
            Select or create a session to begin.
          </div>
        )}
        {/* Input box */}
        <div className="flex items-center mt-2" data-testid="thought-input-box">
          <input
            type="text"
            className="flex-1 px-3 py-2 bg-[#060608] border border-[#1e1e24] rounded text-sm text-white focus:outline-none focus:border-[#a78bfa]"
            placeholder="Your thought..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            data-testid="message-input"
          />
          <button
            className="ml-2 px-4 py-2 bg-[#a78bfa] hover:bg-[#906ffa] text-white rounded disabled:opacity-55"
            onClick={handleSend}
            disabled={!selectedId || !message.trim()}
            data-testid="send-button"
          >
            Send
          </button>
        </div>
      </main>
    </div>
  );
};

export default CaptureSession;
