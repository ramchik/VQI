import React, { useEffect, useState } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import api from '../../services/api';
import { Patient, Procedure, PaginatedResponse } from '../../types';
import { PROCEDURE_TYPE_LABELS } from '../../types';

const RISK_FACTOR_LABELS: Record<string, string> = {
  diabetes: 'Diabetes',
  hypertension: 'Hypertension',
  hyperlipidemia: 'Hyperlipidemia',
  cad: 'Coronary Artery Disease',
  chf: 'Congestive Heart Failure',
  copd: 'COPD',
  renal_insufficiency: 'Renal Insufficiency',
};

const MEDICATION_LABELS: Record<string, string> = {
  antiplatelet: 'Antiplatelet',
  anticoagulant: 'Anticoagulant',
  statin: 'Statin',
  beta_blocker: 'Beta Blocker',
  ace_inhibitor: 'ACE Inhibitor',
};

const PatientDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [patient, setPatient] = useState<Patient | null>(null);
  const [procedures, setProcedures] = useState<Procedure[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!id) return;
    fetchData();
  }, [id]);

  const fetchData = async () => {
    setLoading(true);
    setError('');
    try {
      const [patientData, procedureData] = await Promise.all([
        api.getPatient(id!),
        api.getProcedures({ patient_id: id }),
      ]);
      setPatient(patientData);
      const procResponse = procedureData as PaginatedResponse<Procedure>;
      setProcedures(procResponse.items ?? procedureData);
    } catch (err) {
      setError('Failed to load patient details.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Loading patient details...</div>;
  if (error) return <div className="error-message">{error}</div>;
  if (!patient) return <div className="error-message">Patient not found.</div>;

  const patientRecord = patient as unknown as Record<string, unknown>;

  const activeRiskFactors = Object.entries(RISK_FACTOR_LABELS).filter(
    ([key]) => patientRecord[key] === true
  );

  const activeMedications = Object.entries(MEDICATION_LABELS).filter(
    ([key]) => patientRecord[key] === true
  );

  return (
    <div className="patient-detail">
      <div className="page-header">
        <h2>
          {patient.last_name}, {patient.first_name}
        </h2>
        <div className="header-actions">
          <button className="btn-secondary" onClick={() => navigate(`/patients/${id}/edit`)}>
            Edit
          </button>
          <button
            className="btn-primary"
            onClick={() => navigate(`/procedures/new?patient_id=${id}`)}
          >
            New Procedure
          </button>
        </div>
      </div>

      <div className="detail-cards">
        <div className="card">
          <h3>Demographics</h3>
          <div className="card-body">
            <div className="field-row">
              <span className="field-label">MRN:</span>
              <span className="field-value">{patient.mrn}</span>
            </div>
            <div className="field-row">
              <span className="field-label">Name:</span>
              <span className="field-value">
                {patient.first_name} {patient.last_name}
              </span>
            </div>
            <div className="field-row">
              <span className="field-label">Date of Birth:</span>
              <span className="field-value">{patient.date_of_birth}</span>
            </div>
            <div className="field-row">
              <span className="field-label">Gender:</span>
              <span className="field-value capitalize">{patient.gender}</span>
            </div>
            <div className="field-row">
              <span className="field-label">Hospital:</span>
              <span className="field-value">
                {(patientRecord.hospital_id as string) ?? '---'}
              </span>
            </div>
            {patientRecord.smoking_status && (
              <div className="field-row">
                <span className="field-label">Smoking Status:</span>
                <span className="field-value capitalize">
                  {patientRecord.smoking_status as string}
                </span>
              </div>
            )}
            {patientRecord.asa_class && (
              <div className="field-row">
                <span className="field-label">ASA Class:</span>
                <span className="field-value">{patientRecord.asa_class as number}</span>
              </div>
            )}
          </div>
        </div>

        <div className="card">
          <h3>Risk Factors</h3>
          <div className="card-body">
            {activeRiskFactors.length === 0 ? (
              <p className="empty-state">No risk factors recorded.</p>
            ) : (
              <div className="badge-list">
                {activeRiskFactors.map(([key, label]) => (
                  <span key={key} className="badge badge-warning">
                    {label}
                  </span>
                ))}
              </div>
            )}
            {patientRecord.creatinine != null && (
              <div className="field-row">
                <span className="field-label">Creatinine:</span>
                <span className="field-value">{patientRecord.creatinine as number} mg/dL</span>
              </div>
            )}
            {patientRecord.bmi != null && (
              <div className="field-row">
                <span className="field-label">BMI:</span>
                <span className="field-value">{patientRecord.bmi as number}</span>
              </div>
            )}
          </div>
        </div>

        <div className="card">
          <h3>Medications</h3>
          <div className="card-body">
            {activeMedications.length === 0 ? (
              <p className="empty-state">No medications recorded.</p>
            ) : (
              <div className="badge-list">
                {activeMedications.map(([key, label]) => (
                  <span key={key} className="badge badge-info">
                    {label}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="section">
        <div className="section-header">
          <h3>Procedures</h3>
        </div>
        {procedures.length === 0 ? (
          <p className="empty-state">No procedures recorded for this patient.</p>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Type</th>
                <th>Status</th>
                <th>Urgency</th>
                <th>Hospital</th>
              </tr>
            </thead>
            <tbody>
              {procedures.map((proc) => (
                <tr key={proc.id}>
                  <td>
                    <Link to={`/procedures/${proc.id}`}>{proc.procedure_date}</Link>
                  </td>
                  <td>{PROCEDURE_TYPE_LABELS[proc.procedure_type] ?? proc.procedure_type}</td>
                  <td>
                    <span className={`badge badge-status-${proc.status}`}>{proc.status}</span>
                  </td>
                  <td className="capitalize">{proc.urgency}</td>
                  <td>{proc.hospital ?? (proc as unknown as Record<string, unknown>).hospital_id as string ?? '---'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default PatientDetail;
