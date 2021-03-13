# Flask API generator for peewee models

## version 0.1

This script automatically generates a flask server hosting APIs for models in 
input peewee model file. 

GET and POST api for each model are generated. GET without any argument returns 
all rows in given table. When key value pairs are added as parameters, `WHERE`
cause is added in resulting query with given key value pairs. So data is filtered
according to passed values.

A POST without row id creates a new row with given parameters. If row id is 
sent as paramter `id` then corresponding row is updated.

To see example, please check peewee model db_model.py which is input to the
script and output file FPVAPIserver.py

For now inputs are not validated to check if model/db conditions (eg null/non null,
unique) are met. Also model relationship (like foreign keys) is ignored.
