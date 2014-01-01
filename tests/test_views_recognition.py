import pytest
import unittest
from sqlparse.experiments import view_handler as v
import sqlparse

given_views = {'view1':('name','code','A3'),'view2':('code','A2','A3','A4'),'view3':('A1','A2','A4')}
sql = 'select v1.name as nom,view2.code,count(*) from view1 as v1, view2 where v1.code like "12345" group by nom;'
sql_tokens = sqlparse.parse(sql)[0].tokens
tokenList = sqlparse.sql.TokenList(sql_tokens)

handler = v.ViewHandler()

class TestViewHandler(unittest.TestCase):

	matched_views = dict(handler.query_matched_views(tokenList,given_views))
	identifier_list = handler.get_identifiers(tokenList)
	aliased_view_attributes = tuple(handler.get_view_attributes(tokenList,matched_views['view1']))
	view_attributes = list(handler.get_view_attributes(tokenList,'view2' ))
#---------------------------------------------------------------------------------	
	def test_views_type(self):
		assert(isinstance(self.matched_views,dict))
		
	def test_views_mapping(self):
		checked = 0
		for view in self.matched_views.keys():
			assert(view in given_views)
			checked+=1
		assert(checked == len(self.matched_views))
		
	def test_view3_not_in_matched_views(self):
		assert('view3' not in self.matched_views)
					
	def test_views_length(self):
		checked = 0
		for view in self.matched_views.keys():
			if(view in given_views):
				checked+=1
		assert(checked == len(self.matched_views))
	
	def test_matched_views_aliases(self):
		assert(self.matched_views['view1'] == 'v1')
		assert(self.matched_views['view2'] == None)
#----------------------------------------------------------------------------------
	
	def test_view_exist_in_query(self):
		assert(handler.view_exist_in_query(tokenList,'view1') == True)
		assert(handler.view_exist_in_query(tokenList,'view2') == True)
	
#----------------------------------------------------------------------------------

	def test_get_identifiers_class(self):
		wrong_class = True
		for token in self.identifier_list:
			if(isinstance(token, sqlparse.sql.Identifier)):
				wrong_class = False
		assert(wrong_class == False)
	
#----------------------------------------------------------------------------------	
	def test_attributes_belong_to_root(self):
		root_view = given_views['view1']
		for attr in self.aliased_view_attributes:
			assert(attr in root_view)
    
	def test_attributes_mapping(self):
		attr1 = self.aliased_view_attributes[0]
		attr2 = self.aliased_view_attributes[1]
		assert(attr1 == given_views['view1'][0])
		assert(attr2 == given_views['view1'][1])
        
	def test_A3_not_in_attributes(self):
		check_attr = False
		if('A3' in self.aliased_view_attributes):
			check_attr = True
		assert(check_attr == False)
	