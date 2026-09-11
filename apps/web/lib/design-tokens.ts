/**
 * DESIGN TOKENS — typography conventions for ProjectPulse AI.
 *
 * Central reference for the repeated text styles used across the
 * "command center" UI. Every convention is a plain string of composable
 * Tailwind utilities. Import and spread/apply these constants instead of
 * re-typing utility strings so the system stays consistent.
 */

/**
 * Page titles — "NATIONAL ASSETS", "PAIMANA COMMAND CENTER", etc.
 * Uppercase, extra-bold, tight tracking.
 *
 *  text-2xl md:text-3xl font-extrabold uppercase tracking-tight text-text-primary
 */
export const pageTitle =
  'text-2xl md:text-3xl font-extrabold uppercase tracking-tight text-text-primary'

/**
 * Section card titles — "Portfolio Risk Matrix", "Top Risk Drivers", etc.
 *
 *  text-lg font-semibold text-text-primary
 */
export const sectionTitle = 'text-lg font-semibold text-text-primary'

/**
 * Eyebrow / label pills — "STRATEGIC OVERVIEW", "CRITICAL RISK", etc.
 * Pairs with the <Badge /> component for chip-style headers.
 *
 *  text-xs font-bold uppercase tracking-wider
 */
export const eyebrow = 'text-xs font-bold uppercase tracking-wider'

/**
 * Technical / ID text — asset IDs, timestamps, "LIVE_UPDATE:" readouts.
 * Monospace, small, muted.
 *
 *  font-mono text-xs text-text-muted
 */
export const technical = 'font-mono text-xs text-text-muted'

/**
 * Big stat numbers — "1,775", "14.2K Cr", etc. Monospace so digits align.
 *
 *  text-3xl font-bold font-mono text-text-primary
 */
export const statNumber = 'text-3xl font-bold font-mono text-text-primary'