import React, { useState, useEffect, useCallback } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';
import api from '../../services/api';
import { DashboardResponse } from '../../types';

const DashboardPage: React.FC = () => {
  const [hospitalId, setHospitalId] = useState('');
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboard = useCallback(async (id: string) => {
    if (!id.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await api.getDashboard(id);
      setDashboard(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchDashboard(hospitalId);
  };

  const summary = dashboard?.hospital_summary;

  const volumeData = summary?.procedure_volumes.map((v) => ({
    name: v.procedure_type,
    count: v.count,
  })) ?? [];

  const formatRate = (rate: number) => `${(rate * 100).toFixed(2)}%`;

  return (
    <div className="dashboard-page">
      <h1>VQI Georgia Hospital Dashboard</h1>

      <form onSubmit={handleSubmit} style={{ marginBottom: '1.5rem' }}>
        <label htmlFor="hospital-id">Hospital ID: </label>
        <input
          id="hospital-id"
          type="text"
          value={hospitalId}
          onChange={(e) => setHospitalId(e.target.value)}
          placeholder="Enter hospital ID"
        />
        <button type="submit" disabled={loading || !hospitalId.trim()}>
          {loading ? 'Loading...' : 'Load Dashboard'}
        </button>
      </form>

      {error && <div className="error-message">{error}</div>}

      {summary && (
        <>
          {/* Summary Cards */}
          <div className="dashboard-grid">
            <div className="stat-card">
              <h3>Total Procedures</h3>
              <p className="stat-value">{summary.total_procedures}</p>
            </div>
            <div className="stat-card">
              <h3>Total Patients</h3>
              <p className="stat-value">{summary.total_patients}</p>
            </div>
            <div className="stat-card">
              <h3>Audit Completion Rate</h3>
              <p className="stat-value">
                {formatRate(summary.audit_completion_rate)}
              </p>
            </div>
          </div>

          {/* Procedure Volume Chart */}
          <div className="chart-container">
            <h2>Procedure Volume by Type</h2>
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={volumeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#3b82f6" name="Procedures" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Outcome Rates Table */}
          <div className="chart-container">
            <h2>Outcome Rates Comparison</h2>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Outcome</th>
                  <th>Hospital Rate</th>
                  <th>National Rate</th>
                </tr>
              </thead>
              <tbody>
                {summary.outcome_rates.map((outcome) => {
                  const isBetter =
                    outcome.hospital_rate <= outcome.national_rate;
                  return (
                    <tr key={outcome.label}>
                      <td>{outcome.label}</td>
                      <td
                        style={{
                          color: isBetter ? '#16a34a' : '#dc2626',
                          fontWeight: 600,
                        }}
                      >
                        {formatRate(outcome.hospital_rate)}
                      </td>
                      <td>{formatRate(outcome.national_rate)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          <p className="period-label">
            Period: {dashboard.period_start} to {dashboard.period_end}
          </p>
        </>
      )}
    </div>
  );
};

export default DashboardPage;
