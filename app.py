import streamlit as st
import gspread
import re
from oauth2client.service_account import ServiceAccountCredentials

# --- إعدادات الصفحة الافتراضية ---
st.set_page_config(page_title="منصة تعليم الطلاب الرقمية", page_icon="🎓", layout="wide")

# --- إضافة الستايل المخصص (CSS) ---
st.markdown("""
    <style>
    /* تغيير اتجاه النصوص والصفحة لتناسب اللغة العربية */
    body, .main, block-container {
        direction: RTL;
        text-align: right;
    }
    
    /* ستايل مخصص للبطاقات (Cards) الخاصة بالفيديوهات والاختبارات */
    .content-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border-right: 5px solid #4A90E2; /* شريط ملون جانبي */
    }
    
    .quiz-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border-right: 5px solid #2ECC71; /* شريط أخضر للاختبارات */
    }
    
    /* تحسين خطوط العناوين */
    h1 {
        color: #2C3E50;
        text-align: center;
        font-family: 'Cairo', sans-serif;
        margin-bottom: 30px !important;
    }
    
    h2, h3 {
        color: #34495E;
        font-family: 'Cairo', sans-serif;
    }
    
    /* تحسين القائمة الجانبية */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    </style>
""", unsafe_safe_boundary=True)

# --- إعداد الاتصال بقاعدة البيانات (Google Sheets) ---
def connect_to_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    if "gcp_service_account" in st.secrets:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    else:
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        
    client = gspread.authorize(creds)
    sheet_url = "https://docs.google.com/spreadsheets/d/1o1dk1mQdXOTR_6x8H-_iWMVg_vQAaMB0UUav3aSKlyU/edit?usp=sharing"
    sheet = client.open_by_url(sheet_url).sheet1
    return sheet

try:
    db = connect_to_sheets()
except Exception as e:
    st.error("فشل الاتصال بقاعدة البيانات. تأكد من إعداد المفاتيح السرية بشكل صحيح.")
    db = None

# --- دالة ذكية لإصلاح روابط اليوتيوب المأخوذة من الهاتف ---
def get_clean_youtube_url(url):
    url = str(url).strip()
    if "youtu.be/" in url:
        video_id = url.split("youtu.be/")[-1].split("?")[0]
        return f"https://www.youtube.com/watch?v={video_id}"
    elif "youtube.com/shorts/" in url:
        video_id = url.split("youtube.com/shorts/")[-1].split("?")[0]
        return f"https://www.youtube.com/watch?v={video_id}"
    return url

