.. TerrainLib documentation master file, created by
   sphinx-quickstart on Wed Jun 13 20:05:55 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

TerrainLib
======================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

TerrainLib is a library of algorithms used for landscape generation. They include generation, filtering and export
functions to allow to do everything with only one dependency: this library.

TerrainLib aims to be useful at both other projects wanting to include terrain generation, and end-user that don't mind
using scripting as a mean to generate landscape. The API is easy to use by striping away the complicated stuff while
staying customizable.

In a few lines you'll be able to create realistic looking terrain of any size.

Getting Started
---------------

Installation
~~~~~~~~~~~~

TerrainLib is available on PyPi, therefore the easiest way to install it is the following::
    pip install TerrainLib

You can also install the library by downloading a version over the `GitLab project home`_.
.. _GitLab project home: https://gitlab.com/solarliner/terrainlib


Introduction to the library
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Once the library installed, you can import the algorithms from those three places:

* `terrainlib.generator` holds all generators, in sub-categories

* `terrainlib.filters` holds all filters, also in sub-categories

* `terrainlib.readers`, hold all readers, in sub-categories

What do we mean by those words? It may sound weird, as I, a non-native English speaker chose those words, but it allows
everyone to know what they're talking about:

Generator
  An algorithm that only has parameter inputs, and outputs a terrain. This include image import, Perlin noise, etc.

Filter
  An algorithm that both inputs and outputs a terrain, while also accepting other parameter inputs. Those are erosion
  algorithms, manipulations on the terrain, masking, etc.

Reader
  An algorithm that inputs a terrain (and parameters) and output something completely different. These include image
  export, mesh export, texture output, 'playability' scores, etc.

By feeding each the output of the previous algorithm we are able to define *pipelines* that define our terrain.  
Let's create one right now.

A first pipeline
~~~~~~~~~~~~~~~~

Start off by importing the Diamond Square generator. This is a fast noise generation alrogithm that can output detailed
terrain fast - at the cost of not being tile-able.::

    from terrainlib.generators.procedural import DiamondSquareGenerator

The output of that generator will be either too flat or too rough for the terrain to be interesting or even somewhat
realistic. To smooth things out, we need to simulate the process by which rocks and dirt fall downhill.  
We need some thermal erosion.::

    from terrainlib.filters.erosion import ThermalErosionFilter

Last, but not least, we need to export that terrain somewhere. The best way to do that is through an image - it's easily
visualizable, and can be imported anywhere really. Load up the Image exporter:

    from terrainlib.readers.image import PILImageReader

Now, we need to initialize those. We're going to create a 1025 pixel wide terrain, with a decent amount of roughness,
then apply 150 iterations of erosion at standard rates, and then export it to 'terrain_out.png' as a 16-bit image.::

    generator = DiamondSquareGenerator(10, 0.1)
    erosion = ThermalErosionFilter(150)
    img_reader = PILImageReader(PILImageReader.BITDEPTH_16)

Couple of things to notice:

* Due to the way the Diamond Square algorithm works, we do not enter the desired size directly, but the power of two
that will result in the desired size. Here, we're taking the 10th power of two (2^10 = 1024), and the algorithm adds one
to that number (this is a technical restriction, the algorithm needs a center pixel to work with, needing an odd number
of pixels on the side). Thus, we get a 1025 pixel wide terrain.

* We aren't providing a filename to the reader *directly*, because the reader outputs a Pillow image. The actual file
will be saved from the `PIL.Image` instance.

Now, let's setup our pipeline::

    terrain = erosion(generator())
    img = img_reader(terrain)
    img.save('terrain_out.png')

If you run your script, and after some processing time, it will have created a file named 'terrain_out.png' with the 
terrain saved in it. If you open that image as a heightfield, you will see your image in all its glory!

Here is the whole script::

    from terrainlib.generators.procedural import DiamondSquareGenerator
    from terrainlib.filters.erosion import ThermalErosionFilter
    from terrainlib.readers.image import PILImageReader

    generator = DiamondSquareGenerator(10, 0.1)
    erosion = ThermalErosionFilter(150)
    img_reader = PILImageReader(PILImageReader.BITDEPTH_16)

    terrain = erosion(generator())
    img = img_reader(terrain)
    img.save('terrain_out.png')

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
