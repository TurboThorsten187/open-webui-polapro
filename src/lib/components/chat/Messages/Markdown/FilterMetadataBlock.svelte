<script lang="ts">
	import type { PolaProFilterMetadata } from '$lib/utils/citation-utils';

	export let filterMetadata: PolaProFilterMetadata | null = null;

	const CMP_MAP: Record<string, string> = {
		'101': 'Auslandsbeziehungen: Positiv',
		'102': 'Auslandsbeziehungen: Negativ',
		'103': 'Antimilitarismus',
		'104': 'Militär: Positiv',
		'105': 'Militär: Negativ',
		'106': 'Frieden',
		'107': 'Internationale Kooperation',
		'108': 'Europäische Integration: Positiv',
		'109': 'Europäische Integration: Negativ',
		'110': 'Internationale Sicherheit',
		'201': 'Freiheit und Menschenrechte',
		'202': 'Demokratie',
		'203': 'Verfassungsstaat/Rechtsstaat',
		'204': 'Verfassungsreform',
		'301': 'Dezentralisierung',
		'302': 'Zentralisierung',
		'303': 'Effizienz der Verwaltung',
		'304': 'Korruptionsbekämpfung',
		'305': 'Politisches System: Positiv',
		'401': 'Freie Marktwirtschaft',
		'402': 'Marktregulierung',
		'403': 'Wirtschaftliche Entwicklung',
		'404': 'Infrastruktur/Technologie',
		'405': 'Korporatismus/Sozialpartnerschaft',
		'406': 'Protektionismus: Positiv',
		'407': 'Protektionismus: Negativ',
		'408': 'Wirtschaftliche Ziele',
		'409': 'Verstaatlichung',
		'410': 'Wirtschaftliche Planung',
		'411': 'Technologie und Wissenschaft',
		'412': 'Arbeitnehmerrechte: Positiv',
		'413': 'Arbeitnehmerrechte: Negativ',
		'414': 'Wirtschaftswachstum',
		'415': 'Agrarpolitik',
		'416': 'Verbraucherschutz',
		'501': 'Umweltschutz',
		'502': 'Kultur/Wissenschaft: Positiv',
		'503': 'Gleichheit/Gerechtigkeit',
		'504': 'Sozialstaat: Ausbau',
		'505': 'Sozialstaat: Einschränkung',
		'506': 'Bildungsausbau',
		'507': 'Bildungseinschränkung',
		'601': 'Nationale Lebensweise: Positiv',
		'602': 'Nationale Lebensweise: Negativ',
		'603': 'Traditionelle Moral: Positiv',
		'604': 'Traditionelle Moral: Negativ',
		'605': 'Recht und Ordnung',
		'606': 'Nationaler Zusammenhalt',
		'607': 'Multikulturalismus: Positiv',
		'608': 'Multikulturalismus: Negativ',
		'701': 'Arbeiterschaft: Positiv',
		'702': 'Arbeiterschaft: Negativ',
		'703': 'Landwirte: Positiv',
		'704': 'Mittelstand/Unternehmer: Positiv',
		'705': 'Minderheiten: Positiv',
		'706': 'Ältere Menschen: Positiv'
	};

	const SPEECH_LABELS: Record<string, string> = {
		speakers: 'Redner',
		parties: 'Fraktionen',
		roles: 'Rollen',
		speech_id: 'Speech-ID',
		electoral_term: 'Wahlperiode',
		session: 'Sitzung',
		date: 'Datum',
		date_range: 'Zeitraum',
		date_unix: 'Datum (Unix)'
	};

	const MANIFESTO_LABELS: Record<string, string> = {
		manifesto_parties: 'Parteien',
		manifesto_year_range: 'Zeitraum',
		manifesto_themes: 'Themen'
	};

	$: hasSpeechFilters =
		filterMetadata !== null &&
		Object.keys(SPEECH_LABELS).some((key) => {
			const val = (filterMetadata as any)?.[key];
			return val !== undefined && val !== null;
		});

	$: hasManifestoFilters =
		filterMetadata !== null &&
		Object.keys(MANIFESTO_LABELS).some((key) => {
			const val = (filterMetadata as any)?.[key];
			return val !== undefined && val !== null;
		});

	$: hasFilters = hasSpeechFilters || hasManifestoFilters;
	$: filtersActive = filterMetadata?.filters_active ?? false;

	function formatValue(key: string, value: any): string {
		if (key === 'manifesto_themes' && Array.isArray(value)) {
			return value
				.map((code) => {
					const label = CMP_MAP[String(code)];
					return label ? `${code} (${label})` : String(code);
				})
				.join(', ');
		}
		if (Array.isArray(value)) {
			return value.join(', ');
		}
		return String(value);
	}
</script>

