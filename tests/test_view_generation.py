import pytest
import unittest
from sqlparse.experiments import view_handler as v

sql='select v1.name as nom,V2.code,count(*) from view1 as v1, view2 as v2 where v1.code like "12345" group by nom;'
query=sqlparse.parse(sql)

class TestGeneratedView(unittest.TestCase):
	
	view=v.GeneratedView({},{},{})
	
	def test_root_exist(self):
		
		assert (self.view.root_exists({},{})==False)