# --- واجهة المستخدم الرئيسية للتطبيق ---
st.markdown("<h1>🎓 منصة تعليم الطلاب الرقمية</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #7F8C8D; font-size: 1.1rem;'>أهلاً بكم في المنصة التعليمية الرقمية. يمكنكم تصفح الدروس وحل الاختبارات المتاحة أدناه بسهولة:</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

col_video, col_quiz = st.columns(2)

if db:
    try:
        all_records = db.get_all_records()
        
        with col_video:
            st.markdown("<h2>📺 فيديوهات الدروس المشروحة</h2>", unsafe_allow_html=True)
            videos = [r for r in all_records if str(r.get('نوع الرابط')).strip() == 'فيديو']
            if videos:
                for v in videos:
                    # فتح بطاقة مخصصة للفيديو بالـ CSS
                    st.markdown(f"""
                    <div class="content-card">
                        <h3>📖 درس رقم {v.get('رقم الدرس', '#')}: {v.get('وصف الدرس', '')}</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    clean_url = get_clean_youtube_url(v['الرابط'])
                    st.video(clean_url)
                    st.markdown("<br>", unsafe_allow_html=True)
            else:
                st.info("لا توجد فيديوهات مضافة بعد.")
                
        with col_quiz:
            st.markdown("<h2>📝 الاختبارات والتقييمات المتاحة</h2>", unsafe_allow_html=True)
            quizzes = [r for r in all_records if str(r.get('نوع الرابط')).strip() == 'اختبار']
            if quizzes:
                for q in quizzes:
                    # فتح بطاقة مخصصة للاختبار بالـ CSS
                    st.markdown(f"""
                    <div class="quiz-card">
                        <h3>🎯 اختبار الدرس رقم {q.get('رقم الدرس', '#')}</h3>
                        <p style='color: #7F8C8D;'>ملاحظة: {q.get('وصف الدرس', 'لا توجد ملاحظات إضافية')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.link_button(url=q['الرابط'], label=f"🔗 دخول الاختبار السريع", use_container_width=True)
                    st.markdown("<br><br>", unsafe_allow_html=True)
            else:
                st.info("لا توجد اختبارات مضافة بعد.")
    except Exception as e:
        st.warning("الجدول فارغ حالياً، قم بتسجيل الدخول كمعلم لإضافة المحتوى الأول.")

# --- لوحة التحكم المغلقة بكلمة السر (7962400) ---
st.sidebar.title("🔐 لوحة تحكم المعلم")
password_input = st.sidebar.text_input("أدخل كلمة السر للدخول:", type="password")

if password_input == "7962400":
    st.sidebar.success("تم تسجيل الدخول بنجاح!")
    
    admin_mode = st.sidebar.radio("اختر العملية:", ("➕ إضافة محتوى جديد", "🗑️ حذف محتوى حالي"))
    
    if admin_mode == "➕ إضافة محتوى جديد":
        action = st.sidebar.radio("نوع المحتوى:", ("إضافة رابط اختبار", "إضافة فيديو الدرس (يوتيوب)"))
        
        lesson_num = st.sidebar.text_input("رقم الدرس (مثال: 1 أو 2):")
        lesson_desc = st.sidebar.text_input("وصف الدرس (مثال: شرح الجمع والطرح):")
        
        if action == "إضافة رابط اختبار":
            quiz_url = st.sidebar.text_input("أدخل رابط الاختبار:")
            if st.sidebar.button("حفظ رابط الاختبار"):
                if quiz_url and db:
                    db.append_row(["اختبار", quiz_url, lesson_desc, lesson_num])
                    st.sidebar.success("تم حفظ الاختبار بنجاح!")
                    st.rerun()
                else:
                    st.sidebar.error("الرجاء إدخال رابط صحيح.")
                    
        elif action == "إضافة فيديو الدرس (يوتيوب)":
            video_url = st.sidebar.text_input("أدخل رابط فيديو اليوتيوب:")
            if st.sidebar.button("حفظ فيديو الدرس"):
                if video_url and db:
                    db.append_row(["فيديو", video_url, lesson_desc, lesson_num])
                    st.sidebar.success("تم حفظ فيديو الدرس بنجاح!")
                    st.rerun()
                else:
                    st.sidebar.error("الرجاء إدخال رابط صحيح.")
                    
    elif admin_mode == "🗑️ حذف محتوى حالي":
        st.sidebar.markdown("### اختر المحتوى المراد حذفه:")
        if db:
            try:
                raw_rows = db.get_all_values()
                if len(raw_rows) > 1:
                    options_to_delete = []
                    for idx, row in enumerate(raw_rows[1:], start=2):
                        if len(row) >= 4:
                            display_text = f"[{row[0]}] درس {row[3]}: {row[2][:20]}"
                            options_to_delete.append((idx, display_text))
                    
                    selected_item = st.sidebar.selectbox(
                        "اختر العنصر للحذف:", 
                        options=options_to_delete, 
                        format_func=lambda x: x[1]
                    )
                    
                    if st.sidebar.button("❌ تأكيد الحذف النهائي"):
                        row_index_to_delete = selected_item[0]
                        db.delete_rows(row_index_to_delete)
                        st.sidebar.success("تم حذف العنصر بنجاح من قاعدة البيانات!")
                        st.rerun()
                else:
                    st.sidebar.info("قاعدة البيانات فارغة تماماً، لا يوجد ما يمكن حذفه.")
            except Exception as e:
                st.sidebar.error("حدث خطأ أثناء محاولة جلب قائمة الحذف.")

elif password_input != "":
    st.sidebar.error("كلمة السر غير صحيحة!")