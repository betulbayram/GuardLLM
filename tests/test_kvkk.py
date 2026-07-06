from guardllm import Guard
from guardllm.compliance import ComplianceReport, KVKKChecker


def test_no_personal_data_is_compliant():
    report = KVKKChecker().check("Bugün hava çok güzel, parkta yürüyüş yaptım.")
    assert report.compliant
    assert report.risk_level == "yok"
    assert not report.requires_explicit_consent


def test_general_pii_medium_risk():
    report = KVKKChecker().check("Müşteri e-postası ali@firma.com, tel 0532 123 45 67")
    assert not report.compliant
    assert report.risk_level == "orta"
    assert not report.requires_explicit_consent
    keys = {f.category.key for f in report.findings}
    assert "email" in keys and "telefon" in keys
    # PII masked in the redacted output
    assert "[EMAIL]" in report.redacted


def test_special_category_health_high_risk():
    report = KVKKChecker().check("Hastanın kanser teşhisi kondu ve tedavi başladı.")
    assert report.risk_level == "yüksek"
    assert report.has_special_category
    assert report.requires_explicit_consent
    keys = {f.category.key for f in report.findings}
    assert "saglik" in keys


def test_biometric_and_criminal_detected():
    report = KVKKChecker().check(
        "Parmak izi kaydı alındı; ayrıca sabıka kaydında mahkûmiyet bulunuyor."
    )
    keys = {f.category.key for f in report.findings}
    assert "biyometrik" in keys
    assert "ceza_mahkumiyeti" in keys
    assert report.risk_level == "yüksek"


def test_article_references_present():
    report = KVKKChecker().check("Hastanın sağlık raporu ve TC 10000000146 kayıtlı.")
    d = report.to_dict()
    joined = " ".join(d["articles_referenced"])
    assert "Madde 6" in joined  # özel nitelikli (sağlık)
    assert "Madde 5" in joined  # genel (kimlik)


def test_report_markdown_renders():
    report = KVKKChecker().check("Müşteri TC 10000000146 ve sağlık verisi mevcut.")
    md = report.to_markdown()
    assert "# KVKK Uyumluluk Raporu" in md
    assert "Risk seviyesi" in md
    assert "Öneriler" in md


def test_guard_check_kvkk():
    guard = Guard()
    report = guard.check_kvkk("İletişim: veli@example.com")
    assert isinstance(report, ComplianceReport)
    assert not report.compliant


def test_special_recommendation_first():
    report = KVKKChecker().check("Çalışanın sendika üyeliği bilgisi işlendi.")
    assert report.requires_explicit_consent
    assert "ÖZEL NİTELİKLİ" in report.recommendations[0]
