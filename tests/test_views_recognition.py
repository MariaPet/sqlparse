import pytest
import unittest
from sqlparse.experiments import view_handler as v
import sqlparse

given_views = {'view1':('name','code','A3'),'view2':('code','A2','A3','A4'),'view3':('A1','A2','A4')}
sql = 'select v1.name as nom,V2.code,count(*) from view1 as v1, view2 as v2 where v1.code like "12345" group by nom;'
sql_tokens = sqlparse.parse(sql)[0].tokens
tokenList = sqlparse.sql.TokenList(sql_tokens)

handler = v.ViewHandler()

class TestViewHandler(unittest.TestCase):

	mentioned_views = list(handler.views_in_from(sql,given_views))
	identifier_list = handler.get_identifiers(tokenList)
	attributes = list(handler.get_view_attributes(sql,mentioned_views[0]))
#---------------------------------------------------------------------------------	
	def test_views_type(self):
		assert(isinstance(self.mentioned_views,list))
		
	def test_views_mapping(self):
		view1 = self.mentioned_views[0]
		view2 = self.mentioned_views[1]
		assert(view1 == 'view1')
		assert(view2 == 'view2')
		
	def test_views_length(self):
		length = len(self.mentioned_views)
		assert(length == 2)
#----------------------------------------------------------------------------------

	def test_get_identifiers_class(self):
		wrong_class = True
		for token in self.identifier_list:
			if(isinstance(token, sqlparse.sql.Identifier)):
				wrong_class = False
		assert(wrong_class == False)
	
#----------------------------------------------------------------------------------	
	def test_attributes_belong_to_root(self):
		root_view = given_views[self.mentioned_views[0]]
		assert(self.attributes in root_view)
    
	def test_attributes_mapping(self):
		attr1 = self.attributes[0]
		attr2 = self.attributes[1]
		assert(attr1 == given_views['view1'][0])
		assert(attr2 == given_views['view1'][1])
        
	def test_A3_not_in_attributes(self):
		check_attr = False
		if('A3' in self.attributes):
			check_attr = True
		assert(check_attr == False)
	