import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_place_coordinates import compare


class CoordinateAuditTests(unittest.TestCase):
    def row(self,name='Perry',kind='Village'):
        return dict(moratorium_id='synthetic',state_abbrev='OH',jurisdiction=name,
                    jurisdiction_type=kind,latitude='39.6',longitude='-82.2')
    def place(self,name='Perry village'):
        return dict(USPS='OH',NAME=name,GEOID='synthetic-place',INTPTLAT='41.763674',INTPTLONG='-81.143013')
    def test_large_distance_is_a_review_prompt_without_input_mutation(self):
        rows=[self.row()];before=copy.deepcopy(rows)
        result=compare(rows,[self.place()])
        self.assertEqual(result[0]['disposition'],'distance_review_required')
        self.assertGreater(result[0]['distance_km'],200)
        self.assertEqual(rows,before)
    def test_ambiguous_matches_are_not_selected(self):
        result=compare([self.row()],[self.place(),self.place()])
        self.assertEqual(result[0]['disposition'],'ambiguous')
        self.assertNotIn('census_geoid',result[0])
    def test_township_is_not_joined_to_same_named_place(self):
        self.assertEqual(compare([self.row(kind='Township')],[self.place()]),[])
    def test_city_word_is_part_of_grove_city_name(self):
        result=compare([self.row('City of Grove City','City')],[self.place('Grove City city')])
        self.assertEqual(result[0]['lookup_name'],'Grove City city')
        self.assertEqual(result[0]['match_count'],1)


if __name__=='__main__':unittest.main()
