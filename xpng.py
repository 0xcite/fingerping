#!/usr/bin/python
#
# xpng: a quick and dirty (and very buggy) PNG library
# 
# @author:Dominique Bongard
# 
#
# Code is licensed under -- Apache License 2.0 http://www.apache.org/licenses/
#


from collections import namedtuple
from struct import *
import zlib
import binascii
import itertools
import os.path

# Named tuple representing a PNG chunk - offset is the position in the file
Chunk = namedtuple("chunk", "size name content checksum offset")

class Png:

  # Reads a png image and tries to decode it
  # valid can take several values from 0 to 10 depending on how 'valid' the PNG file is
  # valid == 0 => the file doesn't exist or is empty
  # valid == 10 => the file is at least structurally correct
  def __init__(self, fileName):
    self.valid = 0

    image = self.readImage(fileName)  
    if  (image['ok']):
      if  not len(image['data']) == 0:
        self.valid = 1
      if  image['data'].startswith('\x89PNG') : 
        self.valid = 2
        try:
          self.chunks = self.parseChunks(image['data'])
          self.valid = 3
          self.properties()
          self.valid = 4
          try:
            self.unfilter()
            self.valid = 10
          except:
            pass
        except:
          pass
  # reads the image in memory from file       
  def readImage(self, fileName):
    if os.path.exists(fileName):
      with open(fileName, 'rb') as f:
        try:
          data = f.read()
          return {'ok':True,'data':data}
        except :
          return {'ok': False}
    return {'ok': False}

  # Gets binary data in input and returns a representation as a Chunk named tuple
  def parseChunk(self, data,offset):
    start = offset
    size,name = unpack_from("!I4s", data,start)
    start+=8
    content =  data[start:start+size]
    start += size
    checksum = unpack_from("!I", data,start)[0]
    return Chunk(size,name,content,checksum,offset)

  # Parses all the chunks in the PNG file until it reaches IEND
  def parseChunks(self,data):
    chunks = []
    offset = 8
    chunk = Chunk(0,"",0,0,0)
    while chunk.name != "IEND":
      chunk = self.parseChunk(data,offset)
      chunks.append(chunk)
      offset += chunk.size + 12
    return chunks

    # returns the crc32 of a chunk named tuple
  def chunkChecksum(self,name,content):
    return binascii.crc32(name+content)  & 0xffffffff

    # Returns True if the checksum of the passed Chunk is correct
  def verifyChecksum(self,chunk):
    return chunk.checksum == self.chunkChecksum(chunk.name,chunk.content)

  # Returns True is the checksum of all the chunks in the image are correct
  def verifyChecksums(self): 
    for chunk in self.chunks:
      if not self.verifyChecksum(chunk):
        return False
    return True 

  # returns a chunk which name corresponds to the name parameter.
  # A PNG file can have several chunks with the same name, so there is also an index parameter
  def getChunk(self,name, index = 0):
    currentIndex = 0
    for chunk in self.chunks :
      if chunk.name == name :
        if (currentIndex == index) :
          return chunk
        else :
          currentIndex += 1
    return None

  # returns the binary representation of a Chunk named tuple
  def generateChunkBlob(self, chunk):
    blob = pack("!L4s",chunk.size,chunk.name)
    blob += chunk.content
    blob += pack("!L",chunk.checksum)
    return blob

        # returns the binary representation of a Chunk named tuple given its name and index
  def getChunkBlob(self,name, index=0):
    chunk = self.getChunk(name,index)
    if chunk == None :
      return None	
    return self.generateChunkBlob(chunk)

  # Extracts the properties of the image from the ihdr chunk
  def properties(self):
    ihdr = self.getChunk('IHDR')
    self.width,self.height, self.colorDepth, self.colorType, self.compressionMethod, self.filterMethod, self.interlaceMethod = unpack("!IIBBBBB",ihdr.content)

  # returns the size in bytes of a pixel, which depends on image type and bit depth 
  def pixelSize(self):
    if self.colorType == 3 : 
      return 1
    else :
      size = [1,0,3,1,2,0,4]
      return (self.colorDepth / 8.0) * size[self.colorType]

  # concatenates all the IDAT chunks and then decompresses the resulting zlib blob
  # also extracts the zlib compression level   	
  def decompress(self):
    finished = False
    compressed = ""
    index = 0
    while not finished:
      chunk = self.getChunk('IDAT',index)
      if chunk == None :
        finished = True
      else :
        compressed += chunk.content
        index = index + 1
    self.zlevel = ord(compressed[1]) >> 6
    return bytearray(zlib.decompress(compressed))

  # paeth scanline compression filter
  def paeth(self,a,b,c):
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc :
      pr = a
    elif pb <= pc : 
      pr = b
    else :
      pr = c
    return pr

  # type 0 scanline compression filter
  def type0(self,a,b,c,x):
    return list(x)

  # type 1 scanline compression filter
  def type1(self,a,b,c,x):
    return map(lambda k: (k[0]+k[1]) % 256,zip(a,x))

  # type 2 scanline compression filter
  def type2(self,a,b,c,x):
    return map(lambda k: (k[0]+k[1]) %256,zip(b,x))

  # type 3 scanline compression filter
  def type3(self,a,b,c,x):
    return map(lambda k: (((k[0]+k[1])//2) +k[2])%256,zip(a,b,x))

  # type 4 scanline compression filter
  def type4(self,a,b,c,x):
    return map(lambda k: (self.paeth(k[0],k[1],k[2])+k[3])%256,zip(a,b,c,x))

  # Removes the PNG compression filter from a scanline
  # A byte representing the compressed filter type is prepended to each scanline
  # returns a list of pixels. Each pixel is a list of samples (e.g. [r,g,b])
  def unfilterLine(self,line, prior = None):
    type, data = line[0], line[1:]
    # keep a list of the filters used by the compressor for fingerprinting purposes
    self.filtersUsed.add(type)
    ps = int(max(1,self.pixelSize())) #pixel size for filtering purposes is always >= 1 byte
    unfiltered = []
    zeropixel = [0 for x in range(ps)]
    if prior == None:
      prior = [zeropixel  for x in range(len(data)//ps)]

    a = zeropixel
    c= zeropixel

    filters = [self.type0,self.type1,self.type2,self.type3,self.type4]
    filter = filters[type]

    # Unfilter each pixel
    for i in range(len(data)//ps) :
      x = list(data[i*ps:(i+1)*ps])
      b= prior[i]
      recon = filter(a,b,c,x)
      a = recon
      c = b
      unfiltered.append(recon)     	
    return unfiltered

  # Unfilters the whole image
  # The result self.pixels is a list of rows, containing a list of pixels containing a list of samples
  def unfilter(self):
    self.filtersUsed = set()
    pix= []
    prior = None
    ps = self.pixelSize()
    lineSize = int(round(ps * self.width)) + 1
    filtered = self.decompress()
    for y in range(self.height) :
      line = filtered[y*lineSize:(y+1)*(lineSize)]
      unfiltered = self.unfilterLine(line,prior)
      pix.append(unfiltered)
      prior = unfiltered
    self.pixels = pix

  # Returns a list of all the colors in an indexed image
  # It doesn't take into account if the color is actually used in the image
  def getPaletteColors(self):
    plte = self.getChunk("PLTE")
    plteBytes = bytearray(plte.content)
    colors = []
    for x in xrange(0,plte.size,3) :
      colors.append([plteBytes[x],plteBytes[x+1],plteBytes[x+2]])
    return colors

  # Returns the RGB value of a pixel in the image given its coordinates
  # if the image is indexed, the pixel color is looked up in the palette
  # alpha is discarded
  def getPixelRgb(self,x,y):
    if not self.colorDepth == 8:
      return None
    value = self.pixels[y][x]
    if self.colorType == 2 :
      return value
    elif self.colorType == 6 :
      return value[0:3]
    elif self.colorType == 3 :
      return self.getPaletteColors()[value[0]]

  # Check if the image contains a particular color	
  def hasColor(self,color):
    if not self.colorDepth == 8:
      return False
    if self.colorType == 2 :
      return color in itertools.chain(*self.pixels)
    elif self.colorType == 6 :
      return color in map(lambda x: [x[0],x[1],x[2]], itertools.chain(*self.pixels))
    elif self.colorType == 3 :
      return color in self.getPaletteColors()

  # Generate a chunk from name and data (for saving)		
  def generateChunk(self,name,data):
    return Chunk(len(data),name,data,self.chunkChecksum(name,data),0)

  # Generate the IDAT chunk from the pixels (for saving) 
  def generateIdat(self):
    data = ""
    for line in self.pixels :
      data+='\0'
      data += str(bytearray(itertools.chain(*line)))
    compressed = zlib.compress(data)
    idat = self.generateChunkBlob(self.generateChunk("IDAT",compressed))
    return idat

  # returns the binary representation of the image in PNG format
  def getBlob(self):
    blob = "\x89PNG\x0d\x0a\x1a\x0a"
    blob += self.getChunkBlob("IHDR")
    plte = self.getChunkBlob("PLTE")
    if not plte == None:
      blob += plte
    blob += self.generateIdat()
    blob += self.getChunkBlob("IEND")
    return blob

  # Save the image in PNG format (used to verify that the image decoding works correctly)
  def save(self,fileName):
    with open(fileName, 'wb') as f:
      f.write(self.getBlob())
