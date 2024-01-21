import os

folder_path = 'Baza_final'

if os.path.isdir(folder_path):
    files = os.listdir(folder_path)

    png_files = [file for file in files if file.lower().endswith('.png')]
    
    for idx, file_name in enumerate(png_files):
        new_name = str(idx + 1) + '.png'
        current_path = os.path.join(folder_path, file_name)
        new_path = os.path.join(folder_path, new_name)
        os.rename(current_path, new_path)
    
    print("Zmieniono nazwy plików PNG.")
else:
    print("Podana ścieżka nie istnieje lub nie jest folderem.")
