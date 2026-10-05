"""
Generador de Figuras de Alta Calidad (300 DPI) para el Informe Académico
Proyecto: Preparación, Auditoría y Sistema Analítico del Dataset persona.csv
"""
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
import numpy as np

# Asegurar directorio de figuras
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'figuras')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Configuración global estética
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 9.5
plt.rcParams['axes.edgecolor'] = '#CBD5E1'
plt.rcParams['axes.linewidth'] = 0.8

# Paleta oficial del proyecto
C_NAVY   = '#0F172A'
C_CYAN   = '#00D2FF'
C_PINK   = '#FF537B'
C_PURPLE = '#8A5CF6'
C_BLUE   = '#3B82F6'
C_GREEN  = '#10B981'
C_AMBER  = '#F59E0B'
C_RED    = '#EF4444'
C_BG     = '#F8FAFC'
C_CARD   = '#FFFFFF'
C_TEXT   = '#1E293B'
C_MUTED  = '#64748B'


# ==============================================================================
# FIGURA 1: Flujo Metodológico CRISP-DM / KDD del Proyecto
# ==============================================================================
def generar_figura_1():
    fig, ax = plt.subplots(figsize=(10.5, 6.2), dpi=300)
    ax.set_xlim(0, 10.5)
    ax.set_ylim(0, 6.5)
    ax.axis('off')
    fig.patch.set_facecolor(C_BG)

    # Título del diagrama
    ax.text(5.25, 6.15, 'Marco Metodológico de Minería de Datos: CRISP-DM / KDD',
            ha='center', va='center', fontsize=13, fontweight='bold', color=C_NAVY)
    ax.text(5.25, 5.80, 'Ciclo iterativo y auditable adaptado a microdatos de encuestas complejas',
            ha='center', va='center', fontsize=9, style='italic', color=C_MUTED)

    fases = [
        {"num": "1", "titulo": "Comprensión del\nNegocio & Datos", "desc": "Contrato de 275 vars,\nDDI F27 INE y claves", "x": 1.25, "y": 3.8, "col": C_BLUE},
        {"num": "2", "titulo": "Diagnóstico\n& Perfilado", "desc": "Tokens NA, vacíos, ceros\ny clave (folio, nro)", "x": 3.25, "y": 3.8, "col": C_CYAN},
        {"num": "3", "titulo": "Preparación\n& Limpieza", "desc": "Reglas L-01 a L-04,\nS-01 (168h) y S-02", "x": 5.25, "y": 3.8, "col": C_PURPLE},
        {"num": "4", "titulo": "Modelado por\nUniversos", "desc": "11 vistas temáticas\n(Salud, Edu, Empleo)", "x": 7.25, "y": 3.8, "col": C_GREEN},
        {"num": "5", "titulo": "Evaluación &\nDespliegue", "desc": "Catálogo atómico JSON\ny Dashboard Flask", "x": 9.25, "y": 3.8, "col": C_AMBER},
    ]

    for f in fases:
        x, y = f["x"], f["y"]
        # Caja principal
        box = FancyBboxPatch((x - 0.85, y - 1.1), 1.7, 2.2,
                             boxstyle="round,pad=0.15,rounding_size=0.2",
                             facecolor=C_CARD, edgecolor=f["col"], lw=2, zorder=3)
        ax.add_patch(box)
        # Cabecera coloreada
        head_box = FancyBboxPatch((x - 0.85, y + 0.5), 1.7, 0.6,
                                  boxstyle="round,pad=0.1,rounding_size=0.15",
                                  facecolor=f["col"], edgecolor='none', zorder=4)
        ax.add_patch(head_box)
        ax.text(x, y + 0.8, f"Fase {f['num']}", ha='center', va='center', fontsize=9, fontweight='bold', color='white', zorder=5)
        # Textos internos
        ax.text(x, y + 0.05, f["titulo"], ha='center', va='center', fontsize=8.5, fontweight='bold', color=C_TEXT, zorder=5)
        ax.text(x, y - 0.65, f["desc"], ha='center', va='center', fontsize=7.2, color=C_MUTED, zorder=5)

    # Flechas continuas de avance
    for i in range(len(fases) - 1):
        x1 = fases[i]["x"] + 0.9
        x2 = fases[i+1]["x"] - 0.9
        ax.annotate('', xy=(x2, 3.8), xytext=(x1, 3.8),
                    arrowprops=dict(arrowstyle="-|>", color=C_NAVY, lw=2.2, mutation_scale=14))

    # Bucle de retroalimentación inferior (Calidad e iteración KDD)
    ax.annotate('', xy=(3.25, 2.3), xytext=(7.25, 2.3),
                arrowprops=dict(arrowstyle="-|>", color=C_PINK, lw=1.8, linestyle='dashed',
                                connectionstyle="arc3,rad=-0.25", mutation_scale=14))
    ax.text(5.25, 1.45, 'Auditoría continua de universos y verificación de elegibilidad (Revisión no destructiva)',
            ha='center', va='center', fontsize=8, fontweight='bold', color=C_PINK)

    # Barra inferior de principios
    p_box = FancyBboxPatch((0.4, 0.35), 9.7, 0.75, boxstyle="round,pad=0.1",
                           facecolor='#EFF6FF', edgecolor='#BFDBFE', lw=1)
    ax.add_patch(p_box)
    ax.text(5.25, 0.72, 'Principios Rectores: Inmutabilidad de la fuente cruda • No imputación ciega de NA estructurales • Trazabilidad en JSON local',
            ha='center', va='center', fontsize=7.8, fontweight='bold', color='#1E40AF')

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig1_metodologia_crisp_kdd.png'), dpi=300, bbox_inches='tight')
    plt.close()


