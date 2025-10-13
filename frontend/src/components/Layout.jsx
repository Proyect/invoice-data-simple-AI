import React, { useState } from 'react';
import { Layout as AntLayout, Menu, Button, Typography, Space } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  DashboardOutlined,
  UploadOutlined,
  FileTextOutlined,
  ApiOutlined,
} from '@ant-design/icons';

const { Header, Sider, Content } = AntLayout;
const { Title } = Typography;

const AppLayout = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
    },
    {
      key: '/upload',
      icon: <UploadOutlined />,
      label: 'Subir Documento',
    },
    {
      key: '/documents',
      icon: <FileTextOutlined />,
      label: 'Documentos',
    },
  ];

  const handleMenuClick = ({ key }) => {
    navigate(key);
  };

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        theme="dark"
      >
        <div style={{ padding: '16px', textAlign: 'center' }}>
          <Title level={4} style={{ color: 'white', margin: 0 }}>
            {collapsed ? 'DE' : 'Document Extractor'}
          </Title>
        </div>
        <Menu
          theme="dark"
          selectedKeys={[location.pathname]}
          mode="inline"
          items={menuItems}
          onClick={handleMenuClick}
        />
      </Sider>
      
      <AntLayout>
        <Header style={{ background: '#fff', padding: '0 24px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', height: '100%' }}>
            <Title level={3} style={{ margin: 0 }}>
              Sistema de Extracción de Documentos
            </Title>
            <Space>
              <Button
                type="primary"
                icon={<ApiOutlined />}
                onClick={() => window.open('http://localhost:8006/docs', '_blank')}
              >
                API Docs
              </Button>
            </Space>
          </div>
        </Header>
        
        <Content style={{ margin: '24px', background: '#fff', borderRadius: '8px', padding: '24px' }}>
          {children}
        </Content>
      </AntLayout>
    </AntLayout>
  );
};

export default AppLayout;
