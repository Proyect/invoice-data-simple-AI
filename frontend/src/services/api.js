import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8006';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// Interceptor para manejar errores con mensajes más informativos
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    
    // Mejorar mensaje de error para el usuario
    if (error.response) {
      // El servidor respondió con un código de error
      const { status, data } = error.response;
      const errorMessage = data?.error?.message || data?.detail || `Error ${status}`;
      
      // Mensajes más específicos según el código de error
      switch (status) {
        case 400:
          error.userMessage = `Solicitud inválida: ${errorMessage}`;
          break;
        case 401:
          error.userMessage = 'No autorizado. Por favor, inicia sesión.';
          break;
        case 403:
          error.userMessage = 'No tienes permiso para realizar esta acción.';
          break;
        case 404:
          error.userMessage = 'Recurso no encontrado.';
          break;
        case 422:
          error.userMessage = `Error de validación: ${errorMessage}`;
          break;
        case 429:
          error.userMessage = 'Demasiadas solicitudes. Por favor, espera un momento.';
          break;
        case 500:
          error.userMessage = 'Error interno del servidor. Por favor, intenta más tarde.';
          break;
        case 503:
          error.userMessage = 'Servicio no disponible. Por favor, intenta más tarde.';
          break;
        default:
          error.userMessage = errorMessage || 'Ocurrió un error inesperado.';
      }
    } else if (error.request) {
      // La solicitud se hizo pero no hubo respuesta
      error.userMessage = 'No se pudo conectar con el servidor. Verifica tu conexión a internet.';
    } else {
      // Algo más causó el error
      error.userMessage = error.message || 'Ocurrió un error inesperado.';
    }
    
    return Promise.reject(error);
  }
);

export const documentAPI = {
  // Subir documento simple
  uploadSimple: (file, documentType = 'factura') => {
    const formData = new FormData();
    formData.append('file', file);
    // document_type va como query parameter, no en FormData
    
    return api.post(`/api/v1/upload?document_type=${encodeURIComponent(documentType)}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // Subir documento flexible
  uploadFlexible: (file, documentType = 'factura', ocrMethod = 'auto', extractionMethod = 'auto') => {
    const formData = new FormData();
    formData.append('file', file);
    // Los parámetros van como query parameters, no en FormData
    
    const params = new URLSearchParams({
      document_type: documentType,
      ocr_method: ocrMethod,
      extraction_method: extractionMethod
    });
    
    return api.post(`/api/v1/upload-flexible?${params.toString()}`, formData, {
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

  // Reprocesar documento
  reprocessDocument: (documentId, documentType = null) => {
    const params = {};
    if (documentType) {
      params.document_type = documentType;
    }
    return api.post(`/api/v1/documents/${documentId}/reprocess`, null, { params });
  },
};

export default api;
