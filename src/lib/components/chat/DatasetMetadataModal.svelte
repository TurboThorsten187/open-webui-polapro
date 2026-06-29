<script lang="ts">
	import { getContext } from 'svelte';
	import Modal from '$lib/components/common/Modal.svelte';
	import XMark from '$lib/components/icons/XMark.svelte';

	const i18n = getContext('i18n');

	export let show = false;
	export let metadata: {
		speeches: {
			last_speech_date: string;
			meta: any;
		};
		manifestos: {
			last_manifesto_year: string | number;
			meta: any;
		};
	};

	let activeTab: 'overview' | 'speeches' | 'manifestos' = 'overview';

	const formatNumber = (num: number | undefined) => {
		if (num === undefined) return '0';
		return num.toLocaleString('de-DE');
	};

	const formatDuration = (seconds: number | undefined) => {
		if (seconds === undefined) return 'N/A';
		const hrs = Math.floor(seconds / 3600);
		const mins = Math.floor((seconds % 3600) / 60);
		const secs = Math.round(seconds % 60);
		let out = '';
		if (hrs > 0) out += `${hrs}h `;
		if (mins > 0 || hrs > 0) out += `${mins}m `;
		out += `${secs}s`;
		return out;
	};

	const formatDateTime = (isoString: string | undefined) => {
		if (!isoString) return 'N/A';
		try {
			const dt = new Date(isoString);
			return dt.toLocaleString('de-DE', { dateStyle: 'medium', timeStyle: 'short' });
		} catch {
			return isoString;
		}
	};

	const formatPercent = (val: number | undefined) => {
		if (val === undefined) return 'N/A';
		return `${(val * 100).toFixed(2)}%`;
	};

	// Extracts speech data safely
	$: speechMeta = metadata?.speeches?.meta || {};
	$: speechStats = speechMeta?.stats || {};
	$: speechSuccess = speechMeta?.success ?? false;

	// Extracts manifesto data safely
	$: manifestoMeta = metadata?.manifestos?.meta || {};
	$: manifestoStats = manifestoMeta?.stats || {};
	$: manifestoParams = manifestoMeta?.parameters || {};
	$: manifestoSuccess = manifestoMeta?.success ?? false;
</script>

