import os
import tarfile
import threading
import queue
import zstandard as zstd
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
from archive_format import ArchiveFormat

CHUNK_SIZE = 64 * 1024 * 1024  # 64 MB

class WriteStream:
    def __init__(self, q, chunk_size):
        self.q = q
        self.chunk_size = chunk_size
        self.buffer = bytearray()
        self.closed = False
        
    def write(self, b):
        self.buffer.extend(b)
        while len(self.buffer) >= self.chunk_size:
            self.q.put(bytes(self.buffer[:self.chunk_size]))
            self.buffer = self.buffer[self.chunk_size:]
            
    def flush(self):
        pass
        
    def close(self):
        if self.buffer:
            self.q.put(bytes(self.buffer))
            self.buffer = bytearray()
        self.q.put(None)
        self.closed = True

class ReadStream:
    def __init__(self, q):
        self.q = q
        self.buffer = bytearray()
        self.eof = False
        
    def read(self, size=-1):
        if size < 0:
            # Read all
            res = bytearray()
            res.extend(self.buffer)
            self.buffer.clear()
            while not self.eof:
                chunk = self.q.get()
                if chunk is None:
                    self.eof = True
                else:
                    res.extend(chunk)
            return bytes(res)
            
        while len(self.buffer) < size and not self.eof:
            chunk = self.q.get()
            if chunk is None:
                self.eof = True
            else:
                self.buffer.extend(chunk)
                
        res = self.buffer[:size]
        self.buffer = self.buffer[size:]
        return bytes(res)
        
    def close(self):
        pass

def compress_chunk(data):
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
            
            for i, comp_data in enumerate(tqdm(results, total=total_chunks, desc="Compressing File")):
                comp_size = len(comp_data)
                f_out.write(comp_data)
                chunk_map.append((comp_size, 0))
                
                if progress_callback:
                    progress_callback((i + 1) / total_chunks)

        ArchiveFormat.write_footer(f_out, chunk_map, is_dir=False)

def compress_directory(input_dir, output_path, progress_callback=None):
    q = queue.Queue(maxsize=10) # Bounded queue to prevent memory blowup
    
    def tar_worker():
        try:
            stream = WriteStream(q, CHUNK_SIZE)
            with tarfile.open(fileobj=stream, mode='w|') as tar:
                tar.add(input_dir, arcname=os.path.basename(input_dir))
            stream.close()
        except Exception as e:
            q.put(e)
            
    t = threading.Thread(target=tar_worker)
    t.start()
    
    chunk_map = []
    with open(output_path, 'wb') as f_out:
        ArchiveFormat.write_header(f_out)
        
        def chunk_generator():
            while True:
                item = q.get()
                if item is None:
                    break
                if isinstance(item, Exception):
                    raise item
                yield item
                
        with ProcessPoolExecutor() as executor:
            results = executor.map(compress_chunk, chunk_generator())
            
            # Since size is unknown for dir tar stream, we just update progress visually or fake it.
            for i, comp_data in enumerate(tqdm(results, desc="Compressing Dir")):
                comp_size = len(comp_data)
                f_out.write(comp_data)
                chunk_map.append((comp_size, 0))
                
                if progress_callback:
                    # Fake progress that resets (since we don't know total tar size upfront)
                    progress_callback((i % 100) / 100.0)

        ArchiveFormat.write_footer(f_out, chunk_map, is_dir=True)
    t.join()

def decompress_archive(input_path, output_path, progress_callback=None):
    with open(input_path, 'rb') as f_in:
        magic = f_in.read(4)
        if magic != b'AGC\x01':
            raise ValueError("Not an AGC archive.")
            
        chunk_map, is_dir = ArchiveFormat.read_footer(f_in)
        f_in.seek(4)
        
        def chunk_generator():
            for comp_size, _ in chunk_map:
                yield f_in.read(comp_size)
                
        total_chunks = len(chunk_map)
        
        if is_dir:
            # output_path is treated as output directory
            os.makedirs(output_path, exist_ok=True)
            q = queue.Queue(maxsize=10)
            
            def extract_worker():
                try:
                    stream = ReadStream(q)
                    with tarfile.open(fileobj=stream, mode='r|') as tar:
                        tar.extractall(path=output_path)
                except Exception as e:
                    print("Extract error:", e)
                    
            t = threading.Thread(target=extract_worker)
            t.start()
            
            with ProcessPoolExecutor() as executor:
                results = executor.map(decompress_chunk, chunk_generator())
                for i, orig_data in enumerate(tqdm(results, total=total_chunks, desc="Decompressing Dir")):
                    q.put(orig_data)
                    if progress_callback:
                        progress_callback((i + 1) / total_chunks)
            q.put(None)
            t.join()
        else:
            with open(output_path, 'wb') as f_out:
                with ProcessPoolExecutor() as executor:
                    results = executor.map(decompress_chunk, chunk_generator())
                    for i, orig_data in enumerate(tqdm(results, total=total_chunks, desc="Decompressing File")):
                        f_out.write(orig_data)
                        if progress_callback:
                            progress_callback((i + 1) / total_chunks)
