import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../../services/api';
import { Patient, PaginatedResponse } from '../../types';

const PatientList: React.FC = () => {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchPatients();
  }, [page, search]);

  const fetchPatients = async () => {
    setLoading(true);
    setError('');
    try {
      const response: PaginatedResponse<Patient> = await api.getPatients({
        page,
        page_size: pageSize,
        search: search || undefined,
      });
      setPatients(response.items);
      setTotal(response.total);
    } catch (err) {
      setError('Failed to load patients.');
    } finally {
      setLoading(false);
    }
  };

  const totalPages = Math.ceil(total / pageSize);

  const countRiskFactors = (patient: Patient): number => {
    const riskFields: (keyof Patient)[] = [
      'diabetes' as keyof Patient,
      'hypertension' as keyof Patient,
      'hyperlipidemia' as keyof Patient,
      'cad' as keyof Patient,
      'chf' as keyof Patient,
      'copd' as keyof Patient,
      'renal_insufficiency' as keyof Patient,
    ];
    return riskFields.reduce((count, field) => {
      const value = (patient as Record<string, unknown>)[field];
      return count + (value === true ? 1 : 0);
    }, 0);
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value);
    setPage(1);
  };

  return (
    <div className="patient-list">
      <div className="page-header">
        <h2>Patients</h2>
        <button className="btn-primary" onClick={() => navigate('/patients/new')}>
          New Patient
        </button>
      </div>

      <div className="search-bar">
        <input
          type="text"
          placeholder="Search by name or MRN..."
          value={search}
          onChange={handleSearchChange}
        />
      </div>

      {error && <div className="error-message">{error}</div>}

      {loading ? (
        <div className="loading">Loading patients...</div>
      ) : (
        <>
          <table className="data-table">
            <thead>
              <tr>
                <th>MRN</th>
                <th>Name</th>
                <th>Date of Birth</th>
                <th>Gender</th>
                <th>Hospital</th>
                <th>Risk Factors</th>
              </tr>
            </thead>
            <tbody>
              {patients.length === 0 ? (
                <tr>
                  <td colSpan={6} className="empty-state">
                    No patients found.
                  </td>
                </tr>
              ) : (
                patients.map((patient) => (
                  <tr key={patient.id}>
                    <td>
                      <Link to={`/patients/${patient.id}`}>{patient.mrn}</Link>
                    </td>
                    <td>
                      <Link to={`/patients/${patient.id}`}>
                        {patient.last_name}, {patient.first_name}
                      </Link>
                    </td>
                    <td>{patient.date_of_birth}</td>
                    <td className="capitalize">{patient.gender}</td>
                    <td>{(patient as Record<string, unknown>).hospital_id as string ?? patient.hospital ?? '---'}</td>
                    <td>
                      <span className="badge badge-info">{countRiskFactors(patient)}</span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>

          {totalPages > 1 && (
            <div className="pagination">
              <button
                className="btn-secondary"
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
              >
                Previous
              </button>
              <span className="page-info">
                Page {page} of {totalPages} ({total} total)
              </span>
              <button
                className="btn-secondary"
                disabled={page >= totalPages}
                onClick={() => setPage((p) => p + 1)}
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default PatientList;
