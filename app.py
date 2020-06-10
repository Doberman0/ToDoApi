#!flask/bin/python
from flask import Flask, jsonify #jsonify for RESTFUL services 
from flask import abort # To throw error 404s
from flask import make_response
from flask import request # Allows us to make requests
from flask import url_for # Top help make a more user-friendly interface

app = Flask(__name__)

# We won't use a database for this demo project because it's a simply to do app
# Don't do this for larger projects, as this method only works on a single process

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol', 
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web', 
        'done': False
    }
]

# Taking a task from our database and creating a new task w/ id being replaced by uri
# URI is more user friendly than id
def make_public_task(task):
	new_task = {}
	for field in task:
		if field == 'id':
			new_task['uri'] = url_for('get_task', task_id=task['id'], _external=True)
		else:
			new_task[field] = task[field]
	return new_task

# ------------------------------------ GET requests ------------------------
# Get a json response of all the tasks
# We now use make_public_task
@app.route('/todo/api/v1.0/tasks', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': [make_public_task(task) for task in tasks]})

# Get a specific task by id
#The addition of <int:task_id> tells Flask that it expects an integer which is the parameter, task_id 
@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
	# Get a list of all the tasks for a given id
	task = [task for task in tasks if task['id'] == task_id]
	if len(task) == 0:
		abort(404) # Throw an error 404 - no task found
	return jsonify({'task': task[0]})

# ------------------------------------ POST requests ---------------------------
# Inserting item into our todo lost via POST
@app.route('/todo/api/v1.0/tasks', methods=['POST'])
def create_task():
	# If there isn't a proper json request or the data isn't formulate properly
	if not request.json or not 'title' in request.json:
		abort(400)
	task = {
		'id': tasks[-1]['id']+1, #increment latest id
		'title': request.json['title'],
		'description': request.json.get('description', ''), #defaults to empty description if not provided
		'done': False # Task isn't initially done
	}
	tasks.append(task)
	# Return the json of the task + code 201 (successfully completed)
	return jsonify({'task': task}), 201

# ------------------------------------- PUT requests ----------------------------
# Update first of the tasks with the ID given
@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
	# Get all tasks with the id, task_id
	task = [task for task in tasks if task['id'] == task_id]
	# If there are no tasks to update/the task id doesn't exist
	if len(task) == 0:
		abort(404)
	# If it's not a json request  
	if not request.json:
		abort(400)
	# Non unicode title
	if 'title' in request.json and type(request.json['title']) != unicode:
		abort(400)
	# Non uniunicode description
	if 'description' in request.json and type(request.json['description']) is not unicode:
		abort(400)
	#Task completion is not boolean
	if 'done' in request.json and type(request.json['done']) is not bool:
		abort(400)
	task[0]['title'] = request.json.get('title', task[0]['title'])
	task[0]['description'] = request.json.get('description', task[0]['description'])
	task[0]['done'] = request.json.get('done', task[0]['done'])
	return jsonify({'task': task[0]})

# ----------------------------------- DELETE requests -----------------------------
@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
	task = [tasl for task in tasks if task['id']==task_id]
	if len(task) == 0:
		abort(404)
	tasks.remove(task[0])
	return jsonify({'return': True})


# ----------------------------------- Error handling ----------------------------
#We make our own error handler to return a json response
@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    app.run(debug=True)