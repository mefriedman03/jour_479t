# load libraries
from flask import Flask, jsonify, request
import pandas as pd
import os

# start app
app = Flask(__name__)

# load the earmark data once when the app starts
earmark_data = pd.read_excel('week12/data/copy of earmarks for jour479t.xlsx')

# clean column names by stripping white space
earmark_data.columns = [col.strip() for col in earmark_data.columns]

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
        'description': 'Earmarks Data API',
        'endpoints': [
            {
                'path': '/api/earmarks', # this links to /api/earmarks
                'method': 'GET',
                'description': 'Return all records in the earmark data',
                'params': ['agency', 'account', 'location', 'min_amount', 'max_amount']
            },
            {
                'path': '/api/earmarks/search',
                'method': 'GET',
                'description': 'Search by recipient location. Returns all records with case-insensitive partial matches to the query.',
                'params': ['location (required)']
            },
            {
                'path': '/api/earmarks/agencies',
                'method': 'GET',
                'description': 'List all unique agencies.',
                'params': []
            },
            {
                'path': '/api/earmarks/locations',
                'method': 'GET',
                'description': 'List all unique locations.',
                'params': []
            },
            {
                'path': '/api/earmarks/top',
                'method': 'GET',
                'description': 'Top-N highest-amount earmarks.',
                'params': ['n (default: 10)']
            },
        ]
    })

"""
Endpoint 1: GET /api/earmarks
   Returns all records. 
   Supports optional query parameters

   Examples of parameters:
     ?agency=Agricultural Research Service
     ?account=...
     ?location=...
     ?min_amount=100000
     ?max_amount=500000
"""
@app.route('/api/earmarks') # defines the URL endpoint: /api/earmarks
def get_earmarks(): # function that runs when this endpoint is accessed
    # create a dataframe that is a copy of our earmark_data dataframe, so we don't modify the original
    df = earmark_data.copy() 

    ## This is where we define our parameters

    # get the value of ?agency= from the URL (returns None if not provided)
    agency = request.args.get('agency')
    # get the value of ?account= from the URL
    account = request.args.get('account')
    # get the value of ?location= from the URL
    location = request.args.get('location')
    # get the value of ?min_amount= and convert it to a float (number)
    min_amount = request.args.get('min_amount', type=float)
    # get the value of ?max_amount= and convert it to a float
    max_amount = request.args.get('max_amount', type=float)

    # if an agency was provided in the URL
    if agency:
        # filter the dataframe to only include rows where Agency matches.
        # .upper() makes the comparison case-insensitive
        df = df[df['Agency'].str.upper() == agency.upper()]
    # if an account was provided,
    if account:
        # filter rows where Account matches (case-insensitive).
        df = df[df['Account'].str.lower() == account.lower()]
    # if a location was provided,
    if location:
        # filter rows where Location matches (case-insensitive).
        df = df[df['Location'].str.lower() == location.lower()]
    # if a minimum amount was provided,
    if min_amount is not None:
        # filter to only rows where amount is greater than or equal to min_amount.
        df = df[df['House Amount'] >= min_amount]
    # if a maximum amount was provided,
    if max_amount is not None:
        # filter to only rows where amount is less than or equal to max_amount.
        df = df[df['House Amount'] <= max_amount]
    
    # return the result after this filtering
    return jsonify({
        # return the total number of rows after filtering
        'count': len(df),
        # convert dataframe to JSON format using the rows_to_json() function we defined earlier.
        'results': rows_to_json(df)
    })


"""
Endpoint 2: GET /api/earmarks/search?name=

Name parameter is required. 
Example: GET /api/earmarks/search?name=Alford

Case-insensitive partial-match search on the "Recipient" column 

"""
@app.route('/api/earmarks/search') # defines the endpoint: /api/earmarks/search
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

     # create a filtered dataframe that looks at 'Recipient' to see if it contains 
     # the string that the user specified in ?name= in the URL
     # case=False makes it case-insensitive
     # na=False prevents errors if there are missing values
    df = earmark_data[earmark_data['Recipient'].str.contains(name, case=False, na=False)]
    
    # return results as JSON
    return jsonify({
        # return count of total rows 
        'count': len(df),
        # return the data as JSON
        'results': rows_to_json(df)
    })

"""
Endpoint 3: GET /api/earmarks/agencies
Returns a list of all unique agencies in the dataset.
No parameters
"""
@app.route('/api/earmarks/agencies')
def get_agencies():
    agencies = sorted(earmark_data['Agency'].dropna().unique().tolist())
    return jsonify({'agencies': agencies})

"""
Endpoint 3.5: GET /api/earmarks/locations
Returns a list of all unique locations in the dataset.
No parameters
"""
@app.route('/api/earmarks/locations')
def get_locations():
    locations = sorted(earmark_data['Location'].dropna().unique().tolist())
    return jsonify({'locations': locations})

"""
Endpoint 4: GET /api/earmarks/top?n=10

Returns the top N highest-amount earmarks. Default N is 10.
"""
@app.route('/api/earmarks/top')
def top_earners():
    ### Defining our parameter n
    # if there is something after ?n=, save it to the object n.
    # if there is nothing after ?n=, default to 10
    # ensure n is an integer
    n = request.args.get('n', default=10, type=int)
    # filter our earmark data to the largest N amounts
    df = earmark_data.nlargest(n, 'House Amount')
    
    # return as JSON
    return jsonify({
        'count': len(df), # give the count of rows (this should be same as N)
        'results': rows_to_json(df) # turn rows to json
    })


if __name__ == '__main__':
    # debug=True gives you auto-reload when you save the file
    # host='0.0.0.0' allows access from outside localhost (e.g., in a container or remote environment)
    # port=5000 tells Flask which port to run the server on
    # so you can access it at http://127.0.0.1:5000/ or the server's IP
    app.run(debug=True, host='0.0.0.0', port=5000)