<Modal bind:show size="lg" className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-100 dark:border-gray-800">
	<div class="flex flex-col h-full max-h-[85dvh] text-gray-800 dark:text-gray-100">
		<!-- Header -->
		<div class="flex justify-between items-center px-6 py-4 border-b border-gray-100 dark:border-gray-800">
			<div class="flex items-center gap-2">
				<div class="size-2.5 rounded-full bg-emerald-500 animate-pulse" />
				<h2 class="text-xl font-semibold tracking-tight font-medium">Datenbestand & Pipeline-Status</h2>
			</div>
			<button
				class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition"
				aria-label="Close"
				on:click={() => (show = false)}
			>
				<XMark className="size-6" />
			</button>
		</div>

		<!-- Navigation Tabs -->
		<div class="flex border-b border-gray-100 dark:border-gray-800 px-6 bg-gray-50/50 dark:bg-gray-950/20">
			<button
				class="py-3 px-4 text-sm font-medium border-b-2 transition-all -mb-px {activeTab === 'overview'
					? 'border-blue-600 dark:border-blue-400 text-blue-600 dark:text-blue-400 font-semibold'
					: 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'}"
				on:click={() => (activeTab = 'overview')}
			>
				Übersicht
			</button>
			<button
				class="py-3 px-4 text-sm font-medium border-b-2 transition-all -mb-px {activeTab === 'speeches'
					? 'border-blue-600 dark:border-blue-400 text-blue-600 dark:text-blue-400 font-semibold'
					: 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'}"
				on:click={() => (activeTab = 'speeches')}
			>
				Bundestagsreden
			</button>
			<button
				class="py-3 px-4 text-sm font-medium border-b-2 transition-all -mb-px {activeTab === 'manifestos'
					? 'border-blue-600 dark:border-blue-400 text-blue-600 dark:text-blue-400 font-semibold'
					: 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'}"
				on:click={() => (activeTab = 'manifestos')}
			>
				Wahlprogramme
			</button>
		</div>

		<!-- Scrollable Content -->
		<div class="flex-1 overflow-y-auto p-6 space-y-6">
			{#if activeTab === 'overview'}
				<!-- Dashboard Overview -->
				<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
					<!-- Speeches Summary Card -->
					<div class="p-5 rounded-xl border border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-900/30 flex flex-col justify-between">
						<div>
							<div class="flex justify-between items-start mb-3">
								<h3 class="font-semibold text-base text-gray-900 dark:text-gray-100 font-medium">Reden (Bundestag)</h3>
								<span class="px-2.5 py-0.5 rounded-full text-xs font-semibold {speechSuccess ? 'bg-emerald-55 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-400' : 'bg-red-50 text-red-700 dark:bg-red-500/10 dark:text-red-400'}">
									{speechSuccess ? 'Aktiv' : 'Inaktiv'}
								</span>
							</div>
							<div class="space-y-2 text-sm text-gray-600 dark:text-gray-300">
								<div class="flex justify-between"><span class="text-gray-400">Datenstand:</span> <span class="font-medium text-gray-900 dark:text-white">{metadata?.speeches?.last_speech_date || 'Unbekannt'}</span></div>
								<div class="flex justify-between"><span class="text-gray-400">Anzahl Reden:</span> <span class="font-medium text-gray-900 dark:text-white">{formatNumber(speechStats?.speeches_count)}</span></div>
								<div class="flex justify-between"><span class="text-gray-400 font-medium text-gray-400">Letzter Import:</span> <span class="font-medium">{formatDateTime(speechMeta?.end_time)}</span></div>
							</div>
						</div>
					</div>

					<!-- Manifesto Summary Card -->
					<div class="p-5 rounded-xl border border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-900/30 flex flex-col justify-between">
						<div>
							<div class="flex justify-between items-start mb-3">
								<h3 class="font-semibold text-base text-gray-900 dark:text-gray-100 font-medium">Wahlprogramme</h3>
								<span class="px-2.5 py-0.5 rounded-full text-xs font-semibold {manifestoSuccess ? 'bg-emerald-55 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-400' : 'bg-red-50 text-red-700 dark:bg-red-500/10 dark:text-red-400'}">
									{manifestoSuccess ? 'Aktiv' : 'Inaktiv'}
								</span>
							</div>
							<div class="space-y-2 text-sm text-gray-600 dark:text-gray-300">
								<div class="flex justify-between"><span class="text-gray-400 font-medium text-gray-400 font-medium">Aktuellstes Jahr:</span> <span class="font-medium text-gray-900 dark:text-white">{metadata?.manifestos?.last_manifesto_year || 'Unbekannt'}</span></div>
								<div class="flex justify-between"><span class="text-gray-400 font-medium text-gray-400 font-medium">Wahlprogramme:</span> <span class="font-medium text-gray-900 dark:text-white">{formatNumber(manifestoStats?.manifestos_processed)}</span></div>
								<div class="flex justify-between"><span class="text-gray-400 font-medium text-gray-400 font-medium">Letzter Import:</span> <span class="font-medium">{formatDateTime(manifestoMeta?.end_time)}</span></div>
							</div>
						</div>
					</div>
				</div>

				<!-- Database Info / Weaviate status -->
				<div class="p-5 rounded-xl border border-gray-100 dark:border-gray-800 bg-gray-50/30 dark:bg-gray-900/10">
					<h3 class="font-semibold text-base text-gray-900 dark:text-gray-100 mb-4 font-medium">Vektordatenbank (Weaviate)</h3>
					<div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
						<div class="flex flex-col">
							<span class="text-xs text-gray-400 uppercase tracking-wider font-medium text-gray-400">Integritätsstatus</span>
							<span class="text-lg font-semibold text-emerald-600 dark:text-emerald-400 font-medium">
								{speechStats?.weaviate_integrity_check?.status || 'Unbekannt'}
							</span>
						</div>
						<div class="flex flex-col">
							<span class="text-xs text-gray-400 uppercase tracking-wider font-medium text-gray-400">Reden-Vektoren</span>
							<span class="text-lg font-semibold text-gray-900 dark:text-white font-medium">
								{formatNumber(speechStats?.weaviate_integrity_check?.document_count)} Chunks
							</span>
						</div>
						<div class="flex flex-col">
							<span class="text-xs text-gray-400 uppercase tracking-wider font-medium text-gray-400">Wahlprogramm-Vektoren</span>
							<span class="text-lg font-semibold text-gray-900 dark:text-white font-medium">
								{formatNumber(manifestoStats?.weaviate_integrity_check?.document_count)} Chunks
							</span>
						</div>
					</div>
				</div>

			{:else if activeTab === 'speeches'}
				<!-- Speech Pipeline Stats -->
				<div class="space-y-6">
					<div>
						<h3 class="font-semibold text-base text-gray-900 dark:text-gray-100 mb-3 font-medium">Reden pro Legislaturperiode</h3>
						<div class="grid grid-cols-3 gap-4">
							{#each Object.entries(speechStats?.speeches_per_term || {}) as [term, count]}
								<div class="p-4 rounded-xl border border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-900/20 text-center">
									<div class="text-xs text-gray-400 font-medium text-gray-400">Wahlperiode {term}</div>
									<div class="text-xl font-bold mt-1 text-gray-900 dark:text-white font-medium">{formatNumber(count as number)}</div>
								</div>
							{/each}
						</div>
					</div>

					<!-- Speeches per faction (Term 21 / 20 / 19) -->
					{#if speechStats?.speeches_per_faction_per_term}
						<div>
							<h3 class="font-semibold text-base text-gray-900 dark:text-gray-100 mb-3 font-medium">Reden-Verteilung nach Fraktionen</h3>
							<div class="overflow-x-auto border border-gray-100 dark:border-gray-800 rounded-xl">
								<table class="w-full text-sm text-left">
									<thead class="bg-gray-50 dark:bg-gray-950/40 text-gray-500 font-medium text-gray-400">
										<tr>
											<th class="px-4 py-3">Fraktion / Partei</th>
											<th class="px-4 py-3 text-right">WP 19</th>
											<th class="px-4 py-3 text-right">WP 20</th>
											<th class="px-4 py-3 text-right">WP 21</th>
										</tr>
									</thead>
									<tbody class="divide-y divide-gray-100 dark:divide-gray-850">
										{#each Array.from(new Set([
											...Object.keys(speechStats.speeches_per_faction_per_term['19'] || {}),
											...Object.keys(speechStats.speeches_per_faction_per_term['20'] || {}),
											...Object.keys(speechStats.speeches_per_faction_per_term['21'] || {})
										])).filter(f => f !== 'Faction_-1') as faction}
											<tr class="hover:bg-gray-50/50 dark:hover:bg-gray-900/10">
												<td class="px-4 py-2.5 font-medium">{faction}</td>
												<td class="px-4 py-2.5 text-right font-mono text-gray-500 dark:text-gray-400">
													{formatNumber(speechStats.speeches_per_faction_per_term['19']?.[faction])}
												</td>
												<td class="px-4 py-2.5 text-right font-mono text-gray-500 dark:text-gray-400">
													{formatNumber(speechStats.speeches_per_faction_per_term['20']?.[faction])}
												</td>
												<td class="px-4 py-2.5 text-right font-mono text-gray-500 dark:text-gray-400">
													{formatNumber(speechStats.speeches_per_faction_per_term['21']?.[faction])}
												</td>
											</tr>
										{/each}
									</tbody>
								</table>
							</div>
						</div>
					{/if}

					<!-- Ingestion Correctness -->
					<div>
						<h3 class="font-semibold text-base text-gray-900 dark:text-gray-100 mb-3 font-medium">Ingestion Correctness Checks</h3>
						<div class="space-y-3">
							{#each [19, 20, 21] as term}
								{@const corr = speechStats?.[`ingestion_correctness_${term}`]}
								{#if corr}
									<div class="p-4 rounded-xl border border-gray-100 dark:border-gray-800 flex justify-between items-center text-sm">
										<div>
											<span class="font-semibold font-medium">Wahlperiode {term}:</span>
											<span class="ml-1 text-gray-450 dark:text-gray-400">{formatNumber(corr.number_ingested_speeches)} von {formatNumber(corr.total_number_speeches)} Reden importiert</span>
										</div>
										<span class="px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-400">
											{formatPercent(1 - corr.percentage_speeches_incorrectly_not_ingested)} Korrekt
										</span>
									</div>
								{/if}
							{/each}
						</div>
					</div>

					<!-- Processing times -->
					{#if speechMeta?.step_durations}
						<div>
							<h3 class="font-semibold text-base text-gray-900 dark:text-gray-100 mb-3 font-medium">Pipeline-Schritt-Dauer</h3>
							<div class="overflow-hidden border border-gray-100 dark:border-gray-800 rounded-xl text-sm">
								<table class="w-full text-left">
									<thead class="bg-gray-50 dark:bg-gray-950/40 text-gray-500 font-medium text-gray-400">
										<tr>
											<th class="px-4 py-2.5">Arbeitsschritt</th>
											<th class="px-4 py-2.5 text-right">Dauer</th>
										</tr>
									</thead>
									<tbody class="divide-y divide-gray-100 dark:divide-gray-850 font-mono text-gray-600 dark:text-gray-400">
										{#each Object.entries(speechMeta.step_durations) as [step, sec]}
											<tr class="hover:bg-gray-50/50 dark:hover:bg-gray-900/10">
												<td class="px-4 py-2 capitalize">{step.replace(/_/g, ' ')}</td>
												<td class="px-4 py-2 text-right">{formatDuration(sec as number)}</td>
											</tr>
										{/each}
									</tbody>
								</table>
							</div>
						</div>
					{/if}
				</div>

			{:else if activeTab === 'manifestos'}
				<!-- Manifesto Pipeline Stats -->
				<div class="space-y-6">
					<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
						<div class="p-4 rounded-xl border border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-900/20 text-center">
							<span class="text-xs text-gray-400 font-medium text-gray-400">Sätze Verarbeitet</span>
							<div class="text-xl font-bold mt-1 text-gray-900 dark:text-white font-medium">{formatNumber(manifestoStats?.sentences_processed)}</div>
						</div>
						<div class="p-4 rounded-xl border border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-900/20 text-center">
							<span class="text-xs text-gray-400 font-medium text-gray-400">Vektor Chunks Generiert</span>
							<div class="text-xl font-bold mt-1 text-gray-900 dark:text-white font-medium">{formatNumber(manifestoStats?.chunks_generated)}</div>
						</div>
						<div class="p-4 rounded-xl border border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-900/20 text-center">
							<span class="text-xs text-gray-400 uppercase tracking-wider font-medium text-gray-450">Token-Menge Embeddings</span>
							<div class="text-xl font-bold mt-1 text-gray-900 dark:text-white font-medium">{formatNumber(manifestoStats?.embeddings_token_count)}</div>
						</div>
					</div>

					<div class="space-y-2 text-sm text-gray-600 dark:text-gray-300">
						<div class="flex justify-between border-b border-gray-100 dark:border-gray-800 py-2"><span class="text-gray-405 dark:text-gray-400">Startjahr der Abdeckung:</span> <span class="font-medium text-gray-900 dark:text-white">{manifestoParams?.start_year || 'Unbekannt'}</span></div>
						<div class="flex justify-between border-b border-gray-100 dark:border-gray-800 py-2"><span class="text-gray-405 dark:text-gray-400">Endjahr der Abdeckung:</span> <span class="font-medium text-gray-900 dark:text-white">{manifestoParams?.end_year || 'Unbekannt'}</span></div>
						<div class="flex justify-between border-b border-gray-100 dark:border-gray-800 py-2"><span class="text-gray-405 dark:text-gray-400 font-medium">GPU Beschleunigung verwendet:</span> <span class="font-medium text-gray-900 dark:text-white font-medium">{manifestoParams?.use_gpu ? 'Ja' : 'Nein'}</span></div>
					</div>

					<!-- Processing times -->
					{#if manifestoMeta?.step_durations}
						<div>
							<h3 class="font-semibold text-base text-gray-900 dark:text-gray-100 mb-3 font-medium">Pipeline-Schritt-Dauer</h3>
							<div class="overflow-hidden border border-gray-100 dark:border-gray-800 rounded-xl text-sm">
								<table class="w-full text-left">
									<thead class="bg-gray-50 dark:bg-gray-950/40 text-gray-500 font-medium text-gray-400">
										<tr>
											<th class="px-4 py-2.5">Arbeitsschritt</th>
											<th class="px-4 py-2.5 text-right">Dauer</th>
										</tr>
									</thead>
									<tbody class="divide-y divide-gray-100 dark:divide-gray-850 font-mono text-gray-600 dark:text-gray-400">
										{#each Object.entries(manifestoMeta.step_durations) as [step, sec]}
											<tr class="hover:bg-gray-50/50 dark:hover:bg-gray-900/10">
												<td class="px-4 py-2 capitalize">{step.replace(/_/g, ' ')}</td>
												<td class="px-4 py-2 text-right">{formatDuration(sec as number)}</td>
											</tr>
										{/each}
									</tbody>
								</table>
							</div>
						</div>
					{/if}
				</div>
			{/if}
		</div>

		<!-- Footer -->
		<div class="flex justify-end px-6 py-4 border-t border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-950/30">
			<button
				class="flex items-center justify-center gap-2 rounded-lg bg-gray-900 hover:bg-gray-800 text-white px-4 py-2 text-sm transition dark:bg-white dark:hover:bg-gray-100 dark:text-gray-900"
				on:click={() => (show = false)}
			>
				Schließen
			</button>
		</div>
	</div>
</Modal>
