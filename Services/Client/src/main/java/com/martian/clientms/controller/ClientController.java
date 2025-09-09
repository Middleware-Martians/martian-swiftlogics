package com.martian.clientms.controller;

import com.martian.clientms.dto.LoginRequest;
import com.martian.clientms.dto.RegisterRequest;
import com.martian.clientms.entity.Client;
import com.martian.clientms.service.ClientService;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/clients")
@Validated
public class ClientController {

    private final ClientService clientService;

    @Autowired
    public ClientController(ClientService clientService) {
        this.clientService = clientService;
    }

    @PostMapping("/register")
    public ResponseEntity<Client> register(@Valid @RequestBody RegisterRequest req) {
        Client created = clientService.register(req);
        created.setPassword(null);
        return ResponseEntity.ok(created);
    }

    @PostMapping("/login")
    public ResponseEntity<Client> login(@Valid @RequestBody LoginRequest req) {
        Client c = clientService.login(req);
        c.setPassword(null);
        return ResponseEntity.ok(c);
    }

    @GetMapping
    public ResponseEntity<List<Client>> getAll() {
        List<Client> list = clientService.getAll();
        list.forEach(c -> c.setPassword(null));
        return ResponseEntity.ok(list);
    }

    @GetMapping("/{id}")
    public ResponseEntity<Client> getById(@PathVariable Long id) {
        Client c = clientService.getById(id);
        c.setPassword(null);
        return ResponseEntity.ok(c);
    }

    @PutMapping("/{id}")
    public ResponseEntity<Client> update(@PathVariable Long id, @RequestBody Client update) {
        Client c = clientService.update(id, update);
        c.setPassword(null);
        return ResponseEntity.ok(c);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        clientService.delete(id);
        return ResponseEntity.noContent().build();
    }
}

