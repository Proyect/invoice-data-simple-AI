"""
Validadores para datos extraídos de facturas AFIP/ARCA.
CUIT, fechas, CAE, moneda, etc.
"""
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def validate_cuit(cuit: str) -> bool:
    """Valida formato y dígito verificador de CUIT."""
    try:
        clean_cuit = re.sub(r"[^\d]", "", cuit)
        if len(clean_cuit) != 11:
            return False
        if clean_cuit == "0" * 11 or len(set(clean_cuit)) == 1:
            return False
        valid_prefixes = ["20", "23", "24", "25", "26", "27", "30", "33", "34"]
        if clean_cuit[:2] not in valid_prefixes:
            return False
        multipliers = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
        check_digit = int(clean_cuit[-1])
        body = clean_cuit[:-1]
        total = sum(int(d) * m for d, m in zip(body, multipliers))
        remainder = total % 11
        calculated_check = remainder if remainder < 2 else 11 - remainder
        is_valid = calculated_check == check_digit
        if not is_valid:
            logger.warning(f"CUIT inválido (dígito verificador incorrecto): {clean_cuit}")
        return is_valid
    except Exception as e:
        logger.error(f"Error validando CUIT {cuit}: {e}")
        return False


def validate_date(date_str: str) -> bool:
    """Valida formato de fecha DD/MM/YYYY o variantes."""
    if not date_str or not date_str.strip():
        return False
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y"):
        try:
            datetime.strptime(date_str.strip(), fmt)
            return True
        except ValueError:
            continue
    return False


def validate_currency(amount_str: str) -> bool:
    """Valida formato de moneda."""
    if not amount_str:
        return False
    try:
        clean = re.sub(r"[^\d,.]", "", amount_str)
        return bool(re.match(r"^\d{1,3}([.,]\d{3})*([.,]\d{2})?$", clean))
    except Exception:
        return False


def clean_cae_number(cae_str: str) -> str:
    """Limpia número de CAE (espacios, guiones, etc.)."""
    try:
        return re.sub(r"[^\d]", "", cae_str)
    except Exception:
        return ""


def validate_cae_format(cae: str) -> bool:
    """Valida formato del CAE (14 dígitos y rangos de fecha/hora)."""
    try:
        if len(cae) != 14 or not cae.isdigit() or cae == "0" * 14:
            return False
        year = int(cae[:4])
        month = int(cae[4:6])
        day = int(cae[6:8])
        hour = int(cae[8:10])
        minute = int(cae[10:12])
        second = int(cae[12:14])
        current_year = datetime.now().year
        if year < 2000 or year > current_year + 1:
            return False
        if month < 1 or month > 12:
            return False
        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
            days_in_month[1] = 29
        if day < 1 or day > days_in_month[month - 1]:
            return False
        if hour > 23 or minute > 59 or second > 59:
            return False
        return True
    except (ValueError, Exception) as e:
        logger.debug(f"Error validando CAE {cae}: {e}")
        return False


def validate_extracted_data(field_name: str, value: str) -> bool:
    """Valida un valor extraído según el tipo de campo."""
    if not value or not value.strip():
        return False
    if field_name == "cuit":
        return validate_cuit(value)
    if field_name in (
        "fecha_emision",
        "fecha_vencimiento",
        "periodo_desde",
        "periodo_hasta",
        "fecha_inicio_actividades",
    ):
        return validate_date(value)
    if field_name in ("punto_venta", "numero_comprobante"):
        return value.strip().isdigit()
    if field_name in ("subtotal", "importe_total", "importe_otros_tributos"):
        return validate_currency(value)
    if field_name == "cae_numero":
        return validate_cae_format(clean_cae_number(value))
    return True
