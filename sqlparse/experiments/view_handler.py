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
			    view_name = subtoken.get_real_name()
			    if(view_name in given_views):
			        yield view_name.__str__()
		 	
    def get_view_attributes(self,statement,view):
    	"""returns all the attributes mentioned in a query that belong to a given view"""
    	pass
    	
    	
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
            
            
#test = ViewHandler()
#given_views = {'view1':('A1','A2','A3'),'view2':('A1','A2','A3','A4'),'view3':('A1','A2','A4')}
#sql_test = 'select v1.name as nom,V2.code,count(*) from view1 as v1, view2 as v2 where v1.code like "12345" group by nom;'
#print list(test.views_in_from(sql_test,given_views))[0]