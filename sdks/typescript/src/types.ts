/**
 * SDK Configuration
 */
export interface AutofillerConfig {
  /**
   * API key for authentication.
   * Get your key at https://autofiller.dev
   */
  apiKey: string;

  /**
   * Base URL for the API.
   * @default "https://api.autofiller.dev/v1"
   */
  baseUrl?: string;

  /**
   * Request timeout in milliseconds.
   * @default 30000
   */
  timeout?: number;

  /**
   * Maximum number of retries for failed requests.
   * @default 3
   */
  maxRetries?: number;
}

/**
 * Options for document extraction
 */
export interface ExtractOptions {
  /**
   * Path to the file or a Buffer/Blob containing the document.
   */
  file: string | Buffer | Blob;

  /**
   * Optional filename (required when file is a Buffer/Blob).
   */
  filename?: string;

  /**
   * Domain pack to use for extraction.
   * If omitted, auto-routing will select the best pack.
   */
  domainPack?: string;

  /**
   * Include confidence scores for each extracted field.
   * @default true
   */
  includeConfidence?: boolean;

  /**
   * Include bounding box coordinates for each field.
   * @default false
   */
  includeBoundingBoxes?: boolean;

  /**
   * Document language hint (ISO 639-1 code).
   * @default "en"
   */
  language?: string;
}

/**
 * Options for async extraction
 */
export interface ExtractAsyncOptions extends ExtractOptions {
  /**
   * Webhook URL to receive results when processing completes.
   */
  webhookUrl?: string;
}

/**
 * Extraction result
 */
export interface ExtractResult<T = Record<string, unknown>> {
  /**
   * Unique extraction ID.
   */
  id: string;

  /**
   * Extraction status.
   */
  status: 'completed' | 'partial';

  /**
   * Domain pack used for extraction.
   */
  domainPack: string;

  /**
   * Extracted structured data.
   */
  data: T;

  /**
   * Per-field confidence scores (0-1).
   */
  confidence?: Record<string, number>;

  /**
   * Per-field bounding box coordinates.
   */
  boundingBoxes?: Record<string, BoundingBox>;

  /**
   * Extraction metadata.
   */
  metadata: ExtractionMetadata;

  /**
   * Non-fatal warnings encountered during extraction.
   */
  warnings?: string[];
}

/**
 * Bounding box coordinates
 */
export interface BoundingBox {
  page: number;
  x: number;
  y: number;
  width: number;
  height: number;
}

/**
 * Extraction metadata
 */
export interface ExtractionMetadata {
  /**
   * Total pages in the document.
   */
  pages: number;

  /**
   * Processing time in milliseconds.
   */
  processingTimeMs: number;

  /**
   * Model version used.
   */
  modelVersion: string;

  /**
   * Timestamp when extraction was created.
   */
  createdAt: Date;
}

/**
 * Async job status
 */
export interface JobStatus<T = Record<string, unknown>> {
  /**
   * Job ID.
   */
  jobId: string;

  /**
   * Current status.
   */
  status: 'pending' | 'processing' | 'completed' | 'failed';

  /**
   * Processing progress (0-100).
   */
  progress?: number;

  /**
   * Extraction result (when completed).
   */
  result?: ExtractResult<T>;

  /**
   * Error details (when failed).
   */
  error?: {
    code: string;
    message: string;
  };

  /**
   * Job creation timestamp.
   */
  createdAt: Date;

  /**
   * Job completion timestamp.
   */
  completedAt?: Date;
}

/**
 * Domain pack information
 */
export interface DomainPack {
  /**
   * Pack name/identifier.
   */
  name: string;

  /**
   * Pack version.
   */
  version: string;

  /**
   * Human-readable description.
   */
  description: string;

  /**
   * JSON Schema for extracted data.
   */
  schema: Record<string, unknown>;

  /**
   * Routing configuration.
   */
  routing?: {
    keywords?: string[];
    anchors?: string[];
  };

  /**
   * Supported file formats.
   */
  supportedFormats?: string[];
}

/**
 * Health check response
 */
export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  version: string;
  timestamp: Date;
}

/**
 * Extracted data types for common domain packs
 */
export namespace ExtractionData {
  /**
   * Invoice extraction result
   */
  export interface Invoice {
    vendor_name?: string;
    vendor_address?: string;
    invoice_number?: string;
    invoice_date?: string;
    due_date?: string;
    total_amount?: number;
    currency?: string;
    line_items?: Array<{
      description?: string;
      quantity?: number;
      unit_price?: number;
      amount?: number;
    }>;
    tax_amount?: number;
    subtotal?: number;
  }

  /**
   * W-2 form extraction result
   */
  export interface W2 {
    employee_name?: string;
    employee_ssn?: string;
    employer_name?: string;
    employer_ein?: string;
    wages?: number;
    federal_income_tax_withheld?: number;
    social_security_wages?: number;
    social_security_tax_withheld?: number;
    medicare_wages?: number;
    medicare_tax_withheld?: number;
    tax_year?: number;
  }
}
