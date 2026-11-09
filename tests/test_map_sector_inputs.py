import sys
import unittest
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from moratorium_maps.maps import recorded_sector_inputs


class SectorInputs(unittest.TestCase):
    def test_recorded_arrays_override_misleading_prose_and_preserve_ties(self):
        rows = pd.DataFrame([
            dict(state_abbrev='AA', sectors='["solar", "wind"]', trigger='Data center proposal'),
            dict(state_abbrev='BB', sectors='["general"]', trigger='Battery storage discussion'),
            dict(state_abbrev='CC', sectors='[]', trigger='Data center proposal'),
        ])
        counts, dominant = recorded_sector_inputs(rows)
        observed = {(r.state_abbrev, r.sector): r.count for r in counts.itertuples()}
        self.assertEqual(observed, {('AA', 'Solar'): 1, ('AA', 'Wind'): 1,
                                    ('BB', 'Other'): 1, ('CC', 'Unknown'): 1})
        self.assertEqual(dominant, {'AA': 'Mixed', 'BB': 'Other', 'CC': 'Unknown'})

    def test_invalid_recorded_sector_is_not_silently_promoted(self):
        with self.assertRaises(ValueError):
            recorded_sector_inputs(pd.DataFrame([dict(state_abbrev='AA', sectors='["invented"]')]))


if __name__ == '__main__':
    unittest.main()
