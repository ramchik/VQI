// VQI Georgia - TypeScript Type Definitions

export enum ProcedureType {
  CAROTID_ENDARTERECTOMY = 'carotid_endarterectomy',
  CAROTID_STENT = 'carotid_stent',
  OPEN_AAA = 'open_aaa',
  EVAR = 'evar',
  SUPRAINGUINAL_BYPASS = 'suprainguinal_bypass',
  INFRAINGUINAL_BYPASS = 'infrainguinal_bypass',
  PVI = 'pvi',
  VARICOSE_VEIN = 'varicose_vein',
  HEMODIALYSIS_ACCESS = 'hemodialysis_access',
  THORACIC_ENDOVASCULAR = 'thoracic_endovascular',
  IVC_FILTER = 'ivc_filter',
  UPPER_EXTREMITY_BYPASS = 'upper_extremity_bypass',
  VISCERAL_AORTIC_INTERVENTION = 'visceral_aortic_intervention',
  AMPUTATION = 'amputation',
}

export const PROCEDURE_TYPE_LABELS: Record<ProcedureType, string> = {
  [ProcedureType.CAROTID_ENDARTERECTOMY]: 'Carotid Endarterectomy',
  [ProcedureType.CAROTID_STENT]: 'Carotid Stent',
  [ProcedureType.OPEN_AAA]: 'Open AAA Repair',
  [ProcedureType.EVAR]: 'Endovascular Aneurysm Repair (EVAR)',
  [ProcedureType.SUPRAINGUINAL_BYPASS]: 'Suprainguinal Bypass',
  [ProcedureType.INFRAINGUINAL_BYPASS]: 'Infrainguinal Bypass',
  [ProcedureType.PVI]: 'Peripheral Vascular Intervention (PVI)',
  [ProcedureType.VARICOSE_VEIN]: 'Varicose Vein Treatment',
  [ProcedureType.HEMODIALYSIS_ACCESS]: 'Hemodialysis Access',
  [ProcedureType.THORACIC_ENDOVASCULAR]: 'Thoracic Endovascular Repair',
  [ProcedureType.IVC_FILTER]: 'IVC Filter',
  [ProcedureType.UPPER_EXTREMITY_BYPASS]: 'Upper Extremity Bypass',
  [ProcedureType.VISCERAL_AORTIC_INTERVENTION]: 'Visceral Aortic Intervention',
  [ProcedureType.AMPUTATION]: 'Amputation',
};

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: 'surgeon' | 'registrar' | 'admin' | 'auditor';
  institution?: string;
  npi_number?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Patient {
  id: number;
  mrn: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender: 'male' | 'female' | 'other';
  race?: string;
  ethnicity?: string;
  phone?: string;
  email?: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  insurance_type?: string;
  insurance_id?: string;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  primary_surgeon_id?: number;
  primary_surgeon?: User;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface PreOperativeData {
  id: number;
  procedure_id: number;
  symptoms?: string;
  indication?: string;
  comorbidities?: Record<string, boolean | string>;
  medications?: Record<string, boolean | string>;
  lab_results?: Record<string, number | string>;
  imaging_results?: string;
  risk_score?: number;
  asa_class?: number;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface IntraOperativeData {
  id: number;
  procedure_id: number;
  anesthesia_type?: string;
  incision_type?: string;
  graft_type?: string;
  graft_material?: string;
  shunt_used?: boolean;
  contrast_volume_ml?: number;
  fluoroscopy_time_min?: number;
  estimated_blood_loss_ml?: number;
  operative_time_min?: number;
  technical_success?: boolean;
  complications?: Record<string, boolean | string>;
  devices_used?: Array<Record<string, string>>;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface PostOperativeData {
  id: number;
  procedure_id: number;
  discharge_date?: string;
  discharge_disposition?: string;
  length_of_stay_days?: number;
  complications?: Record<string, boolean | string>;
  mortality_30_day?: boolean;
  readmission_30_day?: boolean;
  reintervention_30_day?: boolean;
  stroke?: boolean;
  mi?: boolean;
  wound_complication?: boolean;
  aki?: boolean;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface FollowUpData {
  id: number;
  procedure_id: number;
  follow_up_date: string;
  follow_up_interval?: string;
  patency_status?: string;
  symptoms?: string;
  imaging_results?: string;
  reintervention?: boolean;
  reintervention_type?: string;
  amputation?: boolean;
  mortality?: boolean;
  mortality_date?: string;
  mortality_cause?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface Procedure {
  id: number;
  patient_id: number;
  patient?: Patient;
  surgeon_id: number;
  surgeon?: User;
  procedure_type: ProcedureType;
  procedure_date: string;
  urgency: 'elective' | 'urgent' | 'emergent';
  hospital?: string;
  status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled';
  pre_operative?: PreOperativeData;
  intra_operative?: IntraOperativeData;
  post_operative?: PostOperativeData;
  follow_ups?: FollowUpData[];
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface OutcomeRate {
  label: string;
  rate: number;
  count: number;
  total: number;
  benchmark?: number;
}

export interface ProcedureVolume {
  period: string;
  count: number;
  procedure_type?: ProcedureType;
}

export interface DashboardData {
  total_patients: number;
  total_procedures: number;
  procedures_this_month: number;
  active_patients: number;
  outcome_rates: OutcomeRate[];
  procedure_volumes: ProcedureVolume[];
  procedure_type_distribution: Record<string, number>;
  recent_procedures: Procedure[];
  mortality_rate: number;
  complication_rate: number;
  readmission_rate: number;
}

export interface AuditRecord {
  id: number;
  procedure_id: number;
  procedure?: Procedure;
  auditor_id?: number;
  auditor?: User;
  audit_status: 'pending' | 'selected' | 'in_progress' | 'completed' | 'flagged';
  audit_date?: string;
  findings?: string;
  discrepancies?: Record<string, string>;
  risk_adjusted_score?: number;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface SurgeonReport {
  surgeon: User;
  total_procedures: number;
  procedures_by_type: Record<string, number>;
  outcome_rates: OutcomeRate[];
  benchmark_comparisons: Record<string, { actual: number; benchmark: number }>;
  period_start: string;
  period_end: string;
}
