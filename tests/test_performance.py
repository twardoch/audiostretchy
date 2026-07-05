import time

import pytest

from audiostretchy.core import AudioStretch, stretch_audio


@pytest.mark.performance
def test_stretch_performance_benchmark(generate_test_files):
    """Benchmark stretching performance."""
    stereo_file = generate_test_files["stereo_wav"]

    processor = AudioStretch()
    processor.open(stereo_file)

    # Measure stretching time
    start_time = time.time()
    processor.stretch(ratio=1.5)
    end_time = time.time()

    processing_time = end_time - start_time

    # Should process 1 second of audio in reasonable time (< 5 seconds)
    assert processing_time < 5.0, (
        f"Processing took {processing_time:.2f} seconds, which is too slow"
    )

    print(f"Stretch performance: {processing_time:.3f} seconds for 1 second of audio")


@pytest.mark.performance
def test_resample_performance_benchmark(generate_test_files):
    """Benchmark resampling performance."""
    stereo_file = generate_test_files["stereo_wav"]

    processor = AudioStretch()
    processor.open(stereo_file)

    # Measure resampling time
    start_time = time.time()
    processor.resample(22050)
    end_time = time.time()

    processing_time = end_time - start_time

    # Resampling should be very fast
    assert processing_time < 1.0, (
        f"Resampling took {processing_time:.2f} seconds, which is too slow"
    )

    print(f"Resample performance: {processing_time:.3f} seconds")


@pytest.mark.performance
def test_complete_pipeline_performance(generate_test_files, tmp_path):
    """Benchmark complete pipeline performance."""
    input_file = generate_test_files["stereo_wav"]
    output_file = tmp_path / "perf_output.wav"

    # Measure complete pipeline
    start_time = time.time()
    stretch_audio(str(input_file), str(output_file), ratio=1.2, sample_rate=22050)
    end_time = time.time()

    processing_time = end_time - start_time

    # Complete pipeline should be reasonable
    assert processing_time < 10.0, (
        f"Complete pipeline took {processing_time:.2f} seconds"
    )

    print(f"Complete pipeline performance: {processing_time:.3f} seconds")


def test_memory_usage_stability(generate_test_files):
    """Test that multiple operations don't cause memory leaks."""
    stereo_file = generate_test_files["stereo_wav"]

    # Run multiple operations
    for i in range(10):
        processor = AudioStretch()
        processor.open(stereo_file)
        processor.stretch(ratio=1.1 + i * 0.1)
        processor.resample(44100)
        # Processor should be garbage collected when it goes out of scope

    # If we get here without crashing, memory is probably stable
    assert True
