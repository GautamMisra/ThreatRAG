OWASP Top 10: 2025
A01:2025 – Broken Access Control
Description:

Occurs when restrictions on what authenticated or anonymous users are allowed to do are not properly enforced. Attackers can exploit these flaws to access unauthorized functionality or data (e.g., viewing other accounts, accessing sensitive files, modifying user permissions). In the 2025 edition, Server-Side Request Forgery (SSRF) as well as API authorization flaws (BOLA and BFLA) are formally folded into this category.

How to Prevent:

Adopt a "deny by default" access policy; only explicitly granted roles or users should gain access.

Implement centralized access control mechanisms in server-side code rather than client-side validations.

Enforce record ownership checks on every request (ensure user_id belongs to the current session).

Block unauthorized internal requests (restrict internal network access to eliminate SSRF vectors).

Disable directory listing and protect sensitive metadata endpoints.

Attack Scenario:

An attacker logs into an application as user 1002. By modifying the request URL from GET /api/documents/1002/invoice.pdf to GET /api/documents/1001/invoice.pdf, the system fails to verify ownership and returns confidential financial records belonging to user 1001 (Broken Object Level Authorization / IDOR).

A02:2025 – Security Misconfiguration
Description:

Climbing to #2 in 2025 due to the explosion of complex cloud, container, and infrastructure-as-code deployments. It involves unhardened application stacks, default credentials, exposed administrative interfaces, excessive cloud permissions, unneeded enabled services/ports, or overly permissive CORS configurations.

How to Prevent:

Implement automated hardened baseline images and Infrastructure-as-Code (IaC) scanners.

Disable default accounts and enforce password changes on initial setup.

Turn off debugging and detailed stack-trace error messages in production environments.

Send security headers (Content-Security-Policy, X-Frame-Options, Strict-Transport-Security).

Enforce the principle of least privilege on all cloud IAM roles and service tokens.

Attack Scenario:

A developer leaves default administrative credentials (admin:admin) on an exposed cloud management dashboard (/admin-console) and fails to disable debug mode. An attacker accesses the interface, forces an application error to dump environment variables via verbose error reporting, and extracts production database credentials.

A03:2025 – Software Supply Chain Failures
Description:

A new category replacing and expanding Vulnerable and Outdated Components. It covers the entire lifecycle of third-party software and dependencies—including compromised open-source packages, malicious transitive dependencies, typo-squatting, unpinned dependency updates, and tampered CI/CD pipelines.

How to Prevent:

Generate and continuously audit Software Bills of Materials (SBOMs) using standards like CycloneDX or SPDX.

Use automated Software Composition Analysis (SCA) to detect known CVEs and malicious package behaviors.

Lock and pin package dependencies and check cryptographic hashes (e.g., package-lock.json, poetry.lock).

Sign build artifacts and ensure build pipelines (GitHub Actions, GitLab CI) require MFA and strict runner permissions.

Attack Scenario:

An attacker gains commit access to an abandoned NPM package used by thousands of applications. They push a minor update containing an obfuscated credential-harvesting payload. When a target team’s automated CI/CD pipeline builds the production image using unpinned dependencies (^1.4.0), it pulls the malicious version, exfiltrating the application's runtime API keys.

A04:2025 – Cryptographic Failures
Description:

Focuses on weaknesses related to data protection in transit and at rest. Common issues include transmitting sensitive data in cleartext, utilizing deprecated cryptographic algorithms (MD5, SHA1, DES), inadequate randomness, hardcoded cryptographic keys, and poor certificate validation.

How to Prevent:

Classify data processed by the application and enforce encryption at rest using modern standards (e.g., AES-256, ChaCha20).

Enforce TLS 1.3 (or modern TLS 1.2) everywhere, with HTTP Strict Transport Security (HSTS) enabled.

Never invent or roll custom encryption algorithms; use vetted cryptographic libraries.

Hash passwords using salted, work-factor algorithms such as Argon2id or bcrypt.

Attack Scenario:

A web platform stores user credit card records in a database encrypted using DES with a static, hardcoded encryption key in the source code. Once an attacker extracts the database backup via a backup storage leak, they retrieve the static key from GitHub and decrypt all cardholder data within minutes.

A05:2025 – Injection
Description:

Occurs when untrusted data is sent to an interpreter as part of a command or query without proper validation or sanitization. Attack vectors include SQL injection, OS command injection, Cross-Site Scripting (XSS), NoSQL injection, and LDAP injection.

How to Prevent:

Use parameterized queries or Object-Relational Mappers (ORMs) that enforce parameterization.

Employ context-aware output encoding to neutralize browser-rendered scripts (preventing XSS).

Strictly validate input using allow-lists (whitelists) rather than block-lists.