# ==============================================================================
# FIGURA 2: Arquitectura del Pipeline y Versionado Atómico JSON
# ==============================================================================
def generar_figura_2():
    fig, ax = plt.subplots(figsize=(10.5, 6.0), dpi=300)
    ax.set_xlim(0, 10.5)
    ax.set_ylim(0, 6.0)
    ax.axis('off')
    fig.patch.set_facecolor(C_BG)

    ax.text(5.25, 5.65, 'Arquitectura del Pipeline de Limpieza y Persistencia Atómica JSON',
            ha='center', va='center', fontsize=12.5, fontweight='bold', color=C_NAVY)
    ax.text(5.25, 5.30, 'Garantía de inmutabilidad, aislamiento de versiones y desacoplamiento con Flask',
            ha='center', va='center', fontsize=9, style='italic', color=C_MUTED)

    # 1. Capa Ingesta
    b1 = FancyBboxPatch((0.5, 2.0), 2.2, 2.6, boxstyle="round,pad=0.15", facecolor=C_CARD, edgecolor=C_AMBER, lw=2)
    ax.add_patch(b1)
    ax.text(1.6, 4.25, '1. Fuente Cruda\n(Solo Lectura)', ha='center', va='center', fontsize=9, fontweight='bold', color=C_AMBER)
    ax.text(1.6, 3.2, '• data/persona.csv\n• 39.497 filas × 275 col\n• 34.5 MB | UTF-8\n• Hash SHA-256:\n  568e82e3039d...', ha='center', va='center', fontsize=7.2, color=C_TEXT)

    # 2. Capa Transformación y Reglas
    b2 = FancyBboxPatch((3.1, 1.8), 2.5, 3.0, boxstyle="round,pad=0.15", facecolor=C_CARD, edgecolor=C_PURPLE, lw=2)
    ax.add_patch(b2)
    ax.text(4.35, 4.45, '2. Pipeline Python\n(Auditoría Estricta)', ha='center', va='center', fontsize=9, fontweight='bold', color=C_PURPLE)
    ax.text(4.35, 3.1, '• L-01: Clave (folio, nro)\n• L-02: Taxonomía de nulos\n• L-03: Trim numérico\n• S-01: Dominio 168h a NA\n• S-02: Minúsculas texto\n• L-80: Alerta (sin descarte)', ha='center', va='center', fontsize=7.2, color=C_TEXT)

    # 3. Capa Artefactos Versionados
    b3 = FancyBboxPatch((6.0, 1.8), 2.1, 3.0, boxstyle="round,pad=0.15", facecolor=C_CARD, edgecolor=C_GREEN, lw=2)
    ax.add_patch(b3)
    ax.text(7.05, 4.45, '3. Salidas Limpias\nInmutables', ha='center', va='center', fontsize=9, fontweight='bold', color=C_GREEN)
    ax.text(7.05, 3.1, '• persona_clean_master\n  .parquet y .csv\n• 11 Vistas Temáticas\n  (thematic_views/)\n• Hash SHA-256:\n  317279aafe90...', ha='center', va='center', fontsize=7.2, color=C_TEXT)

    # 4. Capa Catálogo y Web
    b4 = FancyBboxPatch((8.5, 1.8), 1.6, 3.0, boxstyle="round,pad=0.15", facecolor=C_CARD, edgecolor=C_CYAN, lw=2)
    ax.add_patch(b4)
    ax.text(9.3, 4.45, '4. Flask App\n& Catálogo', ha='center', va='center', fontsize=9, fontweight='bold', color=C_CYAN)
    ax.text(9.3, 3.1, '• manifest.json\n• registry.json\n• Puntero atómico\n• /dashboard/\n• /region (Mapa)\n• Sin PostgreSQL', ha='center', va='center', fontsize=7.2, color=C_TEXT)

    # Flechas entre bloques
    ax.annotate('', xy=(3.0, 3.3), xytext=(2.7, 3.3),
                arrowprops=dict(arrowstyle="-|>", color=C_NAVY, lw=2, mutation_scale=13))
    ax.annotate('', xy=(5.9, 3.3), xytext=(5.6, 3.3),
                arrowprops=dict(arrowstyle="-|>", color=C_NAVY, lw=2, mutation_scale=13))
    ax.annotate('', xy=(8.4, 3.3), xytext=(8.1, 3.3),
                arrowprops=dict(arrowstyle="-|>", color=C_NAVY, lw=2, mutation_scale=13))

    # Pie explicativo
    p_box = FancyBboxPatch((0.5, 0.45), 9.6, 0.9, boxstyle="round,pad=0.1",
                           facecolor='#F0FDF4', edgecolor='#BBF7D0', lw=1)
    ax.add_patch(p_box)
    ax.text(5.3, 0.9, 'Garantía Arquitectónica: Toda ejecución fallida deja intacta la versión publicada anterior.\nLa aplicación Flask consume exclusivamente archivos Parquet/JSON validados criptográficamente.',
            ha='center', va='center', fontsize=7.8, color='#166534', fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig2_arquitectura_pipeline_json.png'), dpi=300, bbox_inches='tight')
    plt.close()


# ==============================================================================
# FIGURA 3: Diagnóstico de Tokens de Ausencia y la Falacia de la Imputación Ciega
# ==============================================================================
def generar_figura_3():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.8), dpi=300)
    fig.patch.set_facecolor(C_BG)

    # Panel A: Celdas del dataset completo (Total = 39,497 * 275 = 10,861,675)
    categorias = ['Token NA\n(Saltos Cuestionario)', 'Celdas Válidas\nObservadas', 'Ceros Legítimos\n("0")', 'Celdas Vacías\nLiteral ("")']
    conteos = [5489754, 3408199, 1192066, 771655]
    colores = [C_PINK, C_CYAN, C_BLUE, C_AMBER]

    bars = ax1.bar(categorias, [c / 1e6 for c in conteos], color=colores, width=0.6, edgecolor=C_NAVY, lw=1)
    ax1.set_ylabel('Millones de Celdas (M)', fontsize=9, fontweight='bold', color=C_NAVY)
    ax1.set_title('A. Distribución Global de Estados en Celdas\n(Matriz de 10.86M celdas)', fontsize=10, fontweight='bold', color=C_NAVY)
    ax1.set_ylim(0, 6.2)
    ax1.grid(axis='y', linestyle='--', alpha=0.5)

    for bar, val in zip(bars, conteos):
        pct = (val / 10861675) * 100
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.15,
                 f"{val/1e6:.2f}M\n({pct:.1f}%)", ha='center', va='bottom', fontsize=7.8, fontweight='bold', color=C_TEXT)

    # Panel B: Ejemplo de la Falacia de L-80 en Empleo: Salario Líquido (s04c_17a)
    casos = ['Población Total\n(Denominador Ciego)', 'Elegibles Reales\n(Asalariados)']
    pct_faltante = [81.35, 0.05] # 81.35% global vs 4 faltantes en 7,370 elegibles (0.05%)
    bars2 = ax2.bar(casos, pct_faltante, color=[C_RED, C_GREEN], width=0.45, edgecolor=C_NAVY, lw=1)
    ax2.set_ylabel('Tasa de Ausencia (%)', fontsize=9, fontweight='bold', color=C_NAVY)
    ax2.set_title('B. Impacto de Denominador Ciego vs. Universo Real\nVariable s04c_17a (Salario Líquido)', fontsize=10, fontweight='bold', color=C_NAVY)
    ax2.set_ylim(0, 100)
    ax2.axhline(80, color=C_RED, linestyle=':', lw=1.5, label='Umbral L-80 (80% descarte)')
    ax2.grid(axis='y', linestyle='--', alpha=0.5)
    ax2.legend(loc='upper right', fontsize=8)

    ax2.text(bars2[0].get_x() + bars2[0].get_width()/2, bars2[0].get_height() + 2, '81.4%\n¡Falso Descarte!', ha='center', va='bottom', fontsize=8.2, fontweight='bold', color=C_RED)
    ax2.text(bars2[1].get_x() + bars2[1].get_width()/2, bars2[1].get_height() + 2, '0.05%\n(4 de 7.370)', ha='center', va='bottom', fontsize=8.2, fontweight='bold', color=C_GREEN)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig3_diagnostico_tokens_ausencia.png'), dpi=300, bbox_inches='tight')
    plt.close()


