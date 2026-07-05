import subprocess
import sys


def test_cli_help():
    """Test that the CLI shows help information."""
    result = subprocess.run(
        [sys.executable, "-m", "audiostretchy", "--help"],
        capture_output=True,
        text=True,
    )

    # Should exit with code 0 and show help with parameter info
    assert result.returncode == 0
    assert "ratio" in result.stdout.lower() or "ratio" in result.stderr.lower()


def test_cli_version():
    """Test that the CLI can show version information."""
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import audiostretchy; print(audiostretchy.__version__)",
        ],
        capture_output=True,
        text=True,
    )

    # Should exit with code 0 and show version
    assert result.returncode == 0
    assert result.stdout.strip()  # Version should be non-empty


def test_cli_stretch_audio(generate_test_files, tmp_path):
    """Test the CLI with actual audio files."""
    input_file = generate_test_files["stereo_wav"]
    output_file = tmp_path / "cli_output.wav"

    # Run CLI command
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "audiostretchy",
            str(input_file),
            str(output_file),
            "--ratio",
            "1.2",
        ],
        capture_output=True,
        text=True,
    )

    # Should succeed
    assert result.returncode == 0
    assert output_file.exists()

    # Verify output properties
    import soundfile as sf

    with sf.SoundFile(output_file, "r") as f:
        assert f.channels == 2  # Should preserve stereo
        assert f.samplerate == 44100  # Should preserve sample rate


def test_cli_with_all_parameters(generate_test_files, tmp_path):
    """Test CLI with various parameters."""
    input_file = generate_test_files["stereo_wav"]
    output_file = tmp_path / "cli_full_params.wav"

    # Run CLI with many parameters
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "audiostretchy",
            str(input_file),
            str(output_file),
            "--ratio",
            "1.3",
            "--upper_freq",
            "300",
            "--lower_freq",
            "60",
            "--fast_detection",
            "True",
            "--sample_rate",
            "22050",
        ],
        capture_output=True,
        text=True,
    )

    # Should succeed
    assert result.returncode == 0
    assert output_file.exists()

    # Verify resampling worked
    import soundfile as sf

    with sf.SoundFile(output_file, "r") as f:
        assert f.samplerate == 22050
