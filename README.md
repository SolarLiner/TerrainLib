# TerrainLib

A fast, modular library to generate landscapes.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) to lean about the novelties of each version.

## Use

Learning how the library is structured goes a long way in understanding how to 
operate the classes in this library. As such, you should read the section 
[Extend the algorithms](#extend-the-algorithms) to learn more.

Every object is first initialized, then called upon. This allows a preparation 
step if needed, for the algorithms to bootstrap themselves.
Generators and filters output a Terrain object, and Filters and Readers take in
a Terrain object, so you can chain filters to achieve the desired effect.

## Development install

This project uses Pipenv to manage dev and production dependencies. Therefore, 
virtual environment creation and dependency installation is all done with a 
single command:
```bash
pipenv install --dev
```

### Extend the algorithms

There are 3 types of classes, typically; **generators**, **filters** and 
**readers**. The names should be straightforward enough, but here are
descriptions about them:

- **Generators** generate terrain out of input parameters. This allows terrain 
to be created without any prior material.
- **Filters** act on the terrain by applying transformations. They take a 
terrain (and some inputs) and output another terrain, transformed.
- **Readers** Read the terrain and output another type of object entirely. Use 
readers to save an image of your terrain, a 3D mesh, etc.

Each kind has its own base class, that is nothing more than an abstract 
`__call__` function.

Any of these follow a two-step process:

1. The generator is initialized with input parameters. This allows setting up 
internal parameters, bootstrap routines, etc. but **does not generate the 
terrain**. This is done from the `__init__` function.
2. The generator is then called through `__call__` in order to actually process 
data in and/or out. The `__call__` function should return a Terrain object, or, 
in the case of a reader, the resulting object.

All predefined algorithms in this library follow this convention, so see those 
for examples of implementation.

## License

This project is licensed under a GNU LGPLv3 license. Non open-source, commercial
projects are welcomed, but should ask for explicit licensing agreement.