package validator

import (
	"fmt"
	"regexp"
)

// Validator provides basic validation functions
type Validator struct{}

// NewValidator creates a new validator
func NewValidator() *Validator {
	return &Validator{}
}

// ValidateUUID validates a UUID string
func (v *Validator) ValidateUUID(uuid string) bool {
	r := regexp.MustCompile(`^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$`)
	return r.MatchString(uuid)
}

// ValidateEmail validates an email address
func (v *Validator) ValidateEmail(email string) bool {
	r := regexp.MustCompile(`^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$`)
	return r.MatchString(email)
}

// ValidateNonEmpty validates that a string is not empty
func (v *Validator) ValidateNonEmpty(value string, fieldName string) error {
	if value == "" {
		return fmt.Errorf("%s cannot be empty", fieldName)
	}
	return nil
}

// ValidateMaxLength validates that a string doesn't exceed a maximum length
func (v *Validator) ValidateMaxLength(value string, maxLength int, fieldName string) error {
	if len(value) > maxLength {
		return fmt.Errorf("%s exceeds maximum length of %d characters", fieldName, maxLength)
	}
	return nil
}

// ValidateMinLength validates that a string meets a minimum length
func (v *Validator) ValidateMinLength(value string, minLength int, fieldName string) error {
	if len(value) < minLength {
		return fmt.Errorf("%s must be at least %d characters long", fieldName, minLength)
	}
	return nil
}
