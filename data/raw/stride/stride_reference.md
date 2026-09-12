# STRIDE Threat Modeling Reference

## Spoofing

Spoofing is the act of pretending to be another user, service, or system component.

Typical security concern:
- Attacker impersonates a legitimate identity.
- Attacker gains access using stolen or forged credentials.

Examples:
- Stolen user credentials
- Forged authentication tokens
- Impersonating an internal service

---

## Tampering

Tampering involves unauthorized modification of data, messages, configurations, or system state.

Typical security concern:
- An attacker changes information without authorization.

Examples:
- Modifying database records
- Altering data in transit
- Changing application configuration

---

## Repudiation

Repudiation occurs when an actor can deny performing an action and the system lacks sufficient evidence to prove otherwise.

Typical security concern:
- Insufficient logging or auditing makes actions difficult to attribute.

Examples:
- User denies performing a transaction
- Missing audit logs
- Logs that can be modified by unauthorized users

---

## Information Disclosure

Information disclosure occurs when sensitive information is exposed to an unauthorized person or system.

Typical security concern:
- Confidential data becomes accessible to an unintended party.

Examples:
- Exposed passwords
- Leaked personal information
- Sensitive data returned through an API
- Database information exposed through an injection vulnerability

---

## Denial of Service

Denial of Service occurs when an attacker prevents legitimate users from accessing a system or resource.

Typical security concern:
- System availability is degraded or completely disrupted.

Examples:
- Flooding an API with requests
- Exhausting server resources
- Resource exhaustion through expensive operations

---

## Elevation of Privilege

Elevation of Privilege occurs when an attacker gains permissions beyond those they are authorized to have.

Typical security concern:
- A low-privileged user or process gains higher privileges.

Examples:
- Normal user gaining administrator privileges
- Exploiting an authorization vulnerability
- A compromised service accessing restricted resources