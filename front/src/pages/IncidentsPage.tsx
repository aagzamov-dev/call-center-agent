import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { listIncidents } from '../api/incidents';
import { runScenario } from '../api/demo';
import { injectAlert } from '../api/alerts';
import { formatDate, severityClass } from '../lib/utils';

const SCENARIOS = ['disk_full', 'cpu_spike', 'db_connections', 'network_blocked', 'cert_expired'];
const SCENARIO_LABELS: Record<string, string> = {
    disk_full: '💾 Disk Full', cpu_spike: '🔥 CPU Spike', db_connections: '🔌 DB Connections',
    network_blocked: '🚧 Network Blocked', cert_expired: '🔐 Cert Expired',
};

export default function IncidentsPage() {
    const nav = useNavigate();
    const qc = useQueryClient();
    const { data, isLoading } = useQuery({ queryKey: ['incidents'], queryFn: () => listIncidents(), refetchInterval: 5000 });

    const scenarioMut = useMutation({
        mutationFn: runScenario,
        onSuccess: (d) => { qc.invalidateQueries({ queryKey: ['incidents'] }); nav(`/incidents/${d.incident_id}`); },
    });

    const [showAlert, setShowAlert] = useState(false);
    const [alertForm, setAlertForm] = useState({ host: '', service: '', severity: 'high', title: '', description: '' });
    const alertMut = useMutation({
        mutationFn: () => injectAlert({ alert_id: `manual-${Date.now()}`, ...alertForm, tags: {} }),
        onSuccess: (d) => { qc.invalidateQueries({ queryKey: ['incidents'] }); nav(`/incidents/${d.incident_id}`); setShowAlert(false); },
    });

    return (
        <div>
            <div className="flex items-center justify-between mb-4">
                <h1>Incidents</h1>
                <button className="btn btn-secondary" onClick={() => setShowAlert(!showAlert)}>
                    {showAlert ? '✕ Close' : '+ Inject Alert'}
                </button>
            </div>

            {/* Scenario buttons */}
            <div className="card mb-4">
                <div className="card-header"><span className="card-title">🚀 Demo Scenarios</span></div>
                <div className="flex gap-2" style={{ flexWrap: 'wrap' }}>
                    {SCENARIOS.map((s) => (
                        <button key={s} className="btn btn-secondary" onClick={() => scenarioMut.mutate(s)}
                            disabled={scenarioMut.isPending}>
                            {SCENARIO_LABELS[s] || s}
                        </button>
                    ))}
                </div>
            </div>

            {/* Alert injection form */}
            {showAlert && (
                <div className="card mb-4">
                    <div className="card-header"><span className="card-title">🔔 Inject Custom Alert</span></div>
                    <div className="flex-col gap-3">
                        <div className="flex gap-3">
                            <div className="form-group w-full">
                                <label className="form-label">Host</label>
                                <input className="form-input" value={alertForm.host} onChange={(e) => setAlertForm({ ...alertForm, host: e.target.value })} placeholder="db-prod-01" />
                            </div>
                            <div className="form-group w-full">
                                <label className="form-label">Service</label>
                                <input className="form-input" value={alertForm.service} onChange={(e) => setAlertForm({ ...alertForm, service: e.target.value })} placeholder="postgresql" />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Severity</label>
                                <select className="form-select" value={alertForm.severity} onChange={(e) => setAlertForm({ ...alertForm, severity: e.target.value })}>
                                    <option value="critical">Critical</option>
                                    <option value="high">High</option>
                                    <option value="medium">Medium</option>
                                    <option value="low">Low</option>
                                </select>
                            </div>
                        </div>
                        <div className="form-group">
                            <label className="form-label">Title</label>
                            <input className="form-input" value={alertForm.title} onChange={(e) => setAlertForm({ ...alertForm, title: e.target.value })} placeholder="CPU > 90% on api-gw-01" />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Description</label>
                            <textarea className="form-textarea" value={alertForm.description} onChange={(e) => setAlertForm({ ...alertForm, description: e.target.value })} placeholder="Detailed description..." />
                        </div>
                        <button className="btn btn-primary" onClick={() => alertMut.mutate()} disabled={alertMut.isPending || !alertForm.host || !alertForm.title}>
                            {alertMut.isPending ? 'Sending...' : 'Send Alert'}
                        </button>
                    </div>
                </div>
            )}

            {/* Incident list */}
            {isLoading ? (
                <div className="empty-state"><div className="spinner" /></div>
            ) : !data?.items?.length ? (
                <div className="empty-state">
                    <span style={{ fontSize: 32 }}>📭</span>
                    <p>No incidents yet. Launch a scenario above!</p>
                </div>
            ) : (
                <div className="flex-col gap-2">
                    {data.items.map((inc: Record<string, string | number>) => (
                        <div key={inc.id as string} className="card" style={{ cursor: 'pointer' }} onClick={() => nav(`/incidents/${inc.id}`)}>
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <span className={`badge ${severityClass(inc.severity as string)}`}>{(inc.severity as string).toUpperCase()}</span>
                                    <div>
                                        <div style={{ fontWeight: 600 }}>{inc.title as string}</div>
                                        <div className="text-xs text-muted">{inc.host as string} · {inc.service as string} · {inc.event_count as number} events</div>
                                    </div>
                                </div>
                                <div className="text-xs text-muted">{formatDate(inc.created_at as string)}</div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
