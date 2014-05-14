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
                            yield view_name.__str__(),view_alias.__str__().encode('ascii','replace')


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


    def get_view_attributes(self,token_list,local_view_name,local_view_attributes):
        """returns all the attributes mentioned in a query that belong to a given view"""
        attribute = None 
        for x,token in enumerate(token_list.tokens):
            if(token.ttype == tokens.Token.Wildcard and token.value == '*' and token_list.token_prev(x).normalized == 'SELECT'):
                for attribute in local_view_attributes:
                    yield attribute	
        else:
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
#check for the case of an asterisk wild card


    def get_view_predicates(self,where,local_view_name,attributes,actual_view_name=None):
        """
        This method receives as parameters a Where Token, the alias with which the view
        is referred within the query, the attributes related to this view and the actual
        view name, if it doesn't have an alias.
        """
        tok_idx = 0
        subtokens = list(where.flatten())
        while (tok_idx < len(subtokens)):
            #comparisons handling
            if(subtokens[tok_idx].ttype == tokens.Token.Operator.Comparison):
                comparison_group = ''
                left = subtokens[:tok_idx]
                left = left[::-1]
                for i in range(len(left)):
                    if(left[i].value.upper() == 'NOT'):
                        comparison_group += left[i].value.upper()+' '
                        break
                for i in range(len(left)):
                    if(left[i].value in attributes and left[i+1].value =='.' and left[i+2].value == local_view_name ):
                        if(actual_view_name == None):
                            comparison_group += left[i+2].value+left[i+1].value+left[i].value
                            break
                        else:
                            comparison_group += actual_view_name+left[i+1].value+left[i].value
                            break
                    elif(left[i].ttype in tokens.Token.Literal):
                        comparison_group += left[i].value
                        break
                comparison_group += subtokens[tok_idx].value
                right = subtokens[tok_idx+1:]
                for i in range(len(right)):
                    if(i == len(right)-1):
                        comparison_group += right[i].value
                        break
                    else:
                        if(right[i].value == local_view_name and right[i+1].value =='.' and right[i+2].value in attributes):
                            if(actual_view_name == None):
                                comparison_group += right[i].value+right[i+1].value+right[i+2].value 
                                break;
                            else:
                                comparison_group += actual_view_name+right[i+1].value+right[i+2].value 
                                break;
                        elif(right[i].ttype in tokens.Token.Literal):
                            comparison_group += right[i].value
                            break;
                print 'to comparsion group pou epistrefei i get view predicates'
                yield comparison_group.encode('ascii','replace')
            tok_idx +=1

    def get_pushed_predicates(self,where,local_view_name,attributes,actual_view_name=None): 
        print'mpainei stin get_pushed_predicates'
        if(actual_view_name!=None):
            normalized = where._to_string().replace(local_view_name+'.',actual_view_name+'.')
            cnf_clause = re.findall(r'\(.*\)',normalized)
        else:
            cnf_clause = re.findall(r'\(.*\)',where._to_string())
        for predicate in cnf_clause:
            #handles multiple predicates, by stripping the outer parentheses
            complex_formula = re.findall(r'(?<=\()\(.*\)(?=\))',predicate)
            if(len(complex_formula)>0):
                for disj in complex_formula:
                    #A complex formula contains multiple conjunctions of disjunctions. We have to retrieve these disjunctions
                    disjunctions = disj.split(' AND ');
                    print disjunctions
                    #disjunctions = re.findall(r'(?:\(.*\)(?= AND))|(?:(?<=AND )\(.*\))',disj)
                    for x in range(len(disjunctions)):
                        pushed = disjunctions[x]
                        print 'pushed :'+pushed
                        for comparison in self.get_view_predicates(where,local_view_name,attributes,actual_view_name):
                            print comparison
                            if (comparison in disjunctions[x]):
                                pushed = pushed.replace(comparison, '')
                        get_pushed = re.findall(r'\((?:\s*OR\s*)+\)',pushed)
                        if(len(get_pushed)>0):
                            yield disjunctions[x].encode('ascii','replace')

class GeneratedView(object):

    __slots__ = ('root', 'root_attributes', 'name', 'attributes', 'predicates')

    def __init__(self,root,query_view_attributes,query_view_predicates):
        self.root = root
        self.name = 'temp_'+self.root
        self.root_attributes = query_view_attributes
        self.predicates = query_view_predicates
        self.attributes = ()

    def temp_view_query(self):
        self.attributes = list(self.root_attributes)
        selected_attributes = ''
        predicate = ''
        for i,attr in enumerate(self.root_attributes):
            """if(i == len(self.root_attributes)-1):
                    selected_attributes += attr+''
                else:
                    selected_attributes += attr+', '"""

            for j,pred in enumerate(self.predicates):
                if('.'+attr in pred and attr in self.attributes):
                    self.attributes.remove(attr) 
        for j,pred in enumerate(self.predicates):
            if(j == len(self.predicates)-1):
                predicate += pred+''
            else:
                predicate += pred+' AND '			
        temp_view_attributes = ''
        for x,attr in enumerate(self.attributes):
            if(x == len(self.attributes)-1):
                temp_view_attributes += attr+''
            else:
                temp_view_attributes += attr+', '	
        if(predicate != ""):
            where_clause = "WHERE "+predicate
        else:
            where_clause = ''
        create_view = 'CREATE VIEW '+self.name+' ('+temp_view_attributes+') AS SELECT '+self.root+'.'+temp_view_attributes+' FROM '+self.root + ' '+where_clause;
        return create_view

    def transformed_query(self,old_sql,root_alias=None):
        if(root_alias != None):
            old_sql = old_sql.replace(root_alias,self.root)
        for predicate in self.predicates:
            if(predicate in old_sql):
                old_sql = old_sql.replace(predicate, '')
        old_sql = old_sql.replace(self.root,self.name)
        if(root_alias != None):
            old_sql = old_sql.replace(self.name+' AS '+self.name,self.name)
        new_sql = old_sql
        return new_sql           
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
	
#	print test.view_exist_in_query(tokenlist,'view1')
#	print '\n'
	attributes= list(test.get_view_attributes(tokenlist,'V1',given_views['View1']))
	print attributes
	
	for token in parsed[0].tokens:
		if(isinstance(token,sql.Where)):
			print list(test.get_view_predicates(token,'V1',attributes))
	
	print '\npushed'
	print list(test.get_pushed_predicate(tokenlist,'V1',attributes))