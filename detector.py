"""
AI-Phishing-Detector
Makine Ogrenmesi (NLP & TF-IDF) Tabanli E-Posta / URL Oltalama (Phishing) Tespit Araci.
"""

import sys
import os

# Windows konsol UTF-8 uyumlulugu
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score

# Genisletilmis Egitim Veri Seti (Phishing ve Guvenli Ornekler)
SAMPLE_DATA = [
    # Phishing / Zararli Ornekler (Label: 1)
    ("Urgent! Your bank account has been suspended. Click here to verify your identity immediately.", 1),
    ("Dear customer, suspicious login detected. Reset your password now at http://secure-login-bank.fake.com", 1),
    ("You have won a 1000$ lottery prize! Claim your reward now by providing your credit card details.", 1),
    ("Security Alert: Your mailbox quota is full. Verify credentials to avoid account deactivation.", 1),
    ("Action Required: Unauthorized wire transfer detected. Cancel transaction immediately: http://bit.ly/cancel-tx", 1),
    ("Invoice #84920 payment overdue. Download the attached zip file and review immediately.", 1),
    ("Hesabiniz kisitlandi! Lutfen 24 saat icinde linke tiklayarak sifrenizi yenileyiniz.", 1),
    ("Tebrikler! Cekilisten iPhone 15 kazandiniz. Odulu almak icin bilgilerinizi giriniz: http://hediye-al.net", 1),
    ("Banka uyarisi: Kartinizdan supheli islem yapildi. Iptal etmek icin SMS kodunu giriniz.", 1),
    ("Fatura borcunuz bulunmaktadir. Ekli dosyayi acarak odeme dekontunu onaylayiniz.", 1),
    ("Your PayPal account has been limited. Please confirm your identity within 24 hours.", 1),
    ("Payroll notification: Update your direct deposit information before the next pay cycle.", 1),
    ("Google Drive: An urgent encrypted document has been shared with you. Sign in to view.", 1),
    ("Kargo teslim edilemedi! Adres guncellemek icin linke tiklayin: http://ptt-kargo-takip.site", 1),
    ("E-Devlet ceza bildirimi: Odenmemis radar cezaniz var. Hemen odeyin: http://e-devlet-odeme.top", 1),

    # Normal / Guvenli (Ham) Ornekler (Label: 0)
    ("Hi John, can we schedule the weekly engineering sync meeting for tomorrow at 10 AM?", 0),
    ("Please find attached the quarterly project progress report and budget summary.", 0),
    ("Thank you for your application to Karabuk University. We will review your submission shortly.", 0),
    ("Here is the updated documentation for our API endpoints. Let me know if you have feedback.", 0),
    ("The team lunch is confirmed for Friday at 12:30 PM. See you all at the cafeteria.", 0),
    ("Your order has been shipped and is scheduled for delivery on Monday. Tracking number: 9847291.", 0),
    ("Yarinki yazilim muhendisligi dersi saat 14:00'te D-102 nolu sinifta yapilacaktir.", 0),
    ("Haftalik proje raporunu ekte bulabilirsiniz, inceleyip donus yaparsaniz sevinirim.", 0),
    ("Universite kutuphanesi vize haftasi boyunca 24 saat acik olacaktir.", 0),
    ("Siparisiniz kargoya verildi. Takip numaraniz ile teslimat durumunu sorgulayabilirsiniz.", 0),
    ("Can you please review the merge request on GitHub when you have a free moment?", 0),
    ("The network maintenance is scheduled for Sunday between 02:00 AM and 04:00 AM.", 0),
    ("Attached are the lecture notes and reading materials for this week's seminar.", 0),
    ("Ogrenci isleri duyurusu: Bahar donemi ders kayitlari onumuzdeki pazartesi baslayacaktir.", 0),
    ("Toplanti tutanagi ektedir, revizyon taleplerinizi yarin aksama kadar iletebilirsiniz.", 0)
]

class PhishingDetector:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words=None)
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.is_trained = False

    def train(self, data):
        df = pd.DataFrame(data, columns=["text", "label"])
        X = self.vectorizer.fit_transform(df["text"])
        y = df["label"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=42, stratify=y
        )
        self.model.fit(X_train, y_train)
        self.is_trained = True

        # Test degerlendirmesi
        y_pred = self.model.predict(X_test)
        print("=== Model Basari Metrikleri ===")
        print(f"Accuracy : %{accuracy_score(y_test, y_pred) * 100:.2f}")
        print(f"Precision: %{precision_score(y_test, y_pred) * 100:.2f}")
        print(f"Recall   : %{recall_score(y_test, y_pred) * 100:.2f}")
        print("\nDetayli Rapor:")
        print(classification_report(y_test, y_pred, target_names=["Guvenli (Ham)", "Oltalama (Phishing)"]))

    def predict(self, text: str):
        if not self.is_trained:
            raise Exception("Model henuz egitilmedi!")
        vec = self.vectorizer.transform([text])
        prediction = self.model.predict(vec)[0]
        prob = self.model.predict_proba(vec)[0]
        return {
            "text": text,
            "is_phishing": bool(prediction == 1),
            "confidence": float(prob[prediction]),
            "label": "[!] TEHLIKE: PHISHING" if prediction == 1 else "[+] GUVENLI: NORMAL METIN"
        }

if __name__ == "__main__":
    print("=" * 60)
    print("[*] AI Destekli Phishing Tespit Araci Baslatiliyor...")
    print("=" * 60)

    detector = PhishingDetector()
    detector.train(SAMPLE_DATA)

    test_samples = [
        "Your account is locked! Click http://fake-bank-auth.com immediately to unlock.",
        "Hey team, the slide deck for tomorrow's presentation is ready for review.",
        "Acil: Hesabiniz bloke oldu! Hemen giris yaparak dogrulama yapin.",
        "Ders notlarini kutuphaneden alip fotokopi cektirebilirsiniz."
    ]

    print("\n=== Canli Test Sonuclari ===")
    for text in test_samples:
        res = detector.predict(text)
        print(f"\n[Metin] : \"{res['text']}\"")
        print(f"[Sonuc] : {res['label']} (Guven Skoru: %{res['confidence']*100:.1f})")
