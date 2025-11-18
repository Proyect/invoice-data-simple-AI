#!/usr/bin/env python3
"""
Script para crear un PDF de prueba con datos de factura
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io

def create_test_invoice():
    """Crear un PDF de prueba con datos de factura"""
    
    # Crear buffer para el PDF
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 100, "FACTURA")
    
    # Datos de la empresa
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 130, "Empresa: Mi Empresa S.A.")
    c.drawString(100, height - 150, "CUIT: 20-12345678-9")
    c.drawString(100, height - 170, "Dirección: Av. Principal 123, CABA")
    c.drawString(100, height - 190, "Teléfono: (011) 1234-5678")
    c.drawString(100, height - 210, "Email: facturacion@miempresa.com")
    
    # Datos del cliente
    c.drawString(100, height - 250, "Cliente: Cliente Test S.A.")
    c.drawString(100, height - 270, "CUIT: 30-87654321-0")
    c.drawString(100, height - 290, "Dirección: Calle Falsa 456, CABA")
    
    # Datos de la factura
    c.drawString(100, height - 330, "Número de Factura: 0001-00000001")
    c.drawString(100, height - 350, "Fecha: 17/10/2025")
    c.drawString(100, height - 370, "Condición de IVA: Responsable Inscripto")
    
    # Tabla de productos
    c.drawString(100, height - 410, "Producto: Servicio de Consultoría")
    c.drawString(100, height - 430, "Cantidad: 1")
    c.drawString(100, height - 450, "Precio Unitario: $1000.00")
    c.drawString(100, height - 470, "Subtotal: $1000.00")
    c.drawString(100, height - 490, "IVA (21%): $210.00")
    c.drawString(100, height - 510, "TOTAL: $1210.00")
    
    # Método de pago
    c.drawString(100, height - 550, "Forma de Pago: Transferencia Bancaria")
    c.drawString(100, height - 570, "Vencimiento: 17/11/2025")
    
    c.save()
    
    # Obtener el contenido del PDF
    buffer.seek(0)
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content

if __name__ == "__main__":
    print("Creando PDF de prueba...")
    pdf_content = create_test_invoice()
    
    # Guardar el PDF
    with open("test_invoice.pdf", "wb") as f:
        f.write(pdf_content)
    
    print("PDF de prueba creado: test_invoice.pdf")







