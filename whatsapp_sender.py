# =============================================================================
# KARIM | WhatsApp Sender PRO — Revamped (2025)
# =============================================================================
# هذا الملف يقدّم أداة إرسال رسائل واتساب شبه-جماعية عبر Streamlit بواجهة احترافية.
# يحافظ على كل ميزات الكود الأصلي ويضيف:
# - هيدر احترافي (Glass + Animated Gradient) + شارات الحالة
# - ثيم داكن/فاتح + CSS مُهيكل
# - Quick Links احترافية (Grid + Badges + CTA)
# - تصدير/استيراد الجلسة (Session Export/Import)
# - إزالة تكرارات، حد أدنى لطول الرقم، كود دولة افتراضي
# - أوضاع Simple و Smart (CSV/Excel/Data Editor)
# - قوالب رسائل مع متغيرات {name}, {country}, {number}, {idx}
# - فتح واتساب (Web/App) لكل جهة اتصال
# - شريط تقدّم + Prev/Next/Skip/Jump
# - تنزيل TXT/CSV للأرقام والرسائل
#
# نقاط مهمة:
# - معالجة مشكلة StreamlitDuplicateElementId عبر مفاتيح فريدة للأزرار والعمليات.
# - كل جزء موثّق لتعقبّله وتعديله بسهولة لاحقًا.
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
from uuid import uuid4  # لمفاتيح فريدة لعناصر Streamlit

