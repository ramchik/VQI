import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
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
import { SurgeonReportCard } from '../../types';

const SurgeonReport: React.FC = () => {
  const { surgeon_id } = useParams<{ surgeon_id: string }>();
  const [report, setReport] = useState<SurgeonReportCard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!surgeon_id) return;

    const fetchReport = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await api.getSurgeonReport(surgeon_id);
        setReport(data);
      } catch (err: any) {
        setError(err.message || 'Failed to load surgeon report');
      } finally {
        setLoading(false);
      }
    };

    fetchReport();
  }, [surgeon_id]);

  if (loading) {
    return <div className="loading-spinner">Loading surgeon report...</div>;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  if (!report) {
    return <div className="error-message">No report data available.</div>;
  }

  const volumeData = report.procedure_volumes.map((v) => ({
    name: v.procedure_type,
    count: v.count,
  }));

  const formatRate = (rate: number) => `${(rate * 100).toFixed(2)}%`;

  return (
    <div className="surgeon-report">
      <h1>Surgeon Report Card</h1>

      <div className="dashboard-grid">
        <div className="stat-card">
          <h3>Surgeon</h3>
          <p className="stat-value">{report.surgeon_name}</p>
        </div>
        <div className="stat-card">
          <h3>Total Procedures</h3>
          <p className="stat-value">{report.total_procedures}</p>
        </div>
      </div>

      {/* Procedure Volumes - Horizontal Bar Chart */}
      <div className="chart-container">
        <h2>Procedure Volumes</h2>
        <ResponsiveContainer width="100%" height={Math.max(250, volumeData.length * 50)}>
          <BarChart data={volumeData} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" allowDecimals={false} />
            <YAxis type="category" dataKey="name" width={180} />
            <Tooltip />
            <Bar dataKey="count" fill="#6366f1" name="Procedures" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Outcome Rates Comparison Table */}
      <div className="chart-container">
        <h2>Outcome Rates</h2>
        <table className="data-table">
          <thead>
            <tr>
              <th>Outcome</th>
              <th>Surgeon Rate</th>
              <th>National Rate</th>
            </tr>
          </thead>
          <tbody>
            {report.outcome_rates.map((outcome) => {
              const isBetter = outcome.hospital_rate <= outcome.national_rate;
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

      {report.risk_adjusted_mortality != null && (
        <div className="stat-card" style={{ marginTop: '1rem' }}>
          <h3>Risk-Adjusted Mortality</h3>
          <p className="stat-value">{formatRate(report.risk_adjusted_mortality)}</p>
        </div>
      )}
      {report.risk_adjusted_morbidity != null && (
        <div className="stat-card" style={{ marginTop: '1rem' }}>
          <h3>Risk-Adjusted Morbidity</h3>
          <p className="stat-value">{formatRate(report.risk_adjusted_morbidity)}</p>
        </div>
      )}
    </div>
  );
};

export default SurgeonReport;
