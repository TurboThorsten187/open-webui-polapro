/**
 * PoLaPro Citation Utilities
 *
 * Extracts structured citation metadata from the hidden HTML-comment block
 * that the PoLaPro RAG backend appends to every response.
 *
 * Format:  <!-- CITATION_DATA\n[...JSON...]\n-->
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

/**
 * Extracts PoLaPro citation metadata from a hidden HTML comment block
 * appended by the RAG backend.
 *
 * Returns the citation array **and** the content with the block stripped
 * so it never reaches the Markdown renderer.
 */
export function extractCitationData(content: string): {
	cleanContent: string;
	citations: PolaProCitation[];
} {
	const regex = /\n*<!-- CITATION_DATA\n([\s\S]*?)\n-->/;
	const match = content.match(regex);

	if (!match) {
		return { cleanContent: content, citations: [] };
	}

	let citations: PolaProCitation[] = [];
	try {
		citations = JSON.parse(match[1]);
	} catch (e) {
		console.error('[PoLaPro] Failed to parse citation data:', e);
	}

	const cleanContent = content.replace(regex, '');
	return { cleanContent, citations };
}
