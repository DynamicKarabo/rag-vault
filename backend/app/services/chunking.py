from typing import List

class RecursiveCharacterTextSplitter:
    def __init__(
        self, 
        chunk_size: int = 512, 
        chunk_overlap: int = 102,
        separators: List[str] = None
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", " ", ""]

    def split_text(self, text: str) -> List[str]:
        """
        Split the incoming text into chunks recursively based on separators.
        """
        final_chunks = []
        separator = self.separators[-1]
        
        # dynamic separator selection
        for sep in self.separators:
            if sep == "":
                separator = sep
                break
            if sep in text:
                separator = sep
                break
                
        # split
        if separator:
            splits = text.split(separator)
        else:
            splits = list(text) # split by character if no separator found/empty

        # merge splits into chunks
        good_splits = []
        current_chunk = []
        current_length = 0
        
        for s in splits:
            s_len = len(s)
            if current_length + s_len + (len(separator) if current_chunk else 0) > self.chunk_size:
                if current_chunk:
                    text_chunk = separator.join(current_chunk)
                    if text_chunk:
                        good_splits.append(text_chunk)
                    
                    # Handle overlap (simplified sliding window)
                    # For strict recursive splitting, we might want to recurse on the too-long split itself
                    # if it's a single split that is too long.
                    
                    # Reset
                    overlap_len = 0
                    new_chunk = []
                    # Backtrack to keep overlap?
                    # A proper greedy merger:
                    # We simply start a new chunk. implementing overlap in a simple custom splitter is tricky 
                    # without full logic.
                    # Let's try to keep some trailing splits if possible, or just reset clean for now 
                    # to match the complexity requested.
                    # Wait, user *specifically* asked for overlap.
                    
                    # Logic:
                    # Keep adding to current_chunk until full.
                    # When full, save it.
                    # Start new chunk with last N items from previous that fit within overlap?
                    # Or just simple overlap logic.
                    
                    # Let's use a standard "merge splits" approach.
                    while current_length > self.chunk_overlap and current_chunk:
                         removed = current_chunk.pop(0)
                         current_length -= len(removed) + len(separator)
                    
            current_chunk.append(s)
            current_length += s_len + (len(separator) if current_chunk else 0)
            
        if current_chunk:
            good_splits.append(separator.join(current_chunk))
            
        # Post-processing: If any chunk is still too large, we recurse on it with the next separator
        # This is the "Recursive" part
        recursive_chunks = []
        for chunk in good_splits:
            if len(chunk) > self.chunk_size:
                # Find next separator index
                try:
                    next_sep_index = self.separators.index(separator) + 1
                    if next_sep_index < len(self.separators):
                        sub_splitter = RecursiveCharacterTextSplitter(
                            chunk_size=self.chunk_size, 
                            chunk_overlap=self.chunk_overlap,
                            separators=self.separators[next_sep_index:]
                        )
                        recursive_chunks.extend(sub_splitter.split_text(chunk))
                    else:
                        # Cannot split further, just hard clip? or keep as is?
                        # Usually at character level (empty sep) it splits strictly.
                        recursive_chunks.append(chunk)
                except ValueError:
                     recursive_chunks.append(chunk)
            else:
                recursive_chunks.append(chunk)
                
        return recursive_chunks
