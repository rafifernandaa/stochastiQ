import numpy as np
from scipy import stats
from dataclasses import dataclass
from typing import Optional

@dataclass
class ExplorationResult:
    mean: float
    variance: float
    skewness: float
    kurtosis: float
    vmr: float  # variance-to-mean ratio
    tail_flag: str
    summary: str

@dataclass
class ModelFitResult:
    model_name: str
    parameters: dict
    ks_statistic: float
    p_value: float
    good_fit: bool
    verdict: str

@dataclass
class AssessmentResult:
    exploration: ExplorationResult
    candidates: list[str]
    fit_results: list[ModelFitResult]
    best_model: str
    extreme_event_prob: float
    reasoning_trace: list[str]

def explore(data: np.ndarray) -> ExplorationResult:
    mean = float(np.mean(data))
    variance = float(np.var(data))
    skewness = float(stats.skew(data))
    kurtosis = float(stats.kurtosis(data))
    vmr = variance / mean if mean != 0 else 0
    tail_flag = "heavy" if kurtosis > 3 else "light"

    summary = (
        f"Mean={mean:.3f}, Variance={variance:.3f}, "
        f"VMR={vmr:.3f}, Skewness={skewness:.3f}, "
        f"Kurtosis={kurtosis:.3f}, Tail={tail_flag}"
    )
    return ExplorationResult(
        mean, variance, skewness, kurtosis, vmr, tail_flag, summary
    )

def test_poisson(counts: np.ndarray) -> ModelFitResult:
    lambda_hat = float(np.mean(counts))
    max_val = int(max(counts))
    bins = np.arange(0, max_val + 2)
    
    observed_freq, _ = np.histogram(counts, bins=bins)
    expected_freq = np.array([
        stats.poisson.pmf(k, lambda_hat) * len(counts)
        for k in range(max_val + 1)
    ])

    # Merge low-expected bins from the right
    while len(expected_freq) > 1 and expected_freq[-1] < 5:
        expected_freq[-2] += expected_freq[-1]
        expected_freq = expected_freq[:-1]
        observed_freq[-2] += observed_freq[-1]
        observed_freq = observed_freq[:-1]

    # Normalize expected to match observed sum exactly
    expected_freq = expected_freq * (
        observed_freq.sum() / expected_freq.sum()
    )

    if len(observed_freq) < 2:
        return ModelFitResult(
            "Poisson", {"lambda": lambda_hat},
            0, 0, False, "Insufficient bins for chi-square test"
        )

    chi2, p = stats.chisquare(observed_freq, expected_freq)
    good_fit = p > 0.05
    verdict = (
        f"Poisson(λ={lambda_hat:.3f}) "
        f"{'PASSES' if good_fit else 'FAILS'} "
        f"chi-square test (p={p:.4f})"
    )
    return ModelFitResult(
        "Poisson", {"lambda": lambda_hat},
        float(chi2), float(p), good_fit, verdict
    )

def test_exponential(inter_arrivals: np.ndarray) -> ModelFitResult:
    mean_hat = float(np.mean(inter_arrivals))
    ks_stat, p = stats.kstest(
        inter_arrivals, 'expon',
        args=(0, mean_hat)
    )
    good_fit = p > 0.05
    verdict = (
        f"Exponential(mean={mean_hat:.3f}) "
        f"{'PASSES' if good_fit else 'FAILS'} "
        f"KS test (p={p:.4f}) — "
        f"memoryless property "
        f"{'supported' if good_fit else 'rejected'}"
    )
    return ModelFitResult(
        "Exponential", {"mean": mean_hat},
        float(ks_stat), float(p), good_fit, verdict
    )

def test_levy(data: np.ndarray) -> ModelFitResult:
    loc, scale = stats.levy.fit(data)
    ks_stat, p = stats.kstest(
        data, 'levy', args=(loc, scale)
    )
    good_fit = p > 0.05
    verdict = (
        f"Lévy(loc={loc:.3f}, scale={scale:.3f}) "
        f"{'PASSES' if good_fit else 'FAILS'} "
        f"KS test (p={p:.4f})"
    )
    return ModelFitResult(
        "Lévy", {"loc": float(loc), "scale": float(scale)},
        float(ks_stat), float(p), good_fit, verdict
    )

