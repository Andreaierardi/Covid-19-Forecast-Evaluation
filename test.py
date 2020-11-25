import json
import os

from zoltpy import util
import zoltpy

conn = util.authenticate()
print('\n* projects')


#for project in conn.projects:
 #       print(f'- {project}, {project.id}, {project.name}')

project_name = 'COVID-19 Forecasts'
model_abbr = 'BPagano-RtDriven'
timezero_date = '2020-11-22'
#json_io_dict = util.download_forecast(conn, project_name, model_abbr, timezero_date)
#print(f"downloaded {len(json_io_dict['predictions'])} predictions")


#util.print_models(conn, project_name)
#print(json_io_dict)

#df = util.dataframe_from_json_io_dict(json_io_dict)
#print("dataframe:\n", df)

query = {"units": ["01"]}
project = [project for project in conn.projects if project.name == project_name][0]

print(project.units)

print(dir(project))

print(project.models[0])


# GET FORECAST DATA
f = []
for model in range(len(project.models)):
	for fore in range(len(project.models[model].forecasts)):
		f.append(project.models[model].forecasts[fore].data())


#dataframe = util.dataframe_from_json_io_dict(f)



#QUERIES 

#print(dir(project.submit_query))
#job = project.submit_query(zoltpy.connection.QueryType.FORECASTS, query)
#util.busy_poll_job(job)  # does refresh()
#rows = job.download_data()
#print(rows)
#print(util.dataframe_from_rows(rows))
#names = []
#for model in project.models:
#	names.append(model.abbreviation)


#json_io_dict = util.download_forecast(conn, project_name, " ", timezero_date)
#df = util.dataframe_from_json_io_dict(json_io_dict)

#print("dataframe:\n", df)
