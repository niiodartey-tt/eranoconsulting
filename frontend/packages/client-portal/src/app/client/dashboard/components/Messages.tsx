'use client';
import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Message {
  id: number;
  sender_id: number;
  receiver_id: number;
  content: string;
  timestamp: string;
  sender_name?: string;
  receiver_name?: string;
  is_read: boolean;
}

interface Conversation {
  partner_id: number;
  partner_name: string;
  partner_email: string;
  last_message: string;
  last_message_time: string;
  unread_count: number;
}

interface User {
  id: number;
  email: string;
  full_name?: string;
  role: string;
}

interface MessagesProps {
  onClose: () => void;
  currentUserId: number;
}

export default function Messages({ onClose, currentUserId }: MessagesProps) {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedPartner, setSelectedPartner] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [showNewConversation, setShowNewConversation] = useState(false);
  const [users, setUsers] = useState<User[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  useEffect(() => {
    fetchConversations();
  }, []);

  useEffect(() => {
    if (selectedPartner) {
      fetchMessages(selectedPartner.partner_id);
    }
  }, [selectedPartner]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  async function fetchConversations() {
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch(`${API_URL}/api/v1/messages/conversations`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (res.ok) {
        const data = await res.json();
        setConversations(data);
      }
    } catch (error) {
      console.error('Error fetching conversations:', error);
    } finally {
      setLoading(false);
    }
  }

  async function fetchUsers() {
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch(`${API_URL}/api/v1/users`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (res.ok) {
        const data = await res.json();
        // Filter out current user
        setUsers(data.filter((u: User) => u.id !== currentUserId));
      }
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  }

  async function fetchMessages(partnerId: number) {
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch(`${API_URL}/api/v1/messages/with/${partnerId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (res.ok) {
        const data = await res.json();
        setMessages(data);
        
        // Update unread count in conversations
        setConversations(prev => 
          prev.map(conv => 
            conv.partner_id === partnerId 
              ? { ...conv, unread_count: 0 }
              : conv
          )
        );
      }
    } catch (error) {
      console.error('Error fetching messages:', error);
    }
  }

  async function sendMessage() {
    if (!newMessage.trim() || !selectedPartner || sending) return;

    setSending(true);
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch(`${API_URL}/api/v1/messages/send`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          receiver_id: selectedPartner.partner_id,
          content: newMessage,
        }),
      });

      if (res.ok) {
        const sentMessage = await res.json();
        setMessages(prev => [...prev, sentMessage]);
        setNewMessage('');
        
        // Update conversation list
        await fetchConversations();
      }
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setSending(false);
    }
  }

  function startNewConversation(user: User) {
    // Check if conversation already exists
    const existingConv = conversations.find(c => c.partner_id === user.id);
    
    if (existingConv) {
      setSelectedPartner(existingConv);
    } else {
      // Create new conversation object
      const newConv: Conversation = {
        partner_id: user.id,
        partner_name: user.full_name || user.email,
        partner_email: user.email,
        last_message: '',
        last_message_time: new Date().toISOString(),
        unread_count: 0,
      };
      setSelectedPartner(newConv);
      setMessages([]);
    }
    
    setShowNewConversation(false);
    setSearchQuery('');
  }

  function formatTime(timestamp: string) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString();
  }

  const filteredUsers = users.filter(user => {
    const searchLower = searchQuery.toLowerCase();
    return (
      user.email.toLowerCase().includes(searchLower) ||
      (user.full_name && user.full_name.toLowerCase().includes(searchLower))
    );
  });

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={(e) => {
        // Close if clicking the backdrop
        if (e.target === e.currentTarget) {
          onClose();
        }
      }}
    >
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-5xl h-[600px] flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-200 flex justify-between items-center">
          <h3 className="text-xl font-bold text-gray-900">Messages</h3>
          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                setShowNewConversation(true);
                fetchUsers();
              }}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition text-sm font-medium flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              New Message
            </button>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition"
              type="button"  // ADD THIS to prevent form submission
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex overflow-hidden">
          {/* Conversations List */}
          <div className="w-1/3 border-r border-gray-200 overflow-y-auto">
            {loading ? (
              <div className="flex items-center justify-center h-full">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            ) : conversations.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full p-4 text-center">
                <svg className="w-16 h-16 text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
                <p className="text-gray-600 font-medium">No conversations yet</p>
                <p className="text-sm text-gray-500 mt-2">Click "New Message" to start</p>
              </div>
            ) : (
              conversations.map((conv) => (
                <div
                  key={conv.partner_id}
                  onClick={() => setSelectedPartner(conv)}
                  className={`p-4 border-b border-gray-100 cursor-pointer transition ${
                    selectedPartner?.partner_id === conv.partner_id
                      ? 'bg-blue-50'
                      : 'hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-semibold text-gray-900">{conv.partner_name}</span>
                    {conv.unread_count > 0 && (
                      <span className="bg-blue-600 text-white text-xs font-bold px-2 py-1 rounded-full">
                        {conv.unread_count}
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-600 truncate">{conv.last_message}</p>
                  <p className="text-xs text-gray-400 mt-1">{formatTime(conv.last_message_time)}</p>
                </div>
              ))
            )}
          </div>

          {/* Messages Area */}
          <div className="flex-1 flex flex-col">
            {selectedPartner ? (
              <>
                {/* Chat Header */}
                <div className="p-4 border-b border-gray-200 bg-gray-50">
                  <h4 className="font-semibold text-gray-900">{selectedPartner.partner_name}</h4>
                  <p className="text-sm text-gray-500">{selectedPartner.partner_email}</p>
                </div>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
                  {messages.length === 0 ? (
                    <div className="flex items-center justify-center h-full">
                      <p className="text-gray-500">No messages yet. Start the conversation!</p>
                    </div>
                  ) : (
                    messages.map((msg) => {
                      const isOwn = msg.sender_id === currentUserId;
                      return (
                        <div
                          key={msg.id}
                          className={`flex ${isOwn ? 'justify-end' : 'justify-start'}`}
                        >
                          <div
                            className={`max-w-[70%] rounded-2xl px-4 py-2 ${
                              isOwn
                                ? 'bg-blue-600 text-white'
                                : 'bg-white text-gray-900 shadow-sm'
                            }`}
                          >
                            <p className="text-sm break-words">{msg.content}</p>
                            <p
                              className={`text-xs mt-1 ${
                                isOwn ? 'text-blue-100' : 'text-gray-500'
                              }`}
                            >
                              {formatTime(msg.timestamp)}
                            </p>
                          </div>
                        </div>
                      );
                    })
                  )}
                  <div ref={messagesEndRef} />
                </div>

                {/* Message Input */}
                <div className="p-4 border-t border-gray-200 bg-white">
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                      placeholder="Type your message..."
                      className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                      disabled={sending}
                    />
                    <button
                      onClick={sendMessage}
                      disabled={!newMessage.trim() || sending}
                      className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition font-semibold disabled:bg-gray-300 disabled:cursor-not-allowed"
                    >
                      {sending ? 'Sending...' : 'Send'}
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <svg className="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  <p className="text-gray-600">Select a conversation or start a new one</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* New Conversation Modal */}
      {showNewConversation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md">
            <div className="p-4 border-b border-gray-200">
              <div className="flex justify-between items-center mb-4">
                <h4 className="text-lg font-bold text-gray-900">New Message</h4>
                <button
                  onClick={() => {
                    setShowNewConversation(false);
                    setSearchQuery('');
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search users..."
                className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
              />
            </div>
            <div className="max-h-96 overflow-y-auto">
              {filteredUsers.map((user) => (
                <div
                  key={user.id}
                  onClick={() => startNewConversation(user)}
                  className="p-4 border-b border-gray-100 hover:bg-gray-50 cursor-pointer transition"
                >
                  <div className="flex items-center gap-3">
                    <div className="bg-blue-100 p-2 rounded-full">
                      <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{user.full_name || user.email}</p>
                      <p className="text-sm text-gray-500">{user.email}</p>
                      <span className="text-xs text-gray-400 capitalize">{user.role}</span>
                    </div>
                  </div>
                </div>
              ))}
              {filteredUsers.length === 0 && (
                <div className="p-8 text-center text-gray-500">
                  No users found
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
