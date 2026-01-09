/**
 * Base error class for Autofiller SDK
 */
export class AutofillerError extends Error {
  /**
   * Machine-readable error code
   */
  readonly code: string;

  constructor(message: string, code: string) {
    super(message);
    this.name = 'AutofillerError';
    this.code = code;

    // Maintains proper stack trace for where our error was thrown (only available on V8)
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, this.constructor);
    }
  }
}

/**
 * Thrown when request validation fails (400, 422)
 */
export class ValidationError extends AutofillerError {
  constructor(message: string) {
    super(message, 'validation_error');
    this.name = 'ValidationError';
  }
}

/**
 * Thrown when authentication fails (401)
 */
export class AuthenticationError extends AutofillerError {
  constructor(message: string = 'Invalid or missing API key') {
    super(message, 'authentication_error');
    this.name = 'AuthenticationError';
  }
}

/**
 * Thrown when rate limit is exceeded (429)
 */
export class RateLimitError extends AutofillerError {
  constructor(message: string = 'Rate limit exceeded') {
    super(message, 'rate_limit_exceeded');
    this.name = 'RateLimitError';
  }
}

/**
 * Thrown when document processing fails
 */
export class ExtractionError extends AutofillerError {
  constructor(message: string, code: string = 'extraction_failed') {
    super(message, code);
    this.name = 'ExtractionError';
  }
}