{#if hasFilters && filterMetadata}
	<details class="polapro-filter-metadata">
		<summary class="polapro-filter-summary">
			<svg class="polapro-filter-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
				/>
			</svg>
			<span class="polapro-filter-title">Filterparameter</span>
			<span class="polapro-filter-status" class:polapro-filter-active={filtersActive}>
				{filtersActive ? 'aktiv' : 'nicht angewandt'}
			</span>
			<svg class="polapro-filter-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M19 9l-7 7-7-7"
				/>
			</svg>
		</summary>
		<div class="polapro-filter-content">
			<div class="polapro-filter-grid" class:double-column={hasSpeechFilters && hasManifestoFilters}>
				<!-- Speech Filters Column -->
				{#if hasSpeechFilters}
					<div class="polapro-filter-column">
						<div class="polapro-column-header">Bundestagsreden</div>
						<div class="polapro-rows">
							{#each Object.entries(SPEECH_LABELS) as [key, label]}
								{@const value = filterMetadata[key]}
								{#if value !== undefined && value !== null}
									<div class="polapro-filter-row">
										<span class="polapro-filter-label">{label}</span>
										<span class="polapro-filter-value">{formatValue(key, value)}</span>
									</div>
								{/if}
							{/each}
						</div>
					</div>
				{/if}

				<!-- Manifesto Filters Column -->
				{#if hasManifestoFilters}
					<div class="polapro-filter-column">
						<div class="polapro-column-header">Wahlprogramme</div>
						<div class="polapro-rows">
							{#each Object.entries(MANIFESTO_LABELS) as [key, label]}
								{@const value = filterMetadata[key]}
								{#if value !== undefined && value !== null}
									<div class="polapro-filter-row">
										<span class="polapro-filter-label">{label}</span>
										<span class="polapro-filter-value">{formatValue(key, value)}</span>
									</div>
								{/if}
							{/each}
						</div>
					</div>
				{/if}
			</div>
		</div>
	</details>
{/if}

<style>
	/* ────────────────────────────────────────────────────────────────
	   PoLaPro Filter Metadata Block
	   Collapsible display of extracted RAG filter parameters
	   Theme-aware: light-mode default, dark via :global(.dark)
	   ──────────────────────────────────────────────────────────────── */

	.polapro-filter-metadata {
		margin-top: 1rem;
		border: 1px solid #e2e8f0;
		border-radius: 10px;
		overflow: hidden;
		font-size: 0.8125rem;
		background: #f8fafc;
		transition: border-color 0.2s;
	}
	:global(.dark) .polapro-filter-metadata {
		background: rgba(255, 255, 255, 0.03);
		border-color: #3b3b3b;
	}

	.polapro-filter-metadata[open] {
		border-color: #cbd5e1;
	}
	:global(.dark) .polapro-filter-metadata[open] {
		border-color: #4b4b4b;
	}

	/* ── Summary (clickable header) ── */
	.polapro-filter-summary {
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 10px 14px;
		cursor: pointer;
		user-select: none;
		color: #475569;
		transition: background 0.15s, color 0.15s;
		list-style: none;
	}
	.polapro-filter-summary::-webkit-details-marker {
		display: none;
	}
	.polapro-filter-summary::marker {
		display: none;
		content: '';
	}
	.polapro-filter-summary:hover {
		background: rgba(0, 0, 0, 0.03);
	}
	:global(.dark) .polapro-filter-summary {
		color: #94a3b8;
	}
	:global(.dark) .polapro-filter-summary:hover {
		background: rgba(255, 255, 255, 0.04);
	}

	.polapro-filter-icon {
		width: 16px;
		height: 16px;
		flex-shrink: 0;
		opacity: 0.7;
	}

	.polapro-filter-title {
		font-weight: 600;
		font-size: 0.8125rem;
	}

	.polapro-filter-status {
		font-size: 0.7rem;
		padding: 1px 8px;
		border-radius: 999px;
		background: rgba(234, 179, 8, 0.12);
		color: #a16207;
		font-weight: 500;
	}
	:global(.dark) .polapro-filter-status {
		background: rgba(234, 179, 8, 0.1);
		color: #facc15;
	}

	.polapro-filter-status.polapro-filter-active {
		background: rgba(22, 163, 74, 0.1);
		color: #15803d;
	}
	:global(.dark) .polapro-filter-status.polapro-filter-active {
		background: rgba(22, 163, 74, 0.12);
		color: #4ade80;
	}

	.polapro-filter-chevron {
		width: 14px;
		height: 14px;
		margin-left: auto;
		flex-shrink: 0;
		opacity: 0.5;
		transition: transform 0.2s ease;
	}
	.polapro-filter-metadata[open] .polapro-filter-chevron {
		transform: rotate(180deg);
	}

	/* ── Content (filter rows) ── */
	.polapro-filter-content {
		padding: 8px 14px 12px;
		border-top: 1px solid #e2e8f0;
	}
	:global(.dark) .polapro-filter-content {
		border-top-color: #3b3b3b;
	}

	.polapro-filter-grid {
		display: grid;
		grid-template-columns: 1fr;
		gap: 1rem;
	}
	.polapro-filter-grid.double-column {
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 1.5rem;
	}

	.polapro-filter-column {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.polapro-column-header {
		font-size: 0.7rem;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: #64748b;
		border-bottom: 1px solid #cbd5e1;
		padding-bottom: 0.25rem;
		margin-bottom: 0.25rem;
	}
	:global(.dark) .polapro-column-header {
		color: #94a3b8;
		border-bottom-color: #4b4b4b;
	}

	.polapro-rows {
		display: flex;
		flex-direction: column;
		gap: 6px;
	}

	.polapro-filter-row {
		display: flex;
		align-items: baseline;
		gap: 8px;
	}

	.polapro-filter-label {
		font-weight: 600;
		color: #64748b;
		min-width: 90px;
		flex-shrink: 0;
		font-size: 0.75rem;
	}
	:global(.dark) .polapro-filter-label {
		color: #94a3b8;
	}

	.polapro-filter-value {
		color: #1e293b;
		font-size: 0.8125rem;
	}
	:global(.dark) .polapro-filter-value {
		color: #e2e8f0;
	}
</style>