# ================================
# 2) Page Config / إعدادات الصفحة
# ================================
st.set_page_config(
    page_title="KARIM | WhatsApp Sender PRO",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# 3) Constants / Templates / الإعدادات الثابتة
# ============================================

# نمط المتغيرات المسموح بها داخل القوالب
VAR_PATTERN = re.compile(r"\{(name|country|number|idx)\}")

# قوالب جاهزة لكل لغة (يمكن التعديل والإضافة)
LANG_TEMPLATES = {
    "tr": """Merhaba {name},

EUROSWEET GIDA LTD. ŞTİ. Satış Departmanından ulaşıyorum. İstanbul’da NUKKA ve PROSWEET markalarımız altında yüksek kaliteli kruvasan, kek, bisküvi, donut, wafer ve jelly üretimi ve ihracatı yapıyoruz.

İlgilendiğiniz ürün kategorilerini belirtirseniz; kataloglarımızı, FOB/CIF fiyat tekliflerini, teslim sürelerini ve MOQ bilgilerini hemen paylaşabilirim. Özel marka (OEM/Private Label) üretim seçenekleri de sunuyoruz.

📞 WhatsApp: +90 552 080 29 16
📧 Email: karim@kalitecikolata.com.tr
Satış Departmanı | EUROSWEET GIDA LTD. ŞTİ.""",

    "en": """Hello {name},

I’m reaching out from the Sales Department of EUROSWEET GIDA LTD. ŞTİ. (Istanbul–Türkiye).  
We manufacture and export high-quality FMCG snacks under our brands **NUKKA & PROSWEET**, including croissants, cakes, biscuits, donuts, wafers, and jellies.

Kindly advise which product categories you are interested in, and I will share our catalogues, FOB/CIF pricing, lead times, and MOQ details. Private label (OEM) options are also available.

📞 WhatsApp: +90 552 080 29 16  
📧 Email: karim@kalitecikolata.com.tr  
Sales Department | EUROSWEET GIDA LTD. ŞTİ.""",

    "ar": """مرحبًا {name}،

أتواصل معكم من قسم المبيعات في شركة **EUROSWEET GIDA LTD. ŞTİ.** في إسطنبول.  
نقوم بتصنيع وتصدير منتجات سناكس عالية الجودة تحت علامتَي **NUKKA & PROSWEET** مثل الكرواسون، الكيك، البسكويت، الدونات، الويفر والجيلي.

يرجى تزويدنا بالأصناف التي تهمكم لنرسل لكم الكتالوجات والأسعار (FOB/CIF) ومدة التسليم وكمية الطلب الدنيا. كما نوفر خدمة الإنتاج للعلامات التجارية الخاصة (Private Label).

📞 واتساب: +90 552 080 29 16  
📧 البريد: karim@kalitecikolata.com.tr  
قسم المبيعات | EUROSWEET GIDA LTD. ŞTİ."""
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
    min_len = st.session_state.get("min_length", 8)
    for line in lines:
        digits = re.sub(r"\D", "", line or "")
        if len(digits) >= min_len:
            out.append(digits)
    return out

def clean_number(n: str) -> str:
    """
    ينظف رقم واحد فقط — يبقي أرقام 0-9 ويحذف غيرها.
    """
    return re.sub(r"\D", "", str(n or ""))

def to_e164(num: str, default_cc: str) -> str:
    """
    تحويل مبسّط نحو شكل E.164 (مناسب لروابط واتساب):
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
    زر نسخ للClipboard باستخدام HTML/JS مضمّن.
    - لا يستخدم st.button حتى لا يحدث تضارب مفاتيح.
    - مناسب لنسخ القوائم الكبيرة (الأرقام/الرسائل).
    """
    btn_id = f"copy_{uuid4().hex}"
    st.markdown(
        f"""
        <button id="{btn_id}" style="background:linear-gradient(90deg,#22d3ee,#06b6d4);
                border:none;border-radius:10px;padding:8px 16px;color:#0b1220;
                font-weight:800;cursor:pointer;box-shadow:0 6px 18px #06b6d433;margin:4px 0;">
            {label}
        </button>
        <script>
        const el = document.getElementById('{btn_id}');
        if (el) {{
            el.onclick = () => {{
                navigator.clipboard.writeText({json.dumps(content)});
                const old = el.innerText;
                el.innerText = 'Copied!';
                setTimeout(()=> el.innerText = old, 1100);
            }}
        }}
        </script>
        """,
        unsafe_allow_html=True,
    )

def download_bytes(name: str, text: str, key: str | None = None, mime: str = "text/plain"):
    """
    زر تنزيل ملف نصّي آمن من ناحية تكرار المفاتيح:
    - إذا كان هناك زرين بنفس الـlabel داخل الصفحة، يجب توفير key فريد.
    - إن لم يمرّر key، سيتم توليده تلقائياً من اسم الملف ومحتواه.
    """
    key = key or f"dl-{name}-{uuid4().hex}"
    st.download_button(
        label=f"⬇️ Download {name}",
        data=text.encode("utf-8") if isinstance(text, str) else text,
        file_name=name,
        mime=mime,
        key=key,
    )

# ======================================
# 5) Theme Defaults / الثيم والقيم الأولية
# ======================================
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
if "numbers" not in st.session_state:
    st.session_state.numbers = []
if "names" not in st.session_state:
    st.session_state.names = []
if "countries" not in st.session_state:
    st.session_state.countries = []
if "current" not in st.session_state:
    st.session_state.current = 0
if "skipped" not in st.session_state:
    st.session_state.skipped = set()
if "tpl" not in st.session_state:
    st.session_state.tpl = LANG_TEMPLATES["en"]

# ==========================
# 6) CSS Themes / أنماط CSS
# ==========================
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

# حقن CSS حسب الثيم الحالي
st.markdown(DARK_CSS if st.session_state.theme_dark else LIGHT_CSS, unsafe_allow_html=True)

# ======================================================
# 7) Header Component (Pro) / الهيدر الاحترافي المتحرك
# ======================================================
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
    subtitle: str = "WhatsApp Sender PRO — Revamped | KALİTE ÇİKOLATA GIDA SAN. TİC. A.Ş.",
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

# ===============================
# 8) Quick Links — CSS + Renderer
# ===============================
QUICK_LINKS_CSS = """
<style>
.ql-card{padding:14px;border-radius:16px;border:1px solid var(--cardb, #e6eef8);background:var(--card, #fff);box-shadow:0 7px 27px rgba(36,44,76,.11),0 1px 5px #00000010}
.ql-grid{display:grid;grid-template-columns:1fr;gap:10px}
@media (min-width:520px){.ql-grid{grid-template-columns:1fr 1fr}}
.ql-item{position:relative;display:flex;gap:10px;align-items:flex-start;padding:12px;border-radius:14px;border:1px solid var(--cardb, #e6eef8);background:linear-gradient(180deg,rgba(255,255,255,.75),rgba(255,255,255,.55));cursor:pointer;text-decoration:none!important;color:inherit!important;transition:transform .12s,box-shadow .12s,border-color .12s}
.dark .ql-item{background:rgba(255,255,255,.05)}
.ql-item:hover{transform:translateY(-2px);box-shadow:0 12px 28px rgba(14,165,233,.16);border-color:rgba(14,165,233,.35)}
.ql-icon{width:38px;height:38px;min-width:38px;border-radius:11px;display:grid;place-items:center;font-size:18px;font-weight:900;color:#07111f;background:linear-gradient(135deg,#60a5fa,#22d3ee);box-shadow:0 10px 22px rgba(56,189,248,.28);user-select:none}
.ql-body{flex:1;line-height:1.25}
.ql-title{font-weight:900;font-size:.98rem;margin:0}
.ql-sub{font-size:.84rem;opacity:.85;margin-top:2px}
.ql-badges{display:flex;gap:6px;flex-wrap:wrap}
.ql-badge{padding:3px 8px;border-radius:999px;font-size:.72rem;font-weight:800;border:1px solid rgba(99,102,241,.25);background:rgba(99,102,241,.09)}
.ql-cta{margin-top:8px;display:inline-block;padding:6px 10px;border-radius:10px;font-weight:900;font-size:.82rem;background:linear-gradient(90deg,#60a5fa,#22d3ee);color:#08111f!important;text-decoration:none!important;box-shadow:0 10px 22px rgba(34,211,238,.22)}
.ql-cta:hover{transform:translateY(-1px)}
.ql-item[data-tint="blue"]  .ql-icon{background:linear-gradient(135deg,#60a5fa,#22d3ee)}
.ql-item[data-tint="green"] .ql-icon{background:linear-gradient(135deg,#34d399,#10b981)}
.ql-item[data-tint="amber"] .ql-icon{background:linear-gradient(135deg,#fbbf24,#f59e0b)}
.ql-item[data-tint="rose"]  .ql-icon{background:linear-gradient(135deg,#fb7185,#f43f5e)}
</style>
"""
st.markdown(QUICK_LINKS_CSS, unsafe_allow_html=True)

def render_quick_links(links: list[dict], title: str = "Quick Links"):
    """
    يرسم شبكة روابط احترافية.
    كل عنصر في links عبارة عن dict بالمفاتيح:
      - title: عنوان الرابط (إجباري)
      - href:  رابط الوجهة (mailto:/https:/wa.me/...) (إجباري)
      - icon:  نص الأيقونة (إيموجي/حرفين) (اختياري)
      - sub:   وصف صغير/سطر توضيحي (اختياري)
      - badges:[قائمة شارات] (اختياري)
      - cta:   {"label": "...", "href": "..."} زر نداء (اختياري)
      - tint:  "blue" | "green" | "amber" | "rose" للتلوين (اختياري)
    """
    st.markdown(f"<div class='ql-card'><div class='label'>{title}</div>", unsafe_allow_html=True)
    html = ["<div class='ql-grid'>"]
    for it in links:
        t = it.get("title","").strip()
        href  = it.get("href","#").strip()
        icon  = it.get("icon","🔗")
        sub   = it.get("sub","").strip()
        badges= it.get("badges",[]) or []
        tint  = it.get("tint","blue")
        cta   = it.get("cta")

        line  = [f"<a class='ql-item' data-tint='{tint}' href='{href}' target='_blank' rel='noopener'>"]
        line += [f"<div class='ql-icon'>{icon}</div>"]
        line += ["<div class='ql-body'>"]
        line += [f"<div class='ql-title'>{t}</div>"]
        if sub:
            line += [f"<div class='ql-sub'>{sub}</div>"]
        if badges:
            bs = "".join([f"<span class='ql-badge'>{b}</span>" for b in badges])
            line += [f"<div class='ql-badges' style='margin-top:6px;'>{bs}</div>"]
        if cta and cta.get("label") and cta.get("href"):
            line += [f"<a class='ql-cta' href='{cta['href']}' target='_blank' rel='noopener'>{cta['label']}</a>"]
        line += ["</div></a>"]
        html.append("".join(line))
    html.append("</div></div>")
    st.markdown("".join(html), unsafe_allow_html=True)

# ---------------------------
# بيانات الروابط (قابلة للتبديل)
# ---------------------------
QUICK_LINKS_DATA = [
    {
        "title": "EUROSWEET Catalog",
        "sub": "منتجات / كتالوج رسمي",
        "href": "https://eurosweet.com.tr",
        "icon": "📘",
        "tint": "blue",
        "badges": ["Official", "Public"],
        "cta": {"label": "Open Catalog ↗", "href": "https://eurosweet.com.tr"}
    },
    {
        "title": "Contact Developer",
        "sub": "تواصل مع كريم — استفسارات ودعم",
        "href": "mailto:karim.amsha@gmail.com",
        "icon": "✉️",
        "tint": "green",
        "badges": ["Support"],
        "cta": {"label": "Email Now", "href": "mailto:karim.amsha@gmail.com"}
    },
    {
        "title": "WhatsApp Support",
        "sub": "تواصل عبر واتساب لطلبات عاجلة",
        "href": "https://wa.me/905382319857",
        "icon": "💬",
        "tint": "amber",
        "badges": ["Fast", "Direct"],
        "cta": {"label": "Open WhatsApp", "href": "https://wa.me/905382319857"}
    },
    {
        "title": "Changelog",
        "sub": "آخر الميزات: Responsive + One-click Copy",
        "href": "https://eurosweet.com.tr/#updates",
        "icon": "🚀",
        "tint": "rose",
        "badges": ["Updated"],
        "cta": {"label": "View Updates", "href": "https://eurosweet.com.tr/#updates"}
    },
]

# ===================================================
# 9) Sidebar / الشريط الجانبي — إعدادات + جلسة
# ===================================================
with st.sidebar:
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

    # تصدير/استيراد جلسة
    st.markdown("<span class='label'>Session</span>", unsafe_allow_html=True)
    if st.button("💾 Export Session", key="btn_export_session"):
        payload = {
            "numbers": st.session_state.get("numbers", []),
            "names": st.session_state.get("names", []),
            "countries": st.session_state.get("countries", []),
            "current": st.session_state.get("current", 0),
            "skipped": list(st.session_state.get("skipped", set())),
            "tpl": st.session_state.get("tpl", ""),
            "settings": {
                "theme_dark": st.session_state.get("theme_dark", True),
                "default_cc": st.session_state.get("default_cc", ""),
                "min_length": st.session_state.get("min_length", 8),
                "dedupe": st.session_state.get("dedupe", True),
                "rate_ms": st.session_state.get("rate_ms", 0),
            }
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
            st.session_state.numbers = data.get("numbers", [])
            st.session_state.names = data.get("names", [])
            st.session_state.countries = data.get("countries", [])
            st.session_state.current = int(data.get("current", 0))
            st.session_state.skipped = set(data.get("skipped", []))
            st.session_state.tpl = data.get("tpl", st.session_state.tpl)
            for k, v in (data.get("settings") or {}).items():
                st.session_state[k] = v
            st.success("Session imported.")
        except Exception as e:
            st.error(f"Failed to import session: {e}")

# ===========================================================
# 10) Header (Pro)
# ===========================================================
render_pro_header(
    title="K A R I M",
    subtitle="WhatsApp Sender PRO — Revamped | KALİTE ÇİKOLATA GIDA SAN. TİC. A.Ş.",
    chips=["Bulk Sender", "CSV/Excel", "Templates", "Progress Control"]
)

# ===========================================================
# 11) Main Layout (3 Columns)
# ===========================================================
colL, colC, colR = st.columns([1.05, 2.4, 1.05])

# -----------------------------------
# 11.1) Right Column: Quick Links
# -----------------------------------
with colR:
    render_quick_links(QUICK_LINKS_DATA, title="Quick Links")

# -----------------------------------
# 11.2) Left Column: Tools + Stats
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
# 11.3) Center Column: Core Workflow
# -----------------------------------
with colC:
    st.markdown("<div class='card' style='padding:16px;'>", unsafe_allow_html=True)

    # اختيار الوضع: بسيط (أرقام فقط) / ذكي (أسماء + دولة)
    st.markdown("<span class='label'>Choose Mode</span>", unsafe_allow_html=True)
    mode = st.radio("", ["Simple: Numbers Only", "Smart: Personalized (Name & Country)"] , horizontal=True, key="mode_radio")

    # منصة الإرسال (واتساب ويب أو تطبيق الموبايل)
    platform = st.radio("Send using", ["💻 WhatsApp Web", "📱 WhatsApp App"], horizontal=True, key="platform_radio")
    platform_type = "web" if platform.startswith("💻") else "mobile"

    # احمل القوائم من الحالة (أو قيّم افتراضية)
    numbers: list[str] = st.session_state.get("numbers", []) or []
    names: list[str] = st.session_state.get("names", []) or []
    countries: list[str] = st.session_state.get("countries", []) or []

    # =======================
    # Simple Mode (Numbers)
    # =======================
    if mode.startswith("Simple"):
        lang_label = st.radio("Language", list(LANG_CHOICES.keys()), horizontal=True, key="lang_radio")
        lang_code = LANG_CHOICES[lang_label]
        tpl_simple = LANG_TEMPLATES[lang_code]
        st.session_state.tpl = tpl_simple

        # إدخال الأرقام الخام
        raw = st.text_area(
            "Numbers (comma/newline/any format)",
            placeholder="Paste numbers like: +254 722 206312, 201111223344, ...",
            height=120,
            key="numbers_raw"
        )

        # استخراج وتنظيف وتطبيع الأرقام
        extracted = extract_numbers(raw)
        default_cc = st.session_state.default_cc or ""
        normalized = [to_e164(n, default_cc) for n in extracted]
        normalized = [n for n in normalized if len(n) >= st.session_state.min_length]
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

        # عرض النتائج + أدوات النسخ/التحميل
        if raw and numbers:
            st.subheader("Filtered Numbers")
            st.code("\n".join(numbers), language="text")
            copy_to_clipboard("Copy Filtered Numbers", "\n".join(numbers))
            download_bytes("clean_numbers.txt", "\n".join(numbers), key="dl-clean-center")

    # =======================
    # Smart Mode (CSV/Editor)
    # =======================
    else:
        st.info("Upload CSV/Excel or enter data manually. Columns: number, name, country")
        st.download_button(
            "⬇️ Download example CSV",
            data="number,name,country\n201111223344,Mohamed,Egypt\n971500000001,Ahmed,UAE\n",
            file_name="example_contacts.csv",
            key="dl-example-csv"
        )

        how = st.radio("Input method", ["Upload CSV/Excel", "Manual editor"], horizontal=True, key="input_method")
        df = None

        if how.startswith("Upload"):
            up = st.file_uploader("Upload (CSV, XLSX, XLS)", type=["csv", "xlsx", "xls"], key="uploader")
            if up is not None:
                try:
                    if up.name.lower().endswith(".csv"):
                        df = pd.read_csv(up)
                    else:
                        df = pd.read_excel(up)

                    columns = list(df.columns)
                    ncol = st.selectbox("Select number column", columns, key="sel_ncol")
                    name_col = st.selectbox("Select name column (optional)", [""] + columns, key="sel_namecol")
                    ctry_col = st.selectbox("Select country column (optional)", [""] + columns, key="sel_ctrycol")

                    df = df.dropna(subset=[ncol])
                    df[ncol] = df[ncol].astype(str).apply(clean_number)
                    df[ncol] = df[ncol].apply(lambda x: to_e164(x, st.session_state.default_cc))
                    df = df[df[ncol].str.len() >= st.session_state.min_length]
                    df = df.astype(str)

                    st.success(f"{len(df)} contacts loaded.")

                    numbers = df[ncol].tolist()
                    names = df[name_col].tolist() if name_col else [""] * len(df)
                    countries = df[ctry_col].tolist() if ctry_col else [""] * len(df)

                except Exception as e:
                    st.error(f"Failed to process file: {e}")
                    numbers, names, countries = [], [], []

        else:
            example = pd.DataFrame({
                "number": ["201111223344", "971500000001"],
                "name": ["Mohamed", "Ahmed"],
                "country": ["Egypt", "UAE"]
            })
            df = st.data_editor(example, num_rows="dynamic", use_container_width=True, key="editor")
            if df is not None and not df.empty:
                if "number" in df.columns:
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

        # القالب الذكي (قابل للتعديل) + معاينة + تنزيل الرسائل
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
            height=220,
            key="tpl_smart"
        )
        st.session_state.tpl = tpl

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
    # 12) Progress + Open WhatsApp
    # ===================================
    # تحضير الحالة
    if "current" not in st.session_state:
        st.session_state.current = 0
    if "skipped" not in st.session_state:
        st.session_state.skipped = set()

    numbers = st.session_state.get("numbers", []) or []
    names = st.session_state.get("names", []) or []
    countries = st.session_state.get("countries", []) or []

    # عرض نسبة التقدّم الدائرية
    if numbers:
        percent = int((st.session_state.current + 1) / max(len(numbers),1) * 100)
        st.markdown(
            f"""
            <div style='margin:6px 0;'><b>Progress:</b></div>
            <div style='margin-bottom:9px;'>
                <div style='width:72px;height:72px;margin:auto;position:relative;'>
                    <div style='width:72px;height:72px;border-radius:50%;background:conic-gradient(#22d3ee {percent}%, rgba(127,127,127,.15) {percent}% 100%);display:flex;align-items:center;justify-content:center;box-shadow:0 6px 20px #22d3ee22;position:absolute;top:0;left:0;'>
                        <span style='font-size:1.05rem;color:#051423;font-weight:900;letter-spacing:2px;'>
                            {min(st.session_state.current+1,len(numbers))}/{len(numbers)}
                        </span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # زر إعادة التقدّم
    if st.button("🔄 Reset Progress", key="btn_reset"):
        st.session_state.current = 0
        st.session_state.skipped = set()

    # واجهة الإرسال
    if numbers:
        idx = st.session_state.current
        tpl = st.session_state.get("tpl", LANG_TEMPLATES.get("en", ""))

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

        message = st.text_area("Message", value=msg_personal, key=f"msgbox_{idx}", height=140)

        contact_info = f"{numbers[idx]}" \
            + (f" — {names[idx]}" if idx < len(names) and names[idx] else "") \
            + (f" — {countries[idx]}" if idx < len(countries) and countries[idx] else "")
        st.markdown(f"<div class='badge' style='margin:8px 0;'>{contact_info}</div>", unsafe_allow_html=True)

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

        c1, c2, c3, c4, c5 = st.columns([1.2, 1.2, 1.2, 1.8, 1.2])

        # السابق
        if c1.button("← Prev", disabled=(idx <= 0), key=f"btn_prev_{idx}"):
            st.session_state.current = max(0, idx-1)

        # تجاوز (Skip)
        skip_disabled = (numbers[idx] in st.session_state.skipped)
        if c2.button("Skip", disabled=skip_disabled, key=f"btn_skip_{idx}"):
            st.session_state.skipped.add(numbers[idx])
            if idx < len(numbers)-1:
                st.session_state.current = idx+1

        # قفزة برقم index
        jump_to = c3.number_input("Jump", min_value=1, max_value=max(len(numbers),1), value=idx+1, step=1, key=f"jump_{idx}")
        if c3.button("Go", key=f"btn_go_{idx}"):
            st.session_state.current = min(max(jump_to-1, 0), len(numbers)-1)

        # فتح واتساب
        if c4.button("Open WhatsApp", disabled=(not message.strip()), key=f"btn_open_{idx}"):
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
            st.components.v1.html(f"""<script>window.open('{url}', '_blank');</script>""")

        # التالي
        if c5.button("Next →", disabled=(idx >= len(numbers)-1), key=f"btn_next_{idx}"):
            st.session_state.current = min(idx+1, len(numbers)-1)

    # نهاية الكارد المركزي
    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# 13) Footer / التذييل
# =========================
st.markdown(
    "<div style='text-align:center;margin:12px 0;opacity:.9;'>✦ Powered by <b>KARIM OTHMAN</b> © 2025</div>",
    unsafe_allow_html=True
)
