import docker
from flask import Flask, render_template, redirect, url_for, request, session
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
app.secret_key = "devops_secret_key"

# Connect to MongoDB
try:
    mongo_client = MongoClient('mongodb://mongodb:27017/', serverSelectionTimeoutMS=2000)
    db = mongo_client['docker_db']
    history_col = db['cleanup_history']
except:
    print("Mongo not connected yet...")

# Connect to Docker
docker_client = docker.from_env()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'password':
            session['user'] = 'admin'
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Modules 1-4: Fetching Data
    containers = docker_client.containers.list(all=True)
    images = docker_client.images.list()
    volumes = docker_client.volumes.list()
    networks = docker_client.networks.list()
    
    # Module 5: Fetch History from MongoDB
    logs = list(history_col.find().sort("timestamp", -1))
    
    return render_template('index.html', 
                           containers=containers, 
                           images=images, 
                           volumes=volumes, 
                           networks=networks,
                           logs=logs)

@app.route('/prune/<type>')
def prune(type):
    if 'user' not in session: return redirect(url_for('login'))
    
    reclaimed_info = "0"
    protected_domain = 'university'
    
    # Updated Self-Preservation List: Shielding the entire infrastructure
    # This prevents the app from deleting its own UI, DB, or CI/CD engine
    my_project_keywords = ["dockercleanerpro", "mongodb", "jenkins-automation"]

    if type == 'containers':
        all_containers = docker_client.containers.list(all=True)
        count = 0
        for container in all_containers:
            # 1. SHIELD CHECK: Skip project infra AND anything labeled 'university'
            # This fulfills the "University Shield" and "Self-Preservation" requirements
            is_protected_infra = any(kw in container.name.lower() for kw in my_project_keywords)
            is_university_shielded = container.labels.get('domain') == protected_domain

            if is_protected_infra or is_university_shielded:
                continue
            
            # 2. DELETE only if stopped (Exited or Created but not running)
            if container.status in ['exited', 'created']:
                container.remove(force=True)
                count += 1
        reclaimed_info = f"{count} containers"

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)