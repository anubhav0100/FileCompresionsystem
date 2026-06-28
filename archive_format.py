import struct
import os

MAGIC = b'AGC\x01'

class ArchiveFormat:
    @staticmethod
    def write_header(file_obj):
        file_obj.write(MAGIC)
    
    @staticmethod
    def write_footer(file_obj, chunk_map):
        """
        Writes the chunk map at the end of the file so we can compress streaming chunks.
        chunk_map is a list of tuples: (compressed_size, original_size)
        """
        map_offset = file_obj.tell()
        
        # Write number of chunks (8 bytes)
        file_obj.write(struct.pack('<Q', len(chunk_map)))
        
        for comp_size, orig_size in chunk_map:
            file_obj.write(struct.pack('<QQ', comp_size, orig_size))
            
        # Write the offset of the map (8 bytes)
        file_obj.write(struct.pack('<Q', map_offset))
        
        # Write magic again to verify it's a complete file
        file_obj.write(MAGIC)
        
    @staticmethod
    def read_footer(file_obj):
        """
        Reads the footer to extract the chunk map.
        Returns a list of tuples: (compressed_size, original_size)
        """
        file_obj.seek(-12, os.SEEK_END)
        map_offset_bytes = file_obj.read(8)
        magic_bytes = file_obj.read(4)
        
        if magic_bytes != MAGIC:
            raise ValueError("Invalid archive format or incomplete file (magic missing at end).")
            
        map_offset = struct.unpack('<Q', map_offset_bytes)[0]
        
        file_obj.seek(map_offset)
        num_chunks = struct.unpack('<Q', file_obj.read(8))[0]
        
        chunk_map = []
        for _ in range(num_chunks):
            comp_size, orig_size = struct.unpack('<QQ', file_obj.read(16))
            chunk_map.append((comp_size, orig_size))
            
        return chunk_map
