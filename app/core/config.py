import string 


special_char=[ch for ch in string.punctuation]

def contains_special_character(text:str):
  for c in text:
    if c in special_char:
      return True
  else:
    return False

def contains_number(text:str):
  for c in text:
    if c.isdigit():
      return True
  else:
    return False
   
    
  
