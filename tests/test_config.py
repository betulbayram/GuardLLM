from guardllm import Guard, GuardConfig


def test_default_config_loads():
    cfg = GuardConfig.default()
    assert cfg.input.prompt_injection.enabled
    assert cfg.output.hallucination.threshold == 0.7


def test_load_from_yaml():
    cfg = GuardConfig.from_yaml("configs/default_config.yaml")
    assert cfg.input.prompt_injection.threshold == 0.85
    assert "tc_kimlik" in cfg.input.pii_scanner.categories
    assert cfg.input.pii_scanner.action == "mask"


def test_guard_accepts_yaml_path():
    guard = Guard("configs/default_config.yaml")
    assert guard.injection.config.threshold == 0.85
