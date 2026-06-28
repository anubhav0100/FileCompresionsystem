import argparse
import sys
import time
import os
from compressor import compress_file, compress_directory, decompress_archive

def main():
    parser = argparse.ArgumentParser(description="High-Ratio File & Directory Compression System (AGC)")
    subparsers = parser.add_subparsers(dest="command", help="Command to run (compress or decompress)")
    
    compress_parser = subparsers.add_parser("compress", help="Compress a file or directory")
    compress_parser.add_argument("input", help="Path to the input file or directory")
    compress_parser.add_argument("output", help="Path to the output .agc file")
    
    decompress_parser = subparsers.add_parser("decompress", help="Decompress an .agc file")
    decompress_parser.add_argument("input", help="Path to the input .agc file")
    decompress_parser.add_argument("output", help="Path to the output file or directory")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
        
    start_time = time.time()
    
    if args.command == "compress":
        print(f"Compressing {args.input} to {args.output}...")
        if os.path.isdir(args.input):
            compress_directory(args.input, args.output)
        else:
            compress_file(args.input, args.output)
        print("Compression complete.")
    elif args.command == "decompress":
        print(f"Decompressing {args.input} to {args.output}...")
        decompress_archive(args.input, args.output)
        print("Decompression complete.")
        
    elapsed = time.time() - start_time
    print(f"Time taken: {elapsed:.2f} seconds")

if __name__ == "__main__":
    main()
