import tkinter as tk
from tkinter import messagebox, Listbox, Scrollbar, ttk
from PIL import Image, ImageTk
import mysql.connector
import pygame
import os

global current_song_index, songs
current_song_index = 0

# Function to connect to the MySQL database
def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="password",
            database="songs"
        )
        return connection
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Failed to connect to the database: {err}")
        return None

# Function to retrieve songs from the database
def retrieve_songs():
    try:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT title, artist, album, file_path, pic_path FROM songs")
            songs = cursor.fetchall()
            return songs
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Failed to retrieve songs: {err}")
    finally:
        if connection:
            connection.close()

# Function to play the selected song
def play_song(song_index):
    global current_song_index, songs
    current_song_index = song_index
    current_song = songs[current_song_index]
    pygame.mixer.music.load(current_song[3])
    pygame.mixer.music.play()
    update_song_info(current_song)
    update_album_art(current_song[4])
    # Bind the event handler for song completion
    pygame.mixer.music.set_endevent(pygame.USEREVENT)

# Function to handle song completion event
def on_song_end(event):
    # Add your desired action here, such as displaying a message
    messagebox.showinfo("Song Finished", "The song has finished playing.")

# Function to pause the currently playing song
def pause_song():
    pygame.mixer.music.pause()

# Function to resume the paused song
def resume_song():
    pygame.mixer.music.unpause()

# Function to go to the previous song
def previous_song():
    global current_song_index, songs
    current_song_index = (current_song_index - 1) % len(songs)
    play_song(current_song_index)

# Function to go to the next song
def next_song():
    global current_song_index, songs
    current_song_index = (current_song_index + 1) % len(songs)
    play_song(current_song_index)

# Function to update the song information label
def update_song_info(song):
    song_info_label.config(text=f"{song[0]} - {song[1]} - {song[2]}")

# Function to update the album art
def update_album_art(pic_path):
    image = Image.open(pic_path)
    image = image.resize((300, 300), Image.LANCZOS)
    photo = ImageTk.PhotoImage(image)
    album_art_label.config(image=photo)
    album_art_label.image = photo

# Function to show/hide the song list
def toggle_song_list(event=None):
    global song_list_visible
    if song_list_visible:
        song_list_frame.pack_forget()
        song_list_visible = False
    else:
        populate_song_list()
        song_list_frame.pack(side=tk.TOP, padx=10, pady=10)
        song_list_visible = True

# Function to populate the song list
def populate_song_list():
    song_list.delete(0, tk.END)
    for song in songs:
        song_list.insert(tk.END, song[0])

# Function to play a song from the song list
def play_song_from_list(event):
    selection = song_list.curselection()
    if selection:
        index = selection[0]
        play_song(index)

# Function to close the song list when clicking outside the box
def close_song_list(event):
    if song_list_visible:
        toggle_song_list()

# Function to resize and save images
def resize_images(images):
    resized_images = []
    for img_path in images:
        img = Image.open(img_path)
        img = img.resize((50, 50), Image.LANCZOS)
        filename, ext = os.path.splitext(img_path)
        resized_path = f"{filename}_resized{ext}"
        img.save(resized_path)
        resized_images.append(resized_path)
    return resized_images

# Function to update the volume
def update_volume(val):
    volume = float(val) / 100  # Convert to a value between 0.0 and 1.0
    pygame.mixer.music.set_volume(volume)

# Initialize Pygame mixer
pygame.mixer.init()
pygame.init()

# Bind the song completion event
pygame.mixer.music.set_endevent(pygame.USEREVENT)
# Add the event handler for song completion
pygame.event.set_allowed(pygame.USEREVENT)
pygame.event.post(pygame.event.Event(pygame.USEREVENT))

# Create the GUI
root = tk.Tk()
root.title("Music Player")
root.geometry("600x700")

# Load custom button images
button_images = ["images/previous.png", "images/pause.png", "images/resume.png", "images/next.png"]
resized_button_images = resize_images(button_images)

# Create a frame for album art and song information
frame = tk.Frame(root, bd=2, relief=tk.GROOVE)
frame.place(relx=0.5, rely=0.3, anchor=tk.CENTER, width=400)

