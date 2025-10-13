import React, { useState } from 'react';
import {
  Upload,
  Button,
  Card,
  Form,
  Select,
  message,
  Typography,
  Space,
  Alert,
  Row,
  Col,
  Progress,
  Spin,
  Result,
} from 'antd';
import { InboxOutlined, FileTextOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { documentAPI } from '../services/api';

const { Dragger } = Upload;
const { Title } = Typography;
const { Option } = Select;

const DocumentUpload = () => {
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const [uploading, setUploading] = useState(false);
  const [uploadMethod, setUploadMethod] = useState('simple');
  const [processingStatus, setProcessingStatus] = useState(null); // 'uploading', 'processing', 'completed', 'error'
  const [processingStep, setProcessingStep] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);

  const documentTypes = [
    { value: 'factura', label: 'Factura' },
    { value: 'recibo', label: 'Recibo' },
    { value: 'boleta', label: 'Boleta' },
    { value: 'contrato', label: 'Contrato' },
    { value: 'documento', label: 'Documento Genérico' },
  ];

  const ocrMethods = [
    { value: 'auto', label: 'Automático' },
    { value: 'tesseract', label: 'Tesseract (Local)' },
    { value: 'google_vision', label: 'Google Vision' },
    { value: 'aws_textract', label: 'AWS Textract' },
  ];

  const extractionMethods = [
    { value: 'auto', label: 'Automático' },
    { value: 'regex', label: 'Expresiones Regulares' },
    { value: 'spacy', label: 'spaCy NLP' },
    { value: 'llm', label: 'OpenAI GPT' },
    { value: 'hybrid', label: 'Híbrido' },
  ];

  const handleUpload = async (options) => {
    const { file, onSuccess, onError } = options;
    
    if (!file) return;

    try {
      setUploading(true);
      setProcessingStatus('uploading');
      setProcessingStep('Subiendo archivo...');
      setUploadProgress(0);
      
      const values = form.getFieldsValue();
      
      // Simular progreso de subida
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);
      
      setProcessingStep('Analizando documento con IA...');
      setProcessingStatus('processing');
      
      let response;
      
      if (uploadMethod === 'simple') {
        response = await documentAPI.uploadSimple(file, values.document_type);
      } else {
        response = await documentAPI.uploadFlexible(
          file,
          values.document_type,
          values.ocr_method,
          values.extraction_method
        );
      }

      clearInterval(progressInterval);
      setUploadProgress(100);
      setProcessingStep('¡Análisis completado!');
      setProcessingStatus('completed');
      
      message.success('Documento procesado exitosamente!');
      onSuccess(response.data);
      
      // Redirigir a la lista de documentos después de mostrar el éxito
      setTimeout(() => {
        navigate('/documents');
      }, 3000);

    } catch (error) {
      console.error('Upload error:', error);
      setProcessingStatus('error');
      setProcessingStep('Error en el procesamiento');
      message.error(error.response?.data?.detail || 'Error procesando documento');
      onError(error);
    } finally {
      setUploading(false);
    }
  };

  const [selectedFile, setSelectedFile] = useState(null);

  const uploadProps = {
    name: 'file',
    multiple: false,
    showUploadList: false,
    accept: '.pdf,.jpg,.jpeg,.png,.tiff',
    beforeUpload: (file) => {
      const isValidType = ['application/pdf', 'image/jpeg', 'image/png', 'image/tiff'].includes(file.type);
      if (!isValidType) {
        message.error('Solo se permiten archivos PDF e imágenes!');
        return false;
      }
      
      const isLt10M = file.size / 1024 / 1024 < 10;
      if (!isLt10M) {
        message.error('El archivo debe ser menor a 10MB!');
        return false;
      }
      
      setSelectedFile(file);
      return false; // Prevent default upload
    },
  };

  const handleSubmitFile = async () => {
    if (!selectedFile) {
      message.warning('Por favor selecciona un archivo primero');
      return;
    }

    try {
      setUploading(true);
      setProcessingStatus('uploading');
      setProcessingStep('Subiendo archivo...');
      setUploadProgress(0);
      
      const values = form.getFieldsValue();
      
      // Simular progreso de subida
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);
      
      setProcessingStep('Analizando documento con IA...');
      setProcessingStatus('processing');
      
      let response;
      
      if (uploadMethod === 'simple') {
        response = await documentAPI.uploadSimple(selectedFile, values.document_type);
      } else {
        response = await documentAPI.uploadFlexible(
          selectedFile,
          values.document_type,
          values.ocr_method,
          values.extraction_method
        );
      }

      clearInterval(progressInterval);
      setUploadProgress(100);
      setProcessingStep('¡Análisis completado!');
      setProcessingStatus('completed');
      
      message.success('Documento procesado exitosamente!');
      
      // Redirigir a la lista de documentos después de mostrar el éxito
      setTimeout(() => {
        navigate('/documents');
      }, 3000);

    } catch (error) {
      console.error('Upload error:', error);
      setProcessingStatus('error');
      setProcessingStep('Error en el procesamiento');
      message.error(error.response?.data?.detail || 'Error procesando documento');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <Title level={2}>Subir Documento</Title>
      
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Card>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Select
                value={uploadMethod}
                onChange={setUploadMethod}
                style={{ width: 200 }}
              >
                <Option value="simple">Upload Simple</Option>
                <Option value="flexible">Upload Flexible</Option>
              </Select>
              
              <Alert
                message={uploadMethod === 'simple' 
                  ? "Método simple: Tesseract + spaCy (rápido y confiable)"
                  : "Método flexible: Puedes elegir OCR y extracción específicos"
                }
                type="info"
                showIcon
              />
            </Space>
          </Card>
        </Col>
        
        <Col span={24}>
          <Card title="Configuración">
            <Form form={form} layout="vertical">
              <Form.Item
                name="document_type"
                label="Tipo de Documento"
                initialValue="factura"
              >
                <Select placeholder="Selecciona el tipo de documento">
                  {documentTypes.map(type => (
                    <Option key={type.value} value={type.value}>
                      {type.label}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
              
              {uploadMethod === 'flexible' && (
                <>
                  <Form.Item
                    name="ocr_method"
                    label="Método OCR"
                    initialValue="auto"
                  >
                    <Select placeholder="Selecciona método OCR">
                      {ocrMethods.map(method => (
                        <Option key={method.value} value={method.value}>
                          {method.label}
                        </Option>
                      ))}
                    </Select>
                  </Form.Item>
                  
                  <Form.Item
                    name="extraction_method"
                    label="Método de Extracción"
                    initialValue="auto"
                  >
                    <Select placeholder="Selecciona método de extracción">
                      {extractionMethods.map(method => (
                        <Option key={method.value} value={method.value}>
                          {method.label}
                        </Option>
                      ))}
                    </Select>
                  </Form.Item>
                </>
              )}
            </Form>
          </Card>
        </Col>
        
        {/* Estado de Procesamiento */}
        {processingStatus && (
          <Col span={24}>
            <Card title="Estado del Procesamiento">
              {processingStatus === 'uploading' && (
                <div style={{ textAlign: 'center', padding: '20px' }}>
                  <Spin size="large" />
                  <p style={{ marginTop: '16px', fontSize: '16px' }}>
                    {processingStep}
                  </p>
                  <Progress 
                    percent={uploadProgress} 
                    status="active" 
                    style={{ marginTop: '16px' }}
                  />
                </div>
              )}
              
              {processingStatus === 'processing' && (
                <div style={{ textAlign: 'center', padding: '20px' }}>
                  <Spin size="large" />
                  <p style={{ marginTop: '16px', fontSize: '16px', color: '#1890ff' }}>
                    {processingStep}
                  </p>
                  <Progress 
                    percent={uploadProgress} 
                    status="active" 
                    style={{ marginTop: '16px' }}
                    strokeColor={{
                      '0%': '#108ee9',
                      '100%': '#87d068',
                    }}
                  />
                  <Alert
                    message="Análisis en Progreso"
                    description="El sistema está utilizando IA para extraer datos del documento. Esto puede tomar unos momentos."
                    type="info"
                    showIcon
                    style={{ marginTop: '16px' }}
                  />
                </div>
              )}
              
              {processingStatus === 'completed' && (
                <Result
                  status="success"
                  title="Análisis Completado"
                  subTitle={processingStep}
                  icon={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
                  extra={[
                    <Button type="primary" onClick={() => navigate('/documents')}>
                      Ver Documentos
                    </Button>,
                    <Button onClick={() => {
                      setProcessingStatus(null);
                      setProcessingStep('');
                      setUploadProgress(0);
                    }}>
                      Procesar Otro
                    </Button>
                  ]}
                />
              )}
              
              {processingStatus === 'error' && (
                <Result
                  status="error"
                  title="Error en el Procesamiento"
                  subTitle={processingStep}
                  extra={[
                    <Button type="primary" onClick={() => {
                      setProcessingStatus(null);
                      setProcessingStep('');
                      setUploadProgress(0);
                    }}>
                      Intentar de Nuevo
                    </Button>
                  ]}
                />
              )}
            </Card>
          </Col>
        )}
        
        <Col span={24}>
          <Card title="Subir Archivo">
            {!selectedFile ? (
              <Dragger {...uploadProps} className="upload-dragger" disabled={uploading}>
                <p className="ant-upload-drag-icon">
                  <InboxOutlined />
                </p>
                <p className="ant-upload-text">
                  Haz clic o arrastra el archivo aquí para seleccionarlo
                </p>
                <p className="ant-upload-hint">
                  Soporta PDF, JPG, PNG, TIFF (máximo 10MB)
                </p>
                <div style={{ marginTop: '16px' }}>
                  <Button 
                    type="primary" 
                    size="large" 
                    icon={<FileTextOutlined />}
                  >
                    Seleccionar Archivo
                  </Button>
                </div>
              </Dragger>
            ) : (
              <div style={{ padding: '20px', textAlign: 'center' }}>
                <div style={{ 
                  border: '2px dashed #d9d9d9', 
                  borderRadius: '6px', 
                  padding: '20px',
                  backgroundColor: '#fafafa'
                }}>
                  <FileTextOutlined style={{ fontSize: '48px', color: '#1890ff', marginBottom: '16px' }} />
                  <h4 style={{ margin: '0 0 8px 0', color: '#1890ff' }}>Archivo Seleccionado</h4>
                  <p style={{ margin: '0 0 16px 0', fontSize: '16px', fontWeight: 'bold' }}>
                    {selectedFile.name}
                  </p>
                  <p style={{ margin: '0 0 20px 0', color: '#666' }}>
                    Tamaño: {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                  
                  <Space>
                    <Button 
                      type="primary" 
                      size="large" 
                      icon={<InboxOutlined />}
                      loading={uploading}
                      onClick={handleSubmitFile}
                    >
                      {uploading ? 'Procesando...' : 'Analizar Documento'}
                    </Button>
                    <Button 
                      onClick={() => setSelectedFile(null)}
                      disabled={uploading}
                    >
                      Cambiar Archivo
                    </Button>
                  </Space>
                </div>
              </div>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default DocumentUpload;
