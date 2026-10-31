"""Run Week 7 model comparisons; keeps config.yaml unchanged afterwards.
Run from the ETAI-Pipeline project root: python run_all_week7.py
"""
from pathlib import Path
import copy
import csv
import datetime
import subprocess
import sys
import yaml

CONFIG = Path('config.yaml')
MODELS = {
    'dummy': {'strategy': 'prior'},
    'logistic_regression': {'max_iter': 2000, 'class_weight': 'balanced'},
    'naive_bayes': {},
    'decision_tree': {'random_state': 42, 'class_weight': 'balanced'},
    'random_forest': {'n_estimators': 200, 'random_state': 42, 'n_jobs': -1, 'class_weight': 'balanced'},
    'oblique_random_forest': {'n_estimators': 200, 'n_components': 10, 'random_state': 42, 'n_jobs': -1},
    'adaboost': {'max_depth': 1, 'n_estimators': 200, 'learning_rate': 1.0, 'random_state': 42},
    'gradient_boosting': {'random_state': 42},
    'hist_gradient_boosting': {'random_state': 42, 'class_weight': 'balanced'},
}

def main():
    original = CONFIG.read_bytes()
    cfg = yaml.safe_load(original)
    spaces = cfg.get('tuning', {}).get('search_spaces', {})
    logdir = Path('results/week7_logs')
    logdir.mkdir(parents=True, exist_ok=True)
    summary = logdir / 'execution_status.csv'
    # Preserve any pre-existing scoreboard. The pipeline itself appends rows to results/runs.csv.
    scoreboard = Path(cfg.get('output', {}).get('scoreboard', 'results/runs.csv'))
    if scoreboard.exists():
        backup = scoreboard.with_name(scoreboard.name + '.before_week7_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + '.bak')
        backup.write_bytes(scoreboard.read_bytes())
        print('Scoreboard backup:', backup, flush=True)
    tasks = [(name, False) for name in MODELS] + [(name, True) for name in MODELS if name in spaces]
    print(f'Running {len(tasks)} experiments. Tuned runs use configured n_trials={cfg["tuning"]["n_trials"]}.', flush=True)
    try:
        with summary.open('w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['model', 'tuned', 'return_code', 'log_file'])
            for i, (name, tuned) in enumerate(tasks, 1):
                current = copy.deepcopy(cfg)
                current['model'] = {'type': name, 'params': MODELS[name]}
                current['tuning']['enabled'] = tuned
                CONFIG.write_text(yaml.safe_dump(current, sort_keys=False, allow_unicode=True), encoding='utf-8')
                log = logdir / f'{i:02d}_{name}_{"tuned" if tuned else "default"}.log'
                print(f'[{i}/{len(tasks)}] {name} ({"tuned" if tuned else "default"})', flush=True)
                with log.open('w', encoding='utf-8') as output:
                    result = subprocess.run([sys.executable, 'main.py'], stdout=output, stderr=subprocess.STDOUT)
                writer.writerow([name, tuned, result.returncode, str(log)])
                file.flush()
                print('  OK' if result.returncode == 0 else f'  FAILED; see {log}', flush=True)
    finally:
        CONFIG.write_bytes(original)
        print('Original config.yaml restored.', flush=True)
    print('Execution status:', summary)
    print('Model results (if runs succeeded):', scoreboard)

if __name__ == '__main__':
    main()
