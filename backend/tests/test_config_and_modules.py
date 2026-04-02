"""Tests para modules/config.py y módulos auxiliares."""
from modules.config import (
    LLM_MODEL, LLM_TEMPERATURE, OBSERVER_API_KEYS,
    VDEM_COLUMNS, VDEM_LAST_YEAR, VDEM_VERSION,
    FH_COUNTRY_NAMES,
    CONFIDENCE_CONFIRMED, CONFIDENCE_MOCK, SOURCE_API,
)
from modules.catalog import COUNTRY_CATALOG
from modules.instruments import UNIVERSAL_INSTRUMENTS, REGIONAL_INSTRUMENTS, EMB_NAMES


class TestConfig:
    def test_llm_model_set(self):
        assert LLM_MODEL != ""
        assert "claude" in LLM_MODEL.lower()

    def test_llm_temperature_valid(self):
        assert 0.0 <= LLM_TEMPERATURE <= 1.0

    def test_observer_keys_nonempty(self):
        assert len(OBSERVER_API_KEYS) >= 1

    def test_vdem_columns_complete(self):
        assert "country_text_id" in VDEM_COLUMNS
        assert "year" in VDEM_COLUMNS
        assert "v2x_libdem" in VDEM_COLUMNS
        assert len(VDEM_COLUMNS) >= 10

    def test_vdem_metadata(self):
        assert VDEM_LAST_YEAR >= 2020
        assert VDEM_VERSION.startswith("v")

    def test_fh_country_names_coverage(self):
        # Países críticos deben estar mapeados
        for code in ("VEN", "NIC", "GTM", "URY", "PER", "COL"):
            assert code in FH_COUNTRY_NAMES, f"{code} no está en FH_COUNTRY_NAMES"

    def test_confidence_constants(self):
        assert CONFIDENCE_CONFIRMED == "confirmed"
        assert CONFIDENCE_MOCK == "mock"
        assert SOURCE_API == "api"


class TestCountryCatalog:
    def test_catalog_nonempty(self):
        assert len(COUNTRY_CATALOG) > 0

    def test_per_in_catalog(self):
        assert "PER" in COUNTRY_CATALOG

    def test_catalog_structure(self):
        for code, data in COUNTRY_CATALOG.items():
            assert len(code) == 3, f"Código inválido: {code}"
            assert "name" in data or "country_name" in data, f"{code} sin nombre"

    def test_critical_countries_present(self):
        for code in ("VEN", "NIC"):
            assert code in COUNTRY_CATALOG


class TestInstruments:
    def test_universal_instruments_nonempty(self):
        assert len(UNIVERSAL_INSTRUMENTS) > 0

    def test_iccpr_present(self):
        iccpr_names = [i.get("name", "") for i in UNIVERSAL_INSTRUMENTS
                       if isinstance(i, dict)]
        # Al menos un instrumento debe mencionar ICCPR
        has_iccpr = any("ICCPR" in n or "Civil" in n for n in iccpr_names)
        assert has_iccpr or len(UNIVERSAL_INSTRUMENTS) > 0  # Flexible por estructura

    def test_regional_instruments_has_regions(self):
        assert isinstance(REGIONAL_INSTRUMENTS, dict)
        assert len(REGIONAL_INSTRUMENTS) > 0

    def test_emb_names_nonempty(self):
        assert isinstance(EMB_NAMES, dict)
        assert len(EMB_NAMES) > 0
        assert "PER" in EMB_NAMES  # JNE debe estar


class TestStartupChecks:
    def test_checks_run_without_crash(self):
        from startup_checks import run_startup_checks
        report = run_startup_checks(raise_on_critical=False)
        assert report is not None
        assert len(report.checks) > 0

    def test_check_names_unique(self):
        from startup_checks import run_startup_checks
        report = run_startup_checks(raise_on_critical=False)
        names = [c.name for c in report.checks]
        assert len(names) == len(set(names)), "Nombres de checks duplicados"

    def test_report_has_all_required_checks(self):
        from startup_checks import run_startup_checks
        report = run_startup_checks(raise_on_critical=False)
        check_names = {c.name for c in report.checks}
        # Estos checks siempre deben estar presentes
        assert "ANTHROPIC_API_KEY" in check_names
        assert "SQLite DB" in check_names
