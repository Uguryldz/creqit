# Facebook Lead Ads Kullanım Kılavuzu

## 1. Facebook Developer Hesabı Hazırlığı

### Facebook App Oluşturma

1. **Facebook Developers** sitesine git: https://developers.facebook.com/
2. **My Apps** > **Create App** tıkla
3. **Business** tipini seç
4. App adını belirle (örn: "creqit Lead Ads")
5. App ID ve App Secret değerlerini kaydet

### Gerekli İzinleri Ekle

1. App Dashboard'da **Add Product** tıkla
2. **Webhooks** ürününü ekle
3. **Lead Ads** permissions ekle:
   - `leads_retrieval`
   - `pages_show_list`
   - `pages_manage_metadata`
   - `pages_manage_ads`
   - `business_management`

## 2. creqit'te Ayarlar

### Facebook Lead Ads Settings'i Yapılandır

1. creqit'e login ol
2. Arama kutusuna "**Facebook Lead Ads Settings**" yaz
3. Ayarları doldur:
   - **Enabled**: ✓ İşaretle
   - **App ID**: Facebook App ID'ni gir
   - **App Secret**: Facebook App Secret'ı gir
   - **Authorization URL**: `https://www.facebook.com/v24.0/dialog/oauth` (varsayılan)
   - **Access Token URL**: `https://graph.facebook.com/v24.0/oauth/access_token` (varsayılan)
   - **Scope**: `leads_retrieval pages_show_list pages_manage_metadata pages_manage_ads business_management ads_management ads_read`
   - **API Version**: `v24.0` (varsayılan)
4. **Save** butonuna bas

### Access Token Alma

Access token almak için iki yöntem var:

**Yöntem 1: OAuth2 Flow (Önerilen) ✅**
1. **Facebook Lead Ads Settings** sayfasını aç
2. **App ID** ve **App Secret** bilgilerini gir ve kaydet
3. **OAuth2** > **Authorize with Facebook** butonuna tıkla
4. Açılan popup'ta Facebook'a giriş yap
5. İzinleri onayla
6. Otomatik olarak geri dönüldüğünde token kaydedilecek

**Yöntem 2: Manuel Token Alma**
1. Facebook Graph API Explorer'a git: https://developers.facebook.com/tools/explorer/
2. App'ini seç
3. Gerekli izinleri seç:
   - `leads_retrieval`
   - `pages_show_list`
   - `pages_manage_metadata`
   - `pages_manage_ads`
   - `business_management`
4. **Generate Access Token** tıkla
5. Token'ı kopyala ve **Facebook Lead Ads Settings** > **Access Token** alanına yapıştır

**Token Kontrolü**
- **OAuth2** > **Check Token Status**: Token durumunu kontrol et
- **OAuth2** > **Refresh Token**: Token'ı yenile (re-authorization gerekir)

## 3. Webhook Oluşturma

### Yeni Webhook Kaydı

1. creqit'te "**Facebook Lead Ads Webhook**" DocType'ına git
2. **New** butonuna bas
3. Bilgileri doldur:
   - **Webhook Name**: Benzersiz bir isim (örn: "Ana Sayfa Lead Formu")
   - **Enabled**: ✓ İşaretle
   - **Page ID**: Facebook Page ID'ni gir
   - **Form ID**: Lead Form ID'ni gir
   - **Simplify Output**: ✓ İşaretle (önerilen)
4. **Save** butonuna bas

### Page ID ve Form ID Nasıl Bulunur?

**Page ID Bulma:**
1. Facebook Page'ine git
2. **About** sekmesine bas
3. En altta **Page ID** göreceksin

**Form ID Bulma:**
1. Facebook Business Manager'a git
2. **Publishing Tools** > **Forms Library** tıkla
3. Form'u seç
4. URL'de form ID'yi göreceksin: `facebook.com/ads/lead_ads/forms/?id=FORM_ID`

### Otomatik Liste Getirme (API ile)

```python
import creqit

# Sayfa listesi al
from creqit.meta.FacebookLeadAds.webhook import get_page_list
pages = get_page_list()
print(pages)

# Form listesi al (sayfa ID'si gerekli)
from creqit.meta.FacebookLeadAds.webhook import get_form_list
forms = get_form_list(page_id="123456789")
print(forms)
```

## 4. Facebook'ta Webhook Ayarları

### Webhook URL'i Kaydet

Webhook kaydını kaydettiğinde otomatik olarak Facebook'a subscription oluşturulur. Ancak manuel kontrol için:

1. Facebook App Dashboard'a git
2. **Webhooks** bölümüne git
3. **Page** object'i için subscription göreceksin
4. Callback URL: `https://[site-url]/api/method/creqit.meta.FacebookLeadAds.webhook.handle_webhook`
5. Verify Token: Otomatik oluşturulur (creqit'te görülebilir)

## 5. Lead'leri İzleme

### Realtime Events

creqit'te lead geldiğinde realtime event tetiklenir. Bunu dinlemek için:

```javascript
// Client-side JavaScript
creqit.realtime.on('facebook_lead_received', function(data) {
    console.log('Yeni lead geldi!', data);
    
    // Örnek veri yapısı:
    // {
    //     id: "lead_id",
    //     data: {
    //         full_name: "Ahmet Yılmaz",
    //         email: "ahmet@example.com",
    //         phone_number: "+905551234567"
    //     },
    //     form: {
    //         id: "form_id",
    //         name: "İletişim Formu"
    //     },
    //     created_time: "2025-10-25T12:00:00+0000"
    // }
    
    // Bildirim göster
    creqit.show_alert({
        message: 'Yeni lead: ' + data.data.full_name,
        indicator: 'green'
    });
});
```

### Lead İstatistikleri

Webhook DocType'ında otomatik olarak izlenir:
- **Lead Count**: Toplam gelen lead sayısı
- **Last Lead Received**: Son lead'in geldiği tarih/saat
- **Is Active**: Webhook'un aktif olup olmadığı

## 6. Lead'leri İşleme

### Otomatik Lead Document Oluşturma

Eğer sistemde **Lead** DocType varsa, gelen her lead için otomatik olarak Lead kaydı oluşturulur:

```python
# Lead DocType'ı varsa otomatik oluşturulur
# Aşağıdaki alanlar otomatik doldurulur:
- lead_name: İsim (form'dan)
- email_id: E-posta
- phone: Telefon
- company_name: Şirket adı (varsa)
- source: "Facebook Lead Ads"
- facebook_lead_id: Facebook'tan gelen lead ID
- facebook_form_id: Form ID
- facebook_page_id: Sayfa ID
- facebook_ad_id: Reklam ID
- facebook_lead_data: Tüm lead verisi (JSON)
```

### Custom İşleme

Kendi özel işleme mantığını eklemek için:

```python
# custom_app/hooks.py
doc_events = {
    "Facebook Lead Ads Webhook": {
        "on_update": "custom_app.facebook_leads.process_custom_lead"
    }
}

# custom_app/facebook_leads.py
import creqit

def process_custom_lead(doc, method):
    """Lead geldiğinde özel işlemler yap"""
    # Örnek: Slack'e bildirim gönder
    # Örnek: CRM'e kaydet
    # Örnek: E-posta gönder
    pass
```

## 7. Test Etme

### Test Lead Gönderme

1. Facebook'ta test lead ads kampanyası oluştur
2. Form'u doldur
3. creqit'te **Error Log** ve **Webhook Statistics**'i kontrol et

### Debug Modu

```python
# Console'da webhook bilgilerini kontrol et
import creqit
from creqit.meta.FacebookLeadAds.webhook import test_webhook

result = test_webhook("webhook-adi")
print(result)
# {
#     "webhook_url": "https://...",
#     "verify_token": "...",
#     "is_active": True,
#     "enabled": True
# }
```

## 8. Sorun Giderme

### Webhook Çalışmıyor

1. **Error Log**'u kontrol et: Arama > "Error Log"
2. Facebook App Settings'te webhook URL'in doğru olduğunu kontrol et
3. Verify Token'ın eşleştiğini kontrol et
4. creqit site'ın internetten erişilebilir olduğunu kontrol et (localhost olmaz)

### Access Token Hatası

1. Token'ın expire olmadığını kontrol et
2. Token'ın doğru izinlere sahip olduğunu kontrol et
3. Yeni token al ve **Facebook Lead Ads Settings**'te güncelle

### Lead Gelmiyor

1. Webhook subscription'ın aktif olduğunu Facebook'ta kontrol et
2. Page ve Form ID'lerin doğru olduğunu kontrol et
3. Form'un ACTIVE durumda olduğunu kontrol et

## 9. Güvenlik

- App Secret güvenli şekilde saklanır (Password field)
- Webhook istekleri HMAC SHA-256 ile doğrulanır
- Sadece Facebook'tan gelen istekler işlenir
- Access token şifrelenir

## 10. Sınırlamalar

- Facebook API rate limit'lerine tabidir
- Bir app için sadece bir webhook subscription olabilir
- Lead verisi 90 gün sonra Facebook'ta expire olur
- Test mode lead'leri production'a gelmez

## İletişim ve Destek

Sorular için:
- GitHub Issues
- creqit Forum
- E-posta: support@creqit.io

