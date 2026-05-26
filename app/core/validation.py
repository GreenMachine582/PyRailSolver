from dataclasses import dataclass, field


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str


@dataclass
class ValidationResult:
    errors: list[ValidationIssue] = field(default_factory=list)
    warnings: list[ValidationIssue] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def add_error(self, code: str, message: str) -> None:
        self.errors.append(ValidationIssue(code=code, message=message))

    def add_warning(self, code: str, message: str) -> None:
        self.warnings.append(ValidationIssue(code=code, message=message))

    def merge(self, other: "ValidationResult") -> None:
        """Absorb all issues from another result into this one."""
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
