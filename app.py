import streamlit as st
import csv
import os
from transformers import pipeline
import requests
from PIL import Image
from io import BytesIO

FAKE_THRESHOLD = 0.1  # Minimum threshold for fake score
CSV_FILE = "deepfake_sonuclar.csv"  # Save results to CSV file

# Supported interface languages
interface_languages = ["Türkçe", "English"]

# Supported countries and their available legal languages
supported_countries = {
    "Türkiye": ["Türkçe", "English"],
    "USA": ["Türkçe", "English"],
    "Germany": ["Türkçe", "English", "Deutsch"],
    "France": ["Türkçe", "English", "Français"],
    "India": ["Türkçe", "English"]
}

# Legal regulations per country (translated)
legal_information = {
    "Türkiye": {
        "Türkçe": "Türk Ceza Kanunu'nun 243 ve 244. maddelerine göre deepfake içeriklerin manipülasyonu yasa dışıdır.",
        "English": "Under Turkish Penal Code Articles 243 and 244, deepfake manipulation is illegal."
    },
    "USA": {
        "Türkçe": "Deepfake içerikleri DEEPFAKES Accountability Act kapsamında düzenlenmiştir.",
        "English": "Deepfake content is regulated under the DEEPFAKES Accountability Act."
    },
    "Germany": {
        "Türkçe": "Deepfake içerikleri Alman Ceza Yasası'nın 201b maddesi kapsamında cezalandırılabilir.",
        "English": "Deepfake content is punishable under German Criminal Code Section 201b.",
        "Deutsch": "Deepfake-Inhalte sind gemäß Abschnitt 201b des deutschen Strafgesetzbuches strafbar."
    },
    "France": {
        "Türkçe": "Deepfake içerikleri Fransız siber güvenlik yasası kapsamında düzenlenmiştir.",
        "English": "Deepfake content is regulated under French cybersecurity law.",
        "Français": "Le contenu deepfake est réglementé par la loi française sur la cybersécurité."
    },
    "India": {
        "Türkçe": "Hindistan IT Act 2000 ve değişiklikleri, yapay zeka destekli sahte medya kullanımını düzenlemektedir.",
        "English": "Indian IT Act 2000 regulates AI-generated fake media."
    }
}

# Load the AI model
@st.cache_resource
def load_model():
    return pipeline("image-classification", model="prithivMLmods/Deep-Fake-Detector-Model", framework="pt")

model = load_model()

# Validate image input
def validate_image(response):
    if response.status_code != 200:
        st.error("Image could not be downloaded. Please provide a valid URL.")
        return False
    if response.headers.get("Content-Type") not in ["image/jpeg", "image/png"]:
        st.error("Unsupported image format. Please use JPEG or PNG.")
        return False
    return True

# Save results to CSV
def save_results(image_url, real_score, fake_score, classification):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Image URL", "Real Score", "Fake Score", "Result"])
        writer.writerow([image_url, f"{real_score:.2f}", f"{fake_score:.2f}", classification])
    st.success("Results saved successfully!")

# Download and analyze the image
def analyze_image(image_url):
    try:
        response = requests.get(image_url)
        if not validate_image(response):
            return None
        
        img = Image.open(BytesIO(response.content)).convert("RGB")
        st.image(img, caption="Analysis Results", use_container_width=True)
        img.save("temp_image.jpg")
        result = model("temp_image.jpg")
        return result
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# Display results and legal information
def display_analysis(image_url, real_score, fake_score, selected_country, legal_language, interface_language):
    st.subheader("Analysis Results" if interface_language == "English" else "Analiz Sonuçları")

    if fake_score >= FAKE_THRESHOLD and fake_score > real_score:
        classification = "Deepfake suspicion detected!" if interface_language == "English" else "Deepfake şüphesi tespit edildi!"
        st.error(classification)
        st.warning("### Legal Information:" if interface_language == "English" else "### Yasal Bilgiler:")
        st.write(legal_information[selected_country].get(legal_language, "No legal information available for this country."))
    elif real_score >= FAKE_THRESHOLD and real_score > fake_score:
        classification = "This image is classified as original." if interface_language == "English" else "Bu görsel orijinal olarak değerlendirildi."
        st.success(classification)
    else:
        classification = "Uncertain results." if interface_language == "English" else "Sonuçlar belirsiz."
        st.warning(classification)

    # Save results to CSV
    save_results(image_url, real_score, fake_score, classification)

    # User feedback button
    if st.button("Report Incorrect Result" if interface_language == "English" else "Sonuç yanlış mı? Geri bildirim verin", key="feedback_button"):
        st.info("Thank you for your feedback!" if interface_language == "English" else "Geri bildiriminiz alındı. Teşekkür ederiz!")

# Main application interface
def main():
    st.sidebar.title("Language & Country Selection")

    # Define UI language
    interface_language = st.sidebar.selectbox("Interface Language", interface_languages, key="interface_language_selection")

    # Define country selection and legal information language
    selected_country = st.sidebar.selectbox(
        "Select Country for Legal Info" if interface_language == "English" else "Yasal bilgilerin gösterileceği ülkeyi seçin",
        list(legal_information.keys()), key="country_selection"
    )
    legal_language = st.sidebar.selectbox(
        "Legal Info Language" if interface_language == "English" else "Yasal Bilgi Dilini Seçin",
        supported_countries[selected_country], key="legal_language_selection"
    )

    st.title("Deepfake Detection System" if interface_language == "English" else "Deepfake Tespit Sistemi")
    st.info("### Why This Project Matters?" if interface_language == "English" else "### Neden Bu Proje Önemli?")
    st.write("Deepfake technology threatens digital rights and societal trust..." if interface_language == "English" else "Deepfake teknolojisi dijital hakları ve toplumsal güveni tehdit ediyor...")

    # Image URL input
    image_url = st.text_input("Enter Image URL" if interface_language == "English" else "Görsel URL'sini girin", key="image_url_input")
    if st.button("Analyze" if interface_language == "English" else "Analiz Et", key="analyze_button"):
        analysis_result = analyze_image(image_url)
        if not analysis_result:
            return
        display_analysis(
            image_url,
            sum(r["score"] for r in analysis_result if r["label"].lower() == "real"),
            sum(r["score"] for r in analysis_result if r["label"].lower() == "fake"),
            selected_country,
            legal_language,
            interface_language
        )

if __name__ == "__main__":
    main()