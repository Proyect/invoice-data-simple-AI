#!/usr/bin/env python3
"""
Script para crear una factura AFIP/ARCA de prueba
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

def create_afip_invoice():
    """Crear una factura AFIP/ARCA de prueba"""
    
    # Crear buffer para el PDF
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # ORIGINAL
    c.setFont("Helvetica-Bold", 14)
    c.drawString(width/2 - 30, height - 50, "ORIGINAL")
    
    # Caja con código
    c.rect(width/2 - 100, height - 120, 80, 60)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(width/2 - 70, height - 90, "C")
    c.setFont("Helvetica", 10)
    c.drawString(width/2 - 85, height - 110, "COD. 011")
    
    # FACTURA
    c.setFont("Helvetica-Bold", 18)
    c.drawString(width/2 + 20, height - 80, "FACTURA")
    
    # Información del comprobante (lado derecho)
    c.setFont("Helvetica", 10)
    c.drawString(width/2 + 20, height - 100, "Punto de Venta: 00003")
    c.drawString(width/2 + 20, height - 115, "Comp. Nro: 00000001")
    c.drawString(width/2 + 20, height - 130, "Fecha de Emisión: 22/03/2019")
    
    # Sección del emisor (lado izquierdo)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 180, "Razón Social:")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 195, "Mi Empresa S.A.")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 210, "Domicilio Comercial:")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 225, "Av. Principal 123, CABA")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 240, "Condición frente al IVA:")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 255, "Responsable Monotributo")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 270, "Período Facturado Desde:")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 285, "22/03/2019")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 300, "Hasta:")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 315, "22/03/2019")
    
    # Sección del comprador (lado derecho)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(width/2 + 50, height - 180, "CUIT:")
    c.setFont("Helvetica", 10)
    c.drawString(width/2 + 50, height - 195, "30-87654321-0")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(width/2 + 50, height - 210, "Ingresos Brutos:")
    c.setFont("Helvetica", 10)
    c.drawString(width/2 + 50, height - 225, "Exento")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(width/2 + 50, height - 240, "Fecha de Inicio de Actividades:")
    c.setFont("Helvetica", 10)
    c.drawString(width/2 + 50, height - 255, "01/01/2018")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(width/2 + 50, height - 270, "Fecha de Vto. para el pago:")
    c.setFont("Helvetica", 10)
    c.drawString(width/2 + 50, height - 285, "22/03/2019")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(width/2 + 50, height - 300, "Apellido y Nombre / Razón Social:")
    c.setFont("Helvetica", 10)
    c.drawString(width/2 + 50, height - 315, "Cliente Test S.A.")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(width/2 + 50, height - 330, "Domicilio:")
    c.setFont("Helvetica", 10)
    c.drawString(width/2 + 50, height - 345, "Calle Falsa 456, CABA")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(width/2 + 50, height - 360, "CUIT:")
    c.setFont("Helvetica", 10)
    c.drawString(width/2 + 50, height - 375, "30-87654321-0")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(width/2 + 50, height - 390, "Condición frente al IVA:")
    c.setFont("Helvetica", 10)
    c.drawString(width/2 + 50, height - 405, "Consumidor Final")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(width/2 + 50, height - 420, "Condición de venta:")
    c.setFont("Helvetica", 10)
    c.drawString(width/2 + 50, height - 435, "Contado")
    
    # CUIT del emisor (lado izquierdo)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 330, "CUIT:")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 345, "20-12345678-9")
    
    # Tabla de productos
    y_table = height - 480
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y_table, "Código")
    c.drawString(150, y_table, "Producto / Servicio")
    c.drawString(350, y_table, "Cantidad")
    c.drawString(420, y_table, "U. Medida")
    c.drawString(480, y_table, "Precio Unit.")
    c.drawString(540, y_table, "% Bonif")
    c.drawString(580, y_table, "Imp. Bonif.")
    c.drawString(640, y_table, "Subtotal")
    
    # Línea de producto
    y_product = y_table - 20
    c.setFont("Helvetica", 9)
    c.drawString(50, y_product, "001")
    c.drawString(150, y_product, "Servicio de Consultoría")
    c.drawString(350, y_product, "1,00")
    c.drawString(420, y_product, "unidades")
    c.drawString(480, y_product, "1000,00")
    c.drawString(540, y_product, "0,00")
    c.drawString(580, y_product, "0,00")
    c.drawString(640, y_product, "1000,00")
    
    # Totales (lado derecho)
    y_totals = y_product - 40
    c.setFont("Helvetica-Bold", 10)
    c.drawString(500, y_totals, "Subtotal: $1000,00")
    c.drawString(500, y_totals - 15, "Importe Otros Tributos: $0,00")
    c.drawString(500, y_totals - 30, "Importe Total: $1000,00")
    
    # Footer AFIP
    y_footer = 100
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y_footer, "AFIP")
    c.setFont("Helvetica", 8)
    c.drawString(50, y_footer - 15, "Comprobante Autorizado")
    
    # Página
    c.setFont("Helvetica", 10)
    c.drawString(width/2 - 20, y_footer, "Pág. 1/1")
    
    # CAE
    c.setFont("Helvetica-Bold", 10)
    c.drawString(500, y_footer, "CAE N°: 12345678901234")
    c.drawString(500, y_footer - 15, "Fecha de Vto. de CAE: 22/04/2019")
    
    c.save()
    
    # Obtener el contenido del PDF
    buffer.seek(0)
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content

if __name__ == "__main__":
    print("Creando factura AFIP de prueba...")
    pdf_content = create_afip_invoice()
    
    # Guardar el PDF
    with open("factura_afip_test.pdf", "wb") as f:
        f.write(pdf_content)
    
    print("Factura AFIP de prueba creada: factura_afip_test.pdf")










