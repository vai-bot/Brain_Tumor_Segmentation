from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from tensorflow.keras.models import load_model

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from design import empty_state, end_shell, glass_intro, hero_section, inject_global_styles, sidebar_profile, start_shell
from utils.analysis import load_study, run_segmentation, summarize_analysis
from utils.classification import get_classifier_model, classify_tumor_type
from utils.database import (
    DatabaseIntegrityError,
    authenticate_user,
    get_database_backend,
    init_db,
    load_patient_history,
    register_user,
    save_patient_record,
)


MODEL_PATH = ROOT_DIR / "model" / "unet_model.h5"
ASSET_DIR = Path(__file__).resolve().parent

st.set_page_config(page_title="NeuroScan AI | Doctor MRI Console", layout="wide")
inject_global_styles()


@st.cache_resource
def get_model():
    try:
        return load_model(MODEL_PATH)
    except Exception:
        return None


def make_hashes(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def check_hashes(password: str, hashed_text: str) -> bool:
    return make_hashes(password) == hashed_text


def build_overlay(slice_image: np.ndarray, mask_slice: np.ndarray) -> np.ndarray:
    normalized = (slice_image * 255).astype(np.uint8)
    image_bgr = cv2.cvtColor(normalized, cv2.COLOR_GRAY2BGR)
    red_layer = np.zeros_like(image_bgr)
    red_layer[:, :, 2] = (mask_slice * 255).astype(np.uint8)
    return cv2.addWeighted(image_bgr, 0.82, red_layer, 0.46, 0)


def build_3d_figure(volume: np.ndarray, mask_volume: np.ndarray) -> go.Figure:
    brain_points = np.argwhere(volume > max(float(np.percentile(volume, 55)), 0.18))
    tumor_points = np.argwhere(mask_volume > 0)

    if len(brain_points) > 5000:
        brain_points = brain_points[np.linspace(0, len(brain_points) - 1, 5000, dtype=int)]
    if len(tumor_points) > 4000:
        tumor_points = tumor_points[np.linspace(0, len(tumor_points) - 1, 4000, dtype=int)]

    figure = go.Figure()

    if len(brain_points) > 0:
        figure.add_trace(
            go.Scatter3d(
                x=brain_points[:, 2],
                y=brain_points[:, 1],
                z=brain_points[:, 0],
                mode="markers",
                marker={"size": 2.6, "color": "rgba(103, 232, 249, 0.16)"},
                name="Brain tissue",
            )
        )

    if len(tumor_points) > 0:
        figure.add_trace(
            go.Scatter3d(
                x=tumor_points[:, 2],
                y=tumor_points[:, 1],
                z=tumor_points[:, 0],
                mode="markers",
                marker={"size": 3.8, "color": "rgba(251, 113, 133, 0.88)"},
                name="Predicted tumor",
            )
        )

    figure.update_layout(
        height=560,
        margin={"l": 0, "r": 0, "t": 16, "b": 0},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        scene={
            "bgcolor": "rgba(0,0,0,0)",
            "xaxis": {"title": "X", "backgroundcolor": "rgba(0,0,0,0)", "gridcolor": "rgba(148,163,184,0.15)"},
            "yaxis": {"title": "Y", "backgroundcolor": "rgba(0,0,0,0)", "gridcolor": "rgba(148,163,184,0.15)"},
            "zaxis": {"title": "Slice", "backgroundcolor": "rgba(0,0,0,0)", "gridcolor": "rgba(148,163,184,0.15)"},
            "camera": {"eye": {"x": 1.45, "y": 1.45, "z": 0.9}},
        },
        legend={"orientation": "h", "y": 1.02, "x": 0},
    )
    return figure


def build_report(patient_name: str, patient_age: int, doctor: str, study_type: str, summary: dict) -> tuple[str, str]:
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_payload = {
        "patient_name": patient_name,
        "patient_age": patient_age,
        "doctor": doctor,
        "generated_at": generated_at,
        "study_type": study_type,
        "tumor_detected": summary["detected"],
        "affected_percent": round(summary["affected_percent"], 3),
        "tumor_level": summary["tumor_level"],
        "tumor_type": summary["tumor_type"],
        "tumor_type_source": summary["tumor_type_source"],
        "tumor_type_confidence": round(summary["tumor_type_confidence"], 2),
        "tumor_pattern": summary["tumor_pattern"],
        "estimated_region": summary["estimated_region"],
        "positive_slice_count": summary["positive_slice_count"],
        "total_slice_count": summary["total_slice_count"],
        "confidence_percent": round(summary["confidence_percent"], 2),
        "affected_volume_mm3": None if summary["affected_volume_mm3"] is None else round(summary["affected_volume_mm3"], 3),
    }

    report_text = f"""
NeuroScan AI Clinical Summary
Generated: {generated_at}
Doctor: {doctor}
Patient: {patient_name}
Age: {patient_age}
Study type: {study_type}

Tumor detected: {"Yes" if summary["detected"] else "No"}
Affected brain percentage: {summary["affected_percent"]:.2f}%
Tumor burden level: {summary["tumor_level"]}
Tumor type: {summary["tumor_type"]}
Tumor type source: {summary["tumor_type_source"]}
Tumor type confidence: {summary["tumor_type_confidence"]:.2f}%
Tumor pattern: {summary["tumor_pattern"]}
Estimated affected region: {summary["estimated_region"]}
Slices with tumor: {summary["positive_slice_count"]}/{summary["total_slice_count"]}
Model confidence signal: {summary["confidence_percent"]:.2f}%
Affected volume (mm^3): {"N/A" if summary["affected_volume_mm3"] is None else f"{summary['affected_volume_mm3']:.2f}"}

Clinical note:
Tumor classification utilizes deep-learning models when available. In fallback mode, the system provides a morphological estimation. Final diagnosis must be verified by the attending radiologist.
""".strip()

    return report_text, json.dumps(report_payload, indent=2)


def render_result_summary(summary: dict) -> None:
    status_class = "detected" if summary["detected"] else "clear"
    st.markdown(
        f"""
        <div class='status-board'>
            <div class='status-pill {status_class}'>Tumor status: {"Detected" if summary["detected"] else "Not detected"}</div>
            <div class='status-pill neutral'>Type engine: {summary["tumor_type_source"]}</div>
            <div class='status-pill neutral'>Typing confidence: {summary["tumor_type_confidence"]:.1f}%</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div class='metric-ribbon'>", unsafe_allow_html=True)
    primary_metrics = st.columns(5)
    primary_metrics[0].metric("Tumor detected", "Yes" if summary["detected"] else "No")
    primary_metrics[1].metric("Affected brain", f"{summary['affected_percent']:.2f}%")
    primary_metrics[2].metric("Tumor level", summary["tumor_level"])
    primary_metrics[3].metric("Affected part", summary["estimated_region"])
    primary_metrics[4].metric("Positive slices", f"{summary['positive_slice_count']}/{summary['total_slice_count']}")
    st.markdown("</div>", unsafe_allow_html=True)

    secondary_metrics = st.columns(4)
    secondary_metrics[0].metric("Tumor type", summary["tumor_type"])
    secondary_metrics[1].metric("Type confidence", f"{summary['tumor_type_confidence']:.1f}%")
    secondary_metrics[2].metric("Model signal", f"{summary['confidence_percent']:.1f}%")
    secondary_metrics[3].metric(
        "Affected volume",
        "N/A" if summary["affected_volume_mm3"] is None else f"{summary['affected_volume_mm3']:.1f} mm^3",
    )


def render_result_tabs(patient_name: str, patient_age: int, segmentation: dict, summary: dict) -> None:
    peak_index = summary["peak_slice_index"]

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-label'>Automated review output</div>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'>MRI analysis workspace</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='card-copy'>Scroll through 2D slices interactively, inspect the reconstructed 3D tumor map, and export a doctor-ready report from one place.</div>",
        unsafe_allow_html=True,
    )

    render_result_summary(summary)

    tab_overview, tab_visuals, tab_report = st.tabs(["Case summary", "Visual review", "Export"])

    with tab_overview:
        info_left, info_right = st.columns([1.2, 1])
        with info_left:
            glass_intro(
                "Patient context",
                f"{patient_name}, age {patient_age}",
                f"Study type: {segmentation['study_type']}. Source: {segmentation['source_name']}. Positive slices: {summary['positive_slice_count']} of {summary['total_slice_count']}.",
            )
        with info_right:
            glass_intro(
                "Tumor classification",
                summary["tumor_type"],
                f"Source: {summary['tumor_type_source']}. Tumor pattern: {summary['tumor_pattern']}. Estimated affected region: {summary['estimated_region']}.",
            )

    with tab_visuals:
        st.markdown("<div class='card-title' style='margin-top: 1rem;'>Interactive 2D Slice Viewer</div>", unsafe_allow_html=True)
        total_slices = len(segmentation["volume"])
        
        if total_slices > 1:
            selected_slice_idx = st.slider(
                "Scroll through MRI slices", 
                min_value=1, 
                max_value=total_slices, 
                value=peak_index + 1,
                help="Move the slider to explore the brain volume slice by slice."
            ) - 1
        else:
            selected_slice_idx = 0
            st.info("Single image uploaded. Interactive scroller is active for multi-slice volumes.")
        
        preview_slice = segmentation["volume"][selected_slice_idx]
        preview_mask = segmentation["masks"][selected_slice_idx]
        overlay = build_overlay(preview_slice, preview_mask)

        image_col, overlay_col = st.columns(2)
        image_col.image((preview_slice * 255).astype(np.uint8), caption=f"Slice #{selected_slice_idx + 1}", use_container_width=True)
        overlay_col.image(overlay, caption="Predicted tumor overlay", use_container_width=True)
        
        st.markdown("<div class='card-title' style='margin-top: 2.5rem;'>3D Volumetric Review</div>", unsafe_allow_html=True)
        st.plotly_chart(build_3d_figure(segmentation["volume"], segmentation["masks"]), use_container_width=True)
        st.caption("For optimal 3D rendering and volumetric accuracy, a complete NIfTI study or sequential MRI slice directory is recommended.")
        st.markdown(
            f"""
            <div class='insight-strip'>
                <div><span>Pattern</span><strong>{summary["tumor_pattern"]}</strong></div>
                <div><span>Region</span><strong>{summary["estimated_region"]}</strong></div>
                <div><span>Typing source</span><strong>{summary["tumor_type_source"]}</strong></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with tab_report:
        report_text, report_json = build_report(
            patient_name=patient_name,
            patient_age=patient_age,
            doctor=st.session_state.username,
            study_type=segmentation["study_type"],
            summary=summary,
        )
        st.code(report_text, language="text")
        download_left, download_right = st.columns(2)
        download_left.download_button(
            "Download report (.txt)",
            report_text,
            file_name=f"{patient_name.replace(' ', '_')}_clinical_report.txt",
            use_container_width=True,
        )
        download_right.download_button(
            "Download report data (.json)",
            report_json,
            file_name=f"{patient_name.replace(' ', '_')}_clinical_report.json",
            mime="application/json",
            use_container_width=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


def about_section():
    start_shell()
    hero_section(
        eyebrow="Clinical Efficacy",
        title="NeuroScan AI Specifications",
        subtitle="Advanced AI-driven clinical decision support. Secure, high-resolution 3D MRI segmentation and automated pathology classification for rapid diagnostic review.",
        features=[
            {"kicker": "Ingestion", "title": "Multi-Modal Support", "copy": "Supports standardized NIfTI volumes, ZIP archives, and sequential MRI slices."},
            {"kicker": "Output", "title": "Diagnostic Findings", "copy": "Review volumetric tumor burden, regional estimates, and structural report data."},
            {"kicker": "Archive", "title": "Secure Patient History", "copy": "Encrypted, longitudinal tracking of patient scans and diagnostic history."},
        ],
    )

    left, right = st.columns([1.05, 1.15])
    with left:
        process_path = ASSET_DIR / "process_animation.gif"
        if process_path.exists():
            st.image(str(process_path), caption="Automated 3D segmentation workflow", use_container_width=True)
        else:
            glass_intro("Workflow", "Animated process preview unavailable", "The asset is missing, but the analysis pipeline remains available.")

    with right:
        glass_intro(
            "System Overview",
            "Clinical Decision Support",
            "Secure physician access, automated multi-slice volumetric analysis, neoplastic burden calculation, tumor-type prediction, and interactive 3D spatial rendering.",
        )
        glass_intro(
            "AI Classification",
            "Deep Learning & Morphological Estimation",
            "Utilizes a dedicated convolutional neural network (CNN) for pathological classification. In the absence of the model, the system employs morphological heuristics for preliminary estimation.",
        )
        glass_intro(
            "Optimal Modality",
            "Volumetric Scans Recommended",
            "For highest spatial fidelity, NIfTI volumes or sequential slice sequences are strongly recommended. Single-slice ingestion provides limited spatial depth.",
        )
    end_shell()


def login_page():
    start_shell()
    left, right = st.columns([1.4, 1])
    with left:
        hero_section(
            eyebrow="Clinical Portal",
            title="Neuro-Oncology Diagnostics",
            subtitle="Advanced AI-driven clinical decision support for neuro-oncology. Secure, high-resolution 3D MRI segmentation and automated tumor classification for rapid review.",
            features=[
                {"kicker": "Ingest", "title": "Multi-Modal Support", "copy": "Supports standardized NIfTI volumes, DICOM-compliant ZIPs, and slice sequences."},
                {"kicker": "Classify", "title": "AI Tumor Typing", "copy": "Automated morphological tumor typing with explicit confidence intervals."},
                {"kicker": "Archive", "title": "Secure Tracking", "copy": "Secure, longitudinal tracking of patient scans and diagnostic history."},
            ],
        )

        hero_path = ASSET_DIR / "hero_animation.gif"
        if hero_path.exists():
            st.image(str(hero_path), use_container_width=True)

    with right:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-label'>Secure access</div>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Access portal</div>", unsafe_allow_html=True)
        st.markdown("<div class='card-copy'>Sign in as a doctor or register a new account to enter the MRI review console.</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='db-badge'>Active storage backend: <strong>{get_database_backend()}</strong></div>",
            unsafe_allow_html=True,
        )

        choice = st.radio("Select Action", ["Login", "Register"], label_visibility="collapsed")
        username = st.text_input("Doctor ID", placeholder="Enter your doctor ID")
        password = st.text_input("Access Key", type="password", placeholder="Enter your password")

        if choice == "Register":
            if st.button("Create account", use_container_width=True):
                try:
                    register_user(username, make_hashes(password))
                    st.success("Account created. Please sign in.")
                except DatabaseIntegrityError:
                    st.error("This doctor ID is already registered.")
        else:
            if st.button("Open dashboard", use_container_width=True):
                password_hash = authenticate_user(username)

                if password_hash and check_hashes(password, password_hash):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Invalid doctor ID or password.")

        st.markdown("</div>", unsafe_allow_html=True)
    end_shell()


def render_dashboard_intake():
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-label'>Patient intake</div>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'>Run fully automated MRI analysis</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='card-copy'>Upload a complete NIfTI study or sequential MRI slice directory. The AI engine will segment neoplastic tissue, calculate volumetric brain involvement, predict pathological tumor type, and render an interactive 3D spatial review.</div>",
        unsafe_allow_html=True,
    )

    with st.form("intake"):
        patient_col, age_col = st.columns(2)
        patient_name = patient_col.text_input("Patient name")
        patient_age = age_col.number_input("Patient age", min_value=1, max_value=120, value=35)
        uploads = st.file_uploader(
            "Upload MRI image, slice set, ZIP study, or .nii/.nii.gz volume",
            type=["png", "jpg", "jpeg", "zip", "nii", "gz"],
            accept_multiple_files=True,
            help="For a folder-style upload, select multiple ordered image slices or provide a ZIP archive.",
        )
        submitted = st.form_submit_button("Run automated analysis", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    return patient_name, patient_age, uploads, submitted


def render_dashboard_guidance():
    glass_intro(
        "Optimal Modality",
        "Volumetric Scans Recommended",
        "For accurate 3D reconstruction and volumetric measurement, upload a complete NIfTI study or sequential MRI slice directory. Single-slice ingestion provides limited spatial depth.",
    )
    glass_intro(
        "Diagnostic Outputs",
        "Automated Pathology Metrics",
        "Volumetric brain involvement, neoplastic burden level, morphological tumor type, confidence intervals, affected regional mapping, and downloadable clinical reports.",
    )
    glass_intro(
        "Data Security",
        "Encrypted Patient Archive",
        "Patient records and segmentation data are stored securely. Configure production database environment variables for enterprise-scale clinical deployments.",
    )


def dashboard_page():
    start_shell()
    hero_section(
        eyebrow="Clinical Workspace",
        title="Diagnostic Dashboard",
        subtitle="AI-Assisted Diagnostic Workspace. Upload patient MRI volumes to generate automated 3D segmentations, volumetric burden analysis, and structured clinical reports.",
        features=[
            {"kicker": "Segmentation", "title": "Automated Inference", "copy": "Execute volumetric segmentation across comprehensive MRI studies."},
            {"kicker": "Classification", "title": "Pathology Prediction", "copy": "Deep-learning driven tumor classification with morphological heuristic fallbacks."},
            {"kicker": "Visualization", "title": "Spatial Review", "copy": "Examine neoplastic tissue via an interactive 3D rendering surface."},
        ],
    )

    intake_col, help_col = st.columns([1.4, 0.9])
    with intake_col:
        patient_name, patient_age, uploads, submitted = render_dashboard_intake()
    with help_col:
        render_dashboard_guidance()

    current_case = st.session_state.get("current_case")

    if submitted:
        if not patient_name.strip():
            st.error("Please enter the patient name.")
            end_shell()
            return
        if not uploads:
            st.error("Please upload at least one MRI file.")
            end_shell()
            return

        model = get_model()
        classifier_model = get_classifier_model()
        with st.spinner("Running segmentation, tumor burden estimation, and 3D reconstruction..."):
            try:
                study = load_study(list(uploads))
                segmentation = run_segmentation(study, model=model)
                summary = summarize_analysis(segmentation)
                summary.update(classify_tumor_type(segmentation, summary, classifier_model=classifier_model))
            except Exception as error:
                st.error(f"Analysis failed: {error}")
                end_shell()
                return

        report_text, report_json = build_report(
            patient_name=patient_name,
            patient_age=patient_age,
            doctor=st.session_state.username,
            study_type=segmentation["study_type"],
            summary=summary,
        )
        save_patient_record(
            st.session_state.username,
            patient_name,
            patient_age,
            segmentation["study_type"],
            summary,
            report_json,
            datetime.now().strftime("%Y-%m-%d"),
        )
        st.session_state.current_case = {
            "patient_name": patient_name,
            "patient_age": int(patient_age),
            "segmentation": segmentation,
            "summary": summary,
            "saved_at": datetime.now().isoformat(),
        }
        current_case = st.session_state.current_case

    if current_case:
        render_result_tabs(
            current_case["patient_name"],
            current_case["patient_age"],
            current_case["segmentation"],
            current_case["summary"],
        )
    else:
        empty_state("No case loaded yet", "Start with a patient name and MRI upload to generate automated findings and a 3D review panel.")

    end_shell()


def history_page():
    start_shell()
    hero_section(
        eyebrow="Encrypted Archive",
        title="Patient Diagnostic History",
        subtitle="Review longitudinal MRI studies, monitor neoplastic progression across visits, and access stored pathological classifications.",
        features=[
            {"kicker": "Secure", "title": "Clinical Records", "copy": "Encrypted storage of all diagnostic studies associated with your physician ID."},
            {"kicker": "Continuity", "title": "Longitudinal Tracking", "copy": "Monitor changes in volumetric tumor burden, region, and morphology over time."},
            {"kicker": "Export", "title": "Structured Data", "copy": "Comprehensive metadata including scan modality, burden percentage, and confidence scoring."},
        ],
    )

    data_frame = load_patient_history(st.session_state.username)

    if data_frame.empty:
        empty_state("No patient studies saved yet", "Run at least one MRI analysis from the dashboard and it will appear here.")
    else:
        summary_cols = st.columns(4)
        summary_cols[0].metric("Cases", int(len(data_frame)))
        summary_cols[1].metric("Avg affected %", f"{data_frame['tumor_pct'].mean():.2f}%")
        summary_cols[2].metric("Latest study", str(data_frame['date'].iloc[0]))
        summary_cols[3].metric("High burden cases", int((data_frame["stage"].isin(["High", "Critical"])).sum()))

        st.markdown("<div class='history-shell'>", unsafe_allow_html=True)
        st.dataframe(data_frame, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    end_shell()


def main_app():
    with st.sidebar:
        sidebar_profile(st.session_state.username)
        st.caption(f"Storage backend: {get_database_backend()}")
        menu = st.radio("Menu", ["Dashboard", "Patient History", "About System"])
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    if menu == "Dashboard":
        dashboard_page()
    elif menu == "Patient History":
        history_page()
    else:
        about_section()


init_db()
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_page()
else:
    main_app()
