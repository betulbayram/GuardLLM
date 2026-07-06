from guardllm.output import HallucinationDetector


def test_unsupported_number_flagged():
    det = HallucinationDetector()
    result = det.check(
        response="Ankara'nın nüfusu 15 milyon kişidir.",
        context="Ankara'nın 2024 nüfusu 5.8 milyon kişidir.",
    )
    assert not result.safe
    assert result.threat == "hallucination"


def test_faithful_response_is_safe():
    det = HallucinationDetector()
    result = det.check(
        response="Ankara'nın nüfusu 5.8 milyon kişidir.",
        context="Ankara'nın 2024 nüfusu 5.8 milyon kişidir.",
    )
    assert result.safe


def test_wrong_year_flagged():
    det = HallucinationDetector()
    result = det.check(
        response="KVKK 2020 yılında yürürlüğe girmiştir.",
        context="6698 sayılı KVKK 7 Nisan 2016 tarihinde yürürlüğe girmiştir.",
    )
    assert not result.safe


def test_no_context_is_safe_but_low_confidence():
    det = HallucinationDetector()
    result = det.check(response="Herhangi bir cevap", context=None)
    assert result.safe
    assert result.confidence <= 0.5
