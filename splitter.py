

class Splitter:
  def __init__(self):
    self.document = None

  
  def split_chapters(self, document):
    self.document = document

    chapters = document.split("\n\n\n\n")
    chapters = ["\n"+chapter.strip()+"\n" for chapter in chapters]

    return chapters