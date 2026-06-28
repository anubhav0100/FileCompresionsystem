import os
import zstandard as zstd
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
from archive_format import ArchiveFormat

CHUNK_SIZE = 64 * 1024 * 1024  # 64 MB

def compress_chunk(data):
    # Using level 22 for maximum compression ratio, similar to LZMA
    # Note: Requires a lot of memory for very large chunks, 64MB is safe.
    cctx = zstd.ZstdCompressor(level=22, threads=1)
    return cctx.compress(data)

def decompress_chunk(data):
    dctx = zstd.ZstdDecompressor()
    return dctx.decompress(data)

def compress_file(input_path, output_path, progress_callback=None):
    file_size = os.path.getsize(input_path)
    total_chunks = (file_size + CHUNK_SIZE - 1) // CHUNK_SIZE
    
    chunk_map = []
    
    with open(input_path, 'rb') as f_in, open(output_path, 'wb') as f_out:
        ArchiveFormat.write_header(f_out)
        
        def chunk_generator():
            while True:
                data = f_in.read(CHUNK_SIZE)
                if not data:
                    break
                yield data
                
        with ProcessPoolExecutor() as executor:
            results = executor.map(compress_chunk, chunk_generator())
            
            for i, comp_data in enumerate(tqdm(results, total=total_chunks, desc="Compressing")):
                comp_size = len(comp_data)
                f_out.write(comp_data)
                chunk_map.append((comp_size, 0))
                
                if progress_callback:
                    # Send progress from 0.0 to 1.0
                    progress_callback((i + 1) / total_chunks)

        ArchiveFormat.write_footer(f_out, chunk_map)

def decompress_file(input_path, output_path):
    with open(input_path, 'rb') as f_in:
        # Read magic
        magic = f_in.read(4)
        if magic != b'AGC\x01':
            raise ValueError("Not an AGC archive.")
            
        chunk_map = ArchiveFormat.read_footer(f_in)
        
        f_in.seek(4) # start after magic
        
        def chunk_generator():
            for comp_size, _ in chunk_map:
                yield f_in.read(comp_size)
                
        total_chunks = len(chunk_map)
        
        with open(output_path, 'wb') as f_out:
            with ProcessPoolExecutor() as executor:
                results = executor.map(decompress_chunk, chunk_generator())
                
                for orig_data in tqdm(results, total=total_chunks, desc="Decompressing"):
                    f_out.write(orig_data)
