import time
from watchdog.events import FileSystemEventHandler

class FileMonitor(FileSystemEventHandler):
    def on_modified(self, event):
        print(f'File {event.src_path} has been modified')

    def on_moved(self, event):
        print(f'File moved from {event.src_path} to {event.dest_path}')
        update_document(event.src_path,{'file_path':event.dest_path})
        
    def on_deleted(self, event):
        print(f'File {event.src_path} has been deleted')
        # Update MongoDB to set deleted tag to True
        update_document(event.src_path,{'deleted':True})

if __name__ == "__main__":
    event_handler = FileMonitor()
    observer = Observer()
    observer.schedule(event_handler, path='/root/gpt_projects/ABoringKnowledgeManagementSystem/DocumentBank', recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()