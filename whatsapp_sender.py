# =============================================================================
# KARIM | WhatsApp Sender PRO — Revamped (2025)
# =============================================================================
# هذا الملف يقدّم أداة إرسال رسائل واتساب شبه-جماعية مع واجهة Streamlit محسّنة.
# يحافظ على كل ميزات الكود الأصلي ويضيف:
# - هيدر احترافي (Glass + Animated Gradient)
# - ثيم داكن/فاتح + CSS مُهيكل
# - بنية شيفرة أوضح + تعليقات تفصيلية
# - تصدير/استيراد جلسة (Session Export/Import)
# - إزالة تكرارات، حد أدنى لطول الرقم، كود دولة افتراضي
# - أوضاع Simple و Smart (CSV/Excel/Data Editor)
# - قوالب رسائل مع متغيرات {name}, {country}, {number}, {idx}
# - فتح واتساب (Web/App) لكل جهة اتصال
# - شريط تقدم + Prev/Next/Skip/Jump
# - تنزيل ملفات TXT/CSV للنتائج أو الرسائل
#
# ملاحظات:
# - تم الاهتمام بتوليد مفاتيح (key=) فريدة لعناصر التحميل لتجنّب StreamlitDuplicateElementId
# - جميع الأجزاء موثقة بعناوين واضحة لتسهيل الرجوع والتعديل
# =============================================================================

# =========================
# 1) Imports / المكتبات
# =========================
import streamlit as st
import pandas as pd
import urllib.parse
import re
import json
from io import StringIO

