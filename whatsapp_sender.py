import streamlit as st
import pandas as pd
import urllib.parse

st.set_page_config(page_title="KARIM | WhatsApp Sender PRO", layout="centered")

# --- Material Design Colors ---
PRIMARY = "#1976d2"        # Blue 700
PRIMARY_DARK = "#115293"   # Blue 900
PRIMARY_LIGHT = "#63a4ff"  # Blue 400
ACCENT = "#26c6da"         # Cyan 400
BG = "#f5f7fa"             # Background grey
SURFACE = "#fff"
SHADOW = "0 8px 40px 0 #1976d22a, 0 1.5px 10px #26c6da22"
TEXT_MAIN = "#212121"      # Main dark text
TEXT_FAINT = "#636e72"     # Muted text

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&family=Cairo:wght@700&display=swap');
html, body, [class*="css"] {{
  font-family: 'Roboto', 'Cairo', Arial, sans-serif !important;
  background: {BG} !important;
  color: {TEXT_MAIN};
}}
.stApp {{
  background: {BG} !important;
  min-height: 100vh;
}}
.glass-box {{
  background: {SURFACE};
  border-radius: 18px;
  box-shadow: {SHADOW};
  padding: 32px 18px 16px 18px;
  margin: 28px auto 16px auto;
  max-width: 490px;
  border: 1.5px solid #e3e8ee;
  animation: fadeInCard .8s cubic-bezier(.56,.19,.34,.98);
}}
@keyframes fadeInCard {{
  0% {{opacity:0; transform: scale(.96) translateY(40px);}}
  100% {{opacity:1; transform: scale(1) translateY(0);}}
}}
.karim-logo {{
  font-family: 'Cairo', 'Roboto', sans-serif;
  font-size: 2.1rem; font-weight: 900; letter-spacing: 7px;
  margin-bottom: .4rem; text-align: center;
  background: linear-gradient(90deg, {PRIMARY} 35%, {ACCENT} 90%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text; text-fill-color: transparent;
  user-select: none;
  text-shadow: 0 3px 15px #1976d22e;
  animation: popIn 1.1s cubic-bezier(.31,1.37,.71,1);
}}
@keyframes popIn {{
  0% {{letter-spacing:0px;opacity:0;transform: scale(.7);}}
  80% {{letter-spacing:11px;transform: scale(1.04);}}
  100% {{opacity:1;}}
}}
.title-pro {{
  font-size: 1.18rem;
  margin-bottom: 1.1rem;
  color: {PRIMARY};
  text-align: center; letter-spacing: 1.4px;
  font-family: 'Cairo', 'Roboto', sans-serif;
  font-weight: bold;
  animation: fadeDown .7s;
}}
@keyframes fadeDown {{
  0% {{opacity:0;transform:translateY(-22px);}}
  100% {{opacity:1;transform:translateY(0);}}
}}
.numbers-list-karim {{
  display: flex; flex-direction: column; gap: 2.5px; font-size: 13.8px;
  background: #f7fafd; border-radius: 7px; padding: 8px 10px 8px 11px; margin-bottom: 14px;
  max-height: 85px; overflow-y: auto; color: {PRIMARY_DARK};
  border: 1.1px solid #e3e8ee;
  box-shadow: 0 2px 9px #1976d219;
  font-family: 'Roboto', 'Cairo', sans-serif;
}}
.numbers-list-karim .active {{
  background: linear-gradient(90deg,#e3f2fd 55%,#b3ecf7 100%);
  border-radius: 6px; font-weight: bold; color: {PRIMARY};
  font-size: 1.03em; border-left: 4.2px solid {ACCENT}; padding-left: 3px;
}}
button[kind="primary"], button[data-testid="baseButton-primary"] {{
  background: linear-gradient(90deg, {PRIMARY} 35%, {ACCENT} 100%);
  border-radius: 12px !important; color: #fff !important; font-weight: bold;
  box-shadow: 0 4px 14px #26c6da30;
  border: none !important; font-family: 'Roboto', 'Cairo', sans-serif;
  font-size: 1.07em; letter-spacing:.3px;
  transition: box-shadow 0.18s, transform 0.18s;
}}
button[kind="primary"]:hover, button[data-testid="baseButton-primary"]:hover {{
  background: linear-gradient(90deg, {ACCENT} 15%, {PRIMARY} 100%);
  box-shadow: 0 8px 22px #1976d248;
  transform: translateY(-2px) scale(1.045);
}}
[data-testid="collapsedControl"] {{display: none;}}
.footer-karim {{
  margin-top: 2.0rem; font-size: 1.05rem; color: {PRIMARY_DARK};
  text-align: center; letter-spacing: 1.0px;
  font-family: 'Cairo', 'Roboto', sans-serif;
  opacity: .85; font-weight: bold; padding-bottom: 12px;
  animation: fadeUp 1.2s; text-shadow: 0 1px 6px #1976d21a;
}}

/* *** التباين العالي: *** */
.stRadio label, .stRadio div, .stRadio span, .stRadio p,
.stTextInput label, .stTextArea label,
.stMarkdown, .stSelectbox label, .stInfo, .stFileUploader label, .stDataFrame label {{
  color: #222 !important;
  font-weight: 600 !important;
  letter-spacing: .1px;
}}

.stTextInput input, .stTextArea textarea {{
  background: #fff !important;
  color: #222 !important;
}}

.stButton>button {{
  box-shadow: 0 4px 16px #1976d240;
}}
@keyframes fadeUp {{0% {{opacity:0;transform:translateY(28px);}}100% {{opacity:1;transform:translateY(0);}}}}
</style>
""", unsafe_allow_html=True)

# ==== TEMPLATES ====
templates = {
    'en': """Hello 👋

We are the Sales Department at EUROSWEET GIDA LTD. ŞTİ. (Istanbul – Turkey).

We specialize in producing high-quality snacks such as:
🍪 Croissants, Cakes, Biscuits, Donuts, Jelly, and Wafers.

We're always eager to connect with reliable partners and explore new markets together. 🤝

If you are interested, we are happy to share our catalog, price list, and discuss how we can work together.

Looking forward to your reply!

Best regards,
Sales Department""",
    'ar': """مرحبًا 👋

نحن قسم المبيعات في شركة EUROSWEET GIDA LTD. ŞTİ. (إسطنبول - تركيا).

نحن متخصصون في إنتاج سناكات عالية الجودة مثل:
🍪 الكرواسون، الكيك، البسكويت، الدونات، الجيلي، والويفر.

نسعى دائمًا للتواصل مع شركاء موثوقين واستكشاف أسواق جديدة معًا 🤝

إذا كنت مهتمًا، يسعدنا أن نرسل لك الكتالوج وقائمة الأسعار ومناقشة فرص التعاون المشترك.

بانتظار ردكم الكريم!

تحياتنا،
قسم المبيعات""",
    'tr': """Merhaba 👋

Biz EUROSWEET GIDA LTD. ŞTİ. (İstanbul – Türkiye) Satış Departmanıyız.

Aşağıdaki yüksek kaliteli atıştırmalıkları üretiyoruz:
🍪 Kruvasan, Kek, Bisküvi, Donut, Jöle ve Gofret.

Her zaman güvenilir ortaklarla bağlantı kurmak ve yeni pazarları birlikte keşfetmek isteriz. 🤝

İlgileniyorsanız, size kataloğumuzu ve fiyat listemizi paylaşabilir, iş birliğini konuşabiliriz.

Cevabınızı dört gözle bekliyoruz!

Saygılarımızla,
Satış Departmanı""",
    'fr': """Bonjour 👋

Nous sommes le département commercial de EUROSWEET GIDA LTD. ŞTİ. (Istanbul – Turquie).

Nous sommes spécialisés dans la production de snacks de haute qualité tels que :
🍪 Croissants, gâteaux, biscuits, donuts, gelées et gaufrettes.

Nous sommes toujours prêts à collaborer avec des partenaires fiables et à explorer de nouveaux marchés ensemble. 🤝

Si vous êtes intéressé, nous serions heureux de partager notre catalogue, notre liste de prix et de discuter des opportunités de collaboration.

Dans l’attente de votre réponse !

Cordialement,
Département des ventes""",
    'es': """Hola 👋

Somos el Departamento de Ventas de EUROSWEET GIDA LTD. ŞTİ. (Estambul – Turquía).

Estamos especializados en la producción de snacks de alta calidad como:
🍪 Cruasanes, pasteles, galletas, donas, gelatinas y barquillos.

Siempre estamos dispuestos a conectar con socios confiables y explorar juntos nuevos mercados. 🤝

Si está interesado, estaremos encantados de compartir nuestro catálogo, lista de precios y hablar sobre cómo podemos colaborar.

¡Esperamos su respuesta!

Saludos cordiales,
Departamento de Ventas"""
}

# ==== UI ====
with st.container():
    st.markdown('<div class="glass-box">', unsafe_allow_html=True)
    st.markdown('<div class="karim-logo">KARIM</div>', unsafe_allow_html=True)
    st.markdown('<div class="title-pro">WhatsApp Broadcast Sender</div>', unsafe_allow_html=True)

    mode = st.radio(
        "Choose mode:",
        ["Simple: Numbers Only", "Smart: Personalized Name & Country"],
        horizontal=True,
        key="mode"
    )

    if mode == "Simple: Numbers Only":
        lang = st.radio("Language", [
            "🇬🇧 English", "🇸🇦 العربية", "🇹🇷 Türkçe", "🇫🇷 Français", "🇪🇸 Español"
        ], horizontal=True, key="lang_radio")
        lang_code = {
            "🇬🇧 English": "en",
            "🇸🇦 العربية": "ar",
            "🇹🇷 Türkçe": "tr",
            "🇫🇷 Français": "fr",
            "🇪🇸 Español": "es"
        }[lang]
        platform = st.radio("Send using", ["💻 WhatsApp Web", "📱 WhatsApp App"], horizontal=True, key="plat_radio")
        platform_type = "web" if platform == "💻 WhatsApp Web" else "mobile"
        numbers_raw = st.text_area("Numbers (comma/newline separated)", placeholder="Paste numbers, comma or newline separated")
        numbers = [
            n.strip().replace("-", "").replace(" ", "")
            for n in numbers_raw.replace(",", "\n").split("\n")
            if n.strip() and n.strip().replace("-", "").replace(" ", "").isdigit() and len(n.strip().replace("-", "").replace(" ", "")) >= 8
        ]
        names = [''] * len(numbers)
        countries = [''] * len(numbers)
        msg_template = templates[lang_code]
    else:
        platform = st.radio("Send using", ["💻 WhatsApp Web", "📱 WhatsApp App"], horizontal=True, key="plat_radio2")
        platform_type = "web" if platform == "💻 WhatsApp Web" else "mobile"
        st.info("You can upload a CSV file (number,name,country) or enter data manually 👇")
        data_opt = st.radio("Input method:", ["Upload CSV file", "Manual entry"], horizontal=True, key="smart_input")
        df = None
        if data_opt == "Upload CSV file":
            uploaded_file = st.file_uploader("Upload CSV (number,name,country)", type=["csv"])
            if uploaded_file is not None:
                df = pd.read_csv(uploaded_file).dropna(subset=["number"])
                df = df.astype(str)
                st.success(f"{len(df)} contacts loaded.")
        else:
            st.info("Enter data manually (add/remove rows as needed):")
            example_data = pd.DataFrame({
                'number': ['201111223344', '971500000001'],
                'name': ['Mohamed', 'Ahmed'],
                'country': ['Egypt', 'UAE']
            })
            df = st.data_editor(
                example_data,
                num_rows="dynamic",
                use_container_width=True,
                key="editor"
            )
            df = df.astype(str)
        if df is not None and not df.empty:
            numbers = df['number'].tolist()
            names = df['name'].tolist() if 'name' in df.columns else ['']*len(df)
            countries = df['country'].tolist() if 'country' in df.columns else ['']*len(df)
        else:
            numbers, names, countries = [], [], []
        msg_template = st.text_area(
            "Write message template (use {name}, {country}, {number}):",
            value="Hello {name} from {country}, we have new products for the {country} market!",
            height=120,
            key="smart_template"
        )

    if 'current' not in st.session_state:
        st.session_state.current = 0
    if 'skipped' not in st.session_state:
        st.session_state.skipped = set()

    if numbers:
        percent = int((st.session_state.current+1) / len(numbers) * 100)
        st.markdown(
            f'''
            <div style="margin-bottom:6px;"><b style="color:{PRIMARY_DARK};font-size:1.05rem">Progress:</b></div>
            <div class="progress-outer">
                <div class="progress-circle" style="background:conic-gradient({ACCENT} {percent}%, #e3f2fd {percent}% 100%);">
                    <span class="progress-num">{st.session_state.current+1}/{len(numbers)}</span>
                </div>
            </div>
            ''', unsafe_allow_html=True
        )

    if st.button("🔄 Reset Progress"):
        st.session_state.current = 0
        st.session_state.skipped = set()

    if numbers:
        # Personalized msg for smart mode
        try:
            msg_personal = msg_template.format(
                name=names[st.session_state.current] if names else '',
                country=countries[st.session_state.current] if countries else '',
                number=numbers[st.session_state.current]
            )
        except Exception as e:
            msg_personal = "⚠️ Please check your template or data"
        message = st.text_area(
            "Message",
            value=msg_personal,
            key="msgboxfinal",
            help="Edit before sending if you want",
            height=120,
        )
        st.write(f"**Contact:** {min(st.session_state.current+1, len(numbers))} / {len(numbers)}")
        info = f'{numbers[st.session_state.current]}'
        if mode == "Smart: Personalized Name & Country" and names and countries:
            info += f" — {names[st.session_state.current]} — {countries[st.session_state.current]}"
        st.write(
            f'<span style="display:inline-block;padding:7px 19px;background:linear-gradient(90deg,#e3f2fd,#b3ecf7);color:{PRIMARY_DARK};'
            'border-radius:20px;font-family:Roboto,sans-serif;font-size:1.08rem;font-weight:bold;'
            'box-shadow:0 1px 7px #1976d217;margin-bottom:10px;">'
            f'{info}</span>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="numbers-list-karim">' +
            "".join([
                f"<div class='{ 'active' if i == st.session_state.current else ''}'>{i+1}. {numbers[i]}{(' - ' + names[i]) if (mode=='Smart: Personalized Name & Country' and names and names[i]) else ''}{(' - ' + countries[i]) if (mode=='Smart: Personalized Name & Country' and countries and countries[i]) else ''}</div>"
                for i in range(len(numbers))
            ]) +
            "</div>", unsafe_allow_html=True
        )

        cols = st.columns([1.2, 1.2, 1.7, 1.2])
        prev_disabled = st.session_state.current <= 0
        next_disabled = st.session_state.current >= len(numbers)-1
        skip_disabled = numbers[st.session_state.current] in st.session_state.skipped

        if cols[0].button("← Prev", disabled=prev_disabled, key="prev"):
            if st.session_state.current > 0:
                st.session_state.current -= 1

        if cols[1].button("Skip", disabled=skip_disabled, key="skip"):
            st.session_state.skipped.add(numbers[st.session_state.current])
            if st.session_state.current < len(numbers)-1:
                st.session_state.current += 1

        if cols[2].button("Open WhatsApp", disabled=not message.strip(), key="open"):
            msg_encoded = urllib.parse.quote(message.strip())
            num = numbers[st.session_state.current]
            if platform_type == "web":
                url = f"https://web.whatsapp.com/send?phone={num}&text={msg_encoded}"
            else:
                url = f"https://wa.me/{num}?text={msg_encoded}"
            st.markdown(
                f"<div style='text-align:center; margin-top:6px;'>"
                f"<a href='{url}' target='_blank' style='font-weight:bold; color:{PRIMARY}; font-size:18px; letter-spacing:.5px;'>"
                "🚀 Click here if WhatsApp didn't open automatically</a></div>", unsafe_allow_html=True
            )
            st.components.v1.html(f"""<script>window.open("{url}", "_blank");</script>""")

        if cols[3].button("Next →", disabled=next_disabled, key="next"):
            if st.session_state.current < len(numbers)-1:
                st.session_state.current += 1

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(f'<div class="footer-karim">✦ Powered by <span style="font-family:Cairo,sans-serif;letter-spacing:2.3px;color:{ACCENT};">Karim OTHMAN 😍</span> &copy; 2025</div>', unsafe_allow_html=True)
