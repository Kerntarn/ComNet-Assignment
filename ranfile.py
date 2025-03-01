import random
import string

# Define the target size in bytes
size_in_bytes = 1024 * 1024  # 1,048,576 bytes = 1 MiB

# Use only ASCII characters to ensure each character is one byte in UTF-8.
chars = string.ascii_letters + string.digits + string.punctuation + " "

# Generate a random string of exactly 'size_in_bytes' characters.
random_text = ''.join(random.choices(chars, k=size_in_bytes))

# Write the random text to a file.
filename = "cute.txt"
with open(filename, "w", encoding="utf-8") as f:
    f.write(random_text)

print(f"Created {filename} with size approximately 1 MiB.")
