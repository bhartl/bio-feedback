""" Audio manipulation and file-handling routines """
import soundfile as sf
from os.path import abspath


def available_formats():
    """ check available audio subtypes

    :return: all available 'FLAC' subtypes """
    return sf.available_subtypes('FLAC')


def transform_format(wav_file, suffix='.wav', convert_suffix='-converted.wav'):
    """ convert wav_file to format 'PCM_24' or 'PCM_16'

    :param wav_file: Path to original wav-file (str).
    :param suffix: Suffix of wav file (str, defaults to '.wav').
    :param convert_suffix: Replace-suffix of converted wav-file (str, defaults to '-converted.wav').
    :return: Path to new wave file.
    """
    assert wav_file.endswith(suffix), f"wave file with suffix {suffix} required."

    # generate converted file name
    new_wav_file = wav_file.split(suffix)
    new_wav_file = suffix.join(new_wav_file[:-1]) + convert_suffix

    # generate converted wav
    data, sample_rate = sf.read(abspath(wav_file))
    subtype = 'PCM_24' if 'PCM_24' in sf.available_subtypes('FLAC') else 'PCM_16'
    sf.write(abspath(new_wav_file), data, sample_rate, subtype=subtype)

    return new_wav_file
