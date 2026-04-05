/**
 * Complete Discovery Dashboard
 * app/dashboard/page.tsx
 *
 * Real-time dashboard to view and manage all scoping conversations
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import { createClient } from '@supabase/supabase-js';
import Link from 'next/link';

// Initialize Supabase
const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

interface Conversation {
  id: string;
  conversation_id: string;
  user_name: string;
  email: string;
  project_type: string;
  requirements: string[];
  tech_stack: string[];
  timeline: string;
  budget: string;
  status: 'pending_review' | 'reviewed' | 'archived';
  analysis: {
    completeness: number;
    quality: 'low' | 'medium' | 'high';
  };
  transcript: Array<{ role: 'agent' | 'user'; message: string }>;
  created_at: string;
  duration_secs: number;
}

export default function Dashboard() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null);
  const [filter, setFilter] = useState<'pending_review' | 'reviewed' | 'archived'>('pending_review');
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [showTranscript, setShowTranscript] = useState(false);
  const [stats, setStats] = useState({
    total: 0,
    pending: 0,
    reviewed: 0,
    avgCompleteness: 0
  });

  // Fetch conversations
  const fetchConversations = useCallback(async () => {
    setLoading(true);
    try {
      let query = supabase
        .from('elevenlabs_conversations')
        .select('*')
        .order('created_at', { ascending: false });

      if (filter !== 'all') {
        query = query.eq('status', filter);
      }

      const { data, error } = await query;

      if (error) throw error;

      setConversations(data || []);

      // Calculate stats
      if (data) {
        const pending = data.filter((c) => c.status === 'pending_review').length;
        const reviewed = data.filter((c) => c.status === 'reviewed').length;
        const avgCompleteness =
          data.reduce((sum, c) => sum + (c.analysis?.completeness || 0), 0) / data.length;

        setStats({
          total: data.length,
          pending,
          reviewed,
          avgCompleteness: Math.round(avgCompleteness)
        });
      }
    } catch (error) {
      console.error('Error fetching conversations:', error);
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    fetchConversations();

    // Subscribe to real-time updates
    const subscription = supabase
      .channel('conversations')
      .on(
        'postgres_changes',
        { event: '*', schema: 'public', table: 'elevenlabs_conversations' },
        () => {
          fetchConversations();
        }
      )
      .subscribe();

    return () => {
      subscription.unsubscribe();
    };
  }, [fetchConversations, filter]);

  // Filter conversations by search
  const filteredConversations = conversations.filter(
    (conv) =>
      conv.user_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      conv.email?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      conv.project_type?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Handle status update
  const updateStatus = async (conversationId: string, newStatus: string) => {
    try {
      const { error } = await supabase
        .from('elevenlabs_conversations')
        .update({ status: newStatus, updated_at: new Date().toISOString() })
        .eq('conversation_id', conversationId);

      if (error) throw error;

      // Update local state
      setConversations(
        conversations.map((c) =>
          c.conversation_id === conversationId ? { ...c, status: newStatus as any } : c
        )
      );

      if (selectedConversation?.conversation_id === conversationId) {
        setSelectedConversation({ ...selectedConversation, status: newStatus as any });
      }
    } catch (error) {
      console.error('Error updating status:', error);
    }
  }

  // Generate document
  const generateDocument = async (conversationId: string) => {
    try {
      const response = await fetch('/api/generate-document', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ conversationId })
      });

      if (response.ok) {
        alert('Document generated and sent to user!');
      }
    } catch (error) {
      console.error('Error generating document:', error);
      alert('Failed to generate document');
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white border-b shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Discovery Dashboard</h1>
              <p className="text-gray-600 mt-1">Manage and review scoping conversations</p>
            </div>
            <Link
              href="/"
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
            >
              New Scoping Call
            </Link>
          </div>
        </div>
      </header>

      {/* Stats */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard label="Total Conversations" value={stats.total} icon="📞" />
          <StatCard label="Pending Review" value={stats.pending} icon="⏳" color="yellow" />
          <StatCard label="Reviewed" value={stats.reviewed} icon="✓" color="green" />
          <StatCard label="Avg Completeness" value={`${stats.avgCompleteness}%`} icon="📊" />
        </div>
      </div>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Conversation List */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md sticky top-24">
              {/* Search */}
              <div className="p-4 border-b">
                <input
                  type="text"
                  placeholder="Search by name, email..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                />
              </div>

              {/* Filters */}
              <div className="border-b">
                {[
                  { key: 'pending_review', label: '⏳ Pending', color: 'yellow' },
                  { key: 'reviewed', label: '✓ Reviewed', color: 'green' },
                  { key: 'archived', label: '📦 Archived', color: 'gray' }
                ].map((f) => (
                  <button
                    key={f.key}
                    onClick={() => setFilter(f.key as any)}
                    className={`w-full text-left px-4 py-3 text-sm font-medium transition-colors ${
                      filter === f.key
                        ? 'bg-blue-50 border-l-4 border-blue-600 text-blue-600'
                        : 'border-l-4 border-transparent hover:bg-gray-50'
                    }`}
                  >
                    {f.label}
                    <span className="float-right text-xs px-2 py-1 bg-gray-200 rounded-full">
                      {conversations.filter((c) => c.status === f.key).length}
                    </span>
                  </button>
                ))}
              </div>

              {/* List */}
              <div className="divide-y max-h-96 overflow-y-auto">
                {loading ? (
                  <div className="p-4 text-center text-gray-500">Loading...</div>
                ) : filteredConversations.length === 0 ? (
                  <div className="p-4 text-center text-gray-500 text-sm">No conversations found</div>
                ) : (
                  filteredConversations.map((conv) => (
                    <button
                      key={conv.id}
                      onClick={() => setSelectedConversation(conv)}
                      className={`w-full text-left p-4 hover:bg-gray-50 transition-colors ${
                        selectedConversation?.id === conv.id ? 'bg-blue-50' : ''
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <p className="font-semibold text-sm text-gray-900 truncate">
                            {conv.user_name}
                          </p>
                          <p className="text-xs text-gray-500 truncate">{conv.email}</p>
                          <div className="flex items-center gap-2 mt-2">
                            <span className={`text-xs px-2 py-0.5 rounded-full ${
                              conv.analysis?.quality === 'high'
                                ? 'bg-green-100 text-green-700'
                                : conv.analysis?.quality === 'medium'
                                  ? 'bg-yellow-100 text-yellow-700'
                                  : 'bg-red-100 text-red-700'
                            }`}>
                              {conv.analysis?.quality || 'unknown'}
                            </span>
                            <span className="text-xs text-gray-500">
                              {conv.analysis?.completeness || 0}%
                            </span>
                          </div>
                        </div>
                        <span className="text-xs text-gray-400 ml-2 whitespace-nowrap">
                          {new Date(conv.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </button>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Right: Details */}
          <div className="lg:col-span-2">
            {selectedConversation ? (
              <div className="bg-white rounded-lg shadow-md">
                {/* Header */}
                <div className="p-6 border-b">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h2 className="text-2xl font-bold text-gray-900">
                        {selectedConversation.user_name}
                      </h2>
                      <p className="text-gray-600">{selectedConversation.email}</p>
                    </div>
                    <select
                      value={selectedConversation.status}
                      onChange={(e) =>
                        updateStatus(selectedConversation.conversation_id, e.target.value)
                      }
                      className={`px-3 py-2 rounded-lg text-sm font-medium border-0 ${
                        selectedConversation.status === 'pending_review'
                          ? 'bg-yellow-100 text-yellow-800'
                          : selectedConversation.status === 'reviewed'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      <option value="pending_review">Pending Review</option>
                      <option value="reviewed">Reviewed</option>
                      <option value="archived">Archived</option>
                    </select>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-blue-50 p-3 rounded">
                      <p className="text-xs text-blue-600 font-medium">Completeness</p>
                      <p className="text-2xl font-bold text-blue-900">
                        {selectedConversation.analysis?.completeness || 0}%
                      </p>
                    </div>
                    <div className="bg-purple-50 p-3 rounded">
                      <p className="text-xs text-purple-600 font-medium">Quality</p>
                      <p className="text-2xl font-bold text-purple-900 capitalize">
                        {selectedConversation.analysis?.quality || 'Unknown'}
                      </p>
                    </div>
                    <div className="bg-green-50 p-3 rounded">
                      <p className="text-xs text-green-600 font-medium">Duration</p>
                      <p className="text-2xl font-bold text-green-900">
                        {Math.round(selectedConversation.duration_secs / 60)}m
                      </p>
                    </div>
                    <div className="bg-orange-50 p-3 rounded">
                      <p className="text-xs text-orange-600 font-medium">Date</p>
                      <p className="text-sm font-bold text-orange-900">
                        {new Date(selectedConversation.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Info */}
                <div className="p-6 border-b">
                  <div className="grid grid-cols-2 gap-6">
                    <div>
                      <p className="text-xs text-gray-500 font-semibold uppercase">Project Type</p>
                      <p className="text-lg font-semibold text-gray-900 capitalize">
                        {selectedConversation.project_type}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 font-semibold uppercase">Timeline</p>
                      <p className="text-lg font-semibold text-gray-900">
                        {selectedConversation.timeline || 'Not specified'}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 font-semibold uppercase">Budget</p>
                      <p className="text-lg font-semibold text-gray-900">
                        {selectedConversation.budget || 'Not specified'}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 font-semibold uppercase">Tech Stack</p>
                      <div className="flex flex-wrap gap-2 mt-2">
                        {selectedConversation.tech_stack?.map((tech, i) => (
                          <span
                            key={i}
                            className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-medium"
                          >
                            {tech}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Requirements */}
                <div className="p-6 border-b">
                  <h3 className="font-semibold text-gray-900 mb-4">Requirements</h3>
                  <div className="space-y-2">
                    {selectedConversation.requirements?.map((req, i) => (
                      <div key={i} className="flex items-start">
                        <span className="text-blue-500 mr-3 mt-1">✓</span>
                        <span className="text-gray-700">{req}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Transcript */}
                <div className="p-6 border-b">
                  <button
                    onClick={() => setShowTranscript(!showTranscript)}
                    className="w-full text-left font-semibold text-gray-900 py-2 hover:text-blue-600"
                  >
                    {showTranscript ? '▼' : '▶'} Full Transcript ({selectedConversation.transcript?.length || 0} turns)
                  </button>

                  {showTranscript && (
                    <div className="mt-4 bg-gray-50 rounded p-4 max-h-64 overflow-y-auto space-y-3">
                      {selectedConversation.transcript?.map((turn, i) => (
                        <div key={i} className={`p-3 rounded ${
                          turn.role === 'agent' ? 'bg-blue-50' : 'bg-gray-100'
                        }`}>
                          <p className="text-xs font-semibold text-gray-600 uppercase">
                            {turn.role === 'agent' ? '🤖 Agent' : '👤 User'}
                          </p>
                          <p className="text-sm text-gray-800 mt-1">{turn.message}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="p-6 flex gap-3">
                  <button
                    onClick={() => generateDocument(selectedConversation.conversation_id)}
                    className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium"
                  >
                    Generate & Send Document
                  </button>
                  <button
                    onClick={() => {
                      const element = document.createElement('a');
                      element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(
                        `SCOPING CALL TRANSCRIPT\n\nUser: ${selectedConversation.user_name}\nEmail: ${selectedConversation.email}\nProject Type: ${selectedConversation.project_type}\n\n${selectedConversation.transcript?.map(t => `${t.role.toUpperCase()}: ${t.message}`).join('\n\n')}`
                      ));
                      element.setAttribute('download', `scoping-${selectedConversation.user_name.replace(/\s/g, '_')}.txt`);
                      element.click();
                    }}
                    className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 font-medium"
                  >
                    Export Transcript
                  </button>
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-md p-12 text-center">
                <div className="text-6xl mb-4">👇</div>
                <p className="text-gray-600 text-lg">Select a conversation to view details</p>
                <p className="text-gray-500 text-sm mt-2">
                  Click on any conversation in the list to see the full transcript and data
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

/**
 * Stat Card Component
 */
function StatCard({
  label,
  value,
  icon,
  color = 'blue'
}: {
  label: string;
  value: string | number;
  icon: string;
  color?: 'blue' | 'yellow' | 'green' | 'purple';
}) {
  const bgColor = {
    blue: 'bg-blue-50',
    yellow: 'bg-yellow-50',
    green: 'bg-green-50',
    purple: 'bg-purple-50'
  }[color];

  const textColor = {
    blue: 'text-blue-600',
    yellow: 'text-yellow-600',
    green: 'text-green-600',
    purple: 'text-purple-600'
  }[color];

  return (
    <div className={`${bgColor} rounded-lg p-4 border border-${color}-200`}>
      <div className="flex items-center justify-between">
        <div>
          <p className={`text-sm font-medium ${textColor}`}>{label}</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
        </div>
        <span className="text-4xl opacity-50">{icon}</span>
      </div>
    </div>
  );
}
