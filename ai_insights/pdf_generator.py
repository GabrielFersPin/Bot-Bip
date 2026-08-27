import io
from fpdf import FPDF
import pandas as pd
from datetime import datetime
from i18n import t, resolve_lang_code

class InformeClinicoPDF(FPDF):
    def __init__(self, lang: str = "es"):
        super().__init__()
        self.lang = resolve_lang_code(lang)

    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(30, 41, 59) # Slate Dark
        title = t("pdf_report_title", self.lang)
        self.cell(0, 10, title, ln=True, align="C")
        self.set_font("Helvetica", "I", 10)
        self.set_text_color(100, 116, 139)
        subtitle = t("pdf_report_subtitle", self.lang)
        self.cell(0, 5, subtitle, ln=True, align="C")
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
        footer_text = f"Página {self.page_no()} | Bot-Bip Clinical Wellness Report" if self.lang != "es" else f"Página {self.page_no()} | Documento de apoyo para consulta profesional de salud mental"
        self.cell(0, 10, footer_text, align="C")

def generar_pdf_clinico(df: pd.DataFrame, user_id: str = "Usuario", ai_summary: str = "", lang: str = "es") -> bytes:
    pdf = InformeClinicoPDF(lang=lang)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # 1. Información General del Paciente / Periodo
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(15, 23, 42)
    head_sec = "Clinical Summary for Medical Consultation" if lang == "en" else ("Résumé clinique pour consultation médicale" if lang == "fr" else "Resumen Clinico para Consulta Medica")
    pdf.cell(0, 7, head_sec, ln=True)
    
    pdf.set_font("Helvetica", "", 10)
    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    total_registros = len(df)
    
    periodo_str = "N/A"
    if not df.empty and "fecha" in df.columns:
        fechas_ord = pd.to_datetime(df["fecha"]).sort_values()
        periodo_str = f"{fechas_ord.iloc[0].strftime('%d/%m/%Y')} - {fechas_ord.iloc[-1].strftime('%d/%m/%Y')}"

    lbl_date = "Issue date" if lang == "en" else ("Date d'émission" if lang == "fr" else "Fecha de emision")
    lbl_period = "Evaluated period" if lang == "en" else ("Période évaluée" if lang == "fr" else "Periodo evaluado")
    lbl_count = "Total logged entries" if lang == "en" else ("Total des évaluations" if lang == "fr" else "Total de evaluaciones registradas")

    pdf.multi_cell(0, 6, f"- {lbl_date}: {fecha_actual}\n- {lbl_period}: {periodo_str}\n- {lbl_count}: {total_registros}")
    pdf.ln(4)

    # 2. Promedios y Métricas Clave
    if not df.empty:
        prom_energia = round(df["energia"].mean(), 1) if "energia" in df.columns else 0
        prom_humor = round(df["humor"].mean(), 1) if "humor" in df.columns else 0
        prom_sueno = round(df["sueno_horas"].mean(), 1) if "sueno_horas" in df.columns else 0

        pdf.set_fill_color(241, 245, 249)
        pdf.set_font("Helvetica", "B", 11)
        lbl_avg_sec = "  PERIOD AVERAGES" if lang == "en" else ("  MOYENNES DE LA PÉRIODE" if lang == "fr" else "  PROMEDIOS DEL PERIODO")
        pdf.cell(0, 8, lbl_avg_sec, ln=True, fill=True)
        pdf.ln(2)

        pdf.set_font("Helvetica", "", 10)
        lbl_e = t("pdf_col_energy", lang)
        lbl_h = t("pdf_col_mood", lang)
        lbl_s = t("pdf_col_sleep", lang)
        pdf.cell(63, 7, f"{lbl_e}: {prom_energia}/10", border=1, align="C")
        pdf.cell(63, 7, f"{lbl_h}: {prom_humor}/10", border=1, align="C")
        pdf.cell(64, 7, f"{lbl_s}: {prom_sueno}h", border=1, align="C")
        pdf.ln(12)

        # 2b. Grafica de Evolución Temporal (Efecto Vectorial)
        pdf.set_fill_color(248, 250, 252)
        pdf.set_font("Helvetica", "B", 10)
        lbl_chart_title = "  WELLNESS TREND CHART" if lang == "en" else ("  GRAPHIQUE D'ÉVOLUTION DU BIEN-ÊTRE" if lang == "fr" else "  GRAFICA DE EVOLUCION Y TENDENCIA DE BIENESTAR")
        pdf.cell(0, 7, lbl_chart_title, ln=True, fill=True)
        pdf.ln(2)

        # Marco del grafico
        gx = 15
        gy = pdf.get_y() + 2
        gw = 180
        gh = 45

        pdf.set_draw_color(203, 213, 225)
        pdf.set_line_width(0.3)
        pdf.rect(gx, gy, gw, gh)

        # Grid lines
        pdf.set_draw_color(241, 245, 249)
        pdf.set_line_width(0.2)
        pdf.line(gx, gy + gh/2, gx + gw, gy + gh/2)

        # Leyenda
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(239, 68, 68)
        pdf.text(gx + 5, gy - 2, f"[---] {lbl_e}")
        pdf.set_text_color(59, 130, 246)
        pdf.text(gx + 50, gy - 2, f"[---] {lbl_h}")
        pdf.set_text_color(16, 185, 129)
        pdf.text(gx + 90, gy - 2, f"[---] {lbl_s}")
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

            if n_points > 1:
                pdf.set_draw_color(239, 68, 68)
                pdf.set_line_width(1.2)
                for i in range(len(pts_e) - 1):
                    pdf.line(pts_e[i][0], pts_e[i][1], pts_e[i+1][0], pts_e[i+1][1])

                pdf.set_draw_color(59, 130, 246)
                pdf.set_line_width(1.2)
                for i in range(len(pts_h) - 1):
                    pdf.line(pts_h[i][0], pts_h[i][1], pts_h[i+1][0], pts_h[i+1][1])

                pdf.set_draw_color(16, 185, 129)
                pdf.set_line_width(1.2)
                for i in range(len(pts_s) - 1):
                    pdf.line(pts_s[i][0], pts_s[i][1], pts_s[i+1][0], pts_s[i+1][1])

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
        pdf.set_fill_color(238, 242, 255)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(49, 46, 129)
        lbl_ai_sec = "  AI INSIGHTS AND TREND ANALYSIS" if lang == "en" else ("  ANALYSE ET TENDANCES PAR IA" if lang == "fr" else "  ANALISIS DE TENDENCIAS Y PATRONES (AI INSIGHTS)")
        pdf.cell(0, 8, lbl_ai_sec, ln=True, fill=True)
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
    lbl_table_sec = "  DAILY LOG DETAILS AND SYMPTOM NOTES" if lang == "en" else ("  DÉTAIL DES ENREGISTREMENTS QUOTIDIENS ET NOTES" if lang == "fr" else "  DETALLE DE REGISTROS DIARIOS Y NOTAS DE SINTOMAS")
    pdf.cell(0, 8, lbl_table_sec, ln=True, fill=True)
    pdf.ln(3)

    # Cabecera de Tabla
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(226, 232, 240)
    pdf.cell(26, 7, t("pdf_col_date", lang), border=1, align="C", fill=True)
    pdf.cell(18, 7, t("pdf_col_energy", lang), border=1, align="C", fill=True)
    pdf.cell(18, 7, t("pdf_col_mood", lang), border=1, align="C", fill=True)
    pdf.cell(18, 7, t("pdf_col_sleep", lang), border=1, align="C", fill=True)
    pdf.cell(24, 7, t("pdf_col_medication", lang), border=1, align="C", fill=True)
    pdf.cell(86, 7, t("pdf_col_notes", lang), border=1, align="L", fill=True)
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
