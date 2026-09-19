"""Read-only course environment discovery; no installs, downloads, or GPU workloads."""
import argparse
import csv
import importlib.metadata
import importlib.util
import io
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone


def command(argv, timeout=15):
    try:
        result = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
        return {
            "command": argv,
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip()[:1500],
        }
    except (OSError, subprocess.TimeoutExpired) as error:
        return {"command": argv, "returncode": None, "error": str(error)}


def package_info(name):
    try:
        version = importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        version = None
    return {"distribution_version": version, "import_discoverable": importlib.util.find_spec(name) is not None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, help="New JSON file; existing files are never overwritten.")
    parser.add_argument("--check-torch", action="store_true", help="Import PyTorch in a child process and query CUDA. Does not run a tensor workload.")
    args = parser.parse_args()
    if not args.project.is_dir():
        parser.error(f"Project directory does not exist: {args.project}")

    report = {
        "schema_version": 1,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Current local process and interpreter only; discovery is not a training or serving benchmark.",
        "project": str(args.project.resolve()),
        "platform": {"system": platform.system(), "release": platform.release(), "machine": platform.machine()},
        "python": {"executable": sys.executable, "version": platform.python_version()},
        "cpu_logical_count": os.cpu_count(),
        "packages": {name: package_info(name) for name in ("torch", "numpy", "markdown_it", "vllm", "sglang")},
        "torch_cuda": {"status": "not_requested"},
    }
    meminfo = Path("/proc/meminfo")
    if meminfo.exists():
        wanted = {"MemTotal", "MemAvailable", "SwapTotal"}
        report["memory_kib"] = {line.split(":")[0]: int(line.split()[1]) for line in meminfo.read_text().splitlines() if line.split(":")[0] in wanted}

    executable = shutil.which("nvidia-smi")
    if not executable and Path("/usr/lib/wsl/lib/nvidia-smi").is_file():
        executable = "/usr/lib/wsl/lib/nvidia-smi"
    report["gpu_query"] = {"status": "executable_not_found"}
    if executable:
        query = command([executable, "--query-gpu=name,memory.total,memory.used,driver_version,compute_cap", "--format=csv,noheader,nounits"])
        query["status"] = "ok" if query["returncode"] == 0 else "unavailable_in_this_execution_context"
        if query["returncode"] == 0:
            fields = ["name", "memory_total_mib", "memory_used_mib", "driver_version", "compute_capability"]
            query["devices"] = [dict(zip(fields, (value.strip() for value in row))) for row in csv.reader(io.StringIO(query["stdout"])) if row]
        report["gpu_query"] = query

    if shutil.which("findmnt"):
        # Do not collect mount options, credentials, server names, or network addresses.
        report["project_mount"] = command(["findmnt", "--json", "--target", str(args.project.resolve()), "--output", "TARGET,FSTYPE"])

    if args.check_torch:
        if not report["packages"]["torch"]["import_discoverable"]:
            report["torch_cuda"] = {"status": "torch_not_installed_in_this_interpreter"}
        else:
            code = "import json,torch; print(json.dumps({'torch':torch.__version__,'cuda_build':torch.version.cuda,'cuda_available':torch.cuda.is_available(),'device_count':torch.cuda.device_count(),'scope':'query_only_no_tensor_workload'}))"
            result = command([sys.executable, "-c", code], timeout=30)
            result["status"] = "query_completed" if result["returncode"] == 0 else "query_failed"
            report["torch_cuda"] = result

    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        try:
            with args.output.open("x", encoding="utf-8") as handle:
                handle.write(text)
        except FileExistsError:
            parser.error(f"Refusing to overwrite evidence: {args.output}")
        print(f"Saved environment discovery to {args.output}")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
