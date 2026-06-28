import os
import subprocess
import shutil

def run_test():
    # 1. Create a highly compressible dummy file (e.g. repeated zeros)
    dummy_file = "test_data.bin"
    comp_file = "test_data.agc"
    decomp_file = "test_data.decomp.bin"
    
    print("Generating dummy file (100 MB of zeros)...")
    with open(dummy_file, "wb") as f:
        # write 100 MB of zeros
        f.write(b'\x00' * (100 * 1024 * 1024))
        
    print("Running compression...")
    subprocess.run(["python", "main.py", "compress", dummy_file, comp_file], check=True)
    
    orig_size = os.path.getsize(dummy_file)
    comp_size = os.path.getsize(comp_file)
    print(f"Original size: {orig_size} bytes")
    print(f"Compressed size: {comp_size} bytes")
    print(f"Ratio: {orig_size / comp_size:.2f}:1")
    
    print("Running decompression...")
    subprocess.run(["python", "main.py", "decompress", comp_file, decomp_file], check=True)
    
    # Because decompress_archive works the same way for files if is_dir is false.
    decomp_size = os.path.getsize(decomp_file)
    print(f"Decompressed size: {decomp_size} bytes")
    
    if orig_size == decomp_size:
        print("Success! Decompressed file matches original size.")
        # Clean up
        os.remove(dummy_file)
        os.remove(comp_file)
        os.remove(decomp_file)
    else:
        print("Error: Decompressed size does not match!")

if __name__ == "__main__":
    run_test()
