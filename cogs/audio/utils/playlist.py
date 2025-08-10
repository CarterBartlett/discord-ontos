
class Playlist:
    def __init__(self):
        self.entries = []
        self.pointer = 0

    def add(self, data):
        self.entries.append(data)

    def step(self):
        if self.entries:
            song = self.entries[self.pointer]
            self.pointer += 1
            return song
        return None
    
    def get_current(self):
        if self.entries:
            return self.entries[self.pointer]
        return None

    def get_remaining(self):
        if (self.pointer + 1) > len(self.entries) - 1:
            return []
        return self.entries[self.pointer + 1:]

    def get_remaining_and_current(self):
        return self.entries[self.pointer:]

    def has_remaining(self):
        return self.pointer + 1 <= len(self.entries) - 1

    def has_remaining_or_current(self):
        return self.pointer <= len(self.entries) - 1

    def is_empty(self):
        return len(self.entries) == 0

    def at_end_of_playlist(self):
        return self.pointer >= len(self.entries) - 1

    def clear(self):
        self.entries.clear()

    def reset_pointer(self):
        self.pointer = 0