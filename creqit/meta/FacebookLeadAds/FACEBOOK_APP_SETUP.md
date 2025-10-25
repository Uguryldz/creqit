# Facebook App Kurulum Rehberi

## 🔧 Facebook Developer Console'da Yapılacaklar

### 1. Yeni App Oluşturma

1. **Facebook Developers**'a git: https://developers.facebook.com/apps/
2. **Create App** butonuna tıkla
3. **Use case** seç: **Business**
4. App bilgilerini doldur:
   - **App Name**: creqit Lead Ads Integration (veya istediğin isim)
   - **App Contact Email**: E-posta adresin
5. **Create App** tıkla

### 2. Temel Ayarlar

**Settings** > **Basic** sayfasında:

1. **App ID** ve **App Secret** değerlerini kopyala
   - ⚠️ **App Secret**'ı güvenli tut!
2. **App Domains** ekle:
   ```
   your-site.com
   ```
3. **Save Changes** tıkla

### 3. OAuth Redirect URI Ekleme (ÖNEMLİ!)

⚠️ **Bu adım çok önemli! OAuth2 flow çalışması için gerekli.**

**Settings** > **Basic** > **Website** bölümünde:

```
Site URL: https://your-site.com/api/method/creqit.meta.FacebookLeadAds.oauth.callback
```

**VEYA**

**Facebook Login** ürününü eklediyseniz:
**Facebook Login** > **Settings** > **Valid OAuth Redirect URIs**:

```
https://your-site.com/api/method/creqit.meta.FacebookLeadAds.oauth.callback
```

🔍 **creqit'teki Redirect URI'yi Öğrenme:**
1. creqit'te **Facebook Lead Ads Settings** sayfasını aç
2. **OAuth2** > **Authorize with Facebook** butonuna tıkla
3. Açılan mesajda **Redirect URI** gösterilecek
4. Bu URI'yi Facebook App ayarlarına ekle

### 4. Webhooks Ürünü Ekleme

1. **Dashboard** > **Add Product** tıkla
2. **Webhooks** bul ve **Set Up** tıkla
3. **Page** object'i seç
4. Webhook ayarları:
   - **Callback URL**: `https://your-site.com/api/method/creqit.meta.FacebookLeadAds.webhook.handle_webhook`
   - **Verify Token**: creqit'te webhook oluşturduğunda gösterilecek
   - **Fields**: `leadgen` seç
5. **Subscribe** tıkla

### 5. Lead Ads İzinleri

**App Review** > **Permissions and Features**:

Aşağıdaki izinleri **Request Advanced Access** ile talep et:

- ✅ `leads_retrieval` - Lead verilerini okumak için
- ✅ `pages_show_list` - Sayfa listesi için
- ✅ `pages_manage_metadata` - Sayfa ayarları için  
- ✅ `pages_manage_ads` - Reklam yönetimi için
- ✅ `business_management` - Business hesabı erişimi için

⚠️ **Not:** Test modunda bu izinler otomatik verilir. Production'da App Review gerekir.

### 6. Test Kullanıcıları Ekleme (Development)

Development modunda test için:

**Roles** > **Test Users**:

1. **Add Test Users** tıkla
2. Test kullanıcısı ekle
3. Bu kullanıcı ile Facebook'ta login olup test edebilirsin

### 7. App'i Canlıya Alma (Production)

**App Review** > **Requests**:

1. İzinleri talep et
2. Use case açıklaması yaz
3. Video/ekran görüntüsü ekle
4. Submit et
5. Facebook onayını bekle (genelde 3-7 gün)

## 🔐 Güvenlik Ayarları

### App Secret Proof (Opsiyonel ama Önerilen)

**Settings** > **Advanced**:

- **Require App Secret**: Aktif et
- **Server IP Whitelist**: creqit sunucu IP'sini ekle

### HTTPS Zorunluluğu

⚠️ **Önemli:** Facebook OAuth ve Webhooks HTTPS gerektirir!

- Site'ın HTTPS üzerinden erişilebilir olması gerekli
- `localhost` veya `http://` ile çalışmaz
- Test için **ngrok** kullanabilirsin:
  ```bash
  ngrok http 8000
  # Aldığın HTTPS URL'i Facebook ayarlarına ekle
  ```

## 📋 Checklist

Kurulum tamamlandığında kontrol et:

- [ ] App ID ve App Secret alındı
- [ ] App Domain eklendi
- [ ] OAuth Redirect URI eklendi
- [ ] Webhooks URL eklendi
- [ ] Lead Ads izinleri istendi
- [ ] HTTPS aktif
- [ ] Test kullanıcısı eklendi (development)
- [ ] creqit'te ayarlar yapıldı

## ⚙️ creqit Ayarları

Facebook App hazır olduktan sonra:

1. **Facebook Lead Ads Settings** sayfasını aç
2. Bilgileri doldur:
   ```
   Enabled: ✓
   App ID: [Facebook'tan kopyala]
   App Secret: [Facebook'tan kopyala]
   ```
3. **Save** et
4. **OAuth2** > **Authorize with Facebook** ile token al
5. **Facebook Lead Ads Webhook** oluştur

## 🐛 Sorun Giderme

### OAuth Redirect Hatası

```
Can't Load URL: The domain of this URL isn't included in the app's domains
```

**Çözüm:** Facebook App Settings > Basic > App Domains'e domain ekle

### Webhook Verification Failed

```
The URL couldn't be validated
```

**Çözüm:** 
- Site HTTPS olmalı
- Verify Token doğru olmalı
- creqit sitesi internetten erişilebilir olmalı

### Invalid Permissions

```
This endpoint requires the 'leads_retrieval' permission
```

**Çözüm:** App Review'dan izinleri talep et veya Test Mode kullan

## 📚 Kaynaklar

- Facebook Developers: https://developers.facebook.com/
- Lead Ads Docs: https://developers.facebook.com/docs/marketing-api/guides/lead-ads
- Webhooks Guide: https://developers.facebook.com/docs/graph-api/webhooks
- OAuth Docs: https://developers.facebook.com/docs/facebook-login/guides/advanced/manual-flow

