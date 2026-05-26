from app.core.validation import ValidationIssue, ValidationResult


class TestValidationIssue:
    def test_fields(self) -> None:
        issue = ValidationIssue(code="SOME_CODE", message="Something went wrong")
        assert issue.code == "SOME_CODE"
        assert issue.message == "Something went wrong"

    def test_frozen(self) -> None:
        issue = ValidationIssue(code="X", message="y")
        try:
            issue.code = "Z"  # type: ignore[misc]
            raise AssertionError("should have raised")
        except AttributeError:
            pass


class TestValidationResult:
    def test_empty_is_valid(self) -> None:
        assert ValidationResult().is_valid

    def test_add_error_makes_invalid(self) -> None:
        result = ValidationResult()
        result.add_error("E001", "something broke")
        assert not result.is_valid

    def test_warning_alone_stays_valid(self) -> None:
        result = ValidationResult()
        result.add_warning("W001", "heads up")
        assert result.is_valid

    def test_error_stored(self) -> None:
        result = ValidationResult()
        result.add_error("E001", "oops")
        assert len(result.errors) == 1
        assert result.errors[0].code == "E001"
        assert result.errors[0].message == "oops"

    def test_warning_stored(self) -> None:
        result = ValidationResult()
        result.add_warning("W001", "note")
        assert len(result.warnings) == 1
        assert result.warnings[0].code == "W001"

    def test_multiple_errors(self) -> None:
        result = ValidationResult()
        result.add_error("E1", "first")
        result.add_error("E2", "second")
        assert len(result.errors) == 2

    def test_merge_combines_errors(self) -> None:
        a = ValidationResult()
        a.add_error("E1", "from a")
        b = ValidationResult()
        b.add_error("E2", "from b")
        a.merge(b)
        assert len(a.errors) == 2

    def test_merge_combines_warnings(self) -> None:
        a = ValidationResult()
        a.add_warning("W1", "from a")
        b = ValidationResult()
        b.add_warning("W2", "from b")
        a.merge(b)
        assert len(a.warnings) == 2

    def test_merge_preserves_validity(self) -> None:
        a = ValidationResult()
        b = ValidationResult()
        b.add_error("E1", "from b")
        a.merge(b)
        assert not a.is_valid
