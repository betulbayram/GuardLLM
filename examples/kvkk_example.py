"""KVKK compliance check example.

Run: python examples/kvkk_example.py
"""

from guardllm import Guard


def main() -> None:
    guard = Guard()

    text = (
        "Müşteri Ali Yılmaz, TC 10000000146, tel 0532 123 45 67. "
        "Sağlık raporunda diyabet teşhisi mevcut; sabıka kaydı temiz değil."
    )

    report = guard.check_kvkk(text)

    print(report.to_markdown())
    print("\n--- Maskeleme ---")
    print(report.redacted)
    print("\n--- JSON özet ---")
    d = report.to_dict()
    print("risk:", d["risk_level"], "| açık rıza:", d["requires_explicit_consent"])
    print("maddeler:", d["articles_referenced"])


if __name__ == "__main__":
    main()