Avoid executing shell commands directly using dynamic input (e.g., avoid os.system() or exec()).

Attack Scenario:

A search form takes user input and concatenates it into an SQL query: SELECT * FROM products WHERE name = ' + input + '. An attacker submits ' OR '1'='1'; DROP TABLE users; --, manipulating the query structure to dump all rows and potentially delete the user database table.

A06:2025 – Insecure Design
Description:

A broad category focusing on architectural and design flaws that cannot be solved by simply fixing bugs in the implementation. If the fundamental design lacks security controls, threat modeling, or domain-specific safeguards, the system remains vulnerable despite bug-free code.

How to Prevent:

Embed Threat Modeling into early software architecture and design phases.

Establish and document secure design patterns, reference architectures, and user story abuse cases.

Enforce business logic constraints (e.g., rate limits on password resets, atomic financial transactions).

Segregate tenants and isolate sensitive internal services at the architectural level.

Attack Scenario:

An e-commerce website designs a voucher redemption system where the user submits a promo code. The developers validate the code correctly, but the architectural design lacks a check to enforce atomic one-time redemption per account. An attacker issues 50 concurrent requests simultaneously, redeeming the same one-time $100 voucher multiple times before the balance counter registers.

A07:2025 – Authentication Failures
Description:

(Refined from Identification and Authentication Failures). Involves flaws that allow attackers to compromise passwords, keys, session tokens, or exploit other implementation flaws to assume other users' identities.

How to Prevent:

Require Multi-Factor Authentication (MFA) for all sensitive actions and administrative portals.

Implement rate limiting, CAPTCHAs, and account lockout/back-off policies against brute-force and credential stuffing attacks.

Use secure, randomly generated session identifiers stored in HttpOnly, Secure, and SameSite cookies.

Invalidate session tokens immediately upon logout or privilege modification.

Attack Scenario:

An application’s login endpoint lacks rate limiting and account lockout mechanisms. An attacker uses a leaked list of millions of username/password pairs to run an automated credential-stuffing script, successfully compromising several user accounts that reused passwords.

A08:2025 – Software and Data Integrity Failures
Description:

Focuses on code and infrastructure that does not protect against integrity violations. This includes deserializing untrusted data without verification, relying on unverified CDNs or plugins, and running unsigned firmware or application update scripts.

How to Prevent:

Use digital signatures to verify that software artifacts, binaries, and updates originate from trusted sources.

Avoid native deserialization formats (e.g., Python pickle, Java ObjectInputStream) for untrusted user inputs; adopt safe serialization formats like JSON or Protocol Buffers.

Use Subresource Integrity (SRI) hashes when including third-party scripts via CDNs.

Attack Scenario:

A web application receives a serialized Java object in a base64-encoded cookie. An attacker crafts a malicious serialized gadget chain payload inside the cookie. When the server automatically deserializes the object upon arrival, arbitrary code executes on the host server (Remote Code Execution).

A09:2025 – Security Logging and Alerting Failures
Description:

Insufficient logging, detection, monitoring, and active alerting. If security-relevant events (such as failed logins, access violations, or server exceptions) are not recorded or analyzed in real time, attackers can persist within systems undetected for months.

How to Prevent:

Ensure all login, access control, and server-side validation failures generate auditable log records with sufficient user/request context.

Prevent logs from recording sensitive data (plain passwords, API keys, PII).

Centralize logs into a SIEM/monitoring service with real-time alerting on suspicious patterns (e.g., multiple access violations from a single IP).

Implement log integrity safeguards to prevent attackers from deleting traces.

Attack Scenario:

An attacker probes an API with thousands of unauthorized IDOR requests trying to find valid user IDs. Because the application logs failed access control checks as normal HTTP 403 responses without triggering an alert or rate-limit flag, the attacker iterates undisturbed until finding and exfiltrating confidential patient data.

A10:2025 – Mishandling of Exceptional Conditions
Description:

A new category in 2025 capturing failures that occur when things go wrong unexpectedly during runtime. This includes "fail-open" logic (granting access or bypassing checks when a database query or auth provider times out), uncaught exceptions exposing internal stack traces, and unhandled race conditions leading to system instability.

How to Prevent:

Enforce "fail-closed / fail-secure" programming patterns—if an authentication or permission check crashes or times out, access must default to denied.

Implement global exception-handling handlers that return generic, friendly error pages while routing raw details to private logs.

Clean up and release system resources (file handles, database locks, memory buffers) inside finally blocks or structured context managers.

Attack Scenario:

An application relies on an external microservice to verify role-based permissions. The developers write a try/except block where, if the external permission service fails or times out, the code logs a warning and proceeds through the pipeline. An attacker overwhelms the auth service with dummy traffic (DoS); when the service times out, the application fails open, granting the attacker unrestricted administrative privileges.