# ================================
# 2) Page Config / إعدادات الصفحة
# ================================
# - ترويسة الصفحة (title)
# - عرض الصفحة (wide)
# - حالة الشريط الجانبي
st.set_page_config(
    page_title="KARIM | WhatsApp Sender PRO",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# 3) Constants / Templates / الإعدادات الثابتة
# ============================================

# نمط المتغيرات المسموح استخدامها داخل القوالب
VAR_PATTERN = re.compile(r"\{(name|country|number|idx)\}")

# قوالب جاهزة لكل لغة (يمكن التعديل والإضافة)
LANG_TEMPLATES = {
    'en': """Hello {name} 👋

We are the Sales Department at EUROSWEET GIDA LTD. ŞTİ. (Istanbul – Turkey).

We specialize in producing high-quality snacks such as:
🍪 Croissants, Cakes, Biscuits, Donuts, Jelly, and Wafers.

We're always eager to connect with reliable partners and explore new markets together. 🤝

If you are interested, we are happy to share our catalog, price list, and discuss how we can work together.

Looking forward to your reply!

Best regards,
Sales Department""",
    'ar': """مرحبًا {name} 👋

نحن قسم المبيعات في شركة EUROSWEET GIDA LTD. ŞTİ. (إسطنبول - تركيا).

نحن متخصصون في إنتاج سناكات عالية الجودة مثل:
🍪 الكرواسون، الكيك، البسكويت، الدونات، الجيلي، والويفر.

نسعى دائمًا للتواصل مع شركاء موثوقين واستكشاف أسواق جديدة معًا 🤝

إذا كنت مهتمًا، يسعدنا أن نرسل لك الكتالوج وقائمة الأسعار ومناقشة فرص التعاون المشترك.

بانتظار ردكم الكريم!

تحياتنا،
قسم المبيعات""",
    'tr': """Merhaba {name} 👋

Biz EUROSWEET GIDA LTD. ŞTİ. (İstanbul – Türkiye) Satış Departmanıyız.

Aşağıdaki yüksek kaliteli atıştırmalıkları üretiyoruz:
🍪 Kruvasan, Kek, Bisküvi, Donut, Jöle ve Gofret.

Her zaman güvenilir ortaklarla bağlantı kurmak ve yeni pazarları birlikte keşfetmek isteriz. 🤝

İlgileniyorsanız, kataloğumuzu ve fiyat listemizi paylaşabilir, iş birliğini konuşabiliriz.

Saygılarımızla,
Satış Departmanı""",
    'fr': """Bonjour {name} 👋

Nous sommes le département commercial de EUROSWEET GIDA LTD. ŞTİ. (Istanbul – Turquie).

Nous produisons des snacks de haute qualité :
🍪 Croissants, gâteaux, biscuits, donuts, gelées et gaufrettes.

Nous serions ravis d'échanger et d'explorer de nouveaux marchés ensemble. 🤝

Si intéressé, nous partageons volontiers notre catalogue et nos tarifs.

Cordialement,
Département des ventes""",
    'es': """Hola {name} 👋

Somos el Departamento de Ventas de EUROSWEET GIDA LTD. ŞTİ. (Estambul – Turquía).

Producimos snacks de alta calidad como:
🍪 Cruasanes, pasteles, galletas, donas, gelatinas y barquillos.

Nos encanta colaborar con socios confiables y abrir nuevos mercados. 🤝

Si le interesa, le compartimos el catálogo y la lista de precios.

Saludos,
Departamento de Ventas""",
}

# للاختيار من الـ Radio (واجهة المستخدم)
LANG_CHOICES = {
    "🇬🇧 English": "en",
    "🇸🇦 العربية": "ar",
    "🇹🇷 Türkçe": "tr",
    "🇫🇷 Français": "fr",
    "🇪🇸 Español": "es",
}

# =====================================
# 4) Utilities / دوال الأدوات العامة
# =====================================

def extract_numbers(text: str) -> list[str]:
    """
    استخراج الأرقام من نص خام (يفصل بفواصل/سطر جديد) ويزيل أي محارف غير رقمية.
    - يحترم الحد الأدنى لطول الرقم من st.session_state.min_length
    - يعيد قائمة أرقام نظيفة كسلاسل نصية
    """
    if not text:
        return []
    lines = text.replace(",", "\n").splitlines()
    out = []
    for line in lines:
        digits = re.sub(r"\D", "", line)  # أزل كل ما ليس رقماً
        if len(digits) >= st.session_state.get("min_length", 8):
            out.append(digits)
    return out

def clean_number(n: str) -> str:
    """
    ينظف رقم واحد فقط — يبقي أرقام 0-9 ويحذف غيرها.
    """
    return re.sub(r"\D", "", str(n or ""))

def to_e164(num: str, default_cc: str) -> str:
    """
    تحويل مبسّط نحو شكل E.164:
    - إن لم يبدأ الرقم بكود دولي، أضف الكود الافتراضي default_cc.
    - لا يضيف '+'، يكتفي بضم الكود والرقم (يناسب لينك whatsapp).
    - مثال: default_cc='20' و num='0111122334' -> '200111122334'
    """
    num = clean_number(num)
    if not num:
        return ""
    cc = re.sub(r"\D", "", default_cc or "")
    if cc and not num.startswith(cc) and not num.startswith("00") and not num.startswith("+"):
        num = num.lstrip("0")
        return f"{cc}{num}"
    return num

def format_message(tpl: str, name: str, country: str, number: str, idx: int) -> str:
    """
    يُعبّئ متغيرات {name}, {country}, {number}, {idx} داخل القالب tpl.
    """
    safe = tpl or ""
    return safe.format(name=name or "", country=country or "", number=number or "", idx=idx)

def copy_to_clipboard(label: str, content: str):
    """
    زر نسخ لل Clipboard باستخدام HTML/JS مضمّن.
    مهم: لا يستخدم st.button حتى لا يصير تضارب مفاتيح.
    """
    btn_id = f"copy_{abs(hash(label+content))}"
    st.markdown(
        f"""
        <button id="{btn_id}" style="background:linear-gradient(90deg,#22d3ee,#06b6d4);border:none;border-radius:10px;padding:8px 16px;color:#0b1220;font-weight:800;cursor:pointer;box-shadow:0 6px 18px #06b6d433;margin:4px 0;">{label}</button>
        <script>
        const el_{btn_id} = document.getElementById('{btn_id}');
        if (el_{btn_id}) {{
            el_{btn_id}.onclick = () => {{
                navigator.clipboard.writeText({json.dumps(content)});
                el_{btn_id}.innerText = 'Copied!';
                setTimeout(()=> el_{btn_id}.innerText = {json.dumps(label)}, 1100);
            }}
        }}
        </script>
        """,
        unsafe_allow_html=True,
    )

def download_bytes(name: str, text: str, key: str | None = None):
    """
    زر تنزيل ملف نصّي آمن من ناحية تكرار المفاتيح:
    - إذا كان هناك زرين بنفس الـlabel داخل الصفحة، يجب توفير key فريد.
    - إن لم يمرّر key، سيتم توليده تلقائياً من اسم الملف ومحتواه.
    """
    key = key or f"dl-{name}-{abs(hash(text))}"
    st.download_button(
        label=f"⬇️ Download {name}",
        data=text.encode("utf-8"),
        file_name=name,
        mime="text/plain",
        key=key,
    )

# ======================================
# 5) Theme Defaults / الثيم والقيم الأولية
# ======================================
# تهيئة قيم session_state الافتراضية إذا لم تكن موجودة مسبقاً
if "theme_dark" not in st.session_state:
    st.session_state.theme_dark = True
if "min_length" not in st.session_state:
    st.session_state.min_length = 8
if "dedupe" not in st.session_state:
    st.session_state.dedupe = True
if "default_cc" not in st.session_state:
    st.session_state.default_cc = ""
if "rate_ms" not in st.session_state:
    st.session_state.rate_ms = 0

# ==========================
# 6) CSS Themes / أنماط CSS
# ==========================
# ثيمين: داكن وفاتح — يمكن التبديل من الشريط الجانبي
DARK_CSS = """
<style>
:root{--bg:#0b0f19;--bg2:#0f172a;--card:rgba(255,255,255,.05);--cardb:rgba(255,255,255,.1);--tx:#e5e9f0;--mut:#9fb2c8;--cy1:#22d3ee;--cy2:#06b6d4;--bl:#60a5fa;}
.stApp{background:radial-gradient(1200px 700px at 15% -10%, #111827 10%, var(--bg) 45%, #000 100%) fixed!important;color:var(--tx)!important;font-family:'Inter',system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif}
.block-container{padding-top:18px;padding-bottom:10px}
.card{background:var(--card);border:1px solid var(--cardb);border-radius:16px;box-shadow:0 16px 50px rgba(0,0,0,.30)}
.h1{font-size:2.2rem;font-weight:900;letter-spacing:.22em;text-align:center;margin:2px 0 4px;background:linear-gradient(90deg,var(--cy1),#7dd3fc);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.h2{font-size:1.04rem;text-align:center;color:#9cc9ff;font-weight:800;margin-top:0}
.badge{display:inline-block;padding:6px 10px;border-radius:999px;border:1px solid var(--cardb);background:rgba(255,255,255,.06);font-weight:800;color:#9cc9ff;}
.label{color:#a5b4fc;font-weight:800;font-size:1.03em;margin:.3rem 0 .2rem 0;display:block}
input, textarea, .stTextInput>div>input,.stTextArea>div>textarea{border-radius:10px!important;background:#0b1220!important;color:#e5e9f0!important;border:1.6px solid #23314b;font-size:1.02em;font-weight:600;box-shadow:0 2px 7px #0004}
input:focus,textarea:focus{border:2px solid var(--cy1)!important;background:#0f172a!important}
.stButton>button{background:linear-gradient(90deg,var(--cy2),var(--cy1));border:none;border-radius:10px!important;color:#08111f!important;font-weight:900;box-shadow:0 10px 26px #06b6d433}
.stButton>button:hover{transform:translateY(-1px) scale(1.02)}
.klist{display:flex;flex-direction:column;gap:2px;background:#0b1220;border:1px solid #1f2b40;border-radius:10px;padding:6px 9px;color:#cfe8ff;max-height:150px;overflow:auto}
.kitem{padding:2px 6px}
.kitem.active{background:linear-gradient(90deg,#0ea5e980,#22d3ee60);border-left:4px solid #7dd3fc;border-radius:8px;color:#051423;font-weight:800}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.stat{background:#0b1220;border:1px solid #1f2b40;border-radius:10px;padding:10px;text-align:center}
</style>
"""

LIGHT_CSS = """
<style>
:root{--bg:#f6fbff;--bg2:#ffffff;--card:#ffffff;--cardb:#e6eef8;--tx:#0f172a;--mut:#475569;--cy1:#2563eb;--cy2:#38bdf8;--bl:#0ea5e9}
.stApp{background:linear-gradient(120deg,#f6fbff 85%,#e0e7ef 100%) fixed!important;color:var(--tx)!important;font-family:'Inter',system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif}
.block-container{padding-top:18px;padding-bottom:10px}
.card{background:var(--card);border:1.2px solid var(--cardb);border-radius:16px;box-shadow:0 7px 27px rgba(36,44,76,.11),0 1px 5px #38bdf810}
.h1{font-size:2.1rem;font-weight:900;letter-spacing:.22em;text-align:center;margin:2px 0 4px;background:linear-gradient(90deg,#2563eb 45%,#38bdf8 70%,#22d3ee 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.h2{font-size:1rem;text-align:center;color:#2563eb;font-weight:800;margin-top:0}
.badge{display:inline-block;padding:6px 10px;border-radius:999px;border:1px solid var(--cardb);background:#f1f7fd;font-weight:900;color:#2563eb}
.label{color:#2563eb;font-weight:900;font-size:1.03em;margin:.3rem 0 .2rem 0;display:block}
input, textarea, .stTextInput>div>input,.stTextArea>div>textarea{border-radius:9px!important;background:#f4f8fb!important;color:#17213d!important;border:1.5px solid #bcd0ee;font-size:1.02em;font-weight:600;box-shadow:0 2px 7px #38bdf810}
input:focus,textarea:focus{border:2px solid #38bdf8!important;background:#fff!important}
.stButton>button{background:linear-gradient(90deg,#2563eb,#38bdf8);border:none;border-radius:9px!important;color:#fff!important;font-weight:900;box-shadow:0 10px 20px #2563eb22}
.klist{display:flex;flex-direction:column;gap:2px;background:#f1f7fd;border:1px solid #e5eaf7;border-radius:8px;padding:6px 9px;color:#2563eb;max-height:150px;overflow:auto}
.kitem{padding:2px 6px}
.kitem.active{background:linear-gradient(90deg,#38bdf849 60%,#22d3ee80 100%);border-left:4px solid #2563eb;border-radius:7px;color:#fff;font-weight:800}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.stat{background:#f6fbff;border:1px solid #e5eaf7;border-radius:10px;padding:10px;text-align:center}
</style>
"""

# حقن الـCSS حسب الثيم الحالي
st.markdown(DARK_CSS if st.session_state.theme_dark else LIGHT_CSS, unsafe_allow_html=True)

# ======================================================
# 7) Header Component (Pro) / الهيدر الاحترافي المتحرك
# ======================================================
# CSS خاص بالهيدر الاحترافي (Glass + Animated Gradient Border)
HEADER_CSS = """
<style>
.pro-header {
  position: relative;
  margin: 6px 0 14px 0;
  border-radius: 18px;
  padding: 22px 18px;
  overflow: hidden;
  --g1: var(--cy1, #22d3ee);
  --g2: var(--bl,  #60a5fa);
  --bgc: rgba(255,255,255,.06);
  --bdc: rgba(255,255,255,.12);
}
.pro-header.light { --bgc:#ffffff; --bdc:#e6eef8; }
.pro-header::before {
  content: "";
  position: absolute; inset: -2px;
  background: conic-gradient(from 160deg, var(--g1), var(--g2), var(--g1));
  filter: blur(14px); opacity: .38;
  animation: spin 9.5s linear infinite;
}
.pro-header::after {
  content: "";
  position: absolute; inset: 0; border-radius: 18px;
  background: var(--bgc);
  border: 1px solid var(--bdc);
  box-shadow: 0 18px 45px rgba(0,0,0,.18);
  backdrop-filter: saturate(140%) blur(10px);
}
@keyframes spin { to { transform: rotate(1turn); } }

.pro-inner { position: relative; z-index: 2; }
.pro-top {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center; gap: 14px;
}
.brand { display:flex; align-items:center; gap:12px; }
.brand-badge {
  width: 52px; height: 52px; border-radius: 14px;
  background: linear-gradient(135deg, var(--g1), var(--g2));
  display:flex; align-items:center; justify-content:center;
  font-weight: 900; color: #051423; letter-spacing: 1.5px;
  box-shadow: 0 12px 30px rgba(34,211,238,.25);
  user-select:none;
}
.brand-title { line-height:1.05; }
.brand-title .t1 {
  font-size: 1.95rem; font-weight: 900; letter-spacing: .14em;
  background: linear-gradient(90deg, var(--g1), var(--g2));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.brand-title .t2 { font-size: .96rem; font-weight: 800; opacity: .9; }
.pro-right { display:flex; gap:8px; flex-wrap:wrap; justify-content:flex-end; }
.chip {
  display:inline-flex; align-items:center; gap:6px;
  padding:6px 10px; border-radius: 999px;
  font-weight: 800; font-size: .86rem;
  border: 1px solid var(--bdc);
  background: rgba(255,255,255,.08);
}
.light .chip { background:#f5f8ff; color:#0f172a; }
.chip .dot { width: 8px; height: 8px; border-radius: 50%; background: var(--g1); }
.pro-bottom { margin-top: 10px; display:flex; align-items:center; gap:10px; flex-wrap:wrap; }
.k-pill {
  padding:7px 12px; border-radius: 999px; border: 1px dashed var(--bdc);
  font-weight: 700; font-size: .84rem; opacity: .9;
}
.pro-links a {
  text-decoration:none; font-weight:900; padding:8px 12px; border-radius: 10px;
  background: linear-gradient(90deg, var(--g2), var(--g1)); color:#08111f !important;
  box-shadow: 0 10px 22px rgba(6,182,212,.25);
}
.pro-links a:hover { transform: translateY(-1px); }
@media (max-width: 880px){
  .pro-top { grid-template-columns: 1fr; row-gap: 8px; }
  .pro-right { justify-content:flex-start; }
}
</style>
"""
st.markdown(HEADER_CSS, unsafe_allow_html=True)

def render_pro_header(
    title: str = "K A R I M",
    subtitle: str = "WhatsApp Sender PRO — Revamped",
    chips: list[str] | None = None,
    light: bool | None = None,
):
    """
    يرسم الهيدر الاحترافي مع شارات (chips) ومعلومات ديناميكية من الإعدادات.
    - يأخذ في الاعتبار الثيم الحالي: light/dark
    - يعرض إعداداتك الحالية: Default CC, De-duplicate, Min length
    """
    if light is None:
        light = not st.session_state.get("theme_dark", True)

    cc = st.session_state.get("default_cc", "") or "—"
    dedupe = "On" if st.session_state.get("dedupe", True) else "Off"
    minlen = st.session_state.get("min_length", 8)

    chips = chips or ["Reliable", "Fast", "Clean"]
    header_cls = "pro-header light" if light else "pro-header"
    chips_html = "".join([f"<span class='chip'><span class='dot'></span>{c}</span>" for c in chips])

    st.markdown(
        f"""
        <div class="{header_cls}">
          <div class="pro-inner">
            <div class="pro-top">
              <div class="brand">
                <div class="brand-badge">WA</div>
                <div class="brand-title">
                  <div class="t1">{title}</div>
                  <div class="t2">{subtitle}</div>
                </div>
              </div>
              <div></div>
              <div class="pro-right">
                {chips_html}
              </div>
            </div>
            <div class="pro-bottom">
              <div class="k-pill">Default CC: <b>{cc}</b></div>
              <div class="k-pill">De-duplicate: <b>{dedupe}</b></div>
              <div class="k-pill">Min length: <b>{minlen}</b></div>
              <div class="pro-links"><a href="https://eurosweet.com.tr" target="_blank">EUROSWEET Catalog ↗</a></div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ===================================================
# 8) Sidebar / الشريط الجانبي — إعدادات + جلسة
# ===================================================
with st.sidebar:
    # عنوان جانبي بسيط (اختياري، لأن الهيدر الرئيسي موجود بالأعلى)
    st.markdown("<div class='h1'>KARIM</div>", unsafe_allow_html=True)
    st.markdown("<div class='h2'>WhatsApp Broadcast Sender</div>", unsafe_allow_html=True)

    # تبديل الثيم
    theme = st.toggle("🌗 Dark Mode", value=st.session_state.theme_dark, help="Switch theme")
    st.session_state.theme_dark = theme

    # إعدادات عامة — تؤثر على التنظيف والتطبيع
    st.markdown("<span class='label'>Global Settings</span>", unsafe_allow_html=True)
    st.session_state.default_cc = st.text_input(
        "Default country code (e.g. 90, 971, 20)",
        value=st.session_state.default_cc
    )
    st.session_state.min_length = st.number_input(
        "Min phone length", min_value=6, max_value=16,
        value=st.session_state.min_length, step=1
    )
    st.session_state.dedupe = st.checkbox(
        "Remove duplicates", value=st.session_state.dedupe
    )
    st.session_state.rate_ms = st.number_input(
        "Suggested delay between opens (ms)", min_value=0, max_value=10000,
        value=st.session_state.rate_ms
    )

    # تصدير/استيراد جلسة لتسهيل الاستكمال لاحقاً
    st.markdown("<span class='label'>Session</span>", unsafe_allow_html=True)
    if st.button("💾 Export Session"):
        payload = {
            "numbers": st.session_state.get("numbers", []),
            "names": st.session_state.get("names", []),
            "countries": st.session_state.get("countries", []),
            "current": st.session_state.get("current", 0),
            "skipped": list(st.session_state.get("skipped", set())),
            "tpl": st.session_state.get("tpl", ""),
        }
        st.download_button(
            "⬇️ Download session.json",
            data=json.dumps(payload, ensure_ascii=False, indent=2),
            file_name="session.json",
            mime="application/json",
            key="dl-session-json"
        )
    up = st.file_uploader("Import session.json", type=["json"], key="sessu")
    if up is not None:
        try:
            data = json.loads(up.read().decode("utf-8"))
            # استعادة جميع القوائم والحالة
            st.session_state.numbers = data.get("numbers", [])
            st.session_state.names = data.get("names", [])
            st.session_state.countries = data.get("countries", [])
            st.session_state.current = int(data.get("current", 0))
            st.session_state.skipped = set(data.get("skipped", []))
            st.session_state.tpl = data.get("tpl", "")
            st.success("Session imported.")
        except Exception as e:
            st.error(f"Failed to import session: {e}")

# عرض الهيدر الاحترافي أعلى الواجهة الرئيسية
render_pro_header(
    title="K A R I M",
    subtitle="WhatsApp Sender PRO — Revamped",
    chips=["Bulk Sender", "CSV/Excel", "Templates", "Progress Control"]
)

# ===========================================================
# 9) Main Layout (3 Columns) / الواجهة الأساسية ثلاث أعمدة
# ===========================================================
colL, colC, colR = st.columns([1.05, 2.4, 1.05])

# -----------------------------------
# 9.1) Left Column: Tools + Stats
# -----------------------------------
with colL:
    st.markdown("<div class='card' style='padding:12px;'>", unsafe_allow_html=True)

    # أدوات سريعة: تنزيل الأرقام النظيفة + نسخها
    st.markdown("<span class='label'>Bulk Tools</span>", unsafe_allow_html=True)
    last_numbers = st.session_state.get("numbers", []) or st.session_state.get("last_numbers", [])
    if last_numbers:
        download_bytes("clean_numbers.txt", "\n".join(last_numbers), key="dl-clean-left")
        copy_to_clipboard("Copy All Numbers", "\n".join(last_numbers))
    else:
        st.info("Clean numbers will appear here after filtering.")

    # إحصائيات صغيرة لحالة التقدم
    st.markdown("<span class='label'>Stats</span>", unsafe_allow_html=True)
    total = len(st.session_state.get("numbers", []))
    skipped = len(st.session_state.get("skipped", set()))
    done = min(st.session_state.get("current", 0), total)
    st.markdown(
        "<div class='stats'>"
        f"<div class='stat'><b>Total</b><br>{total}</div>"
        f"<div class='stat'><b>Done</b><br>{done}</div>"
        f"<div class='stat'><b>Skipped</b><br>{skipped}</div>"
        "</div>", unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------
# 9.2) Right Column: Quick Links
# -----------------------------------
with colR:
    st.markdown("<div class='card' style='padding:12px;'>", unsafe_allow_html=True)
    st.markdown("<span class='label'>Quick Links</span>", unsafe_allow_html=True)
    # روابط سريعة (يمكن تعديلها/إضافة غيرها)
    st.markdown("- 🌐 [EUROSWEET Catalog](https://eurosweet.com.tr)")
    st.markdown("- ✉️ karim.amsha@gmail.com")
    st.markdown("- 🆕 Responsive + One-click Copy")
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------
# 9.3) Center Column: Core Workflow
# -----------------------------------
with colC:
    st.markdown("<div class='card' style='padding:16px;'>", unsafe_allow_html=True)

    # اختيار الوضع: بسيط (أرقام فقط) / ذكي (أسماء + دولة)
    st.markdown("<span class='label'>Choose Mode</span>", unsafe_allow_html=True)
    mode = st.radio("", ["Simple: Numbers Only", "Smart: Personalized (Name & Country)"] , horizontal=True)

    # احمل القوائم من الحالة (أو قيّم افتراضية)
    numbers: list[str] = st.session_state.get("numbers", []) or []
    names: list[str] = st.session_state.get("names", []) or []
    countries: list[str] = st.session_state.get("countries", []) or []

    # اختيار منصة الإرسال (واتساب ويب أو تطبيق الموبايل)
    platform = st.radio("Send using", ["💻 WhatsApp Web", "📱 WhatsApp App"], horizontal=True)
    platform_type = "web" if platform.startswith("💻") else "mobile"

    # =============== Simple Mode ===============
    if mode.startswith("Simple"):
        # اختيار اللغة ثم تحميل القالب تلقائياً
        lang_label = st.radio("Language", list(LANG_CHOICES.keys()), horizontal=True)
        lang_code = LANG_CHOICES[lang_label]
        tpl_simple = LANG_TEMPLATES[lang_code]
        st.session_state.tpl = tpl_simple

        # إدخال الأرقام الخام (أي صيغة)
        raw = st.text_area(
            "Numbers (comma/newline/any format)",
            placeholder="Paste numbers like: +254 722 206312, 201111223344, ...",
            height=120
        )

        # استخراج الأرقام وتنظيفها + إضافة كود الدولة الافتراضي إن لزم
        extracted = extract_numbers(raw)
        default_cc = st.session_state.default_cc or ""
        normalized = [to_e164(n, default_cc) for n in extracted]
        normalized = [n for n in normalized if len(n) >= st.session_state.min_length]

        # إزالة التكرارات مع الحفاظ على الترتيب
        if st.session_state.dedupe:
            normalized = list(dict.fromkeys(normalized))

        # تحديث الحالة
        numbers = normalized
        names = [""] * len(numbers)
        countries = [""] * len(numbers)

        st.session_state.last_numbers = numbers
        st.session_state.numbers = numbers
        st.session_state.names = names
        st.session_state.countries = countries

        # عرض النتائج + أزرار النسخ/التنزيل
        if raw and numbers:
            st.subheader("Filtered Numbers")
            st.code("\n".join(numbers), language="text")
            copy_to_clipboard("Copy Filtered Numbers", "\n".join(numbers))
            download_bytes("clean_numbers.txt", "\n".join(numbers), key="dl-clean-center")

    # =============== Smart Mode ===============
    else:
        # شرح بسيط + ملف CSV مثال
        st.info("Upload CSV/Excel or enter data manually. Columns: number, name, country")
        st.download_button(
            "⬇️ Download example CSV",
            data="number,name,country\n201111223344,Mohamed,Egypt\n971500000001,Ahmed,UAE\n",
            file_name="example_contacts.csv",
            key="dl-example-csv"
        )

        # طريقة الإدخال: رفع ملف أو محرر يدوي
        how = st.radio("Input method", ["Upload CSV/Excel", "Manual editor"], horizontal=True)
        df = None

        if how.startswith("Upload"):
            # رفع CSV أو Excel
            up = st.file_uploader("Upload (CSV, XLSX, XLS)", type=["csv", "xlsx", "xls"])
            if up is not None:
                try:
                    # قراءة الملف
                    if up.name.lower().endswith(".csv"):
                        df = pd.read_csv(up)
                    else:
                        df = pd.read_excel(up)

                    # اختيار أعمدة الأرقام/الاسم/الدولة
                    columns = list(df.columns)
                    ncol = st.selectbox("Select number column", columns)
                    name_col = st.selectbox("Select name column (optional)", [""] + columns)
                    ctry_col = st.selectbox("Select country column (optional)", [""] + columns)

                    # تنظيف وتطبيع الأرقام
                    df = df.dropna(subset=[ncol])
                    df[ncol] = df[ncol].astype(str).apply(clean_number)
                    df[ncol] = df[ncol].apply(lambda x: to_e164(x, st.session_state.default_cc))
                    df = df[df[ncol].str.len() >= st.session_state.min_length]
                    df = df.astype(str)

                    st.success(f"{len(df)} contacts loaded.")

                    # استخراج القوائم من الأعمدة المختارة
                    numbers = df[ncol].tolist()
                    names = df[name_col].tolist() if name_col else [""] * len(df)
                    countries = df[ctry_col].tolist() if ctry_col else [""] * len(df)

                except Exception as e:
                    st.error(f"Failed to process file: {e}")
                    numbers, names, countries = [], [], []

        else:
            # محرر يدوي بصفّين مثال
            example = pd.DataFrame({
                "number": ["201111223344", "971500000001"],
                "name": ["Mohamed", "Ahmed"],
                "country": ["Egypt", "UAE"]
            })
            df = st.data_editor(example, num_rows="dynamic", use_container_width=True)
            if df is not None and not df.empty:
                if "number" in df.columns:
                    # تنظيف وتطبيع الأرقام
                    df["number"] = df["number"].astype(str).apply(clean_number)
                    df["number"] = df["number"].apply(lambda x: to_e164(x, st.session_state.default_cc))
                    df = df[df["number"].str.len() >= st.session_state.min_length]
                    df = df.astype(str)

                    numbers = df["number"].tolist()
                    names = df["name"].tolist() if "name" in df.columns else [""] * len(df)
                    countries = df["country"].tolist() if "country" in df.columns else [""] * len(df)

        # تحديث الحالة بعد الإدخال
        st.session_state.numbers = numbers
        st.session_state.names = names
        st.session_state.countries = countries
        st.session_state.last_numbers = numbers

        # حقل القالب الذكي (قابل للتعديل) + معاينة
        st.markdown("<span class='label'>Message template</span>", unsafe_allow_html=True)
        default_tpl = (
            "Hello {name} 👋\n\n"
            "We are the Sales Department at EUROSWEET GIDA LTD. ŞTİ. (Istanbul – Turkey).\n\n"
            "We specialize in producing high-quality snacks such as:\n"
            "🍪 Croissants, Cakes, Biscuits, Donuts, Jelly, and Wafers.\n\n"
            "We’re always eager to connect with reliable partners in {country} and explore new markets together. 🤝\n\n"
            "If you are interested, we’d be happy to share our catalog and price list, and discuss how we can collaborate.\n\n"
            "Looking forward to your reply, {name}!\n\n"
            "Best regards,\nSales Department\n"
        )
        tpl = st.text_area(
            "Use {name}, {country}, {number}, {idx}",
            value=st.session_state.get("tpl", default_tpl),
            height=220
        )
        st.session_state.tpl = tpl

        # معاينة أول 3 رسائل + تنزيل TXT/CSV للرسائل
        if numbers:
            st.markdown("**Variables:** `{" + "name,country,number,idx" + "}`")
            previews = []
            for i in range(min(3, len(numbers))):
                previews.append(
                    format_message(
                        tpl,
                        (names[i] if i < len(names) else ""),
                        (countries[i] if i < len(countries) else ""),
                        numbers[i],
                        i+1
                    )
                )
            st.code("\n\n---\n".join(previews), language="text")

            # توليد الرسائل كاملة للتنزيل
            msgs = [
                format_message(
                    tpl,
                    (names[i] if i < len(names) else ""),
                    (countries[i] if i < len(countries) else ""),
                    numbers[i],
                    i+1
                )
                for i in range(len(numbers))
            ]
            download_bytes("whatsapp_messages.txt", "\n\n".join(msgs), key="dl-msgs-txt")

            # تصدير CSV يحوي (number, name, country, message)
            csv_buf = StringIO()
            pd.DataFrame({
                "number": numbers,
                "name": names,
                "country": countries,
                "message": msgs
            }).to_csv(csv_buf, index=False)
            st.download_button(
                "⬇️ Export messages.csv",
                data=csv_buf.getvalue(),
                file_name="messages.csv",
                mime="text/csv",
                key="dl-msgs-csv"
            )

    # ===================================
    # 10) Progress + Open WhatsApp / التقدم والإرسال
    # ===================================
    # حالة المؤشر الحالي + مجموعة المتجاوزين
    if "current" not in st.session_state:
        st.session_state.current = 0
    if "skipped" not in st.session_state:
        st.session_state.skipped = set()

    # تحديث نسخ محلية للعرض
    numbers = st.session_state.get("numbers", []) or []
    names = st.session_state.get("names", []) or []
    countries = st.session_state.get("countries", []) or []

    # عداد دائري بسيط يوضح (العنصر الحالي/الإجمالي)
    if numbers:
        percent = int((st.session_state.current + 1) / max(len(numbers),1) * 100)
        st.markdown(
            f"""
            <div style='margin:6px 0;'><b>Progress:</b></div>
            <div style='margin-bottom:9px;'>
                <div style='width:72px;height:72px;margin:auto;position:relative;'>
                    <div style='width:72px;height:72px;border-radius:50%;background:conic-gradient(#22d3ee {percent}%, rgba(127,127,127,.15) {percent}% 100%);display:flex;align-items:center;justify-content:center;box-shadow:0 6px 20px #22d3ee22;position:absolute;top:0;left:0;'>
                        <span style='font-size:1.05rem;color:#051423;font-weight:900;letter-spacing:2px;'>{min(st.session_state.current+1,len(numbers))}/{len(numbers)}</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # زر إعادة التقدم للصفر + تفريغ قائمة المتجاوزين
    if st.button("🔄 Reset Progress"):
        st.session_state.current = 0
        st.session_state.skipped = set()

    if numbers:
        idx = st.session_state.current
        tpl = st.session_state.get("tpl", LANG_TEMPLATES.get("en", ""))

        # توليد الرسالة للشخص الحالي
        try:
            msg_personal = format_message(
                tpl,
                names[idx] if idx < len(names) else "",
                countries[idx] if idx < len(countries) else "",
                numbers[idx],
                idx+1
            )
        except Exception:
            msg_personal = "⚠️ Please check your template or data"

        # حقل تحرير الرسالة الخاصة بالعنصر الحالي (يمكن تعديلها قبل الإرسال)
        message = st.text_area("Message", value=msg_personal, key="msgboxfinal", height=140)

        # شارة تعرض معلومات جهة الاتصال الحالية
        contact_info = f"{numbers[idx]}" \
            + (f" — {names[idx]}" if idx < len(names) and names[idx] else "") \
            + (f" — {countries[idx]}" if idx < len(countries) and countries[idx] else "")
        st.markdown(f"<div class='badge' style='margin:8px 0;'>{contact_info}</div>", unsafe_allow_html=True)

        # قائمة مصغّرة بكل الأرقام مع تمييز الحالي
        st.markdown(
            "<div class='klist'>" +
            "".join([
                f"<div class='kitem {'active' if i==idx else ''}'>{i+1}. {numbers[i]}"
                + (f" - {names[i]}" if i < len(names) and names[i] else "")
                + (f" - {countries[i]}" if i < len(countries) and countries[i] else "")
                + "</div>"
                for i in range(len(numbers))
            ]) +
            "</div>", unsafe_allow_html=True
        )

        # أزرار التحكم: السابق/تجاوز/قفزة/فتح واتساب/التالي
        c1, c2, c3, c4, c5 = st.columns([1.2, 1.2, 1.2, 1.8, 1.2])

        # السابق
        if c1.button("← Prev", disabled=(idx <= 0)):
            st.session_state.current = max(0, idx-1)

        # تجاوز (Skip) — تُضاف للمجموعة skipped
        skip_disabled = (numbers[idx] in st.session_state.skipped)
        if c2.button("Skip", disabled=skip_disabled):
            st.session_state.skipped.add(numbers[idx])
            if idx < len(numbers)-1:
                st.session_state.current = idx+1

        # قفزة برقم index
        jump_to = c3.number_input("Jump", min_value=1, max_value=max(len(numbers),1), value=idx+1, step=1)
        if c3.button("Go"):
            st.session_state.current = min(max(jump_to-1, 0), len(numbers)-1)

        # فتح واتساب بالرابط المناسب (ويب/موبايل)
        if c4.button("Open WhatsApp", disabled=(not message.strip())):
            msg_encoded = urllib.parse.quote(message.strip())
            num = numbers[idx]
            url = (
                f"https://web.whatsapp.com/send?phone={num}&text={msg_encoded}"
                if platform_type == "web"
                else f"https://wa.me/{num}?text={msg_encoded}"
            )
            st.markdown(
                f"<div style='text-align:center;margin-top:6px;'><a href='{url}' target='_blank' style='font-weight:900;'>🚀 Click here if WhatsApp didn't open automatically</a></div>",
                unsafe_allow_html=True
            )
            # فتح تلقائي في نافذة جديدة
            st.components.v1.html(f"""<script>window.open('{url}', '_blank');</script>""")

        # التالي
        if c5.button("Next →", disabled=(idx >= len(numbers)-1)):
            st.session_state.current = min(idx+1, len(numbers)-1)

    # نهاية الكارد المركزي
    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# 11) Footer / التذييل
# =========================
st.markdown(
    "<div style='text-align:center;margin:12px 0;opacity:.9;'>✦ Powered by <b>KARIM OTHMAN</b> © 2025</div>",
    unsafe_allow_html=True
)
