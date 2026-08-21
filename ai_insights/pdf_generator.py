import io
from fpdf import FPDF
import pandas as pd
from datetime import datetime

class InformeClinicoPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(30, 41, 59) # Slate Dark
        self.cell(0, 10, "INFORME CLINICO DE BIENESTAR PSICOAFECTIVO", ln=True, align="C")
        self.set_font("Helvetica", "I", 10)
        self.set_text_color(100, 116, 139)
        self.cell(0, 5, "Generado por Bot-Bip - Sistema de Monitorización Diaria", ln=True, align="C")
        self.ln(5)
        # Línea divisoria
        self.set_draw_color(226, 232, 240)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, f"Página {self.page_no()} | Documento de apoyo para consulta profesional de salud mental", align="C")

def generar_pdf_clinico(df: pd.DataFrame, user_id: str = "Usuario", ai_summary: str = "") -> bytes:
    pdf = InformeClinicoPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # 1. Información General del Paciente / Periodo
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, "Resumen Clinico para Consulta Medica", ln=True)
    
    pdf.set_font("Helvetica", "", 10)
    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    total_registros = len(df)
    
    periodo_str = "N/A"
    if not df.empty and "fecha" in df.columns:
        fechas_ord = pd.to_datetime(df["fecha"]).sort_values()
        periodo_str = f"{fechas_ord.iloc[0].strftime('%d/%m/%Y')} al {fechas_ord.iloc[-1].strftime('%d/%m/%Y')}"

    pdf.multi_cell(0, 6, f"- Fecha de emision: {fecha_actual}\n- Periodo evaluado: {periodo_str}\n- Total de evaluaciones registradas: {total_registros}")
    pdf.ln(4)

    # 2. Promedios y Métricas Clave
    if not df.empty:
        prom_energia = round(df["energia"].mean(), 1) if "energia" in df.columns else 0
        prom_humor = round(df["humor"].mean(), 1) if "humor" in df.columns else 0
        prom_sueno = round(df["sueno_horas"].mean(), 1) if "sueno_horas" in df.columns else 0

        pdf.set_fill_color(241, 245, 249)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, "  PROMEDIOS DEL PERIODO", ln=True, fill=True)
        pdf.ln(2)

        pdf.set_font("Helvetica", "", 10)
        pdf.cell(63, 7, f"Energia Promedio: {prom_energia}/10", border=1, align="C")
        pdf.cell(63, 7, f"Animo Promedio: {prom_humor}/10", border=1, align="C")
        pdf.cell(64, 7, f"Sueno Promedio: {prom_sueno}h", border=1, align="C")
        pdf.ln(10)

    # 3. Resumen Interpretativo / Diagnóstico con IA (Si está presente)
    if ai_summary:
        pdf.set_fill_color(238, 242, 255) # Indigo soft
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(49, 46, 129)
        pdf.cell(0, 8, "  ANALISIS DE TENDENCIAS Y PATRONES (AI INSIGHTS)", ln=True, fill=True)
        pdf.ln(2)
        
        pdf.set_font("Helvetica", "", 9.5)
        pdf.set_text_color(30, 41, 59)
        clean_summary = ai_summary.replace("**", "").replace("###", "").replace("##", "").replace("*", "-")
        clean_summary = clean_summary.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 5, clean_summary)
        pdf.ln(6)

    # 4. Tabla Detallada de Registros
    pdf.set_fill_color(241, 245, 249)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, "  DETALLE DE REGISTROS DIARIOS Y NOTAS DE SINTOMAS", ln=True, fill=True)
    pdf.ln(3)

    # Cabecera de Tabla
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(226, 232, 240)
    pdf.cell(28, 7, "Fecha", border=1, align="C", fill=True)
    pdf.cell(22, 7, "Energia", border=1, align="C", fill=True)
    pdf.cell(22, 7, "Animo", border=1, align="C", fill=True)
    pdf.cell(22, 7, "Sueno", border=1, align="C", fill=True)
    pdf.cell(96, 7, "Comentarios / Notas del Paciente", border=1, align="L", fill=True)
    pdf.ln(7)

    pdf.set_font("Helvetica", "", 8.5)
    df_sorted = df.sort_values("fecha", ascending=False) if "fecha" in df.columns else df

    for _, row in df_sorted.iterrows():
        f_val = str(row.get("fecha", ""))[:10]
        e_val = f"{row.get('energia', '-')}/10"
        h_val = f"{row.get('humor', '-')}/10"
        s_val = f"{row.get('sueno_horas', '-')}h"
        com_val = str(row.get("comentarios", "")) if pd.notna(row.get("comentarios")) else ""
        if com_val.lower() == "none" or not com_val:
            com_val = "-"

        # Truncar comentarios si son muy largos
        if len(com_val) > 65:
            com_val = com_val[:62] + "..."

        com_val = com_val.encode('latin-1', 'replace').decode('latin-1')

        pdf.cell(28, 6, f_val, border=1, align="C")
        pdf.cell(22, 6, e_val, border=1, align="C")
        pdf.cell(22, 6, h_val, border=1, align="C")
        pdf.cell(22, 6, s_val, border=1, align="C")
        pdf.cell(96, 6, com_val, border=1, align="L")
        pdf.ln(6)

    return bytes(pdf.output())
