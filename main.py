from dotenv import load_dotenv
from splitter import Splitter
from pathlib import Path
from openai import OpenAI
import tiktoken
import logging
import os

# Load the .env.local file
load_dotenv(dotenv_path=Path(__file__).parent / ".env.local")

if not os.getenv("OPENAI_API_KEY"):
  raise ValueError("API key is missing.  Check your .env.local file")

# Initialize a tokenizer to count input tokens
tokenizer = tiktoken.get_encoding('cl100k_base')
MAX_TOKENS = 4096

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup OpenAI client
openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# speech_file_path = Path(__file__).parent / "audio_files" / "speech.mp3"
# speech_file_path.parent.mkdir(parents=True, exist_ok=True)


def split_text_into_chunks(text, max_tokens=MAX_TOKENS):
  '''Split input text into token safe chunks '''
  tokens = tokenizer.encode(text) # calculate the total tokens of the input text
  chunks = []
  start = 0

  while start < len(tokens):
    end = start + max_tokens # 4096 for tts-1-hd 
    chunk_tokens = tokens[start:end] # slice the tokens from 0 to max_tokens
    chunk_text = tokenizer.decode(chunk_tokens) # converts tokens back to text
    chunks.append(chunk_text) # append chunk to 
    start = end
  
  return chunks

#NOTE: pass whole document to "convert" function and call splitting functions inside?
#NOTE: pass split chapters to "convert" function and call 

#-------------------------------------------------------------------------------------
def convert_text_chunks_to_audio(text_chunks):
  "NOTE: add tokenizer to chunk text in tokens <=4096"
  text = " ".join(text.split(" ")[:600])
  '''
  voice options:
  alloy, echo, fable, onyx, nova, shimmer
  '''
  try:
    response =  openai.audio.speech.create(
        model="tts-1-hd",
        voice="onyx",
        input=text,
    )
    response.stream_to_file(speech_file_path)

    # with open(speech_file_path, "wb") as f:
    #   for chunk in response.iter_content():
    #     f.write(chunk)
    # print(f"Audio file saved to {speech_file_path}")
  except Exception as e:
    print(f"Error creating audiobook: {e}")

# -------------------------------------------------------------------------------------
def process_books():
  splitter = Splitter()
  root_path = Path(__file__).parent
  path_to_docs = root_path / "books"
  path_to_audio_files = root_path / "audio_files"

  # check if paths exist and if not create them
  path_to_docs.mkdir(exist_ok=True)
  path_to_audio_files.mkdir(exist_ok=True)

  books = []
  # Check all files in "books" folder and if a file then add to the array to be processed
  book_paths= list(path_to_docs.glob('*.txt'))

  for book_path in book_paths:
    book_title = book_path.stem
    logger.info(f"Loading book: {book_title}")

    file_contents = book_path.read_text()
    if not file_contents.strip():
      logger.warning(f"Skipping empty file: {book_title}")
      continue
    
    # append a book object to the books array
    books.append({
      "title": book_title,
      "path": book_path,
      "contents": file_contents,
      "is_processed": false,
      "audio_files":[]
    })

  # Process each book

  for book in books:
    book_title = book["title"]
    logger.info(f"Processing book: {book_title}")

    # Split the book into chapters
    chapters = splitter.split_chapters(book['contents'])
    chapter_audio_files = []

    for idx, chapter in enumerate(chapters):
      logger.info(f"Processing Chapter {idx} of {book_title}")

      chunks = split_text_into_chunks(chapter)
      chunk_audio_files = []

      for chunk_idx, chunk in enumerate(chunks):
        # send each chunk for conversion to audio file
        audio_file_path = (path_to_audio_files / book_title / f"chapter_{idx}_chunk_{chunk_idx}.mp3")
        audio_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Call OPENAI TTS Model and save the resulting audio file
        logger.info(f"Generating audio for {audio_file_path}")
        with audio_file_path.open("wb") as audio_file:
          audio_file.write(b"simulated audio content")  # NOTE: Replace with real audio content
        
        chunk_audio_files.append(str(audio_file_path))
      
      # Track audio files for this chapter
      chapter_audio_files.append(chunk_audio_files)

    # Mark the book as processed and save the audio file paths:
    book["is_processed"] = True
    book["audio_files"] = chapter_audio_files
    logger.info(f"Completed processing book: {book_title}")
  
  logger.info("All books processed.")
  for book in books:
    logger.info(f"Book: {book['title']}, Processed: {book['is_processed']}, Audio Files: {book['audio_files']}")




def main():
  pass

    # text = chapters[9]
    # tokens = tokenizer.encode(text)
    # print(len(tokens))


  # Test tokenizer for model 'tts-1-hd'

  


  # with open("books/frankenstein.txt") as f:
  #   file_contents = f.read()
  #   # print(file_contents)



  # splitter.split_chapters(path_to_docs)



main()

if __name__ == "__main__":
  process_books()