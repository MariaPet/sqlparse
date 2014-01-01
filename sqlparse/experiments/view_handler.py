from sqlparse import sql,tokens
import sqlparse


class ViewHandler(object):
    
	def query_matched_views(self,token_list,given_views):
		"""returns the views that exist in the from clause of the query
		and also in the given views dictionary"""
		for idx,token in enumerate(token_list.tokens):
			if(isinstance(token,sql.IdentifierList)):
				previous = token_list.token_prev(idx)
				if(previous.normalized == 'FROM' and previous.ttype==tokens.Token.Keyword):
					for subtoken in token.get_sublists():
						if(isinstance(subtoken,sql.Identifier)):
							view_alias = None
							view_name = subtoken.get_real_name()
							if(subtoken.has_alias()):
								view_alias = subtoken.get_alias()
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
						yield attribute.value
							    	
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
test = ViewHandler()
given_views = {'view1':('A1','A2','A3'),'view2':('A1','A2','A3','A4'),'view3':('A1','A2','A4')}
sql_test = 'select v1.name as nom,V2.code,count(V2.id) from view1 as v1, view2,sales where v1.code like "12345" group by nom;'

parsed = sqlparse.parse(sql_test)
tokenlist = sql.TokenList(parsed[0].tokens)

print dict(test.query_matched_views(tokenlist,given_views))
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
print list(test.get_view_attributes(tokenlist,'V2'))