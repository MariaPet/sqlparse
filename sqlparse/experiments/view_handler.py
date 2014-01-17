from sqlparse import sql,tokens
import sqlparse
import re


class ViewHandler(object):
    
	def query_matched_views(self,token_list,given_views):
		"""returns the views that exist in the from clause of the query
		and also in the given views dictionary"""
		for idx,token in enumerate(token_list.tokens):
			if(idx>0):
				previous = token_list.token_prev(idx)
				#In case there are multiple view or table names in a query from clause
				if(previous.normalized == 'FROM' and previous.ttype==tokens.Token.Keyword):
					if(isinstance(token,sql.IdentifierList)):
						for subtoken in token.get_sublists():
							if(isinstance(subtoken,sql.Identifier)):
								view_alias = None
								view_name = subtoken.get_real_name()
								if(subtoken.has_alias()):
									view_alias = subtoken.get_alias()
								if(view_name in given_views):
									yield view_name.__str__(),view_alias
					#In case there is just one view or table names in a query from clause
					if(isinstance(token,sql.Identifier)):
						view_alias = None
						view_name = token.get_real_name()
						if(token.has_alias()):
							view_alias = token.get_alias()
						if(view_name in given_views):
							yield view_name.__str__(),view_alias
			
								
	def view_exist_in_query(self,token_list,view):
		"""returns True if the specified view is found in the from clause of the query"""
		exist = False
		for idx,token in enumerate(token_list.tokens):
			if(isinstance(token,sql.IdentifierList)):
					previous = token_list.token_prev(idx)
					if(previous.normalized == 'FROM' and previous.ttype==tokens.Token.Keyword):
						for subtoken in token.get_sublists():
							if(isinstance(subtoken,sql.Identifier)):
								view_name = subtoken.get_real_name()
								if(view_name == view):
									exist = True
		return exist
											
	def get_identifiers(self,token_list,identifiers_tuple=())	:
		""" recursive method that fetches identifiers from a token list"""					
		for token in token_list.tokens:
			if(isinstance(token,sql.Identifier)):
				identifiers_tuple+=(token,)
			if(token.is_group()):
				for identifier in token.get_sublists():
					if(isinstance(identifier,sql.Identifier)):
						identifiers_tuple+=(identifier,)
						identifiers_tuple=(self.get_identifiers(identifier,identifiers_tuple))
					elif(identifier.is_group()):
						identifiers_tuple=(self.get_identifiers(identifier,identifiers_tuple))
		return identifiers_tuple
		
	def get_view_attributes(self,token_list,local_view_name):
		"""returns all the attributes mentioned in a query that belong to a given view"""
		attribute = None 
		identifiers = self.get_identifiers(token_list)
		for x,identifier in enumerate(identifiers):
			id_tokens = sql.TokenList(list(identifier.flatten()))
			for idx,token in enumerate(id_tokens.tokens):
				if(token.ttype == tokens.Token.Name and token.value == local_view_name):
					next_token = id_tokens.token_next(idx)
					if(next_token == None):
						continue
					elif(next_token.ttype == tokens.Token.Punctuation and next_token.value == '.'):
						attribute = id_tokens.token_next(idx+1)
						yield attribute.value.encode('ascii','replace')
						
	def get_view_predicates(self,where,local_view_name,attributes):
		"""generates <Comparison> objects which contain the given view's attributes"""
		tok_idx = 0
		subtokens = list(where.flatten())
		n=len(subtokens)
		
		while (tok_idx < n):
			#comparisons handling
			if(subtokens[tok_idx].ttype == tokens.Token.Operator.Comparison):
				comparison_group = ''
				left = subtokens[:tok_idx]
				left = left[::-1]
				for i in range(len(left)):
					if(left[i].ttype == tokens.Token.Name and left[i+1].value =='.' and left[i+2].ttype == tokens.Token.Name):
						comparison_group += left[i+2].value+left[i+1].value+left[i].value
						break;
					elif(left[i].ttype in tokens.Token.Literal):
						comparison_group += left[i].value
						break;
				comparison_group += subtokens[tok_idx].value		
				right = subtokens[tok_idx+1:]
				for i in range(len(right)):
					if(i == len(right)-1):
						comparison_group += right[i].value
						break;
					else:
						if(right[i].ttype == tokens.Token.Name and right[i+1].value =='.' and right[i+2].ttype == tokens.Token.Name):
							comparison_group += right[i].value+right[i+1].value+right[i+2].value 
							break;
						elif(right[i].ttype in tokens.Token.Literal):
							comparison_group += right[i].value
							break;
				yield comparison_group.encode('ascii','replace')
			tok_idx +=1
		
		"""for token in token_list.tokens:
			if(isinstance(token,sql.Where)):
				for comparison in token.get_sublists():
					if(isinstance(comparison,sql.Comparison)):
						for identifier in comparison.get_sublists():
							if(isinstance(identifier,sql.Identifier)):
								names = list(identifier.flatten())
								for idx in range(len(names)):
									if(names[idx].ttype == tokens.Token.Name and names[idx].value == local_view_name and 
									(names[idx+2].value in attributes)):
										yield comparison"""
	
	def get_pushed_predicate(self,where,local_view_name,attributes):
		"""returns a <Comparison> object containing the pushed predicates"""
		comparisons = list(self.get_view_predicates(where,local_view_name,attributes))
		for comparison in comparisons:
			print comparison
			pushed = re.findall(r'(.*\..*=".*")|(?:.*\..*=\d*,?\.?(\d?)*)',comparison)
			print pushed
			if(pushed!=[]):
				yield pushed[0][0]
			else:
				yield None
			
		
		
		
			#if( (isinstance(comparison.left,sql.Identifier) and (comparison.right.ttype in tokens.Token.Literal.Number)) or(isinstance(comparison.right,sql.Identifier) and (comparison.left.ttype in tokens.Token.Literal.Number)) ):
				#return comparison
				
								    	
