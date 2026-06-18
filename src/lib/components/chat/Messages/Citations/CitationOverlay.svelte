<script lang="ts">
	import { getContext, onDestroy, tick } from 'svelte';
	import { activeCitation } from '$lib/stores';
	import XMark from '$lib/components/icons/XMark.svelte';
	import { fade } from 'svelte/transition';

	const i18n = getContext('i18n');

	$: citation = $activeCitation;

	let chunkElement: HTMLElement | null = null;
	let scrollContainer: HTMLElement | null = null;

	$: if (citation) {
		scrollToChunk();
	}

	async function scrollToChunk() {
		await tick();
		// Wait a small timeout to guarantee Svelte modal transitions and layouts are finalized
		setTimeout(() => {
			if (chunkElement && scrollContainer) {
				const containerRect = scrollContainer.getBoundingClientRect();
				const elementRect = chunkElement.getBoundingClientRect();
				const relativeTop = elementRect.top - containerRect.top + scrollContainer.scrollTop;
				scrollContainer.scrollTop = Math.max(0, relativeTop);
			}
		}, 60);
	}

	function close() {
		activeCitation.set(null);
	}

	const decodeString = (str: string) => {
		try {
			return decodeURIComponent(str);
		} catch (e) {
			return str;
		}
	};

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
		'706': 'Ältere Menschen: Positiv',
		'NA': 'Nicht zugeordnet'
	};

	const MONTH_NAMES = [
		'',
		'Januar',
		'Februar',
		'März',
		'April',
		'Mai',
		'Juni',
		'Juli',
		'August',
		'September',
		'Oktober',
		'November',
		'Dezember'
	];
</script>

