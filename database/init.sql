-- Docker MySQL init seed data
USE student_risk_monitoring;

-- Sample admin user (hash from werkzeug)
INSERT IGNORE INTO users (username, email, password_hash, role, created_at) VALUES 
('admin', 'admin@example.com', '$2b$12$EixZaYVK1fsbw1Zfbx3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'admin', NOW());

-- Note: Full seed via Python seed_data.py recommended

