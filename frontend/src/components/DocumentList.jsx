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
import { SearchOutlined, EyeOutlined, ReloadOutlined } from '@ant-design/icons';
import { documentAPI } from '../services/api';

const { Title } = Typography;
const { Search } = Input;

const DocumentList = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);
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
      render: (size) => size ? `${(size / 1024).toFixed(1)} KB` : '-',
    },
    {
      title: 'Confianza',
      dataIndex: 'confidence_score',
      key: 'confidence_score',
      render: (score) => (
        <Progress
          percent={score}
          size="small"
          strokeColor={getConfidenceColor(score)}
          showInfo={false}
        />
      ),
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
    </div>
  );
};

export default DocumentList;
