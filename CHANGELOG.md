# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Image input to allow terrains from other programs to be imported, through PIL.
- Thermal erosion

### Changed

- Image input and output are now bitdepth-aware (but must be selected manually)
 Note that this is very much a hack and with some help, the issue opened upstream at PIL
 will pick up and conversion be automatic and seamless.
- Diamond Square generator now works and is fabulous!

### Known bugs

- PILReader will choke on 16bit output for some reason, PIL saying there is "not enough image data". All other supported bitdepths are fine, however.

## [0.0.1] - First test release (2018-06-06)

### Added

- Terrain object with operators
- Diamond Square algorithm generator (which outputs garbage and I have no idea why)
- Image output which generates grayscale images through the PIL library
