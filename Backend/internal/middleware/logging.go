package middleware

import (
	"net/http"
	"time"

	"github.com/karolk75/PiChat/Backend/pkg/logger"
	"github.com/sirupsen/logrus"
)

// LoggingMiddleware logs HTTP requests
func LoggingMiddleware(log *logger.Logger) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			start := time.Now()

			// Create a custom response writer to capture the status code
			rw := &responseWriter{
				ResponseWriter: w,
				statusCode:     http.StatusOK, // Default to 200 OK
			}

			// Process the request
			next.ServeHTTP(rw, r)

			// Log the request details after it's processed
			duration := time.Since(start)
			log.With(logrus.Fields{
				"method":     r.Method,
				"path":       r.URL.Path,
				"status":     rw.statusCode,
				"duration":   duration.String(),
				"user_agent": r.UserAgent(),
				"remote_ip":  r.RemoteAddr,
			}).Info("HTTP request")
		})
	}
}

// responseWriter is a custom response writer that captures the status code
type responseWriter struct {
	http.ResponseWriter
	statusCode int
}

// WriteHeader captures the status code before writing it
func (rw *responseWriter) WriteHeader(code int) {
	rw.statusCode = code
	rw.ResponseWriter.WriteHeader(code)
}
