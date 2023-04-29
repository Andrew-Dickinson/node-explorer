
# OSPF Data Explorer

Utilizes Andrew's [OSPF JSON API](http://api.andrew.mesh/api/v1/ospf/linkdb) to present an interactive
visualization of the mesh OSPF data. Can be used to debug or explore OSPF current state information.

## Usage

Check it out at: [http://ospf-explorer.andrew.mesh](http://ospf-explorer.andrew.mesh)

## Self Deployment

To deploy a copy of this package yourself

Pre-requisites: `python3` available via the shell

First, install the CLI via pip:
```shell
pip install nycmesh-ospf-explorer
```

then invoke the tool with the CLI command:
```shell

```

## Built with
- [NetworkX](https://networkx.org/)
- [Flask](https://flask.palletsprojects.com/en/2.3.x/)
- [Cytoscape.js](https://js.cytoscape.org/)
- [Bootstrap](https://getbootstrap.com/)
- [ReactStrap](https://reactstrap.github.io/)
- [React](https://react.dev/)


## Dev Setup

Pre-requisites: `python3` available via the shell

Setup by cloning, creating a virtual env, and installing the application
```sh
git clone https://github.com/nycmeshnet/nycmesh-ospf-explorer
cd nycmesh-ospf-explorer
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

then start the dev servers with the following commands:
```sh

```

## Running the unit tests

Follow the instructions under "Dev Setup" above, to clone a local copy of this application and activate
the virtual environment. Then install the test dependencies with:
```sh
pip install -e ".[test,dev]"
```

Finally, invoke the test suite using pytest:
```
cd backend/
pytest test/
```

## Building to PyPi

Follow the instructions above to clone a local copy of this application, activate
the virtual environment, and run the tests.

Then, build & upload the application with
```
rm -rf dist/*
python -m build .
twine upload dist/*
```

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
