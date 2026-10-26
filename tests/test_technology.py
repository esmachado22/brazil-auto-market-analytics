import unittest

from src.transformations.technology import (
    COMBUSTAO,
    ELETRICO,
    HIBRIDO,
    NAO_INFORMADO,
    OUTRO,
    classify_technology,
    is_abve_electrified_component,
)


class TechnologyClassificationTests(unittest.TestCase):
    def test_electric_categories(self) -> None:
        self.assertEqual(classify_technology("BEV"), ELETRICO)
        self.assertEqual(classify_technology("elétricos"), ELETRICO)

    def test_hybrid_categories_include_mhev(self) -> None:
        self.assertEqual(classify_technology("PHEV"), HIBRIDO)
        self.assertEqual(classify_technology("HEV Flex"), HIBRIDO)
        self.assertEqual(classify_technology("MHEV"), HIBRIDO)

    def test_combustion_categories(self) -> None:
        self.assertEqual(classify_technology("Flex"), COMBUSTAO)
        self.assertEqual(classify_technology("DIESEL"), COMBUSTAO)

    def test_missing_and_aggregate_categories_are_not_technologies(self) -> None:
        self.assertEqual(classify_technology(None), NAO_INFORMADO)
        self.assertEqual(classify_technology("TOTAL"), OUTRO)
        self.assertEqual(classify_technology("categoria não publicada"), OUTRO)

    def test_abve_total_excludes_mhev(self) -> None:
        self.assertTrue(is_abve_electrified_component("BEV"))
        self.assertTrue(is_abve_electrified_component("HEV Flex"))
        self.assertFalse(is_abve_electrified_component("MHEV"))
        self.assertFalse(is_abve_electrified_component("TOTAL"))


if __name__ == "__main__":
    unittest.main()
