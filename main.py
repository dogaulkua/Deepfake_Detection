from transformers import pipeline
import requests
from PIL import Image
from io import BytesIO
import csv
import os

# Dil seçenekleri ve metinler
language_options = {
    "Türkçe": {
        "welcome": "Deepfake Tespit Sistemi'ne Hoş Geldiniz!",
        "language_prompt": "Lütfen bir dil seçiniz (Türkçe, English): ",
        "image_prompt": "Görsel yolunu veya URL'sini girin: ",
        "results_header": "Nihai Analiz Sonuçları:",
        "original_result": "Bu görsel orijinal olarak değerlendirildi.",
        "deepfake_result": "Görselde deepfake şüphesi tespit edildi!",
        "uncertainty": "Sonuçlar eşit görünüyor. Günümüzde deepfake tehlikeleri ve SDG bağlantıları:",
        "csv_saved": "Sonuçlar başarıyla kaydedildi.",
        "legal_rights": {
            "Türkiye": "Türk Ceza Kanunu'nun 243 ve 244. maddelerine göre kişisel verilerin manipülasyonu yasa dışıdır.",
            "global": "Deepfake içeriklerin kötüye kullanımı dünya genelinde yasal sorunlara yol açabilir."
        },
        "sdg_impacts": [
            "SDG 16: Barış, Adalet ve Güçlü Kurumlar - Deepfake'ler dezenformasyona neden olabilir.",
            "SDG 5: Toplumsal Cinsiyet Eşitliği - Özellikle kadınlar için suistimal riski yaratabilir.",
            "SDG 10: Eşitsizliklerin Azaltılması - Sosyal ayrışmayı derinleştirebilir."
        ],
        "moral_support": "Bu tür içeriklerin yasal yollarla çözülmesi çok önemlidir. Haklarınızı arayın!"
    },
    "English": {
        "welcome": "Welcome to the Deepfake Detection System!",
        "language_prompt": "Please select a language (Türkçe, English): ",
        "image_prompt": "Enter the image URL: ",
        "results_header": "Final Analysis Results:",
        "original_result": "This image is classified as original.",
        "deepfake_result": "Deepfake suspicion detected!",
        "uncertainty": "Scores are equal. Here's the importance of deepfake threats and SDG connections:",
        "csv_saved": "Results successfully saved.",
        "legal_rights": {
            "Türkiye": "Under Turkish Penal Code Articles 243 and 244, manipulation of personal data is illegal.",
            "global": "The misuse of deepfake content can lead to legal issues worldwide."
        },
        "sdg_impacts": [
            "SDG 16: Peace, Justice, and Strong Institutions - Deepfakes foster disinformation.",
            "SDG 5: Gender Equality - Risky for women in terms of exploitation.",
            "SDG 10: Reduced Inequalities - Can exacerbate social disparities."
        ],
        "moral_support": "Resolving such issues legally is crucial. Stand up for your rights!"
    }
}

# Modeli yükleme
def load_model():
    try:
        pipe = pipeline("image-classification", model="prithivMLmods/Deep-Fake-Detector-Model", framework="pt")
        print("Model successfully loaded.")
        return pipe
    except Exception as e:
        print(f"Failed to load the model: {e}")
        return None

# Görseli indir ve işle
def download_image(image_url):
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content)).convert("RGB")
            img.save("temp_image.jpg")
            return "temp_image.jpg"
        else:
            print("Invalid image URL.")
            return None
    except Exception as e:
        print(f"Failed to download image: {e}")
        return None

# Görsel analizi
def analyze_image(pipe, image_path):
    try:
        return pipe(image_path)
    except Exception as e:
        print(f"Error during image analysis: {e}")
        return None

# Sonuçları görüntüleme ve yasal bilgilendirme
def display_results(real_score, fake_score, lang, region, is_user_owned):
    print(f"\n{lang['results_header']}")
    if real_score > fake_score:
        print(lang["original_result"])
    elif fake_score > real_score:
        print(lang["deepfake_result"])
        print("\nLegal Rights:")
        print(lang["legal_rights"].get(region, lang["legal_rights"]["global"]))
        print("\nSDG Impacts:")
        for sdg in lang["sdg_impacts"]:
            print(f"- {sdg}")
    else:
        print(lang["uncertainty"])
        print("\nSDG Impacts:")
        for sdg in lang["sdg_impacts"]:
            print(f"- {sdg}")

# Sonuçları kaydetme
def save_results_to_csv(image_path, result, lang):
    csv_path = "deepfake_results.csv"
    try:
        file_exists = os.path.isfile(csv_path)
        with open(csv_path, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["Image Path", "Result"])
            writer.writerow([image_path, result])
        print(lang["csv_saved"])
    except Exception as e:
        print(f"Failed to save results: {e}")

# Ana program
def main():
    print("Dil seçimi başlatılıyor...")
    language = input(language_options["Türkçe"]["language_prompt"] if "Türkçe" in language_options else language_options["English"]["language_prompt"]).strip()
    lang = language_options.get(language, language_options["Türkçe"])  # Varsayılan Türkçe

    print(lang["welcome"])

    pipe = load_model()
    if not pipe:
        return

    image_url = input(lang["image_prompt"])
    image_path = download_image(image_url)
    if not image_path:
        return

    result = analyze_image(pipe, image_path)
    if not result:
        print(lang["no_result"])
        return

    real_score = sum(r["score"] for r in result if r["label"].lower() == "real")
    fake_score = sum(r["score"] for r in result if r["label"].lower() == "fake")

    # Bölge ve görsel sahipliği promptlarını dil seçimine göre dinamik hale getirme
    region_prompt = lang["image_prompt"] if language == "Türkçe" else "Enter your region (e.g., 'Türkiye', 'global'): "
    region = input(region_prompt).strip()

    ownership_prompt = "Bu görsel size mi ait? (Evet/Hayır): " if language == "Türkçe" else "Is this image yours? (Yes/No): "
    is_user_owned = input(ownership_prompt).strip().lower() in ["evet", "yes"]

    # Sonucu belirleme
    result_text = lang["original_result"] if real_score > fake_score else lang["deepfake_result"] if fake_score > real_score else lang["uncertainty"]
    display_results(real_score, fake_score, lang, region, is_user_owned)
    save_results_to_csv(image_path, result_text, lang)

if __name__ == "__main__":
    main()