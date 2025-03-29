package logger

import (
	"os"

	"github.com/sirupsen/logrus"
)

// Logger is a wrapper around logrus.Logger
type Logger struct {
	*logrus.Logger
}

// NewLogger creates a new logger instance
func NewLogger() *Logger {
	log := logrus.New()

	// Set output to stdout
	log.SetOutput(os.Stdout)

	// Set default level to Info
	log.SetLevel(logrus.InfoLevel)

	// Check environment to set appropriate log level and format
	if os.Getenv("ENVIRONMENT") == "development" {
		log.SetFormatter(&logrus.TextFormatter{
			FullTimestamp: true,
		})

		// Enable more verbose logging in development
		log.SetLevel(logrus.DebugLevel)
	} else {
		// Use JSON formatter for production for better parsing
		log.SetFormatter(&logrus.JSONFormatter{})
	}

	return &Logger{
		Logger: log,
	}
}

// With returns a logger with the specified fields
func (l *Logger) With(fields logrus.Fields) *Logger {
	return &Logger{
		Logger: l.Logger.WithFields(fields).Logger,
	}
}

// Info logs a message at the info level
func (l *Logger) Info(args ...interface{}) {
	l.Logger.Info(args...)
}

// Infof logs a formatted message at the info level
func (l *Logger) Infof(format string, args ...interface{}) {
	l.Logger.Infof(format, args...)
}

// Error logs a message at the error level
func (l *Logger) Error(args ...interface{}) {
	l.Logger.Error(args...)
}

// Errorf logs a formatted message at the error level
func (l *Logger) Errorf(format string, args ...interface{}) {
	l.Logger.Errorf(format, args...)
}

// Warn logs a message at the warn level
func (l *Logger) Warn(args ...interface{}) {
	l.Logger.Warn(args...)
}

// Warnf logs a formatted message at the warn level
func (l *Logger) Warnf(format string, args ...interface{}) {
	l.Logger.Warnf(format, args...)
}

// Debug logs a message at the debug level
func (l *Logger) Debug(args ...interface{}) {
	l.Logger.Debug(args...)
}

// Debugf logs a formatted message at the debug level
func (l *Logger) Debugf(format string, args ...interface{}) {
	l.Logger.Debugf(format, args...)
}

// Fatal logs a message at the fatal level and then exits
func (l *Logger) Fatal(args ...interface{}) {
	l.Logger.Fatal(args...)
}

// Fatalf logs a formatted message at the fatal level and then exits
func (l *Logger) Fatalf(format string, args ...interface{}) {
	l.Logger.Fatalf(format, args...)
}
