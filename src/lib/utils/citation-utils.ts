/**
 * PoLaPro Citation Utilities
 *
 * Extracts structured citation metadata from the hidden HTML-comment block
 * that the PoLaPro RAG backend appends to every response.
 *
 * Format:  <!-- CITATION_DATA\n[...JSON...]\n-->
 * Format:  <!-- FILTER_METADATA\n{...JSON...}\n-->
 */

export interface PolaProCitation {
	id: number;
	chunk: string;
	speaker: string;
	party: string;
	date: string;
	term: string | number;
	session: string | number;
	speech_id: string | number;
	score: number | null;
	doc_url: string;
}

export interface PolaProFilterMetadata {
	filters_active: boolean;
	speakers?: string[];
	parties?: string[];
	roles?: string[];
	speech_id?: string | number;
	electoral_term?: string | number;
	session?: string | number;
	date?: string;
	date_range?: string;
	date_unix?: number;
	[key: string]: any;
}

/**
 * Extracts PoLaPro citation metadata and filter metadata from hidden
 * HTML comment blocks appended by the RAG backend.
 *
 * Returns the citation array, filter metadata, **and** the content with
 * both blocks stripped so they never reach the Markdown renderer.
 */
export function extractCitationData(content: string): {
	cleanContent: string;
	citations: PolaProCitation[];
	filterMetadata: PolaProFilterMetadata | null;
} {
	const citationRegex = /\n*<!-- CITATION_DATA\n([\s\S]*?)\n-->/;
	const filterRegex = /\n*<!-- FILTER_METADATA\n([\s\S]*?)\n-->/;

	let citations: PolaProCitation[] = [];
	let filterMetadata: PolaProFilterMetadata | null = null;

	// Extract citations
	const citationMatch = content.match(citationRegex);
	if (citationMatch) {
		try {
			citations = JSON.parse(citationMatch[1]);
		} catch (e) {
			console.error('[PoLaPro] Failed to parse citation data:', e);
		}
	}

	// Extract filter metadata
	const filterMatch = content.match(filterRegex);
	if (filterMatch) {
		try {
			filterMetadata = JSON.parse(filterMatch[1]);
		} catch (e) {
			console.error('[PoLaPro] Failed to parse filter metadata:', e);
		}
	}

	// Strip both blocks from the content
	let cleanContent = content.replace(citationRegex, '').replace(filterRegex, '');

	return { cleanContent, citations, filterMetadata };
}
