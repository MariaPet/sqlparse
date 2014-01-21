import sqlparse
from sqlparse.experiments import view_handler as VH, cnf 
from sqlparse import sql, tokens

given_views = {'View1':('id','name','surname'),'View2':('id','department','area','supervisor'),'View3':('id','type','salary')}
#sql_query = 'Select * from View1 as V1 where (V1.name="Maria" and V1.surname="Petriti");'
#sql_query = 'Select * from View1 AS V1 where (V1.name="Maria" and V1.surname="Petriti") or (V1.name!="Nikos" and V1.surname!="Tades");'
sql_query = 'Select V1.name,V1.id,View2.department from View1 as V1, View2 where (V1.name="Maria" and V1.surname="Petriti") or not(View2.area!="Athens" and View2.supervisor!="Tades");'
#sql_query = 'Select * from sales where sales.name=5 or sales.surname=9;'
sql_query = sqlparse.format(sql_query,keyword_case='upper')
parsed_sql = sqlparse.parse(sql_query);
print 'Arxiko query : ',sql_query
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
		attr_in_query[view] = tuple(set(handler.get_view_attributes(parsed_sql[0],view,given_views[view])))
	else:
		attr_in_query[occurrences[view]] = tuple(set(handler.get_view_attributes(parsed_sql[0],occurrences[view],given_views[view])))
		
#Fetching of predicates related to a given view	
for where_clause in parsed_sql[0].tokens:
	if(isinstance(where_clause,sql.Where)):
		predicates_in_query = {}
		for view in occurrences.keys():
			if(occurrences[view] == None):
				predicates_in_query[view] = tuple(set(handler.get_pushed_predicates(where_clause,view,attr_in_query[view]))) 
			else:
				predicates_in_query[occurrences[view]] = tuple(set(handler.get_pushed_predicates(where_clause,occurrences[view],attr_in_query[occurrences[view]],view)))
print 'pushed predicates',predicates_in_query

#Generating query for creating the temporary view
#new_view = GeneratedView()

if(len(occurrences)>0):
	for view in occurrences.keys():
		if(occurrences[view] == None):
			new_view = VH.GeneratedView(view,attr_in_query[view],predicates_in_query[view])
			print new_view.temp_view_query()
			print new_view.transformed_query(sql_query)
		else:
			new_view = VH.GeneratedView(view,attr_in_query[occurrences[view]],predicates_in_query[occurrences[view]])
			print new_view.temp_view_query()
			print new_view.transformed_query(sql_query,occurrences[view])
