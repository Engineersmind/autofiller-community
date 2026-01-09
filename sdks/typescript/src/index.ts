/**
 * Autofiller SDK for TypeScript/JavaScript
 *
 * Official client library for the Autofiller Community Edition API.
 *
 * @example
 * ```typescript
 * import { AutofillerClient } from '@autofiller/sdk';
 *
 * const client = new AutofillerClient({
 *   apiKey: process.env.AUTOFILLER_API_KEY
 * });
 *
 * const result = await client.extract({
 *   file: './invoice.pdf',
 *   domainPack: 'invoice-standard'
 * });
 *
 * console.log(result.data);
 * ```
 */

export { AutofillerClient } from './client';
export { AutofillerError, ValidationError, AuthenticationError, RateLimitError } from './errors';
export type {
  AutofillerConfig,
  ExtractOptions,
  ExtractResult,
  ExtractionData,
  ExtractionMetadata,
  JobStatus,
  DomainPack,
  HealthStatus,
} from './types';
