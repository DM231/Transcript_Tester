import docx2txt
import re


# دالة لاستخراج النص من ملف Word
def extract_text_from_docx(docx_path):
    try:
        text = docx2txt.process(docx_path)
        return text if text.strip() else "الملف لا يحتوي على نص قابل للاستخراج"
    except Exception as e:
        return f"خطأ في استخراج النص: {str(e)}"


# دالة لتنظيف النص من الفراغات الزائدة والأسطر الفارغة
def clean_text(text):
    # استبدال الفراغات المتعددة بفراغ واحد
    text = re.sub(r'\s+', ' ', text)
    # إزالة الأسطر الفارغة
    text = re.sub(r'\n\s*\n+', '\n', text)
    # تنظيف بداية ونهاية كل سطر
    text = '\n'.join(line.strip() for line in text.splitlines() if line.strip())
    return text


# دالة لاستخراج المواد باستخدام التعابير المنتظمة
def extract_courses_from_text(text):
    # قائمة التعابير المنتظمة لكل نوع من المواد
    patterns = [
        # للمواد التي تبدأ بـ BM (تشمل الستاج مع YT/YZ)
        r'(BM\d{3})\s+(.+?)\s+(?:[0-9]+\.[0-9]+\s+){2}([A-Z]{2}|YT|YZ)',
        # للمواد التي تبدأ بـ AIB
        r'(AIB\d{3})\s+(.+?)\s+(?:[0-9]+\.[0-9]+\s+){2}([A-Z]{2})',
        # للمواد التي تبدأ بـ TDB
        r'(TDB\d{3})\s+(.+?)\s+(?:[0-9]+\.[0-9]+\s+){2}([A-Z]{2})',
        # للمواد التي تبدأ بـ FIZ
        r'(FIZ\d{3})\s+(.+?)\s+(?:[0-9]+\.[0-9]+\s+){2}([A-Z]{2})',
        # للمواد التي تبدأ بـ MAT
        r'(MAT\d{3})\s+(.+?)\s+(?:[0-9]+\.[0-9]+\s+){2}([A-Z]{2})',
        # للمواد التي تبدأ بـ ING
        r'(ING\d{3})\s+(.+?)\s+(?:[0-9]+\.[0-9]+\s+){2}([A-Z]{2})',
        # للمواد التي تبدأ بـ KRP
        r'(KRP\d{3})\s+(.+?)\s+(?:[0-9]+\.[0-9]+\s+){2}([A-Z]{2})',
        # للمواد التي تبدأ بـ US
        r'(US\d{3})\s+(.+?)\s+(?:[0-9]+\.[0-9]+\s+){2}([A-Z]{2})',
        # للمواد التي تبدأ بـ MS
        r'(MS\d{3})\s+(.+?)\s+(?:[0-9]+\.[0-9]+\s+){2}([A-Z]{2})',
    ]

    courses = []
    lines = text.splitlines()

    print("=== المواد التي تم استخراجها ===")
    for i, line in enumerate(lines):
        for pattern in patterns:
            match = re.search(pattern, line.strip())
            if match:
                course_code = match.group(1)
                course_name = match.group(2).strip()
                grade = match.group(3)
                courses.append({
                    "code": course_code,
                    "name": course_name,
                    "grade": grade
                })
                print(f"السطر {i + 1}: {line}")
                print(f"  - الكود: {course_code}")
                print(f"  - الاسم: {course_name}")
                print(f"  - الدرجة: {grade}\n")
                break

    if not courses:
        print("لم يتم العثور على أي مواد تتطابق مع التعابير المنتظمة.")

    return courses


# المسار إلى ملف Word (قم بتغييره إلى المسار الصحيح لملفك)
docx_path = "path/to/your/file.docx"  # استبدل هذا بالمسار الصحيح لملفك

# استخراج النص من ملف Word
text = extract_text_from_docx(docx_path)

# تنظيف النص
text = clean_text(text)

# طباعة النص المستخرج بعد التنظيف
print("=== النص المستخرج من الملف ===")
print(text)
print("\n")

# استخراج المواد باستخدام التعابير المنتظمة
extracted_courses = extract_courses_from_text(text)