def test_negative_binomial(counts: np.ndarray) -> ModelFitResult:
    """Fit Negative Binomial for overdispersed count data."""
    mean = float(np.mean(counts))
    variance = float(np.var(counts))
    
    if variance <= mean:
        return ModelFitResult(
            "Negative Binomial",
            {"note": "VMR <= 1, underdispersed"},
            0, 1.0, False,
            "Negative Binomial not applicable — data is not overdispersed"
        )
    
    # Method of moments estimation
    # p = mean/variance, r = mean²/(variance - mean)
    p_hat = mean / variance
    r_hat = (mean ** 2) / (variance - mean)
    
    max_val = int(max(counts))
    observed_freq, _ = np.histogram(
        counts, bins=np.arange(0, max_val + 2)
    )
    expected_freq = np.array([
        stats.nbinom.pmf(k, r_hat, p_hat) * len(counts)
        for k in range(max_val + 1)
    ])
    
    # Merge low bins from right
    while len(expected_freq) > 1 and expected_freq[-1] < 5:
        expected_freq[-2] += expected_freq[-1]
        expected_freq = expected_freq[:-1]
        observed_freq[-2] += observed_freq[-1]
        observed_freq = observed_freq[:-1]
    
    # Normalize
    expected_freq = expected_freq * (
        observed_freq.sum() / expected_freq.sum()
    )
    
    if len(observed_freq) < 2:
        return ModelFitResult(
            "Negative Binomial",
            {"r": r_hat, "p": p_hat},
            0, 0, False, "Insufficient bins for test"
        )
    
    chi2, p = stats.chisquare(observed_freq, expected_freq)
    good_fit = p > 0.05
    verdict = (
        f"NegativeBinomial(r={r_hat:.3f}, p={p_hat:.3f}) "
        f"{'PASSES' if good_fit else 'FAILS'} "
        f"chi-square test (p={p:.4f}) — "
        f"VMR={variance/mean:.3f} confirms "
        f"{'overdispersion' if variance > mean else 'underdispersion'}"
    )
    return ModelFitResult(
        "Negative Binomial",
        {"r": float(r_hat), "p": float(p_hat)},
        float(chi2), float(p), good_fit, verdict
    )

def simulate(model_name: str,
             params: dict,
             n: int = 1000) -> np.ndarray:
    if model_name == "Poisson":
        return np.random.poisson(params["lambda"], n)
    elif model_name == "Exponential":
        return np.random.exponential(params["mean"], n)
    elif model_name == "Lévy":
        return stats.levy.rvs(
            loc=params["loc"], scale=params["scale"], size=n
        )
    else:
        raise ValueError(f"Unknown model: {model_name}")

def extreme_event_probability(data: np.ndarray,
                               threshold: float) -> float:
    return float(np.mean(data > threshold))

def generate_scenario(scenario: str,
                       n: int = 500) -> np.ndarray:
    """Generate synthetic demo data for each scenario."""
    np.random.seed(42)
    if scenario == "poisson":
        # Clean Poisson process, rate=3
        return np.random.poisson(3, n).astype(float)
    elif scenario == "levy":
        # Heavy-tailed, laser-like burst behavior
        return stats.levy.rvs(loc=0, scale=0.5, size=n)
    elif scenario == "exponential":
        # Memoryless inter-arrivals
        return np.random.exponential(2.0, n)
    elif scenario == "ambiguous":
        # Mixed: mostly Poisson but with injected extremes
        base = np.random.poisson(3, n).astype(float)
        base[np.random.choice(n, 20)] = np.random.uniform(20, 50, 20)
        return base
    else:
        raise ValueError(f"Unknown scenario: {scenario}")