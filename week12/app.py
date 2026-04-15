# load libraries
from flask import Flask, jsonify, request
import pandas as pd
import os

# start app
app = Flask(__name__)

# load the salary data once when the app starts
salary_data = pd.read_excel('week12/data/Employee Annual Salaried-Diamondback 2025.xlsx')

# clean column names by stripping white space
salary_data.columns = [col.strip() for col in salary_data.columns]

# defining a function that converts a dataframe into a list of JSON dictionaries
def rows_to_json(df):
    """Convert a DataFrame to a list of dicts, handling NaN values."""
    return df.where(pd.notna(df), None).to_dict(orient='records')

""" 
Below is the information for the root directory.
When we go to the root directory '/' there will be a landing page with all of the available endpoints as JSON.
Reminder that you have to run python week12/app.py in the terminal and ensure the app is running before you can actually access this endpoint.  
"""
@app.route('/') # defines the URL endpoint: /
def index():
    return jsonify({
        # we can customize what is shown on this page. It will be shown as JSON, but
        # other API endpoints for landing pages might have fancier built-out pages to show information
        'description': 'University of Maryland Salary Data API',
        'endpoints': [
            {
                'path': '/api/salaries', # this links to /api/salaries
                'method': 'GET',
                'description': 'Return all records in the salary data',
                'params': ['division', 'employee_type', 'min_salary', 'max_salary']
            },
            {
                'path': '/api/salaries/search',
                'method': 'GET',
                'description': 'Search by employee name. Returns all records with case-insensitive partial matches to the query.',
                'params': ['name (required)']
            },
            {
                'path': '/api/salaries/divisions',
                'method': 'GET',
                'description': 'List all unique divisions.',
                'params': []
            },
            {
                'path': '/api/salaries/top',
                'method': 'GET',
                'description': 'Top-N highest-paid employees.',
                'params': ['n (default: 10)']
            },
        ]
    })

"""
Endpoint 1: GET /api/salaries
   Returns all records. 
   Supports optional query parameters

   Examples of parameters:
     ?division=PRES
     ?employee_type=Faculty Regular
     ?min_salary=100000
     ?max_salary=500000
"""
@app.route('/api/salaries') # defines the URL endpoint: /api/salaries
def get_salaries(): # function that runs when this endpoint is accessed
    # create a dataframe that is a copy of our salary_data dataframe, so we don't modify the original
    df = salary_data.copy() 

    ## This is where we define our parameters

    # get the value of ?division= from the URL (returns None if not provided)
    division = request.args.get('division')
    # get the value of ?employee_type= from the URL
    employee_type = request.args.get('employee_type')
    # get the value of ?min_salary= and convert it to a float (number)
    min_salary = request.args.get('min_salary', type=float)
    # get the value of ?max_salary= and convert it to a float
    max_salary = request.args.get('max_salary', type=float)

    # if a division was provided in the URL
    if division:
        # filter the dataframe to only include rows where Division matches.
        # .upper() makes the comparison case-insensitive (PRES will work, but pres won't)
        df = df[df['Division'].str.upper() == division.upper()]
    # if an employee type was provided,
    if employee_type:
        # filter rows where Employee Type matches (case-insensitive).
        df = df[df['Employee Type'].str.lower() == employee_type.lower()]
    # if a minimum salary was provided,
    if min_salary is not None:
        # filter to only rows where salary is greater than or equal to min_salary.
        df = df[df['Appt Base Annual Salary'] >= min_salary]
    # if a maximum salary was provided,
    if max_salary is not None:
        # filter to only rows where salary is less than or equal to max_salary.
        df = df[df['Appt Base Annual Salary'] <= max_salary]
    
    # return the result after this filtering
    return jsonify({
        # return the total number of rows after filtering
        'count': len(df),
        # convert dataframe to JSON format using the rows_to_json() function we defined earlier.
        'results': rows_to_json(df)
    })


"""
Endpoint 2: GET /api/salaries/search?name=

Name parameter is required. 
Example: GET /api/salaries/search?name=Frese

Case-insensitive partial-match search on the "Primary Name" column 

"""
@app.route('/api/salaries/search') # defines the endpoint: /api/salaries/search
def search_by_name():  # function that runs when this endpoint is accessed
    
    ### Defining our name parameter
    # get the value of ?name= from the URL
    # if no name is provided, default to an empty string ''
    name = request.args.get('name', '')
    # if the user did NOT provide a name parameter,
    if not name:
        # return an error message as JSON
        # 400 error means the client made a mistake
        ### This makes our name parameter required
        return jsonify({'error': 'Provide a ?name= query parameter'}), 400

     # create a filtered dataframe that looks at 'Primary Name' to see if it contains 
     # the string that the user specified in ?name= in the URL
     # case=False makes it case-insensitive
     # na=False prevents errors if there are missing values
    df = salary_data[salary_data['Primary Name'].str.contains(name, case=False, na=False)]
    
    # return results as JSON
    return jsonify({
        # return count of total rows 
        'count': len(df),
        # return the data as JSON
        'results': rows_to_json(df)
    })

"""
Endpoint 3: GET /api/salaries/divisions
Returns a list of all unique divisions in the dataset.
No parameters
"""
@app.route('/api/salaries/divisions')
def get_divisions():
    divisions = sorted(salary_data['Division'].dropna().unique().tolist())
    return jsonify({'divisions': divisions})

"""
Endpoint 4: GET /api/salaries/top?n=10

Returns the top N highest-paid employees. Default N is 10.
"""
@app.route('/api/salaries/top')
def top_earners():
    ### Defining our parameter n
    # if there is something after ?n=, save it to the object n.
    # if there is nothing after ?n=, default to 10
    # ensure n is an integer
    n = request.args.get('n', default=10, type=int)
    # filter our salary data to the largest N salaries
    df = salary_data.nlargest(n, 'Appt Base Annual Salary')
    
    # return as JSON
    return jsonify({
        'count': len(df), # give the count of rows (this should be same as N)
        'results': rows_to_json(df) # turn rows to json
    })


if __name__ == '__main__':
    # debug=True gives you auto-reload when you save the file
    # port=5000 tells Flask which port to run the server on
    # so you can access it at http://127.0.0.1:5000/
    app.run(debug=True, port=5000)
