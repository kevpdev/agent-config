package com.example.validation;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.Test;

class EmailValidatorTest {

    @Test
    void should_returnFalse_when_candidateIsBlank() {
        String candidate = "   ";

        boolean valid = EmailValidator.isValid(candidate);

        assertFalse(valid);
    }

    @Test
    void should_returnFalse_when_candidateIsNull() {
        boolean valid = EmailValidator.isValid(null);

        assertFalse(valid);
    }

    @Test
    void should_returnTrue_when_addressIsWellFormed() {
        String candidate = "kevin@example.com";

        boolean valid = EmailValidator.isValid(candidate);

        assertTrue(valid);
    }

    @Test
    void should_returnFalse_when_atSignIsMissing() {
        String candidate = "kevin.example.com";

        boolean valid = EmailValidator.isValid(candidate);

        assertFalse(valid);
    }

    @Test
    void should_returnFalse_when_domainHasNoDot() {
        String candidate = "kevin@example";

        boolean valid = EmailValidator.isValid(candidate);

        assertFalse(valid);
    }
}
