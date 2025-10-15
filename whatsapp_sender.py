
import streamlit as st
import pandas as pd
import urllib.parse
import re
from datetime import datetime

# =============================
# APP CONFIG
# =============================
st.set_page_config(
    page_title="KARIM | WhatsApp Sender – Hybrid V3.2",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================
# UTILITIES
# =============================
def extract_numbers(text):
    if not text:
        return []
    lines = text.replace(",", "\n").splitlines()
    numbers = []
    for line in lines:
        digits = re.sub(r"\D", "", line or "")
        if len(digits) >= 8:
            numbers.append(digits)
    return numbers

def clean_number(n):
    return re.sub(r"\D", "", str(n or ""))

def normalize_batch(numbers, default_cc=""):
    seen, out = set(), []
    for raw in numbers or []:
        d = clean_number(raw)
        if len(d) < 8:
            continue
        if default_cc:
            if d.startswith("0"):
                d = default_cc + d.lstrip("0")
            elif len(d) < 11 and not d.startswith(default_cc):
                d = default_cc + d
        if d not in seen:
            seen.add(d)
            out.append(d)
    return out

def copy_to_clipboard_code(content, label="Copy"):
    btn_id = "copybtn" + str(abs(hash(content)) % (10**9))
    st.markdown(f"""
    <button id="{btn_id}" style="
        background:linear-gradient(90deg,#2563eb,#06b6d4);
        border:none;border-radius:10px;padding:9px 18px;
        color:#fff;font-size:0.95em;font-weight:900;
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

def build_whatsapp_url(number: str, message: str, platform: str = "web"):
    msg_encoded = urllib.parse.quote(message.strip())
    if platform == "web":
        return f"https://web.whatsapp.com/send?phone={number}&text={msg_encoded}"
    return f"https://wa.me/{number}?text={msg_encoded}"

def validate_placeholders(template: str, allowed=None):
    allowed = allowed or {"name", "country", "number"}
    vars_found = set(re.findall(r"\{(\w+)\}", template))
    extra = vars_found - allowed
    return (len(extra) == 0, extra)

# =============================
# TEMPLATES
# =============================
templates = {
    'en': """Hello {name} 👋

We are the Sales Department at EUROSWEET GIDA LTD. ŞTİ. (Istanbul – Turkey).

We specialize in producing high-quality snacks such as:
🍪 Croissants, Cakes, Biscuits, Donuts, Jelly, and Wafers.

We’re always eager to connect with reliable partners in {country} and explore new markets together. 🤝

If you are interested, we’d be happy to share our catalogue and price list, and discuss how we can collaborate.

Looking forward to your reply, {name}!

Best regards,
Sales Department""",
    'ar': """مرحبًا {name} 👋

نحن قسم المبيعات في شركة EUROSWEET GIDA LTD. ŞTİ. (إسطنبول - تركيا).

نُنتج سناكات عالية الجودة مثل:
🍪 الكرواسون، الكيك، البسكويت، الدونات، الجيلي، والويفر.

نسعد دائمًا بالتواصل مع شركاء موثوقين في {country} واستكشاف أسواق جديدة معًا 🤝

إن كنتم مهتمين، يسعدنا مشاركة الكتالوج وقائمة الأسعار ومناقشة سُبل التعاون.

بانتظار ردكم الكريم {name}.

تحياتنا،
قسم المبيعات""",
    'tr': """Merhaba {name} 👋

Biz EUROSWEET GIDA LTD. ŞTİ. (İstanbul – Türkiye) Satış Departmanıyız.

Aşağıdaki yüksek kaliteli atıştırmalıkları üretiyoruz:
🍪 Kruvasan, Kek, Bisküvi, Donut, Jöle ve Gofret.

{country} pazarında güvenilir ortaklarla tanışmak ve yeni fırsatları birlikte keşfetmek isteriz. 🤝

İlgileniyorsanız, kataloğumuzu ve fiyat listemizi paylaşabilir, iş birliğini konuşabiliriz.

Saygılarımızla,
Satış Departmanı""",
    'fr': """Bonjour {name} 👋

Nous sommes le département commercial de EUROSWEET GIDA LTD. ŞTİ. (Istanbul – Turquie).

Nous sommes spécialisés dans la production de snacks de haute qualité :
🍪 Croissants, gâteaux, biscuits, donuts, gelées et gaufrettes.

Nous serions ravis de collaborer avec des partenaires fiables en {country} et d'explorer ensemble de nouveaux marchés. 🤝

Si vous êtes intéressé, nous pouvons partager notre catalogue et notre liste de prix.

Cordialement,
Département des ventes""",
    'es': """Hola {name} 👋

Somos el Departamento de Ventas de EUROSWEET GIDA LTD. ŞTİ. (Estambul – Turquía).

Producimos snacks de alta calidad como:
🍪 Cruasanes, pasteles, galletas, donuts, gelatinas y barquillos.

Nos gustaría conectar con socios confiables en {country} y explorar nuevos mercados juntos. 🤝

Si le interesa, podemos compartir nuestro catálogo y lista de precios.

Saludos cordiales,
Departamento de Ventas"""
}

# =============================
# SESSION
# =============================
ss = st.session_state
ss.setdefault("numbers", [])
ss.setdefault("names", [])
ss.setdefault("countries", [])
ss.setdefault("current", 0)
ss.setdefault("skipped", set())
ss.setdefault("last_numbers", [])
ss.setdefault("theme", "Pure Black")
ss.setdefault("saved_custom", "")
ss.setdefault("heading_color", "#22d3ee")  # default for dark
ss.setdefault("text_color", "#e5e7eb")     # default for dark

# =============================
# THEME CONTROLS
# =============================
with st.sidebar:
    st.markdown("### 🎨 Theme & Colors")
    theme = st.radio("Theme", ["Classic Glass", "Pure Black"], index=1 if ss.theme == "Pure Black" else 0)
    ss.theme = theme
    ss.heading_color = st.color_picker("Heading/Label Color", ss.heading_color, help="ينطبق على العناوين والتبويبات والراديو والليبل")
    ss.text_color = st.color_picker("Body/Text Color", ss.text_color, help="لون النص العام في الثيم المختار")

# =============================
# CSS BUILDERS
# =============================
def css_classic(heading_color: str, text_color: str) -> str:
    return f"""
<style>
:root {{ --pri:#4f46e5; --sec:#8b5cf6; --sky:#06b6d4; --ink:{text_color}; }}
.stApp {{background: radial-gradient(1200px 600px at 10% 0%, #eef2ff 0%, #f7f7ff 20%, #ffffff 60%) fixed !important;}}
.block-container {{padding-top:18px; padding-bottom:14px;}}
.card {{background:#fff; border:1px solid #e7e8ff; border-radius:18px; box-shadow:0 8px 28px rgba(53, 35, 160, .10); padding:20px 18px; margin-bottom:14px;}}
.h1 {{font-weight:900; font-size:2.1rem; letter-spacing:2px; text-align:center; background:linear-gradient(90deg,{heading_color},{heading_color},#06b6d4);
-webkit-background-clip:text; -webkit-text-fill-color:transparent; margin-bottom:6px;}}
.sub {{text-align:center; color:{heading_color}; font-weight:900; letter-spacing:.6px; margin-bottom:14px;}}
/* labels + tabs + radios */
label, h3, h4, .stMarkdown p, .stTextInput label, .stSelectbox label, .stRadio label, .stTextArea label {{ color:{heading_color} !important; font-weight:900 !important; }}
/* tabs */
.stTabs [data-baseweb="tab"] button p {{ color:{heading_color} !important; font-weight:900 !important; }}
/* radio/checkbox inner text */
.stRadio > div[role="radiogroup"] * {{ color:{text_color} !important; font-weight:700 !important; }}
/* inputs */
input, textarea {{ border-radius:10px !important; background:#f8fafc !important; color:{text_color} !important; border:1.4px solid #dce1fb !important; font-weight:700;}}
/* buttons */
.stButton>button {{background:linear-gradient(90deg, #4f46e5, #06b6d4); border-radius:10px !important; color:#fff !important; font-weight:900; border:none !important; box-shadow:0 10px 22px rgba(79,70,229,.22);}}
.stButton>button:hover {{ transform: translateY(-1px); }}
.progress-circle {{width: 64px; height:64px; border-radius:50%; background: conic-gradient(#06b6d4 var(--p,0%), #e2e8f0 var(--p,0%) 100%); display:flex; align-items:center; justify-content:center; box-shadow: 0 4px 16px rgba(2,132,199,0.18); margin: 0 auto 8px;}}
.progress-circle span {{ font-weight:900; color:#0ea5e9; }}
.k-list {{ display:flex; flex-direction:column; gap:2px; background:#f1f5f9; border:1px solid #e2e8f0; border-radius:10px; padding:8px; max-height:150px; overflow:auto; color:{text_color}; font-weight:800;}}
.k-list .active {{ background:linear-gradient(90deg,#0ea5e9,#22d3ee); color:#fff; border-radius:7px; padding-left:6px; }}
</style>
"""

def css_black(heading_color: str, text_color: str) -> str:
    return f"""
<style>
:root {{ --bg:#000; --panel:#0b0b0b; --panel-border:#1a1a1a; --ink:{text_color}; --accent:{heading_color}; }}
.stApp {{ background: var(--bg) !important; }}
.block-container {{ padding-top:16px; }}
.card {{ background: linear-gradient(180deg,#0a0a0a,#0f0f0f); border:1px solid var(--panel-border); border-radius:18px; box-shadow:0 10px 30px rgba(0,0,0,.45), inset 0 1px 0 rgba(255,255,255,.02); padding:20px 18px; margin:10px 0 14px; }}
.h1 {{ font-weight:1000; font-size:2.2rem; letter-spacing:6px; text-align:center; background: linear-gradient(90deg, #fff, {heading_color}, {heading_color}); -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin-bottom:6px; }}
.sub {{ text-align:center; color:{heading_color}; font-weight:1000; letter-spacing:1px; margin-bottom:10px; opacity:.95; }}
/* labels + tabs + radios */
label, h3, h4, .stMarkdown p, .stTextInput label, .stSelectbox label, .stRadio label, .stTextArea label {{ color:{heading_color} !important; font-weight:1000 !important; }}
/* tabs text */
.stTabs [data-baseweb="tab"] button p {{ color:{heading_color} !important; font-weight:1000 !important; }}
/* radio/checkbox inner text */
.stRadio > div[role="radiogroup"] * {{ color:{text_color} !important; font-weight:900 !important; }}
/* inputs */
input, textarea {{ background:#0c0c0c !important; color:{text_color} !important; border:1.4px solid #1f2937 !important; border-radius:10px !important; font-weight:900 !important; }}
/* buttons */
.stButton>button {{ background: linear-gradient(90deg, #2563eb, #06b6d4); border-radius: 11px !important; color:#fff !important; font-weight:1000 !important; border:none !important; box-shadow: 0 10px 24px rgba(3,105,161,.35); }}
.stButton>button:hover {{ transform: translateY(-1px); }}
.progress-circle {{width: 64px; height:64px; border-radius:50%; background: conic-gradient({heading_color} var(--p,0%), #111827 var(--p,0%) 100%); display:flex; align-items:center; justify-content:center; box-shadow: 0 4px 16px rgba(34,211,238,.22); margin: 0 auto 8px;}}
.progress-circle span {{ font-weight:1000; color:{text_color}; }}
.k-list {{ display:flex; flex-direction:column; gap:2px; background:#0a0a0a; border:1px solid #171923; border-radius:10px; padding:8px; max-height:150px; overflow:auto; color:{text_color}; font-weight:900; }}
.k-list .active {{ background: linear-gradient(90deg, rgba(34,211,238,.25), rgba(96,165,250,.25)); color:#fff; border-left: 4px solid {heading_color}; border-radius: 7px; padding-left: 6px; }}
</style>
"""

# Apply CSS
st.markdown(css_classic(ss.heading_color, ss.text_color) if ss.theme == "Classic Glass" else css_black(ss.heading_color, ss.text_color), unsafe_allow_html=True)

# =============================
# HEADER
# =============================
st.markdown('<div class="card"><div class="h1">KARIM – WhatsApp Sender</div><div class="sub">Hybrid V3.2 • Custom Colors</div></div>', unsafe_allow_html=True)

# =============================
# SIDEBAR CONTROLS
# =============================
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    platform = st.radio("Send using", ["💻 WhatsApp Web", "📱 WhatsApp App"], horizontal=False, key="platform")
    platform_type = "web" if platform == "💻 WhatsApp Web" else "mobile"
    st.markdown("---")
    st.markdown("### 🌍 Default Country Code")
    default_cc = st.text_input("Digits only (e.g., 20, 971, 90)", value=st.session_state.get("default_cc",""))
    st.session_state["default_cc"] = clean_number(default_cc)
    st.markdown("---")
    st.markdown("### 💾 Export")
    if ss.get("last_numbers"):
        st.download_button("⬇️ Download .txt", "\n".join(ss["last_numbers"]), file_name="clean_numbers.txt", key="dl-side")
        st.download_button("⬇️ Download .csv", pd.DataFrame({"number": ss["last_numbers"]}).to_csv(index=False), file_name="cleaned_contacts.csv", key="dl-side-csv")

# =============================
# TABS
# =============================
tab1, tab2, tab3 = st.tabs(["📥 Upload & Clean", "✍️ Compose", "📤 Send"])

# TAB 1
with tab1:
    st.markdown("#### Import data")
    colA, colB = st.columns([1.2, 1])
    with colA:
        uploaded = st.file_uploader("Upload CSV or Excel (any column order).", type=["csv", "xlsx", "xls"])
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
            st.markdown("##### Map columns")
            col1, col2, col3 = st.columns(3)
            number_col = col1.selectbox("🟣 Number", cols, index=0)
            name_col = col2.selectbox("🟢 Name (optional)", ["- none -"] + cols, index=min(1, len(cols)))
            country_col = col3.selectbox("🔵 Country (optional)", ["- none -"] + cols, index=min(2, len(cols)))

            df[number_col] = df[number_col].astype(str).map(clean_number)
            df = df[df[number_col].str.len() >= 8].copy()
            df.fillna("", inplace=True)

            numbers = df[number_col].tolist()
            names = (df[name_col].tolist() if name_col != "- none -" else [""] * len(df))
            countries = (df[country_col].tolist() if country_col != "- none -" else [""] * len(df))

        except Exception as e:
            st.error(f"Failed to read file: {e}")
            df = None

    st.markdown("##### Or paste numbers")
    raw = st.text_area("Paste comma/newline/mixed text here", height=120, placeholder="e.g. tel +254 722 206312, 0020-111-222-3344, 0597 499 217 ...")
    pasted = extract_numbers(raw)
    if pasted:
        st.info(f"Found {len(pasted)} numbers from pasted text.")

    colx, coly = st.columns(2)
    with colx:
        st.markdown("##### Clean & normalize")
        if st.button("🧹 Clean numbers (default CC + dedupe)"):
            base_list = numbers or pasted
            if not base_list:
                st.warning("Upload a file or paste numbers first.")
            else:
                cleaned = normalize_batch(base_list, default_cc=st.session_state["default_cc"])
                st.success(f"{len(cleaned)} numbers are ready after normalization.")
                ss.numbers = cleaned
                ss.names = names if numbers else [""] * len(cleaned)
                ss.countries = countries if numbers else [""] * len(cleaned)
                ss.last_numbers = cleaned
                ss.df = pd.DataFrame({"number": ss.numbers, "name": ss.names, "country": ss.countries})
    with coly:
        if ss.get("df", None) is not None and not getattr(ss.get("df"), "empty", True):
            st.markdown("##### Export cleaned")
            st.download_button("⬇️ .txt", "\n".join(ss.numbers), file_name="clean_numbers.txt")
            st.download_button("⬇️ .csv", ss.df.to_csv(index=False), file_name="cleaned_contacts.csv")
            copy_to_clipboard_code("\n".join(ss.numbers), "Copy all numbers")

    if ss.get("df", None) is not None and not getattr(ss.get("df"), "empty", True):
        st.markdown("##### Preview")
        st.dataframe(ss.df, use_container_width=True, height=260, hide_index=True)
    else:
        st.markdown('<div class="table-box">No cleaned data yet. Upload or paste, then click <b>Clean numbers</b>.</div>', unsafe_allow_html=True)

# TAB 2
with tab2:
    st.markdown("#### Templates / Compose")
    colL, colR = st.columns([1, 1])
    with colL:
        lang = st.radio("Templates", ["English (en)", "العربية (ar)", "Türkçe (tr)", "Français (fr)", "Español (es)", "Custom"], horizontal=True)
    with colR:
        st.markdown("""
        <div>
            <span class="badge">{name}</span>
            <span class="badge">{country}</span>
            <span class="badge">{number}</span>
        </div>
        """, unsafe_allow_html=True)

    # choose base template
    if lang.startswith("English"):
        base_template = templates["en"]
    elif lang.startswith("العربية"):
        base_template = templates["ar"]
    elif lang.startswith("Türkçe"):
        base_template = templates["tr"]
    elif lang.startswith("Français"):
        base_template = templates["fr"]
    elif lang.startswith("Español"):
        base_template = templates["es"]
    else:
        base_template = ss.saved_custom or templates["en"]

    edited_template = st.text_area("Edit / Write your message template", height=260, value=base_template, key="tmpl_edit")

    ok, extra = validate_placeholders(edited_template)
    if extra:
        st.error("Unknown placeholders: " + ", ".join(sorted(extra)))
    else:
        st.success("Template placeholders look good.")

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("💾 Save as Custom"):
            ss.saved_custom = edited_template
            st.success("Saved to Custom.")
    with c2:
        if st.button("♻️ Reset Progress & Skips"):
            ss.current = 0
            ss.skipped = set()
            st.success("Progress reset.")
    with c3:
        st.caption("Use tabs to preview/send.")

    # Live preview (if we have data)
    if ss.get("numbers"):
        idx = min(ss.current, len(ss.numbers)-1)
        example_name = ss.names[idx] if ss.names else ""
        example_country = ss.countries[idx] if ss.countries else ""
        example_number = ss.numbers[idx] if ss.numbers else ""
        try:
            preview = edited_template.format(name=example_name, country=example_country, number=example_number)
        except Exception as e:
            preview = f"⚠️ Format error: {e}"
        st.markdown("##### Live preview with current contact")
        st.text_area("Preview", value=preview, height=200)

# TAB 3
with tab3:
    st.markdown("#### Send messages")
    if not ss.get("numbers"):
        st.warning("No numbers loaded. Go to **Upload & Clean** first.")
    else:
        total = len(ss.numbers)
        current = min(ss.current, total-1)
        percent = int(((current+1) / total) * 100) if total else 0
        st.markdown(f'<div class="progress-circle" style="--p:{percent}%"><span>{current+1}/{total}</span></div>', unsafe_allow_html=True)

        # Compose final per-contact from current edited template (fallback to saved/custom)
        active_template = st.session_state.get("tmpl_edit") or ss.saved_custom or templates["en"]
        name = ss.names[current] if ss.names else ""
        country = ss.countries[current] if ss.countries else ""
        number = ss.numbers[current]
        try:
            default_message = active_template.format(name=name, country=country, number=number)
        except Exception as e:
            default_message = f"⚠️ Template error: {e}"
        message = st.text_area("Message to send (per contact)", value=default_message, height=180, key="final_msg_box")

        colA, colB = st.columns([2.2, 1])
        with colA:
            if st.button("🚀 Open WhatsApp"):
                url = build_whatsapp_url(number, message, platform_type=st.session_state.get("platform_type","web"))
                st.markdown(
                    f"<div style='text-align:center; margin-top:6px;'>"
                    f"<a href='{url}' target='_blank' style='font-weight:900; color:{ss.heading_color}; font-size:17px;'>"
                    "Open in WhatsApp</a></div>", unsafe_allow_html=True
                )
                st.components.v1.html(f"""<script>window.open("{url}", "_blank");</script>""")
        with colB:
            st.markdown("##### Contact")
            info = f"**{number}**"
            if name: info += f" — {name}"
            if country: info += f" — {country}"
            st.write(info)
            # quick list
            max_show = min(120, total)
            lines = [f"{i+1}. {ss.numbers[i]}" + (f" - {ss.names[i]}" if i < len(ss.names) and ss.names[i] else "") for i in range(max_show)]
            st.text("\n".join(lines))

        # navigation
        col1, col2, col3, col4 = st.columns([1.1, 1.1, 1.1, 1.1])
        if col1.button("← Prev", disabled=(current <= 0)):
            ss.current = max(0, ss.current-1)
        if col2.button("Skip", disabled=(ss.numbers[current] in ss.skipped)):
            ss.skipped.add(ss.numbers[current])
            if ss.current < total-1:
                ss.current += 1
        if col3.button("Next →", disabled=(current >= total-1)):
            ss.current = min(total-1, ss.current+1)
        if col4.button("Reset ↻"):
            ss.current = 0
            ss.skipped = set()

# =============================
# FOOTER
# =============================
st.markdown(f'**© KARIM OTHMAN — {datetime.now().year}**')
