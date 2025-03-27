from flask import Flask, render_template, request
import docx2txt
import re
import os

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(os.path.expanduser('~'), 'Desktop', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# قائمة الدروس المطلوبة حسب الفصل الدراسي
REQUIRED_COURSES_BY_SEMESTER = {
    "1. Yarıyıl": {
        "mandatory": {
            "AIB101": "Atatürk İlkeleri ve İnkılap Tarihi I",
            "TDB121": "Türk Dili I",
            "FIZ101": "Fizik I",
            "BM107": "Elektrik Devre Temelleri",
            "MAT101": "Matematik I",
            "BM103": "Bilgisayar Mühendisliğine Giriş",
            "BM105": "Bilişim Teknolojileri",
            "BM101": "Algoritmalar ve Programlama I",
            "ING101": "İngilizce I",
        },
        "elective": {}
    },
    "2. Yarıyıl": {
        "mandatory": {
            "AIB102": "Atatürk İlkeleri ve İnkılap Tarihi II",
            "TDB122": "Türk Dili II",
            "FIZ102": "Fizik II",
            "MAT102": "Matematik II",
            "BM102": "Algoritmalar ve Programlama II",
            "BM104": "Web Teknolojileri",
            "BM106": "Olasılık ve İstatistik",
            "KRP102": "Kariyer Planlama",
            "ING102": "İngilizce II",
        },
        "elective": {}
    },
    "3. Yarıyıl": {
        "mandatory": {
            "BM211": "Diferansiyel Denklemler",
            "BM213": "Lineer Cebir",
            "BM205": "Nesneye Dayalı Programlama",
            "BM209": "Sayısal Analiz",
            "BM203": "Elektronik",
            "BM215": "Ayrık İşlemsel Yapılar",
        },
        "elective": {
            "SECSOS3YY": {
                "prefix": "US",
                "required_count": 1,
                "courses": {
                    "US211": "İş Psikolojisi",
                    "US215": "Kültür Tarihi",
                    "US217": "Sanat Tarihi",
                    "US219": "Sivil Toplum Organizasyonları",
                    "US221": "Uygarlık Tarihi",
                    "US201": "Bilim Tarihi ve Felsefesi",
                    "US207": "Girişimcilik",
                    "US225": "Girişimcilik I",
                    "US227": "Girişimcilik II",
                    "US203": "Çevre ve Enerji",
                    "US209": "İletişim Tekniği",
                    "US205": "Davranış Bilimine Giriş",
                    "US213": "İşletme Yönetimi",
                }
            }
        }
    },
    "4. Yarıyıl": {
        "mandatory": {
            "BM204": "Bilgisayar Organizasyonu",
            "BM206": "Sayısal Elektronik",
            "BM208": "Nesneye Dayalı Analiz ve Tasarım",
            "BM210": "Programlama Dillerinin Prensipleri",
            "BM212": "Mesleki İngilizce",
            "BM214": "Veri Yapıları",
        },
        "elective": {
            "SECSOS4YY": {
                "prefix": "US",
                "required_count": 1,
                "courses": {
                    "US211": "İş Psikolojisi",
                    "US215": "Kültür Tarihi",
                    "US217": "Sanat Tarihi",
                    "US219": "Sivil Toplum Organizasyonları",
                    "US221": "Uygarlık Tarihi",
                    "US201": "Bilim Tarihi ve Felsefesi",
                    "US207": "Girişimcilik",
                    "US225": "Girişimcilik I",
                    "US227": "Girişimcilik II",
                    "US203": "Çevre ve Enerji",
                    "US209": "İletişim Tekniği",
                    "US205": "Davranış Bilimine Giriş",
                    "US213": "İşletme Yönetimi",
                }
            }
        }
    },
    "5. Yarıyıl": {
        "mandatory": {
            "BM301": "Biçimsel Diller ve Soyut Makinalar",
            "BM303": "İşaretler ve Sistemler",
            "BM305": "İşletim Sistemleri",
            "BM307": "Bilgisayar Ağları I",
            "BM309": "Veritabanı Yönetim Sistemleri",
            "BM399": "Yaz Dönemi Stajı I",
        },
        "elective": {
            "SECTEK5YY": {
                "prefix": "MS",
                "required_count": 1,
                "courses": {
                    "MS301": "Endüstri İlişkileri",
                    "MS303": "Meslek Hastalıkları",
                    "MS305": "Teknoloji Felsefesi",
                    "MS311": "Kalite Yönetim Sistemleri ve Uygulaması",
                    "MS317": "İş Hukuku",
                    "MS319": "Mühendislik Ekonomisi",
                    "MS332": "Bilimsel Araştırma ve Rapor Yazma",
                    "MS321": "Bilişim Teknolojilerinde Yeni Gelişmeler",
                    "MS309": "Mühendislik Etiği",
                    "MS313": "Toplam Kalite Yönetimi",
                    "MS315": "İş Güvenliği",
                    "MS307": "Mühendisler İçin Yönetim",
                    "MS323": "Betik Dilleri",
                }
            }
        }
    },
    "6. Yarıyıl": {
        "mandatory": {
            "BM302": "Bilgisayar Ağları II",
            "BM304": "Mikroişlemciler",
            "BM306": "Sistem Programlama",
            "BM308": "Web Programlama",
            "BM310": "Yazılım Mühendisliği",
        },
        "elective": {
            "SECTEK6YY": {
                "prefix": "MS",
                "required_count": 1,
                "courses": {
                    "MS301": "Endüstri İlişkileri",
                    "MS303": "Meslek Hastalıkları",
                    "MS305": "Teknoloji Felsefesi",
                    "MS311": "Kalite Yönetim Sistemleri ve Uygulaması",
                    "MS317": "İş Hukuku",
                    "MS319": "Mühendislik Ekonomisi",
                    "MS332": "Bilimsel Araştırma ve Rapor Yazma",
                    "MS321": "Bilişim Teknolojilerinde Yeni Gelişmeler",
                    "MS309": "Mühendislik Etiği",
                    "MS313": "Toplam Kalite Yönetimi",
                    "MS315": "İş Güvenliği",
                    "MS307": "Mühendisler İçin Yönetim",
                    "MS323": "Betik Dilleri",
                    "MS331": "Mühendislikte Temel Bilgiler",
                }
            }
        }
    },
    "7. Yarıyıl": {
        "mandatory": {
            "BM401": "Bilgisayar Mühendisliği Proje Tasarımı",
            "BM499": "Yaz Dönemi Stajı II",
        },
        "elective": {
            "SECMES7YY": {
                "prefix": "BM",
                "required_count": 5,
                "courses": {
                    "BM429": "Optimizasyon",
                    "BM433": "Sayısal İşaret İşleme",
                    "BM447": "Sayısal Görüntü İşleme",
                    "BM480": "Derin Öğrenme",
                    "BM455": "Bulanık Mantığa Giriş",
                    "BM437": "Yapay Zeka",
                    "BM489": "Programlanabilir Mantık Denetleyiciler",
                    "BM441": "Bilgisayar Güvenliğine Giriş",
                    "BM449": "Ağ Güvenliğine Giriş",
                    "BM472": "Ağ Programlama",
                    "BM481": "Sanallaştırma Teknolojileri",
                    "BM478": "Python İle Veri Bilimine Giriş",
                    "BM471": "Gömülü Sistem Uygulamaları",
                    "BM482": "Yazılım Gereksinimleri Mühendisliği",
                    "BM485": "Dosya Organizasyonu",
                    "BM486": "Sayısal Sistem Tasarım",
                    "BM487": "Nesnelerin İnterneti",
                    "BM488": "Veri Analizi ve Tahminleme Yöntemleri",
                    "BM490": "Bilgi Güvenliği",
                    "BM491": "Sistem Biyolojisi",
                    "BM492": "Tıbbi İstatistik ve Tıp Bilimine Giriş",
                    "BM493": "Veri İletişimi",
                    "BM494": "Kablosuz Haberleşme",
                    "BM495": "İleri Gömülü Sistem Uygulamaları",
                    "BM422": "Biyobilişime Giriş",
                    "BM438": "Yurtdışı Staj Etkinliği",
                    "BM428": "Oyun Programlamaya Giriş",
                    "BM459": "Yazılım Test Mühendisliği",
                    "BM475": "Kurumsal Java",
                    "BM479": "Kompleks Ağ Analizi",
                    "BM423": "Bulanık Mantık ve Yapay Sinir Ağlarına Giriş",
                    "BM435": "Veri Madenciliği",
                    "BM463": "İleri Sistem Programlama",
                    "BM440": "Veri Tabanı Tasarımı ve Uygulamaları",
                    "BM457": "Bilgisayar Aritmetiği ve Otomata",
                    "BM442": "Görsel Programlama",
                    "BM430": "Proje Yönetimi",
                    "BM469": "Makine Öğrenmesine Giriş",
                    "BM424": "Derleyici Tasarımı",
                    "BM451": "Kontrol Sistemlerine Giriş",
                    "BM432": "Robotik",
                    "BM434": "Sayısal Kontrol Sistemleri",
                    "BM465": "Mikrodenetleyiciler ve Uygulamaları",
                    "BM420": "Bilgisayar Mimarileri",
                    "BM431": "Örüntü Tanıma",
                    "BM426": "Gerçek Zamanlı Ağ Sistemleri",
                    "BM436": "Sistem Simülasyonu",
                    "BM461": "Coğrafi Bilgi Sistemleri",
                    "BM474": "ERP Uygulamaları",
                    "BM427": "İnternet Mühendisliği",
                    "BM453": "İçerik Yönetim Sistemleri",
                    "BM439": "Bilgisayar Görmesi",
                    "BM425": "Erp Sistemleri",
                    "BM473": "Karar Destek Sistemleri",
                    "BM443": "Mobil Programlama",
                    "BM445": "Java Programlama",
                    "BM470": "İleri Java Programlama",
                    "BM496": "Bilgi Mühendisliği ve Büyük Veriye Giriş",
                    "BM421": "Bilgisayar Grafiği",
                    "BM477": "Graf Teorisi",
                    "BM444": "Yazılım Tasarım Kalıpları",
                    "BM467": "Kodlama Teorisi ve Kriptografi",
                    "BM476": "Açık Kaynak Programlama",
                    "MTH401": "LLM tabanlı Soru-Cevap Sistemleri",
                }
            }
        }
    },
    "8. Yarıyıl": {
        "mandatory": {
            "BM498": "Mezuniyet Tezi",
        },
        "elective": {
            "SECMES8YY": {
                "prefix": "BM",
                "required_count": 5,
                "courses": {
                    "BM429": "Optimizasyon",
                    "BM433": "Sayısal İşaret İşleme",
                    "BM447": "Sayısal Görüntü İşleme",
                    "BM480": "Derin Öğrenme",
                    "BM455": "Bulanık Mantığa Giriş",
                    "BM437": "Yapay Zeka",
                    "BM489": "Programlanabilir Mantık Denetleyiciler",
                    "BM441": "Bilgisayar Güvenliğine Giriş",
                    "BM449": "Ağ Güvenliğine Giriş",
                    "BM472": "Ağ Programlama",
                    "BM481": "Sanallaştırma Teknolojileri",
                    "BM478": "Python İle Veri Bilimine Giriş",
                    "BM471": "Gömülü Sistem Uygulamaları",
                    "BM482": "Yazılım Gereksinimleri Mühendisliği",
                    "BM485": "Dosya Organizasyonu",
                    "BM486": "Sayısal Sistem Tasarım",
                    "BM487": "Nesnelerin İnterneti",
                    "BM488": "Veri Analizi ve Tahminleme Yöntemleri",
                    "BM490": "Bilgi Güvenliği",
                    "BM491": "Sistem Biyolojisi",
                    "BM492": "Tıbbi İstatistik ve Tıp Bilimine Giriş",
                    "BM493": "Veri İletişimi",
                    "BM494": "Kablosuz Haberleşme",
                    "BM495": "İleri Gömülü Sistem Uygulamaları",
                    "BM422": "Biyobilişime Giriş",
                    "BM438": "Yurtdışı Staj Etkinliği",
                    "BM428": "Oyun Programlamaya Giriş",
                    "BM459": "Yazılım Test Mühendisliği",
                    "BM475": "Kurumsal Java",
                    "BM479": "Kompleks Ağ Analizi",
                    "BM423": "Bulanık Mantık ve Yapay Sinir Ağlarına Giriş",
                    "BM435": "Veri Madenciliği",
                    "BM463": "İleri Sistem Programlama",
                    "BM440": "Veri Tabanı Tasarımı ve Uygulamaları",
                    "BM457": "Bilgisayar Aritmetiği ve Otomata",
                    "BM442": "Görsel Programlama",
                    "BM430": "Proje Yönetimi",
                    "BM469": "Makine Öğrenmesine Giriş",
                    "BM424": "Derleyici Tasarımı",
                    "BM451": "Kontrol Sistemlerine Giriş",
                    "BM432": "Robotik",
                    "BM434": "Sayısal Kontrol Sistemleri",
                    "BM465": "Mikrodenetleyiciler ve Uygulamaları",
                    "BM420": "Bilgisayar Mimarileri",
                    "BM431": "Örüntü Tanıما",
                    "BM426": "Gerçek Zamanlı Ağ Sistemleri",
                    "BM436": "Sistem Simülasyonu",
                    "BM461": "Coğrafi Bilgi Sistemleri",
                    "BM474": "ERP Uygulamaları",
                    "BM427": "İنternet Mühendisliği",
                    "BM453": "İçerik Yönetim Sistemleri",
                    "BM439": "Bilgisayar Görmesi",
                    "BM425": "Erp Sistemleri",
                    "BM473": "Karar Destek Sistemleri",
                    "BM443": "Mobil Programlama",
                    "BM445": "Java Programlama",
                    "BM470": "İleri Java Programlama",
                    "BM496": "Bilgi Mühendisliği ve Büyük Veriye Giriş",
                    "BM421": "Bilgisayar Grafiği",
                    "BM477": "Graf Teorisi",
                    "BM444": "Yazılım Tasarım Kalıpları",
                    "BM467": "Kodlama Teorisi ve Kriptografi",
                    "BM476": "Açık Kaynak Programlama",
                    "MTH401": "LLM tabanlı Soru-Cevap Sistemleri",
                }
            }
        }
    }
}

def extract_text_from_docx(docx_path):
    try:
        text = docx2txt.process(docx_path)
        return text if text.strip() else "Dosyada çıkarılabilir metin bulunamadı."
    except Exception as e:
        return f"Metin çıkarma hatası: {str(e)}"

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n+', '\n', text)
    text = '\n'.join(line.strip() for line in text.splitlines() if line.strip())
    return text

def extract_gpa(text):
    pattern = r"Genel\s*(\d+\.\d+)\s*(\d+\.\d+)\s*(\d+\.\d+)\s*(\d+\.\d+)"
    matches = re.findall(pattern, text)
    if len(matches) >= 8:
        try:
            gpa = float(matches[7][3])
            return gpa
        except ValueError:
            return None
    return None

def check_akts(text):
    pattern = r"Dönem Sonu\s*(\d+\.\d+)\s*(\d+\.\d+)\s*(\d+\.\d+)\s*(\d+\.\d+)"
    matches = re.findall(pattern, text)
    warnings = []
    if len(matches) >= 8:
        for i, match in enumerate(matches[:8], start=1):
            try:
                second_number = float(match[1])
                if second_number < 30.0:
                    warnings.append({
                        "semester": f"{i}. Yarıyıl",
                        "message": f"{i}. Yarıyıl'da AKTS eksikliği var: {second_number} < 30.0"
                    })
            except ValueError:
                warnings.append({
                    "semester": f"{i}. Yarıyıl",
                    "message": f"{i}. Yarıyıl'da AKTS değeri geçersiz: {match[1]}"
                })
    else:
        warnings.append({
            "semester": "Genel",
            "message": f"Dönem Sonu eşleşmeleri 8'den az: Yalnızca {len(matches)} eşleşme bulundu."
        })
    return warnings

def extract_courses_from_text(text):
    patterns = [
        r'(BM\d{3})\s+(.+?)\s+(?:[0-9]+\.[0-9]+\s+){2}([A-Z]{2}|YT|YZ)',
        r'(AIB\d{3})\s+(.+?)\s+(?:[0-9]+\.[0-9]+\s+){2}([A-Z]{2})',
        r'(TDB\d{3})\s+(.+?)\s+(?:[0-9]+\.[0-9]+\s+){2}([A-Z]{2})',
        r'(FIZ\d{3})\s+(.+?)\s+(?:[0-9]+\.[0-9]+\s+){2}([A-Z]{2})',
        r'(MAT\d{3})\s+(.+?)\s+(?:[0-9]+\.[0-9]+\s+){2}([A-Z]{2})',
        r'(ING\d{3})\s+(.+?)\s+(?:[0-9]+\.[0-9]+\s+){2}([A-Z]{2})',
        r'(KRP\d{3})\s+(.+?)\s+(?:[0-9]+\.[0-9]+\s+){2}([A-Z]{2})',
        r'(US\d{3})\s+(.+?)\s+(?:[0-9]+\.[0-9]+\s+){2}([A-Z]{2})',
        r'(MS\d{3})\s+(.+?)\s+(?:[0-9]+\.[0-9]+\s+){2}([A-Z]{2})',
        r'(MTH\d{3})\s+(.+?)\s+(?:[0-9]+\.[0-9]+\s+){2}([A-Z]{2})',
        r'(BM\d{3})\s+(.+?)\s+([A-Z]{2}|YT|YZ)',
        r'(AIB\d{3})\s+(.+?)\s+([A-Z]{2})',
        r'(TDB\d{3})\s+(.+?)\s+([A-Z]{2})',
        r'(FIZ\d{3})\s+(.+?)\s+([A-Z]{2})',
        r'(MAT\d{3})\s+(.+?)\s+([A-Z]{2})',
        r'(ING\d{3})\s+(.+?)\s+([A-Z]{2})',
        r'(KRP\d{3})\s+(.+?)\s+([A-Z]{2})',
        r'(US\d{3})\s+(.+?)\s+([A-Z]{2})',
        r'(MS\d{3})\s+(.+?)\s+([A-Z]{2})',
        r'(MTH\d{3})\s+(.+?)\s+([A-Z]{2})',
        r'(BM\d{3}|AIB\d{3}|TDB\d{3}|FIZ\d{3}|MAT\d{3}|ING\d{3}|KRP\d{3}|US\d{3}|MS\d{3}|MTH\d{3})\s+(.+?)\s+(?:[0-9]+\.[0-9]+\s+){0,2}([A-Z]{2}|YT|YZ)',
    ]

    combined_pattern = '|'.join(patterns)
    courses = []
    text_for_courses = ' '.join(text.splitlines())

    for match in re.finditer(combined_pattern, text_for_courses):
        if match.group(1):
            course_code = match.group(1)
            course_name = match.group(2).strip()
            grade = match.group(3)
        elif match.group(4):
            course_code = match.group(4)
            course_name = match.group(5).strip()
            grade = match.group(6)
        elif match.group(7):
            course_code = match.group(7)
            course_name = match.group(8).strip()
            grade = match.group(9)
        elif match.group(10):
            course_code = match.group(10)
            course_name = match.group(11).strip()
            grade = match.group(12)
        elif match.group(13):
            course_code = match.group(13)
            course_name = match.group(14).strip()
            grade = match.group(15)
        elif match.group(16):
            course_code = match.group(16)
            course_name = match.group(17).strip()
            grade = match.group(18)
        elif match.group(19):
            course_code = match.group(19)
            course_name = match.group(20).strip()
            grade = match.group(21)
        elif match.group(22):
            course_code = match.group(22)
            course_name = match.group(23).strip()
            grade = match.group(24)
        elif match.group(25):
            course_code = match.group(25)
            course_name = match.group(26).strip()
            grade = match.group(27)
        elif match.group(28):
            course_code = match.group(28)
            course_name = match.group(29).strip()
            grade = match.group(30)
        elif match.group(31):
            course_code = match.group(31)
            course_name = match.group(32).strip()
            grade = match.group(33)
        elif match.group(34):
            course_code = match.group(34)
            course_name = match.group(35).strip()
            grade = match.group(36)
        elif match.group(37):
            course_code = match.group(37)
            course_name = match.group(38).strip()
            grade = match.group(39)
        elif match.group(40):
            course_code = match.group(40)
            course_name = match.group(41).strip()
            grade = match.group(42)
        elif match.group(43):
            course_code = match.group(43)
            course_name = match.group(44).strip()
            grade = match.group(45)
        elif match.group(46):
            course_code = match.group(46)
            course_name = match.group(47).strip()
            grade = match.group(48)
        elif match.group(49):
            course_code = match.group(49)
            course_name = match.group(50).strip()
            grade = match.group(51)
        elif match.group(52):
            course_code = match.group(52)
            course_name = match.group(53).strip()
            grade = match.group(54)
        elif match.group(55):
            course_code = match.group(55)
            course_name = match.group(56).strip()
            grade = match.group(57)
        elif match.group(58):
            course_code = match.group(58)
            course_name = match.group(59).strip()
            grade = match.group(60)
        elif match.group(61):
            course_code = match.group(61)
            course_name = match.group(62).strip()
            grade = match.group(63)

        course_name = re.sub(r'\d+\.\d+\s+\d+\.\d+', '', course_name).strip()
        course_name = re.sub(r'[:]', '', course_name).strip()

        # التحقق من استخراج المادة MTH401
        if course_code == "MTH401":
            print(f"تم استخراج المادة: {course_code} - {course_name} - {grade}")

        courses.append({
            "code": course_code,
            "name": course_name,
            "grade": grade
        })

    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        match = re.match(
            r'(BM\d{3}|AIB\d{3}|TDB\d{3}|FIZ\d{3}|MAT\d{3}|ING\d{3}|KRP\d{3}|US\d{3}|MS\d{3}|MTH\d{3})\s+(.+?)$',
            line)
        if match:
            course_code = match.group(1)
            course_name = match.group(2).strip()
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                grade_match = re.match(r'([A-Z]{2}|YT|YZ)\s*:راسب$', next_line)
                if grade_match:
                    grade = grade_match.group(1)
                    if not any(course['code'] == course_code for course in courses):
                        # التحقق من استخراج المادة MTH401
                        if course_code == "MTH401":
                            print(f"تم استخراج المادة (نمط بديل): {course_code} - {course_name} - {grade}")
                        courses.append({
                            "code": course_code,
                            "name": re.sub(r'[:]', '', course_name).strip(),
                            "grade": grade
                        })
                    i += 2
                else:
                    i += 1
            else:
                i += 1
        else:
            i += 1

    failed_courses = []
    failed_elective_requirements = []
    gpa_requirements = []
    akts_warnings = check_akts(text)
    semester_course_status = {}

    gpa = extract_gpa(text)
    if gpa is not None:
        if gpa < 2.50:
            gpa_requirements.append({
                "message": f"Genel Not Ortalaması {gpa:.2f} olarak hesaplandı. Mezuniyet için Genel Not Ortalaması en az 2.50 olmalıdır."
            })
    else:
        gpa_requirements.append({
            "message": "Genel Not Ortalaması (8. eşleşme) dosyada bulunamadı veya eşleşme sayısı 8'den az."
        })

    mandatory_courses_7_8 = {"BM401", "BM499", "BM498"}

    # لتتبع المواد الاختيارية المجتازة للفصلين 7 و8 فقط لتجنب التكرار في الإجمالي
    passed_electives_bm_total = set()  # لتتبع المواد المجتازة من BM أو MTH عبر الفصلين 7 و8
    passed_elective_bm_7 = 0
    passed_elective_bm_8 = 0

    # التحقق من المواد الإجبارية والاختيارية لكل فصل مع تخزين الحالة
    for semester, requirements in REQUIRED_COURSES_BY_SEMESTER.items():
        semester_course_status[semester] = {"mandatory": {}, "elective": {}}

        # الدروس الإجبارية
        for course_code, course_name in requirements["mandatory"].items():
            found = False
            for course in courses:
                if course["code"] == course_code:
                    found = True
                    status = "Başarılı" if course["grade"] != "FF" else "Başarısız"
                    semester_course_status[semester]["mandatory"][course_code] = {
                        "name": course_name,
                        "status": status,
                        "grade": course["grade"]
                    }
                    if course["grade"] == "FF":
                        failed_courses.append({
                            "semester": semester,
                            "code": course_code,
                            "name": course_name,
                            "grade": "FF",
                            "message": f"{semester} içinde '{course_name}' dersi FF ile başarısız."
                        })
                    break
            if not found:
                semester_course_status[semester]["mandatory"][course_code] = {
                    "name": course_name,
                    "status": "Eksik",
                    "grade": "Alınmadı"
                }
                failed_courses.append({
                    "semester": semester,
                    "code": course_code,
                    "name": course_name,
                    "grade": "Alınmadı",
                    "message": f"{semester} içinde '{course_name}' dersi eksik."
                })

        # الدروس الاختيارية
        for elective_code, elective_info in requirements["elective"].items():
            prefix = elective_info["prefix"]
            required_count = elective_info["required_count"]
            elective_courses = elective_info["courses"]

            passed_count = 0
            failed_in_elective = []
            taken_electives = []  # لتخزين المواد الاختيارية التي تم أخذها

            for course in courses:
                # التحقق من المواد الاختيارية بناءً على الـ prefix أو MTH للفصلين 7 و8
                if semester in ["7. Yarıyıl", "8. Yarıyıl"]:
                    if (course["code"].startswith("BM") or course["code"].startswith("MTH")) and course["code"] in elective_courses:
                        if course["code"] in mandatory_courses_7_8:
                            continue
                        status = "Başarılı" if course["grade"] != "FF" else "Başarısız"
                        taken_electives.append({
                            "code": course["code"],
                            "name": elective_courses[course["code"]],
                            "status": status,
                            "grade": course["grade"]
                        })
                        if course["grade"] != "FF":
                            passed_count += 1
                            if semester == "7. Yarıyıl":
                                passed_elective_bm_7 += 1
                                passed_electives_bm_total.add(course["code"])
                            elif semester == "8. Yarıyıl":
                                passed_elective_bm_8 += 1
                                passed_electives_bm_total.add(course["code"])
                        else:
                            failed_in_elective.append({
                                "semester": semester,
                                "code": course["code"],
                                "name": elective_courses[course["code"]],
                                "grade": "FF",
                                "message": f"{semester} içinde '{elective_courses[course['code']]}' seçmeli dersi FF ile başarısız."
                            })
                else:
                    if course["code"].startswith(prefix) and course["code"] in elective_courses:
                        status = "Başarılı" if course["grade"] != "FF" else "Başarısız"
                        taken_electives.append({
                            "code": course["code"],
                            "name": elective_courses[course["code"]],
                            "status": status,
                            "grade": course["grade"]
                        })
                        if course["grade"] != "FF":
                            passed_count += 1
                        else:
                            failed_in_elective.append({
                                "semester": semester,
                                "code": course["code"],
                                "name": elective_courses[course["code"]],
                                "grade": "FF",
                                "message": f"{semester} içinde '{elective_courses[course['code']]}' seçmeli dersi FF ile başarısız."
                            })

            semester_course_status[semester]["elective"] = {
                "required_count": required_count,
                "passed_count": passed_count,
                "status": "Tamamlandı" if passed_count >= required_count else "Eksik",
                "taken_electives": taken_electives
            }

            if passed_count < required_count:
                failed_courses.extend(failed_in_elective)
                if passed_count == 0:
                    failed_elective_requirements.append({
                        "semester": semester,
                        "message": f"{semester} için {required_count} adet {prefix} ile başlayan seçmeli ders geçmeniz gerekiyor, ancak hiçbiri alınmadı veya geçilemedi."
                    })
                else:
                    failed_elective_requirements.append({
                        "semester": semester,
                        "message": f"{semester} için {required_count} adet {prefix} ile başlayan seçmeli ders geçmeniz gerekiyor, ancak sadece {passed_count} tanesi geçildi."
                    })

    # التحقق من مجموع المواد الاختيارية للفصل السابع والثامن (BM و MTH)
    total_passed_elective_bm = len(passed_electives_bm_total)
    required_total_elective_bm = 10
    if total_passed_elective_bm < required_total_elective_bm:
        remaining = required_total_elective_bm - total_passed_elective_bm
        failed_elective_requirements.append({
            "semester": "7. ve 8. Yarıyıl",
            "message": f"7. ve 8. Yarıyıl için toplam {required_total_elective_bm} adet BM veya MTH ile başlayan seçmeli ders geçmeniz gerekiyor, ancak sadece {total_passed_elective_bm} tanesi geçildi. {remaining} ders daha geçmeniz gerekiyor."
        })

    elective_bm_summary = {
        "passed_elective_bm_7": passed_elective_bm_7,
        "passed_elective_bm_8": passed_elective_bm_8,
        "total_passed_elective_bm": total_passed_elective_bm,
        "required_total_elective_bm": required_total_elective_bm
    }

    # التحقق من شروط التخرج
    graduation_status = {
        "is_eligible": False,
        "message": ""
    }

    # الشرط الأول: اجتياز جميع المواد الإجبارية والاختيارية
    courses_condition = len(failed_courses) == 0 and len(failed_elective_requirements) == 0

    # الشرط الثاني: المعدل العام أعلى من 2.50
    gpa_condition = gpa is not None and gpa >= 2.50

    # الشرط الثالث: عدد AKTS مكتمل
    akts_condition = len(akts_warnings) == 0

    # التحقق من جميع الشروط
    if courses_condition and gpa_condition and akts_condition:
        graduation_status["is_eligible"] = True
        graduation_status["message"] = "Tebrikler! Tüm mezuniyet şartlarını karşılıyorsunuz. Mezun olmaya hak kazandınız!"
    else:
        reasons = []
        if not courses_condition:
            reasons.append("Bazı zorunlu veya seçmeli derslerde eksiklik veya başarısızlık var.")
        if not gpa_condition:
            reasons.append(f"Genel Not Ortalaması ({gpa if gpa is not None else 'Bilinmiyor'}) 2.50'nin altında.")
        if not akts_condition:
            reasons.append("AKTS eksikliği mevcut.")
        graduation_status["message"] = "Mezuniyet şartlarını karşılamıyorsunuz. Eksiklikler: " + ", ".join(reasons)

    return courses, failed_courses, failed_elective_requirements, gpa, gpa_requirements, akts_warnings, elective_bm_summary, semester_course_status, graduation_status

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "Hiçbir dosya yüklenmedi."

    file = request.files['file']
    if file.filename == '':
        return "Dosya seçilmedi."

    if file and file.filename.endswith('.docx'):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        try:
            file.save(file_path)
        except PermissionError as e:
            return f"Dosya kaydetme hatası: {str(e)}. Yazma izninizin olduğundan emin olun."

        text = extract_text_from_docx(file_path)
        text = clean_text(text)
        all_courses, failed_courses, failed_elective_requirements, gpa, gpa_requirements, akts_warnings, elective_bm_summary, semester_course_status, graduation_status = extract_courses_from_text(
            text)

        return render_template('index.html', extracted_text=text,
                               failed_courses=failed_courses,
                               failed_elective_requirements=failed_elective_requirements,
                               gpa=gpa, gpa_requirements=gpa_requirements,
                               akts_warnings=akts_warnings,
                               elective_bm_summary=elective_bm_summary,
                               semester_course_status=semester_course_status,
                               graduation_status=graduation_status)
    else:
        return "Lütfen bir Word (.docx) dosyası yükleyin."

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
