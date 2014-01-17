import sqlparse
from sqlparse.experiments import view_handler as VH, cnf 
from sqlparse import sql, tokens

given_views = {'View1':('id','name','surname'),'View2':('id','department','area','supervisor'),'View3':('id','type','salary')}
#sql_query = 'Select * from View1 as V1 where (V1.name="Maria" and V1.surname="Petriti");'
#sql_query = 'Select * from View1 as V1 where (V1.name="Maria" and V1.surname="Petriti") or (V1.name!="Nikos" and V1.surname!="Tades");'
sql_query = 'Select * from View1 as V1, View2 where (V1.name="Maria" and V1.surname="Petriti") or not(View2.area!="Athens" and View2.supervisor!="Tades");'
print 'Arxiko query : ',sql_query

parsed_sql = sqlparse.parse(sql_query);

#Convertion to cnf
for where in parsed_sql[0].tokens:
	if(isinstance(where,sql.Where)):
		where_str = where.__str__().encode('ascii','replace')
		#print where_str
		cnf_formula = cnf.where_to_cnf(where)
		#print cnf_formula
		sql_query = sql_query.replace(where_str, cnf_formula)
		print 'Query me cnf : ',sql_query

#Parsing of the converted query one more time
parsed_sql = sqlparse.parse(sql_query);

handler = VH.ViewHandler()
		
#Checking for views occurrence in sql query
#print '\nAytes oi opseis vrethikan st query apo tis given: '
occurrences = dict(handler.query_matched_views(parsed_sql[0],given_views))
#print occurrences

#Fetching of the given view attributes in the query
attr_in_query = {}
for view in occurrences.keys():
	if(occurrences[view] == None):
		attr_in_query[view] = tuple(set(handler.get_view_attributes(parsed_sql[0],view)))
	else:
		attr_in_query[occurrences[view]] = tuple(set(handler.get_view_attributes(parsed_sql[0],occurrences[view])))
	print attr_in_query

#Fetching of predicates related to a given view	
predicates_in_query = {}
	
