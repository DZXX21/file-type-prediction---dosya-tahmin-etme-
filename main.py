import os
import mimetypes
import zipfile

def read_file_header(file_path, num_bytes=512):
    """Dosyanın başlık kısmını (magic bytes) okur."""
    try:
        with open(file_path, 'rb') as file:
            return file.read(num_bytes)
    except Exception:
        return None

def analyze_magic_bytes(header):
    """Magic bytes'lara göre dosya türünü analiz eder."""
    if not header:
        return "Dosya okunamadı"
    if header.startswith(b'%PDF'):
        return "PDF Belgesi"
    elif header.startswith(b'\xFF\xD8\xFF'):
        return "JPEG Görseli"
    elif header.startswith(b'\x89PNG'):
        return "PNG Görseli"
    elif header[:4] == b'PK\x03\x04':  # ZIP dosyası
        return "ZIP Arşivi"
    elif header[:6] == b'7z\xBC\xAF\x27\x1C':  # Seven Zip dosyası
        return "Seven Zip Arşivi (.7z)"
    elif header[:8] == b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1':  # Eski Microsoft Office dosyaları
        return "Microsoft Word Belgesi (.doc)"
    elif all(32 <= b <= 126 or b in (9, 10, 13) for b in header[:100]):
        return "Düz Metin Dosyası"
    return "Bilinmeyen Tür"

def analyze_zip_contents(file_path):
    """ZIP dosyasının içeriğini analiz ederek türü belirler."""
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            
            # Excel dosyasına özgü bileşenler
            if "xl/workbook.xml" in file_list and any(f.startswith("xl/worksheets/") for f in file_list):
                return "Microsoft Excel Belgesi (.xlsx)"
            
            # Word dosyasına özgü bileşenler
            if "word/document.xml" in file_list:
                return "Microsoft Word Belgesi (.docx)"
            
            # PowerPoint dosyasına özgü bileşenler
            if "ppt/presentation.xml" in file_list:
                return "Microsoft PowerPoint Belgesi (.pptx)"
            
            return "ZIP Arşivi: Belirsiz İçerik"
    except zipfile.BadZipFile:
        return "ZIP formatında değil"

def guess_file_type(file_path):
    """Dosyanın türünü tahmin eder."""
    header = read_file_header(file_path)
    magic_type = analyze_magic_bytes(header)

    if magic_type == "ZIP Arşivi":
        zip_contents = analyze_zip_contents(file_path)
        return zip_contents

    return magic_type

def suggest_extension(file_type):
    """Dosya türüne uygun önerilen uzantıyı döndür."""
    if "PDF" in file_type:
        return ".pdf"
    elif "JPEG" in file_type:
        return ".jpg"
    elif "PNG" in file_type:
        return ".png"
    elif "Excel" in file_type:
        return ".xlsx"
    elif "Word" in file_type:
        if ".docx" in file_type:
            return ".docx"
        elif ".doc" in file_type:
            return ".doc"
    elif "PowerPoint" in file_type:
        if ".pptx" in file_type:
            return ".pptx"
        elif ".ppt" in file_type:
            return ".ppt"
    elif "Seven Zip" in file_type:
        return ".7z"
    elif "ZIP Arşivi: Belirsiz İçerik" in file_type:
        return ".zip"
    elif "Metin" in file_type or "Düz Metin Dosyası" in file_type:
        return ".txt"
    return None

def rename_files(directory="."):
    """Dosya türlerini analiz eder ve uygun bir uzantıyla yeniden adlandırır."""
    renamed_count = 0  # Toplam yeniden adlandırma sayacı

    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        if os.path.isfile(file_path):
            # Dosya türünü tespit et
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type:
                file_type = mime_type
            else:
                file_type = guess_file_type(file_path)

            # Yeni uzantıyı öner
            suggested_extension = suggest_extension(file_type)
            if suggested_extension:
                base_name, ext = os.path.splitext(file_name)
                new_name = base_name + suggested_extension
                new_path = os.path.join(directory, new_name)

                # Eski ve yeni ad farklıysa yeniden adlandır
                if file_path != new_path:
                    try:
                        os.rename(file_path, new_path)
                        renamed_count += 1
                        print(f"'{file_name}' dosyası '{new_name}' olarak yeniden adlandırıldı.")
                    except Exception as e:
                        print(f"'{file_name}' dosyası yeniden adlandırılamadı: {e}")

    print(f"\nToplamda {renamed_count} dosya yeniden adlandırıldı.")  # Toplam sayıyı yazdırma

# Mevcut dizindeki dosyaları analiz ve yeniden adlandır
rename_files()
