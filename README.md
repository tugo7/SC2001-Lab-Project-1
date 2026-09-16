# SC2001 Project 1: Integration of Merge Sort & Insertion Sort

Hybrid sorting algorithm that switches from merge sort to insertion sort
once a subarray's size drops to a threshold `S`, compared against plain
merge sort.

## Files

| File | Part | Description |
|---|---|---|
| [`hybrid_sort.py`](hybrid_sort.py) | (a), (b) | Hybrid merge sort + insertion sort implementation, with key-comparison counting, plus `generate_data(n, x)` used for Part (b)'s input generation. Running it directly (`python hybrid_sort.py`) reproduces Part (c)(i): comparisons vs. `n` for fixed `S`. |
| [`experiment.py`](experiment.py) | (c)(ii) | Fixed `n`, sweeps `S`, plots comparisons vs. `S`. |
| [`part_c_iii_optimal_s.py`](part_c_iii_optimal_s.py) | (c)(iii) | Sweeps both `n` (1,000 → 10,000,000) and `S` to find the empirically optimal `S` per input size. |
| [`merge_sort.py`](merge_sort.py) | (d) | Original (plain) merge sort, self-contained — no dependency on the insertion sort code. |
| [`part_d_compare_mergesort.py`](part_d_compare_mergesort.py) | (d) | Compares hybrid sort (using the optimal `S` from (c)(iii)) against plain merge sort on 10,000,000 integers: key comparisons and CPU time. |

All scripts generate random integer arrays with `random.seed(42)` so
results are reproducible.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install matplotlib
```

## Running

```bash
python hybrid_sort.py                  # Part c(i)  -> comparisons_vs_n.png
python experiment.py                   # Part c(ii) -> part_c_ii_plot.png, part_c_ii_results.csv
python part_c_iii_optimal_s.py         # Part c(iii)-> part_c_iii_*.png/.csv
python part_d_compare_mergesort.py     # Part d     -> part_d_comparison.png, part_d_results.csv
```

`part_d_compare_mergesort.py` automatically reads the CPU-time-optimal
`S` for n = 10,000,000 from `part_c_iii_optimal_s_summary.csv`
(produced by the `part_c_iii_optimal_s.py` run) if present, otherwise
falls back to a default of `S = 16`.

## Results

### (b) Input data generation

`generate_data(n, x)` (defined identically in `hybrid_sort.py` and
`merge_sort.py`) produces an array of `n` random integers drawn
uniformly from `[1, x]` using `random.randint`. Every experiment script
calls it with:

- **Sizes `n`:** `1,000`, `10,000`, `100,000`, `1,000,000`,
  `10,000,000` — spanning the full range required by Part (b), from
  small (1,000) to large (10 million).
- **Value range:** `x = 10,000,000`, i.e. integers in `[1, 10,000,000]`
  — the largest dataset size, so values are as spread out as the
  largest array needs while staying within a plain Python `int`.
- **Reproducibility:** `random.seed(42)` is set immediately before
  generation in every script, so the same array is produced each run
  (and reused across every `S` in a sweep, so only `S` varies within a
  given `n`).

No datasets are checked into the repo — each script generates its own
input on the fly at run time, sized to whatever experiment it's
running.

### (c)(i) Comparisons vs. n (S fixed = 10)

Empirical comparisons track the `n·log₂(n)` reference closely — see
`comparisons_vs_n.png`.

### (c)(ii) Comparisons vs. S (n fixed = 1,000,000)

See `part_c_ii_plot.png` / `part_c_ii_results.csv`. Comparisons increase
monotonically with `S` (18.67M at S=1 up to 254.8M at S=1000), since
larger insertion-sort blocks make more comparisons than merge sort
would for the same elements. CPU time, however, is not monotonic: it
dips slightly to a minimum around S=20 (3.36s, vs. 3.90s at S=1) before
rising sharply for large S (33.65s at S=1000) — the same
comparisons-vs-time divergence explored more systematically in (c)(iii)
below.

### (c)(iii) Optimal S across input sizes

Sweeping `S` for each `n` (see `part_c_iii_results.csv`,
`part_c_iii_comparisons_vs_S.png`, `part_c_iii_time_vs_S.png`) surfaces
**two different answers** depending on what "optimal" means:

| n | Optimal S (fewest comparisons) | Optimal S (fastest CPU time) |
|---:|---:|---:|
| 1,000 | 1 | 16 |
| 10,000 | 1 | 16 |
| 100,000 | 1 | 12 |
| 1,000,000 | 1 | 8 |
| 10,000,000 | 1 | 24 |

- **By key comparisons**, `S = 1` (i.e. no insertion-sort cutoff at all —
  plain merge sort) always wins. This matches theory: insertion sort on
  a block of size `S` makes on average `O(S²/4)` comparisons, while merge
  sort would only need `O(S log S)` comparisons for the same block, and
  `S log S < S²/4` for essentially every `S` worth switching at. So
  minimizing *comparisons alone* never favors switching to insertion
  sort — this metric mainly serves the theoretical analysis in (c)(i)/(c)(ii),
  not a real tuning target.
- **By actual CPU time** — the practically meaningful notion of "best
  performance" the question is really after — the optimum is a small,
  **roughly constant** `S` in the ~8–24 range across all five input
  sizes, not something that grows with `n`. This matches the
  motivation in the problem statement: insertion sort has far less
  per-element overhead (no recursive calls, no sub-array copying) than
  merge sort, so for small blocks it's faster in wall-clock terms even
  though it performs more comparisons. See `part_c_iii_optimal_S_vs_n.png`.
  (Timing noise means the exact per-n value isn't perfectly flat — a
  single run per `(n, S)` pair, especially at small `n` where runs are
  only milliseconds, is sensitive to system jitter — but the values stay
  within one order of magnitude regardless of `n` scaling by four orders
  of magnitude, which is the qualitative point.)

Part (d) below uses the **CPU-time-optimal** `S` (loaded automatically
from `part_c_iii_optimal_s_summary.csv`), since that's the metric Part
(d) itself is measuring performance with.

### (d) Hybrid sort vs. original merge sort (n = 10,000,000)

Using `S = 24` (the CPU-time-optimal value found in (c)(iii) for
n = 10,000,000):

| Algorithm | Key comparisons | CPU time (s) |
|---|---:|---:|
| Hybrid sort (S=24) | 242,307,872 | 47.03 |
| Original merge sort | 220,099,725 | 52.89 |

- Hybrid sort makes **~10% more** key comparisons than plain merge sort
  (consistent with the (c)(iii) finding above — insertion sort is never
  comparison-cheaper).
- Hybrid sort is **~11% faster** in CPU time, because avoiding recursive
  merge-sort calls on the smallest subarrays saves more real time than
  the extra comparisons cost.
- Net result: for real-world performance (the actual point of
  hybridizing merge sort with insertion sort), the hybrid algorithm
  wins, even though it is not the "optimal" choice if you only look at
  the comparison count.

See `part_d_comparison.png` / `part_d_results.csv`.

## Notes

- `hybrid_sort.py`'s Part (c)(i) experiment code was wrapped in
  `if __name__ == "__main__":` so the module can be imported (for its
  `hybrid_sort()`/`generate_data()` functions) by the other experiment
  scripts without re-running the whole experiment as a side effect.
- Both `hybrid_sort.py` and `merge_sort.py` use the same `merge()`
  logic and comparison-counting convention, so the Part (d) comparison
  isolates the effect of the insertion-sort cutoff rather than any
  incidental implementation difference.
