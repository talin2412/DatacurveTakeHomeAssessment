This project is made with React(Vite) for the frontend and FAST API for the backend.
We make use of docker images and containers to create trusted envs for code execution and to isolate these from the filesystem which
our servers run on. This will help against malicious user intent.
Using ORM models also help against attacks like SQL injections....


Installation Steps:

Backend:

    Install the dependancies....
    Run `pip install -r requirements.txt`

    Create the Docker Image used for backend python code execution... you might need to `chmod +x runDocker.sh`
    Run `./runDocker.sh`

    Start the Backend server.... you might need to `chmod +x runFast.sh`
    Run `./runFast.sh`


Frontend:

    Run `npm install`

    Run `npm run dev`


