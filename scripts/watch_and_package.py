from pathlib import Path
import shutil
import time
import datetime
import zipfile

ROOT = Path(__file__).resolve().parents[1]
WATCH_FILES = [ROOT / 'best_model.zip', ROOT / 'final_model.zip']
ARTIFACTS_DIR = ROOT / 'artifacts'


def find_model():
    for p in WATCH_FILES:
        if p.exists():
            return p
    return None


def package_model(model_path: Path):
    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    dest = ARTIFACTS_DIR / f'artifacts_{ts}'
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(model_path, dest / model_path.name)
    # copy logs if present
    for fname in ('full_training.log', 'full_training.err'):
        f = ROOT / fname
        if f.exists():
            shutil.copy2(f, dest / fname)
    if (ROOT / 'eval_logs').exists():
        shutil.copytree(ROOT / 'eval_logs', dest / 'eval_logs', dirs_exist_ok=True)

    zip_path = ARTIFACTS_DIR / f'artifacts_{ts}.zip'
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for p in dest.rglob('*'):
            zf.write(p, p.relative_to(dest.parent))
    print(f'Packaged artifacts to {zip_path}')
    return zip_path


def main(poll_interval: float = 10.0):
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    print('Watcher started, polling for model files...')
    while True:
        model = find_model()
        if model:
            print(f'Detected model: {model}')
            package_model(model)
            break
        time.sleep(poll_interval)


if __name__ == '__main__':
    main()
