import React, { useState, useEffect } from 'react';
import {
  Table,
  Card,
  Input,
  Button,
  Tag,
  Space,
  Typography,
  Modal,
  Descriptions,
  Progress,
  message,
} from 'antd';
import { SearchOutlined, EyeOutlined, ReloadOutlined, FileTextOutlined } from '@ant-design/icons';
import { documentAPI } from '../services/api';

const { Title } = Typography;
const { Search } = Input;

const DocumentList = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [analysisModalVisible, setAnalysisModalVisible] = useState(false);
  const [selectedDocumentForAnalysis, setSelectedDocumentForAnalysis] = useState(null);
  const [searchText, setSearchText] = useState('');
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
  });

  useEffect(() => {
    loadDocuments();
  }, [pagination.current, pagination.pageSize, searchText]);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      const response = await documentAPI.getDocuments(
        (pagination.current - 1) * pagination.pageSize,
        pagination.pageSize,
        searchText || null
      );
      
      setDocuments(response.data.documents);
      setPagination(prev => ({
        ...prev,
        total: response.data.total,
      }));
    } catch (error) {
      message.error('Error cargando documentos');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (value) => {
    setSearchText(value);
    setPagination(prev => ({ ...prev, current: 1 }));
  };

  const handleTableChange = (pagination) => {
    setPagination(prev => ({
      ...prev,
      current: pagination.current,
      pageSize: pagination.pageSize,
    }));
  };

  const viewDocument = async (record) => {
    try {
      const response = await documentAPI.getDocument(record.id);
      setSelectedDocument(response.data);
      setModalVisible(true);
    } catch (error) {
      message.error('Error cargando documento');
    }
  };

  const viewAnalysis = async (record) => {
    try {
      const response = await documentAPI.getDocument(record.id);
      setSelectedDocumentForAnalysis(response.data);
      setAnalysisModalVisible(true);
    } catch (error) {
      message.error('Error cargando análisis del documento');
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 80) return 'green';
    if (confidence >= 60) return 'orange';
    return 'red';
  };

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: 'Nombre',
      dataIndex: 'original_filename',
      key: 'original_filename',
      ellipsis: true,
    },
    {
      title: 'Tipo',
      dataIndex: 'mime_type',
      key: 'mime_type',
      render: (type) => <Tag>{type?.split('/')[1]?.toUpperCase()}</Tag>,
    },
    {
      title: 'Tamaño',
      dataIndex: 'file_size',
      key: 'file_size',
      render: (size) => {
        if (!size) return '-';
        // Si ya está en MB, usar directamente, sino convertir desde bytes
        if (size < 1024) return `${size} B`;
        if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
        return `${(size / (1024 * 1024)).toFixed(1)} MB`;
      },
    },
    {
      title: 'Confianza',
      dataIndex: 'confidence_score',
      key: 'confidence_score',
      render: (score) => {
        // Convertir de 0.0-1.0 a porcentaje 0-100
        const percent = score ? (score * 100) : 0;
        return (
          <Progress
            percent={percent}
            size="small"
            strokeColor={getConfidenceColor(percent)}
            showInfo={false}
          />
        );
      },
    },
    {
      title: 'Fecha',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date) => new Date(date).toLocaleDateString(),
    },
    {
      title: 'Acciones',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            type="primary"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => viewDocument(record)}
          >
            Ver
          </Button>
          {record.status === 'processed' || record.status === 'completed' ? (
            <Button
              type="default"
              size="small"
              icon={<FileTextOutlined />}
              onClick={() => viewAnalysis(record)}
            >
              Análisis
            </Button>
          ) : null}
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Title level={2}>Documentos Procesados</Title>
      
      <Card>
        <Space style={{ marginBottom: 16, width: '100%', justifyContent: 'space-between' }}>
          <Search
            placeholder="Buscar documentos..."
            allowClear
            style={{ width: 300 }}
            onSearch={handleSearch}
          />
          <Button
            icon={<ReloadOutlined />}
            onClick={loadDocuments}
            loading={loading}
          >
            Actualizar
          </Button>
        </Space>
        
        <Table
          columns={columns}
          dataSource={documents}
          rowKey="id"
          loading={loading}
          pagination={{
            current: pagination.current,
            pageSize: pagination.pageSize,
            total: pagination.total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) =>
              `${range[0]}-${range[1]} de ${total} documentos`,
          }}
          onChange={handleTableChange}
        />
      </Card>

      <Modal
        title="Detalles del Documento"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={800}
      >
        {selectedDocument && (
          <div>
            <Descriptions bordered column={2}>
              <Descriptions.Item label="ID">{selectedDocument.id}</Descriptions.Item>
              <Descriptions.Item label="Archivo">{selectedDocument.original_filename}</Descriptions.Item>
              <Descriptions.Item label="Tamaño">{selectedDocument.file_size ? `${(selectedDocument.file_size / 1024).toFixed(1)} KB` : '-'}</Descriptions.Item>
              <Descriptions.Item label="Tipo">{selectedDocument.mime_type}</Descriptions.Item>
              <Descriptions.Item label="Confianza">
                <Progress percent={selectedDocument.confidence_score} />
              </Descriptions.Item>
              <Descriptions.Item label="Proveedor OCR">{selectedDocument.ocr_provider}</Descriptions.Item>
              <Descriptions.Item label="Fecha Creación" span={2}>
                {new Date(selectedDocument.created_at).toLocaleString()}
              </Descriptions.Item>
            </Descriptions>
            
            {selectedDocument.extracted_data && (
              <Card title="Datos Extraídos" style={{ marginTop: 16 }}>
                <pre style={{ background: '#f5f5f5', padding: '12px', borderRadius: '4px' }}>
                  {JSON.stringify(selectedDocument.extracted_data, null, 2)}
                </pre>
              </Card>
            )}
          </div>
        )}
      </Modal>

      {/* Modal de Análisis Detallado */}
      <Modal
        title="Análisis Completo del Documento"
        open={analysisModalVisible}
        onCancel={() => {
          setAnalysisModalVisible(false);
          setSelectedDocumentForAnalysis(null);
        }}
        footer={[
          <Button key="close" onClick={() => {
            setAnalysisModalVisible(false);
            setSelectedDocumentForAnalysis(null);
          }}>
            Cerrar
          </Button>
        ]}
        width={1000}
      >
        {selectedDocumentForAnalysis && (
          <div>
            {/* Información General */}
            <Card title="Información General" style={{ marginBottom: 16 }}>
              <Descriptions bordered column={2} size="small">
                <Descriptions.Item label="Archivo">{selectedDocumentForAnalysis.original_filename}</Descriptions.Item>
                <Descriptions.Item label="Tipo de Documento">
                  {selectedDocumentForAnalysis.extracted_data?.document_type || selectedDocumentForAnalysis.document_type || 'N/A'}
                </Descriptions.Item>
                <Descriptions.Item label="Confianza">
                  <Progress 
                    percent={selectedDocumentForAnalysis.confidence_score ? (selectedDocumentForAnalysis.confidence_score * 100) : 0} 
                    status={selectedDocumentForAnalysis.confidence_score && selectedDocumentForAnalysis.confidence_score > 0.7 ? 'success' : 'exception'}
                  />
                </Descriptions.Item>
                <Descriptions.Item label="Proveedor OCR">{selectedDocumentForAnalysis.ocr_provider || 'N/A'}</Descriptions.Item>
                <Descriptions.Item label="Fecha de Procesamiento" span={2}>
                  {new Date(selectedDocumentForAnalysis.created_at).toLocaleString()}
                </Descriptions.Item>
              </Descriptions>
            </Card>

            {/* Datos Extraídos Estructurados */}
            {selectedDocumentForAnalysis.extracted_data && (
              <>
                {/* Para Facturas */}
                {selectedDocumentForAnalysis.extracted_data.document_type === 'factura' || 
                 (selectedDocumentForAnalysis.extracted_data.emisor || selectedDocumentForAnalysis.extracted_data.numero_factura) ? (
                  <>
                    {/* Información de la Factura */}
                    <Card title="Información de la Factura" style={{ marginBottom: 16 }}>
                      <Descriptions bordered column={2} size="small">
                        {selectedDocumentForAnalysis.extracted_data.numero_factura && (
                          <Descriptions.Item label="Número de Factura">{selectedDocumentForAnalysis.extracted_data.numero_factura}</Descriptions.Item>
                        )}
                        {selectedDocumentForAnalysis.extracted_data.punto_venta && (
                          <Descriptions.Item label="Punto de Venta">{selectedDocumentForAnalysis.extracted_data.punto_venta}</Descriptions.Item>
                        )}
                        {selectedDocumentForAnalysis.extracted_data.numero_comprobante && (
                          <Descriptions.Item label="Número Comprobante">{selectedDocumentForAnalysis.extracted_data.numero_comprobante}</Descriptions.Item>
                        )}
                        {selectedDocumentForAnalysis.extracted_data.tipo_comprobante && (
                          <Descriptions.Item label="Tipo Comprobante">{selectedDocumentForAnalysis.extracted_data.tipo_comprobante}</Descriptions.Item>
                        )}
                        {selectedDocumentForAnalysis.extracted_data.codigo_comprobante && (
                          <Descriptions.Item label="Código Comprobante">{selectedDocumentForAnalysis.extracted_data.codigo_comprobante}</Descriptions.Item>
                        )}
                        {selectedDocumentForAnalysis.extracted_data.fecha_emision && (
                          <Descriptions.Item label="Fecha de Emisión">{selectedDocumentForAnalysis.extracted_data.fecha_emision}</Descriptions.Item>
                        )}
                        {selectedDocumentForAnalysis.extracted_data.fecha_vencimiento && (
                          <Descriptions.Item label="Fecha de Vencimiento">{selectedDocumentForAnalysis.extracted_data.fecha_vencimiento}</Descriptions.Item>
                        )}
                        {selectedDocumentForAnalysis.extracted_data.periodo_facturado_desde && (
                          <Descriptions.Item label="Período Facturado Desde">{selectedDocumentForAnalysis.extracted_data.periodo_facturado_desde}</Descriptions.Item>
                        )}
                        {selectedDocumentForAnalysis.extracted_data.periodo_facturado_hasta && (
                          <Descriptions.Item label="Período Facturado Hasta">{selectedDocumentForAnalysis.extracted_data.periodo_facturado_hasta}</Descriptions.Item>
                        )}
                        {selectedDocumentForAnalysis.extracted_data.cae && (
                          <Descriptions.Item label="CAE">{selectedDocumentForAnalysis.extracted_data.cae}</Descriptions.Item>
                        )}
                        {selectedDocumentForAnalysis.extracted_data.cae_vencimiento && (
                          <Descriptions.Item label="CAE Vencimiento">{selectedDocumentForAnalysis.extracted_data.cae_vencimiento}</Descriptions.Item>
                        )}
                      </Descriptions>
                    </Card>

                    {/* Emisor */}
                    {selectedDocumentForAnalysis.extracted_data.emisor && (
                      <Card title="Emisor" style={{ marginBottom: 16 }}>
                        <Descriptions bordered column={2} size="small">
                          {selectedDocumentForAnalysis.extracted_data.emisor.razon_social && (
                            <Descriptions.Item label="Razón Social" span={2}>
                              {selectedDocumentForAnalysis.extracted_data.emisor.razon_social}
                            </Descriptions.Item>
                          )}
                          {selectedDocumentForAnalysis.extracted_data.emisor.nombre_fantasia && (
                            <Descriptions.Item label="Nombre de Fantasía">{selectedDocumentForAnalysis.extracted_data.emisor.nombre_fantasia}</Descriptions.Item>
                          )}
                          {selectedDocumentForAnalysis.extracted_data.emisor.cuit && (
                            <Descriptions.Item label="CUIT">{selectedDocumentForAnalysis.extracted_data.emisor.cuit}</Descriptions.Item>
                          )}
                          {selectedDocumentForAnalysis.extracted_data.emisor.condicion_iva && (
                            <Descriptions.Item label="Condición IVA">{selectedDocumentForAnalysis.extracted_data.emisor.condicion_iva}</Descriptions.Item>
                          )}
                          {selectedDocumentForAnalysis.extracted_data.emisor.ingresos_brutos && (
                            <Descriptions.Item label="Ingresos Brutos">{selectedDocumentForAnalysis.extracted_data.emisor.ingresos_brutos}</Descriptions.Item>
                          )}
                          {selectedDocumentForAnalysis.extracted_data.emisor.domicilio_fiscal && (
                            <Descriptions.Item label="Domicilio Fiscal" span={2}>
                              {selectedDocumentForAnalysis.extracted_data.emisor.domicilio_fiscal}
                            </Descriptions.Item>
                          )}
                          {selectedDocumentForAnalysis.extracted_data.emisor.localidad && (
                            <Descriptions.Item label="Localidad">{selectedDocumentForAnalysis.extracted_data.emisor.localidad}</Descriptions.Item>
                          )}
                          {selectedDocumentForAnalysis.extracted_data.emisor.provincia && (
                            <Descriptions.Item label="Provincia">{selectedDocumentForAnalysis.extracted_data.emisor.provincia}</Descriptions.Item>
                          )}
                          {selectedDocumentForAnalysis.extracted_data.emisor.codigo_postal && (
                            <Descriptions.Item label="Código Postal">{selectedDocumentForAnalysis.extracted_data.emisor.codigo_postal}</Descriptions.Item>
                          )}
                          {selectedDocumentForAnalysis.extracted_data.emisor.telefono && (
                            <Descriptions.Item label="Teléfono">{selectedDocumentForAnalysis.extracted_data.emisor.telefono}</Descriptions.Item>
                          )}
                          {selectedDocumentForAnalysis.extracted_data.emisor.email && (
                            <Descriptions.Item label="Email">{selectedDocumentForAnalysis.extracted_data.emisor.email}</Descriptions.Item>
                          )}
                        </Descriptions>
                      </Card>
                    )}

                    {/* Receptor */}
                    {selectedDocumentForAnalysis.extracted_data.receptor && (
                      <Card title="Receptor" style={{ marginBottom: 16 }}>
                        <Descriptions bordered column={2} size="small">
                          {selectedDocumentForAnalysis.extracted_data.receptor.razon_social && (
                            <Descriptions.Item label="Razón Social" span={2}>
                              {selectedDocumentForAnalysis.extracted_data.receptor.razon_social}
                            </Descriptions.Item>
                          )}
                          {selectedDocumentForAnalysis.extracted_data.receptor.cuit && (
                            <Descriptions.Item label="CUIT">{selectedDocumentForAnalysis.extracted_data.receptor.cuit}</Descriptions.Item>
                          )}
                          {selectedDocumentForAnalysis.extracted_data.receptor.condicion_iva && (
                            <Descriptions.Item label="Condición IVA">{selectedDocumentForAnalysis.extracted_data.receptor.condicion_iva}</Descriptions.Item>
                          )}
                          {selectedDocumentForAnalysis.extracted_data.receptor.domicilio && (
                            <Descriptions.Item label="Domicilio" span={2}>
                              {selectedDocumentForAnalysis.extracted_data.receptor.domicilio}
                            </Descriptions.Item>
                          )}
                        </Descriptions>
                      </Card>
                    )}

                    {/* Items */}
                    {selectedDocumentForAnalysis.extracted_data.items && 
                     Array.isArray(selectedDocumentForAnalysis.extracted_data.items) && 
                     selectedDocumentForAnalysis.extracted_data.items.length > 0 && (
                      <Card title="Items" style={{ marginBottom: 16 }}>
                        <Table
                          dataSource={selectedDocumentForAnalysis.extracted_data.items.map((item, index) => ({ ...item, key: index }))}
                          pagination={false}
                          size="small"
                          columns={[
                            { title: 'Código', dataIndex: 'codigo', key: 'codigo', width: 80 },
                            { 
                              title: 'Descripción', 
                              dataIndex: 'descripcion', 
                              key: 'descripcion', 
                              ellipsis: true,
                              render: (text, record) => (
                                <div>
                                  <div>{text}</div>
                                  {record.descripcion_adicional && (
                                    <div style={{ fontSize: '11px', color: '#666', fontStyle: 'italic', marginTop: '4px' }}>
                                      {record.descripcion_adicional}
                                    </div>
                                  )}
                                </div>
                              )
                            },
                            { title: 'Cantidad', dataIndex: 'cantidad', key: 'cantidad', align: 'right', width: 100 },
                            { title: 'Unidad', dataIndex: 'unidad_medida', key: 'unidad_medida', width: 100 },
                            { title: 'Precio Unit.', dataIndex: 'precio_unitario', key: 'precio_unitario', align: 'right', width: 120 },
                            { title: '% Bonif.', dataIndex: 'porcentaje_bonificacion', key: 'porcentaje_bonificacion', align: 'right', width: 100 },
                            { title: 'Imp. Bonif.', dataIndex: 'importe_bonificacion', key: 'importe_bonificacion', align: 'right', width: 100 },
                            { title: 'IVA %', dataIndex: 'alicuota_iva', key: 'alicuota_iva', align: 'right', width: 80 },
                            { title: 'Subtotal', dataIndex: 'subtotal', key: 'subtotal', align: 'right', width: 120 },
                            { title: 'Total', dataIndex: 'total_item', key: 'total_item', align: 'right', width: 120 },
                          ]}
                        />
                      </Card>
                    )}

                    {/* Totales - Optimizado para Facturas Argentinas */}
                    {selectedDocumentForAnalysis.extracted_data.totales && (
                      <Card title="Totales" style={{ marginBottom: 16 }}>
                        <Descriptions bordered column={2} size="small">
                          {/* Subtotal y Netos */}
                          {selectedDocumentForAnalysis.extracted_data.totales.subtotal && (
                            <Descriptions.Item label="Subtotal">{selectedDocumentForAnalysis.extracted_data.totales.subtotal}</Descriptions.Item>
                          )}
                          {selectedDocumentForAnalysis.extracted_data.totales.subtotal_sin_iva && (
                            <Descriptions.Item label="Subtotal sin IVA">{selectedDocumentForAnalysis.extracted_data.totales.subtotal_sin_iva}</Descriptions.Item>
                          )}
                          {selectedDocumentForAnalysis.extracted_data.totales.importe_neto_gravado && (
                            <Descriptions.Item label="Importe Neto Gravado">{selectedDocumentForAnalysis.extracted_data.totales.importe_neto_gravado}</Descriptions.Item>
                          )}
                          {selectedDocumentForAnalysis.extracted_data.totales.importe_neto_no_gravado && (
                            <Descriptions.Item label="Importe Neto No Gravado">{selectedDocumentForAnalysis.extracted_data.totales.importe_neto_no_gravado}</Descriptions.Item>
                          )}
                          
                          {/* IVA */}
                          {selectedDocumentForAnalysis.extracted_data.totales.iva_21 && (
                            <Descriptions.Item label="IVA 21%">{selectedDocumentForAnalysis.extracted_data.totales.iva_21}</Descriptions.Item>
                          )}
                          {selectedDocumentForAnalysis.extracted_data.totales.iva_10_5 && (
                            <Descriptions.Item label="IVA 10.5%">{selectedDocumentForAnalysis.extracted_data.totales.iva_10_5}</Descriptions.Item>
                          )}
                          {selectedDocumentForAnalysis.extracted_data.totales.iva_27 && (
                            <Descriptions.Item label="IVA 27%">{selectedDocumentForAnalysis.extracted_data.totales.iva_27}</Descriptions.Item>
                          )}
                          {selectedDocumentForAnalysis.extracted_data.totales.iva_0 && (
                            <Descriptions.Item label="Operaciones Exentas">{selectedDocumentForAnalysis.extracted_data.totales.iva_0}</Descriptions.Item>
                          )}
                          {selectedDocumentForAnalysis.extracted_data.totales.total_iva && (
                            <Descriptions.Item label="Total IVA" span={2}>
                              <strong>{selectedDocumentForAnalysis.extracted_data.totales.total_iva}</strong>
                            </Descriptions.Item>
                          )}
                          
                          {/* Otros Tributos */}
                          {selectedDocumentForAnalysis.extracted_data.totales.impuestos_internos && (
                            <Descriptions.Item label="Impuestos Internos">{selectedDocumentForAnalysis.extracted_data.totales.impuestos_internos}</Descriptions.Item>
                          )}
                          {selectedDocumentForAnalysis.extracted_data.totales.otros_tributos && (
                            <Descriptions.Item label="Otros Tributos">{selectedDocumentForAnalysis.extracted_data.totales.otros_tributos}</Descriptions.Item>
                          )}
                          {selectedDocumentForAnalysis.extracted_data.totales.importe_otros_tributos && (
                            <Descriptions.Item label="Importe Otros Tributos">{selectedDocumentForAnalysis.extracted_data.totales.importe_otros_tributos}</Descriptions.Item>
                          )}
                          {selectedDocumentForAnalysis.extracted_data.totales.total_otros_tributos && (
                            <Descriptions.Item label="Total Otros Tributos">{selectedDocumentForAnalysis.extracted_data.totales.total_otros_tributos}</Descriptions.Item>
                          )}
                          
                          {/* Percepciones */}
                          {selectedDocumentForAnalysis.extracted_data.totales.percepciones_iva && (
                            <Descriptions.Item label="Percepciones IVA">{selectedDocumentForAnalysis.extracted_data.totales.percepciones_iva}</Descriptions.Item>
                          )}
                          {selectedDocumentForAnalysis.extracted_data.totales.percepciones_ingresos_brutos && (
                            <Descriptions.Item label="Percepciones Ing. Brutos">{selectedDocumentForAnalysis.extracted_data.totales.percepciones_ingresos_brutos}</Descriptions.Item>
                          )}
                          {selectedDocumentForAnalysis.extracted_data.totales.percepciones_otras && (
                            <Descriptions.Item label="Otras Percepciones">{selectedDocumentForAnalysis.extracted_data.totales.percepciones_otras}</Descriptions.Item>
                          )}
                          {selectedDocumentForAnalysis.extracted_data.totales.total_percepciones && (
                            <Descriptions.Item label="Total Percepciones">{selectedDocumentForAnalysis.extracted_data.totales.total_percepciones}</Descriptions.Item>
                          )}
                          
                          {/* Retenciones */}
                          {selectedDocumentForAnalysis.extracted_data.totales.retenciones && (
                            <Descriptions.Item label="Retenciones">{selectedDocumentForAnalysis.extracted_data.totales.retenciones}</Descriptions.Item>
                          )}
                          {selectedDocumentForAnalysis.extracted_data.totales.total_retenciones && (
                            <Descriptions.Item label="Total Retenciones">{selectedDocumentForAnalysis.extracted_data.totales.total_retenciones}</Descriptions.Item>
                          )}
                          
                          {/* Total Final */}
                          {selectedDocumentForAnalysis.extracted_data.totales.importe_total && (
                            <Descriptions.Item label="Importe Total" span={2}>
                              <strong style={{ fontSize: '18px', color: '#1890ff', fontWeight: 'bold' }}>
                                {selectedDocumentForAnalysis.extracted_data.totales.importe_total}
                                {selectedDocumentForAnalysis.extracted_data.totales.moneda && ` ${selectedDocumentForAnalysis.extracted_data.totales.moneda}`}
                              </strong>
                            </Descriptions.Item>
                          )}
                          {selectedDocumentForAnalysis.extracted_data.totales.total && (
                            <Descriptions.Item label="Total Final" span={2}>
                              <strong style={{ fontSize: '18px', color: '#1890ff', fontWeight: 'bold' }}>
                                {selectedDocumentForAnalysis.extracted_data.totales.total}
                                {selectedDocumentForAnalysis.extracted_data.totales.moneda && ` ${selectedDocumentForAnalysis.extracted_data.totales.moneda}`}
                              </strong>
                            </Descriptions.Item>
                          )}
                        </Descriptions>
                      </Card>
                    )}

                    {/* Información Adicional */}
                    {(selectedDocumentForAnalysis.extracted_data.forma_pago || 
                      selectedDocumentForAnalysis.extracted_data.condicion_venta || 
                      selectedDocumentForAnalysis.extracted_data.observaciones) && (
                      <Card title="Información Adicional" style={{ marginBottom: 16 }}>
                        <Descriptions bordered column={1} size="small">
                          {selectedDocumentForAnalysis.extracted_data.forma_pago && (
                            <Descriptions.Item label="Forma de Pago">{selectedDocumentForAnalysis.extracted_data.forma_pago}</Descriptions.Item>
                          )}
                          {selectedDocumentForAnalysis.extracted_data.condicion_venta && (
                            <Descriptions.Item label="Condición de Venta">{selectedDocumentForAnalysis.extracted_data.condicion_venta}</Descriptions.Item>
                          )}
                          {selectedDocumentForAnalysis.extracted_data.observaciones && (
                            <Descriptions.Item label="Observaciones">{selectedDocumentForAnalysis.extracted_data.observaciones}</Descriptions.Item>
                          )}
                        </Descriptions>
                      </Card>
                    )}
                  </>
                ) : (
                  /* Para otros tipos de documentos */
                  <Card title="Datos Extraídos" style={{ marginBottom: 16 }}>
                    <pre style={{ background: '#f5f5f5', padding: '12px', borderRadius: '4px', maxHeight: '400px', overflow: 'auto' }}>
                      {JSON.stringify(selectedDocumentForAnalysis.extracted_data, null, 2)}
                    </pre>
                  </Card>
                )}
              </>
            )}

            {/* Texto OCR Completo */}
            {selectedDocumentForAnalysis.raw_text && (
              <Card title="Texto Extraído (OCR)" style={{ marginBottom: 16 }}>
                <div style={{ 
                  background: '#f5f5f5', 
                  padding: '12px', 
                  borderRadius: '4px', 
                  maxHeight: '300px', 
                  overflow: 'auto',
                  whiteSpace: 'pre-wrap',
                  fontFamily: 'monospace',
                  fontSize: '12px'
                }}>
                  {selectedDocumentForAnalysis.raw_text}
                </div>
              </Card>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default DocumentList;
