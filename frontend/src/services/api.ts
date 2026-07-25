// frontend/src/services/api.ts
// Central API client — all backend calls go through here
// Change BASE_URL for production deployment

import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8080',
  withCredentials: true,  // sends session cookie with every request
})

// Companies
export const createCompany = (data: { name: string; sector?: string }) =>
  api.post('/companies/', data)

export const getMyCompany = () =>
  api.get('/companies/me')

// Documents
export const uploadDocument = (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/documents/upload', formData)
}

export const getDocumentStatus = (id: string) =>
  api.get(`/documents/${id}/status`)

export const getAllDocuments = () =>
  api.get('/documents/')

// Financial
export const getPnLOverview = () =>
  api.get('/financial/pnl')

export const getLatestBalanceSheet = () =>
  api.get('/financial/balance-sheet/latest')

// Anomalies
export const getAnomalies = (resolved?: boolean) =>
  api.get('/anomalies/', { params: { resolved } })

export const getUnresolvedCount = () =>
  api.get('/anomalies/unresolved/count')

export const resolveAnomaly = (id: string) =>
  api.patch(`/anomalies/${id}/resolve`, { resolved: true })

// Chat
export const askQuestion = (question: string, documentId?: string) =>
  api.post('/chat/', { question, document_id: documentId })

export default api