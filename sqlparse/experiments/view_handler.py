from sqlparse import sql,tokens
import sqlparse


class ViewHandler(object):
    
	def views_in_from(self,statement,given_views):
		"""returns the views that are mentioned in the from clause of the query"""
		parsed=sqlparse.parse(statement)#this a tuple of Statement objects
		token_list = sql.TokenList(parsed[0].tokens)
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
								yield view_name.__str__(),view_alias.__str__()
	
	def get_identifiers(self,token_list,identifiers_list=[])	:
		""" recursive method that fetches identifiers from a token list"""						
		for token in token_list.tokens:
			if(isinstance(token,sql.Identifier)):
				identifiers_list.append(token)
			if(token.is_group()):
				for identifier in token.get_sublists():
					if(isinstance(identifier,sql.Identifier)):
						identifiers_list.append(identifier)
						identifiers_list=(self.get_identifiers(identifier,identifiers_list))
					elif(identifier.is_group()):
						identifiers_list=(self.get_identifiers(identifier,identifiers_list))
		return identifiers_list
	
	
	
	def get_view_attributes(self,token_list,view):
		"""returns all the attributes mentioned in a query that belong to a given view"""
		#parsed=sqlparse.parse(statement)#this a tuple of Statement objects
		#token_list = sql.TokenList(parsed[0].tokens)
		
		#pairnei to alias tis view an exei, mporei na ginei ksexwristi methodos
		for token in token_list.tokens:
			if(isinstance(token,sql.IdentifierList)):
				print 'to token einai I dentifierList : ',token
				for identifier in token.get_sublists():
					print 'sublist :',identifier
					if(isinstance(identifier,sql.Identifier) and identifier.has_alias()):
						if(identifier.get_real_name()==view):
							view_alias = identifier.get_alias()
							return view_alias
					else:
						print 'den exei alias'
						return view 
		#yield view
		    	
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
            
            
test = ViewHandler()
given_views = {'view1':('A1','A2','A3'),'view2':('A1','A2','A3','A4'),'view3':('A1','A2','A4')}
sql_test = 'select v1.name as nom,V2.code,count(V2.id) from view1 as v1, view2 where v1.code like "12345" group by nom;'
print dict(test.views_in_from(sql_test,given_views))
parsed = sqlparse.parse(sql_test)
tokenlist = sql.TokenList(parsed[0].tokens)
identifiers = test.get_identifiers(tokenlist)
for x,token in enumerate(identifiers):
	print x, " ",token.normalized,' ',token.__class__.__name__
	
print test.get_view_attributes(tokenlist,'view1')