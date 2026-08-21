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
        pdf.ln(12)

        # 2b. Grafica de Evolución Temporal (Efecto Vectorial)
        pdf.set_fill_color(248, 250, 252)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 7, "  GRAFICA DE EVOLUCION Y TENDENCIA DE BIENESTAR", ln=True, fill=True)
        pdf.ln(2)

        # Marco del grafico
        gx = 15
        gy = pdf.get_y() + 2
        gw = 180
        gh = 45

        pdf.set_draw_color(203, 213, 225)
        pdf.set_line_width(0.3)
        pdf.rect(gx, gy, gw, gh)

        # Grid lines (0, 5, 10)
        pdf.set_draw_color(241, 245, 249)
        pdf.set_line_width(0.2)
        pdf.line(gx, gy + gh/2, gx + gw, gy + gh/2)

        # Leyenda
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(239, 68, 68) # Rojo Energia
        pdf.text(gx + 5, gy - 2, "[---] Energia")
        pdf.set_text_color(59, 130, 246) # Azul Animo
        pdf.text(gx + 50, gy - 2, "[---] Animo")
        pdf.set_text_color(16, 185, 129) # Verde Sueno
        pdf.text(gx + 90, gy - 2, "[---] Sueno (Horas)")
        pdf.set_text_color(30, 41, 59)

        # Dibujar puntos y líneas de la gráfica
        df_chart = df.sort_values("fecha") if "fecha" in df.columns else df
        n_points = len(df_chart)

        if n_points >= 1:
            step_x = (gw / (n_points - 1)) if n_points > 1 else (gw / 2)
            pts_e, pts_h, pts_s = [], [], []

            for i, (_, row) in enumerate(df_chart.iterrows()):
                px = (gx + (i * step_x)) if n_points > 1 else (gx + gw / 2)
                e_val = float(row.get("energia", 5))
                h_val = float(row.get("humor", 5))
                s_val = float(row.get("sueno_horas", 8))

                py_e = gy + gh - (e_val / 10.0 * gh)
                py_h = gy + gh - (h_val / 10.0 * gh)
                py_s = gy + gh - (min(s_val, 12) / 12.0 * gh)

                pts_e.append((px, py_e))
                pts_h.append((px, py_h))
                pts_s.append((px, py_s))

            # 1. Dibujar Líneas con mayor grosor (1.5mm)
            if n_points > 1:
                pdf.set_draw_color(239, 68, 68) # Rojo Energia
                pdf.set_line_width(1.2)
                for i in range(len(pts_e) - 1):
                    pdf.line(pts_e[i][0], pts_e[i][1], pts_e[i+1][0], pts_e[i+1][1])

                pdf.set_draw_color(59, 130, 246) # Azul Animo
                pdf.set_line_width(1.2)
                for i in range(len(pts_h) - 1):
                    pdf.line(pts_h[i][0], pts_h[i][1], pts_h[i+1][0], pts_h[i+1][1])

                pdf.set_draw_color(16, 185, 129) # Verde Sueno
                pdf.set_line_width(1.2)
                for i in range(len(pts_s) - 1):
                    pdf.line(pts_s[i][0], pts_s[i][1], pts_s[i+1][0], pts_s[i+1][1])

            # 2. Dibujar Puntos/Pulsos Destacados Visibles (Radio 2.2mm con relleno)
            for px, py in pts_e:
                pdf.set_fill_color(239, 68, 68)
                pdf.set_draw_color(185, 28, 28)
                pdf.ellipse(px - 2, py - 2, 4, 4, "DF")

            for px, py in pts_h:
                pdf.set_fill_color(59, 130, 246)
                pdf.set_draw_color(29, 78, 216)
                pdf.ellipse(px - 2, py - 2, 4, 4, "DF")

            for px, py in pts_s:
                pdf.set_fill_color(16, 185, 129)
                pdf.set_draw_color(4, 120, 87)
                pdf.ellipse(px - 2, py - 2, 4, 4, "DF")

        pdf.set_y(gy + gh + 6)

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
    pdf.cell(26, 7, "Fecha", border=1, align="C", fill=True)
    pdf.cell(18, 7, "Energia", border=1, align="C", fill=True)
    pdf.cell(18, 7, "Animo", border=1, align="C", fill=True)
    pdf.cell(18, 7, "Sueno", border=1, align="C", fill=True)
    pdf.cell(24, 7, "Medicacion", border=1, align="C", fill=True)
    pdf.cell(86, 7, "Comentarios / Notas", border=1, align="L", fill=True)
    pdf.ln(7)

    pdf.set_font("Helvetica", "", 8.5)
    df_sorted = df.sort_values("fecha", ascending=False) if "fecha" in df.columns else df

    for _, row in df_sorted.iterrows():
        f_val = str(row.get("fecha", ""))[:10]
        e_val = f"{row.get('energia', '-')}/10"
        h_val = f"{row.get('humor', '-')}/10"
        s_val = f"{row.get('sueno_horas', '-')}h"
        raw_com = str(row.get("comentarios", "")) if pd.notna(row.get("comentarios")) else ""

        # Extraer medicación si está prefijada
        med_val = "-"
        com_val = raw_com
        if "[Medicacion:" in raw_com:
            try:
                parts = raw_com.split("]", 1)
                med_val = parts[0].replace("[Medicacion:", "").strip()
                com_val = parts[1].strip() if len(parts) > 1 else ""
            except Exception:
                pass

        if com_val.lower() == "none" or not com_val:
            com_val = "-"

        if len(com_val) > 55:
            com_val = com_val[:52] + "..."

        com_val = com_val.encode('latin-1', 'replace').decode('latin-1')
        med_val = med_val.encode('latin-1', 'replace').decode('latin-1')

        pdf.cell(26, 6, f_val, border=1, align="C")
        pdf.cell(18, 6, e_val, border=1, align="C")
        pdf.cell(18, 6, h_val, border=1, align="C")
        pdf.cell(18, 6, s_val, border=1, align="C")
        pdf.cell(24, 6, med_val, border=1, align="C")
        pdf.cell(86, 6, com_val, border=1, align="L")
        pdf.ln(6)

    return bytes(pdf.output())
