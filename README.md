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

Adding new fingerprints
=======================

Adding new fingeprints to fingerping's database is quite trivial. Simply generate the image folder for the library as you would when fingerprinting a web application. Then run fingerping with the "-gen" option. fingerping will then ouput the library's fingerprint as a Python dictionary.

```bash
$ python fingerping.py -gen ../newPNG/
{'black_white': 4, 'control_8bit_i': 4, 'Compression': 13, 'ihdr_too_long': 0, 'ihdr_height_0': 0, 'invalid_name_reserved_bit_ancillary_public_chunk_before_idat': 10, 'idat_bad_zlib_method': 0, 'truecolor_trns_chunk': 13, 'gamma_four_and_srgb': 12, 'truecolor_alpha_trns_chunk': 12, 'invalid_length_iend': 10, 'nonconsecutive_idat': 0, 'filters RGB': [1, 2, 4], 'ihdr_width_0': 0, 'unknown_critical_chunk_bad_checksum': 0, 'two_plte_chunk': 0, 'idat_bad_filter': 11, 'CESA-2004-001': 0, 'ihdr_widthheight0': 0, 'no_iend': 0, 'jng_file': 0, 'control_8bit': 10, 'transparent_truncated_palette': 10, 'filters indexed': [0], 'transparent_bkdred': 13, 'two_ihdr_chunk': 0, 'idat_too_much_data': 10, 'invalid_name_ancillary_public_chunk_before_idat': 0, 'idat_empty_zlib_object': 0, 'truncated_chunk': 0, 'png64': 10, 'idat_junk_after_lz': 0, 'invalid_iccp_2': 10, 'ihdr_not_first_chunk': 0, 'control_rgba': 10, 'chunk_with_number_in_name_before_idat': 0, 'first_idat_empty': 10, 'invalid_name_ancillary_public_chunk_before_idat_bad_checksum': 0, 'png48': 10, 'unknown_critical_chunk': 0, 'iend_before_idat': 0, 'invalid_iccp_1': 10, 'idat_bad_zlib_checksum': 0, 'modified_phys': 11, 'invalid_name_ancillary_private_chunk_before_idat': 0, 'mng_file': 0, 'grayscale_with_plte': 10, 'ihdr_too_short': 0, 'gamma_four_nosrgb': 12, 'junk_after_iend': 10, 'indexed_no_plte': 0, 'plte_after_idat': 0, 'ihdr_invalid_compression_method': 0, 'idat_bad_zlib_checkbits': 0, 'CVE-2014-0333': 4, 'ios_cgbl_chunk': 0, 'Checksums': 11, 'control_grayscale': 10, 'idat_zlib_invalid_window': 0, 'ihdr_invalid_filter_method': 0}
``` 

Then simply add a variable for the library to the fingerprints.py file, like below, replacing {fingerprint} with the aformentioned dictionary. Python reflection does the rest.

```bash
newPNG = Fingerprint("newPNG","newPNG v1.0 64bit",{fingerprint})
```







