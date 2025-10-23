import creqit
from creqit import _

@creqit.whitelist()
def get_filtered_records(filters=None, fields=None, limit=5, offset=0):
    filters = filters or {}
    fields = fields or [                
        "customer_type",                             # Müşteri Tipi
        # Kurumsal Müşteri Bilgileri
        "name",                                      # id
        "trade_name",                                # Ticaret Unvanı
        "scope",                                     # Faaliyet Alanı
        "lead_source",                               # Kanal
        "company_email",                             # Şirket E-Posta
        "company_tel",                               # Şirket Telefonu
        "customer_name",                             # İsim
        "customer_surname",                          # Soyisim
        "customer_group",                            # Müşteri Grubu
        "territory",                                 # Bölge
        "customer_owner",                            # Aday Sahibi 
        "birth_date",                                # Doğum Tarihi
        "citizen",                                   # Vatandaşlık
        "contacs_email",                             # Email
        "contacs_phone",                             # Cep Telefonu
        "phone",                                     # Telefon
        "phone_ext",                                 # Dahili Telefon
        # Hesap Bilgileri
        "activity_status",                           # Aktiflik Durumu
        "account_no",                                # Hesap Numarası
        "account_opening_date",                      # Hesap Açılış Tarihi
        "customer_representative",                   # Müşteri Temsilcisi
        "investment_products_traded",                # İşlem Yapılan Yatırım Ürünleri
        # Yasaklılık Durumu
        "customer_with_transaction_ban",             # İşlem Yasağı Olan Müşteri
        "blocked_account",                           # Bloke Hesap
        "restricted_account",                        # Kısıtlı Hesap
        "temporary_transaction_ban",                 # Geçici İşlem Yasağı
        "margin_call",                               # Teminat Tamamlama Çağrısı
        "blacklisted",                               # Kara Listeye Alınmış
        "pep",                                       # PEP (Politikaya Maruz Kişi)
        "in_international_production",               # Uluslararası Yaptırımda
        "kyc_alm_non_compliant",                     # KYC-ALM Uyumsuz
        # KVKK İzinleri
        "call_permission",                           # Arama İzinleri
        "campaign_permission",                       # Kampanya İzinleri
        "email_permission",                          # Email İzinleri
        # Portföy Bilgileri
        "tl_cash_amount",                            # TL Nakit Tutar
        "usd_cash_amount",                           # USD Nakit Tutar
        "domestic_share_total_value",                # Yurtiçi Pay Toplam Değeri
        "international_share_total_value",           # Yurtdışı Pay Toplam Değeri
        "mutual_fund_total_value"                    # Yatırım Fonu Toplam Değeri
    ]

    # Kayıtları al
    records = creqit.get_all("Customer", filters=filters, fields=fields)

    # Paging uygula
    total_records = len(records)
    paginated_records = records[offset:offset + limit]

    # Yetkili kişi bilgilerini çekip ekleyelim
    for record in paginated_records:
        child_filters = {"parent": record["name"]}  # Ana kaydın ID'sine göre eşleşme yap
        
        child_fields = ["authorized_person_name", "authorized_person_surname", "authorized_person_tckn", "authorized_person_phone", "authorized_person_email"]
        child_records = creqit.get_all("Authorized Persons", filters=child_filters, fields=child_fields)
        
        # Child verileri ana kayda ekleniyor
        record["Authorizedpersons"] = child_records

    # Komisyon bilgilerini çekip ekleyelim
    for record in paginated_records:
        child_filters = {"parent": record["name"]}  # Ana kaydın ID'sine göre eşleşme yap
        
        child_fields = ["commission", "commission_rate"]
        child_records = creqit.get_all("Customer Commission Details", filters=child_filters, fields=child_fields)
        
        # Child verileri ana kayda ekleniyor
        record["CommissionDetails"] = child_records

    # Toplam kayıt sayısı ve sayfalanmış kayıtları döndür
    return {
        "total_records": total_records,
        "records": paginated_records
    }