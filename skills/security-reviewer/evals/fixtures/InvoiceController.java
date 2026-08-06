package com.example.invoice;

import java.security.Principal;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class InvoiceController {

    private static final Logger LOG = LoggerFactory.getLogger(InvoiceController.class);

    private static final String SELECT_INVOICE =
            "SELECT id, owner_login, amount_cents FROM invoice WHERE id = ?";

    private static final RowMapper<Invoice> INVOICE_ROW = (rs, rowNum) ->
            new Invoice(rs.getLong("id"), rs.getString("owner_login"), rs.getLong("amount_cents"));

    private final JdbcTemplate jdbc;

    InvoiceController(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    @GetMapping("/invoices/{id}")
    public ResponseEntity<Invoice> byId(@PathVariable long id, Principal principal) {
        if (principal == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
        List<Invoice> found = jdbc.query(SELECT_INVOICE, INVOICE_ROW, id);
        if (found.isEmpty()) {
            return ResponseEntity.notFound().build();
        }
        Invoice invoice = found.get(0);
        if (!invoice.ownerLogin().equals(principal.getName())) {
            LOG.warn("invoice {} requested by a non-owner", id);
            return ResponseEntity.notFound().build();
        }
        LOG.info("invoice {} served", id);
        return ResponseEntity.ok(invoice);
    }

    public record Invoice(long id, String ownerLogin, long amountCents) {
    }
}
