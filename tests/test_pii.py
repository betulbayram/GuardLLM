from guardllm import Guard
from guardllm.input import PIIScanner
from guardllm.utils.patterns import luhn_check, validate_tc_kimlik


def test_valid_tc_kimlik():
    # A valid TC number that satisfies the checksum algorithm.
    assert validate_tc_kimlik("10000000146")


def test_invalid_tc_kimlik():
    assert not validate_tc_kimlik("12345678901")
    assert not validate_tc_kimlik("00000000000")
    assert not validate_tc_kimlik("123")


def test_luhn_check():
    assert luhn_check("4111111111111111")  # classic test Visa
    assert not luhn_check("4111111111111112")


def test_scan_masks_phone_and_email():
    scanner = PIIScanner()
    result = scanner.scan("Bana ulaş: ahmet@example.com veya 0532 123 45 67")
    assert "[EMAIL]" in result.redacted
    assert "[TELEFON]" in result.redacted
    assert not result.safe  # default action is 'mask' -> surfaced as threat


def test_scan_masks_valid_tc():
    scanner = PIIScanner()
    result = scanner.scan("TC: 10000000146 numaralı müşteri")
    assert "[TC_KİMLİK]" in result.redacted


def test_scan_ignores_invalid_tc():
    scanner = PIIScanner()
    result = scanner.scan("Sipariş no 12345678901 hazır")
    # Invalid checksum -> not masked as TC
    assert "[TC_KİMLİK]" not in result.redacted


def test_iban_masked():
    scanner = PIIScanner()
    result = scanner.scan("IBAN TR33 0006 1005 1978 6457 8413 26 hesabı")
    assert "[IBAN]" in result.redacted


def test_clean_text_is_safe():
    scanner = PIIScanner()
    result = scanner.scan("Bugün hava çok güzel.")
    assert result.safe
    assert result.redacted == "Bugün hava çok güzel."


def test_guard_scan_pii():
    guard = Guard()
    result = guard.scan_pii("Müşteri e-postası: veli@firma.com.tr")
    assert "[EMAIL]" in result.redacted
