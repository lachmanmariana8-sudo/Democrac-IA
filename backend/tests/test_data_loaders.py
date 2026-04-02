"""Tests para modules/data_loaders.py — verifica loaders con datos mock/None."""
import pytest
from modules.data_loaders import (
    get_vdem_country,
    get_freedom_house_country, derive_civil_liberties_from_fh,
    get_rsf_country,
    get_pei_country,
)


class TestVDem:
    def test_load_returns_none_when_missing(self, tmp_path, monkeypatch):
        import modules.data_loaders as dl
        monkeypatch.setattr(dl, "VDEM_CSV_PATH", str(tmp_path / "nonexistent.csv"))
        df = dl.load_vdem_data()
        assert df is None

    def test_get_country_returns_none_for_none_df(self):
        result = get_vdem_country(None, "PER")
        assert result is None

    def test_get_country_returns_none_for_missing_country(self):
        result = get_vdem_country(None, "XYZ")
        assert result is None


class TestFreedomHouse:
    def test_load_returns_none_when_missing(self, tmp_path, monkeypatch):
        import modules.data_loaders as dl
        monkeypatch.setattr(dl, "FH_CSV_PATH", str(tmp_path / "nonexistent.csv"))
        df = dl.load_freedom_house_data()
        assert df is None

    def test_get_country_returns_none_for_none_df(self):
        result = get_freedom_house_country(None, "PER")
        assert result is None

    def test_get_country_unknown_code_returns_none(self):
        result = get_freedom_house_country(None, "XYZ")
        assert result is None

    def test_derive_civil_liberties_free_country(self):
        fh_data = {"civil_liberties_rating": 1, "political_rights_rating": 1, "edition": 2025}
        result = derive_civil_liberties_from_fh(fh_data)
        assert result["freedom_of_press"] == "guaranteed"
        assert result["judicial_independence"] == "strong"
        assert result["political_prisoners"] is False

    def test_derive_civil_liberties_not_free(self):
        fh_data = {"civil_liberties_rating": 7, "political_rights_rating": 7, "edition": 2025}
        result = derive_civil_liberties_from_fh(fh_data)
        assert result["freedom_of_press"] == "severely_restricted"
        assert result["judicial_independence"] == "captured"
        assert result["political_prisoners"] is True

    def test_derive_civil_liberties_structure(self):
        fh_data = {"civil_liberties_rating": 4, "political_rights_rating": 4, "edition": 2025}
        result = derive_civil_liberties_from_fh(fh_data)
        required_keys = [
            "freedom_of_press", "freedom_of_assembly", "judicial_independence",
            "political_prisoners", "cl_rating", "pr_rating", "data_source"
        ]
        for key in required_keys:
            assert key in result, f"Falta clave: {key}"


class TestRSF:
    def test_load_returns_none_when_missing(self, tmp_path, monkeypatch):
        import modules.data_loaders as dl
        monkeypatch.setattr(dl, "RSF_CSV_PATH", str(tmp_path / "nonexistent.csv"))
        df = dl.load_rsf_data()
        assert df is None

    def test_get_country_returns_none_for_none_df(self):
        result = get_rsf_country(None, "PER")
        assert result is None


class TestPEI:
    def test_load_returns_none_when_missing(self, tmp_path, monkeypatch):
        import modules.data_loaders as dl
        monkeypatch.setattr(dl, "PEI_CSV_PATH", str(tmp_path / "nonexistent.csv"))
        df = dl.load_pei_data()
        assert df is None

    def test_get_country_returns_none_for_none_df(self):
        result = get_pei_country(None, "PER")
        assert result is None


class TestDataLoaderGracefulFallback:
    """Verifica que todos los loaders manejan None sin lanzar excepciones."""

    @pytest.mark.parametrize("func,args", [
        (get_vdem_country,         (None, "PER")),
        (get_freedom_house_country,(None, "PER")),
        (get_rsf_country,          (None, "PER")),
        (get_pei_country,          (None, "PER")),
    ])
    def test_returns_none_gracefully(self, func, args):
        result = func(*args)
        assert result is None
