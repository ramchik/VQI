import React, { useState, useEffect, useCallback } from 'react';
import api from '../../services/api';
import { AuditRecord } from '../../types';

interface AuditFormState {
  data_accurate: boolean;
  discrepancies_found: boolean;
  notes: string;
}

const AuditPage: React.FC = () => {
  const [hospitalId, setHospitalId] = useState('');
  const [records, setRecords] = useState<AuditRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectingCases, setSelectingCases] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formState, setFormState] = useState<AuditFormState>({
    data_accurate: true,
    discrepancies_found: false,
    notes: '',
  });

  const fetchRecords = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getAuditRecords();
      setRecords(data.items);
    } catch (err: any) {
      setError(err.message || 'Failed to load audit records');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRecords();
  }, [fetchRecords]);

  const handleSelectCases = async () => {
    if (!hospitalId.trim()) return;
    setSelectingCases(true);
    setError(null);
    try {
      await api.selectAuditCases(hospitalId);
      await fetchRecords();
    } catch (err: any) {
      setError(err.message || 'Failed to select audit cases');
    } finally {
      setSelectingCases(false);
    }
  };

  const handleCompleteAudit = async (auditId: string) => {
    setError(null);
    try {
      await api.completeAudit(auditId, {
        data_accurate: formState.data_accurate,
        discrepancies_found: formState.discrepancies_found,
        notes: formState.notes,
      });
      setEditingId(null);
      setFormState({ data_accurate: true, discrepancies_found: false, notes: '' });
      await fetchRecords();
    } catch (err: any) {
      setError(err.message || 'Failed to complete audit');
    }
  };

  const openEditForm = (auditId: string) => {
    setEditingId(auditId);
    setFormState({ data_accurate: true, discrepancies_found: false, notes: '' });
  };

  const getStatusBadge = (status: string) => {
    const colorMap: Record<string, string> = {
      pending: '#f59e0b',
      in_progress: '#3b82f6',
      completed: '#16a34a',
    };
    const color = colorMap[status] || '#6b7280';

    return (
      <span
        className="status-badge"
        style={{
          backgroundColor: color,
          color: '#fff',
          padding: '0.25rem 0.75rem',
          borderRadius: '9999px',
          fontSize: '0.8rem',
          fontWeight: 600,
        }}
      >
        {status.replace('_', ' ')}
      </span>
    );
  };

  return (
    <div className="audit-page">
      <h1>Audit Management</h1>

      {/* Select Cases Section */}
      <div style={{ marginBottom: '1.5rem' }}>
        <label htmlFor="audit-hospital-id">Hospital ID: </label>
        <input
          id="audit-hospital-id"
          type="text"
          value={hospitalId}
          onChange={(e) => setHospitalId(e.target.value)}
          placeholder="Enter hospital ID"
        />
        <button
          onClick={handleSelectCases}
          disabled={selectingCases || !hospitalId.trim()}
          style={{ marginLeft: '0.5rem' }}
        >
          {selectingCases ? 'Selecting...' : 'Select Cases for Audit'}
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {loading ? (
        <div className="loading-spinner">Loading audit records...</div>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              <th>Procedure ID</th>
              <th>Status</th>
              <th>Selected Date</th>
              <th>Accurate</th>
              <th>Discrepancies</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {records.map((record) => (
              <React.Fragment key={record.id}>
                <tr>
                  <td>{record.procedure_id}</td>
                  <td>{getStatusBadge(record.status)}</td>
                  <td>
                    {record.selected_at
                      ? new Date(record.selected_at).toLocaleDateString()
                      : '-'}
                  </td>
                  <td>
                    {record.data_accurate == null
                      ? '-'
                      : record.data_accurate
                        ? 'Yes'
                        : 'No'}
                  </td>
                  <td>
                    {record.discrepancies_found == null
                      ? '-'
                      : record.discrepancies_found
                        ? 'Yes'
                        : 'No'}
                  </td>
                  <td>
                    {(record.status === 'pending' ||
                      record.status === 'in_progress') && (
                      <button onClick={() => openEditForm(record.id)}>
                        Complete Audit
                      </button>
                    )}
                  </td>
                </tr>
                {editingId === record.id && (
                  <tr>
                    <td colSpan={6}>
                      <div
                        className="audit-form"
                        style={{
                          padding: '1rem',
                          backgroundColor: '#f9fafb',
                          borderRadius: '0.5rem',
                        }}
                      >
                        <div style={{ marginBottom: '0.75rem' }}>
                          <label>
                            <input
                              type="checkbox"
                              checked={formState.data_accurate}
                              onChange={(e) =>
                                setFormState((s) => ({
                                  ...s,
                                  data_accurate: e.target.checked,
                                }))
                              }
                            />{' '}
                            Data Accurate
                          </label>
                        </div>
                        <div style={{ marginBottom: '0.75rem' }}>
                          <label>
                            <input
                              type="checkbox"
                              checked={formState.discrepancies_found}
                              onChange={(e) =>
                                setFormState((s) => ({
                                  ...s,
                                  discrepancies_found: e.target.checked,
                                }))
                              }
                            />{' '}
                            Discrepancies Found
                          </label>
                        </div>
                        <div style={{ marginBottom: '0.75rem' }}>
                          <label>
                            Notes:
                            <br />
                            <textarea
                              rows={3}
                              value={formState.notes}
                              onChange={(e) =>
                                setFormState((s) => ({
                                  ...s,
                                  notes: e.target.value,
                                }))
                              }
                              style={{ width: '100%', marginTop: '0.25rem' }}
                            />
                          </label>
                        </div>
                        <button
                          onClick={() => handleCompleteAudit(record.id)}
                          style={{ marginRight: '0.5rem' }}
                        >
                          Submit
                        </button>
                        <button onClick={() => setEditingId(null)}>
                          Cancel
                        </button>
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
            {records.length === 0 && (
              <tr>
                <td colSpan={6} style={{ textAlign: 'center' }}>
                  No audit records found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default AuditPage;