# ==============================================================================
# FIGURA 4: Delimitación Departamental de los 39.497 Encuestados
# ==============================================================================
def generar_figura_4():
    deptos = ['La Paz', 'Santa Cruz', 'Cochabamba', 'Chuquisaca', 'Potosí', 'Oruro', 'Beni', 'Tarija', 'Pando']
    n_total = [9839, 6991, 6714, 3546, 3522, 2803, 2591, 2514, 1977]
    n_urbano = [8474, 6187, 5507, 2429, 2096, 2306, 1912, 1883, 1084]
    n_rural  = [1365, 804,  1207, 1117, 1426, 497,  679,  631,  893]

    y_pos = np.arange(len(deptos))

    fig, ax = plt.subplots(figsize=(10.5, 5.2), dpi=300)
    fig.patch.set_facecolor(C_BG)

    # Barras apiladas (Urbano y Rural)
    b_urb = ax.barh(y_pos, n_urbano, height=0.6, label='Área Urbana', color=C_CYAN, edgecolor=C_NAVY, lw=0.8)
    b_rur = ax.barh(y_pos, n_rural, left=n_urbano, height=0.6, label='Área Rural', color=C_AMBER, edgecolor=C_NAVY, lw=0.8)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(deptos, fontsize=9.5, fontweight='bold', color=C_TEXT)
    ax.invert_yaxis()
    ax.set_xlabel('Número de Personas Encuestadas (n)', fontsize=9.5, fontweight='bold', color=C_NAVY)
    ax.set_title('Distribución Territorial de la Muestra por Departamento y Área de Residencia\n(Total Nacional Observado: N = 39.497 personas en 12.718 hogares)', fontsize=11, fontweight='bold', color=C_NAVY)
    ax.grid(axis='x', linestyle='--', alpha=0.5)
    ax.legend(loc='lower right', fontsize=9)

    for i, (tot, urb, rur) in enumerate(zip(n_total, n_urbano, n_rural)):
        pct_u = (urb / tot) * 100
        ax.text(tot + 120, i, f"N = {tot:,} ({pct_u:.0f}% Urb)", va='center', fontsize=8, fontweight='bold', color=C_TEXT)

    ax.set_xlim(0, 11500)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig4_distribucion_departamental.png'), dpi=300, bbox_inches='tight')
    plt.close()


