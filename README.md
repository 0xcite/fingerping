fingerping
==========

fingerping is a security tool to fingerprint the PNG libraries used by web applications.

Purpose
=======

fingerping helps you determine which framework and / or PNG image library a web application is using. This is a first step in order to assess potential vulnerabilities either in the web application itself, or in the underlying PNG library.

Requirements
============

fingerping runs on Python 2.x with only the built-in modules.

In order to fingerprint a web application, it must be possible to upload arbitrary PNG files. The web application must then at least decode the image and return a success / fail result. For better results, the web application should return a re-encoded version of the image.

Usage
=====

The first step is to upload all the PNG files from the "images" directory to the target website (you might want to script that). All the resulting images must then be downloaded in a folder (e.g. site.com). Each output image must have the same name as the corresponding input image. Nothing needs to be done for images that the web application failed to decode. If some or all the output files are JPG files instead of PNG files, convert them first to PNG files (This will break some of the tests. A future version of the tool should account for this case).

Next, run fingerping using the folder with all the output images as argument:

```bash
$ python fingerping.py ../site.com/
```

fingerping will then output a count of fingerprint matches between the image folder and each library in its database. The line at the bottom is the most likely match.

```bash
$ python fingerping.py ../site.com/
Dart                  30/ 60
Ruby chunky_png       32/ 60
.Net 4.5              33/ 60
Erlang erl_img        34/ 60
Nodejs pngjs          34/ 60
Haskell JuicyPixels   38/ 60
Python PIL            38/ 60
Python png.py         39/ 60
OpenJDK 7             40/ 60
Go 1.0.2              41/ 60
LodePNG               42/ 60
ImageMagick           49/ 60
Mono                  50/ 60
PHP5                  60/ 60
```

From this, we can deduce that site.com is most likely a PHP site.

Note: Many sites preview or decode the images in the browser itself. The most likely result will be an incorrect fingerprint.
