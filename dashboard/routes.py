"""
Flask Routes for ML Lab Dashboard.
Manages the Overview, Procedure/Methodology, and the 4 Survey Universes (Salud, Educación, Empleo, Ingresos).
"""
from flask import render_template, request, jsonify
from . import dashboard_bp
from .services.dataset_service import dataset_service
from .services.audit_service import audit_service


@dashboard_bp.route("/")
def index():
    """Main DM Lab Dashboard (Minería de Datos & 5 Universos)."""
    manifest = dataset_service.get_manifest()
    rules = dataset_service.get_cleaning_rules()
    return render_template(
        "dashboard/pages/index.html",
        active_page="index",
        manifest=manifest,
        rules=rules
    )


@dashboard_bp.route("/demografia")
def demografia():
    charts = dataset_service.get_demographic_charts()
    return render_template("dashboard/pages/demografia.html", active_page="demografia", charts=charts)


@dashboard_bp.route("/revision-pendiente")
def revision_pendiente():
    summary = dataset_service.get_review_summary()
    return render_template("dashboard/pages/revision_pendiente.html", active_page="revision-pendiente", summary=summary)



@dashboard_bp.route("/procedimiento")
def procedimiento():
    """Detailed Data Cleaning Procedure & Methodology page."""
    return render_template(
        "dashboard/pages/procedimiento.html",
        active_page="procedimiento"
    )


@dashboard_bp.route("/region")
def region():
    """Regional Geographic Distribution & Universe Mapping across 9 Departments of Bolivia."""
    region_data = dataset_service.get_regional_distribution()
    return render_template(
        "dashboard/pages/region.html",
        active_page="region",
        region_data=region_data
    )



@dashboard_bp.route("/salud")
def salud():
    """Universo 1: Salud, Cobertura y Atención Médica (Sección s02)."""
    universe_data = dataset_service.get_universe_data("salud")
    universe_data["charts"] = dataset_service.get_universe_charts("salud")
    return render_template(
        "dashboard/pages/universo.html",
        active_page="salud",
        universe=universe_data
    )


@dashboard_bp.route("/educacion")
def educacion():
    """Universo 2: Educación, Asistencia y Años de Estudio (Sección s03)."""
    universe_data = dataset_service.get_universe_data("educacion")
    universe_data["charts"] = dataset_service.get_universe_charts("educacion")
    return render_template(
        "dashboard/pages/universo.html",
        active_page="educacion",
        universe=universe_data
    )


@dashboard_bp.route("/empleo")
def empleo():
    """Universo 3: Empleo, Mercado Laboral y Ocupación (Sección s04)."""
    universe_data = dataset_service.get_universe_data("empleo")
    universe_data["charts"] = dataset_service.get_universe_charts("empleo")
    return render_template(
        "dashboard/pages/universo.html",
        active_page="empleo",
        universe=universe_data
    )


@dashboard_bp.route("/ingresos")
def ingresos():
    """Universo 4: Ingresos Laborales, No Laborales y Pobreza (Sección s05)."""
    universe_data = dataset_service.get_universe_data("ingresos")
    universe_data["charts"] = dataset_service.get_universe_charts("ingresos")
    return render_template(
        "dashboard/pages/universo.html",
        active_page="ingresos",
        universe=universe_data
    )


@dashboard_bp.route("/exploracion")
def exploracion():
    """Diccionario y Explorador de las 275 variables del Dataset Master."""
    variables = dataset_service.get_all_variables()
    return render_template(
        "dashboard/pages/exploracion.html",
        active_page="exploracion",
        variables=variables
    )


@dashboard_bp.route("/api/simular", methods=["POST"])
def api_simular():
    """API endpoint to log an inference test event to JSON audit log."""
    data = request.get_json() or {}
    event = audit_service.log_event(
        actor="web_user",
        action="INFERENCE_SIMULATION",
        entity="cardio_ensemble_model",
        # Keep arbitrary request values (which may contain microdata) out of logs.
        details={"status": "requested"}
    )
    return jsonify({"status": "ok", "event": event})
