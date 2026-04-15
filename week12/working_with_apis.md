# Introduction to APIs 

## What is an API?
An API, or **Application Programming Interface** is a way for programs to interact with each other.

When you use an API, you're sending a request to a server, and the server sends back data, usually in JSON format. An HTTP request, or API call, is a digital message sent from one application (a client) to another (server) to ask for data or perform a specific action.

There are many types of HTTP requests, and I <i>highly</i> encourage you to learn about the other types, but for the purposes of this class, we'll focus on `GET`, which is essentially the client saying to the server, "send me data."

You can pull data from an API, or you can build your own API to share data with others. 

## Why would I want to use an API?
APIs work great when you're working with data that isn't static -- think information that changes frequently, or data you will need to scale up. 

Example:
Maryland Athletics definitely uses a private API to power the data on their website — there are just too many levels to keep track of, so something like a spreadsheet is not feasible to keep track of all sports. With how frequent games are, statistics can be updated much faster with an API than it would be to try and update a CSV.

Additionally, with an API you can request only the information you need. Instead of downloading an entire dataset, you can filter results directly in the URL. This is the power of the **API parameter**.

API parameters refer to pieces of information you include in a URL to an API endpoint to customize what data you will get back. 

## Pulling data from someone else's API
To access data from an API, you will likely need an API key. 



## Creating your own API with Flask
For the purposes of this assignment, we're going to create an API that allows us to access salary data. 

Let's break down what each part of the `app.py` script is doing.

To create our API endpoint, we need to create an app in Flask. We need this to exist, because this app is essentially our server. all `@app.route` functions are instructions we give the server. For example, the `@app.route('/')` function tells our server what it should return when the endpoint of the app is `/`, or the root of the app. 
 
```python
# this initializes our app
app = Flask(__name__)
```

Next, we're creating this `rows_to_json` function, which turns the same data we have in our `salary_data` dataframe into a JSON. We want it to be in JSON format because key-value pairs and lists in JSON map cleanly onto how programming language store data. With JSON, we don't need to guess where columns are or parse them.

JSON is also the format that most APIs are expected to return -- it's the standard. Returning a CSV or Excel is a bit more unusual and harder to work with programatically. 
```python
# defining a function that converts a dataframe into a list of JSON dictionaries
def rows_to_json(df):
    """Convert a dataframe to a list of dictionariess, handling NaN values."""
    return df.where(pd.notna(df), None).to_dict(orient='records')
```

## All of our API endpoints

### 1. `/` (Root) 

```python
@app.route('/')
def index():
```
This is the homepage of the API. When you go to <http://127.0.0.1:5000/> OR <https://[your-codespace-name-here]-5000.app.github.dev/>, you will see a description of the API as well as a description of each of the endpoints and the parameters you can use with each endpoint. 

### 2. `/api/salaries`
The base /api/salaries endpoint will return ALL salaries.

There are four parameters we can use for this endpoint, outlined here:
```JSON
{
"description": "All records",
"method": "GET",
"params": [
"division",
"employee_type",
"min_salary",
"max_salary"
],
"path": "/api/salaries"
},
```

When we actually access the API in our browser, the endpoints will look like this:
```
/api/salaries?division=
/api/salaries?employee_type=
/api/salaries?min_salary=
/api/salaries?max_salary=
```

Let's try an example. 
What if I want to see **only the millionaires** who work at the University of Maryland?

Let's try:
```
/api/salaries?min_salary=1000000
``` 
at the end of our API endpoint. So from our codespace, the full URL would look something like <https://[your-codespace-name-here]-5000.app.github.dev/api/salaries?min_salary=1000000>.

_How many people make at least $1 million?_

What if I want to see only the salaries of people in the PRES division?
The URL would look like <https://[your-codespace-name-here]-5000.app.github.dev/api/salaries?division=PRES>. What do you see?

### 3. `/api/salaries/search` 
This endpoint allows us to search for individual people by name. It does this through a case-insensitive partial match. This means if any part of the name object exactly matches the query after `?name=`, it will be returned in the API's JSON output.


```python
# This is the main portion that does the gruntwork of matching the strings
.str.contains(name, case=False, na=False)
```

Try this:
```
/api/salaries/search?name=Locksley
```

We only have one parameter -- name.

```JSON
{
"description": "Search by employee name",
"method": "GET",
"params": [
"name (required)"
],
"path": "/api/salaries/search"
},
```

Our name parameter is mandatory. What happens if we try to go to:

```
/api/salaries/search
```

We get thrown an error. 

That's because of this line in our code:

```python
# assigning the query in the api endpoint (whatever is after ?name=) to the object 'name'
name = request.args.get('name', '')
    # if there's no object called 'name', AKA, if theres no query in that parameter, then:
    if not name:
        # throw this error to our client
        return jsonify({'error': 'Provide a ?name= query parameter'}), 400
```

### 4. `/api/salaries/divisions`
This returns all possible divisions in the data. Note that there are no parameters:
```JSON
{
"description": "List all unique divisions",
"method": "GET",
"params": [], 
"path": "/api/salaries/divisions"
},
```

### 5. `/api/salaries/top?n=10`
Our final endpoint returns the top N highest-paid employees. 

What happens when you don't include the number, N?
```
/api/salaries/top
```
It doesn't throw us an error. 


## Bonus: making API endpoints with Datasette

