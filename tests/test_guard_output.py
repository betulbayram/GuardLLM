from guardllm import Guard


def test_check_output_toxicity():
    guard = Guard()
    result = guard.check_output(response="You are an idiot", prompt="hi")
    assert not result.safe
    assert result.threat == "toxicity"


def test_check_output_hallucination():
    guard = Guard()
    result = guard.check_output(
        prompt="Nüfus?",
        response="Nüfus 15 milyon kişidir.",
        context="Nüfus 5.8 milyon kişidir.",
    )
    assert not result.safe
    assert result.threat == "hallucination"


def test_check_output_pii_redacted():
    guard = Guard()
    result = guard.check_output(response="İletişim: ali@firma.com")
    assert not result.safe
    assert "[EMAIL]" in result.redacted


def test_check_output_safe():
    guard = Guard()
    result = guard.check_output(
        prompt="Selam",
        response="Merhaba, size nasıl yardımcı olabilirim?",
        context="Merhaba, size nasıl yardımcı olabilirim?",
    )
    assert result.safe
