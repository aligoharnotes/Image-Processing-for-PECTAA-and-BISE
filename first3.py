import os
import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, ttk
from rembg import remove, new_session
from PIL import Image, ImageTk

session = new_session("u2netp")

SIZES = {
    "Passport Size": (413, 531),
    "1x1 Inch": (300, 300)
}

root = tk.Tk()
root.title("PICTURE PROCESSING FOR PECTAA AND BISE")
root.geometry("820x720")

def set_background():
    try:
        path = os.path.join(os.path.expanduser("~"), "Desktop", "bg.jpg")
        img = Image.open(path)
        img = img.resize((820, 720))
        bg = ImageTk.PhotoImage(img)

        label = tk.Label(root, image=bg)
        label.image = bg
        label.place(x=0, y=0, relwidth=1, relheight=1)
    except:
        root.configure(bg="white")

set_background()

input_folder = tk.StringVar()
output_folder = tk.StringVar()
size_option = tk.StringVar(value="Passport Size")
bg_option = tk.StringVar(value="white")
kb_option = tk.StringVar(value="20 KB")

# ===================== ⭐ PROGRESS BAR ADDED =====================
progress = tk.DoubleVar()

progress_bar = ttk.Progressbar(
    root,
    variable=progress,
    maximum=100
)
progress_bar.pack(fill="x", padx=20, pady=10)

header = tk.Label(
    root,
    text="✨ WELCOME BY ALI GOHAR ✨\nGHS AOC MORGAH RAWALPINDI",
    font=("Helvetica", 16, "bold"),
    fg="white",
    bg="#34495E",
    padx=20,
    pady=10
)
header.pack(pady=12)

done_label = tk.Label(
    root,
    text="",
    font=("Arial", 16, "bold"),
    fg="green",
    bg="white"
)
done_label.pack(pady=10)

def select_input():
    input_folder.set(filedialog.askdirectory())

def select_output():
    output_folder.set(filedialog.askdirectory())

def apply_background(img, color):

    if img.shape[2] != 4:
        return img

    b, g, r, a = cv2.split(img)
    alpha = a / 255.0
    rgb = cv2.merge([b, g, r])

    if color == "white":
        bg = (255, 255, 255)
    elif color == "blue":
        bg = (255, 0, 0)
    elif color == "red":
        bg = (0, 0, 255)
    else:
        bg = (255, 255, 255)

    background = np.full(rgb.shape, bg, dtype=np.uint8)

    for c in range(3):
        background[:, :, c] = alpha * rgb[:, :, c] + (1 - alpha) * background[:, :, c]

    return background.astype(np.uint8)

def save_with_kb(img, path, target_kb):

    target_bytes = target_kb * 1024

    for q in range(95, 20, -5):
        _, encimg = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), q])
        if len(encimg) <= target_bytes:
            with open(path, "wb") as f:
                f.write(encimg)
            return

    cv2.imwrite(path, img)

def process_images():

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    inp_folder = input_folder.get()
    out_folder = output_folder.get()

    size = SIZES[size_option.get()]
    target_kb = int(kb_option.get().split()[0])
    bg_choice = bg_option.get()

    files = [f for f in os.listdir(inp_folder) if f.lower().endswith((".jpg", ".png", ".jpeg"))]
    total = len(files)

    for i, file in enumerate(files):

        path = os.path.join(inp_folder, file)
        img = cv2.imread(path)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5)

        for (x, y, w, h) in faces:

            x = max(0, x - 80)
            y = max(0, y - 130)
            w = w + 160
            h = h + 260

            crop = img[y:y+h, x:x+w]

            resized = cv2.resize(crop, size)

            save_path = os.path.join(out_folder, file)

            if bg_choice == "No Change":
                final_img = resized
            else:
                temp_file = "temp.jpg"
                cv2.imwrite(temp_file, resized)

                inp = Image.open(temp_file)
                out = remove(inp, session=session)

                final_img = np.array(out)
                final_img = cv2.cvtColor(final_img, cv2.COLOR_RGBA2BGRA)

                final_img = apply_background(final_img, bg_choice)

            save_with_kb(final_img, save_path, target_kb)

        # ===================== ⭐ PROGRESS UPDATE =====================
        percent = ((i + 1) / total) * 100
        progress.set(percent)
        root.update_idletasks()

    done_label.config(text="✔ DONE - U R GOOD TO GO!")

# ===================== BUTTONS (UNCHANGED) =====================
btn_style = {
    "font": ("Arial", 12, "bold"),
    "width": 28,
    "pady": 8
}

tk.Button(root, text="📂 Select Input Folder",
          bg="#3498DB", fg="white",
          command=select_input, **btn_style).pack(pady=6)

tk.Label(root, textvariable=input_folder, bg="white").pack()

tk.Button(root, text="📁 Select Output Folder",
          bg="#1ABC9C", fg="white",
          command=select_output, **btn_style).pack(pady=6)

tk.Label(root, textvariable=output_folder, bg="white").pack()

tk.Label(root, text="Select Size", bg="white").pack()
ttk.Combobox(root, textvariable=size_option,
             values=["Passport Size", "1x1 Inch"]).pack()

tk.Label(root, text="Select Background", bg="white").pack()
ttk.Combobox(root, textvariable=bg_option,
             values=["white", "blue", "red", "No Change"]).pack()

tk.Label(root, text="Select File Size", bg="white").pack()
ttk.Combobox(root, textvariable=kb_option,
             values=["15 KB", "20 KB", "25 KB"]).pack()

tk.Button(root, text="🚀 START PROCESSING",
          bg="#2ECC71", fg="white",
          font=("Arial", 14, "bold"),
          command=process_images).pack(pady=18)

tk.Label(
    root,
    text="SELECT THE FOLDER CONTAING SOURCE IMAGES YOU WANT TO CHANGE\nSELECT THE DESTINATION FOLDER WHERE YOU WANT TO PUT YR FINAL PROCESSED IMAGES\nPRESS START PROCESSING\n\nWARNING: THIS SOFTWARE IS FREE AND NOT FOR ANY COMMERCIAL USE.\nTHE DEVELOPER HAS NO FINANCIAL MOTIVES.\naligoharnotes@gmail.com\n\n\n",
    bg="white",
    fg="red"
).pack(side="bottom", pady=10)

root.mainloop()
