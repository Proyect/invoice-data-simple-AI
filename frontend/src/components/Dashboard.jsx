import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Statistic, Spin, Alert, Typography, Space } from 'antd';
import {
  FileTextOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  TrophyOutlined,
} from '@ant-design/icons';
import { documentAPI } from '../services/api';

const { Title } = Typography;

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalDocuments: 0,
    processedToday: 0,
    averageConfidence: 0,
    systemStatus: 'unknown',
  });
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Obtener información del sistema
      const [healthResponse, infoResponse, documentsResponse] = await Promise.all([
        documentAPI.getHealth(),
        documentAPI.getInfo(),
        documentAPI.getDocuments(0, 1), // Solo para obtener el total
      ]);

      const systemStatus = healthResponse.data.status === 'healthy' ? 'healthy' : 'error';
      
      // Calcular estadísticas básicas
      const totalDocuments = documentsResponse.data.total || 0;
      
      setStats({
        totalDocuments,
        processedToday: Math.floor(totalDocuments * 0.1), // Simulado
        averageConfidence: 85, // Simulado
        systemStatus,
      });
      
    } catch (err) {
      setError('Error cargando datos del dashboard');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <p>Cargando dashboard...</p>
      </div>
    );
  }

  if (error) {
    return <Alert message={error} type="error" />;
  }

  return (
    <div>
      <Title level={2}>Dashboard</Title>
      
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Documentos Totales"
              value={stats.totalDocuments}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Procesados Hoy"
              value={stats.processedToday}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Confianza Promedio"
              value={stats.averageConfidence}
              suffix="%"
              prefix={<TrophyOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Estado del Sistema"
              value={stats.systemStatus === 'healthy' ? 'Activo' : 'Error'}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ 
                color: stats.systemStatus === 'healthy' ? '#52c41a' : '#ff4d4f' 
              }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: '24px' }}>
        <Col span={24}>
          <Card title="Acciones Rápidas">
            <Space>
              <a href="/upload">
                <FileTextOutlined /> Subir Documento
              </a>
              <a href="/documents">
                <FileTextOutlined /> Ver Documentos
              </a>
              <a href="http://localhost:8006/docs" target="_blank" rel="noopener noreferrer">
                <FileTextOutlined /> API Documentation
              </a>
            </Space>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
