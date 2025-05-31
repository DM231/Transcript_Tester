from flask import Flask, render_template, request
import docx2txt
import re
import os
import logging

# Configure logging
logging.basicConfig(
    filename='app.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(os.path.expanduser('~'), 'Desktop', 'Uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

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
                    "US215": "Kultur Tarihi",
                    "US217": "Sanat Tarihi",
                    "US219": "Sivil Toplum Organizasyonları",
                    "US221": "Uygarlık Tarihi",
                    "US201": "Bilim Tarihi ve Felsefesi",
                    "US207": "Girişimcilik",
                    "US225": "Girişimcilik I",
                    "US227": "Girişimcilik II",
                    "US203": "Çevre ve Enerji",
                    "US209": "İletişim Tekنیği",
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
                    "MS332": "Bilimsel Araştırma ve Rapor Yazما",
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
                    "BM480": "Derin Öğrenمه",
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
                    "BM488": "Verي Analizi و",
                    "BM490": "Bilgi Güvenliği",
                    "BM491": "Sistem Biyolojisi",
                    "BM492": "Tıbbi İstatistik و Tıp Bilimine Giriş",
                    "BM493": "Veri İletişimi",
                    "BM494": "Kablosuz Haberleşme",
                    "BM495": "İleri Gömülü Sistem Uygulamaları",
                    "BM422": "Biyobilişime Giriş",
                    "BM438": "Yurtdışı Staj Etkinliği",
                    "BM428": "Oyun Programlamaya Giriş",
                    "BM459": "Yazılım Test Mühendisliği",
                    "BM475": "Kurumsal Java",
                    "BM479": "Kompleks Ağ Analizi",
                    "BM423": "Bulanık Mantık و Yapay Sinir Ağlarına Giriş",
                    "BM435": "Veri Madenciliği",
                    "BM463": "İleri Sistem Programlama",
                    "BM440": "Veritabanı Tasarımı ve Uygulamaları",
                    "BM457": "Bilgisayar Aritmetiği ve Otomata",
                    "BM442": "Görsel Programlama",
                    "BM430": "Proje Yönetimi",
                    "BM469": "Makine Öğrenmesine Giriş",
                    "BM424": "Derleyici Tasarımı",
                    "BM451": "Kontrol Sistemlerine Giriş",
                    "BM432": "Robotik",
                    "BM434": "Sayısal Kontrol Sistemleri",
                    "BM465": "Mikrokontrolcüler و Uygulamaları",
                    "BM420": "Bilgisayar Mimarileri",
                    "BM431": "Örüntü Tanıما",
                    "BM426": "Gerçek Zamanlı Ağ Sistemleri",
                    "BM436": "Sistem Simülasyonu",
                    "BM461": "Coğrafي Bilgi Sistemleri",
                    "BM474": "ERP Uygulamaları",
                    "BM427": "İنternet Mühendisliği",
                    "BM453": "İçerik Yönetim Sistemleri",
                    "BM439": "Bilgisayar Görmesi",
                    "BM425": "ERP Sistemleri",
                    "BM473": "Karار Destek Sistemleri",
                    "BM443": "Mobil Programlama",
                    "BM445": "Java Programlama",
                    "BM470": "İleri Java Programlama",
                    "BM496": "Bilgi Mühendisliği و Büyük Veriye Giriş",
                    "BM421": "Bilgisayar Grafیği",
                    "BM477": "Graf Teorisi",
                    "BM444": "Yazılım Tasarım Kalıpları",
                    "BM467": "Kodlama Teorisi و Kriptografi",
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
                    "BM480": "Derin Öğrenمه",
                    "BM455": "Bulanık Mantığa Giriş",
                    "BM437": "Yapay Zeka",
                    "BM489": "Programlanabilir Mantık Denetleyiciler",
                    "BM441": "Bilgisayar Güvenliğine Giriş",
                    "BM449": "Ağ Güvenliğine Giriş",
                    "BM472": "Ağ Programlama",
                    "BM481": "Sanallaştırma Teknolojileri",
                    "BM478": "Python İle Veri Bilimine Giriş",
                    "BM471": "Gömülü Sistem Uygulamaları",
                    "BM482": "Yazılım Gereksینimleri Mühendisliği",
                    "BM485": "Dosya Organizasyonu",
                    "BM486": "Sayısal Sistem Tasarım",
                    "BM487": "Nesnelerin İnterneti",
                    "BM488": "Verي Analizi و Tahminleme Yöntemleri",
                    "BM490": "Bilgi Güvenliği",
                    "BM491": "Sistem Biyolojisi",
                    "BM492": "Tıbbi İstatistik و Tıp Bilimine Giriş",
                    "BM493": "Verي İletişimi",
                    "BM494": "Kablosuz Haberleşme",
                    "BM495": "İleri Gömülü Sistem Uygulamaları",
                    "BM422": "Biyobilişime Giriş",
                    "BM438": "Yurtdışı Staj Etkinliği",
                    "BM428": "Oyun Programlamaya Giriş",
                    "BM459": "Yazılım Test Mühendisliği",
                    "BM475": "Kurumsal Java",
                    "BM479": "Kompleks Ağ Analizi",
                    "BM423": "Bulanık Mantık و Yapay Sinir Ağlarına Giriş",
                    "BM435": "Verي Madenciliği",
                    "BM463": "İleri Sistem Programlama",
                    "BM440": "Verي Tabanı Tasarımı و Uygulamaları",
                    "BM457": "Bilgisayar Aritmetiği و Otomata",
                    "BM442": "Görsel Programlama",
                    "BM430": "Proje Yönetimi",
                    "BM469": "Makine Öğrenmesine Giriş",
                    "BM424": "Derleyici Tasarımı",
                    "BM451": "Kontrol Sistemlerine Giriş",
                    "BM432": "Robotik",
                    "BM434": "Sayısal Kontrol Sistemleri",
                    "BM465": "Mikرودنetleyiciler و Uygulamaları",
                    "BM420": "Bilgisayar Mimarileri",
                    "BM431": "Örüntü Tanıما",
                    "BM426": "Gerçek Zamanlı Ağ Sistemleri",
                    "BM436": "Sistem Simülasyonu",
                    "BM461": "Coğrafي Bilgi Sistemleri",
                    "BM474": "ERP Uygulamaları",
                    "BM427": "İنternet Mühendisliği",
                    "BM453": "İçerik Yönetim Sistemleri",
                    "BM439": "Bilgisayar Görmesi",
                    "BM425": "Erp Sistemleri",
                    "BM473": "Karار Destek Sistemleri",
                    "BM443": "Mobil Programlama",
                    "BM445": "Java Programlama",
                    "BM470": "İleri Java Programlama",
                    "BM496": "Bilgi Mühendisliği و Büyük Veriye Giriş",
                    "BM421": "Bilgisayar Grafیği",
                    "BM477": "Graf Teorisi",
                    "BM444": "Yazılım Tasarım Kalıpları",
                    "BM467": "Kodlama Teorisi و Kriptografi",
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
        logging.error(f"Error extracting text from docx: {str(e)}")
        return f"Metin çıkarma hatası: {str(e)}"

def clean_text(text):
    try:
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n+', '\n', text)
        text = '\n'.join(line.strip() for line in text.splitlines() if line.strip())
        return text
    except Exception as e:
        logging.error(f"Error cleaning text: {str(e)}")
        return text

def extract_gpa(text):
    pattern = r"Genel\s*(\d+\.\d+)\s*(\d+\.\d+)\s*(\d+\.\d+)\s*(\d+\.\d+)"
    matches = re.findall(pattern, text)
    if matches:
        try:
            gpa = float(matches[-1][3])
            return gpa
        except (ValueError, IndexError) as e:
            logging.error(f"Error extracting GPA: {str(e)}")
            return None
    return None

def check_akts(text):
    # More flexible regex pattern to match AKTS values
    pattern = r"Dönem Sonu\s*(\d+\.\d+)\s*(\d+\.\d+|\S+)\s*(\d+\.\d+)\s*(\d+\.\d+)"
    matches = re.findall(pattern, text)
    warnings = []
    seen_semesters = set()  # Track semesters to avoid duplicates

    for i, match in enumerate(matches, start=1):
        semester = f"{i}. Yarıyıl"
        if semester in seen_semesters:
            logging.warning(f"Duplicate AKTS entry detected for {semester}")
            continue
        seen_semesters.add(semester)

        try:
            second_number = float(match[1])
            if second_number < 30.0:
                warnings.append({
                    "semester": semester,
                    "message": f"{semester}'da AKTS eksikliği var: {second_number} < 30.0"
                })
        except (ValueError, TypeError) as e:
            logging.error(f"Invalid AKTS value for {semester}: {match[1]} - Error: {str(e)}")
            warnings.append({
                "semester": semester,
                "message": f"{semester}'da AKTS değeri geçersiz: {match[1]}"
            })

    return warnings

def extract_courses_from_text(text):
    patterns = [
        r'(BM\d{3}|AIB\d{3}|TDB\d{3}|FIZ\d{3}|MAT\d{3}|ING\d{3}|KRP\d{3}|US\d{3}|MS\d{3}|MTH\d{3})\s+(.+?)\s+(?:[0-9]+\.[0-9]+\s+){2}([A-Z]{2}|YT|YZ)',
        r'(BM\d{3}|AIB\d{3}|TDB\d{3}|FIZ\d{3}|MAT\d{3}|ING\d{3}|KRP\d{3}|US\d{3}|MS\d{3}|MTH\d{3})\s+(.+?)\s+([A-Z]{2}|YT|YZ)',
        r'(MTH401)\s+(.+?)\s+(?:[0-9]+\.[0-9]+\s+){0,2}([A-Z]{2}|YT|YZ)',
    ]

    combined_pattern = '|'.join(patterns)
    courses = []
    text_for_courses = ' '.join(text.splitlines())

    for match in re.finditer(combined_pattern, text_for_courses):
        try:
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

            course_name = re.sub(r'\d+\.\d+\s+\d+\.\d+', '', course_name).strip()
            course_name = re.sub(r'[:]', '', course_name).strip()

            courses.append({
                "code": course_code,
                "name": course_name,
                "grade": grade
            })
        except Exception as e:
            logging.error(f"Error processing course match: {match.groups()} - Error: {str(e)}")
            continue

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
            "message": "Genel Not Ortalaması dosyada bulunamadı."
        })

    mandatory_courses_7_8 = {"BM401", "BM499", "BM498"}

    passed_electives_bm_total = set()
    passed_elective_bm_7 = 0
    passed_elective_bm_8 = 0

    graduation_status = {
        "is_eligible": False,
        "message": "",
        "mandatory_issues": [],
        "elective_issues": [],
        "gpa_issue": None,
        "akts_issues": [],
        "completed_semesters": 0
    }

    # Determine completed semesters based on AKTS data
    akts_pattern = r"Dönem Sonu\s*(\d+\.\d+)\s*(\d+\.\d+|\S+)\s*(\d+\.\d+)\s*(\d+\.\d+)"
    akts_matches = re.findall(akts_pattern, text)
    completed_semesters = 0
    valid_semesters = []

    for match in akts_matches:
        try:
            # Check if the second value is a valid number
            float(match[1])
            valid_semesters.append(match)
        except (ValueError, TypeError) as e:
            logging.error(f"Invalid AKTS value in match: {match} - Error: {str(e)}")
            continue

    completed_semesters = len(valid_semesters) if valid_semesters else 0
    graduation_status["completed_semesters"] = completed_semesters

    # Track unique missing courses to avoid duplicates
    added_missing_courses = set()

    # Check for missing semesters
    missing_semesters = []
    for sem_num in range(1, 9):
        sem_key = f"{sem_num}. Yarıyıl"
        if sem_num > completed_semesters:
            missing_semesters.append(sem_key)

            # Add missing mandatory courses for this semester
            for course_code, course_name in REQUIRED_COURSES_BY_SEMESTER[sem_key]["mandatory"].items():
                unique_key = f"{sem_key}_{course_code}"
                if unique_key not in added_missing_courses:
                    failed_courses.append({
                        "semester": sem_key,
                        "code": course_code,
                        "name": course_name,
                        "grade": "Alınmadı",
                        "message": f"{sem_key} henüz tamamlanmadı - '{course_name}' dersi alınmadı."
                    })
                    graduation_status["mandatory_issues"].append(
                        f"{sem_key} döneminde '{course_name}' dersi alınmadı."
                    )
                    added_missing_courses.add(unique_key)

            # Add missing elective requirements for this semester
            for elective_code, elective_info in REQUIRED_COURSES_BY_SEMESTER[sem_key]["elective"].items():
                prefix = elective_info["prefix"]
                required_count = elective_info["required_count"]
                if required_count > 0:
                    message = f"{sem_key} henüz tamamlanmadı - {required_count} adet {prefix} ile başlayan seçmeli ders alınmadı."
                    failed_elective_requirements.append({
                        "semester": sem_key,
                        "message": message
                    })
                    graduation_status["elective_issues"].append(message)

    failed_elective_courses = set()

    for semester, requirements in REQUIRED_COURSES_BY_SEMESTER.items():
        semester_num = int(semester.split('.')[0])
        if semester_num > completed_semesters:
            continue

        semester_course_status[semester] = {"mandatory": {}, "elective": {}}

        for course_code, course_name in requirements["mandatory"].items():
            found = False
            for course in courses:
                if course["code"] == course_code:
                    found = True
                    status = "Başarılı" if course["grade"] not in ["FF", "FD"] else "Başارısız"
                    semester_course_status[semester]["mandatory"][course_code] = {
                        "name": course_name,
                        "status": status,
                        "grade": course["grade"]
                    }
                    if course["grade"] in ["FF", "FD"]:
                        unique_key = f"{semester}_{course_code}"
                        if unique_key not in added_missing_courses:
                            failed_courses.append({
                                "semester": semester,
                                "code": course_code,
                                "name": course_name,
                                "grade": course["grade"],
                                "message": f"{semester} içinde '{course_name}' dersi {course['grade']} ile başarısız."
                            })
                            added_missing_courses.add(unique_key)
                    break
            if not found and semester_num <= completed_semesters:
                unique_key = f"{semester}_{course_code}"
                if unique_key not in added_missing_courses:
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
                        "message": f"{semester} içinde '{course_name}' dersi alınmadı."
                    })
                    added_missing_courses.add(unique_key)

        for elective_code, elective_info in requirements["elective"].items():
            prefix = elective_info["prefix"]
            required_count = elective_info["required_count"]
            elective_courses = elective_info["courses"]

            passed_count = 0
            failed_in_elective = []
            taken_electives = []

            for course in courses:
                if semester in ["7. Yarıyıl", "8. Yarıyıl"]:
                    if (course["code"].startswith("BM") or course["code"].startswith("MTH")) and course[
                        "code"] in elective_courses:
                        if course["code"] in mandatory_courses_7_8:
                            continue
                        status = "Başarılı" if course["grade"] not in ["FF", "FD"] else "Başارısız"
                        taken_electives.append({
                            "code": course["code"],
                            "name": elective_courses[course["code"]],
                            "status": status,
                            "grade": course["grade"]
                        })
                        if course["grade"] not in ["FF", "FD"]:
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
                                "grade": course["grade"],
                                "message": f"{semester} içinde '{elective_courses[course['code']]}' seçmeli dersi {course['grade']} ile başarısız."
                            })
                else:
                    if course["code"].startswith(prefix) and course["code"] in elective_courses:
                        status = "Başarılı" if course["grade"] not in ["FF", "FD"] else "Başارısız"
                        taken_electives.append({
                            "code": course["code"],
                            "name": elective_courses[course["code"]],
                            "status": status,
                            "grade": course["grade"]
                        })
                        if course["grade"] not in ["FF", "FD"]:
                            passed_count += 1
                        else:
                            failed_in_elective.append({
                                "semester": semester,
                                "code": course["code"],
                                "name": elective_courses[course["code"]],
                                "grade": course["grade"],
                                "message": f"{semester} içinde '{elective_courses[course['code']]}' seçmeli dersi {course['grade']} ile başarısız."
                            })
                            if prefix in ["US", "MS"] and course["code"] not in failed_elective_courses:
                                if prefix == "US" and semester == "3. Yarıyıl" and course["code"] in \
                                        REQUIRED_COURSES_BY_SEMESTER["4. Yarıyıl"]["elective"]["SECSOS4YY"]["courses"]:
                                    continue
                                failed_elective_courses.add(course["code"])
                                graduation_status["elective_issues"].append(
                                    f"{semester} döneminde '{elective_courses[course['code']]}' seçmeli dersinden {course['grade']} ile başarısız oldunuz."
                                )

            semester_course_status[semester]["elective"] = {
                "required_count": required_count,
                "passed_count": passed_count,
                "status": "Tamamlandı" if passed_count >= required_count else "Eksik",
                "taken_electives": taken_electives
            }

            if passed_count < required_count and semester_num <= completed_semesters:
                failed_courses.extend(failed_in_elective)
                if passed_count == 0:
                    message = f"{semester} için {required_count} adet {prefix} ile başlayan seçmeli ders geçmeniz gerekiyor, ancak hiçbiri alınmadı veya geçilemedi."
                    failed_elective_requirements.append({
                        "semester": semester,
                        "message": message
                    })
                    graduation_status["elective_issues"].append(message)
                else:
                    message = f"{semester} için {required_count} adet {prefix} ile başlayan seçmeli ders geçmeniz gerekiyor, ancak sadece {passed_count} tanesi geçildi."
                    failed_elective_requirements.append({
                        "semester": semester,
                        "message": message
                    })
                    graduation_status["elective_issues"].append(message)

    if completed_semesters >= 7:
        total_passed_elective_bm = len(passed_electives_bm_total)
        required_total_elective_bm = 10
        if total_passed_elective_bm < required_total_elective_bm:
            remaining = required_total_elective_bm - total_passed_elective_bm
            message = f"7. ve 8. Yarıyıl için toplam {required_total_elective_bm} adet BM veya MTH ile başlayan seçmeli ders geçmeniz gerekiyor, ancak sadece {total_passed_elective_bm} tanesi geçildi. {remaining} ders daha geçmeniz gerekiyor."
            failed_elective_requirements.append({
                "semester": "7. ve 8. Yarıyıl",
                "message": message
            })
            graduation_status["elective_issues"].append(message)

    elective_bm_summary = {
        "passed_elective_bm_7": passed_elective_bm_7,
        "passed_elective_bm_8": passed_elective_bm_8,
        "total_passed_elective_bm": len(passed_electives_bm_total),
        "required_total_elective_bm": 10 if completed_semesters >= 7 else 0
    }

    mandatory_failed_or_missing = [course for course in failed_courses if course["code"] in sum(
        [list(req["mandatory"].keys()) for req in REQUIRED_COURSES_BY_SEMESTER.values()], [])]
    graduation_status["mandatory_issues"] = list(dict.fromkeys(graduation_status["mandatory_issues"]))
    for course in mandatory_failed_or_missing:
        if course["grade"] == "Alınmadı":
            message = f"{course['semester']} döneminde '{course['name']}' dersi alınmadı."
            if message not in graduation_status["mandatory_issues"]:
                graduation_status["mandatory_issues"].append(message)
        else:
            message = f"{course['semester']} döneminde '{course['name']}' dersinden {course['grade']} ile başarısız oldunuz."
            if message not in graduation_status["mandatory_issues"]:
                graduation_status["mandatory_issues"].append(message)

    if gpa is None:
        if completed_semesters > 0:
            graduation_status["gpa_issue"] = "Genel Not Ortalaması dosyada bulunamadı."
        else:
            graduation_status["gpa_issue"] = "Henüz hiç dönem tamamlanmamış."
    elif gpa < 2.50:
        graduation_status["gpa_issue"] = f"Genel Not Ortalamanız ({gpa:.2f}) 2.50'nin altında."

    for akts_issue in akts_warnings:
        graduation_status["akts_issues"].append(
            f"{akts_issue['semester']} döneminde AKTS eksikliği var: {akts_issue['message']}")

    if missing_semesters:
        graduation_status["missing_semesters"] = missing_semesters
        graduation_status[
            "message"] = f"Henüz mezuniyet için gerekli tüm dönemleri tamamlamادınız. {completed_semesters}/8 dönem tamamlandı. Eksik dönemler: {', '.join(missing_semesters)}"
    else:
        graduation_status["missing_semesters"] = []

    if completed_semesters == 8:
        if not (graduation_status["mandatory_issues"] or graduation_status["elective_issues"] or graduation_status[
            "gpa_issue"] or graduation_status["akts_issues"]):
            graduation_status["is_eligible"] = True
            graduation_status[
                "message"] = "Tebrikler! Tüm mezuniyet şartlarını karşılıyorsunuz. Mezun olmaya hak kazandınız!"
        else:
            graduation_status["is_eligible"] = False
            graduation_status["message"] = "Mezun olamazsınız. Aşağıdaki eksiklikler mevcut:"
    else:
        graduation_status["is_eligible"] = False
        if completed_semesters > 0:
            graduation_status[
                "message"] = f"Henüz mezuniyet için gerekli tüm دورهleri tamamlamادınız. {completed_semesters}/8 دوره tamamlandı."
        else:
            graduation_status["message"] = "Henüz hiç دوره tamamlanmamış."

    return courses, failed_courses, failed_elective_requirements, gpa, gpa_requirements, akts_warnings, elective_bm_summary, semester_course_status, graduation_status

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "Hiçbir dosya yüklenmedi.", 400

    file = request.files['file']
    if file.filename == '':
        return "Dosya seçilmedi.", 400

    if file and file.filename.endswith('.docx'):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        try:
            file.save(file_path)
        except PermissionError as e:
            logging.error(f"Permission error saving file: {str(e)}")
            return f"Dosya kaydetme hatası: {str(e)}. Yazma izنiniz olduğundan emin olun.", 500

        try:
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
        except Exception as e:
            logging.error(f"Error processing uploaded file: {str(e)}")
            return f"Dosya işleme hatası: {str(e)}", 500
    else:
        return "Lütfen bir Word (.docx) dosyası yükleyin.", 400

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
