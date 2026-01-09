import * as fs from 'fs';
import * as path from 'path';
import FormData from 'form-data';
import {
  AutofillerConfig,
  ExtractOptions,
  ExtractAsyncOptions,
  ExtractResult,
  JobStatus,
  DomainPack,
  HealthStatus,
} from './types';
import {
  AutofillerError,
  AuthenticationError,
  RateLimitError,
  ValidationError,
} from './errors';

const DEFAULT_BASE_URL = 'https://api.autofiller.dev/v1';
const DEFAULT_TIMEOUT = 30000;
const DEFAULT_MAX_RETRIES = 3;

/**
 * Autofiller API Client
 *
 * @example
 * ```typescript
 * const client = new AutofillerClient({
 *   apiKey: 'your-api-key'
 * });
 *
 * // Synchronous extraction
 * const result = await client.extract({
 *   file: './invoice.pdf',
 *   domainPack: 'invoice-standard'
 * });
 *
 * // Async extraction with polling
 * const job = await client.extractAsync({ file: './large-doc.pdf' });
 * const finalResult = await client.waitForJob(job.jobId);
 * ```
 */
export class AutofillerClient {
  private readonly config: Required<AutofillerConfig>;

  constructor(config: AutofillerConfig) {
    if (!config.apiKey) {
      throw new ValidationError('API key is required');
    }

    this.config = {
      apiKey: config.apiKey,
      baseUrl: config.baseUrl ?? DEFAULT_BASE_URL,
      timeout: config.timeout ?? DEFAULT_TIMEOUT,
      maxRetries: config.maxRetries ?? DEFAULT_MAX_RETRIES,
    };
  }

  /**
   * Check API health status
   */
  async health(): Promise<HealthStatus> {
    const response = await this.request<{
      status: string;
      version: string;
      timestamp: string;
    }>('/health', { method: 'GET', auth: false });

    return {
      status: response.status as HealthStatus['status'],
      version: response.version,
      timestamp: new Date(response.timestamp),
    };
  }

  /**
   * Extract data from a document (synchronous)
   *
   * Use this for small documents (<10 pages). For larger documents,
   * use `extractAsync()`.
   */
  async extract<T = Record<string, unknown>>(
    options: ExtractOptions
  ): Promise<ExtractResult<T>> {
    const formData = await this.buildFormData(options);

    const response = await this.request<ApiExtractionResult>(
      '/extract',
      {
        method: 'POST',
        body: formData,
        headers: formData.getHeaders(),
      }
    );

    return this.transformExtractionResult<T>(response);
  }

  /**
   * Start async extraction job
   *
   * Use this for large documents or when you want webhook notifications.
   */
  async extractAsync(
    options: ExtractAsyncOptions
  ): Promise<{ jobId: string; status: 'pending'; estimatedTimeSeconds?: number }> {
    const formData = await this.buildFormData(options);

    if (options.webhookUrl) {
      formData.append('webhook_url', options.webhookUrl);
    }

    const response = await this.request<{
      job_id: string;
      status: string;
      estimated_time_seconds?: number;
    }>('/extract/async', {
      method: 'POST',
      body: formData,
      headers: formData.getHeaders(),
    });

    return {
      jobId: response.job_id,
      status: 'pending',
      estimatedTimeSeconds: response.estimated_time_seconds,
    };
  }

  /**
   * Get job status
   */
  async getJob<T = Record<string, unknown>>(jobId: string): Promise<JobStatus<T>> {
    const response = await this.request<ApiJobStatus>(`/jobs/${jobId}`, {
      method: 'GET',
    });

    return this.transformJobStatus<T>(response);
  }

  /**
   * Wait for a job to complete (polling)
   *
   * @param jobId - Job ID to wait for
   * @param pollInterval - Polling interval in ms (default: 2000)
   * @param maxWait - Maximum wait time in ms (default: 300000 = 5 minutes)
   */
  async waitForJob<T = Record<string, unknown>>(
    jobId: string,
    pollInterval = 2000,
    maxWait = 300000
  ): Promise<ExtractResult<T>> {
    const startTime = Date.now();

    while (Date.now() - startTime < maxWait) {
      const job = await this.getJob<T>(jobId);

      if (job.status === 'completed' && job.result) {
        return job.result;
      }

      if (job.status === 'failed') {
        throw new AutofillerError(
          job.error?.message ?? 'Job failed',
          job.error?.code ?? 'job_failed'
        );
      }

      await this.sleep(pollInterval);
    }

    throw new AutofillerError(
      'Job timed out waiting for completion',
      'job_timeout'
    );
  }

  /**
   * List available domain packs
   */
  async listDomainPacks(): Promise<DomainPack[]> {
    const response = await this.request<{ items: ApiDomainPack[] }>(
      '/domain-packs',
      { method: 'GET' }
    );

    return response.items.map(this.transformDomainPack);
  }

