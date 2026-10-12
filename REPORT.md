# Whisper STT Implementation Lab

## 1. Objective
Implement an automated speech-to-text system using OpenAI Whisper, including prompted and unprompted transcription, audio chunking, timestamp extraction, and multiple export formats.

## 2. Implementation
The project uses Python, the OpenAI API, pydub, and FFmpeg.

A synthetic 18-second meeting recording was generated using macOS text-to-speech. The recording discusses OpenAI, Python, API integration, and project deadlines.

The script performs:
- Unguided transcription without contextual information
- Guided transcription using a prompt containing relevant terminology
- Audio splitting into smaller chunks
- Timestamp adjustment to preserve the original recording timeline
- Export to TXT, JSON, and SRT formats

## 3. Results

### Guided vs. Unguided
Both methods produced identical transcriptions for the test recording.

This suggests that contextual prompting was unnecessary for this clear, short sample. Prompts may be more useful for recordings containing specialized terminology, unfamiliar names, or ambiguous speech.

### Audio Chunking
The recording was divided into four chunks using a six-second chunk size.

All four chunks were processed successfully. The script adjusts segment timestamps using each chunk's original starting position.

Chunking is particularly useful for longer recordings because it allows audio to be processed in smaller files and helps manage API file-size limits.

### Output Formats
- TXT: Human-readable transcript with timestamps
- JSON: Structured segments with start and end times
- SRT: Subtitle format suitable for video captions

## 4. Challenges
The main challenges involved Python environment compatibility, indentation errors, and converting chunk durations into integer milliseconds.

These issues were resolved using Python 3.11, a dedicated virtual environment, and corrected code.

## 5. Recommendations
For better transcription accuracy:
- Use clear recordings with minimal background noise.
- Provide relevant vocabulary through contextual prompts.
- Use chunking for recordings exceeding API file-size limits.
- Review transcript boundaries when audio is split into short chunks.
- Validate technical terms and proper names manually.

## 6. Conclusion
The implementation successfully demonstrates automated transcription, contextual prompting, audio chunking, timestamp handling, and export functionality.

The test used synthetic speech


