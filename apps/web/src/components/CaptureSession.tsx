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
    fetchUser,
  } = useAuraStore();

  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [message, setMessage] = useState('');

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

  return (
    <div className="flex h-full" data-testid="capture-session">
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
                className={`p-2 rounded ${msg.role === 'assistant' ? 'bg-[#0c0c0e] text-[#e4e4e7]' : 'bg-[#18181b] text-white'}`}
                data-testid={`message-${msg.id || idx}`}
              >
                {msg.content}
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