  /**
   * Get domain pack details
   */
  async getDomainPack(packName: string): Promise<DomainPack> {
    const response = await this.request<ApiDomainPack>(
      `/domain-packs/${packName}`,
      { method: 'GET' }
    );

    return this.transformDomainPack(response);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Private helpers
  // ─────────────────────────────────────────────────────────────────────────────

  private async buildFormData(options: ExtractOptions): Promise<FormData> {
    const formData = new FormData();

    // Handle file input
    if (typeof options.file === 'string') {
      // File path
      const filePath = path.resolve(options.file);
      const filename = options.filename ?? path.basename(filePath);
      formData.append('file', fs.createReadStream(filePath), filename);
    } else if (Buffer.isBuffer(options.file)) {
      // Buffer
      if (!options.filename) {
        throw new ValidationError('filename is required when file is a Buffer');
      }
      formData.append('file', options.file, options.filename);
    } else {
      // Blob (browser)
      formData.append('file', options.file, options.filename ?? 'document');
    }

    if (options.domainPack) {
      formData.append('domain_pack', options.domainPack);
    }

    // Options
    const extractOptions: Record<string, unknown> = {};
    if (options.includeConfidence !== undefined) {
      extractOptions.include_confidence = options.includeConfidence;
    }
    if (options.includeBoundingBoxes !== undefined) {
      extractOptions.include_bounding_boxes = options.includeBoundingBoxes;
    }
    if (options.language) {
      extractOptions.language = options.language;
    }

    if (Object.keys(extractOptions).length > 0) {
      formData.append('options', JSON.stringify(extractOptions));
    }

    return formData;
  }

  private async request<T>(
    endpoint: string,
    options: {
      method: 'GET' | 'POST' | 'PUT' | 'DELETE';
      body?: FormData | Record<string, unknown>;
      headers?: Record<string, string>;
      auth?: boolean;
    }
  ): Promise<T> {
    const { method, body, headers = {}, auth = true } = options;

    const url = `${this.config.baseUrl}${endpoint}`;

    const requestHeaders: Record<string, string> = {
      ...headers,
    };

    if (auth) {
      requestHeaders['Authorization'] = `Bearer ${this.config.apiKey}`;
    }

    let requestBody: BodyInit | undefined;
    if (body instanceof FormData) {
      requestBody = body as unknown as BodyInit;
    } else if (body) {
      requestHeaders['Content-Type'] = 'application/json';
      requestBody = JSON.stringify(body);
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

    try {
      const response = await fetch(url, {
        method,
        headers: requestHeaders,
        body: requestBody,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        await this.handleErrorResponse(response);
      }

      return (await response.json()) as T;
    } catch (error) {
      clearTimeout(timeoutId);

      if (error instanceof AutofillerError) {
        throw error;
      }

      if (error instanceof Error && error.name === 'AbortError') {
        throw new AutofillerError('Request timed out', 'timeout');
      }

      throw new AutofillerError(
        `Request failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        'request_failed'
      );
    }
  }

  private async handleErrorResponse(response: Response): Promise<never> {
    let errorData: { code?: string; message?: string } = {};

    try {
      errorData = await response.json();
    } catch {
      // Ignore JSON parse errors
    }

    const message = errorData.message ?? response.statusText;
    const code = errorData.code ?? `http_${response.status}`;

    switch (response.status) {
      case 401:
        throw new AuthenticationError(message);
      case 429:
        throw new RateLimitError(message);
      case 400:
      case 422:
        throw new ValidationError(message);
      default:
        throw new AutofillerError(message, code);
    }
  }

  private transformExtractionResult<T>(response: ApiExtractionResult): ExtractResult<T> {
    return {
      id: response.id,
      status: response.status as ExtractResult['status'],
      domainPack: response.domain_pack,
      data: response.data as T,
      confidence: response.confidence,
      boundingBoxes: response.bounding_boxes,
      metadata: {
        pages: response.metadata?.pages ?? 0,
        processingTimeMs: response.metadata?.processing_time_ms ?? 0,
        modelVersion: response.metadata?.model_version ?? 'unknown',
        createdAt: new Date(response.metadata?.created_at ?? Date.now()),
      },
      warnings: response.warnings,
    };
  }

  private transformJobStatus<T>(response: ApiJobStatus): JobStatus<T> {
    return {
      jobId: response.job_id,
      status: response.status as JobStatus['status'],
      progress: response.progress,
      result: response.result
        ? this.transformExtractionResult<T>(response.result)
        : undefined,
      error: response.error,
      createdAt: new Date(response.created_at),
      completedAt: response.completed_at
        ? new Date(response.completed_at)
        : undefined,
    };
  }

  private transformDomainPack(pack: ApiDomainPack): DomainPack {
    return {
      name: pack.name,
      version: pack.version,
      description: pack.description,
      schema: pack.schema,
      routing: pack.routing,
      supportedFormats: pack.supported_formats,
    };
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

// API response types (snake_case)
interface ApiExtractionResult {
  id: string;
  status: string;
  domain_pack: string;
  data: Record<string, unknown>;
  confidence?: Record<string, number>;
  bounding_boxes?: Record<string, { page: number; x: number; y: number; width: number; height: number }>;
  metadata?: {
    pages?: number;
    processing_time_ms?: number;
    model_version?: string;
    created_at?: string;
  };
  warnings?: string[];
}

interface ApiJobStatus {
  job_id: string;
  status: string;
  progress?: number;
  result?: ApiExtractionResult;
  error?: { code: string; message: string };
  created_at: string;
  completed_at?: string;
}

interface ApiDomainPack {
  name: string;
  version: string;
  description: string;
  schema: Record<string, unknown>;
  routing?: { keywords?: string[]; anchors?: string[] };
  supported_formats?: string[];
}
