import streamlit as st
import urllib.parse

# ----- PAGE & GLOBAL STYLES -----
st.set_page_config(page_title="KARIM | WhatsApp Sender PRO", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@700&family=Open+Sans:wght@400;700&display=swap');
body, [class*="css"] {
  font-family: 'Open Sans', 'Cairo', Arial, sans-serif !important;
}
.stApp {
  background: linear-gradient(135deg, #13a7df 0%, #71e6fc 50%, #aefaf6 100%) fixed !important;
  min-height: 100vh;
}
.glass-box {
  background: rgba(255,255,255,0.68);
  border-radius: 28px;
  box-shadow: 0 8px 44px 0 #b3eafd4a, 0 1.5px 18px #12b5de38;
  backdrop-filter: blur(7.2px);
  -webkit-backdrop-filter: blur(7.2px);
  padding: 34px 22px 18px 22px;
  margin: 32px auto 14px auto;
  max-width: 520px;
  border: 1.6px solid #e0f8fe33;
  animation: floatUp .8s cubic-bezier(.56,.19,.34,.98);
}
@keyframes floatUp {
  0% {transform: translateY(40px) scale(.95); opacity:0;}
  60% {transform: translateY(-9px) scale(1.02);}
  100% {transform: translateY(0) scale(1); opacity:1;}
}
.karim-logo {
  display: flex; align-items: center; justify-content: center;
  font-family: 'Cairo', sans-serif;
  font-size: 2.7rem; font-weight: 900; letter-spacing: 8px;
  margin-bottom: 0.1rem; padding-bottom: 0.5rem;
  text-align: center;
  background: linear-gradient(90deg, #1e86e4 45%, #1bd6c4 90%, #84e9fb 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-fill-color: transparent;
  user-select: none;
  text-shadow: 0 4px 16px #10b7d466;
  filter: drop-shadow(0 1px 8px #48baff70);
  animation: popIn 1.1s cubic-bezier(.31,1.37,.71,1);
}
.karim-logo .whats-icon {
  font-size: 1.9rem; margin-left: 13px; margin-right: -9px;
  filter: drop-shadow(0 2px 10px #16f383b9);
  animation: pulseLogo 2.4s infinite alternate;
}
@keyframes popIn {
  0% {letter-spacing:0px;opacity:0;transform: scale(.5);}
  80% {letter-spacing:13px;transform: scale(1.08);}
  100% {opacity:1;}
}
@keyframes pulseLogo {
  0% {filter:drop-shadow(0 0 3px #1bd6c4b0);}
  100% {filter:drop-shadow(0 0 13px #1bd6c4e0);}
}
.title-pro {
  font-size: 1.18rem;
  margin-bottom: 1.1rem;
  color: #1297e0;
  text-align: center;
  letter-spacing: 1.6px;
  font-family: 'Cairo', 'Open Sans', sans-serif;
  font-weight: bold;
  animation: fadeDown .7s;
}
@keyframes fadeDown {
  0% {opacity:0;transform:translateY(-34px);}
  100% {opacity:1;transform:translateY(0);}
}
.progress-outer {
  margin: 18px auto 6px auto;
  width: 70px; height: 70px; position: relative;
  display: flex; align-items: center; justify-content: center;
}
.progress-circle {
  width: 70px; height: 70px;
  border-radius: 50%;
  background: conic-gradient(#10b7d4 0% {progress}%, #c5f6fd {progress}% 100%);
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 3px 12px #13a7df24;
  position: absolute; top: 0; left: 0;
  animation: popIn 0.7s cubic-bezier(.18,.6,.58,1.2);
}
.progress-num {
  font-size: 1.2rem; color: #0d577e; font-family: 'Cairo',sans-serif;
  font-weight: 900; letter-spacing: 2px;
  z-index: 1;
}
.numbers-list-karim {
  display: flex; flex-direction: column; gap: 2.5px; font-size: 13.2px;
  background: #f6faffb7;
  border-radius: 10px; padding: 8px 10px 8px 14px; margin-bottom: 12px;
  max-height: 90px; overflow-y: auto; color: #397bbf;
  border: 1.1px solid #e5f2fa;
  box-shadow: 0 2px 7px #beeafd1a;
  font-family: 'Open Sans', Cairo, sans-serif;
}
.numbers-list-karim .active {
  background: linear-gradient(90deg,#beeafd 60%,#bffcf9 100%);
  border-radius: 7px;
  font-weight: bold;
  color: #10b7d4;
  font-size: 1.02em;
}
button[kind="primary"], button[data-testid="baseButton-primary"] {
  background: linear-gradient(90deg, #21cdf8 40%, #1de1bb 100%);
  border-radius: 15px !important;
  color: #fff !important;
  font-weight: bold;
  transition: box-shadow 0.19s, transform 0.19s;
  box-shadow: 0 4px 14px #21cdf832;
  border: none !important;
  font-family: 'Cairo', 'Open Sans', sans-serif;
  font-size: 1.04em;
}
button[kind="primary"]:hover, button[data-testid="baseButton-primary"]:hover {
  background: linear-gradient(90deg, #0ca1ce 25%, #4bffc9 100%);
  box-shadow: 0 8px 22px #009be254;
  transform: translateY(-2px) scale(1.045);
}
[data-testid="collapsedControl"] {display: none;}
.footer-karim {
  margin-top: 2.1rem; font-size: 1.1rem; color: #1e86e4;
  text-align: center; letter-spacing: 1.2px;
  font-family: 'Cairo', 'Open Sans', sans-serif;
  opacity: .78;
  font-weight: bold;
  padding-bottom: 13px;
  animation: fadeUp 1.2s;
  text-shadow: 0 1px 7px #beeafd64;
}
@keyframes fadeUp {
  0% {opacity:0;transform:translateY(32px);}
  100% {opacity:1;transform:translateY(0);}
}
</style>
""", unsafe_allow_html=True)

# ----- APP LOGIC -----
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

with st.container():
    st.markdown('<div class="glass-box">', unsafe_allow_html=True)
    st.markdown(
        '<div class="karim-logo">'
        'KARIM <span class="whats-icon">🟢</span>'
        '</div>', unsafe_allow_html=True
    )
    st.markdown('<div class="title-pro">WhatsApp Broadcast Sender</div>', unsafe_allow_html=True)

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

    if 'current' not in st.session_state:
        st.session_state.current = 0
    if 'skipped' not in st.session_state:
        st.session_state.skipped = set()

    # Progress Circle
    if numbers:
        percent = int((st.session_state.current+1) / len(numbers) * 100)
        st.markdown(
            f'''
            <div class="progress-outer">
                <div class="progress-circle" style="background:conic-gradient(#10b7d4 {percent}%, #c5f6fd {percent}% 100%);">
                    <span class="progress-num">{st.session_state.current+1}/{len(numbers)}</span>
                </div>
            </div>
            ''', unsafe_allow_html=True
        )

    if st.button("🔄 Reset Progress"):
        st.session_state.current = 0
        st.session_state.skipped = set()

    if numbers:
        message = st.text_area(
            "Message",
            value=templates[lang_code],
            key="msgbox_"+lang_code,
            help="Edit the message before sending if you wish.",
            height=130,
        )
        st.write(f"**Contact:** {min(st.session_state.current+1, len(numbers))} / {len(numbers)}")
        st.write(
            f'<span style="display:inline-block;padding:7px 19px;background:linear-gradient(90deg,#10b7d4,#15d5bd);color:#fff;'
            'border-radius:28px;font-family:Cairo,sans-serif;font-size:1.13rem;font-weight:bold;'
            'box-shadow:0 1px 7px #21cdf840;margin-bottom:11px;">'
            f'{numbers[st.session_state.current]}</span>',
            unsafe_allow_html=True
        )

        # أرقام القائمة
        st.markdown(
            '<div class="numbers-list-karim">' +
            "".join([
                f"<div class='{ 'active' if i == st.session_state.current else ''}'>{i+1}. {n}</div>"
                for i, n in enumerate(numbers)
            ]) +
            "</div>", unsafe_allow_html=True
        )

        cols = st.columns([1.2, 1.2, 1.6, 1.2])
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
                f"<a href='{url}' target='_blank' style='font-weight:bold; color:#009be2; font-size:18px; letter-spacing:.5px;'>"
                "🚀 Click here if WhatsApp didn't open automatically</a></div>", unsafe_allow_html=True
            )
            st.components.v1.html(f"""<script>window.open("{url}", "_blank");</script>""")

        if cols[3].button("Next →", disabled=next_disabled, key="next"):
            if st.session_state.current < len(numbers)-1:
                st.session_state.current += 1

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="footer-karim">✦ Powered by <span style="font-family:Cairo,sans-serif;letter-spacing:2.3px;color:#1092d4;">Karim OTHMAN 😍</span> &copy; 2025</div>', unsafe_allow_html=True)
