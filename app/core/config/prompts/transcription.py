TRANSCRIPTION_PROMPT: str = """
    Transcribe the audio word by word, emitting each word as soon as it is recognized.
    Do not cut words. Treat numbers carefully: recognize digits zero to nine, as well as numbers like ten, eleven, twelve, twenty, thirty, forty, ninety.
    The user will pronounce digits as follows:\n
    zero -> 'zero', one -> 'one', two -> 'two', three -> 'three', four -> 'four', five -> 'five', six -> 'six', seven -> 'seven', eight -> 'eight', nine -> 'nine'.
    Pay attention to mispronunciations and minor variations, and do not interrupt the user until the full number sequence is complete."""
