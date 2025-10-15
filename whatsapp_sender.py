
import streamlit as st
import pandas as pd
import re
import urllib.parse
from io import StringIO
from datetime import datetime

# =============================
# APP CONFIG
# =============================
st.set_page_config(
    page_title="KARIM | WhatsApp Sender PRO+",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================
# UTILITIES
# =============================
def extract_numbers(text: str):
    """Extract candidate phone numbers from any messy text (commas/newlines/words)."""
    if not text:
        return []
    # Normalize separators to new lines, then strip non-digits per line
    lines = text.replace(",", "\n").splitlines()
    numbers = []
    for line in lines:
        digits = re.sub(r"\D", "", line or "")
        if len(digits) >= 8:
            numbers.append(digits)
    return numbers

def clean_number(n: str) -> str:
    """Keep digits only. Don't enforce leading + here (WhatsApp accepts countrycode + number without +)."""
    return re.sub(r"\D", "", str(n or ""))

def normalize_batch(numbers, default_cc=""):
    """
    Normalize a list of numbers:
    - Keep digits only
    - Prepend default country code (without +) if number looks local (starts with 0 or length < 11)
    - Drop obviously invalid (len < 8)
    - Deduplicate (preserving order)
    """
    seen = set()
    out = []
    for raw in numbers:
        d = clean_number(raw)
        if not d or len(d) < 8:
            continue
        # Heuristics: if startswith 0 or short, add default CC (if provided and not already starting with it)
        if default_cc:
            if d.startswith("0"):
                d = default_cc + d.lstrip("0")
            elif len(d) < 11 and not d.startswith(default_cc):
                d = default_cc + d
        if d not in seen:
            seen.add(d)
            out.append(d)
    return out

def build_whatsapp_url(number: str, message: str, platform: str = "web"):
    msg_encoded = urllib.parse.quote(message.strip())
    if platform == "web":
        return f"https://web.whatsapp.com/send?phone={number}&text={msg_encoded}"
    return f"https://wa.me/{number}?text={msg_encoded}"

def validate_placeholders(template: str, allowed=None):
    """
    Return (ok, missing, extra_placeholders_set).
    ok=False if template has placeholders not in allowed.
    """
    allowed = allowed or {"name", "country", "number"}
    vars_found = set(re.findall(r"\{(\w+)\}", template))
    extra = vars_found - allowed
    missing = allowed - vars_found if "{name}" in template or "{country}" in template or "{number}" in template else set()
    return (len(extra) == 0, missing, extra)

def copy_to_clipboard_code(content, label="Copy"):
    btn_id = "copybtn" + str(abs(hash(content)) % (10**8))
    st.markdown(f"""
    <button id="{btn_id}" style="
        background:linear-gradient(90deg,#7c3aed,#2563eb);
        border:none;border-radius:8px;padding:8px 18px;
        color:#fff;font-size:0.95em;font-weight:800;
        margin:8px 0;cursor:pointer;">{label}</button>
    <script>
    const btn = document.getElementById('{btn_id}');
    if (btn) {{
        btn.onclick = function() {{
            navigator.clipboard.writeText({content!r});
            this.innerText = 'Copied!';
            setTimeout(()=>{{this.innerText='{label}'}},1400);
        }};
    }}
    </script>
    """, unsafe_allow_html=True)

# =============================
# SESSION STATE
# =============================
ss = st.session_state
ss.setdefault("numbers", [])
ss.setdefault("names", [])
ss.setdefault("countries", [])
ss.setdefault("df", pd.DataFrame())
ss.setdefault("current", 0)
ss.setdefault("skipped", set())
ss.setdefault("templates", {
    "en": """Hello {name} 👋

We are the Sales Department at EUROSWEET GIDA LTD. ŞTİ. (Istanbul – Turkey).

We specialize in producing high-quality snacks such as:
🍪 Croissants, Cakes, Biscuits, Donuts, Jelly, and Wafers.

We’re always eager to connect with reliable partners in {country} and explore new markets together. 🤝

If you are interested, we’d be happy to share our catalogue and price list, and discuss how we can collaborate.

Looking forward to your reply, {name}!

Best regards,
Sales Department""",
    "ar": """مرحبًا {name} 👋

نحن قسم المبيعات في شركة EUROSWEET GIDA LTD. ŞTİ. (إسطنبول - تركيا).

نُنتج سناكات عالية الجودة مثل:
🍪 الكرواسون، الكيك، البسكويت، الدونات، الجيلي، والويفر.

نسعد دائمًا بالتواصل مع شركاء موثوقين في {country} واستكشاف أسواق جديدة معًا 🤝

إن كنتم مهتمين، يسعدنا مشاركة الكتالوج وقائمة الأسعار ومناقشة سُبل التعاون.

بانتظار ردكم الكريم {name}.

تحياتنا،
قسم المبيعات"""
})

# =============================
# THEME / CSS
# =============================
st.markdown("""
<style>
:root { --pri:#4f46e5; --sec:#8b5cf6; --sky:#06b6d4; --ink:#0f172a; }
.stApp {background: radial-gradient(1200px 600px at 10% 0%, #eef2ff 0%, #f7f7ff 20%, #ffffff 60%) fixed !important;}
.block-container {padding-top:18px; padding-bottom:14px;}
/* Glass panels */
.card {
    background:#fff; border:1px solid #e7e8ff; border-radius:18px;
    box-shadow: 0 8px 28px rgba(53, 35, 160, 0.10);
    padding:20px 18px; margin-bottom:14px;
}
.h1 {
    font-weight:900; font-size:2.1rem; letter-spacing:2px; text-align:center;
    background:linear-gradient(90deg,#4f46e5,#8b5cf6,#06b6d4);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    margin-bottom:6px;
}
.sub {text-align:center; color:#4f46e5; font-weight:800; letter-spacing:.6px; margin-bottom:14px;}
/* Inputs */
input, textarea {
    border-radius:10px !important; background:#f8fafc !important; color:#0f172a !important;
    border:1.4px solid #dce1fb !important; font-weight:600;
}
/* Buttons */
.stButton>button {
    background: linear-gradient(90deg, #4f46e5, #06b6d4);
    border-radius: 10px !important; color: #fff !important; font-weight: 800;
    border: none !important; box-shadow: 0 10px 22px rgba(79,70,229,.22); letter-spacing:.2px;
}
.stButton>button:hover { transform: translateY(-1px); box-shadow: 0 12px 24px rgba(79,70,229,.25); }
.stButton>button:active { transform: scale(.98); }
.badge {
    display:inline-block; padding:6px 10px; border-radius:999px;
    background:linear-gradient(90deg,#e0e7ff,#e0f2fe);
    color:#1e293b; font-weight:800; border:1px solid #dbeafe; margin-right:6px;
}
.kbar { display:flex; gap:10px; justify-content:center; flex-wrap:wrap; margin:6px 0 12px; }
.kbar .badge { cursor:default; }
.small { font-size: .88em; color:#334155; }
.table-box {
    background:#f8fafc; border:1px solid #e2e8f0; padding:8px; border-radius:12px;
    box-shadow: inset 0 1px 0 #fff;
}
.progress-circle {
    width: 64px; height:64px; border-radius:50%;
    background: conic-gradient(#06b6d4 var(--p,0%), #e2e8f0 var(--p,0%) 100%);
    display:flex; align-items:center; justify-content:center;
    box-shadow: 0 4px 16px rgba(2,132,199,0.18);
    margin: 0 auto 8px;
}
.progress-circle span { font-weight:900; color:#0ea5e9; }
.footer { text-align:center; color:#334155; font-weight:700; margin-top:12px; }
</style>
""", unsafe_allow_html=True)

# =============================
# HEADER
# =============================
st.markdown('<div class="card"><div class="h1">KARIM – WhatsApp Sender PRO+</div><div class="sub">Clean • Personalize • Send</div></div>', unsafe_allow_html=True)

# =============================
# SIDEBAR
# =============================
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    platform = st.radio("Send using", ["💻 WhatsApp Web", "📱 WhatsApp App"], horizontal=False)
    platform_type = "web" if platform == "💻 WhatsApp Web" else "mobile"

    st.markdown("---")
    st.markdown("### 🌍 Default Country Code")
    st.write("If numbers are local (start with 0 or short), we'll prepend this country code (digits only).")
    default_cc = st.text_input("Country code (e.g., 20 for Egypt, 971 for UAE, 90 for Türkiye)", value="")
    default_cc = clean_number(default_cc)

    st.markdown("---")
    st.markdown("### 🎯 Workflow")
    st.caption("1) Upload or paste numbers  →  2) Clean & dedupe  →  3) Compose  →  4) Send")
    st.caption("TIP: Use tabs to navigate.")

# =============================
# MAIN TABS
# =============================
tab1, tab2, tab3 = st.tabs(["📥 Upload & Clean", "✍️ Compose", "📤 Send"])

# -----------------------------
# TAB 1 – Upload & Clean
# -----------------------------
with tab1:
    st.markdown("#### Import data")
    colA, colB = st.columns([1.15, 1])
    with colA:
        uploaded = st.file_uploader("Upload CSV or Excel (columns can be in any order).", type=["csv", "xlsx", "xls"])
    with colB:
        st.download_button("⬇️ Sample CSV", "number,name,country\n201111223344,Mohamed,Egypt\n971500000001,Ahmed,UAE\n", file_name="example_contacts.csv")

    numbers, names, countries = [], [], []
    df = None

    if uploaded is not None:
        try:
            fname = uploaded.name.lower()
            if fname.endswith(".csv"):
                df = pd.read_csv(uploaded)
            else:
                df = pd.read_excel(uploaded)

            st.success(f"Loaded {len(df)} rows.")
            cols = list(df.columns)
            st.markdown("##### Map your columns")
            col1, col2, col3 = st.columns(3)
            number_col = col1.selectbox("🟣 Number column", cols, index=0)
            name_col = col2.selectbox("🟢 Name column (optional)", ["- none -"] + cols, index=min(1, len(cols)))
            country_col = col3.selectbox("🔵 Country column (optional)", ["- none -"] + cols, index=min(2, len(cols)))

            df[number_col] = df[number_col].astype(str).map(clean_number)
            df = df[df[number_col].str.len() >= 8].copy()
            df.fillna("", inplace=True)

            numbers = df[number_col].tolist()
            names = (df[name_col].tolist() if name_col != "- none -" else [""] * len(df))
            countries = (df[country_col].tolist() if country_col != "- none -" else [""] * len(df))

        except Exception as e:
            st.error(f"Failed to read file: {e}")
            df = None

    st.markdown("##### Or paste numbers (any format)")
    raw = st.text_area("Paste comma/newline/mixed text here", height=120, placeholder="e.g. tel +254 722 206312, 0020-111-222-3344, 0597 499 217 ...")
    pasted = extract_numbers(raw)
    if pasted:
        st.info(f"Found {len(pasted)} numbers from pasted text.")

    colx, coly = st.columns(2)
    with colx:
        st.markdown("##### Clean & normalize")
        if st.button("🧹 Clean numbers (apply default CC + dedupe)"):
            base_list = numbers or pasted
            if not base_list:
                st.warning("Upload a file or paste numbers first.")
            else:
                cleaned = normalize_batch(base_list, default_cc=default_cc)
                st.success(f"{len(cleaned)} numbers are ready after normalization.")
                ss.numbers = cleaned
                ss.names = names if numbers else [""] * len(cleaned)
                ss.countries = countries if numbers else [""] * len(cleaned)
                ss.df = pd.DataFrame({
                    "number": ss.numbers,
                    "name": ss.names,
                    "country": ss.countries
                })
    with coly:
        if ss.df is not None and not ss.df.empty:
            st.markdown("##### Export cleaned numbers")
            st.download_button("⬇️ Download .txt", "\n".join(ss.numbers), file_name="clean_numbers.txt")
            st.download_button("⬇️ Download .csv", ss.df.to_csv(index=False), file_name="cleaned_contacts.csv")
            copy_to_clipboard_code("\n".join(ss.numbers), "Copy all numbers")

    if ss.df is not None and not ss.df.empty:
        st.markdown("##### Preview cleaned data")
        st.dataframe(ss.df, use_container_width=True, height=260, hide_index=True)
    else:
        st.markdown('<div class="table-box small">No cleaned data yet. Upload or paste, then click <b>Clean numbers</b>.</div>', unsafe_allow_html=True)

# -----------------------------
# TAB 2 – Compose
# -----------------------------
with tab2:
    st.markdown("#### Select a template language or write your own")
    colL, colR = st.columns([1, 1])
    with colL:
        lang = st.radio("Templates", ["English (en)", "العربية (ar)", "Custom"], horizontal=True)
    with colR:
        st.markdown("""
        <div class="kbar">
            <span class="badge">{name}</span>
            <span class="badge">{country}</span>
            <span class="badge">{number}</span>
        </div>
        """, unsafe_allow_html=True)

    if lang == "English (en)":
        template = ss.templates["en"]
    elif lang == "العربية (ar)":
        template = ss.templates["ar"]
    else:
        template = st.text_area("Write your message template", height=230, value=ss.templates["en"])

    ok, missing, extra = validate_placeholders(template)
    if extra:
        st.error(f"Unknown placeholders in template: {', '.join(sorted(extra))}")
    else:
        st.success("Template variables look good.")

    if ss.df is not None and not ss.df.empty:
        idx = min(ss.current, len(ss.numbers)-1) if ss.numbers else 0
        example_name = ss.names[idx] if ss.names else ""
        example_country = ss.countries[idx] if ss.countries else ""
        example_number = ss.numbers[idx] if ss.numbers else ""

        try:
            preview = template.format(name=example_name, country=example_country, number=example_number)
        except Exception as e:
            preview = f"⚠️ Format error: {e}"

        st.markdown("##### Live preview with current contact")
        st.text_area("Preview", value=preview, height=200)

    st.markdown("---")
    colSave, colReset = st.columns(2)
    with colSave:
        if lang == "Custom":
            if st.button("💾 Save as custom (overwrites EN slot)"):
                ss.templates["en"] = template
                st.success("Saved to English slot.")
        else:
            # allow edit built-in then save
            edited = st.text_area("Edit selected template (optional)", value=template, height=160, key="edit_tmpl")
            if st.button("💾 Save edits"):
                key = "en" if lang.startswith("English") else "ar"
                ss.templates[key] = edited
                st.success(f"Saved changes to {key.upper()} template.")

    with colReset:
        if st.button("♻️ Reset progress & skips"):
            ss.current = 0
            ss.skipped = set()
            st.success("Progress reset.")

# -----------------------------
# TAB 3 – Send
# -----------------------------
with tab3:
    st.markdown("#### Send messages")
    if not ss.numbers:
        st.warning("No numbers loaded. Go to **Upload & Clean** first.")
    else:
        total = len(ss.numbers)
        current = min(ss.current, total-1)
        percent = int(((current+1) / total) * 100) if total else 0

        st.markdown(f'<div class="progress-circle" style="--p:{percent}%"><span>{current+1}/{total}</span></div>', unsafe_allow_html=True)

        colA, colB = st.columns([2.2, 1])
        with colA:
            # Compose final message for current contact
            name = ss.names[current] if ss.names else ""
            country = ss.countries[current] if ss.countries else ""
            number = ss.numbers[current]

            # Use latest chosen template from tab2 (prefer edited if present)
            active_template = ss.templates.get("en", "")
            # If user used Arabic selection and saved to 'ar', fallback detection:
            active_template = ss.templates.get("en", active_template)
            final_template = st.text_area("Message to send (per contact)", value=(ss.templates.get("en") or "").format(
                name=name, country=country, number=number
            ), height=180, key="final_msg_box")

        with colB:
            st.markdown("##### Contact")
            st.write(f"**#{current+1} / {total}**")
            info = f"**{number}**"
            if name:
                info += f" — {name}"
            if country:
                info += f" — {country}"
            st.write(info)

            st.markdown("##### Quick list")
            max_show = min(120, total)
            small_list = [f"{i+1}. {ss.numbers[i]}" + (f" - {ss.names[i]}" if i < len(ss.names) and ss.names[i] else "") for i in range(max_show)]
            st.text("\n".join(small_list))

        col1, col2, col3, col4 = st.columns([1.1, 1.1, 1.8, 1.1])
        with col1:
            if st.button("← Prev", disabled=(current <= 0)):
                ss.current = max(0, ss.current-1)
        with col2:
            if st.button("Skip", disabled=(ss.numbers[current] in ss.skipped)):
                ss.skipped.add(ss.numbers[current])
                if ss.current < total-1:
                    ss.current += 1
        with col3:
            if st.button("🚀 Open WhatsApp"):
                msg = st.session_state.get("final_msg_box","").strip()
                url = build_whatsapp_url(ss.numbers[current], msg, platform_type)
                st.markdown(
                    f"<div style='text-align:center; margin-top:6px;'>"
                    f"<a href='{url}' target='_blank' style='font-weight:bold; color:#2563eb; font-size:17px;'>"
                    "Open in WhatsApp</a></div>", unsafe_allow_html=True
                )
                st.components.v1.html(f"""<script>window.open("{url}", "_blank");</script>""")
        with col4:
            if st.button("Next →", disabled=(current >= total-1)):
                ss.current = min(total-1, ss.current+1)

# =============================
# FOOTER
# =============================
st.markdown(f'<div class="footer">✦ Built for <b>KARIM</b> • {datetime.now().year} • PRO+</div>', unsafe_allow_html=True)
