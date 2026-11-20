import time

print("Starting the Memory Hog... (Press Ctrl+C to stop!)")
hog_list = []

try:
    while True:
        # This adds roughly 50MB of blank text to RAM every second
        hog_list.append(' ' * 50_000_000)
        print(f"Consuming RAM... Chunks loaded: {len(hog_list)}")
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\nMemory Hog killed. RAM released.")