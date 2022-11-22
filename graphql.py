##*************************************************************************
#   file for graphql api calls
#
#   @author	 Jamie Taylor
#   @Creation Date: 22/11/2022
##*************************************************************************

from ariadne import load_schema_from_path, make_executable_schema, graphql_sync, snake_case_fallback_resolvers, ObjectType
from ariadne.constants import PLAYGROUND_HTML
from flask import request, jsonify
from queries import listCommits_resolver


query = ObjectType("Query")
query.set_field("listCommits", listCommits_resolver)

type_defs = load_schema_from_path("schema.graphql")
schema = make_executable_schema(type_defs, snake_case_fallback_resolvers)

def graphql_playground():
    return PLAYGROUND_HTML, 200

def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(schema, data, context_value=request)
    status_code = 200 if success else 400
    return jsonify(result), status_code


    