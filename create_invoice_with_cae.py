#!/usr/bin/env python3
"""
Script para crear una factura AFIP con CAE realista para pruebas
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
from datetime import datetime, timedelta

def create_invoice_with_cae():
    """Crear una factura AFIP con CAE realista"""
    
    # Crear buffer para el PDF
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Generar CAE realista (formato: AAAAMMDDHHMMSS)
    now = datetime.now()
    cae_number = now.strftime("%Y%m%d%H%M%S")
    
    # ORIGINAL
    c.setFont("Helvetica-Bold", 16)
    c.drawString(width/2 - 40, height - 50, "ORIGINAL")
    
    # Caja con código
    c.rect(width/2 - 100, height - 120, 80, 60)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(width/2 - 70, height - 90, "C")
    c.setFont("Helvetica", 12)
    c.drawString(width/2 - 85, height - 110, "COD. 011")
    
    # FACTURA
    c.setFont("Helvetica-Bold", 20)
    c.drawString(width/2 + 20, height - 80, "FACTURA")
    
    # Información del comprobante (lado derecho)
    c.setFont("Helvetica", 11)
    c.drawString(width/2 + 20, height - 100, "Punto de Venta: 00001")
    c.drawString(width/2 + 20, height - 115, "Comp. Nro: 00012345")
    c.drawString(width/2 + 20, height - 130, "Fecha de Emisión: 15/10/2024")
    
    # Sección del emisor (lado izquierdo)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 180, "Razón Social:")
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 195, "EMPRESA EJEMPLO S.A.")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 210, "Domicilio Comercial:")
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 225, "Av. Corrientes 1234, CABA, CP 1043")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 240, "Condición frente al IVA:")
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 255, "Responsable Inscripto")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 270, "CUIT:")
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 285, "30-12345678-9")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 300, "Período Facturado Desde:")
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 315, "01/10/2024")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 330, "Hasta:")
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 345, "31/10/2024")
    
    # Sección del comprador (lado derecho)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(width/2 + 50, height - 180, "CUIT:")
    c.setFont("Helvetica", 11)
    c.drawString(width/2 + 50, height - 195, "20-87654321-0")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(width/2 + 50, height - 210, "Ingresos Brutos:")
    c.setFont("Helvetica", 11)
    c.drawString(width/2 + 50, height - 225, "30-12345678-9")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(width/2 + 50, height - 240, "Fecha de Inicio de Actividades:")
    c.setFont("Helvetica", 11)
    c.drawString(width/2 + 50, height - 255, "01/01/2020")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(width/2 + 50, height - 270, "Fecha de Vto. para el pago:")
    c.setFont("Helvetica", 11)
    c.drawString(width/2 + 50, height - 285, "15/11/2024")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(width/2 + 50, height - 300, "Apellido y Nombre / Razón Social:")
    c.setFont("Helvetica", 11)
    c.drawString(width/2 + 50, height - 315, "CLIENTE EJEMPLO S.R.L.")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(width/2 + 50, height - 330, "Domicilio:")
    c.setFont("Helvetica", 11)
    c.drawString(width/2 + 50, height - 345, "Av. Santa Fe 5678, CABA, CP 1060")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(width/2 + 50, height - 360, "Condición frente al IVA:")
    c.setFont("Helvetica", 11)
    c.drawString(width/2 + 50, height - 375, "Responsable Inscripto")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(width/2 + 50, height - 390, "Condición de venta:")
    c.setFont("Helvetica", 11)
    c.drawString(width/2 + 50, height - 405, "30 días")
    
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
    
    # Línea separadora
    c.line(50, y_table - 5, 720, y_table - 5)
    
    # Producto 1
    y_product1 = y_table - 20
    c.setFont("Helvetica", 9)
    c.drawString(50, y_product1, "SRV001")
    c.drawString(150, y_product1, "Servicio de Consultoría IT")
    c.drawString(350, y_product1, "40,00")
    c.drawString(420, y_product1, "hs")
    c.drawString(480, y_product1, "2500,00")
    c.drawString(540, y_product1, "0,00")
    c.drawString(580, y_product1, "0,00")
    c.drawString(640, y_product1, "100000,00")
    
    # Totales (lado derecho)
    y_totals = y_product1 - 40
    c.setFont("Helvetica-Bold", 11)
    c.drawString(500, y_totals, "Subtotal: $100000,00")
    c.drawString(500, y_totals - 15, "Importe Otros Tributos: $0,00")
    c.drawString(500, y_totals - 30, "Importe Total: $100000,00")
    
    # Footer AFIP
    y_footer = 100
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_footer, "AFIP")
    c.setFont("Helvetica", 9)
    c.drawString(50, y_footer - 15, "Comprobante Autorizado")
    
    # Página
    c.setFont("Helvetica", 11)
    c.drawString(width/2 - 20, y_footer, "Pág. 1/1")
    
    # CAE - Con formato más grande y claro
    c.setFont("Helvetica-Bold", 12)
    c.drawString(500, y_footer, "CAE N°: " + cae_number)
    cae_venc = (now + timedelta(days=30)).strftime("%d/%m/%Y")
    c.drawString(500, y_footer - 15, "Fecha de Vto. de CAE: " + cae_venc)
    
    c.save()
    
    # Obtener el contenido del PDF
    buffer.seek(0)
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content, cae_number

if __name__ == "__main__":
    print("Creando factura AFIP con CAE realista...")
    pdf_content, cae_number = create_invoice_with_cae()
    
    # Guardar el PDF
    with open("factura_con_cae.pdf", "wb") as f:
        f.write(pdf_content)
    
    print(f"Factura AFIP con CAE creada: factura_con_cae.pdf")
    print(f"CAE generado: {cae_number}")










