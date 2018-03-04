#!/usr/bin/python
#
# List of all Tests that can be done
#
# @author:Dominique Bongard, floyd
#
# Code is licensed under -- Apache License 2.0 http://www.apache.org/licenses/
#
# Class oriented, pythonic and additional fingerpint changes by floyd, @floyd_ch, https://www.floyd.ch

from xpng import Xpng

class Test:
    def __init__(self, name, filename, function, description):
        self.name = name
        self.filename = filename
        self.function = function
        self.description = description

class Tests:
    all_tests = [
Test("Checksums", "control", Xpng.correct_checksums, "Valid image, all libraries should be able to open it"),
Test("Compression", "control", Xpng.zlib_compression, "Test zlib compression level of output file"),
Test("filters RGB","control", Xpng.filters_used, "Check which filters have been used in the reencoding"),
Test("filters indexed","control_8bit", Xpng.filters_used, "Check which filters have been used in the reencoding"),
Test("control_8bit","control_8bit", Xpng.conversion_success, "Valid paletted image"),
Test("control_8bit_i","control_8bit_i", Xpng.conversion_success, "Valid paletted interlaced image"),
Test("control_grayscale","control_grayscale", Xpng.conversion_success, "Valid grayscale image"),
Test("control_rgba","control_rgba", Xpng.conversion_success, "Valid image with alpha"),
Test("CESA-2004-001","CESA-2004-001", Xpng.conversion_success, "Invalid file triggering CESA-2004-001"),
Test("two_plte_chunk","two_plte_chunk", Xpng.palette_used, "PNG file with two palettes, check which is used in result"),
Test("gamma_four_and_srgb","gamma_four_and_srgb", Xpng.gamma,"PNG file with very high gamma, check if output is saturated"),
Test("gamma_four_nosrgb","gamma_four_nosrgb", Xpng.gamma,"Test gamma of output image"),
Test("two_ihdr_chunk","two_ihdr_chunk", Xpng.ihdr_used, "PNG image with two header chunks, check which is used"),
Test("idat_bad_filter","idat_bad_filter", Xpng.bad_idat_filter, "Invalid scan line filter"),
Test("modified_phys","modified_phys", Xpng.phys_chunk, "Check if decoder took phys into account"),
Test("truecolor_trns_chunk","truecolor_trns_chunk", Xpng.truecolor_trns, ""),
Test("truecolor_alpha_trns_chunk","truecolor_alpha_trns_chunk", Xpng.truecolor_trns, "truecolor + alpha image should not have a trns chunk"),
Test("transparent_bkdred","transparent_bkdred", Xpng.truecolor_trns, ""),
Test("black_white","black_white", Xpng.conversion_success, "Valid black & white image"),
Test("chunk_with_number_in_name_before_idat","chunk_with_number_in_name_before_idat", Xpng.conversion_success, "Invalid chunk name"),
Test("CVE-2014-0333","CVE-2014-0333", Xpng.conversion_success, ""),
Test("first_idat_empty","first_idat_empty", Xpng.conversion_success, "valid file with first idat empty"),
Test("grayscale_with_plte","grayscale_with_plte", Xpng.conversion_success, "Grayscale images should not have a plte chunk"),
Test("idat_bad_zlib_checkbits","idat_bad_zlib_checkbits", Xpng.conversion_success, "invalid compressed data"),
Test("idat_bad_zlib_checksum","idat_bad_zlib_checksum", Xpng.conversion_success, "invalid compressed data"),
Test("idat_bad_zlib_method","idat_bad_zlib_method", Xpng.conversion_success, "invalid compressed data"),
Test("idat_empty_zlib_object","idat_empty_zlib_object", Xpng.conversion_success, "invalid compressed data"),
Test("idat_junk_after_lz","idat_junk_after_lz", Xpng.conversion_success, "Some junk appended to idat"),
Test("idat_too_much_data","idat_too_much_data", Xpng.conversion_success, "too many scanlines in the compressed data"),
Test("idat_zlib_invalid_window","idat_zlib_invalid_window", Xpng.conversion_success, "invalid compressed data"),
Test("iend_before_idat","iend_before_idat", Xpng.conversion_success, "iend must be last chunk"),
Test("ihdr_height_0","ihdr_height_0", Xpng.conversion_success, "invalid height"),
Test("ihdr_invalid_compression_method","ihdr_invalid_compression_method", Xpng.conversion_success, "invalid ihdr"),
Test("ihdr_invalid_filter_method","ihdr_invalid_filter_method", Xpng.conversion_success, "invalid ihdr"),
Test("ihdr_not_first_chunk","ihdr_not_first_chunk", Xpng.conversion_success, "ihdr is not the first chunk"),
Test("ihdr_too_long","ihdr_too_long", Xpng.conversion_success, "Invalid ihdr"),
Test("ihdr_too_short","ihdr_too_short", Xpng.conversion_success, "Invalid ihdr"),
Test("ihdr_width_0","ihdr_width_0", Xpng.conversion_success, "invalid width"),
Test("ihdr_widthheight0","ihdr_widthheight0", Xpng.conversion_success, "invalid width and height"),
Test("indexed_no_plte","indexed_no_plte", Xpng.conversion_success, "indexed png file missing the plte chunk"),
Test("invalid_iccp_1","invalid_iccp_1", Xpng.conversion_success, "invalid iccp chunk"),
Test("invalid_iccp_2","invalid_iccp_2", Xpng.conversion_success, "invalid iccp chunk"),
Test("invalid_length_iend","invalid_length_iend", Xpng.conversion_success, "the length of the iend chunk should be zero"),
Test("invalid_name_ancillary_private_chunk_before_idat","invalid_name_ancillary_private_chunk_before_idat", Xpng.conversion_success, "Invalid chunk name"),
Test("invalid_name_ancillary_public_chunk_before_idat_bad_checksum","invalid_name_ancillary_public_chunk_before_idat_bad_checksum", Xpng.conversion_success, "invalid chunk name and invalid checksum"),
Test("invalid_name_ancillary_public_chunk_before_idat","invalid_name_ancillary_public_chunk_before_idat", Xpng.conversion_success, "invalid chunk name"),
Test("invalid_name_reserved_bit_ancillary_public_chunk_before_idat","invalid_name_reserved_bit_ancillary_public_chunk_before_idat", Xpng.conversion_success, "invalid chunk name"),
Test("ios_cgbl_chunk","ios_cgbl_chunk", Xpng.conversion_success, "Apple png"),
Test("jng_file","jng_file", Xpng.conversion_success, "jng file"),
Test("junk_after_iend","junk_after_iend", Xpng.conversion_success, "junk at the end of the image"),
Test("mng_file","mng_file", Xpng.conversion_success, "mng file"),
Test("no_iend","no_iend", Xpng.conversion_success, "missing iend"),
Test("nonconsecutive_idat","nonconsecutive_idat", Xpng.conversion_success, "non consecutive idat, not legal"),
Test("plte_after_idat","plte_after_idat", Xpng.conversion_success, "plte after idat, it should be before"),
Test("png48","png48", Xpng.conversion_success, "48bit per pixel png"),
Test("png64","png64", Xpng.conversion_success, "64bit per pixel png"),
Test("transparent_truncated_palette","transparent_truncated_palette", Xpng.conversion_success, "transparent color is missing in palette"),
Test("truncated_chunk","truncated_chunk", Xpng.conversion_success, "truncated chunk at end of file"),
Test("unknown_critical_chunk_bad_checksum","unknown_critical_chunk_bad_checksum", Xpng.conversion_success, "chunk marked as critical, but not standard with bad checksum"),
Test("unknown_critical_chunk","unknown_critical_chunk", Xpng.conversion_success, "chunk marked as critical, but not standard"),

]