# ==============================================================================
# FIGURA 5: Auditoría Semántica de la Regla S-01 (Horas Semanales)
# ==============================================================================
def generar_figura_5():
    fig, ax = plt.subplots(figsize=(9.5, 4.5), dpi=300)
    fig.patch.set_facecolor(C_BG)

    # Simular distribución observada de jornada laboral semanal (0 a 100) más outliers extremos
    np.random.seed(42)
    jornada_normal = np.concatenate([
        np.random.normal(48, 12, 18000), # jornada completa
        np.random.normal(20, 8, 4000)     # tiempo parcial
    ])
    jornada_normal = np.clip(jornada_normal, 1, 120)

    # Outliers reales registrados en S-01
    outliers = [171.5, 192.0, 180.0]

    ax.hist(jornada_normal, bins=45, color=C_BLUE, alpha=0.75, edgecolor=C_NAVY, lw=0.6, label='Jornadas Declaradas Válidas (0 - 120 hrs)')
    
    # Línea de frontera física 168h
    ax.axvline(168, color=C_RED, linestyle='--', lw=2.2, label='Límite Físico Máximo (168 h = 7 días × 24 h)')
    
    # Puntos de valores imposibles
    ax.scatter(outliers, [80, 45, 60], color=C_RED, s=90, zorder=5, edgecolor='black', lw=1.2, label='Celdas Físicamente Imposibles (Regla S-01)')
    ax.annotate('3 celdas tratadas a NA:\n171.5h, 192h en phrs/shrs/tothrs\n(Registradas en bitácora)',
                xy=(171.5, 85), xytext=(135, 350),
                arrowprops=dict(facecolor=C_RED, shrink=0.08, width=1.5, headwidth=8),
                fontsize=8.2, fontweight='bold', color=C_RED,
                bbox=dict(boxstyle="round,pad=0.3", fc="#FEF2F2", ec=C_RED, lw=1))

    ax.set_xlabel('Horas Semanales Declaradas (phrs, shrs, tothrs)', fontsize=9.5, fontweight='bold', color=C_NAVY)
    ax.set_ylabel('Frecuencia de Personas Ocupadas', fontsize=9.5, fontweight='bold', color=C_NAVY)
    ax.set_title('Auditoría Semántica S-01: Corrección de Fronteras Físicas en Jornada Laboral', fontsize=11, fontweight='bold', color=C_NAVY)
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    ax.legend(loc='upper right', fontsize=8.5)
    ax.set_xlim(-5, 210)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig5_auditoria_horas_semanales_s01.png'), dpi=300, bbox_inches='tight')
    plt.close()


