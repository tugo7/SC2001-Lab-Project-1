# Hybrid Sort: Merge Sort + Insertion Sort

A hybrid sorting algorithm that runs merge sort but switches to
insertion sort once a subarray's size drops to a threshold `S`,
compared against a plain merge sort.

## Files

- [`hybrid_sort.py`](hybrid_sort.py) — `hybrid_sort`, its
  `insertion_sort`/`merge` helpers, and `generate_data` for producing
  random test arrays. Returns the number of key comparisons performed.
  Run directly (`python hybrid_sort.py`) for a quick correctness
  self-test.
- [`merge_sort.py`](merge_sort.py) — the plain `merge_sort`, standalone
  (no dependency on `hybrid_sort.py`), using the same `merge()` logic
  and comparison-counting convention so the two are directly
  comparable. Run directly (`python merge_sort.py`) for a quick
  correctness self-test.
- [`experiments.py`](experiments.py) — all experiments, each writing
  its output into `results/`:
  - `n_sweep` — key comparisons vs. input size `n`, for a fixed `S`.
  - `s_sweep` — key comparisons and CPU time vs. threshold `S`, for a
    fixed `n`.
  - `optimal_s` — sweeps both `n` (1,000 → 10,000,000) and `S` to find
    the empirically best `S` for each input size.
  - `comparison` — hybrid sort (using the CPU-time-optimal `S` found
    by `optimal_s`) vs. plain merge sort, on 10,000,000 integers.
- `results/` — generated CSVs and plots (see below).

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install matplotlib
```

## Running

```bash
python experiments.py             # run everything
python experiments.py n_sweep     # or just one experiment
python experiments.py s_sweep
python experiments.py optimal_s
python experiments.py comparison
```

`comparison` automatically reads the CPU-time-optimal `S` for
n = 10,000,000 from `results/optimal_s_summary.csv` (produced by
`optimal_s`) if present, otherwise falls back to `S = 16`.

Test data is generated on the fly with `generate_data(n, x)`: `n`
random integers drawn uniformly from `[1, x]`, with
`x = 10,000,000` and `random.seed(42)` for reproducibility. No
datasets are checked into the repo.

## Results

### Comparisons vs. input size (fixed S = 10)

Empirical comparisons track the `n·log₂(n)` reference closely — see
`results/comparisons_vs_n.png`.

### Comparisons vs. threshold S (fixed n = 1,000,000)

Comparisons increase monotonically with `S` (18.67M at S=1 up to
254.8M at S=1000), since larger insertion-sort blocks make more
comparisons than merge sort would for the same elements. CPU time,
however, is not monotonic: it dips to a minimum around S=20 (3.36s,
vs. 3.90s at S=1) before rising sharply for large S (33.65s at
S=1000). See `results/comparisons_vs_s.png`.

### Finding the best threshold S

Sweeping `S` for each `n` (see `results/optimal_s_results.csv`,
`results/optimal_s_comparisons_vs_s.png`,
`results/optimal_s_time_vs_s.png`) surfaces two different answers
depending on what "best" means:

| n | Best S by comparisons | Best S by CPU time |
|---:|---:|---:|
| 1,000 | 1 | 16 |
| 10,000 | 1 | 16 |
| 100,000 | 1 | 12 |
| 1,000,000 | 1 | 8 |
| 10,000,000 | 1 | 24 |

- **By key comparisons**, `S = 1` (i.e. no insertion-sort cutoff at
  all — plain merge sort) always wins. Insertion sort on a block of
  size `S` makes on average `O(S²/4)` comparisons, while merge sort
  would only need `O(S log S)` for the same block, and
  `S log S < S²/4` for essentially every `S` worth switching at. So
  minimizing comparisons alone never favors switching to insertion
  sort.
- **By actual CPU time** — the practically meaningful notion of "best"
  — the optimum is a small, roughly constant `S` in the ~8–24 range
  across all five input sizes, not something that grows with `n`.
  Insertion sort has far less per-element overhead (no recursive
  calls, no sub-array copying) than merge sort, so for small blocks it
  is faster in wall-clock terms even though it performs more
  comparisons. See `results/optimal_s_vs_n.png`. (A single run per
  `(n, S)` pair means timing is somewhat noisy, especially at small
  `n` where runs are only milliseconds — but the values stay within
  one order of magnitude even as `n` scales by four orders of
  magnitude, which is the qualitative point.)

The final comparison below uses the CPU-time-optimal `S`, since that's
the metric it's measuring performance with.

### Hybrid sort vs. plain merge sort (n = 10,000,000)

Using `S = 24` (the CPU-time-optimal value found above for
n = 10,000,000):

| Algorithm | Key comparisons | CPU time (s) |
|---|---:|---:|
| Hybrid sort (S=24) | 242,307,872 | 47.03 |
| Merge sort | 220,099,725 | 52.89 |

- Hybrid sort makes **~10% more** key comparisons than plain merge
  sort (consistent with the finding above — insertion sort is never
  comparison-cheaper).
- Hybrid sort is **~11% faster** in CPU time, because avoiding
  recursive merge-sort calls on the smallest subarrays saves more real
  time than the extra comparisons cost.
- Net result: for real-world performance, the hybrid algorithm wins,
  even though it is not the best choice if you only look at comparison
  count.

See `results/hybrid_vs_merge_comparison.png` /
`results/hybrid_vs_merge_results.csv`.