class GeneratedView(object):

	root=None
	name=None
	attributes=[]

	def root_exists(self,given_views,query_views):
		return False

	def get_root(self,given_views):
		pass

	def generate_name(self):
		pass

	def get_attributes_from_root(parent,query_views_attributes):
		pass

	def __init__(self,given_views,query_views,query_views_attributes):
		if(self.root_exists(given_views,query_views)):
			root=self.get_root(given_views)
			name=self.generate_name()
			attributes=self.get_attributes_from_root(root,query_views_attributes)
            
#--------------- debugging -----------------------------------
if __name__ == "__main__":           
	test = ViewHandler()
	given_views = {'View1':('A1','A2','A3'),'view2':('A1','A2','A3','A4'),'view3':('A1','A2','A4')}
	#sql_test = 'select v1.name as nom,V2.code,count(V2.id) from View1 as v1,view2 where v1.code = 2 group by nom;'
	sql_test = 'Select * from View1 as V1 where (V1.name=V1.A1 and V1.surname="Petriti") or not(V1.name!="Nikos" and V1.surname!="Tades");'
	
	parsed = sqlparse.parse(sql_test)
	tokenlist = sql.TokenList(parsed[0].tokens)
	
	print dict(test.query_matched_views(parsed[0],given_views))
	print'\n'
	identifiers = test.get_identifiers(tokenlist)
	print 'arithmos identifiers:',len(identifiers)
	for x,token in enumerate(identifiers):
		print x, " ",token.normalized,' ',token.__class__.__name__
	print '\n\n'	
	
	identifiers2 = test.get_identifiers(tokenlist)
	print 'arithmos identifiers:',len(identifiers2)
	for x,token in enumerate(identifiers2):
		print x, " ",token.normalized,' ',token.__class__.__name__
	
	print test.view_exist_in_query(tokenlist,'view1')
	print '\n'
	attributes= list(test.get_view_attributes(tokenlist,'V1'))
	print attributes
	
	for token in parsed[0].tokens:
		if(isinstance(token,sql.Where)):
			print list(test.get_view_predicates(token,'V1',attributes))
	
	print '\n'
	print list(test.get_pushed_predicate(tokenlist,'V1',attributes))