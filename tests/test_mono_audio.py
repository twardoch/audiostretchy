from audiostretchy.core import AudioStretch, stretch_audio


def test_mono_audio_stretch(
    generate_test_files, audio_properties_checker, tolerance_checker
):
    """Test stretching mono audio files."""
    mono_file = generate_test_files["mono_wav"]

    # Test basic stretching
    processor = AudioStretch()
    processor.open(mono_file)

    # Verify it's mono
    assert processor.num_channels == 1
    original_frames = processor.samples.shape[1]

    # Stretch by 1.5x
    processor.stretch(ratio=1.5)

    # Check results
    assert processor.num_channels == 1
    current_frames = processor.samples.shape[1]
    expected_frames = int(original_frames * 1.5)

    assert tolerance_checker(current_frames, expected_frames, 5)


def test_stereo_audio_stretch(
    generate_test_files, audio_properties_checker, tolerance_checker
):
    """Test stretching stereo audio files."""
    stereo_file = generate_test_files["stereo_wav"]

    # Test basic stretching
    processor = AudioStretch()
    processor.open(stereo_file)

    # Verify it's stereo
    assert processor.num_channels == 2
    original_frames = processor.samples.shape[1]

    # Stretch by 0.8x (faster)
    processor.stretch(ratio=0.8)

    # Check results
    assert processor.num_channels == 2
    current_frames = processor.samples.shape[1]
    expected_frames = int(original_frames * 0.8)

    assert tolerance_checker(current_frames, expected_frames, 5)


def test_gapped_audio_stretch(
    generate_test_files, audio_properties_checker, tolerance_checker
):
    """Test stretching audio with silence gaps."""
    gapped_file = generate_test_files["gapped_wav"]

    processor = AudioStretch()
    processor.open(gapped_file)

    original_frames = processor.samples.shape[1]

    # Test with gap_ratio (though current implementation may not use it effectively)
    processor.stretch(ratio=1.2, gap_ratio=0.8)

    current_frames = processor.samples.shape[1]
    expected_frames = int(original_frames * 1.2)  # Based on main ratio

    assert tolerance_checker(current_frames, expected_frames, 5)


def test_mono_to_stereo_conversion(generate_test_files, tmp_path):
    """Test processing mono audio and ensuring output format is preserved."""
    mono_file = generate_test_files["mono_wav"]
    output_file = tmp_path / "mono_output.wav"

    # Use the convenience function
    stretch_audio(str(mono_file), str(output_file), ratio=1.1)

    # Verify output is still mono
    import soundfile as sf

    with sf.SoundFile(output_file, "r") as f:
        assert f.channels == 1
