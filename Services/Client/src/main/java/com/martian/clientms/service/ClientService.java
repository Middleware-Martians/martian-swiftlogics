package com.martian.clientms.service;

import com.martian.clientms.dto.LoginRequest;
import com.martian.clientms.dto.RegisterRequest;
import com.martian.clientms.entity.Client;
import com.martian.clientms.repository.ClientRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class ClientService {

    private final ClientRepository clientRepository;
    private final BCryptPasswordEncoder passwordEncoder;

    @Autowired
    public ClientService(ClientRepository clientRepository, BCryptPasswordEncoder passwordEncoder) {
        this.clientRepository = clientRepository;
        this.passwordEncoder = passwordEncoder;
    }

    public Client register(RegisterRequest req) {
        if (clientRepository.existsByEmail(req.getEmail())) {
            throw new IllegalArgumentException("Email already in use");
        }
        Client c = new Client();
        c.setName(req.getName());
        c.setEmail(req.getEmail());
        c.setPassword(passwordEncoder.encode(req.getPassword()));
        c.setPhone(req.getPhone());
        c.setAddress(req.getAddress());
        return clientRepository.save(c);
    }

    public Client login(LoginRequest req) {
        Optional<Client> oc = clientRepository.findByEmail(req.getEmail());
        if (oc.isEmpty()) throw new IllegalArgumentException("Invalid credentials");
        Client c = oc.get();
        if (!passwordEncoder.matches(req.getPassword(), c.getPassword())) {
            throw new IllegalArgumentException("Invalid credentials");
        }
        return c; // in real app return token
    }

    public Client getById(Long id) {
        return clientRepository.findById(id).orElseThrow(() -> new IllegalArgumentException("Client not found"));
    }

    public List<Client> getAll() {
        return clientRepository.findAll();
    }

    public Client update(Long id, Client update) {
        Client existing = getById(id);
        if (update.getName() != null) existing.setName(update.getName());
        if (update.getEmail() != null && !update.getEmail().equals(existing.getEmail())) {
            if (clientRepository.existsByEmail(update.getEmail())) {
                throw new IllegalArgumentException("Email already in use");
            }
            existing.setEmail(update.getEmail());
        }
        if (update.getPassword() != null && !update.getPassword().isEmpty()) {
            existing.setPassword(passwordEncoder.encode(update.getPassword()));
        }
        if (update.getPhone() != null) existing.setPhone(update.getPhone());
        if (update.getAddress() != null) existing.setAddress(update.getAddress());
        return clientRepository.save(existing);
    }

    public void delete(Long id) {
        clientRepository.deleteById(id);
    }
}

