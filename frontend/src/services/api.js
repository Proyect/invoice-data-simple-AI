import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8006';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// Interceptor para manejar errores
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const documentAPI = {
  // Subir documento simple
  uploadSimple: (file, documentType = 'factura') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', documentType);
    
    return api.post('/api/v1/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // Subir documento flexible
  uploadFlexible: (file, documentType = 'factura', ocrMethod = 'auto', extractionMethod = 'auto') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', documentType);
    formData.append('ocr_method', ocrMethod);
    formData.append('extraction_method', extractionMethod);
    
    return api.post('/api/v1/upload-flexible', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // Listar documentos
  getDocuments: (skip = 0, limit = 10, search = null) => {
    const params = { skip, limit };
    if (search) params.search = search;
    
    return api.get('/api/v1/documents', { params });
  },

  // Obtener documento específico
  getDocument: (id) => {
    return api.get(`/api/v1/documents/${id}`);
  },

  // Obtener métodos disponibles
  getAvailableMethods: () => {
    return api.get('/api/v1/upload-flexible/methods');
  },

  // Health check
  getHealth: () => {
    return api.get('/health');
  },

  // Info del sistema
  getInfo: () => {
    return api.get('/info');
  },
};

export default api;
