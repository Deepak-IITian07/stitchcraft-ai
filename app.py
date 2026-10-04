import datetime
import json
import random
import re
import requests
import streamlit as st
import streamlit.components.v1 as components


# Load external boutique CSS
def load_css(file_name: str = "style.css"):
    with open(file_name, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("style.css")

# Optional ollama import with graceful fallback to raw HTTP requests
try:
    import ollama
    OLLAMA_PKG_AVAILABLE = True
except ImportError:
    OLLAMA_PKG_AVAILABLE = False


# ==============================================================================
# Page Configuration & CSS
# ==============================================================================
st.set_page_config(
    page_title="AI Tailor Job Ticket Generator",
    page_icon="✂️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling (App view + Strict Print View)
st.markdown(
    """
    <style>
    /* Clean application styling */
    .stTextArea textarea {
        font-family: monospace;
        font-size: 0.95rem;
    }
    
    /* Print Specific Styles */
    @media print {
        /* Hide all Streamlit UI components when printing */
        header, footer, [data-testid="stSidebar"], [data-testid="stToolbar"],
        .stButton, .no-print, [data-testid="stFileUploader"] {
            display: none !important;
        }

        body, .main, [data-testid="stAppViewContainer"] {
            background-color: #ffffff !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        .job-card {
            border: 2px solid #222 !important;
            box-shadow: none !important;
            width: 100% !important;
            margin: 0 auto !important;
            page-break-inside: avoid;
        }
    }

    /* Job Card Styling */
    .job-card {
        background-color: #ffffff;
        color: #1a1a1a;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        margin-top: 15px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        border-bottom: 2px solid #1e293b;
        padding-bottom: 12px;
        margin-bottom: 16px;
    }

    .shop-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #0f172a;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .shop-subtitle {
        font-size: 0.85rem;
        color: #64748b;
        margin-top: 2px;
    }

    .job-meta {
        text-align: right;
    }

    .job-id {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1e293b;
        font-family: monospace;
    }

    .badge {
        display: inline-block;
        padding: 3px 8px;
        font-size: 0.75rem;
        font-weight: 700;
        border-radius: 9999px;
        text-transform: uppercase;
        margin-top: 4px;
    }
    .badge-urgent { background-color: #fee2e2; color: #dc2626; border: 1px solid #f87171; }
    .badge-express { background-color: #fef3c7; color: #d97706; border: 1px solid #fbbf24; }
    .badge-normal { background-color: #ecfdf5; color: #059669; border: 1px solid #6ee7b7; }

    .client-info-strip {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 10px 14px;
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: 10px;
        margin-bottom: 18px;
    }

    .client-item-label {
        font-size: 0.75rem;
        color: #64748b;
        text-transform: uppercase;
        font-weight: 600;
    }
    .client-item-value {
        font-size: 0.95rem;
        font-weight: 600;
        color: #0f172a;
    }

    .measurements-container {
        margin-bottom: 18px;
    }

    .section-title {
        font-size: 0.88rem;
        font-weight: 700;
        text-transform: uppercase;
        color: #334155;
        letter-spacing: 0.5px;
        border-bottom: 1px solid #cbd5e1;
        padding-bottom: 4px;
        margin-bottom: 10px;
    }

    .measurements-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
        gap: 8px;
    }

    .meas-box {
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        padding: 8px;
        background-color: #ffffff;
    }
    .meas-box.empty {
        background-color: #f8fafc;
        border-color: #e2e8f0;
        opacity: 0.55;
    }
    .meas-label {
        font-size: 0.72rem;
        color: #64748b;
        text-transform: uppercase;
        font-weight: 600;
        margin-bottom: 2px;
    }
    .meas-val {
        font-size: 1.05rem;
        font-weight: 700;
        color: #0f172a;
    }

    .details-grid {
        display: grid;
        grid-template-columns: 2fr 1fr;
        gap: 16px;
        margin-top: 14px;
    }

    .instruction-list {
        margin: 4px 0;
        padding-left: 18px;
        color: #334155;
        font-size: 0.88rem;
    }

    .financials-box {
        background-color: #f1f5f9;
        border-radius: 8px;
        padding: 12px;
        border: 1px solid #cbd5e1;
    }

    .fin-row {
        display: flex;
        justify-content: space-between;
        font-size: 0.88rem;
        margin-bottom: 4px;
    }
    .fin-row.total {
        border-top: 1px dashed #94a3b8;
        padding-top: 6px;
        margin-top: 6px;
        font-weight: 800;
        font-size: 1rem;
        color: #0f172a;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
# Sample WhatsApp Data
# ==============================================================================
EXAMPLE_MESSAGES = [
    (
        "Bhaiya stitch an anarkali kurti for Sunita Sharma (9876543210), chest 38, waist 34, "
        "hips 40, length 42, 3/4 sleeves (16 inch), deep neck back with tassels and latkan. "
        "Customer provided royal blue silk fabric. Needs by this Thursday urgent for wedding. "
        "Advance paid 500 total agreed 1400."
    ),
    (
        "Urgent blouse request from Pooja: Bust 36, Waist 30, front neck 7 inch, back boat neck 9 inch, "
        "elbow length sleeve 11, sleeve round 12. Padding needed. Fabric is gold brocade given by her. "
        "Delivery Friday evening express. Advance 300, total stitching 850."
    ),
    (
        "Stitch 2 formal trousers for Mr. Rajesh. Waist 34, length 40, inseam 30, bottom 15, hips 39. "
        "Cross pockets, slim fit cut. Standard delivery by next week. Advance 0, est 1200 balance."
    ),
]


# ==============================================================================
# Helper Functions: JSON Extraction & LLM Calls
# ==============================================================================
PROMPT_SCHEMA = """{
  "customer_name": "String or 'Walk-in / Unspecified'",
  "phone_number": "String or 'Not provided'",
  "garment_type": "e.g., Kurti, Blouse, Trousers, Suit, etc.",
  "measurements": {
    "Chest / Bust": "Value with unit or 'Not specified'",
    "Waist": "Value with unit or 'Not specified'",
    "Hips": "Value with unit or 'Not specified'",
    "Length": "Value with unit or 'Not specified'",
    "Sleeve Length": "Value with unit or 'Not specified'",
    "Shoulder": "Value with unit or 'Not specified'",
    "Neck (Front/Back)": "Value with unit or 'Not specified'",
    "Bottom / Inseam": "Value with unit or 'Not specified'"
  },
  "additional_measurements": [
    {"label": "Name of any custom measurement mentioned", "value": "Value"}
  ],
  "delivery_date": "Extracted or inferred deadline (or 'Standard turnaround')",
  "urgency": "Normal | Urgent | Express",
  "fabric_details": "Customer provided, shop material, color, lining requirements, etc.",
  "design_instructions": ["List of specific design requests like neck design, latkan/tassels, slits, pockets"],
  "pricing": {
    "estimated_cost": "Extracted or 'TBD'",
    "advance_paid": "Extracted or '0'",
    "balance_due": "Calculated or 'TBD'"
  }
}"""

SYSTEM_PROMPT = f"""You are an expert tailor shop assistant and data parser.
Convert rough customer messages/notes into a strictly formatted JSON job card.

Rules:
1. Output strictly valid raw JSON only.
2. Do not include markdown codeblocks (no ```json or ```).
3. Do not include conversational filler, notes, or explanations.
4. Normalize units (inches, cm) when present.
5. If calculations are straightforward, deduce balance_due = estimated_cost - advance_paid.

JSON Output Schema:
{PROMPT_SCHEMA}
"""


def extract_json(raw_text: str) -> dict:
    """Robustly cleans and parses JSON from raw LLM output."""
    cleaned = raw_text.strip()
    
    # Strip markdown backticks if present
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()

    # If extra conversational text exists, isolate the main JSON object
    match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(1)

    return json.loads(cleaned)


def call_ollama(text: str, model_name: str, host: str = "http://localhost:11434") -> str:
    """Invokes local Ollama instance via HTTP endpoint or package."""
    endpoint = f"{host.rstrip('/')}/api/generate"
    payload = {
        "model": model_name,
        "prompt": f"{SYSTEM_PROMPT}\n\nCustomer Message to parse:\n\"\"\"{text}\"\"\"",
        "stream": False,
        "options": {
            "temperature": 0.1,
            "top_p": 0.9,
        }
    }
    try:
        response = requests.post(endpoint, json=payload, timeout=45)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")
    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            "Could not connect to Ollama. Ensure Ollama is running locally.\n\n"
            f"Run this command in your terminal:\n`ollama run {model_name}`"
        )
    except Exception as e:
        raise RuntimeError(f"Ollama generation error: {str(e)}")


def call_huggingface_or_router(
    text: str,
    api_url: str,
    api_key: str,
    model_name: str,
    is_openrouter: bool = False
) -> str:
    """Calls Hugging Face Inference API or OpenRouter endpoint."""
    if not api_key:
        raise ValueError("API Key / Token is required for cloud inference.")

    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json"
    }

    if is_openrouter:
        headers["HTTP-Referer"] = "https://localhost:8501"
        headers["X-Title"] = "AI Tailor Ticket Generator"
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Parse this tailor order:\n{text}"}
            ],
            "temperature": 0.1,
        }
        res = requests.post(api_url, headers=headers, json=payload, timeout=45)
        res.raise_for_status()
        data = res.json()
        return data["choices"][0]["message"]["content"]
    else:
        # Standard Hugging Face Inference API format
        prompt = f"<bos><start_of_turn>user\n{SYSTEM_PROMPT}\n\nParse this message:\n{text}<end_of_turn>\n<start_of_turn>model\n"
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 1024,
                "temperature": 0.1,
                "return_full_text": False
            }
        }
        res = requests.post(api_url, headers=headers, json=payload, timeout=45)
        res.raise_for_status()
        data = res.json()
        if isinstance(data, list) and len(data) > 0:
            return data[0].get("generated_text", "")
        return str(data)


# ==============================================================================
# UI Component: Printable Job Card Renderer
# ==============================================================================
def render_job_card(data: dict, shop_name: str, shop_phone: str, ticket_id: str):
    """Renders high-quality semantic HTML for browser preview and print-to-paper."""
    now_str = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")
    urgency = data.get("urgency", "Normal").strip()
    urgency_lower = urgency.lower()

    if "urgent" in urgency_lower:
        badge_class = "badge-urgent"
    elif "express" in urgency_lower:
        badge_class = "badge-express"
    else:
        badge_class = "badge-normal"

    measurements = data.get("measurements", {})
    add_meas = data.get("additional_measurements", [])

    meas_html = "".join([
        f'<div class="{"meas-box empty" if val.lower() in ["not specified", "none", "n/a", ""] else "meas-box"}">'
        f'<div class="meas-label">{label}</div>'
        f'<div class="meas-val">{"—" if val.lower() in ["not specified", "none", "n/a", ""] else val}</div>'
        f'</div>'
        for label, val in measurements.items()
    ])

    for item in add_meas:
        if isinstance(item, dict) and item.get("label"):
            meas_html += (
                f'<div class="meas-box">'
                f'<div class="meas-label">{item.get("label")}</div>'
                f'<div class="meas-val">{item.get("value", "—")}</div>'
                f'</div>'
            )

    instructions = data.get("design_instructions", [])
    if isinstance(instructions, list) and instructions:
        instr_items = "".join([f"<li>{instr}</li>" for instr in instructions])
        instr_html = f"<ul class='instruction-list'>{instr_items}</ul>"
    else:
        instr_html = "<p style='color:#94a3b8; font-size:0.85rem;'>No special design notes specified.</p>"

    pricing = data.get("pricing", {})
    est_cost = pricing.get("estimated_cost", "TBD")
    adv_paid = pricing.get("advance_paid", "0")
    bal_due = pricing.get("balance_due", "TBD")

    # Pure unindented HTML so markdown parser never wraps it in a code block
    html = (
        '<div class="job-card" id="printable-ticket">'
        '<div class="card-header">'
        f'<div><h1 class="shop-title">🧵 {shop_name}</h1>'
        f'<div class="shop-subtitle">Boutique & Tailoring • Ph: {shop_phone}</div></div>'
        f'<div class="job-meta"><div class="job-id">{ticket_id}</div>'
        f'<div style="font-size:0.75rem; color:#64748b;">{now_str}</div>'
        f'<span class="badge {badge_class}">{urgency} Delivery</span></div>'
        '</div>'
        '<div class="client-info-strip">'
        f'<div><div class="client-item-label">Customer Name</div><div class="client-item-value">{data.get("customer_name", "Walk-in Customer")}</div></div>'
        f'<div><div class="client-item-label">Phone / WhatsApp</div><div class="client-item-value">{data.get("phone_number", "Not provided")}</div></div>'
        f'<div><div class="client-item-label">Garment Type</div><div class="client-item-value" style="color: #2563eb;">{data.get("garment_type", "Custom Stitching")}</div></div>'
        f'<div><div class="client-item-label">Due Date</div><div class="client-item-value" style="color: #dc2626;">{data.get("delivery_date", "Standard")}</div></div>'
        '</div>'
        '<div class="measurements-container">'
        '<div class="section-title">Measurements Record</div>'
        f'<div class="measurements-grid">{meas_html}</div>'
        '</div>'
        '<div class="details-grid">'
        '<div>'
        '<div class="section-title">Fabric & Special Customization</div>'
        f'<p style="font-size:0.88rem; margin: 4px 0 10px 0; color:#334155;"><strong>Fabric Details:</strong> {data.get("fabric_details", "Customer Material")}</p>'
        f'{instr_html}'
        '</div>'
        '<div>'
        '<div class="section-title">Billing & Accounts</div>'
        '<div class="financials-box">'
        f'<div class="fin-row"><span>Total Est:</span><span>{est_cost}</span></div>'
        f'<div class="fin-row"><span>Advance Paid:</span><span style="color:#059669;">- {adv_paid}</span></div>'
        f'<div class="fin-row total"><span>Balance Due:</span><span style="color:#b91c1c;">{bal_due}</span></div>'
        '</div>'
        '<div style="margin-top: 14px; text-align: center; border: 1px dashed #cbd5e1; padding: 10px; border-radius: 6px; font-size: 0.72rem; color: #64748b;">'
        'Master Tailor Signature<br><br>___________________________'
        '</div>'
        '</div>'
        '</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)
# ==============================================================================
# Sidebar Configurations
# ==============================================================================
with st.sidebar:
    st.title("⚙️ Boutique Settings")
    shop_name = st.text_input("Boutique / Shop Name", value="Royal Needle Stitchers")
    shop_phone = st.text_input("Shop Contact Number", value="+91 98765-43210")

    st.markdown("---")
    st.subheader("🤖 AI Engine Provider")
    provider = st.selectbox(
        "Inference Engine",
        [
            "Ollama (Local Gemma - Private & Free)",
            "OpenRouter API",
            "Hugging Face Inference API",
        ],
        index=0,
    )

    if "Ollama" in provider:
        st.info("Runs 100% on your machine offline. Zero API costs.")
        model_name = st.text_input("Ollama Model Name", value="gemma2:2b")
        ollama_host = st.text_input("Ollama Host URL", value="http://localhost:11434")
    elif "OpenRouter" in provider:
        api_key = st.text_input("OpenRouter API Key", type="password")
        model_name = st.text_input("Model ID", value="google/gemma-2-9b-it:free")
        endpoint_url = "[https://openrouter.ai/api/v1/chat/completions](https://openrouter.ai/api/v1/chat/completions)"
    else:
        api_key = st.text_input("HF User Access Token", type="password")
        model_name = st.text_input("Model Repository", value="google/gemma-2-2b-it")
        endpoint_url = f"[https://api-inference.huggingface.co/models/](https://api-inference.huggingface.co/models/){model_name}"

    st.markdown("---")
    st.subheader("💡 Demo Quick-Load")
    if st.button("📋 Load Example WhatsApp Message"):
        sample = random.choice(EXAMPLE_MESSAGES)
        st.session_state["input_text_area"] = sample


# ==============================================================================
# Main Application Layout
# ==============================================================================
st.title("✂️ AI Tailor Job Ticket Generator")
st.markdown(
    "Turn chaotic WhatsApp messages, voice-notes, or scribbled notes into structured, "
    "clean, print-ready stitching tickets in seconds."
)

default_text = st.session_state.get(
    "input_text_area",
    "Bhaiya stitch an anarkali kurti, chest 38, waist 34, length 42, 3/4 sleeves (16 inch), "
    "deep neck back with tassels. Needs by this Thursday urgent, fabric provided by customer. "
    "Advance paid 500 total 1200. Customer: Suman (9811223344)",
)

raw_input = st.text_area(
    "Paste customer message, WhatsApp transcript, or rough notes:",
    value=default_text,
    height=120,
)

col1, col2 = st.columns([1, 4])
with col1:
    generate_btn = st.button("⚡ Generate Job Card", type="primary", use_container_width=True)

# Parse & Render Pipeline
if generate_btn:
    if not raw_input.strip():
        st.warning("Please provide or paste a message to extract measurements.")
    else:
        with st.spinner("Analyzing measurements and drafting job card..."):
            try:
                raw_response = ""
                if "Ollama" in provider:
                    raw_response = call_ollama(raw_input, model_name, ollama_host)
                elif "OpenRouter" in provider:
                    raw_response = call_huggingface_or_router(
                        raw_input, endpoint_url, api_key, model_name, is_openrouter=True
                    )
                else:
                    raw_response = call_huggingface_or_router(
                        raw_input, endpoint_url, api_key, model_name, is_openrouter=False
                    )

                # Parse JSON safely
                parsed_ticket = extract_json(raw_response)
                st.session_state["current_ticket"] = parsed_ticket
                st.session_state["ticket_id"] = f"#JOB-{random.randint(1000, 9999)}"
                st.success("Ticket generated successfully!")

            except ConnectionError as ce:
                st.error(str(ce))
            except json.JSONDecodeError:
                st.error("Failed to parse clean JSON from the AI response. Raw output received:")
                st.code(raw_response)
            except Exception as e:
                st.error(f"Error during extraction: {str(e)}")

# Display Generated Ticket & Actions
if "current_ticket" in st.session_state and st.session_state["current_ticket"]:
    ticket_data = st.session_state["current_ticket"]
    ticket_id = st.session_state.get("ticket_id", "#JOB-0001")

    # Action Toolbar
    # Working Print Button via Streamlit Components
    components.html(
        """
        <button onclick="window.parent.print()" style="
            background-color: #0f172a;
            color: #ffffff;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.15);
        ">
            🖨️ Print / Save as PDF
        </button>
        """,
        height=55,
    )

    # Render Styled Card
    render_job_card(ticket_data, shop_name, shop_phone, ticket_id)

    # Raw JSON debug expander
    with st.expander("🔍 View Raw Extracted JSON Schema"):
        st.json(ticket_data)