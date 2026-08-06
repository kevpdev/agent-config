package com.example.validation;

import java.util.regex.Pattern;

/**
 * Validation syntaxique d'une adresse email.
 *
 * <p>Ne vérifie que la forme : ni l'existence du domaine, ni la délivrabilité.
 * Un appelant qui a besoin de cette garantie doit passer par une vérification réseau.
 */
public final class EmailValidator {

    private static final Pattern EMAIL = Pattern.compile("^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$");

    private EmailValidator() {
    }

    /**
     * Indique si une chaîne a la forme d'une adresse email.
     *
     * @param candidate la chaîne à valider, éventuellement {@code null} ou blanche
     * @return {@code true} si la chaîne porte un local-part, un arobase et un domaine pointé
     */
    public static boolean isValid(String candidate) {
        if (candidate == null || candidate.isBlank()) {
            return false;
        }
        return EMAIL.matcher(candidate).matches();
    }
}
