import subprocess


def test_runner(payload: str) -> None:
    subprocess.run(f"echo {payload}", shell=True, check=True)