# Multi-User Authentication

**Status**: backlog
**Milestone**: M5-Scaling
**Priority**: nice-to-have
**Depends on**: [rest-api](../implemented/rest-api.md), [database-migrations](../planned/database-migrations.md)

## Summary

JWT-based authentication system with user profiles, role-based access control (admin/user/read-only), personalized feeds, and bookmarks, enabling shared instances for multiple users.

## User Stories

- As an admin, I want to manage user accounts and permissions
- As a user, I want my own personalized feed configuration separate from other users
- As a user, I want to bookmark articles for later reading
- As a read-only user, I want to browse news without modifying sources

## Requirements

### Functional

- [ ] User registration and login
- [ ] JWT token authentication with refresh tokens
- [ ] Role-based access: admin (full), user (own config), read-only (browse only)
- [ ] User profiles with personal preferences
- [ ] Per-user feed source configuration
- [ ] Bookmarks and saved articles per user
- [ ] Reading history per user
- [ ] Admin panel for user management

### Non-Functional

- Security: Passwords hashed with bcrypt, JWT with short expiration
- Privacy: User data encrypted at rest
- Scalability: Multi-tenant database schema

## Technical Notes

- Authentication: JWT tokens (access + refresh)
  - Access token: 15-minute expiration
  - Refresh token: 7-day expiration
- Password storage: bcrypt hashing
- Optional future: OAuth2 for third-party login (GitHub, Google)
- Database changes:
  - `Users` table: id, email, password_hash, role, created_at
  - `UserPreferences` table: user_id, settings JSON
  - `Bookmarks` table: user_id, news_id, created_at
  - Foreign key on Sources to User (or shared sources)
- Middleware: JWT verification on protected endpoints
- Requires [database-migrations](../planned/database-migrations.md) for schema changes
- See roadmap.md M5 for full scaling infrastructure plans

## Open Questions

- Shared sources (visible to all) vs per-user sources only?
- Self-registration vs admin-only account creation?
- OAuth2 providers to support

## Acceptance Criteria

- [ ] Users can register and log in
- [ ] JWT authentication works on all protected endpoints
- [ ] Roles correctly restrict access (admin, user, read-only)
- [ ] Each user has independent source configuration
- [ ] Bookmarks are persisted per user
- [ ] Passwords are securely hashed