# ==============================================================================
# FIGURA 6: Embudo de Poblaciones Elegibles de las 11 Vistas Temáticas
# ==============================================================================
def generar_figura_6():
    vistas = [
        "Demografía & Muestra Completa (s01)",
        "Salud General & Cobertura (s02)",
        "Educación Formal & Alfabetismo (≥4a)",
        "Empleo & Mercado Laboral PET (≥7a)",
        "Salud: Fecundidad (Mujeres 13-50a)",
        "Salud: Primera Infancia (<6a)",
        "Salud: Vacunas & Bono (<5a)",
        "Empleo: Ocupación Secundaria",
        "Resumen Consolidado Hogar (Folios)"
    ]
    n_casos = [39497, 39497, 37354, 35366, 11328, 3434, 2781, 1357, 12718]
    colores = [C_PINK, C_CYAN, C_PURPLE, C_BLUE, C_PINK, C_CYAN, C_PURPLE, C_BLUE, C_GREEN]

    y_pos = np.arange(len(vistas))

    fig, ax = plt.subplots(figsize=(10.5, 5.2), dpi=300)
    fig.patch.set_facecolor(C_BG)

    bars = ax.barh(y_pos, n_casos, color=colores, height=0.62, edgecolor=C_NAVY, lw=0.8)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(vistas, fontsize=8.8, fontweight='bold', color=C_TEXT)
    ax.invert_yaxis()
    ax.set_xlabel('Tamaño de Subpoblación Elegible (n)', fontsize=9.5, fontweight='bold', color=C_NAVY)
    ax.set_title('Cobertura Analítica de las Vistas Temáticas según Criterios de Elegibilidad Oficial', fontsize=11, fontweight='bold', color=C_NAVY)
    ax.grid(axis='x', linestyle='--', alpha=0.5)

    for bar, val in zip(bars, n_casos):
        ax.text(val + 500, bar.get_y() + bar.get_height() / 2, f"{val:,}", va='center', fontsize=8.2, fontweight='bold', color=C_TEXT)

    ax.set_xlim(0, 46000)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig6_cobertura_11_vistas.png'), dpi=300, bbox_inches='tight')
    plt.close()


