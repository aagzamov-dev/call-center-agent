import { useState, useRef, useEffect } from 'react';
import { sendMessage, transcribeVoice } from '../api/chat';

interface ChatMsg {
    id: number;
    role: 'user' | 'agent' | 'system';
    content: string;
    ticket?: Record<string, unknown> | null;
}

export default function UserChatPage() {
    const [messages, setMessages] = useState<ChatMsg[]>([
        { id: 0, role: 'agent', content: "Hello! 👋 I'm your support assistant. How can I help you today?\n\nYou can ask me about:\n• Laptop or software issues\n• VPN or network problems\n• Account & password help\n• Sales & licensing questions\n• Security concerns" },
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [recording, setRecording] = useState(false);
    const [mediaRec, setMediaRec] = useState<MediaRecorder | null>(null);
    const bottomRef = useRef<HTMLDivElement>(null);

    useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

    const send = async () => {
        if (!input.trim() || loading) return;
        const text = input.trim();
        setInput('');
        const userMsg: ChatMsg = { id: Date.now(), role: 'user', content: text };
        setMessages((m) => [...m, userMsg]);
        setLoading(true);
        try {
            const res = await sendMessage(text);
            const agentMsg: ChatMsg = { id: Date.now() + 1, role: 'agent', content: res.reply, ticket: res.ticket };
            setMessages((m) => [...m, agentMsg]);
        } catch {
            setMessages((m) => [...m, { id: Date.now() + 1, role: 'system', content: '❌ Failed to get response. Please try again.' }]);
        }
        setLoading(false);
    };

    const startRec = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const mr = new MediaRecorder(stream);
            const chunks: BlobPart[] = [];
            mr.ondataavailable = (e) => chunks.push(e.data);
            mr.onstop = async () => {
                stream.getTracks().forEach((t) => t.stop());
                const blob = new Blob(chunks, { type: 'audio/webm' });
                setLoading(true);
                try {
                    const res = await transcribeVoice(blob);
                    setMessages((m) => [
                        ...m,
                        { id: Date.now(), role: 'user', content: `🎤 ${res.transcript}` },
                        { id: Date.now() + 1, role: 'agent', content: res.reply, ticket: res.ticket },
                    ]);
                } catch {
                    setMessages((m) => [...m, { id: Date.now(), role: 'system', content: '❌ Voice transcription failed.' }]);
                }
                setLoading(false);
            };
            mr.start();
            setMediaRec(mr);
            setRecording(true);
        } catch {
            alert('Microphone access denied');
        }
    };

    const stopRec = () => { mediaRec?.stop(); setRecording(false); };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 56px - 48px)' }}>
            {/* Messages */}
            <div style={{ flex: 1, overflowY: 'auto', padding: '20px 0' }}>
                {messages.map((msg) => (
                    <div key={msg.id} style={{ display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start', padding: '4px 0' }}>
                        <div style={{
                            maxWidth: '70%',
                            padding: '12px 16px',
                            borderRadius: msg.role === 'user' ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
                            background: msg.role === 'user' ? 'var(--accent)' : msg.role === 'system' ? 'var(--danger)' : 'var(--bg-card)',
                            color: msg.role === 'user' ? '#fff' : 'var(--text)',
                            border: msg.role === 'agent' ? '1px solid var(--border)' : 'none',
                            whiteSpace: 'pre-wrap', fontSize: '0.9rem', lineHeight: 1.5,
                        }}>
                            {msg.content}
                            {msg.ticket && (
                                <div style={{
                                    marginTop: 10, padding: '10px 12px', borderRadius: 'var(--radius-sm)',
                                    background: 'rgba(34,197,94,0.1)', border: '1px solid rgba(34,197,94,0.3)',
                                }}>
                                    <span style={{ fontWeight: 600, color: 'var(--success)' }}>🎫 Ticket Created</span>
                                    <div className="text-sm" style={{ marginTop: 4 }}>
                                        <strong>{msg.ticket.id as string}</strong> · {msg.ticket.team as string} · {msg.ticket.priority as string}
                                    </div>
                                    <div className="text-xs text-muted">{msg.ticket.title as string}</div>
                                </div>
                            )}
                        </div>
                    </div>
                ))}
                {loading && (
                    <div style={{ display: 'flex', padding: '4px 0' }}>
                        <div style={{ padding: '12px 16px', borderRadius: '16px 16px 16px 4px', background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
                            <div className="flex items-center gap-2"><div className="spinner" /> <span className="text-sm text-muted">Thinking...</span></div>
                        </div>
                    </div>
                )}
                <div ref={bottomRef} />
            </div>

            {/* Input */}
            <div style={{ flexShrink: 0, borderTop: '1px solid var(--border)', padding: 16, background: 'var(--bg-secondary)' }}>
                <div className="flex gap-2">
                    <button className={`btn ${recording ? 'btn-danger' : 'btn-secondary'} btn-icon`} onClick={recording ? stopRec : startRec} title="Voice input">
                        {recording ? '⏹' : '🎤'}
                    </button>
                    <input
                        className="form-input w-full"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => { if (e.key === 'Enter') send(); }}
                        placeholder="Type your message..."
                        disabled={loading}
                        style={{ fontSize: '0.95rem', padding: '10px 14px' }}
                    />
                    <button className="btn btn-primary" onClick={send} disabled={!input.trim() || loading}>Send</button>
                </div>
            </div>
        </div>
    );
}
