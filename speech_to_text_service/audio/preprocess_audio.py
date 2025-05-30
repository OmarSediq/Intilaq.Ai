# import noisereduce as nr
# import librosa
# import soundfile as sf
# import ffmpeg
# import os
# import asyncio
#
# async def convert_to_wav(input_path: str) -> str:
#     """
#     Converts audio file to WAV format asynchronously using ffmpeg.
#     """
#     base, _ = os.path.splitext(input_path)
#     output_path = base + ".converted.wav"
#
#     def _convert():
#         try:
#             ffmpeg.input(input_path).output(
#                 output_path,
#                 format='wav',
#                 acodec='pcm_s16le',
#                 ac=1,
#                 ar='16000'
#             ).run(overwrite_output=True, quiet=True)
#             return output_path
#         except ffmpeg.Error as e:
#             raise RuntimeError(f"Error converting audio with ffmpeg: {e.stderr.decode()}")
#
#     return await asyncio.to_thread(_convert)
#
# async def clean_audio(input_path: str) -> str:
#     """
#     Applies noise reduction on a WAV file asynchronously.
#     """
#     def _clean():
#         try:
#             y, sr = librosa.load(input_path, sr=None)
#             reduced = nr.reduce_noise(y=y, sr=sr)
#             cleaned_path = input_path.replace(".wav", "_cleaned.wav")
#             sf.write(cleaned_path, reduced, sr)
#             return cleaned_path
#         except Exception as e:
#             raise RuntimeError(f"Error cleaning audio: {str(e)}")
#
#     return await asyncio.to_thread(_clean)
