# Eye Mouse – AI-Based Eye Tracking Mouse Controller  

Bu proje, sadece bir webcam kullanarak göz hareketleriyle bilgisayar faresini kontrol etmeyi sağlayan bir "Eye Mouse" sistemidir.  
MediaPipe FaceMesh kullanılarak yüz ve göz landmark’ları gerçek zamanlı olarak takip edilir.

## 🎯 Özellikler
- Burun hareketi ile **mouse imleci kontrolü**
- **Sol göz kırpma → Sol tık**
- **Sağ göz kırpma → Sağ tık**
- Uzun sol göz kapanması → **Drag & Drop**
- Normal göz kırpmaları tıklama olarak algılanmaz
- Smoothing + Deadzone ile **stabil ve pürüzsüz hareket**
- Tamamen **eller serbest** kullanım

## 🛠 Kullanılan Teknolojiler
- Python
- MediaPipe FaceMesh
- OpenCV
- PyAutoGUI
- NumPy

## 📌 Gereksinimler
```
pip install mediapipe opencv-python pyautogui numpy
```

## 🚀 Çalıştırmak
```
python eye_mouse.py
```

## 📷 Çalışma Mantığı
- Göz açıklığı oranı (eye aspect ratio) hesaplanır.
- Oran belirli bir eşiğin altına düşünce göz kapalı sayılır.
- Kısa kapama → Click  
- Uzun kapama → Drag  
- Burun hareketi ekran koordinatlarına dönüştürülür.

## 🤝 Katkı
Pull request’lere açığım. Fikir ve geliştirme önerilerinizi iletebilirsiniz.

## 📄 Lisans
## © Tüm Hakları Saklıdır.
Bu proje geliştirici **ALİ ERGÜN** tarafından oluşturulmuştur.  
Her hakkı saklıdır. İzinsiz kopyalanamaz, çoğaltılamaz veya dağıtılamaz.