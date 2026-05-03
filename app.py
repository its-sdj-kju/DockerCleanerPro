import docker
from flask import Flask, render_template, redirect, url_for, request, session, flash
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
        else:
            flash("Invalid username or password. Please try again.") 
    return render_template('login.html')

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    try:
        containers = docker_client.containers.list(all=True)
        images = docker_client.images.list()
        volumes = docker_client.volumes.list()
        networks = docker_client.networks.list()
        logs = list(history_col.find().sort("timestamp", -1))
        
        return render_template('index.html', 
                               containers=containers, 
                               images=images, 
                               volumes=volumes, 
                               networks=networks,
                               logs=logs)
    except Exception as e:
        return f"Error connecting to Docker/Mongo: {e}"

@app.route('/prune/<type>')
def prune(type):
    if 'user' not in session: return redirect(url_for('login'))
    
    reclaimed_info = "0"
    protected_domain = 'university'
    my_project_keywords = ["dockercleanerpro", "mongodb", "jenkins-automation"]

    try:
        if type == 'containers':
            all_containers = docker_client.containers.list(all=True)
            count = 0
            for container in all_containers:
                is_protected_infra = any(kw in container.name.lower() for kw in my_project_keywords)
                is_university_shielded = container.labels.get('domain') == protected_domain
                
                if is_protected_infra or is_university_shielded:
                    continue
                
                if container.status in ['exited', 'created']:
                    container.remove(force=True)
                    count += 1
            reclaimed_info = f"{count} containers"

        elif type == 'images':
            # Safely prune only dangling (unused) images
            res = docker_client.images.prune(filters={'dangling': True})
            reclaimed = res.get('SpaceReclaimed', 0)
            reclaimed_info = f"{reclaimed / (1024*1024):.2f} MB"

        elif type == 'volumes':
            res = docker_client.volumes.prune()
            reclaimed_info = "Volumes cleaned"

        # Log the action to MongoDB
        history_col.insert_one({
            "action": f"Selective {type.capitalize()} Cleanup",
            "reclaimed": reclaimed_info,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user": session['user']
        })
        flash(f"Cleanup Successful: {reclaimed_info}", "success")

    except Exception as e:
        flash(f"Error during {type} prune: {e}", "error")

    # CRITICAL: This return was missing, causing the 500 error!
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)