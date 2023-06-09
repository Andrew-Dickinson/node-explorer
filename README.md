
# Node Explorer

Utilizes Andrew's [OSPF JSON API](http://api.andrew.mesh/api/v1/ospf/linkdb) to present an interactive
visualization of the mesh OSPF data. Can be used to debug or explore OSPF current state information.

![A screenshot of the data explorer tool in use](/screenshots/img1.png?raw=true)

## Get Started

If you just want to use this tool and don't need to host your own copy or do development work,
just connect to the mesh and then check it out at: 

[http://node-explorer.andrew.mesh](http://node-explorer.andrew.mesh)

## Built with
- [NetworkX](https://networkx.org/)
- [Flask](https://flask.palletsprojects.com/en/2.3.x/)
- [Cytoscape.js](https://js.cytoscape.org/)
- [Bootstrap](https://getbootstrap.com/)
- [ReactStrap](https://reactstrap.github.io/)
- [React](https://react.dev/)

## Setup 

Pre-requisites: `python3` (>3.8) and `npm` (node 16) available via the shell. Check with:
```sh
python3 --version
node --version
```


Then setup by cloning, creating a virtual env, creating the `.env` file, and installing the dependencies
```sh
git clone https://github.com/Andrew-Dickinson/node-explorer
cd node-explorer
cd explorer-backend/
python3 -m venv .venv
source .venv/bin/activate
cp .env_example .env
pip install -e .
cd ../explorer-frontend/ && npm install
```

## Running the unit tests

Follow the instructions under "Setup" above, to clone a local copy of this application and activate
the virtual environment. Then install the test dependencies with:
```sh
cd explorer-backend/
pip install -e ".[test,dev]"
```

Finally, invoke the test suite using pytest:
```
pytest test/
```

## Running the dev servers for local development

Start the dev servers with the following commands (multiple shell sessions recommended):
```sh
cd explorer-backend/ && flask run &
cd explorer-frontend/ && npm start &
```

The frontend should be accessible at [http://127.0.0.1:3000](http://127.0.0.1:3000), and the backend at [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Deployment via Docker

To make a production build of this application via docker, simply clone the repo and
use the included build script to create a deployable docker image:

```sh
git clone https://github.com/Andrew-Dickinson/node-explorer
bin/docker_build.sh
```

This should create a docker image called `node-explorer`, which can be run with:
```sh
docker run -d -p 80:80  node-explorer
```

You can confirm the docker container was build succesfully by opening [http://127.0.0.1:80](http://127.0.0.1:80) in your browser.

## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


## Acknowledgments
 * [Best-README-Template](https://github.com/othneildrew/Best-README-Template/)