{#if citation}
	<!-- Outer overlay/backdrop -->
	<div
		class="absolute inset-0 bg-black/15 dark:bg-black/45 backdrop-blur-[1px] z-50 flex items-center justify-center p-4"
		transition:fade={{ duration: 150 }}
		on:click={close}
	>
		<!-- Floating Card (restricted height, text-width aligned) -->
		<div
			class="bg-white dark:bg-gray-950 border border-gray-150/80 dark:border-gray-850 shadow-2xl rounded-2xl w-full max-w-6xl h-[75vh] max-h-[700px] min-h-[500px] flex flex-col overflow-hidden"
			on:click|stopPropagation
		>
			<!-- Header -->
			<div class="flex items-center justify-between px-6 py-4 border-b border-gray-150/80 dark:border-gray-850 shrink-0">
				<div class="flex items-center gap-3 min-w-0">
					<span class="bg-blue-100 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 text-xs font-bold px-2.5 py-1 rounded-lg shrink-0 border border-blue-200/50 dark:border-blue-800/30">
						{citation.id}
					</span>
					<h2 class="text-lg font-semibold text-gray-800 dark:text-gray-100 truncate">
						{citation.speaker || $i18n.t('Speech')}
					</h2>
					{#if citation.party && citation.party !== 'N/A'}
						<span class="text-xs text-gray-600 dark:text-gray-300 font-semibold px-2.5 py-0.5 bg-gray-100 dark:bg-gray-850 rounded-full shrink-0 border border-gray-200/40 dark:border-gray-800/40">
							{citation.party}
						</span>
					{/if}
				</div>

				<button
					class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-850 transition-colors"
					on:click={close}
					aria-label="Schließen"
				>
					<XMark className="size-6" />
				</button>
			</div>

			<!-- Metadata Subheader -->
			<div class="px-6 py-3 bg-gray-50/55 dark:bg-gray-900/50 border-b border-gray-150/60 dark:border-gray-850/60 flex flex-wrap items-center gap-x-6 gap-y-2 text-xs text-gray-500 dark:text-gray-400 font-medium shrink-0">
				{#if citation.is_manifesto}
					{#if citation.year || citation.month}
						<span class="flex items-center gap-1.5">
							<span class="text-sm opacity-85">📅</span>
							{#if citation.month && MONTH_NAMES[Number(citation.month)]}
								{MONTH_NAMES[Number(citation.month)]} {citation.year || ''}
							{:else}
								{citation.year}
							{/if}
						</span>
					{/if}
					{#if citation.party && citation.party !== 'N/A'}
						<span class="flex items-center gap-1.5">
							<span class="text-sm opacity-85">🗣️</span> Partei: {citation.party}
						</span>
					{/if}
					{#if citation.kapitelroot}
						<span class="flex items-center gap-1.5 max-w-[250px] truncate" title={citation.heading_path || citation.kapitelroot}>
							<span class="text-sm opacity-85">📖</span> Kapitel: {citation.kapitelroot}
						</span>
					{/if}
					{#if citation.score !== null && citation.score !== undefined}
						<span class="text-emerald-600 dark:text-emerald-400 font-semibold flex items-center gap-1.5">
							<span class="text-sm opacity-85">📈</span> Score: {citation.score}
						</span>
					{/if}
					{#if citation.tags && citation.tags.length > 0}
						<span class="flex items-center gap-1.5 flex-wrap ml-1">
							<span class="text-sm opacity-85">🏷️</span> Tags:
							{#each citation.tags as tag}
								<span
									class="px-2 py-0.5 rounded-md text-[10px] font-semibold bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400 border border-blue-150/40 dark:border-blue-800/30 transition-all hover:bg-blue-100 dark:hover:bg-blue-900/40 cursor-help"
									title={CMP_MAP[tag] || CMP_MAP[tag.split('.')[0]] || 'CMP Kategorie'}
								>
									{tag}{#if CMP_MAP[tag] || CMP_MAP[tag.split('.')[0]]}: {CMP_MAP[tag] || CMP_MAP[tag.split('.')[0]]}{/if}
								</span>
							{/each}
						</span>
					{/if}
				{:else}
					{#if citation.date && citation.date !== 'N/A'}
						<span class="flex items-center gap-1.5">
							<span class="text-sm opacity-85">📅</span> {citation.date}
						</span>
					{/if}
					{#if citation.term && citation.term !== 'N/A'}
						<span class="flex items-center gap-1.5">
							<span class="text-sm opacity-85">🏛️</span> WP {citation.term}
						</span>
					{/if}
					{#if citation.session && citation.session !== 'N/A'}
						<span class="flex items-center gap-1.5">
							<span class="text-sm opacity-85">📋</span> Sitzung {citation.session}
						</span>
					{/if}
					{#if citation.speech_id && citation.speech_id !== 'N/A'}
						<span class="flex items-center gap-1.5">
							<span class="text-sm opacity-85">🆔</span> Rede {citation.speech_id}
						</span>
					{/if}
					{#if citation.score !== null && citation.score !== undefined}
						<span class="text-emerald-600 dark:text-emerald-400 font-semibold flex items-center gap-1.5">
							<span class="text-sm opacity-85">📈</span> Score: {citation.score}
						</span>
					{/if}
				{/if}
			</div>

			<!-- Main Content Scroll Area -->
			<div
				bind:this={scrollContainer}
				class="flex-1 overflow-y-auto px-6 py-6 md:px-10 md:py-8 w-full select-text scrollbar-thin"
			>
				{#if citation.full_speech}
					<!-- Before Chunk (muted/grayer text) -->
					{#if citation.full_speech.before}
						<p class="text-gray-400 dark:text-gray-500 leading-relaxed mb-6 whitespace-pre-wrap text-xs font-normal">
							{citation.full_speech.before}
						</p>
					{/if}

					<!-- Relevant Chunk (highlighted, full contrast, separated by spacing) -->
					<div
						bind:this={chunkElement}
						class="my-8 py-5 px-6 border-l-4 border-blue-500 dark:border-blue-400 bg-blue-50/40 dark:bg-blue-950/20 rounded-r-xl shadow-xs"
					>
						<p class="text-gray-900 dark:text-gray-100 leading-relaxed text-sm font-medium whitespace-pre-wrap">
							{citation.full_speech.chunk}
						</p>
					</div>

					<!-- After Chunk (muted/grayer text) -->
					{#if citation.full_speech.after}
						<p class="text-gray-400 dark:text-gray-500 leading-relaxed mt-6 whitespace-pre-wrap text-xs font-normal">
							{citation.full_speech.after}
						</p>
					{/if}
				{:else}
					<!-- Fallback: Standard Citation / Chunk text only -->
					<div
						bind:this={chunkElement}
						class="py-5 px-6 border-l-4 border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/60 rounded-r-xl"
					>
						<p class="text-gray-900 dark:text-gray-100 leading-relaxed text-xs font-medium whitespace-pre-wrap">
							{citation.chunk || (citation.document ? citation.document.join('\n\n') : '') || ''}
						</p>
					</div>
				{/if}
			</div>

			<!-- Footer (Link to original source if available) -->
			{#if citation.doc_url && citation.doc_url !== 'N/A' && citation.doc_url !== ''}
				<div class="px-6 py-4 bg-gray-50/50 dark:bg-gray-900/40 border-t border-gray-100 dark:border-gray-850 flex justify-end shrink-0">
					<a
						href={citation.doc_url}
						target="_blank"
						rel="noopener noreferrer"
						class="flex items-center gap-2 text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 font-medium transition-colors"
					>
						<span>📄 Quelle im Original anzeigen</span>
						<svg class="size-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
						</svg>
					</a>
				</div>
			{/if}
		</div>
	</div>
{/if}
