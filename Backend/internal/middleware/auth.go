package middleware

import (
	"net/http"
)

// AuthMiddleware provides authentication middleware
type AuthMiddleware struct {
	apiToken string
}

// NewAuthMiddleware creates a new auth middleware
func NewAuthMiddleware(apiToken string) *AuthMiddleware {
	return &AuthMiddleware{
		apiToken: apiToken,
	}
}

// Authenticate is a middleware that checks for valid authentication
func (am *AuthMiddleware) Authenticate(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		// Get token from query string (for WebSocket) or Authorization header
		token := r.URL.Query().Get("token")

		// If token not in query, check header
		if token == "" {
			token = r.Header.Get("Authorization")
		}

		// If token not present or invalid, return unauthorized
		if token == "" || token != am.apiToken {
			http.Error(w, "Unauthorized", http.StatusUnauthorized)
			return
		}

		// Token valid, call the next handler
		next(w, r)
	}
}
