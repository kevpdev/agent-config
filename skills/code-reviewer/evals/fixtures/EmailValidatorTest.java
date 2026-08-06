package com.example.validation;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.Test;

class EmailValidatorTest {

    @Test
    void rejectsBlankCandidate() {
        assertFalse(EmailValidator.isValid("   "));
    }

    @Test
    void acceptsWellFormedAddress() {
        assertTrue(EmailValidator.isValid("kevin@example.com"));
    }

    @Test
    void rejectsAddressWithoutAtSign() {
        assertFalse(EmailValidator.isValid("kevin.example.com"));
    }
}
