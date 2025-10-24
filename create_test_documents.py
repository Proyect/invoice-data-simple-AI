#!/usr/bin/env python3
"""
Script para crear documentos de prueba de diferentes tipos
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
from datetime import datetime, timedelta

def create_test_documents():
    """Crear documentos de prueba de diferentes tipos"""
    
    documents = []
    
    # 1. Recibo de pago
    print("Creando recibo de pago...")
    receipt_pdf = create_receipt()
    with open("recibo_test.pdf", "wb") as f:
        f.write(receipt_pdf)
    documents.append("recibo_test.pdf")
    
    # 2. Contrato simple
    print("Creando contrato simple...")
    contract_pdf = create_contract()
    with open("contrato_test.pdf", "wb") as f:
        f.write(contract_pdf)
    documents.append("contrato_test.pdf")
    
    # 3. DNI simulado
    print("Creando DNI simulado...")
    dni_pdf = create_dni()
    with open("dni_test.pdf", "wb") as f:
        f.write(dni_pdf)
    documents.append("dni_test.pdf")
    
    # 4. Pasaporte simulado
    print("Creando pasaporte simulado...")
    passport_pdf = create_passport()
    with open("pasaporte_test.pdf", "wb") as f:
        f.write(passport_pdf)
    documents.append("pasaporte_test.pdf")
    
    print(f"\nDocumentos de prueba creados:")
    for doc in documents:
        print(f"  - {doc}")
    
    return documents

def create_receipt():
    """Crear un recibo de pago"""
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Encabezado
    c.setFont("Helvetica-Bold", 16)
    c.drawString(250, height - 50, "RECIBO DE PAGO")
    
    # Línea separadora
    c.line(50, height - 70, 550, height - 70)
    
    # Información del recibo
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 100, "Número de Recibo: 00012345")
    c.drawString(50, height - 120, "Fecha: 15/10/2024")
    c.drawString(50, height - 140, "Hora: 14:30")
    
    # Información del emisor
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 180, "EMISOR:")
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 200, "Empresa de Servicios S.A.")
    c.drawString(50, height - 220, "CUIT: 30-12345678-9")
    c.drawString(50, height - 240, "Av. Corrientes 1234, CABA")
    
    # Información del pagador
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 280, "PAGADO POR:")
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 300, "Juan Carlos Pérez")
    c.drawString(50, height - 320, "DNI: 12345678")
    
    # Concepto y monto
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 360, "CONCEPTO:")
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 380, "Servicios de consultoría IT - Octubre 2024")
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 420, "MONTO:")
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 440, "$ 50,000.00")
    
    # Método de pago
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 480, "Método de pago: Transferencia bancaria")
    c.drawString(50, height - 500, "Referencia: T123456789")
    
    # Firma
    c.line(50, height - 550, 200, height - 550)
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 570, "Firma y sello")
    
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

def create_contract():
    """Crear un contrato simple"""
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Encabezado
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, height - 50, "CONTRATO DE PRESTACIÓN DE SERVICIOS")
    
    # Línea separadora
    c.line(50, height - 70, 550, height - 70)
    
    # Número de contrato
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 100, "Número de Contrato: CON-2024-001234")
    c.drawString(50, height - 120, "Fecha de Inicio: 01/10/2024")
    c.drawString(50, height - 140, "Fecha de Finalización: 31/12/2024")
    
    # Partes del contrato
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 180, "PARTES:")
    
    c.setFont("Helvetica", 11)
    c.drawString(70, height - 200, "CONTRATANTE: Empresa ABC S.A.")
    c.drawString(70, height - 220, "CUIT: 30-87654321-0")
    c.drawString(70, height - 240, "Domicilio: Av. Santa Fe 5678, CABA")
    
    c.drawString(70, height - 280, "CONTRATISTA: Consultora XYZ S.R.L.")
    c.drawString(70, height - 300, "CUIT: 30-11223344-5")
    c.drawString(70, height - 320, "Domicilio: Av. Corrientes 9876, CABA")
    
    # Objeto del contrato
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 360, "OBJETO:")
    c.setFont("Helvetica", 11)
    c.drawString(70, height - 380, "Prestación de servicios de consultoría en sistemas")
    c.drawString(70, height - 400, "informáticos por un período de 3 meses.")
    
    # Monto
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 440, "MONTO TOTAL:")
    c.setFont("Helvetica-Bold", 14)
    c.drawString(70, height - 460, "$ 150,000.00")
    
    # Firma
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 520, "Firma Contratante:")
    c.line(50, height - 540, 250, height - 540)
    
    c.drawString(300, height - 520, "Firma Contratista:")
    c.line(300, height - 540, 500, height - 540)
    
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

def create_dni():
    """Crear un DNI simulado"""
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Marco del DNI
    c.rect(100, height - 400, 400, 300)
    
    # República Argentina
    c.setFont("Helvetica-Bold", 14)
    c.drawString(200, height - 430, "REPÚBLICA ARGENTINA")
    
    # DNI
    c.setFont("Helvetica-Bold", 16)
    c.drawString(250, height - 460, "DOCUMENTO NACIONAL DE IDENTIDAD")
    
    # Número de DNI
    c.setFont("Helvetica-Bold", 24)
    c.drawString(200, height - 490, "DNI 12345678")
    
    # Información personal
    c.setFont("Helvetica", 12)
    c.drawString(120, height - 530, "Apellido: GARCÍA")
    c.drawString(120, height - 550, "Nombres: JUAN CARLOS")
    c.drawString(120, height - 570, "Sexo: M")
    c.drawString(120, height - 590, "Fecha de Nacimiento: 15/03/1985")
    c.drawString(120, height - 610, "Lugar de Nacimiento: BUENOS AIRES")
    c.drawString(120, height - 630, "Nacionalidad: ARGENTINA")
    
    # Domicilio
    c.drawString(120, height - 670, "Domicilio: AV. CORRIENTES 1234")
    c.drawString(120, height - 690, "CP: 1043 - CIUDAD AUTÓNOMA DE BUENOS AIRES")
    
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

def create_passport():
    """Crear un pasaporte simulado"""
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Marco del pasaporte
    c.rect(50, height - 400, 500, 350)
    
    # República Argentina
    c.setFont("Helvetica-Bold", 14)
    c.drawString(200, height - 430, "REPÚBLICA ARGENTINA")
    
    # PASAPORTE
    c.setFont("Helvetica-Bold", 16)
    c.drawString(250, height - 460, "PASAPORTE")
    
    # Número de pasaporte
    c.setFont("Helvetica-Bold", 20)
    c.drawString(200, height - 490, "AR 1234567")
    
    # Información personal
    c.setFont("Helvetica", 12)
    c.drawString(70, height - 530, "Apellido: GARCÍA")
    c.drawString(70, height - 550, "Nombres: JUAN CARLOS")
    c.drawString(70, height - 570, "Sexo: M")
    c.drawString(70, height - 590, "Fecha de Nacimiento: 15/03/1985")
    c.drawString(70, height - 610, "Lugar de Nacimiento: BUENOS AIRES, ARGENTINA")
    c.drawString(70, height - 630, "Nacionalidad: ARGENTINA")
    
    # Fechas del pasaporte
    c.drawString(70, height - 670, "Fecha de Emisión: 01/01/2023")
    c.drawString(70, height - 690, "Fecha de Vencimiento: 01/01/2033")
    
    # Autoridad emisora
    c.drawString(70, height - 730, "Autoridad Emisora: MINISTERIO DEL INTERIOR")
    
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

if __name__ == "__main__":
    create_test_documents()