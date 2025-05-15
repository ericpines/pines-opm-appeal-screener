# Streamlit App: FERS Disability Screener + Appeal Strategist
import streamlit as st
import datetime
from PyPDF2 import PdfReader

# --- UI CONFIG ---
st.set_page_config(page_title="FERS Screener + Appeal Strategist", layout="wide")
st.title("🧠 FERS Disability Screener + Appeal Strategist")

# --- SESSION STATE ---
if "parsed_denial" not in st.session_state:
    st.session_state.parsed_denial = ""
if "denial_reasons" not in st.session_state:
    st.session_state.denial_reasons = []
if "quoted_lines" not in st.session_state:
    st.session_state.quoted_lines = []

# --- SECTION: Upload Center ---
st.header("1️⃣ Upload Case Files")
uploaded_denial = st.file_uploader("Upload OPM/MSPB Denial Letter (PDF only)", type=["pdf"])
separation_date = st.date_input("Separation Date")
denial_date = st.date_input("Denial Letter Date")

if uploaded_denial:
    reader = PdfReader(uploaded_denial)
    text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    st.session_state.parsed_denial = text
    st.success("Denial letter parsed successfully.")
    if st.checkbox("Preview Denial Text"):
        st.text_area("Denial Letter Content", text, height=300)

# --- SECTION: Screener ---
st.header("2️⃣ FERS Eligibility Screener")
col1, col2 = st.columns(2)
with col1:
    service_years = st.selectbox("At least 18 months of creditable FERS service?", ["Yes", "No"])
    long_term_disability = st.selectbox("Condition expected to last at least one year?", ["Yes", "No"])
    ssdi_applied = st.selectbox("Applied for Social Security Disability?", ["Yes", "No"])
with col2:
    agency_accommodated = st.selectbox("Did agency offer accommodation or reassignment?", ["No", "Yes", "Unclear"])
    medical_condition = st.text_input("Brief description of disabling condition")

if st.button("🧮 Analyze Eligibility"):
    eligible = (service_years == "Yes" and long_term_disability == "Yes" and ssdi_applied == "Yes")
    if eligible:
        st.success("✅ Likely Eligible for FERS Disability Retirement")
    else:
        st.warning("⚠️ One or more eligibility criteria may be missing. Review carefully.")
    if agency_accommodated == "Yes":
        st.info("📝 Consider rebutting the reassignment/accommodation as unreasonable.")

# --- SECTION: Denial Letter Parser ---
st.header("3️⃣ Denial Letter Analyzer")
if st.session_state.parsed_denial:
    if st.button("🔍 Analyze Denial Letter"):
        text = st.session_state.parsed_denial.lower()
        lines = st.session_state.parsed_denial.splitlines()
        reasons = []
        quotes = []

        for line in lines:
            l = line.lower()
            if "not disabled" in l or "does not demonstrate" in l:
                reasons.append("Medical not proven disabling")
                quotes.append(line.strip())
            if "reassignment" in l or "position available" in l:
                reasons.append("Agency claims reassignment was possible")
                quotes.append(line.strip())
            if "ssdi" in l:
                reasons.append("SSDI application issue")
                quotes.append(line.strip())
            if "not timely" in l or "deadline" in l:
                reasons.append("Filing deadline problem")
                quotes.append(line.strip())

        st.session_state.denial_reasons = reasons
        st.session_state.quoted_lines = quotes

        if reasons:
            st.subheader("🛑 Reasons for Denial Detected:")
            for r, q in zip(reasons, quotes):
                st.markdown(f"- ❗ **{r}**")
                st.markdown(f"> 📄 *Quoted from denial:*")
                st.code(q)
            st.success("See next section for legal reasoning and strategy.")
        else:
            st.info("✅ No standard denial language detected — manual review suggested.")
else:
    st.info("📤 Upload a denial letter to enable parsing.")

# --- SECTION: Legal Strategy Recommendations ---
st.header("4️⃣ Legal Strategy & Next Steps")
if st.session_state.denial_reasons:
    for reason, quote in zip(st.session_state.denial_reasons, st.session_state.quoted_lines):
        st.markdown(f"### ❗ Denial Reason: {reason}")
        st.markdown(f"> 📄 *From denial letter:* \n\n{quote}")

        if reason == "Medical not proven disabling":
            st.markdown("**Legal Basis:** Under *Confer v. OPM*, the MSPB held that subjective accounts of disability supported by credible medical records can establish FERS disability. The ADA Amendments Act also broadens disability definitions.")
            st.markdown("**What You Need:** A physician letter describing specific job-related limitations (e.g., inability to perform duties like lifting, driving, standing). Include a functional capacity evaluation if possible. State clearly that the condition prevents useful and efficient service.")

        elif reason == "Agency claims reassignment was possible":
            st.markdown("**Legal Basis:** In *Confer*, the MSPB vacated a denial where the reassignment was not proven feasible given the medical limitations. Reassignments must match qualifications and limitations.")
            st.markdown("**What You Need:** Documentation of what role was offered, why it was not viable (from physician), and absence of a real job match within the commuting area. Attach medical justification rejecting the reassignment.")

        elif reason == "SSDI application issue":
            st.markdown("**Legal Basis:** 5 C.F.R. § 844.201 requires applying for SSDI, but does not require approval. Filing confirms intent and satisfies eligibility criteria.")
            st.markdown("**What You Need:** Submit proof of SSDI filing. If not yet filed, submit it now and notify OPM. Link SSA findings to your FERS appeal where possible.")

        elif reason == "Filing deadline problem":
            st.markdown("**Legal Basis:** 5 C.F.R. § 844.202(d) allows extension of the 1-year post-separation deadline if the applicant was mentally incompetent at the time or shortly thereafter.")
            st.markdown("**What You Need:** Prepare a statement of good cause. If mental health issues delayed action, get medical corroboration. For MSPB appeals, submit with a motion to waive timeliness.")

        st.markdown("---")

    # --- Final Evaluation for Intake Decision ---
    st.header("5️⃣ Case Intake Recommendation")
    st.markdown("**📋 Internal Review Summary for OPM Intake Team:**")

    if "Medical not proven disabling" in st.session_state.denial_reasons or "Agency claims reassignment was possible" in st.session_state.denial_reasons:
        st.markdown("✅ **This case may be viable if we can strengthen the medical evidence and rebut reassignment viability.**")
        st.markdown("👉 Recommend intake if client can obtain:\n\n- A treating physician’s letter detailing why they cannot perform their job duties\n- Documentation disproving reassignment feasibility\n- SSDI proof of filing (if missing)")
    elif "SSDI application issue" in st.session_state.denial_reasons and len(st.session_state.denial_reasons) == 1:
        st.markdown("⚠️ **Weak denial reason. Likely reversible if SSDI proof is provided promptly. Recommend intake.**")
    elif "Filing deadline problem" in st.session_state.denial_reasons:
        st.markdown("🟡 **Case depends on mental competency evidence or procedural justification. Recommend conditional intake if justification is credible.**")
    else:
        st.markdown("❌ **Do not intake unless additional evidence or medical documentation becomes available.**")