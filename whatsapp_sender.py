
import streamlit as st
import pandas as pd
import urllib.parse
import re
from datetime import datetime

# =============================
# APP CONFIG
# =============================
st.set_page_config(
    page_title="KARIM | WhatsApp Sender V3 – Pure Black",
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
        background:linear-gradient(90deg,#0ea5e9,#2563eb);
        border:none;border-radius:10px;padding:10px 20px;
        color:#fff;font-size:0.98em;font-weight:900;
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

# =============================
# TEMPLATES (5 languages)
# =============================
templates = {
    'en': """Hello 👋

We are the Sales Department at EUROSWEET GIDA LTD. ŞTİ. (Istanbul – Turkey).

We specialize in producing high-quality snacks such as:
🍪 Croissants, Cakes, Biscuits, Donuts, Jelly, and Wafers.

We're always eager to connect with reliable partners and explore new markets together. 🤝

If you are interested, we are happy to share our catalogue and price list, and discuss how we can work together.

Looking forward to your reply!

Best regards,
Sales Department""",
    'ar': """مرحبًا 👋

نحن قسم المبيعات في شركة EUROSWEET GIDA LTD. ŞTİ. (إسطنبول – تركيا).

نحن متخصصون في إنتاج سناكات عالية الجودة مثل:
🍪 الكرواسون، الكيك، البسكويت، الدونات، الجيلي، والويفر.

نسعى دائمًا للتواصل مع شركاء موثوقين واستكشاف أسواق جديدة معًا 🤝

إذا كنت مهتمًا، يسعدنا أن نرسل لك الكتالوج وقائمة الأسعار ومناقشة فرص التعاون.

بانتظار ردكم الكريم!

تحياتنا،
قسم المبيعات""",
    'tr': """Merhaba 👋

Biz EUROSWEET GIDA LTD. ŞTİ. (İstanbul – Türkiye) Satış Departmanıyız.

Şu yüksek kaliteli atıştırmalıkları üretiyoruz:
🍪 Kruvasan, Kek, Bisküvi, Donut, Jöle ve Gofret.

Her zaman güvenilir ortaklarla bağ kurmak ve yeni pazarları birlikte keşfetmek isteriz. 🤝

İlgileniyorsanız, kataloğumuzu ve fiyat listemizi paylaşabilir, iş birliğini konuşabiliriz.

Cevabınızı bekliyoruz!

Saygılarımızla,
Satış Departmanı""",
    'fr': """Bonjour 👋

Nous sommes le département commercial de EUROSWEET GIDA LTD. ŞTİ. (Istanbul – Turquie).

Nous produisons des snacks de haute qualité, notamment :
🍪 Croissants, gâteaux, biscuits, donuts, gelées et gaufrettes.

Nous souhaitons collaborer avec des partenaires fiables et explorer ensemble de nouveaux marchés. 🤝

Si vous êtes intéressé, nous serions ravis de partager notre catalogue, notre liste de prix et d'échanger sur une éventuelle coopération.

Dans l’attente de votre retour !

Cordialement,
Département des ventes""",
    'es': """Hola 👋

Somos el Departamento de Ventas de EUROSWEET GIDA LTD. ŞTİ. (Estambul – Turquía).

Producimos snacks de alta calidad como:
🍪 Cruasanes, pasteles, galletas, donuts, gelatinas y barquillos.

Siempre buscamos conectar con socios confiables y explorar nuevos mercados juntos. 🤝

Si le interesa, podemos compartir nuestro catálogo y lista de precios, y conversar sobre cómo colaborar.

¡Esperamos su respuesta!

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

# =============================
# PURE BLACK THEME (CSS)
# =============================
st.markdown("""
<style>
:root {
  --bg: #000000;
  --panel: #0b0b0b;
  --panel-border: #1a1a1a;
  --ink: #ffffff;
  --ink-dim: #cfd3dc;
  --accent: #22d3ee;
  --accent2: #60a5fa;
  --muted: #0f172a;
}
html, body, .stApp { background: var(--bg) !important; }
.block-container { padding-top: 16px; }

/* Panels */
.panel {
  background: linear-gradient(180deg, #0a0a0a, #0f0f0f);
  border: 1px solid var(--panel-border);
  border-radius: 18px;
  box-shadow: 0 10px 30px rgba(0,0,0,.45), inset 0 1px 0 rgba(255,255,255,.02);
  padding: 20px 18px;
  margin: 10px 0 14px;
}

/* Headings / Labels */
h3, h4, label, .stMarkdown p, .stTextInput label, .stSelectbox label, .stRadio label, .stTextArea label {
  color: var(--ink) !important;
  font-weight: 900 !important;
  letter-spacing: .3px;
}
/* Inputs */
input, textarea, .stTextInput>div>input, .stTextArea>div>textarea {
  background: #0c0c0c !important;
  color: var(--ink) !important;
  border: 1.4px solid #1f2937 !important;
  border-radius: 10px !important;
  font-weight: 800 !important;
}
/* Buttons */
.stButton>button {
  background: linear-gradient(90deg, #2563eb, #06b6d4);
  border-radius: 11px !important;
  color: #fff !important;
  font-weight: 1000 !important;
  border: none !important;
  box-shadow: 0 10px 24px rgba(3,105,161,.35);
}
.stButton>button:hover { transform: translateY(-1px); box-shadow: 0 12px 28px rgba(2,132,199,.38); }
.stButton>button:active { transform: scale(.98); }

/* Logo */
.k-logo {
  font-weight: 1000;
  font-size: 2.4rem;
  letter-spacing: 8px;
  text-align:center;
  background: linear-gradient(90deg, #ffffff, #60a5fa, #22d3ee);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 6px;
}
.k-sub {
  text-align:center;
  color: var(--ink);
  font-weight: 900;
  letter-spacing: 1.2px;
  font-size: 1.05rem;
  margin-bottom: 12px;
  opacity: .92;
}

/* Pills / badges */
.tag, .k-badge {
  display:inline-block;
  background: linear-gradient(90deg, #0b1220, #0f172a);
  border: 1px solid #1f2937;
  padding: 7px 12px;
  border-radius: 999px;
  font-weight: 1000;
  color: #e5e7eb;
}

/* Lists */
.k-list {
  display:flex; flex-direction:column; gap:2px;
  background: #0a0a0a; border:1px solid #171923; border-radius:10px;
  padding:8px; max-height:150px; overflow:auto; color:#cbd5e1; font-weight:900;
}
.k-list .active {
  background: linear-gradient(90deg, rgba(34,211,238,.25), rgba(96,165,250,.25));
  color: #ffffff;
  border-left: 4px solid var(--accent);
  border-radius: 7px;
  padding-left: 6px;
}

/* Footer */
.footer { text-align:center; color:#9ca3af; font-weight:900; margin-top:12px; }
.info-card {
  background: linear-gradient(180deg, rgba(96,165,250,.08), rgba(34,211,238,.06));
  border: 1px solid #1f2937;
  color: #d1d5db; font-weight:900; border-radius:12px; padding:10px 12px;
}

/* Code blocks */
code, pre, .stCode { color:#d8dee9 !important; background: #0b0b0b !important; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# =============================
# LAYOUT
# =============================
col1, col2, col3 = st.columns([1,2.4,1])

# -------- Left sider
with col1:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("### 🧰 Bulk Tools")
    if ss.get("last_numbers"):
        st.download_button("⬇️ Download .txt", "\n".join(ss["last_numbers"]), file_name="clean_numbers.txt", key="dl-side")
        copy_to_clipboard_code("\n".join(ss["last_numbers"]), "Copy All Numbers")
    else:
        st.markdown('<div class="info-card">ℹ️ Clean numbers will appear here after filtering.</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🔗 Import / Export")
    st.markdown("**• Upload CSV/Excel or paste numbers.  • Export or copy filtered numbers.**")
    st.markdown("---")
    st.markdown("### ✨ What’s New")
    st.markdown("**Pure Black theme • Bold typography • Same features, sleeker UI**")
    st.markdown('</div>', unsafe_allow_html=True)

# -------- Right sider
with col3:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("### ⚡ Quick Links & News")
    st.markdown("**Official Catalog:**  \n[eurosweet.com.tr](https://eurosweet.com.tr)")
    st.markdown("**Contact Developer:**  \n[karim.amsha@gmail.com](mailto:karim.amsha@gmail.com)")
    st.markdown("**Latest Update:**  \n🚀 V3 – Pure Black theme")
    st.markdown('</div>', unsafe_allow_html=True)

# -------- Main center
with col2:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="k-logo">KARIM</div>', unsafe_allow_html=True)
    st.markdown('<div class="k-sub">WhatsApp Broadcast Sender • V3 Pure Black</div>', unsafe_allow_html=True)

    # Mode & Platform
    st.markdown("#### Mode")
    mode = st.radio("", ["Simple: Numbers Only", "Smart: Personalized Name & Country"], horizontal=True, key="mode")

    st.markdown("#### Platform")
    platform = st.radio("", ["💻 WhatsApp Web", "📱 WhatsApp App"], horizontal=True, key="plat")
    platform_type = "web" if platform == "💻 WhatsApp Web" else "mobile"

    # Init containers
    numbers = []
    names = []
    countries = []
    df = None

    if mode == "Simple: Numbers Only":
        st.markdown("#### Language")
        lang = st.radio("", ["🇬🇧 English", "🇸🇦 العربية", "🇹🇷 Türkçe", "🇫🇷 Français", "🇪🇸 Español"], horizontal=True, key="lang")
        lang_code = {"🇬🇧 English":"en","🇸🇦 العربية":"ar","🇹🇷 Türkçe":"tr","🇫🇷 Français":"fr","🇪🇸 Español":"es"}[lang]

        st.markdown("#### Numbers")
        numbers_raw = st.text_area("Paste numbers (comma/newline/any format)", height=120, placeholder="e.g. +971 50 000 0001, 0020-111-222-3344 ...")
        numbers = extract_numbers(numbers_raw)
        names = [''] * len(numbers)
        countries = [''] * len(numbers)
        msg_template = templates[lang_code]

        default_cc = st.text_input("Default Country Code (optional, digits only)", value="", key="dcc_simple")
        if st.button("🧹 Clean Numbers", key="clean_simple"):
            cleaned = normalize_batch(numbers, default_cc=clean_number(default_cc))
            ss["last_numbers"] = cleaned
            numbers = cleaned

        if numbers_raw and numbers:
            st.markdown("#### Filtered Numbers")
            st.code('\n'.join(numbers), language="text")
            copy_to_clipboard_code("\n".join(numbers), "Copy Filtered Numbers")
            st.download_button("⬇️ Download filtered numbers", "\n".join(numbers), file_name="clean_numbers.txt", key="dl-main")

    else:
        st.markdown('<div class="info-card">You can upload a CSV (<b>number,name,country</b>) or enter data manually.</div>', unsafe_allow_html=True)
        st.download_button("⬇️ Download example CSV", "number,name,country\n201111223344,Mohamed,Egypt\n971500000001,Ahmed,UAE\n", file_name="example_contacts.csv")

        data_opt = st.radio("Input method", ["Upload CSV/Excel", "Manual entry"], horizontal=True, key="smart_input")

        if data_opt == "Upload CSV/Excel":
            uploaded_file = st.file_uploader("Upload file (CSV or Excel: number,name,country)", type=["csv","xlsx","xls"])
            if uploaded_file is not None:
                try:
                    filename = uploaded_file.name.lower()
                    if filename.endswith('.csv'):
                        df = pd.read_csv(uploaded_file)
                    else:
                        df = pd.read_excel(uploaded_file)
                    columns = list(df.columns)
                    number_col = st.selectbox("Number column", columns, index=0)
                    name_col = st.selectbox("Name column (optional)", ["- none -"] + columns, index=min(1, len(columns)))
                    country_col = st.selectbox("Country column (optional)", ["- none -"] + columns, index=min(2, len(columns)))

                    df = df.dropna(subset=[number_col]).copy()
                    df[number_col] = df[number_col].astype(str).apply(clean_number)
                    df = df[df[number_col].str.len() >= 8].astype(str)

                    numbers = df[number_col].tolist()
                    names = df[name_col].tolist() if name_col != "- none -" else ['']*len(df)
                    countries = df[country_col].tolist() if country_col != "- none -" else ['']*len(df)

                    st.success(f"{len(df)} contacts loaded.")
                except Exception as e:
                    st.error(f"Failed to process file: {e}")
        else:
            st.info("Enter data manually (add/remove rows as needed):")
            example_data = pd.DataFrame({'number':['201111223344','971500000001'],'name':['Mohamed','Ahmed'],'country':['Egypt','UAE']})
            df = st.data_editor(example_data, num_rows="dynamic", use_container_width=True, key="editor")
            df["number"] = df["number"].apply(clean_number)
            df = df[df["number"].str.len() >= 8].astype(str)
            numbers = df['number'].tolist() if 'number' in df.columns else []
            names = df['name'].tolist() if 'name' in df.columns else ['']*len(df)
            countries = df['country'].tolist() if 'country' in df.columns else ['']*len(df)

        default_cc = st.text_input("Default Country Code (optional, digits only)", value="", key="dcc_smart")
        if st.button("🧹 Clean & Normalize List", key="normalize_smart"):
            numbers = normalize_batch(numbers, default_cc=clean_number(default_cc))
            st.success(f"{len(numbers)} numbers ready after normalization.")

        msg_template = st.text_area(
            "Write message template (use {name}, {country}, {number})",
            value=(
                "Hello {name} 👋\n\n"
                "We are the Sales Department at EUROSWEET GIDA LTD. ŞTİ. (Istanbul – Turkey).\n\n"
                "We specialize in producing high-quality snacks.\n\n"
                "We’re eager to connect with reliable partners in {country}.\n\n"
                "Best regards,\nSales Department"
            ),
            height=200, key="smart_template"
        )

        ss["last_numbers"] = numbers if numbers else []
        if df is not None and not df.empty:
            st.markdown("#### Filtered Numbers")
            st.code('\n'.join(numbers), language="text")
            copy_to_clipboard_code("\n".join(numbers), "Copy Filtered Numbers")
            st.download_button("⬇️ Download filtered numbers", "\n".join(numbers), file_name="clean_numbers.txt", key="dl-main-smart")

    # ======= Sending / Progress =======
    if 'current' not in ss:
        ss.current = 0
    if 'skipped' not in ss:
        ss.skipped = set()

    if numbers:
        current_index = min(ss.current, len(numbers)-1)
        percent = int(((current_index+1) / len(numbers)) * 100)

        progress_html = f"""
        <div style='margin:8px 0;'><b style='color:#fff;font-size:1.05rem'>Progress</b></div>
        <div style='width:64px;height:64px;margin:auto;position:relative;'>
            <div style='width:64px;height:64px;border-radius:50%;
                background:conic-gradient(#22d3ee {percent}%, #111827 {percent}% 100%);
                display:flex;align-items:center;justify-content:center;box-shadow:0 3px 12px rgba(34,211,238,.25);'>
                <span style='font-size:1.02rem;color:#e5e7eb;font-weight:1000;'>
                    {current_index+1}/{len(numbers)}
                </span>
            </div>
        </div>
        """
        st.markdown(progress_html, unsafe_allow_html=True)

        # current message
        try:
            msg_personal = msg_template.format(
                name=names[current_index] if names else '',
                country=countries[current_index] if countries else '',
                number=numbers[current_index]
            )
        except Exception as e:
            msg_personal = f"⚠️ Template error: {e}"

        message = st.text_area("Message", value=msg_personal, height=160, key="msgboxfinal")
        st.write(f"**Contact:** {current_index+1} / {len(numbers)}")
        info = f'{numbers[current_index]}'
        if mode == "Smart: Personalized Name & Country":
            if names and len(names) > current_index and names[current_index]:
                info += f" — {names[current_index]}"
            if countries and len(countries) > current_index and countries[current_index]:
                info += f" — {countries[current_index]}"
        st.markdown(f"<span class='tag'>{info}</span>", unsafe_allow_html=True)

        # list with active
        items = []
        for i in range(len(numbers)):
            item = f"{i+1}. {numbers[i]}"
            if mode == "Smart: Personalized Name & Country":
                if names and i < len(names) and names[i]:
                    item += f" - {names[i]}"
                if countries and i < len(countries) and countries[i]:
                    item += f" - {countries[i]}"
            css_class = "active" if i == current_index else ""
            items.append(f"<div class='{css_class}'>{item}</div>")
        st.markdown('<div class="k-list">' + "".join(items) + "</div>", unsafe_allow_html=True)

        cols = st.columns([1.1, 1.1, 1.8, 1.1])
        prev_disabled = current_index <= 0
        next_disabled = current_index >= len(numbers)-1
        skip_disabled = numbers[current_index] in ss.skipped

        if cols[0].button("← Prev", disabled=prev_disabled, key="prev"):
            ss.current = max(0, ss.current-1)

        if cols[1].button("Skip", disabled=skip_disabled, key="skip"):
            ss.skipped.add(numbers[current_index])
            if ss.current < len(numbers)-1:
                ss.current += 1

        if cols[2].button("Open WhatsApp", disabled=not message.strip(), key="open"):
            url = build_whatsapp_url(numbers[current_index], message, "web" if platform == "💻 WhatsApp Web" else "mobile")
            st.markdown(
                "<div style='text-align:center; margin-top:6px;'>"
                "<a href='" + url + "' target='_blank' style='font-weight:900; color:#22d3ee; font-size:18px;'>"
                "🚀 Click here if WhatsApp didn't open</a></div>",
                unsafe_allow_html=True
            )
            st.components.v1.html(f"""<script>window.open("{url}", "_blank");</script>""")

        if cols[3].button("Next →", disabled=next_disabled, key="next"):
            ss.current = min(len(numbers)-1, ss.current+1)

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(f"<div class='footer'>✦ Powered by <b>KARIM OTHMAN</b> • {datetime.now().year}</div>", unsafe_allow_html=True)
