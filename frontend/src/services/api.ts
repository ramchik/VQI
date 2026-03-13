import axios from 'axios';
import type {
  User,
  Patient,
  Procedure,
  PreOperativeData,
  IntraOperativeData,
  PostOperativeData,
  FollowUpData,
  DashboardData,
  SurgeonReport,
  AuditRecord,
  PaginatedResponse,
  LoginResponse,
} from '../types';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: attach auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: handle 401 globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      // Redirect to login if not already there
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// ─── Auth ────────────────────────────────────────────────────────────────────

export async function login(email: string, password: string): Promise<LoginResponse> {
  // OAuth2 password flow uses form-encoded body
  const params = new URLSearchParams();
  params.append('username', email);
  params.append('password', password);
  const { data } = await api.post<LoginResponse>('/api/auth/login', params, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
  return data;
}

export async function register(payload: {
  email: string;
  password: string;
  full_name: string;
  role?: string;
  institution?: string;
  npi_number?: string;
}): Promise<User> {
  const { data } = await api.post<User>('/api/auth/register', payload);
  return data;
}

export async function getMe(): Promise<User> {
  const { data } = await api.get<User>('/api/auth/me');
  return data;
}

// ─── Patients ────────────────────────────────────────────────────────────────

export async function getPatients(params?: {
  page?: number;
  page_size?: number;
  search?: string;
  surgeon_id?: number;
}): Promise<PaginatedResponse<Patient>> {
  const { data } = await api.get<PaginatedResponse<Patient>>('/api/patients', { params });
  return data;
}

export async function getPatient(id: number): Promise<Patient> {
  const { data } = await api.get<Patient>(`/api/patients/${id}`);
  return data;
}

export async function createPatient(patient: Partial<Patient>): Promise<Patient> {
  const { data } = await api.post<Patient>('/api/patients', patient);
  return data;
}

export async function updatePatient(id: number, patient: Partial<Patient>): Promise<Patient> {
  const { data } = await api.put<Patient>(`/api/patients/${id}`, patient);
  return data;
}

export async function deletePatient(id: number): Promise<void> {
  await api.delete(`/api/patients/${id}`);
}

// ─── Procedures ──────────────────────────────────────────────────────────────

export async function getProcedures(params?: {
  page?: number;
  page_size?: number;
  patient_id?: number;
  surgeon_id?: number;
  procedure_type?: string;
  status?: string;
  date_from?: string;
  date_to?: string;
}): Promise<PaginatedResponse<Procedure>> {
  const { data } = await api.get<PaginatedResponse<Procedure>>('/api/procedures', { params });
  return data;
}

export async function getProcedure(id: number): Promise<Procedure> {
  const { data } = await api.get<Procedure>(`/api/procedures/${id}`);
  return data;
}

export async function createProcedure(procedure: Partial<Procedure>): Promise<Procedure> {
  const { data } = await api.post<Procedure>('/api/procedures', procedure);
  return data;
}

export async function addPreOperative(
  procedureId: number,
  payload: Partial<PreOperativeData>
): Promise<PreOperativeData> {
  const { data } = await api.post<PreOperativeData>(
    `/api/procedures/${procedureId}/pre-operative`,
    payload
  );
  return data;
}

export async function addIntraOperative(
  procedureId: number,
  payload: Partial<IntraOperativeData>
): Promise<IntraOperativeData> {
  const { data } = await api.post<IntraOperativeData>(
    `/api/procedures/${procedureId}/intra-operative`,
    payload
  );
  return data;
}

export async function addPostOperative(
  procedureId: number,
  payload: Partial<PostOperativeData>
): Promise<PostOperativeData> {
  const { data } = await api.post<PostOperativeData>(
    `/api/procedures/${procedureId}/post-operative`,
    payload
  );
  return data;
}

export async function addFollowUp(
  procedureId: number,
  payload: Partial<FollowUpData>
): Promise<FollowUpData> {
  const { data } = await api.post<FollowUpData>(
    `/api/procedures/${procedureId}/follow-up`,
    payload
  );
  return data;
}

// ─── Dashboard & Reports ─────────────────────────────────────────────────────

export async function getDashboard(params?: {
  date_from?: string;
  date_to?: string;
}): Promise<DashboardData> {
  const { data } = await api.get<DashboardData>('/api/dashboard', { params });
  return data;
}

export async function getSurgeonReport(
  surgeonId: number,
  params?: { date_from?: string; date_to?: string }
): Promise<SurgeonReport> {
  const { data } = await api.get<SurgeonReport>(`/api/reports/surgeon/${surgeonId}`, { params });
  return data;
}

// ─── Audit ───────────────────────────────────────────────────────────────────

export async function getAuditRecords(params?: {
  page?: number;
  page_size?: number;
  status?: string;
}): Promise<PaginatedResponse<AuditRecord>> {
  const { data } = await api.get<PaginatedResponse<AuditRecord>>('/api/audit', { params });
  return data;
}

export async function selectAuditCases(payload: {
  procedure_ids?: number[];
  random_count?: number;
  date_from?: string;
  date_to?: string;
}): Promise<AuditRecord[]> {
  const { data } = await api.post<AuditRecord[]>('/api/audit/select', payload);
  return data;
}

export async function completeAudit(
  auditId: number,
  payload: {
    findings?: string;
    discrepancies?: Record<string, string>;
    risk_adjusted_score?: number;
    notes?: string;
  }
): Promise<AuditRecord> {
  const { data } = await api.put<AuditRecord>(`/api/audit/${auditId}/complete`, payload);
  return data;
}

export default api;