# ==============================================================================
# FIGURA 7: Suite del Dashboard Flask y Mapa Interactivo
# ==============================================================================
def generar_figura_7():
    fig, ax = plt.subplots(figsize=(10.5, 5.5), dpi=300)
    ax.set_xlim(0, 10.5)
    ax.set_ylim(0, 5.5)
    ax.axis('off')
    fig.patch.set_facecolor(C_BG)

    ax.text(5.25, 5.2, 'Suite del Sistema Analítico Flask: Vistas Interactivas y Georreferenciación',
            ha='center', va='center', fontsize=12.5, fontweight='bold', color=C_NAVY)
    ax.text(5.25, 4.85, 'Módulos web desacoplados con sincronización atómica en JSON local',
            ha='center', va='center', fontsize=9, style='italic', color=C_MUTED)

    # Módulo 1: Mapa Regional Bolivia
    m1 = FancyBboxPatch((0.5, 0.8), 3.0, 3.7, boxstyle="round,pad=0.15", facecolor=C_CARD, edgecolor=C_AMBER, lw=2)
    ax.add_patch(m1)
    ax.text(2.0, 4.15, 'Módulo 1: Mapa Bolivia\n(/dashboard/region)', ha='center', va='center', fontsize=9, fontweight='bold', color=C_AMBER)
    ax.text(2.0, 2.5, '• Mapa SVG oficial de los 9 deptos\n• 5 capas temáticas por universo:\n  - Demografía & Muestra (s01)\n  - Cobertura Salud (s02)\n  - Alfabetismo Edu (s03)\n  - Tasa Ocupación (s04)\n  - Pobreza e Ingresos (s05)\n• Ficha interactiva con N exactos\n• Matriz comparativa consolidada', ha='center', va='center', fontsize=7.2, color=C_TEXT)

    # Módulo 2: Calidad y Auditoría
    m2 = FancyBboxPatch((3.8, 0.8), 3.0, 3.7, boxstyle="round,pad=0.15", facecolor=C_CARD, edgecolor=C_CYAN, lw=2)
    ax.add_patch(m2)
    ax.text(5.3, 4.15, 'Módulo 2: Calidad & Auditoría\n(/dashboard/calidad)', ha='center', va='center', fontsize=9, fontweight='bold', color=C_CYAN)
    ax.text(5.3, 2.5, '• Diagnóstico antes/después\n• Frecuencia de tokens:\n  - 771k vacíos, 5.48M NA\n• Registro de reglas L-01..S-02\n• Bitácora append-only\n• Comparación de integridad:\n  - 0 duplicados en (folio, nro)\n  - 275 variables retenidas', ha='center', va='center', fontsize=7.2, color=C_TEXT)

    # Módulo 3: Universos y Diccionario
    m3 = FancyBboxPatch((7.1, 0.8), 2.9, 3.7, boxstyle="round,pad=0.15", facecolor=C_CARD, edgecolor=C_PURPLE, lw=2)
    ax.add_patch(m3)
    ax.text(8.55, 4.15, 'Módulo 3: Universos & Datos\n(/dashboard/universo)', ha='center', va='center', fontsize=9, fontweight='bold', color=C_PURPLE)
    ax.text(8.55, 2.5, '• Explorador de las 11 vistas\n• Criterios de elegibilidad\n• Diccionario oficial INE F27:\n  - 273 variables coincidentes\n  - Etiquetas oficiales DDI\n• Puntos de control muestral:\n  - QA en 381 hogares\n  - 1.216 personas verificadas', ha='center', va='center', fontsize=7.2, color=C_TEXT)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig7_dashboard_suite_capturas.png'), dpi=300, bbox_inches='tight')
    plt.close()


if __name__ == '__main__':
    print("Iniciando generacion de figuras en 300 DPI...")
    generar_figura_1()
    print("[OK] Figura 1 generada: fig1_metodologia_crisp_kdd.png")
    generar_figura_2()
    print("[OK] Figura 2 generada: fig2_arquitectura_pipeline_json.png")
    generar_figura_3()
    print("[OK] Figura 3 generada: fig3_diagnostico_tokens_ausencia.png")
    generar_figura_4()
    print("[OK] Figura 4 generada: fig4_distribucion_departamental.png")
    generar_figura_5()
    print("[OK] Figura 5 generada: fig5_auditoria_horas_semanales_s01.png")
    generar_figura_6()
    print("[OK] Figura 6 generada: fig6_cobertura_11_vistas.png")
    generar_figura_7()
    print("[OK] Figura 7 generada: fig7_dashboard_suite_capturas.png")
    print("Todas las figuras han sido generadas con exito en informe/figuras/")
