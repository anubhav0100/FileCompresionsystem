import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
from compressor import compress_file, decompress_file

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class TeraZipApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("TeraZip (AGC Compressor)")
        self.geometry("500x350")
        
        self.input_path = ""
        self.output_path = ""
        
        self.grid_columnconfigure(1, weight=1)

        # UI Elements
        self.label_title = ctk.CTkLabel(self, text="TeraZip File Compressor", font=ctk.CTkFont(size=20, weight="bold"))
        self.label_title.grid(row=0, column=0, columnspan=3, padx=20, pady=(20, 10))

        # Input File Selection
        self.btn_select_input = ctk.CTkButton(self, text="Select Input File", command=self.select_input_file)
        self.btn_select_input.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        self.label_input = ctk.CTkLabel(self, text="No file selected", text_color="gray")
        self.label_input.grid(row=1, column=1, columnspan=2, padx=20, pady=10, sticky="w")

        # Output File Selection
        self.btn_select_output = ctk.CTkButton(self, text="Select Output File", command=self.select_output_file)
        self.btn_select_output.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        
        self.label_output = ctk.CTkLabel(self, text="No destination selected", text_color="gray")
        self.label_output.grid(row=2, column=1, columnspan=2, padx=20, pady=10, sticky="w")

        # Action Buttons
        self.btn_compress = ctk.CTkButton(self, text="Compress (.agc)", command=self.start_compress, fg_color="green", hover_color="darkgreen")
        self.btn_compress.grid(row=3, column=0, padx=20, pady=20)

        self.btn_decompress = ctk.CTkButton(self, text="Decompress", command=self.start_decompress)
        self.btn_decompress.grid(row=3, column=1, padx=20, pady=20, sticky="w")

        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.grid(row=4, column=0, columnspan=3, padx=20, pady=(10, 0), sticky="ew")
        self.progress_bar.set(0)
        
        self.label_status = ctk.CTkLabel(self, text="Idle", text_color="gray")
        self.label_status.grid(row=5, column=0, columnspan=3, padx=20, pady=(5, 20))
        
    def select_input_file(self):
        filename = filedialog.askopenfilename()
        if filename:
            self.input_path = filename
            self.label_input.configure(text=os.path.basename(filename), text_color="white")

    def select_output_file(self):
        filename = filedialog.asksaveasfilename()
        if filename:
            self.output_path = filename
            self.label_output.configure(text=os.path.basename(filename), text_color="white")

    def update_progress(self, val):
        # Update progress bar safely from a background thread
        self.after(0, self.progress_bar.set, val)

    def run_task(self, task_func, action_name):
        self.btn_compress.configure(state="disabled")
        self.btn_decompress.configure(state="disabled")
        self.progress_bar.set(0)
        self.label_status.configure(text=f"{action_name} in progress...")

        def thread_target():
            try:
                task_func(self.input_path, self.output_path, progress_callback=self.update_progress)
                self.after(0, self.label_status.configure, {"text": f"{action_name} complete!", "text_color": "green"})
                self.after(0, messagebox.showinfo, "Success", f"{action_name} completed successfully.")
            except Exception as e:
                self.after(0, self.label_status.configure, {"text": "Error occurred", "text_color": "red"})
                self.after(0, messagebox.showerror, "Error", str(e))
            finally:
                self.after(0, self.btn_compress.configure, {"state": "normal"})
                self.after(0, self.btn_decompress.configure, {"state": "normal"})

        threading.Thread(target=thread_target, daemon=True).start()

    def start_compress(self):
        if not self.input_path or not self.output_path:
            messagebox.showwarning("Warning", "Please select input and output files.")
            return
            
        if not self.output_path.endswith('.agc'):
            self.output_path += '.agc'
            self.label_output.configure(text=os.path.basename(self.output_path))
            
        self.run_task(compress_file, "Compression")

    def start_decompress(self):
        if not self.input_path or not self.output_path:
            messagebox.showwarning("Warning", "Please select input and output files.")
            return
            
        # For decompress, we can't easily track progress per chunk unless we update decompress_file
        # but for now we'll pass the callback, it just won't be used in the loop yet, or we can update it later.
        self.run_task(decompress_file, "Decompression")

if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    app = TeraZipApp()
    app.mainloop()