# Display album art
album_art_label = tk.Label(frame)
album_art_label.pack(pady=20)

# Display song information
song_info_label = tk.Label(frame, text="", font=("Helvetica", 12))
song_info_label.pack()

# Create control buttons with resized images
control_frame = tk.Frame(root)
control_frame.place(relx=0.5, rely=0.65, anchor=tk.CENTER)

previous_image = tk.PhotoImage(file=resized_button_images[0])
pause_image = tk.PhotoImage(file=resized_button_images[1])
resume_image = tk.PhotoImage(file=resized_button_images[2])
next_image = tk.PhotoImage(file=resized_button_images[3])

previous_button = tk.Button(control_frame, image=previous_image, command=previous_song)
previous_button.image = previous_image
previous_button.pack(side=tk.LEFT, padx=20)

pause_button = tk.Button(control_frame, image=pause_image, command=pause_song)
pause_button.image = pause_image
pause_button.pack(side=tk.LEFT, padx=20)

resume_button = tk.Button(control_frame, image=resume_image, command=resume_song)
resume_button.image = resume_image
resume_button.pack(side=tk.LEFT, padx=20)

next_button = tk.Button(control_frame, image=next_image, command=next_song)
next_button.image = next_image
next_button.pack(side=tk.LEFT, padx=20)

# Create button to toggle song list
toggle_button = tk.Button(root, text="Show Songs", font=("Helvetica", 12), command=toggle_song_list)
toggle_button.place(relx=0.25, rely=0.05, anchor=tk.CENTER)

# Create frame for song list
song_list_frame = tk.Frame(root)
song_list = Listbox(song_list_frame, width=50, height=10, font=("Helvetica", 12))
song_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar = Scrollbar(song_list_frame, orient=tk.VERTICAL)
scrollbar.config(command=song_list.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
song_list.config(yscrollcommand=scrollbar.set)
song_list.bind("<Double-Button-1>", play_song_from_list)
song_list_frame.pack_forget()
song_list_visible = False

# Create a canvas for the custom progress bar
progress_canvas = tk.Canvas(root, width=300, height=20, bg='white', bd=0, highlightthickness=0)
progress_canvas.place(relx=0.5, rely=0.585, anchor=tk.CENTER)

# Draw the background bar
progress_canvas.create_rectangle(5, 5, 305, 15, fill='gray', outline='')

# Function to update the progress bar
def update_progress_bar():
    global current_song_index, songs
    songs = retrieve_songs()
    abc = current_song_index
    # Get the current position of the playing song
    current_pos = pygame.mixer.music.get_pos() / 1000  # Convert milliseconds to seconds
    # Calculate the percentage of progress
    total_duration = pygame.mixer.Sound(songs[abc][3]).get_length()
    progress_percentage = (current_pos / total_duration) * 100
    # Calculate the width of the progress bar
    progress_width = 3 * progress_percentage
    # Update the progress bar
    progress_canvas.coords('progress', 5, 5, 5 + progress_width, 15)
    # Schedule the next update after 100 milliseconds
    root.after(100, update_progress_bar)

# Draw the progress bar indicator
progress_canvas.create_rectangle(5, 5, 15, 15, fill='black', outline='', tags='progress')

# Call the function to start updating the progress bar
update_progress_bar()

# Create a frame for the volume control
volume_frame = tk.Frame(root)
volume_frame.place(relx=0.5, rely=0.78, anchor=tk.CENTER)

# Create a volume control slider and label
volume_label = tk.Label(volume_frame, text="Volume", font=("Helvetica", 12))
volume_label.pack(side=tk.TOP)

volume_slider = tk.Scale(volume_frame, from_=0, to=100, orient=tk.HORIZONTAL, command=update_volume)
volume_slider.set(50)  # Set initial volume to 50%
volume_slider.pack(side=tk.TOP, padx=10)

# Retrieve songs from the database
songs = retrieve_songs()
if songs:
    current_song_index = 0
    # Play the first song
    play_song(current_song_index)
else:
    tk.Label(root, text="No songs found in the database.").pack()

# Bind events to close the song list when clicking outside the box
root.bind("<Button-1>", close_song_list)

root.mainloop()
