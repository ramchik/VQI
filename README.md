# VQI Georgia

A vascular surgery quality registry for Georgia, modeled after the US Vascular Quality Initiative (VQI) platform (powered by FIVOS PATHWAYS). The system manages the entire lifecycle of patient surgical data across 14 vascular procedures (aneurysm repairs, carotid stents, bypasses, and more), enabling hospitals and surgeons to track outcomes and improve quality of care.

## Core Functions

### Longitudinal Data Collection

The system tracks each patient across four stages of care:

1. **Pre-operative** — Risk factors such as smoking, diabetes, medications, and patient demographics.
2. **Intra-operative** — Surgical details including device used, blood loss, operative time, and technique.
3. **Post-operative** — Immediate outcomes recorded before hospital discharge.
4. **1-Year Follow-up** — Long-term outcomes: graft patency, survival, reintervention rates.

### Real-Time Benchmarking

Surgeons and hospitals can see how their complication rates compare to the national average or to other hospitals in their region — instantly and anonymously. This is the primary value driver of the platform.

### Risk-Adjusted Reporting

Statistical models ensure fair comparisons between institutions. Hospitals that take on higher-acuity patients have their scores adjusted so they are not penalized relative to clinics handling simpler cases. This uses Expected vs. Observed outcome analysis via logistic regression.

## Technical Architecture

### A. Input Layer (Data Capture)

- **Web-Based Forms** — Highly structured forms with strict validation (e.g., a heart rate of 500 is rejected). Optimized for speed and accuracy.
- **EHR Integration (HL7/FHIR)** — Data is pulled directly from Electronic Health Records via standardized APIs to eliminate double entry by clinical staff.
- **Data Abstractor UI** — The interface is purpose-built for data abstractors (specialized nurses who review charts and populate the registry).

### B. Processing Layer (Logic)

- **Registry Modules** — Each of the 14 procedures (e.g., "Varicose Vein," "Carotid Endarterectomy") has its own data model and schema.
- **Statistical Engine** — The back-end runs R or Python scripts to calculate Expected vs. Observed outcomes using logistic regression models.
- **Audit Logic** — A built-in data audit feature randomly selects 10% of cases for accuracy verification.

### C. Output Layer (Dashboards)

- **Biannual Dashboards** — Static and interactive reports (PowerBI/Tableau-style) showing trends over time.
- **Physician Report Cards** — Private views for individual doctors to review their own performance metrics.

## Legal and Clinical Trust

In the US, VQI operates as a **Patient Safety Organization (PSO)**, a legal designation that protects reported data from being used in lawsuits (legal discovery). This protection is essential — doctors must feel safe reporting complications and adverse events without fear of litigation.

**For Georgia:** A corresponding legal framework must be established so that clinicians can report honest data. Without legal protection, participation and data quality will suffer. This is a prerequisite for the registry's success.

## Technical Roadmap for VQI Georgia

| Component | Technical Requirement |
|---|---|
| **Data Standard** | HL7 FHIR for interoperability with Georgian hospital systems |
| **Security** | End-to-end encryption; compliance with local data residency laws for medical data |
| **Architecture** | Cloud-native (AWS/Azure) with a Single Page Application (React/Vue) optimized for high-speed data entry |
| **Analytics** | Reporting engine capable of complex SQL queries to compare individual hospital averages against the national average |
| **Localization** | Georgian language support, with English retained for international research collaboration |

## License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.
