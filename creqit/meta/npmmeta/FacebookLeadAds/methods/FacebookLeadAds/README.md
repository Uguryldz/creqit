# Facebook Lead Ads Integration for creqit

Bu modül, Facebook Lead Ads'den gelen lead'leri webhook aracılığıyla alır ve creqit sistemine entegre eder.

## Özellikler

- ✅ Facebook OAuth2 entegrasyonu
- ✅ Webhook tabanlı lead alma
- ✅ Otomatik lead doğrulama
- ✅ Sayfa ve form yönetimi
- ✅ Basitleştirilmiş lead verisi çıktısı
- ✅ Lead istatistikleri ve takibi

## Kurulum

### 1. DocType'ları Sisteme Yükleme

creqit bench'te şu komutu çalıştırın:

```bash
bench --site [site-name] migrate
```

### 2. Facebook App Oluşturma

1. [Facebook Developers](https://developers.facebook.com/) sitesine gidin
2. Yeni bir App oluşturun
3. App ID ve App Secret değerlerini alın
4. Webhooks ürününü ekleyin
5. Lead Ads (leadgen) izinlerini etkinleştirin

### 3. creqit Ayarları

1. creqit'te "Facebook Lead Ads Settings" sayfasına gidin
2. App ID ve App Secret değerlerini girin
3. "Enabled" kutucuğunu işaretleyin
4. Kaydedin

### 4. Webhook Oluşturma

1. "Facebook Lead Ads Webhook" DocType'ında yeni bir kayıt oluşturun
2. Webhook adı, Page ID ve Form ID girin
3. "Enabled" kutucuğunu işaretleyin
4. Kaydettiğinizde otomatik olarak Facebook'a webhook subscription oluşturulacak

## Kullanım

### Webhook Endpoint

Webhook URL'i otomatik olarak oluşturulur:
```
https://[your-site]/api/method/creqit.meta.FacebookLeadAds.webhook.handle_webhook
```

### Lead Verilerini İşleme

Gelen lead verileri otomatik olarak işlenir ve:
- Webhook DocType'ındaki lead sayacı güncellenir
- `facebook_lead_received` eventi publish edilir
- Eğer Lead DocType varsa, otomatik olarak Lead kaydı oluşturulur

### Realtime Events

Lead geldiğinde realtime event dinleyebilirsiniz:

```javascript
creqit.realtime.on('facebook_lead_received', (data) => {
    console.log('Yeni lead geldi:', data);
});
```

## API Metodları

### Sayfa Listesi Alma

```python
import creqit
from creqit.meta.FacebookLeadAds.utils import get_page_list

pages = get_page_list()
```

### Form Listesi Alma

```python
from creqit.meta.FacebookLeadAds.utils import get_form_list

forms = get_form_list(page_id="123456789")
```

### Lead Detaylarını Alma

```python
from creqit.meta.FacebookLeadAds.utils import get_lead_details

lead = get_lead_details(lead_id="123456789")
```

## Veri Yapısı

### Basitleştirilmiş Lead Verisi (simplify_output=True)

```json
{
    "id": "lead_id",
    "data": {
        "full_name": "John Doe",
        "email": "john@example.com",
        "phone_number": "+1234567890"
    },
    "form": {
        "id": "form_id",
        "name": "Contact Form",
        "locale": "en_US",
        "status": "ACTIVE"
    },
    "ad": {
        "id": "ad_id",
        "name": "Ad Name"
    },
    "adset": {
        "id": "adset_id",
        "name": "AdSet Name"
    },
    "page": {
        "id": "page_id",
        "name": "Page Name"
    },
    "created_time": "2025-10-25T12:00:00+0000"
}
```

### Tam Lead Verisi (simplify_output=False)

Tüm field_data, form detayları ve event bilgilerini içerir.

## Güvenlik

- Webhook istekleri HMAC SHA-256 imzası ile doğrulanır
- Tüm API istekleri OAuth2 access token ile yapılır
- App Secret ve Access Token güvenli şekilde saklanır (Password field)

## Sorun Giderme

### Webhook Çalışmıyor

1. Facebook App Settings'te webhook URL'inin doğru olduğundan emin olun
2. Verify Token'ın doğru olduğunu kontrol edin
3. Error Log'larda hata mesajlarını kontrol edin

### Access Token Hatası

1. Facebook Lead Ads Settings'te access token'ın güncel olduğundan emin olun
2. Token'ın gerekli izinlere sahip olduğunu kontrol edin
3. Token'ı yeniden oluşturun

## Lisans

MIT License

## Destek

Sorunlar için GitHub Issues kullanın veya creqit forumuna yazın.

