"""Typed exceptions for fair-lending-screener. All error paths raise these; no silent empty returns."""


class FairLendingScreenerError(Exception):
    """Base exception for all fair-lending-screener errors."""


class InsufficientDataError(FairLendingScreenerError):
    """Raised when the combined sample falls below the minimum size required for logistic regression."""

    def __init__(self, actual: int, minimum: int, protected_class: str, comparison_class: str):
        self.actual = actual
        self.minimum = minimum
        self.protected_class = protected_class
        self.comparison_class = comparison_class
        super().__init__(
            f"Insufficient sample: {actual} observations (protected={protected_class!r}, "
            f"comparison={comparison_class!r}) — minimum required is {minimum}. "
            f"With fewer than {minimum} observations, logistic regression coefficients are unstable "
            f"and confidence intervals are unreliable. "
            f"See Peduzzi et al. (1996), J. Clin. Epidemiology 49(12):1373–1379."
        )


class ModelConvergenceError(FairLendingScreenerError):
    """Raised when statsmodels Logit fails to converge. Includes diagnostic information."""

    def __init__(self, iterations: int, final_log_likelihood: float, message: str = ""):
        self.iterations = iterations
        self.final_log_likelihood = final_log_likelihood
        super().__init__(
            f"Logistic regression failed to converge after {iterations} iterations "
            f"(final log-likelihood: {final_log_likelihood:.4f}). "
            f"Common causes: perfect separation (one group has only approvals or only denials), "
            f"near-collinear predictors, or an MSA with insufficient variation. "
            f"Inspect the data for degenerate subgroups. "
            + (f"Optimizer message: {message}" if message else "")
        )


class InvalidProtectedClassError(FairLendingScreenerError):
    """Raised when the specified protected or comparison class is not present in the data."""

    def __init__(self, requested: str, field: str, valid_values: list[str]):
        self.requested = requested
        self.field = field
        self.valid_values = valid_values
        super().__init__(
            f"Protected class value {requested!r} not found in column {field!r}. "
            f"Valid values in this dataset: {sorted(valid_values)}. "
            f"Check the derived_race or derived_ethnicity column in your data."
        )


class MissingControlsError(FairLendingScreenerError):
    """Raised when a required control column is absent from the DataFrame."""

    def __init__(self, missing_columns: list[str], available_columns: list[str]):
        self.missing_columns = missing_columns
        self.available_columns = available_columns
        super().__init__(
            f"Required control column(s) not found in DataFrame: {missing_columns}. "
            f"Available columns: {sorted(available_columns)}. "
            f"Either provide a DataFrame with these columns or pass controls=[] to use only "
            f"the columns that are available (results will be less complete)."
        )


class DataSourceError(FairLendingScreenerError):
    """Raised when the CFPB HMDA data source is unreachable or returns unexpected data."""

    def __init__(self, url: str, reason: str):
        self.url = url
        self.reason = reason
        super().__init__(
            f"CFPB HMDA data source check failed for {url!r}: {reason}. "
            f"Verify network connectivity and that https://ffiec.cfpb.gov is reachable."
        )


class InsufficientGroupSizeError(FairLendingScreenerError):
    """Raised when one group (protected or comparison) has too few observations for reliable estimation."""

    def __init__(self, group: str, count: int, minimum: int):
        self.group = group
        self.count = count
        self.minimum = minimum
        super().__init__(
            f"Group {group!r} has only {count} observations (minimum per group: {minimum}). "
            f"Results would be unreliable. Filter to a larger geography or time period."
        )
